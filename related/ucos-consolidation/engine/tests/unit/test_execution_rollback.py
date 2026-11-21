"""EPIC-RTE-002 — Execution Rollback unit tests."""

from __future__ import annotations

import pytest

from engine.runtime.execution.coordinator import coordinate
from engine.runtime.execution.errors import RollbackError
from engine.runtime.execution.rollback import (
    ROLLBACK_PLAN_FORMAT,
    rollback,
    rollback_plan,
)
from engine.runtime.execution.state import FAILED, ROLLED_BACK, ROLLED_BACK_RUN


def test_rollback_plan_is_reverse_order(composition):
    run = coordinate(composition)
    plan = rollback_plan(run)
    assert set(plan.order) == {"A", "B", "C", "D"}
    # leaf (D) reversed first, root (A) last
    assert plan.order[0] == "D"
    assert plan.order[-1] == "A"
    assert not plan.is_empty
    assert plan.plan_id.startswith("UCOS-EXEC-RBACK-")


def test_rollback_plan_to_dict(composition):
    blob = rollback_plan(coordinate(composition)).to_dict()
    assert blob["rollback_plan_format"] == ROLLBACK_PLAN_FORMAT
    assert len(blob["order"]) == 4


def test_rollback_reverses_completed(composition):
    rolled = rollback(coordinate(composition))
    assert {s.status for s in rolled.states} == {ROLLED_BACK}
    assert rolled.status == ROLLED_BACK_RUN
    assert rolled.run_id.startswith("UCOS-EXEC-RUN-")
    assert len(rolled.audit) == 4  # one rollback event per completed universe


def test_rollback_only_reverses_completed(composition):
    # A fails, dependents skipped → nothing completed → cannot roll back
    run = coordinate(composition, outcomes={"A": FAILED})
    assert rollback_plan(run).is_empty
    with pytest.raises(RollbackError) as exc:
        rollback(run)
    assert exc.value.code == "RT-EXEC-RBACK-001"


def test_rollback_partial_completed(composition):
    # D skipped by operator; A,B,C complete → those three roll back, D stays skipped
    run = coordinate(composition, outcomes={"D": FAILED})
    plan = rollback_plan(run)
    assert set(plan.order) == {"A", "B", "C"}
    rolled = rollback(run)
    statuses = {s.universe_id: s.status for s in rolled.states}
    assert statuses["A"] == ROLLED_BACK
    assert statuses["D"] == FAILED


def test_rollback_is_deterministic(composition):
    run = coordinate(composition)
    assert rollback(run).run_id == rollback(run).run_id
