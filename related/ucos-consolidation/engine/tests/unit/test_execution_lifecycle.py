"""EPIC-RTE-002 — Execution Lifecycle unit tests."""

from __future__ import annotations

import pytest

from engine.runtime.execution.errors import ExecutionLifecycleError
from engine.runtime.execution.lifecycle import (
    LIFECYCLE_TRANSITIONS,
    allowed_transitions,
    can_transition,
    require_transition,
)
from engine.runtime.execution.state import (
    COMPLETED,
    FAILED,
    PENDING,
    READY,
    ROLLED_BACK,
    RUNNING,
    SKIPPED,
)


def test_transition_table_is_closed_over_known_states():
    for _source, targets in LIFECYCLE_TRANSITIONS.items():
        for target in targets:
            assert target in LIFECYCLE_TRANSITIONS


def test_allowed_transitions():
    assert allowed_transitions(PENDING) == (READY, SKIPPED)
    assert allowed_transitions(SKIPPED) == ()


def test_can_transition_legal_and_illegal():
    assert can_transition(PENDING, READY)
    assert can_transition(RUNNING, COMPLETED)
    assert can_transition(RUNNING, FAILED)
    assert can_transition(COMPLETED, ROLLED_BACK)
    assert can_transition(FAILED, READY)
    assert not can_transition(PENDING, RUNNING)
    assert not can_transition(COMPLETED, RUNNING)


def test_require_transition_returns_target_when_legal():
    assert require_transition(READY, RUNNING) == RUNNING


def test_require_transition_raises_when_illegal():
    with pytest.raises(ExecutionLifecycleError) as exc:
        require_transition(SKIPPED, RUNNING)
    assert exc.value.code == "RT-EXEC-LIFE-001"
    assert exc.value.context["source"] == SKIPPED
    assert exc.value.context["target"] == RUNNING


def test_require_transition_rejects_unknown_state():
    with pytest.raises(ExecutionLifecycleError):
        require_transition("mystery", READY)
