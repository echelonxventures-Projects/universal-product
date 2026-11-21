"""EPIC-RTE-002 — Execution Recovery unit tests."""

from __future__ import annotations

from engine.runtime.execution.continuation import verify_continuation
from engine.runtime.execution.coordinator import coordinate
from engine.runtime.execution.recovery import (
    recover,
    recover_and_continue,
    recovery_stage,
)
from engine.runtime.execution.state import FAILED


def test_recovery_stage_full_success(composition):
    run = coordinate(composition)
    assert recovery_stage(run) == 2  # every stage of the diamond completed


def test_recovery_stage_first_stage_failure(composition):
    run = coordinate(composition, outcomes={"A": FAILED})
    assert recovery_stage(run) == -1


def test_recovery_stage_mid_failure_stops_at_prior(composition):
    # A (stage 0) completes; B fails at stage 1 → last clean stage is 0
    run = coordinate(composition, outcomes={"B": FAILED})
    assert recovery_stage(run) == 0


def test_recover_returns_checkpoint_at_boundary(composition):
    run = coordinate(composition, outcomes={"B": FAILED})
    cp = recover(run)
    assert cp.through_stage == 0
    assert cp.run_id == run.run_id


def test_recover_and_continue_completes(composition):
    # Recover a first-stage failure to the reset point and resume with a healthy
    # outcome — the resumed run completes successfully.
    failed = coordinate(composition, outcomes={"A": FAILED})
    resumed = recover_and_continue(composition, failed)
    assert resumed.status == "succeeded"


def test_recover_and_continue_matches_uninterrupted(composition):
    original = coordinate(composition)
    resumed = recover_and_continue(composition, original)
    assert verify_continuation(original, resumed)
