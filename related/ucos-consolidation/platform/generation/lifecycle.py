"""EC2-TASK-000110 — Generation Request Lifecycle (EC2-EPIC-007).

The deterministic generation-request **state machine** and its append-only transition
event (Program §2.1 #8, PC-06/PC-07, §5 acceptance). A request occupies exactly one
:class:`~platform.generation.contracts.RequestStatus` at a time; transitions are a
pure, fail-closed function of the current and target status (IMP-007 §5 determinism):

    SUBMITTED  ─▶ VALIDATING · CANCELLED
    VALIDATING ─▶ APPROVED · FAILED · CANCELLED
    APPROVED   ─▶ QUEUED · CANCELLED
    QUEUED     ─▶ DISPATCHED · CANCELLED
    DISPATCHED ─▶ RUNNING · FAILED · CANCELLED
    RUNNING    ─▶ COMPLETED · FAILED
    COMPLETED  ─▶ (terminal)
    FAILED     ─▶ (terminal)
    CANCELLED  ─▶ (terminal)

An illegal transition (unknown edge, any edge out of a terminal state, or a no-op
self-transition) raises :class:`RequestLifecycleError`. Each accepted transition is
recorded as an immutable, ordered :class:`RequestEvent` (no wall-clock; a
caller-supplied logical ``tick``) so the lifecycle history is reproducible and
append-only (OP-C3). This mirrors the certified
:mod:`platform.blueprints.lifecycle` state-machine pattern exactly (proven template).
"""

from __future__ import annotations

from dataclasses import dataclass
from platform.generation.contracts import RequestStatus
from platform.generation.errors import RequestLifecycleError
from typing import Any

#: The legal state-machine edges: current status → the statuses it may transition to.
_TRANSITIONS: dict[RequestStatus, frozenset[RequestStatus]] = {
    RequestStatus.SUBMITTED: frozenset({RequestStatus.VALIDATING, RequestStatus.CANCELLED}),
    RequestStatus.VALIDATING: frozenset(
        {RequestStatus.APPROVED, RequestStatus.FAILED, RequestStatus.CANCELLED}
    ),
    RequestStatus.APPROVED: frozenset({RequestStatus.QUEUED, RequestStatus.CANCELLED}),
    RequestStatus.QUEUED: frozenset({RequestStatus.DISPATCHED, RequestStatus.CANCELLED}),
    RequestStatus.DISPATCHED: frozenset(
        {RequestStatus.RUNNING, RequestStatus.FAILED, RequestStatus.CANCELLED}
    ),
    RequestStatus.RUNNING: frozenset({RequestStatus.COMPLETED, RequestStatus.FAILED}),
    RequestStatus.COMPLETED: frozenset(),
    RequestStatus.FAILED: frozenset(),
    RequestStatus.CANCELLED: frozenset(),
}


def allowed_transitions(status: RequestStatus) -> tuple[RequestStatus, ...]:
    """Return the statuses ``status`` may transition to (stable order)."""
    if not isinstance(status, RequestStatus):
        raise RequestLifecycleError("status must be a RequestStatus")
    targets = _TRANSITIONS[status]
    return tuple(s for s in RequestStatus if s in targets)


def can_transition(current: RequestStatus, target: RequestStatus) -> bool:
    """True iff ``current`` may transition to ``target`` (pure, deterministic)."""
    if not isinstance(current, RequestStatus) or not isinstance(target, RequestStatus):
        raise RequestLifecycleError("transition endpoints must be RequestStatus")
    return target in _TRANSITIONS[current]


def validate_transition(current: RequestStatus, target: RequestStatus) -> None:
    """Raise :class:`RequestLifecycleError` unless ``current → target`` is legal."""
    if not can_transition(current, target):
        raise RequestLifecycleError(
            "illegal generation-request lifecycle transition",
            current=current.value,
            target=target.value,
        )


@dataclass(frozen=True, slots=True)
class RequestEvent:
    """An immutable, ordered record of a request lifecycle transition (append-only)."""

    sequence: int
    request_id: str
    from_status: RequestStatus
    to_status: RequestStatus
    tick: int

    def to_dict(self) -> dict[str, Any]:
        return {
            "sequence": self.sequence,
            "request_id": self.request_id,
            "from_status": self.from_status.value,
            "to_status": self.to_status.value,
            "tick": self.tick,
        }


__all__ = [
    "allowed_transitions",
    "can_transition",
    "validate_transition",
    "RequestEvent",
]
