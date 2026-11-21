"""EC2-TASK-000128 — Execution dashboard domain-model tests (EC2-EPIC-008).

Covers every read-only view projection: ExecutionSnapshot (from a request + certified
derived status, with mismatch/type guards), QueueSummary, RequestMetrics (status /
execution / family censuses + success rate), RequestTrend (over the lifecycle event log,
including empty), HealthSnapshot (from a health endpoint, malformed guarded),
DashboardSummary, and DashboardView — all deterministic, content-addressed, serializable.
"""

from __future__ import annotations

from platform.blueprints.contracts import BlueprintFamily
from platform.execution_dashboard.errors import DashboardViewError
from platform.execution_dashboard.views import (
    DashboardSummary,
    DashboardView,
    ExecutionSnapshot,
    HealthSnapshot,
    QueueSummary,
    RequestMetrics,
    RequestTrend,
)
from platform.generation.contracts import ExecutionState, GenerationRequest, RequestStatus
from platform.generation.lifecycle import RequestEvent
from platform.generation.status import RequestPosture, derive_status

import pytest


def _request(
    *, slug="req", status=RequestStatus.SUBMITTED, tenant=None, family=BlueprintFamily.DATA, tick=1
):
    request = GenerationRequest.create(
        slug, "UCOS-BLPR-1", "UCOS-WSPC-1", "arch@x", family, submitted_tick=tick, tenant=tenant
    )
    return request.with_status(status)


def _derived(request, *, has_dispatch=False, has_provenance=False):
    return derive_status(request, has_dispatch=has_dispatch, has_provenance=has_provenance)


# --------------------------------------------------------------------------- #
# ExecutionSnapshot                                                            #
# --------------------------------------------------------------------------- #


def test_execution_snapshot_projects_request_and_derived():
    request = _request(status=RequestStatus.RUNNING)
    snapshot = ExecutionSnapshot.from_request(request, _derived(request, has_dispatch=True))
    assert snapshot.request_id == request.request_id
    assert snapshot.status == "running"
    assert snapshot.execution_state == ExecutionState.EXECUTING.value
    assert snapshot.posture == RequestPosture.RUNNING.value
    assert snapshot.is_dispatched is True
    assert snapshot.is_terminal is False
    assert snapshot.snapshot_id.startswith("UCOS-EDSN-")
    assert snapshot.to_dict()["family"] == "data"
    assert snapshot.fingerprint() == snapshot.fingerprint()


def test_execution_snapshot_rejects_bad_types_and_mismatch():
    request = _request()
    with pytest.raises(DashboardViewError):
        ExecutionSnapshot.from_request("nope", _derived(request))  # type: ignore[arg-type]
    with pytest.raises(DashboardViewError):
        ExecutionSnapshot.from_request(request, "nope")  # type: ignore[arg-type]
    other = _request(slug="other")
    with pytest.raises(DashboardViewError):
        ExecutionSnapshot.from_request(request, _derived(other))


# --------------------------------------------------------------------------- #
# QueueSummary                                                                 #
# --------------------------------------------------------------------------- #


def test_queue_summary_counts_pipeline_depths():
    requests = (
        _request(slug="a", status=RequestStatus.SUBMITTED),
        _request(slug="b", status=RequestStatus.QUEUED),
        _request(slug="c", status=RequestStatus.QUEUED),
        _request(slug="d", status=RequestStatus.DISPATCHED),
        _request(slug="e", status=RequestStatus.RUNNING),
        _request(slug="f", status=RequestStatus.COMPLETED),
    )
    queue = QueueSummary.from_requests(requests)
    assert queue.total == 6
    assert queue.waiting == 1
    assert queue.queue_depth == 2
    assert queue.dispatched == 1
    assert queue.running == 1
    assert queue.terminal == 1
    assert queue.active == 5
    assert queue.summary_id.startswith("UCOS-EDQS-")
    assert queue.to_dict()["status_census"]["queued"] == 2


def test_queue_summary_rejects_bad_items():
    with pytest.raises(DashboardViewError):
        QueueSummary.from_requests(["nope"])  # type: ignore[list-item]


# --------------------------------------------------------------------------- #
# RequestMetrics                                                               #
# --------------------------------------------------------------------------- #


def test_request_metrics_aggregate_and_success_rate():
    requests = (
        _request(slug="a", status=RequestStatus.COMPLETED, family=BlueprintFamily.DATA),
        _request(slug="b", status=RequestStatus.FAILED, family=BlueprintFamily.DATA),
        _request(slug="c", status=RequestStatus.QUEUED, family=BlueprintFamily.EVENT),
    )
    metrics = RequestMetrics.from_requests(requests)
    assert metrics.total == 3
    assert metrics.terminal == 2
    assert metrics.active == 1
    assert metrics.completed == 1
    assert metrics.failed == 1
    assert metrics.cancelled == 0
    assert metrics.success_rate == 0.5
    assert metrics.metrics_id.startswith("UCOS-EDMT-")
    d = metrics.to_dict()
    assert d["execution_census"][ExecutionState.SUCCEEDED.value] == 1
    assert d["family_census"]["data"] == 2


def test_request_metrics_zero_terminal_success_rate_is_zero():
    metrics = RequestMetrics.from_requests((_request(status=RequestStatus.QUEUED),))
    assert metrics.terminal == 0
    assert metrics.success_rate == 0.0


def test_request_metrics_rejects_bad_items():
    with pytest.raises(DashboardViewError):
        RequestMetrics.from_requests(["nope"])  # type: ignore[list-item]


# --------------------------------------------------------------------------- #
# RequestTrend                                                                 #
# --------------------------------------------------------------------------- #


def test_request_trend_over_events():
    events = (
        RequestEvent(0, "r1", RequestStatus.SUBMITTED, RequestStatus.VALIDATING, 1),
        RequestEvent(1, "r1", RequestStatus.VALIDATING, RequestStatus.APPROVED, 2),
        RequestEvent(2, "r1", RequestStatus.RUNNING, RequestStatus.COMPLETED, 5),
    )
    trend = RequestTrend.from_events(events)
    assert trend.total_transitions == 3
    assert trend.terminal_transitions == 1
    assert trend.first_tick == 1
    assert trend.last_tick == 5
    assert trend.trend_id.startswith("UCOS-EDTR-")
    assert trend.to_dict()["by_target"]["completed"] == 1


def test_request_trend_empty_event_log():
    trend = RequestTrend.from_events(())
    assert trend.total_transitions == 0
    assert trend.terminal_transitions == 0
    assert trend.first_tick == 0
    assert trend.last_tick == 0


def test_request_trend_rejects_bad_items():
    with pytest.raises(DashboardViewError):
        RequestTrend.from_events(["nope"])  # type: ignore[list-item]


# --------------------------------------------------------------------------- #
# HealthSnapshot                                                               #
# --------------------------------------------------------------------------- #


def _endpoint(status="healthy", healthy=True):
    return {
        "status": status,
        "healthy": healthy,
        "checks": [{"name": "c1", "status": "healthy", "detail": "ok"}],
        "report_id": "UCOS-HRPT-x",
    }


def test_health_snapshot_from_endpoint():
    snapshot = HealthSnapshot.from_endpoint(_endpoint(), source_status="healthy")
    assert snapshot.status == "healthy"
    assert snapshot.healthy is True
    assert snapshot.source_status == "healthy"
    assert snapshot.checks == (("c1", "healthy", "ok"),)
    assert snapshot.snapshot_id.startswith("UCOS-EDHS-")
    assert snapshot.to_dict()["checks"][0]["name"] == "c1"


def test_health_snapshot_without_source_status():
    snapshot = HealthSnapshot.from_endpoint(_endpoint(status="degraded", healthy=False))
    assert snapshot.status == "degraded"
    assert snapshot.source_status is None


def test_health_snapshot_rejects_non_mapping_and_malformed():
    with pytest.raises(DashboardViewError):
        HealthSnapshot.from_endpoint("nope")  # type: ignore[arg-type]
    with pytest.raises(DashboardViewError):
        HealthSnapshot.from_endpoint({"healthy": True, "checks": []})  # missing status


# --------------------------------------------------------------------------- #
# DashboardSummary / DashboardView                                             #
# --------------------------------------------------------------------------- #


def _summary(requests):
    metrics = RequestMetrics.from_requests(requests)
    queue = QueueSummary.from_requests(requests)
    health = HealthSnapshot.from_endpoint(_endpoint(), source_status="healthy")
    return DashboardSummary.create(metrics=metrics, queue=queue, health=health)


def test_dashboard_summary_aggregates():
    requests = (_request(status=RequestStatus.QUEUED),)
    summary = _summary(requests)
    assert summary.summary_id.startswith("UCOS-EDSM-")
    assert summary.metrics.total == 1
    assert summary.queue.queue_depth == 1
    assert summary.health.healthy is True
    assert summary.fingerprint() == summary.fingerprint()
    assert summary.to_dict()["metrics"]["total"] == 1


def test_dashboard_summary_rejects_bad_components():
    requests = (_request(),)
    metrics = RequestMetrics.from_requests(requests)
    queue = QueueSummary.from_requests(requests)
    health = HealthSnapshot.from_endpoint(_endpoint())
    with pytest.raises(DashboardViewError):
        DashboardSummary.create(metrics="nope", queue=queue, health=health)  # type: ignore[arg-type]
    with pytest.raises(DashboardViewError):
        DashboardSummary.create(metrics=metrics, queue="nope", health=health)  # type: ignore[arg-type]
    with pytest.raises(DashboardViewError):
        DashboardSummary.create(metrics=metrics, queue=queue, health="nope")  # type: ignore[arg-type]


def test_dashboard_view_composes_full_surface():
    request = _request(status=RequestStatus.QUEUED)
    snapshot = ExecutionSnapshot.from_request(request, _derived(request))
    summary = _summary((request,))
    trend = RequestTrend.from_events(())
    view = DashboardView.create(
        principal_id="UCOS-PRIN-1",
        tenant="acme",
        summary=summary,
        snapshots=(snapshot,),
        trend=trend,
    )
    assert view.view_id.startswith("UCOS-EDVW-")
    assert view.principal_id == "UCOS-PRIN-1"
    assert len(view.snapshots) == 1
    assert view.to_dict()["tenant"] == "acme"
    assert view.fingerprint() == view.fingerprint()


def test_dashboard_view_rejects_bad_inputs():
    request = _request()
    snapshot = ExecutionSnapshot.from_request(request, _derived(request))
    summary = _summary((request,))
    trend = RequestTrend.from_events(())
    with pytest.raises(DashboardViewError):
        DashboardView.create(
            principal_id="", tenant=None, summary=summary, snapshots=(snapshot,), trend=trend
        )
    with pytest.raises(DashboardViewError):
        DashboardView.create(
            principal_id="p",
            tenant=None,
            summary="nope",
            snapshots=(snapshot,),
            trend=trend,  # type: ignore[arg-type]
        )
    with pytest.raises(DashboardViewError):
        DashboardView.create(
            principal_id="p",
            tenant=None,
            summary=summary,
            snapshots=(snapshot,),
            trend="nope",  # type: ignore[arg-type]
        )
    with pytest.raises(DashboardViewError):
        DashboardView.create(
            principal_id="p",
            tenant=None,
            summary=summary,
            snapshots=("nope",),
            trend=trend,  # type: ignore[list-item]
        )
