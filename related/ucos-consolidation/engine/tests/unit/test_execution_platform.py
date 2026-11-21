"""EPIC-RTE-002 — Universal Runtime Execution Platform facade unit tests."""

from __future__ import annotations

import json

import pytest

from engine.runtime.execution.platform import (
    EXECUTION_RESULT_FORMAT,
    ExecutionPlatform,
    ExecutionResult,
)
from engine.runtime.execution.state import FAILED, SUCCEEDED


@pytest.fixture
def platform() -> ExecutionPlatform:
    return ExecutionPlatform()


def test_end_to_end_run_bundles_observations(platform, composition):
    result = platform.run(composition)
    assert isinstance(result, ExecutionResult)
    assert result.status == SUCCEEDED
    assert result.run_id == result.run.run_id
    assert result.monitor.is_complete
    assert result.metrics.total == 4
    assert result.health.healthy
    assert result.diagnostics.clean
    assert result.snapshot.run_id == result.run_id


def test_result_to_dict(platform, composition):
    blob = platform.run(composition).to_dict()
    assert blob["execution_result_format"] == EXECUTION_RESULT_FORMAT
    for key in ("run", "monitor", "metrics", "health", "diagnostics", "snapshot"):
        assert key in blob


def test_run_is_deterministic(platform, composition):
    a = platform.run(composition)
    b = platform.run(composition)
    assert json.dumps(a.to_dict(), sort_keys=True) == json.dumps(b.to_dict(), sort_keys=True)


def test_authorize_isolate_federate_schedule(platform, composition):
    assert platform.authorize(composition).granted
    assert len(platform.isolate(composition).partitions) == 1
    assert platform.federate(composition).links == ()
    assert platform.schedule(composition).stage_count == 3


def test_execute_and_observability_methods(platform, composition):
    run = platform.execute(composition, outcomes={"A": FAILED})
    assert run.status == FAILED
    assert platform.monitor(run).total == 4
    assert platform.metrics(run).failed == 1
    assert platform.metrics(run, emit=False).failed == 1
    assert platform.health(run).health == "failed"
    assert not platform.diagnose(run).clean
    assert platform.snapshot(run).run_id == run.run_id


def test_checkpoint_continue_recover(platform, composition):
    run = platform.execute(composition)
    cp = platform.checkpoint(run, through_stage=0)
    resumed = platform.continue_from(composition, cp)
    assert platform.verify_continuation(run, resumed)
    assert platform.recover(run).run_id == run.run_id
    again = platform.recover_and_continue(composition, run)
    assert platform.verify_continuation(run, again)


def test_rollback_methods(platform, composition):
    run = platform.execute(composition)
    assert not platform.rollback_plan(run).is_empty
    rolled = platform.rollback(run)
    assert rolled.status == "rolled_back"


def test_persistence_methods(platform, composition):
    run = platform.execute(composition)
    cp = platform.checkpoint(run)
    assert platform.restore_checkpoint(platform.persist_checkpoint(cp)) == cp
    assert platform.persist_snapshot(platform.snapshot(run))
    assert platform.persist_run(run)


def test_replay_methods(platform, composition):
    run = platform.execute(composition, outcomes={"A": FAILED})
    assert platform.replay(composition, run).run_id == run.run_id
    assert platform.validate_replay(composition, run).valid
    assert platform.require_replay(composition, run).valid
