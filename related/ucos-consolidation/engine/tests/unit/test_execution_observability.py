"""EPIC-RTE-002 — Execution observability unit tests (monitor/metrics/health/diagnostics)."""

from __future__ import annotations

from engine.foundation.obs.telemetry import metrics_snapshot, reset_metrics
from engine.runtime.execution.coordinator import coordinate
from engine.runtime.execution.diagnostics import DIAGNOSTICS_FORMAT, diagnose
from engine.runtime.execution.health import (
    DEGRADED,
    HEALTHY,
    UNHEALTHY,
    health,
)
from engine.runtime.execution.metrics import METRICS_FORMAT, execution_metrics
from engine.runtime.execution.monitoring import MONITOR_FORMAT, monitor
from engine.runtime.execution.state import COMPLETED, FAILED, SKIPPED

# ---- monitoring ----------------------------------------------------------- #


def test_monitor_complete_run(composition):
    mon = monitor(coordinate(composition))
    assert mon.total == 4
    assert mon.by_state[COMPLETED] == 4
    assert mon.is_complete
    assert mon.completed_fraction == 1.0
    assert mon.terminal_count == 4
    assert mon.transitions == 12
    assert mon.stage_count == 3
    assert mon.parallelism == 2


def test_monitor_to_dict(composition):
    blob = monitor(coordinate(composition)).to_dict()
    assert blob["monitor_format"] == MONITOR_FORMAT
    assert blob["is_complete"] is True


def test_monitor_zero_total_is_complete():
    # The total==0 guard is unreachable via coordinate (a composition has ≥1
    # universe), so it is exercised directly on the value object.
    from engine.runtime.execution.monitoring import ExecutionMonitor
    from engine.runtime.execution.state import EXECUTION_STATES

    mon = ExecutionMonitor(
        run_id="R",
        status="succeeded",
        total=0,
        by_state={s: 0 for s in EXECUTION_STATES},
        transitions=0,
        stage_count=0,
        parallelism=0,
    )
    assert mon.completed_fraction == 1.0
    assert mon.is_complete


# ---- metrics -------------------------------------------------------------- #


def test_metrics_counts_and_ratio(composition):
    metrics = execution_metrics(coordinate(composition, outcomes={"A": FAILED}))
    assert metrics.failed == 1
    assert metrics.skipped == 3
    assert metrics.completed == 0
    assert metrics.success_ratio == 0.0
    assert metrics.by_context == {"ctx1": 4}


def test_metrics_success_ratio_full(composition):
    metrics = execution_metrics(coordinate(composition))
    assert metrics.success_ratio == 1.0


def test_metrics_zero_total_success_ratio():
    # total==0 guard is unreachable via coordinate; exercised on the value object.
    from engine.runtime.execution.metrics import ExecutionMetrics

    metrics = ExecutionMetrics(
        run_id="R",
        status="succeeded",
        total=0,
        completed=0,
        failed=0,
        skipped=0,
        transitions=0,
        stage_count=0,
        parallelism=0,
        by_state={},
        by_context={},
    )
    assert metrics.success_ratio == 1.0


def test_metrics_to_dict(composition):
    blob = execution_metrics(coordinate(composition)).to_dict()
    assert blob["metrics_format"] == METRICS_FORMAT
    assert blob["total"] == 4


def test_metrics_emit_records_registry(composition):
    reset_metrics()
    execution_metrics(coordinate(composition), emit=True)
    snap = metrics_snapshot()
    assert "execution.universes" in snap["gauges"]
    assert "execution.transitions" in snap["counters"]
    reset_metrics()


# ---- health --------------------------------------------------------------- #


def test_health_healthy(composition):
    assert health(coordinate(composition)).health == HEALTHY
    assert health(coordinate(composition)).healthy


def test_health_failed(composition):
    assert health(coordinate(composition, outcomes={"A": FAILED})).health == UNHEALTHY


def test_health_degraded_when_skipped(composition):
    assert health(coordinate(composition, outcomes={"D": SKIPPED})).health == DEGRADED


def test_health_ignores_non_terminal_states_defensively(composition):
    # health() defensively skips any state not among its counted terminal states
    # (unreachable in a normal terminal run — exercised by injecting 'pending').
    import dataclasses

    run = coordinate(composition)
    injected = dataclasses.replace(
        run,
        states=(*run.states[:-1], run.states[-1].with_status("pending")),
    )
    assert health(injected).health == HEALTHY


def test_health_to_dict(composition):
    blob = health(coordinate(composition)).to_dict()
    assert blob["health"] == HEALTHY
    assert blob["completed"] == 4


# ---- diagnostics ---------------------------------------------------------- #


def test_diagnose_clean_when_all_complete(composition):
    report = diagnose(coordinate(composition))
    assert report.clean
    assert report.findings == ()


def test_diagnose_reports_failure_and_blocked(composition):
    report = diagnose(coordinate(composition, outcomes={"A": FAILED}))
    assert not report.clean
    by_id = {f.universe_id: f for f in report.findings}
    assert by_id["A"].status == FAILED
    assert by_id["B"].status == SKIPPED
    assert by_id["B"].blocked_by == ("A",)
    assert "dependency" in by_id["B"].reason


def test_diagnose_operator_skip_reason(composition):
    report = diagnose(coordinate(composition, outcomes={"D": SKIPPED}))
    finding = {f.universe_id: f for f in report.findings}["D"]
    assert finding.blocked_by == ()
    assert "operator" in finding.reason


def test_diagnostics_to_dict(composition):
    blob = diagnose(coordinate(composition, outcomes={"A": FAILED})).to_dict()
    assert blob["diagnostics_format"] == DIAGNOSTICS_FORMAT
    assert blob["clean"] is False
    assert blob["finding_count"] >= 1
