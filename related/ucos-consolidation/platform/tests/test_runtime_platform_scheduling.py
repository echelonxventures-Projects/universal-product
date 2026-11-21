"""EPIC-007 (T7) — Execution scheduling tests."""

from __future__ import annotations

from platform.runtime_platform.errors import ExecutionScheduleError
from platform.runtime_platform.scheduling import schedule
from platform.tests.runtime_platform_helpers import request

import pytest


def test_schedule_orders_by_dependency_stages():
    result = schedule(
        [
            request("a"),
            request("b", dependencies=("a",)),
            request("c", dependencies=("a",)),
            request("d", dependencies=("b", "c")),
        ]
    )
    assert result.stage_count == 3
    assert result.stage_of("a") == 0
    assert result.stage_of("b") == 1
    assert result.stage_of("d") == 2
    assert result.schedule_id.startswith("UCOS-URPS-")


def test_within_stage_priority_then_id_order():
    result = schedule(
        [request("z", priority=1), request("a", priority=1), request("m", priority=5)]
    )
    # single stage; highest priority first, then lexical id
    assert result.steps[0].workload_ids == ("m", "a", "z")


def test_schedule_ready_after_reflects_dependencies():
    result = schedule([request("a"), request("b", dependencies=("a",))])
    stage1 = result.steps[1]
    assert stage1.ready_after == ("a",)


def test_missing_dependency_fails_closed():
    with pytest.raises(ExecutionScheduleError):
        schedule([request("b", dependencies=("missing",))])


def test_cycle_fails_closed():
    # two requests with mutual dependency is impossible to construct directly (self-dep
    # is rejected at request build), so emulate a cycle via three-way references.
    a = request("a", dependencies=("c",))
    b = request("b", dependencies=("a",))
    c = request("c", dependencies=("b",))
    with pytest.raises(ExecutionScheduleError):
        schedule([a, b, c])


def test_duplicate_workload_fails_closed():
    with pytest.raises(ExecutionScheduleError):
        schedule([request("a"), request("a")])


def test_non_request_fails_closed():
    with pytest.raises(ExecutionScheduleError):
        schedule(["not-a-request"])  # type: ignore[list-item]


def test_stage_of_unknown_raises():
    result = schedule([request("a")])
    with pytest.raises(ExecutionScheduleError):
        result.stage_of("zzz")


def test_schedule_is_deterministic():
    reqs = [request("a"), request("b", dependencies=("a",))]
    assert schedule(reqs).fingerprint() == schedule(list(reqs)).fingerprint()
    assert schedule(reqs).to_dict()["parallelism"] == 1
