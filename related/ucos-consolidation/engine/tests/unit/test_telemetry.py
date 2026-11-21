"""Tests for TASK-000007 telemetry (metrics + traces)."""

from __future__ import annotations

import pytest

from engine.foundation.obs import context, telemetry


@pytest.fixture(autouse=True)
def _clean_metrics():
    telemetry.reset_metrics()
    yield
    telemetry.reset_metrics()


def test_counter_accumulates():
    telemetry.metric_counter("jobs", 1, stage="parse")
    telemetry.metric_counter("jobs", 2, stage="parse")
    snapshot = telemetry.metrics_snapshot()
    assert snapshot["counters"]["jobs"]["value"] == 3
    assert snapshot["counters"]["jobs"]["stage"] == "parse"


def test_gauge_sets_latest():
    telemetry.metric_gauge("queue_depth", 5)
    telemetry.metric_gauge("queue_depth", 2)
    assert telemetry.metrics_snapshot()["gauges"]["queue_depth"]["value"] == 2


def test_histogram_records_samples():
    telemetry.metric_histogram("latency", 10.0)
    telemetry.metric_histogram("latency", 30.0)
    hist = telemetry.metrics_snapshot()["histograms"]["latency"]
    assert hist["count"] == 2
    assert hist["sum"] == 40.0


def test_trace_binds_and_resets_correlation_id():
    assert context.correlation_id() is None
    with telemetry.trace("compile") as cid:
        assert cid is not None
        assert context.correlation_id() == cid
    # id is reset after the span when it was created by the span
    assert context.correlation_id() is None


def test_trace_preserves_existing_correlation_id():
    token = context.set_correlation_id("outer")
    try:
        with telemetry.trace("inner") as cid:
            assert cid == "outer"
        assert context.correlation_id() == "outer"
    finally:
        context.reset_correlation_id(token)


def test_trace_records_ok_metrics():
    with telemetry.trace("ok-span"):
        pass
    snapshot = telemetry.metrics_snapshot()
    assert snapshot["counters"]["span.count"]["value"] == 1
    assert snapshot["counters"]["span.count"]["outcome"] == "ok"
    assert snapshot["histograms"]["span.duration_ms"]["count"] == 1


def test_trace_records_error_and_reraises():
    with pytest.raises(ValueError):
        with telemetry.trace("bad-span"):
            raise ValueError("boom")
    snapshot = telemetry.metrics_snapshot()
    assert snapshot["counters"]["span.count"]["outcome"] == "error"
    # correlation id created for the failed span is cleaned up
    assert context.correlation_id() is None


def test_new_correlation_id_generates_unique():
    first = telemetry.new_correlation_id()
    second = telemetry.new_correlation_id()
    assert first != second
    assert context.correlation_id() == second


def test_set_correlation_id_rejects_empty():
    with pytest.raises(ValueError):
        context.set_correlation_id("")
