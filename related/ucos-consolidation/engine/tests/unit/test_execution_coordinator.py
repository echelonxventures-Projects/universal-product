"""EPIC-RTE-002 — Execution Coordinator unit tests."""

from __future__ import annotations

import json

import pytest

from engine.runtime.execution.coordinator import (
    EXECUTION_RUN_FORMAT,
    REQUESTABLE_OUTCOMES,
    coordinate,
)
from engine.runtime.execution.errors import ExecutionScheduleError
from engine.runtime.execution.state import (
    COMPLETED,
    FAILED,
    PARTIAL,
    RUN_FAILED,
    SKIPPED,
    SUCCEEDED,
)


def test_coordinate_all_complete_by_default(composition):
    run = coordinate(composition)
    assert run.status == SUCCEEDED
    assert {s.status for s in run.states} == {COMPLETED}
    assert run.run_id.startswith("UCOS-EXEC-RUN-")
    # 4 universes × 3 transitions each (pending→ready→running→completed)
    assert len(run.audit) == 12


def test_coordinate_failure_propagates_to_dependents(composition):
    run = coordinate(composition, outcomes={"A": FAILED})
    states = {s.universe_id: s.status for s in run.states}
    assert states["A"] == FAILED
    # B, C depend on A → skipped; D depends on B,C → skipped
    assert states["B"] == SKIPPED
    assert states["C"] == SKIPPED
    assert states["D"] == SKIPPED
    assert run.status == RUN_FAILED


def test_coordinate_operator_skip_is_partial(composition):
    run = coordinate(composition, outcomes={"D": SKIPPED})
    states = {s.universe_id: s.status for s in run.states}
    assert states["D"] == SKIPPED
    assert states["A"] == COMPLETED
    assert run.status == PARTIAL
    assert run.state_of("D").outcome == "operator-skipped"


def test_blocked_detail_names_dependency(composition):
    run = coordinate(composition, outcomes={"A": FAILED})
    assert run.state_of("B").outcome == "blocked-by:A"


def test_coordinate_is_deterministic(composition):
    a = coordinate(composition, outcomes={"A": FAILED})
    b = coordinate(composition, outcomes={"A": FAILED})
    assert a.run_id == b.run_id
    assert json.dumps(a.to_dict(), sort_keys=True) == json.dumps(b.to_dict(), sort_keys=True)


def test_outcomes_change_run_identity(composition):
    assert coordinate(composition).run_id != coordinate(composition, outcomes={"A": FAILED}).run_id


def test_state_of_unknown_raises(composition):
    run = coordinate(composition)
    with pytest.raises(ExecutionScheduleError):
        run.state_of("ZZ")


def test_universes_in(composition):
    run = coordinate(composition, outcomes={"A": FAILED})
    assert run.universes_in(FAILED) == ("A",)
    assert run.universes_in(SKIPPED) == ("B", "C", "D")


def test_state_map_and_composition_id(composition):
    run = coordinate(composition)
    assert set(run.state_map()) == {"A", "B", "C", "D"}
    assert run.composition_id == composition.composition_id


def test_outcomes_reject_unknown_universe(composition):
    with pytest.raises(ExecutionScheduleError) as exc:
        coordinate(composition, outcomes={"ZZ": COMPLETED})
    assert exc.value.code == "RT-EXEC-SCHED-001"


def test_outcomes_reject_unknown_value(composition):
    with pytest.raises(ExecutionScheduleError):
        coordinate(composition, outcomes={"A": "exploded"})


def test_requestable_outcomes_constant():
    assert set(REQUESTABLE_OUTCOMES) == {COMPLETED, FAILED, SKIPPED}


def test_run_descriptor_shape(composition):
    blob = coordinate(composition).to_dict()
    assert blob["execution_run_format"] == EXECUTION_RUN_FORMAT
    assert blob["authority"] == "ENGINEERING-EXECUTION-ONLY"
    assert blob["provisional_state_disclosure"]["gate"] == "EC-1"
    assert "schedule" in blob and "states" in blob and "audit" in blob


def test_empty_outcomes_mapping_is_all_complete(composition):
    assert coordinate(composition, outcomes={}).status == SUCCEEDED
