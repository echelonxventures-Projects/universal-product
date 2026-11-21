"""EPIC-007 (T7) — Execution lifecycle transition-model tests."""

from __future__ import annotations

from platform.runtime_platform.errors import RuntimeLifecycleError
from platform.runtime_platform.lifecycle import (
    CANCELLED,
    COMPENSATED,
    EXECUTION_STATES,
    FAILED,
    PENDING,
    PLACED,
    RUNNING,
    SCHEDULED,
    SUCCEEDED,
    allowed_transitions,
    can_transition,
    is_settled,
    is_terminal,
    require_state,
    require_transition,
    validate_trajectory,
)

import pytest


def test_state_set_is_complete():
    assert set(EXECUTION_STATES) == {
        PENDING,
        SCHEDULED,
        PLACED,
        RUNNING,
        SUCCEEDED,
        FAILED,
        COMPENSATED,
        CANCELLED,
    }


def test_require_state_rejects_unknown():
    assert require_state(RUNNING) == RUNNING
    with pytest.raises(RuntimeLifecycleError):
        require_state("bogus")


def test_allowed_and_can_transition():
    assert allowed_transitions(RUNNING) == (SUCCEEDED, FAILED)
    assert can_transition(PENDING, SCHEDULED)
    assert not can_transition(PENDING, RUNNING)


def test_terminal_and_settled():
    assert is_terminal(COMPENSATED)
    assert is_terminal(CANCELLED)
    assert not is_terminal(RUNNING)
    assert is_settled(SUCCEEDED)
    assert is_settled(FAILED)
    assert not is_settled(RUNNING)


def test_require_transition_ok_and_fail():
    assert require_transition(FAILED, SCHEDULED) == SCHEDULED
    with pytest.raises(RuntimeLifecycleError):
        require_transition(SUCCEEDED, RUNNING)


def test_validate_trajectory_happy_path():
    traj = (PENDING, SCHEDULED, PLACED, RUNNING, SUCCEEDED)
    assert validate_trajectory(traj) == traj


def test_validate_trajectory_rejects_empty_or_bad_start_or_illegal():
    with pytest.raises(RuntimeLifecycleError):
        validate_trajectory(())
    with pytest.raises(RuntimeLifecycleError):
        validate_trajectory((RUNNING, SUCCEEDED))
    with pytest.raises(RuntimeLifecycleError):
        validate_trajectory((PENDING, RUNNING))
