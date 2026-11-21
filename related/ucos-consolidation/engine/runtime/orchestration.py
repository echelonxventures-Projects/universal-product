"""TASK-000042 — Runtime Orchestration (EPIC-006).

The top-level entry point of the Universal Runtime Composition Engine and the
realisation of RUNTIME-013 Orchestration: *a typed, identified, bounded,
coordinated composition of behaviour across constructs* (ORL-01). It is the
capability that **composes existing Universes** — the headline mission of the
runtime composition engine.

:func:`orchestrate` is a thin coordinator: it delegates the structural work to
:func:`engine.runtime.composition.compose` (reused verbatim — no duplicate
composition, dependency, or planning logic) and records an orchestration-level
:class:`RuntimeOrchestration` that adds only:

    * a deterministic ``orchestration_id`` derived from the composition identity;
    * the coordination classification (RUNTIME-013 §D9);
    * an auditable orchestration descriptor embedding the full composition;
    * the EC-1 provisional-state disclosure, carried through from the composition.

An orchestration is a **coordinated composition structure only**: it confers no
authority (ORL-22) and is never an engine, scheduler, or executor (ORL-15/ORL-23).
It is deterministic (ORL-20): identical Universes, coordination, and federations
yield a byte-identical orchestration.
"""

from __future__ import annotations

import hashlib
from collections.abc import Iterable
from dataclasses import dataclass
from typing import Any

from engine.foundation.obs.logging import get_logger
from engine.foundation.obs.telemetry import trace
from engine.runtime.composition import RuntimeComposition, Universe, compose
from engine.runtime.context import Federation
from engine.runtime.planner import DEFAULT_COORDINATION, ExecutionPlan

_logger = get_logger("runtime.orchestration")

#: The deterministic orchestration descriptor format the engine emits.
ORCHESTRATION_FORMAT = "ucos-orchestration/1.0.0"


@dataclass(frozen=True, slots=True)
class RuntimeOrchestration:
    """A coordinated composition of Universes (RUNTIME-013 §D8/D9; ORL-01).

    Wraps a :class:`RuntimeComposition` with an orchestration identity and the
    recorded coordination class. A composition structure only — it deploys and
    executes nothing.
    """

    orchestration_id: str
    composition: RuntimeComposition
    coordination: str
    descriptor: dict[str, Any]
    disclosure: dict[str, Any]

    @property
    def composition_id(self) -> str:
        """The identity of the underlying composition."""
        return self.composition.composition_id

    @property
    def plan(self) -> ExecutionPlan:
        """The recorded coordination plan of the composition."""
        return self.composition.plan

    def universe_ids(self) -> tuple[str, ...]:
        """Every orchestrated universe id, in stable sorted order."""
        return self.composition.universe_ids()

    def to_dict(self) -> dict[str, Any]:
        """A complete, auditable, JSON-serialisable view of the orchestration."""
        return dict(self.descriptor)


def orchestrate(
    universes: Iterable[Universe],
    *,
    coordination: str = DEFAULT_COORDINATION,
    federations: Iterable[Federation] = (),
) -> RuntimeOrchestration:
    """Compose ``universes`` into a coordinated :class:`RuntimeOrchestration`.

    Args:
        universes: the assembled Universes to orchestrate (at least one).
        coordination: the coordination class (RUNTIME-013 §D9).
        federations: explicit cross-context federation references (ORL-12).

    Raises:
        RuntimeCompositionError, RuntimeGraphError, ContextResolutionError,
        ReferenceFrameError, ExecutionPlanError: on any composition failure.
    """
    with trace("runtime.orchestrate", coordination=coordination):
        composition = compose(universes, coordination=coordination, federations=federations)
        orchestration = orchestration_of(composition)
    _logger.info(
        "runtime.orchestrated",
        orchestration_id=orchestration.orchestration_id,
        composition_id=composition.composition_id,
        universes=len(composition.universes),
        coordination=coordination,
    )
    return orchestration


def orchestration_of(composition: RuntimeComposition) -> RuntimeOrchestration:
    """Wrap an existing :class:`RuntimeComposition` as a :class:`RuntimeOrchestration`.

    Deterministic: the ``orchestration_id`` is a SHA-256 over the composition
    identity and coordination class, so the same composition yields the same
    orchestration identity.
    """
    orchestration_id = _orchestration_id(composition)
    descriptor = _build_descriptor(orchestration_id, composition)
    return RuntimeOrchestration(
        orchestration_id=orchestration_id,
        composition=composition,
        coordination=composition.coordination,
        descriptor=descriptor,
        disclosure=composition.disclosure,
    )


# --------------------------------------------------------------------------- #
# Helpers                                                                      #
# --------------------------------------------------------------------------- #


def _orchestration_id(composition: RuntimeComposition) -> str:
    """A deterministic, non-authoritative orchestration identity (IMP-007 §5)."""
    payload = f"{composition.composition_id}||coordination={composition.coordination}"
    digest = hashlib.sha256(payload.encode()).hexdigest()
    return f"UCOS-ORCHESTRATION-{digest[:16]}"


def _build_descriptor(orchestration_id: str, composition: RuntimeComposition) -> dict[str, Any]:
    """Build the deterministic orchestration descriptor (embeds the composition)."""
    return {
        "orchestration_descriptor_format": ORCHESTRATION_FORMAT,
        "orchestration_id": orchestration_id,
        "authority": "ENGINEERING-EXECUTION-ONLY",
        "coordination": composition.coordination,
        "composition_id": composition.composition_id,
        "universe_count": len(composition.universes),
        "context_count": len(composition.contexts),
        "federation_count": len(composition.federations),
        "execution_plan": composition.plan.to_dict(),
        "composition": composition.to_dict(),
        "provisional_state_disclosure": composition.disclosure,
    }


__all__ = [
    "ORCHESTRATION_FORMAT",
    "RuntimeOrchestration",
    "orchestrate",
    "orchestration_of",
]
