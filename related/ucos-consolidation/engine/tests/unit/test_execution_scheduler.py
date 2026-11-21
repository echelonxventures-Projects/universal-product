"""EPIC-RTE-002 — Execution Scheduler unit tests."""

from __future__ import annotations

import json

import pytest

from engine.runtime.execution.scheduler import (
    EXECUTION_SCHEDULE_FORMAT,
    ScheduledStep,
    schedule,
)


def test_schedule_concurrent_groups_levels(make_composition):
    composition = make_composition("concurrent")
    sched = schedule(composition)
    assert sched.coordination == "concurrent"
    # diamond: [A], [B,C], [D]
    assert [s.universe_ids for s in sched.steps] == [("A",), ("B", "C"), ("D",)]
    assert sched.parallelism == 2
    assert sched.stage_count == 3
    assert sched.schedule_id.startswith("UCOS-EXEC-SCHED-")


def test_schedule_ready_after_records_dependencies(make_composition):
    sched = schedule(make_composition("concurrent"))
    ready = {s.stage: s.ready_after for s in sched.steps}
    assert ready[0] == ()
    assert ready[1] == ("A",)
    assert ready[2] == ("B", "C")


def test_schedule_sequential(make_composition):
    sched = schedule(make_composition("sequential"))
    assert sched.parallelism == 1
    assert sched.stage_count == 4


def test_stage_of_and_stage_map(make_composition):
    sched = schedule(make_composition("concurrent"))
    assert sched.stage_of("A") == 0
    assert sched.stage_of("D") == 2
    assert sched.stage_map() == {"A": 0, "B": 1, "C": 1, "D": 2}


def test_stage_of_unknown_raises(make_composition):
    sched = schedule(make_composition("concurrent"))
    with pytest.raises(KeyError):
        sched.stage_of("ZZ")


def test_schedule_is_deterministic(make_composition):
    a = schedule(make_composition("concurrent"))
    b = schedule(make_composition("concurrent"))
    assert a.schedule_id == b.schedule_id
    assert json.dumps(a.to_dict(), sort_keys=True) == json.dumps(b.to_dict(), sort_keys=True)


def test_schedule_to_dict(make_composition):
    blob = schedule(make_composition("concurrent")).to_dict()
    assert blob["execution_schedule_format"] == EXECUTION_SCHEDULE_FORMAT
    assert blob["parallelism"] == 2


def test_scheduled_step_to_dict():
    step = ScheduledStep(stage=1, universe_ids=("B", "C"), ready_after=("A",))
    assert step.to_dict() == {
        "stage": 1,
        "universe_ids": ["B", "C"],
        "ready_after": ["A"],
    }
