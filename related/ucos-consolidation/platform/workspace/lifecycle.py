"""EC2-TASK-000082 — Workspace Lifecycle (EC2-EPIC-004).

The deterministic workspace **state machine** and its append-only transition event.
A workspace occupies exactly one :class:`~platform.workspace.contracts.WorkspaceStatus`
at a time; transitions are a pure, fail-closed function of the current and target
status (IMP-007 §5 determinism):

    ACTIVE    ─▶ SUSPENDED · ARCHIVED
    SUSPENDED ─▶ ACTIVE · ARCHIVED
    ARCHIVED  ─▶ (terminal)

An illegal transition (unknown edge, or any edge out of the terminal ARCHIVED state,
or a no-op self-transition) raises :class:`WorkspaceLifecycleError`. Each accepted
transition is recorded as an immutable, ordered :class:`WorkspaceEvent` (no wall-clock;
a caller-supplied logical ``tick``) so the lifecycle history is reproducible and
append-only (OP-C3).
"""

from __future__ import annotations

from dataclasses import dataclass
from platform.workspace.contracts import WorkspaceStatus
from platform.workspace.errors import WorkspaceLifecycleError
from typing import Any

#: The legal state-machine edges: current status → the statuses it may transition to.
_TRANSITIONS: dict[WorkspaceStatus, frozenset[WorkspaceStatus]] = {
    WorkspaceStatus.ACTIVE: frozenset({WorkspaceStatus.SUSPENDED, WorkspaceStatus.ARCHIVED}),
    WorkspaceStatus.SUSPENDED: frozenset({WorkspaceStatus.ACTIVE, WorkspaceStatus.ARCHIVED}),
    WorkspaceStatus.ARCHIVED: frozenset(),
}


def allowed_transitions(status: WorkspaceStatus) -> tuple[WorkspaceStatus, ...]:
    """Return the statuses ``status`` may transition to (stable order)."""
    if not isinstance(status, WorkspaceStatus):
        raise WorkspaceLifecycleError("status must be a WorkspaceStatus")
    targets = _TRANSITIONS[status]
    return tuple(s for s in WorkspaceStatus if s in targets)


def can_transition(current: WorkspaceStatus, target: WorkspaceStatus) -> bool:
    """True iff ``current`` may transition to ``target`` (pure, deterministic)."""
    if not isinstance(current, WorkspaceStatus) or not isinstance(target, WorkspaceStatus):
        raise WorkspaceLifecycleError("transition endpoints must be WorkspaceStatus")
    return target in _TRANSITIONS[current]


def validate_transition(current: WorkspaceStatus, target: WorkspaceStatus) -> None:
    """Raise :class:`WorkspaceLifecycleError` unless ``current → target`` is legal."""
    if not can_transition(current, target):
        raise WorkspaceLifecycleError(
            "illegal workspace lifecycle transition",
            current=current.value,
            target=target.value,
        )


@dataclass(frozen=True, slots=True)
class WorkspaceEvent:
    """An immutable, ordered record of a workspace lifecycle transition (append-only)."""

    sequence: int
    workspace_id: str
    from_status: WorkspaceStatus
    to_status: WorkspaceStatus
    tick: int

    def to_dict(self) -> dict[str, Any]:
        return {
            "sequence": self.sequence,
            "workspace_id": self.workspace_id,
            "from_status": self.from_status.value,
            "to_status": self.to_status.value,
            "tick": self.tick,
        }


__all__ = [
    "allowed_transitions",
    "can_transition",
    "validate_transition",
    "WorkspaceEvent",
]
