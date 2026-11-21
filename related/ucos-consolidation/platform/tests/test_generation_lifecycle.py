"""EC2-TASK-000110 — Generation request lifecycle tests (EC2-EPIC-007).

Covers the deterministic request state machine: legal edges, fail-closed rejection of
illegal edges and edges out of terminal states, and the append-only RequestEvent.
"""

from __future__ import annotations

from platform.generation.contracts import RequestStatus
from platform.generation.errors import RequestLifecycleError
from platform.generation.lifecycle import (
    RequestEvent,
    allowed_transitions,
    can_transition,
    validate_transition,
)

import pytest

_LEGAL = {
    RequestStatus.SUBMITTED: {RequestStatus.VALIDATING, RequestStatus.CANCELLED},
    RequestStatus.VALIDATING: {
        RequestStatus.APPROVED,
        RequestStatus.FAILED,
        RequestStatus.CANCELLED,
    },
    RequestStatus.APPROVED: {RequestStatus.QUEUED, RequestStatus.CANCELLED},
    RequestStatus.QUEUED: {RequestStatus.DISPATCHED, RequestStatus.CANCELLED},
    RequestStatus.DISPATCHED: {
        RequestStatus.RUNNING,
        RequestStatus.FAILED,
        RequestStatus.CANCELLED,
    },
    RequestStatus.RUNNING: {RequestStatus.COMPLETED, RequestStatus.FAILED},
    RequestStatus.COMPLETED: set(),
    RequestStatus.FAILED: set(),
    RequestStatus.CANCELLED: set(),
}


def test_allowed_transitions_match_specification():
    for status, targets in _LEGAL.items():
        assert set(allowed_transitions(status)) == targets


def test_allowed_transitions_stable_order():
    order = allowed_transitions(RequestStatus.VALIDATING)
    assert order == tuple(s for s in RequestStatus if s in set(order))


def test_allowed_transitions_rejects_non_status():
    with pytest.raises(RequestLifecycleError):
        allowed_transitions("submitted")  # type: ignore[arg-type]


def test_can_transition_true_and_false():
    assert can_transition(RequestStatus.SUBMITTED, RequestStatus.VALIDATING) is True
    assert can_transition(RequestStatus.SUBMITTED, RequestStatus.RUNNING) is False
    # No self-transition.
    assert can_transition(RequestStatus.QUEUED, RequestStatus.QUEUED) is False


def test_can_transition_rejects_non_status():
    with pytest.raises(RequestLifecycleError):
        can_transition("a", RequestStatus.VALIDATING)  # type: ignore[arg-type]
    with pytest.raises(RequestLifecycleError):
        can_transition(RequestStatus.SUBMITTED, "b")  # type: ignore[arg-type]


def test_validate_transition_legal_is_noop():
    assert validate_transition(RequestStatus.QUEUED, RequestStatus.DISPATCHED) is None


def test_validate_transition_illegal_raises():
    with pytest.raises(RequestLifecycleError):
        validate_transition(RequestStatus.COMPLETED, RequestStatus.RUNNING)
    with pytest.raises(RequestLifecycleError):
        validate_transition(RequestStatus.SUBMITTED, RequestStatus.DISPATCHED)


def test_terminal_states_have_no_outgoing_edges():
    for terminal in (RequestStatus.COMPLETED, RequestStatus.FAILED, RequestStatus.CANCELLED):
        assert allowed_transitions(terminal) == ()


def test_request_event_serialization():
    event = RequestEvent(
        sequence=0,
        request_id="UCOS-GREQ-1",
        from_status=RequestStatus.QUEUED,
        to_status=RequestStatus.DISPATCHED,
        tick=5,
    )
    assert event.to_dict() == {
        "sequence": 0,
        "request_id": "UCOS-GREQ-1",
        "from_status": "queued",
        "to_status": "dispatched",
        "tick": 5,
    }
