"""EC2-TASK-000100 — Blueprint Lifecycle (EC2-EPIC-006).

The deterministic blueprint **state machine** and its append-only transition event
(Program §2.1 #7, PC-04, §5 acceptance). A blueprint occupies exactly one
:class:`~platform.blueprints.contracts.BlueprintStatus` at a time; transitions are a
pure, fail-closed function of the current and target status (IMP-007 §5 determinism):

    DRAFT      ─▶ VALIDATED · RETIRED
    VALIDATED  ─▶ CATALOGUED · RETIRED
    CATALOGUED ─▶ SUPERSEDED · RETIRED
    SUPERSEDED ─▶ RETIRED
    RETIRED    ─▶ (terminal)

An illegal transition (unknown edge, or any edge out of the terminal RETIRED state, or
a no-op self-transition) raises :class:`BlueprintLifecycleError`. An invalid blueprint
is never promoted past DRAFT (it is refused with the EC-1 gap report). Each accepted
transition is recorded as an immutable, ordered :class:`BlueprintEvent` (no wall-clock;
a caller-supplied logical ``tick``) so the lifecycle history is reproducible and
append-only (OP-C3). This mirrors the certified
:mod:`platform.projects.lifecycle` state-machine pattern exactly (proven template).
"""

from __future__ import annotations

from dataclasses import dataclass
from platform.blueprints.contracts import BlueprintStatus
from platform.blueprints.errors import BlueprintLifecycleError
from typing import Any

#: The legal state-machine edges: current status → the statuses it may transition to.
_TRANSITIONS: dict[BlueprintStatus, frozenset[BlueprintStatus]] = {
    BlueprintStatus.DRAFT: frozenset({BlueprintStatus.VALIDATED, BlueprintStatus.RETIRED}),
    BlueprintStatus.VALIDATED: frozenset({BlueprintStatus.CATALOGUED, BlueprintStatus.RETIRED}),
    BlueprintStatus.CATALOGUED: frozenset({BlueprintStatus.SUPERSEDED, BlueprintStatus.RETIRED}),
    BlueprintStatus.SUPERSEDED: frozenset({BlueprintStatus.RETIRED}),
    BlueprintStatus.RETIRED: frozenset(),
}


def allowed_transitions(status: BlueprintStatus) -> tuple[BlueprintStatus, ...]:
    """Return the statuses ``status`` may transition to (stable order)."""
    if not isinstance(status, BlueprintStatus):
        raise BlueprintLifecycleError("status must be a BlueprintStatus")
    targets = _TRANSITIONS[status]
    return tuple(s for s in BlueprintStatus if s in targets)


def can_transition(current: BlueprintStatus, target: BlueprintStatus) -> bool:
    """True iff ``current`` may transition to ``target`` (pure, deterministic)."""
    if not isinstance(current, BlueprintStatus) or not isinstance(target, BlueprintStatus):
        raise BlueprintLifecycleError("transition endpoints must be BlueprintStatus")
    return target in _TRANSITIONS[current]


def validate_transition(current: BlueprintStatus, target: BlueprintStatus) -> None:
    """Raise :class:`BlueprintLifecycleError` unless ``current → target`` is legal."""
    if not can_transition(current, target):
        raise BlueprintLifecycleError(
            "illegal blueprint lifecycle transition",
            current=current.value,
            target=target.value,
        )


@dataclass(frozen=True, slots=True)
class BlueprintEvent:
    """An immutable, ordered record of a blueprint lifecycle transition (append-only)."""

    sequence: int
    blueprint_id: str
    from_status: BlueprintStatus
    to_status: BlueprintStatus
    tick: int

    def to_dict(self) -> dict[str, Any]:
        return {
            "sequence": self.sequence,
            "blueprint_id": self.blueprint_id,
            "from_status": self.from_status.value,
            "to_status": self.to_status.value,
            "tick": self.tick,
        }


__all__ = [
    "allowed_transitions",
    "can_transition",
    "validate_transition",
    "BlueprintEvent",
]
