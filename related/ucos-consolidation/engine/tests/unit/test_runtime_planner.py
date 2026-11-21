"""TASK-000040 — Runtime Execution Planner unit tests (EPIC-006).

Exercises the three coordination classes (sequential/concurrent/conditional) and
the recorded, deterministic plan structure (RUNTIME-013 §D9; ORL-15/ORL-20).
"""

from __future__ import annotations

import pytest

from engine.runtime.errors import ExecutionPlanError
from engine.runtime.graph import RuntimeGraph
from engine.runtime.planner import (
    COORDINATION_CLASSES,
    EXECUTION_PLAN_FORMAT,
    PlanStep,
    plan_execution,
)


@pytest.fixture
def diamond() -> RuntimeGraph:
    return RuntimeGraph.of({"a": (), "b": ("a",), "c": ("a",), "d": ("b", "c")})


def test_plan_step_to_dict():
    step = PlanStep(stage=2, universe_ids=("a", "b"), condition_on=("x",))
    assert step.to_dict() == {
        "stage": 2,
        "universe_ids": ["a", "b"],
        "condition_on": ["x"],
    }


def test_unknown_coordination_rejected(diamond):
    with pytest.raises(ExecutionPlanError) as exc:
        plan_execution(diamond, coordination="parallelised")
    assert exc.value.code == "RT-PLAN-001"


def test_sequential_plan(diamond):
    plan = plan_execution(diamond, coordination="sequential")
    assert plan.stage_count == 4
    assert plan.parallelism == 1
    assert [s.universe_ids for s in plan.steps] == [("a",), ("c",), ("b",), ("d",)]
    assert all(s.condition_on == () for s in plan.steps)


def test_concurrent_plan_groups_levels(diamond):
    plan = plan_execution(diamond, coordination="concurrent")
    assert plan.parallelism == 2
    assert [s.universe_ids for s in plan.steps] == [("a",), ("b", "c"), ("d",)]
    assert plan.steps[1].condition_on == ("a",)
    assert plan.steps[2].condition_on == ("b", "c")


def test_conditional_plan_records_conditions(diamond):
    plan = plan_execution(diamond, coordination="conditional")
    assert plan.stage_count == 4
    conditions = {s.universe_ids[0]: s.condition_on for s in plan.steps}
    assert conditions["a"] == ()
    assert conditions["d"] == ("b", "c")


def test_empty_graph_plan_has_zero_parallelism():
    plan = plan_execution(RuntimeGraph({}))
    assert plan.stage_count == 0
    assert plan.parallelism == 0


def test_plan_to_dict(diamond):
    blob = plan_execution(diamond, coordination="concurrent").to_dict()
    assert blob["execution_plan_format"] == EXECUTION_PLAN_FORMAT
    assert blob["coordination"] == "concurrent"
    assert blob["order"] == ["a", "c", "b", "d"]
    assert blob["parallelism"] == 2


def test_all_coordination_classes_supported(diamond):
    for coordination in COORDINATION_CLASSES:
        assert plan_execution(diamond, coordination=coordination).coordination == (coordination)
