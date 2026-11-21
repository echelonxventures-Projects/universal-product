"""EPIC-RTE-002 — Execution State unit tests."""

from __future__ import annotations

import pytest

from engine.runtime.execution.errors import ExecutionLifecycleError
from engine.runtime.execution.state import (
    COMPLETED,
    FAILED,
    PARTIAL,
    PENDING,
    ROLLED_BACK,
    ROLLED_BACK_RUN,
    RUN_FAILED,
    SKIPPED,
    SUCCEEDED,
    UniverseExecutionState,
    derive_run_status,
    is_terminal,
    require_state,
)


def _state(uid, status, *, stage=0, context="ctx1", depends_on=(), outcome=""):
    return UniverseExecutionState(
        universe_id=uid,
        context_id=context,
        stage=stage,
        status=status,
        depends_on=tuple(depends_on),
        outcome=outcome,
    )


def test_is_terminal():
    assert is_terminal(COMPLETED)
    assert is_terminal(FAILED)
    assert is_terminal(SKIPPED)
    assert is_terminal(ROLLED_BACK)
    assert not is_terminal(PENDING)


def test_require_state_accepts_known_and_rejects_unknown():
    assert require_state(COMPLETED) == COMPLETED
    with pytest.raises(ExecutionLifecycleError) as exc:
        require_state("exploded")
    assert exc.value.code == "RT-EXEC-LIFE-001"


def test_state_construction_validates_status():
    with pytest.raises(ExecutionLifecycleError):
        _state("A", "not-a-state")


def test_state_terminal_property_and_with_status():
    state = _state("A", "running")
    assert not state.terminal
    done = state.with_status(COMPLETED, outcome="outcome:completed")
    assert done.terminal
    assert done.status == COMPLETED
    assert done.outcome == "outcome:completed"
    # original is unchanged (frozen, immutable)
    assert state.status == "running"


def test_state_to_dict_and_from_dict_round_trip():
    state = _state("A", COMPLETED, stage=2, depends_on=("X", "Y"), outcome="ok")
    blob = state.to_dict()
    assert blob == {
        "universe_id": "A",
        "context_id": "ctx1",
        "stage": 2,
        "status": COMPLETED,
        "depends_on": ["X", "Y"],
        "outcome": "ok",
    }
    restored = UniverseExecutionState.from_dict(blob)
    assert restored == state


def test_from_dict_defaults_optional_fields():
    restored = UniverseExecutionState.from_dict(
        {"universe_id": "A", "context_id": "ctx1", "stage": 0, "status": PENDING}
    )
    assert restored.depends_on == ()
    assert restored.outcome == ""


def test_derive_run_status_succeeded_and_empty():
    assert derive_run_status(()) == SUCCEEDED
    assert derive_run_status((_state("A", COMPLETED),)) == SUCCEEDED


def test_derive_run_status_failed_takes_precedence():
    states = (_state("A", COMPLETED), _state("B", FAILED), _state("C", SKIPPED))
    assert derive_run_status(states) == RUN_FAILED


def test_derive_run_status_partial_when_skipped_but_no_failure():
    states = (_state("A", COMPLETED), _state("B", SKIPPED))
    assert derive_run_status(states) == PARTIAL


def test_derive_run_status_rolled_back_only_when_all_rolled_back():
    all_rb = (_state("A", ROLLED_BACK), _state("B", ROLLED_BACK))
    assert derive_run_status(all_rb) == ROLLED_BACK_RUN
    mixed = (_state("A", ROLLED_BACK), _state("B", COMPLETED))
    # not all rolled back → succeeded (no failure, no skip)
    assert derive_run_status(mixed) == SUCCEEDED
