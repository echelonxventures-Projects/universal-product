"""EPIC-RTE-002 — Execution Replay unit tests."""

from __future__ import annotations

import json

import pytest

from engine.runtime.execution.coordinator import coordinate
from engine.runtime.execution.errors import ReplayError
from engine.runtime.execution.replay import replay, requested_outcomes
from engine.runtime.execution.state import FAILED, SKIPPED


def test_requested_outcomes_empty_for_all_complete(composition):
    assert requested_outcomes(coordinate(composition)) == {}


def test_requested_outcomes_recovers_failure_only(composition):
    run = coordinate(composition, outcomes={"A": FAILED})
    # A failed is recovered; B/C blocked-skips are NOT requested outcomes
    assert requested_outcomes(run) == {"A": FAILED}


def test_requested_outcomes_recovers_operator_skip(composition):
    run = coordinate(composition, outcomes={"D": SKIPPED})
    assert requested_outcomes(run) == {"D": SKIPPED}


def test_replay_reproduces_byte_for_byte(composition):
    run = coordinate(composition, outcomes={"A": FAILED})
    replayed = replay(composition, run)
    assert replayed.run_id == run.run_id
    assert json.dumps(replayed.to_dict(), sort_keys=True) == json.dumps(
        run.to_dict(), sort_keys=True
    )


def test_replay_of_clean_run(composition):
    run = coordinate(composition)
    assert replay(composition, run).run_id == run.run_id


def test_replay_rejects_foreign_composition(composition, make_composition):
    run = coordinate(composition)
    other = make_composition("sequential")  # different coordination → different id
    with pytest.raises(ReplayError) as exc:
        replay(other, run)
    assert exc.value.code == "RT-EXEC-REPLAY-001"
