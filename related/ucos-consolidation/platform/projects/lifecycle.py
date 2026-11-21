"""EC2-TASK-000090 — Project Lifecycle (EC2-EPIC-005).

The deterministic project **state machine** and its append-only transition event
(Program §2.1 #4 "lifecycle & status"; §5 "lifecycle states defined & enforced"). A
project occupies exactly one :class:`~platform.projects.contracts.ProjectStatus` at a
time; transitions are a pure, fail-closed function of the current and target status
(IMP-007 §5 determinism):

    ACTIVE     ─▶ SUSPENDED · COMPLETED · ARCHIVED
    SUSPENDED  ─▶ ACTIVE · ARCHIVED
    COMPLETED  ─▶ ACTIVE · ARCHIVED
    ARCHIVED   ─▶ (terminal)

An illegal transition (unknown edge, or any edge out of the terminal ARCHIVED state,
or a no-op self-transition) raises :class:`ProjectLifecycleError`. Each accepted
transition is recorded as an immutable, ordered :class:`ProjectEvent` (no wall-clock;
a caller-supplied logical ``tick``) so the lifecycle history is reproducible and
append-only (OP-C3). This mirrors the certified
:mod:`platform.workspace.lifecycle` state-machine pattern exactly (proven template).
"""

from __future__ import annotations

from dataclasses import dataclass
from platform.projects.contracts import ProjectStatus
from platform.projects.errors import ProjectLifecycleError
from typing import Any

#: The legal state-machine edges: current status → the statuses it may transition to.
_TRANSITIONS: dict[ProjectStatus, frozenset[ProjectStatus]] = {
    ProjectStatus.ACTIVE: frozenset(
        {ProjectStatus.SUSPENDED, ProjectStatus.COMPLETED, ProjectStatus.ARCHIVED}
    ),
    ProjectStatus.SUSPENDED: frozenset({ProjectStatus.ACTIVE, ProjectStatus.ARCHIVED}),
    ProjectStatus.COMPLETED: frozenset({ProjectStatus.ACTIVE, ProjectStatus.ARCHIVED}),
    ProjectStatus.ARCHIVED: frozenset(),
}


def allowed_transitions(status: ProjectStatus) -> tuple[ProjectStatus, ...]:
    """Return the statuses ``status`` may transition to (stable order)."""
    if not isinstance(status, ProjectStatus):
        raise ProjectLifecycleError("status must be a ProjectStatus")
    targets = _TRANSITIONS[status]
    return tuple(s for s in ProjectStatus if s in targets)


def can_transition(current: ProjectStatus, target: ProjectStatus) -> bool:
    """True iff ``current`` may transition to ``target`` (pure, deterministic)."""
    if not isinstance(current, ProjectStatus) or not isinstance(target, ProjectStatus):
        raise ProjectLifecycleError("transition endpoints must be ProjectStatus")
    return target in _TRANSITIONS[current]


def validate_transition(current: ProjectStatus, target: ProjectStatus) -> None:
    """Raise :class:`ProjectLifecycleError` unless ``current → target`` is legal."""
    if not can_transition(current, target):
        raise ProjectLifecycleError(
            "illegal project lifecycle transition",
            current=current.value,
            target=target.value,
        )


@dataclass(frozen=True, slots=True)
class ProjectEvent:
    """An immutable, ordered record of a project lifecycle transition (append-only)."""

    sequence: int
    project_id: str
    from_status: ProjectStatus
    to_status: ProjectStatus
    tick: int

    def to_dict(self) -> dict[str, Any]:
        return {
            "sequence": self.sequence,
            "project_id": self.project_id,
            "from_status": self.from_status.value,
            "to_status": self.to_status.value,
            "tick": self.tick,
        }


__all__ = [
    "allowed_transitions",
    "can_transition",
    "validate_transition",
    "ProjectEvent",
]
