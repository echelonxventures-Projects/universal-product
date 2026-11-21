"""WP-UCDA-018 — the declared phase graph of the generation runtime (EPIC-006).

The Factory Layer used to carry its execution order twice: as the statement order of
``GenerationOrchestrator.generate``/``execute``, and again as the frozen ``DEFAULT_STAGES``
tuple every factory advertised. ``DEC-MCOS-14`` recorded that defect — a derived plan
existed beside a hard-coded six-step sequence, so two ordering mechanisms coexisted — and
``WP-UCDA-018`` required that a single composition path remain reachable.

This module is the Factory Layer's half of that closure. It holds the **declaration** of
what the generation runtime does, and nothing about the order in which it happens:

    * a :class:`GenerationPhase` declares a phase key, the phase keys it requires, and
      whether it is the declared seam at which the factory is delegated to;
    * :func:`register_generation_phase` admits a phase (and an unbounded number of further
      phases) by registration;
    * :func:`generation_order` **derives** the order through
      :mod:`engine.foundation.composition` — the single ordering authority also used by
      :mod:`engine.civilization.composition`.

Registering one more phase therefore changes the order the runtime executes and the stage
vocabulary every factory advertises, with no edit to this module and none to the
orchestrator. There is no second declaration of the order to drift from this one:
:func:`generation_stages` is derived, not frozen, so what a factory advertises is by
construction what the runtime runs.

The declared graph below reproduces the previously hard-coded sequence exactly, so this is a
change of *authority* over the order, not a change of behaviour: ``resolve-blueprint`` →
``classify`` → ``resolve-factory`` ⟨seam⟩ → ``compile`` → ``assemble`` → ``deploy`` →
``rollback`` → ``evidence``.

The seam is declared rather than implicit because the factory delegation is a real contract
boundary: :meth:`engine.factory.factories.base.BaseFactory.generate` receives the resolved
context and hands execution back to the orchestrator's shared path. Declaring which phase it
follows keeps that boundary a property of the phase graph instead of a special case in code.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any

from engine.factory.errors import GenerationPhaseError
from engine.foundation.composition import (
    DEFAULT_STRATEGY,
    derive_order,
    unresolved_keys,
)

#: A phase handler: applied to the orchestrator and the mutable generation state.
#: Handlers are registered with their phase and are never called in a hard-coded order.
PhaseHandler = Callable[[Any, Any], None]


@dataclass(frozen=True, slots=True)
class GenerationPhase:
    """One declared phase of the generation runtime."""

    key: str
    requires: tuple[str, ...] = ()
    #: True for the single phase after which execution is delegated to the factory.
    seam: bool = False
    handler: PhaseHandler | None = field(default=None, compare=False)

    def to_dict(self) -> dict[str, object]:
        """A deterministic, serialisable rendering of this declaration."""
        return {"key": self.key, "requires": list(self.requires), "seam": self.seam}


_PHASES: dict[str, GenerationPhase] = {}


# --------------------------------------------------------------------------- registration


def register_generation_phase(
    key: str,
    *,
    handler: PhaseHandler,
    requires: tuple[str, ...] = (),
    seam: bool = False,
) -> GenerationPhase:
    """Declare one generation phase (unbounded extension).

    Raises :class:`GenerationPhaseError` if ``key`` is already declared, or if ``seam`` is
    requested while another phase already holds it: the seam is a contract boundary, and two
    boundaries would reintroduce the ambiguity this module exists to remove.
    """
    if key in _PHASES:
        raise GenerationPhaseError("generation phase already declared", phase=key)
    if seam:
        held = [phase.key for phase in _PHASES.values() if phase.seam]
        if held:
            raise GenerationPhaseError(
                "the delegation seam is already declared by another phase",
                phase=key,
                seam=held[0],
            )
    declared = GenerationPhase(key=key, requires=tuple(requires), seam=seam, handler=handler)
    _PHASES[key] = declared
    return declared


def unregister_generation_phase(key: str) -> GenerationPhase:
    """Withdraw a declared phase. Raises :class:`GenerationPhaseError` if undeclared."""
    try:
        return _PHASES.pop(key)
    except KeyError:
        raise GenerationPhaseError("generation phase is not declared", phase=key) from None


def generation_phases() -> tuple[GenerationPhase, ...]:
    """Every declared phase, ordered by key (declaration order is irrelevant)."""
    return tuple(sorted(_PHASES.values(), key=lambda phase: phase.key))


def generation_phase(key: str) -> GenerationPhase:
    """The declaration of one phase. Raises :class:`GenerationPhaseError` if undeclared."""
    try:
        return _PHASES[key]
    except KeyError:
        raise GenerationPhaseError("generation phase is not declared", phase=key) from None


# --------------------------------------------------------------------------- derivation


def phase_graph() -> dict[str, tuple[str, ...]]:
    """The declared dependency graph: phase key -> the phase keys it requires."""
    return {phase.key: phase.requires for phase in generation_phases()}


def generation_order(*, strategy: str = DEFAULT_STRATEGY) -> tuple[str, ...]:
    """Derive the order in which the generation runtime executes its declared phases.

    Derivation is delegated to the single ordering authority, so this order and the
    capability composition order of :mod:`engine.civilization.composition` are produced by
    one mechanism. A phase requiring one that is not declared, or a declared cycle, is
    refused rather than silently ordered.
    """
    graph = phase_graph()
    declared = set(graph)
    for key, requires in sorted(graph.items()):
        missing = sorted(set(requires) - declared)
        if missing:
            raise GenerationPhaseError(
                "generation phase requires a phase that is not declared",
                phase=key,
                missing=missing,
            )
    ordering = derive_order(graph, strategy=strategy)
    if len(ordering) != len(graph):
        raise GenerationPhaseError(
            "generation phase requirements contain a cycle, so no order exists",
            unresolved=unresolved_keys(graph, ordering),
        )
    return tuple(key for _wave, key in ordering)


def generation_stages() -> tuple[str, ...]:
    """The stage vocabulary every factory advertises — the derived order, never a copy.

    This is the value :class:`~engine.factory.contracts.FactoryCapability` carries. It is
    computed from the declared phase graph on every call, so what a factory advertises is by
    construction the order the runtime runs; there is no frozen second declaration.
    """
    return generation_order()


def seam_phase() -> str:
    """The phase after which execution is delegated to the resolved factory.

    Raises :class:`GenerationPhaseError` when no phase declares the seam: the delegation
    boundary is a contract, and a runtime with no declared boundary has no lawful split.
    """
    for phase in generation_phases():
        if phase.seam:
            return phase.key
    raise GenerationPhaseError("no generation phase declares the delegation seam")


def generation_span(*, after_seam: bool, strategy: str = DEFAULT_STRATEGY) -> tuple[str, ...]:
    """The derived phases before-and-including the seam, or those strictly after it."""
    order = generation_order(strategy=strategy)
    boundary = order.index(seam_phase())
    return order[boundary + 1 :] if after_seam else order[: boundary + 1]


def describe() -> dict[str, object]:
    """A deterministic, machine-readable description of the generation phase surface."""
    return {
        "subject": "GenerationPhaseGraph",
        "phases": [phase.to_dict() for phase in generation_phases()],
        "order": list(generation_order()),
        "stages": list(generation_stages()),
        "seam": seam_phase(),
        "count": len(_PHASES),
        "fixed_pipeline": False,
        "upper_limit": None,
    }


__all__ = [
    "GenerationPhase",
    "PhaseHandler",
    "describe",
    "generation_order",
    "generation_phase",
    "generation_phases",
    "generation_span",
    "generation_stages",
    "phase_graph",
    "register_generation_phase",
    "seam_phase",
    "unregister_generation_phase",
]
