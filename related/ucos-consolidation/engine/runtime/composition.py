"""TASK-000041 — Universal Runtime Composition Engine + Dynamic Composition (EPIC-006).

The composition engine of the Universal Runtime Composition Engine: it composes
**already-assembled** runtime units — the ``RuntimeUnit`` produced by
:func:`engine.runtime.assembly.assemble` (EPIC-005), here called a **Universe** —
into a single, deterministic, bounded, acyclic :class:`RuntimeComposition`
(RUNTIME-013 §D8 Composition; ORL-01/ORL-11).

Composition is a **structure only** (RUNTIME-013 ORL-15): the engine reuses the
existing runtime, compiler, and Foundation capabilities **verbatim** and adds no
duplicate assembly, dependency-resolution, or execution logic:

    * ``RuntimeUnit`` (assembly, EPIC-005) is reused as the composed unit — a
      Universe is a thin binding of an assembled unit to a bounding context and its
      inter-universe dependencies;
    * :class:`~engine.runtime.graph.RuntimeGraph` resolves the dependency graph
      (reusing the compiler's cycle/topological primitives);
    * :func:`~engine.runtime.context.resolve_contexts` /
      :func:`~engine.runtime.context.resolve_reference_frames` resolve the bounding
      contexts and cross-context federation;
    * :func:`~engine.runtime.planner.plan_execution` records the coordination plan;
    * :func:`~engine.runtime.disclosure.build_disclosure` stamps the EC-1
      provisional-state disclosure onto the composition (DE-05), and each composed
      Universe must itself already carry that disclosure — so provisionality is
      preserved through composition.

The composition is deterministic (IMP-007 §5; ORL-20): every collection is sorted,
no wall-clock/ambient state is embedded, and the ``composition_id`` is a SHA-256
over the sorted universe fingerprints, coordination class, and federation set —
identical inputs yield a byte-identical composition. :class:`RuntimeComposer`
provides **dynamic composition**: an additive, forward-only builder (ORL-07) that
composes universes incrementally and can extend an existing composition.
"""

from __future__ import annotations

import hashlib
from collections.abc import Iterable
from dataclasses import dataclass, field
from typing import Any

from engine.foundation.obs.logging import get_logger
from engine.foundation.obs.telemetry import trace
from engine.runtime.assembly import RuntimeUnit
from engine.runtime.context import (
    DEFAULT_CONTEXT,
    Federation,
    ReferenceFrame,
    RuntimeContext,
    resolve_contexts,
    resolve_reference_frames,
)
from engine.runtime.disclosure import build_disclosure, disclosure_present
from engine.runtime.errors import RuntimeCompositionError
from engine.runtime.graph import RuntimeGraph
from engine.runtime.planner import DEFAULT_COORDINATION, ExecutionPlan, plan_execution

_logger = get_logger("runtime.composition")

#: The deterministic composition descriptor format the engine emits.
RUNTIME_COMPOSITION_FORMAT = "ucos-composition/1.0.0"


# --------------------------------------------------------------------------- #
# Value types                                                                  #
# --------------------------------------------------------------------------- #


@dataclass(frozen=True, slots=True)
class Universe:
    """A composable runtime unit: an assembled :class:`RuntimeUnit` bound to a context.

    ``depends_on`` are the ids of the other universes this universe depends on
    (downward, acyclic — ORL-17). ``context_id`` is the bounding context (ORL-14).
    A Universe reuses the assembled unit verbatim; it adds no assembly logic.
    """

    universe_id: str
    unit: RuntimeUnit
    context_id: str = DEFAULT_CONTEXT
    depends_on: tuple[str, ...] = field(default_factory=tuple)

    @classmethod
    def of(
        cls,
        unit: RuntimeUnit,
        *,
        universe_id: str | None = None,
        context_id: str = DEFAULT_CONTEXT,
        depends_on: Iterable[str] = (),
    ) -> Universe:
        """Bind an assembled ``unit`` into a composable Universe.

        ``universe_id`` defaults to the unit's blueprint id; ``depends_on`` is
        de-duplicated and sorted for determinism.
        """
        return cls(
            universe_id=universe_id or unit.blueprint_id,
            unit=unit,
            context_id=context_id,
            depends_on=tuple(sorted(set(depends_on))),
        )

    @property
    def package_sha256(self) -> str:
        """The pinned package hash of the composed unit."""
        return self.unit.package_sha256

    def fingerprint(self) -> str:
        """A deterministic, collision-resistant fingerprint of this universe."""
        deps = ",".join(self.depends_on)
        return f"{self.universe_id}@{self.context_id}:{self.unit.package_sha256}:[{deps}]"

    def to_dict(self) -> dict[str, Any]:
        return {
            "universe_id": self.universe_id,
            "context_id": self.context_id,
            "depends_on": list(self.depends_on),
            "unit": {
                "runtime_id": self.unit.runtime_id,
                "blueprint_id": self.unit.blueprint_id,
                "artifact_id": self.unit.artifact_id,
                "package_sha256": self.unit.package_sha256,
                "image_reference": self.unit.image_reference,
            },
        }


@dataclass(frozen=True, slots=True)
class RuntimeComposition:
    """A deterministic, bounded, acyclic composition of Universes (RUNTIME-013 §D8).

    Self-describing: it carries the composed universes, the resolved dependency
    graph, the bounding contexts, the per-universe reference frames, the recorded
    coordination plan, the federation set, and the EC-1 provisional-state
    disclosure. A composition structure only — it deploys and executes nothing.
    """

    composition_id: str
    universes: tuple[Universe, ...]
    graph: RuntimeGraph
    contexts: tuple[RuntimeContext, ...]
    reference_frames: tuple[ReferenceFrame, ...]
    plan: ExecutionPlan
    coordination: str
    federations: tuple[Federation, ...]
    disclosure: dict[str, Any]
    descriptor: dict[str, Any]

    def universe(self, universe_id: str) -> Universe:
        """Return the composed Universe with ``universe_id`` (raises if absent)."""
        for universe in self.universes:
            if universe.universe_id == universe_id:
                return universe
        raise RuntimeCompositionError(
            "universe is not a member of the composition", universe_id=universe_id
        )

    def universe_ids(self) -> tuple[str, ...]:
        """Every composed universe id, in stable sorted order."""
        return tuple(universe.universe_id for universe in self.universes)

    def to_dict(self) -> dict[str, Any]:
        """A complete, auditable, JSON-serialisable view of the composition."""
        return {
            "composition_descriptor_format": RUNTIME_COMPOSITION_FORMAT,
            "composition_id": self.composition_id,
            "authority": "ENGINEERING-EXECUTION-ONLY",
            "coordination": self.coordination,
            "universes": [universe.to_dict() for universe in self.universes],
            "graph": self.graph.to_dict(),
            "contexts": [context.to_dict() for context in self.contexts],
            "reference_frames": [frame.to_dict() for frame in self.reference_frames],
            "federations": [federation.to_dict() for federation in self.federations],
            "execution_plan": self.plan.to_dict(),
            "provisional_state_disclosure": self.disclosure,
        }


# --------------------------------------------------------------------------- #
# Public API — composition                                                     #
# --------------------------------------------------------------------------- #


def compose(
    universes: Iterable[Universe],
    *,
    coordination: str = DEFAULT_COORDINATION,
    federations: Iterable[Federation] = (),
) -> RuntimeComposition:
    """Compose ``universes`` into a deterministic :class:`RuntimeComposition`.

    Args:
        universes: the assembled Universes to compose (at least one).
        coordination: the coordination class of the recorded plan (RUNTIME-013 §D9).
        federations: explicit cross-context federation references (ORL-12).

    Raises:
        RuntimeCompositionError: on an empty set, a duplicate universe id, or a
            composed unit missing its EC-1 provisional-state disclosure.
        RuntimeGraphError, ContextResolutionError, ReferenceFrameError,
        ExecutionPlanError: on any downstream resolution failure.
    """
    materialised = _materialise(universes)
    federation_set = _materialise_federations(federations)

    with trace("runtime.compose", universes=len(materialised), coordination=coordination):
        graph = RuntimeGraph.of(
            {universe.universe_id: universe.depends_on for universe in materialised}
        )
        bindings = {universe.universe_id: universe.context_id for universe in materialised}
        contexts = resolve_contexts(bindings)
        frames = resolve_reference_frames(bindings, graph, federation_set)
        plan = plan_execution(graph, coordination=coordination)

        composition_id = _composition_id(materialised, coordination, federation_set)
        disclosure = build_disclosure()
        descriptor = _build_descriptor(
            composition_id=composition_id,
            universes=materialised,
            graph=graph,
            contexts=contexts,
            frames=frames,
            plan=plan,
            coordination=coordination,
            federations=federation_set,
            disclosure=disclosure,
        )
        composition = RuntimeComposition(
            composition_id=composition_id,
            universes=materialised,
            graph=graph,
            contexts=contexts,
            reference_frames=frames,
            plan=plan,
            coordination=coordination,
            federations=federation_set,
            disclosure=disclosure,
            descriptor=descriptor,
        )

    _logger.info(
        "runtime.composed",
        composition_id=composition_id,
        universes=len(materialised),
        contexts=len(contexts),
        coordination=coordination,
    )
    return composition


# --------------------------------------------------------------------------- #
# Public API — dynamic composition                                             #
# --------------------------------------------------------------------------- #


class RuntimeComposer:
    """An additive, forward-only builder for dynamic composition (ORL-07).

    Universes and federations are added incrementally and composed on demand;
    :meth:`compose` is pure and re-entrant, so re-composing the same builder yields
    a byte-identical composition. :meth:`from_composition` seeds a builder from an
    existing composition so it can be **extended** additively (never mutated).
    """

    __slots__ = ("_universes", "_federations")

    def __init__(self) -> None:
        self._universes: dict[str, Universe] = {}
        self._federations: list[Federation] = []

    @classmethod
    def from_composition(cls, composition: RuntimeComposition) -> RuntimeComposer:
        """Seed a builder from an existing composition (for additive extension)."""
        builder = cls()
        for universe in composition.universes:
            builder.add(universe)
        for federation in composition.federations:
            builder.federate(federation.source, federation.target)
        return builder

    def add(self, universe: Universe) -> RuntimeComposer:
        """Add a Universe (additive; a duplicate id is refused — ORL-07)."""
        if universe.universe_id in self._universes:
            raise RuntimeCompositionError(
                "universe id already present in the composer (no silent mutation)",
                universe_id=universe.universe_id,
            )
        self._universes[universe.universe_id] = universe
        return self

    def add_unit(
        self,
        unit: RuntimeUnit,
        *,
        universe_id: str | None = None,
        context_id: str = DEFAULT_CONTEXT,
        depends_on: Iterable[str] = (),
    ) -> RuntimeComposer:
        """Bind an assembled ``unit`` into the composer as a new Universe."""
        return self.add(
            Universe.of(
                unit,
                universe_id=universe_id,
                context_id=context_id,
                depends_on=depends_on,
            )
        )

    def federate(self, source: str, target: str) -> RuntimeComposer:
        """Add an explicit cross-context federation reference (ORL-12)."""
        self._federations.append(Federation(source=source, target=target))
        return self

    def universes(self) -> tuple[Universe, ...]:
        """The universes added so far, in stable sorted order."""
        return tuple(sorted(self._universes.values(), key=lambda u: u.universe_id))

    def compose(self, *, coordination: str = DEFAULT_COORDINATION) -> RuntimeComposition:
        """Compose everything added so far into a :class:`RuntimeComposition`."""
        return compose(
            self._universes.values(),
            coordination=coordination,
            federations=tuple(self._federations),
        )


# --------------------------------------------------------------------------- #
# Helpers                                                                      #
# --------------------------------------------------------------------------- #


def _materialise(universes: Iterable[Universe]) -> tuple[Universe, ...]:
    """Validate and sort the input universes (deterministic order)."""
    by_id: dict[str, Universe] = {}
    for universe in universes:
        if not isinstance(universe, Universe):
            raise RuntimeCompositionError(
                "composition members must be Universe instances",
                got=type(universe).__name__,
            )
        if universe.universe_id in by_id:
            raise RuntimeCompositionError(
                "duplicate universe id in the composition set",
                universe_id=universe.universe_id,
            )
        # Provisionality is preserved through composition (DE-05): every composed
        # unit must already carry the EC-1 provisional-state disclosure.
        if not disclosure_present(universe.unit.disclosure):
            raise RuntimeCompositionError(
                "composed unit is missing the EC-1 provisional-state disclosure",
                universe_id=universe.universe_id,
            )
        by_id[universe.universe_id] = universe
    if not by_id:
        raise RuntimeCompositionError("a composition requires at least one universe")
    return tuple(sorted(by_id.values(), key=lambda u: u.universe_id))


def _materialise_federations(
    federations: Iterable[Federation],
) -> tuple[Federation, ...]:
    """Sort the federation references deterministically (validation is in context)."""
    return tuple(sorted(federations, key=lambda f: (f.source, f.target)))


def _composition_id(
    universes: tuple[Universe, ...],
    coordination: str,
    federations: tuple[Federation, ...],
) -> str:
    """A deterministic, non-authoritative composition identity (IMP-007 §5)."""
    universe_part = "|".join(universe.fingerprint() for universe in universes)
    federation_part = ";".join(f"{f.source}->{f.target}" for f in federations)
    payload = f"{universe_part}||coordination={coordination}||federations={federation_part}"
    digest = hashlib.sha256(payload.encode()).hexdigest()
    return f"UCOS-COMPOSITION-{digest[:16]}"


def _build_descriptor(
    *,
    composition_id: str,
    universes: tuple[Universe, ...],
    graph: RuntimeGraph,
    contexts: tuple[RuntimeContext, ...],
    frames: tuple[ReferenceFrame, ...],
    plan: ExecutionPlan,
    coordination: str,
    federations: tuple[Federation, ...],
    disclosure: dict[str, Any],
) -> dict[str, Any]:
    """Build the deterministic composition descriptor (no timestamps, sorted)."""
    return {
        "composition_descriptor_format": RUNTIME_COMPOSITION_FORMAT,
        "composition_id": composition_id,
        "authority": "ENGINEERING-EXECUTION-ONLY",
        "coordination": coordination,
        "universes": [universe.to_dict() for universe in universes],
        "graph": graph.to_dict(),
        "contexts": [context.to_dict() for context in contexts],
        "reference_frames": [frame.to_dict() for frame in frames],
        "federations": [federation.to_dict() for federation in federations],
        "execution_plan": plan.to_dict(),
        "provisional_state_disclosure": disclosure,
    }


__all__ = [
    "RUNTIME_COMPOSITION_FORMAT",
    "Universe",
    "RuntimeComposition",
    "compose",
    "RuntimeComposer",
]
