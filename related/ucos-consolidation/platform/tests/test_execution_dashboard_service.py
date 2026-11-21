"""EC2-TASK-000132 — Execution dashboard service tests (EC2-EPIC-008).

Covers the governed L3 composition point end to end: fail-closed construction and component
validation; the full navigation view; summary / queue / census / trend / health-visibility
read surfaces; per-request visibility (list + single snapshot) with tenant isolation; the
composed access decision (identity READ on ``execution-dashboard``) including denial; search
delegation; deterministic evidence (P5); observability metrics; and governed-action emission
(including health-changed). Crucially, an Operator — who holds ``execution-dashboard`` READ
but **no** ``generation-requests`` grant — can observe the dashboard.
"""

from __future__ import annotations

from platform.blueprints.contracts import BlueprintFamily
from platform.execution_dashboard.errors import DashboardAccessError, DashboardServiceError
from platform.execution_dashboard.health import (
    DashboardHealth,
    execution_dashboard_health_checks,
)
from platform.execution_dashboard.search import DashboardSearch
from platform.execution_dashboard.service import (
    DASHBOARD_ACCESS_EVENT,
    DASHBOARD_HEALTH_CHANGED_EVENT,
    DASHBOARD_SEARCH_EVENT,
    DASHBOARD_VIEWED_EVENT,
    METRIC_CENSUS_VIEWS,
    METRIC_HEALTH_INSPECTIONS,
    METRIC_QUEUE_INSPECTIONS,
    METRIC_SEARCHES,
    METRIC_SUMMARIES,
    METRIC_TREND_VIEWS,
    METRIC_VIEWS,
    DashboardAction,
    ExecutionDashboardService,
    build_execution_dashboard_service,
)
from platform.foundation.bootstrap import bootstrap_platform
from platform.foundation.identity import Principal, Role
from platform.generation.registry import GenerationRequestRegistry
from platform.generation.service import build_generation_request_service
from platform.identity.service import build_authorization_service
from platform.observability.health import HealthRegistry
from platform.observability.service import build_observability_service
from platform.workspace.registration import WorkspaceRegistry

import pytest

# --------------------------------------------------------------------------- #
# Helpers                                                                      #
# --------------------------------------------------------------------------- #


def _stack(*, events=None, observability=None, authorization=None):
    auth = authorization or build_authorization_service(events=events)
    workspaces = WorkspaceRegistry()
    generation = build_generation_request_service(
        authorization=auth, workspaces=workspaces, observability=observability, events=events
    )
    dashboard = build_execution_dashboard_service(
        generation=generation, authorization=auth, observability=observability, events=events
    )
    return auth, workspaces, generation, dashboard


def _seed(auth, workspaces, generation, *, tenant=None, slug="req-1", drive="queued"):
    ws = workspaces.create(f"ws-{slug}", "WS", "arch@x", tenant=tenant)
    sess = auth.establish_session(
        Principal.create("arch@x", [Role.ARCHITECT], tenant=tenant), issued_at=0, ttl=1000
    )
    req = generation.submit_request(
        sess.session_id, slug, "UCOS-BLPR-1", ws.workspace_id, BlueprintFamily.DATA, now=1
    )
    if drive in ("validating", "approved", "queued", "completed"):
        generation.start_validation(sess.session_id, req.request_id, now=2)
    if drive in ("approved", "queued", "completed"):
        generation.approve(sess.session_id, req.request_id, now=3)
    if drive in ("queued", "completed"):
        generation.enqueue(sess.session_id, req.request_id, now=4)
    if drive == "completed":
        generation.dispatch_request(sess.session_id, req.request_id, now=5, content_hash="c0ffee")
        generation.mark_running(sess.session_id, req.request_id, now=6)
        generation.complete(sess.session_id, req.request_id, now=7)
    return sess, req


def _viewer(auth, *, role=Role.OPERATOR, subject="op@x", tenant=None):
    return auth.establish_session(
        Principal.create(subject, [role], tenant=tenant), issued_at=0, ttl=1000
    )


def _valid_kwargs(auth, generation):
    hr = HealthRegistry()
    for check in execution_dashboard_health_checks():
        hr.register(check)
    return {
        "generation": generation,
        "authorization": auth,
        "search": DashboardSearch(generation.registry, auth),
        "health": DashboardHealth(generation.registry),
        "health_registry": hr,
    }


# --------------------------------------------------------------------------- #
# Construction                                                                 #
# --------------------------------------------------------------------------- #


def test_build_requires_generation_and_authorization():
    auth = build_authorization_service()
    generation = build_generation_request_service(
        authorization=auth, workspaces=WorkspaceRegistry()
    )
    with pytest.raises(DashboardServiceError):
        build_execution_dashboard_service(generation="nope", authorization=auth)  # type: ignore[arg-type]
    with pytest.raises(DashboardServiceError):
        build_execution_dashboard_service(generation=generation, authorization="nope")  # type: ignore[arg-type]


@pytest.mark.parametrize(
    "field", ["generation", "authorization", "search", "health", "health_registry"]
)
def test_service_rejects_each_invalid_required_component(field):
    auth = build_authorization_service()
    generation = build_generation_request_service(
        authorization=auth, workspaces=WorkspaceRegistry()
    )
    kwargs = _valid_kwargs(auth, generation)
    kwargs[field] = "nope"
    with pytest.raises(DashboardServiceError):
        ExecutionDashboardService(**kwargs)  # type: ignore[arg-type]


@pytest.mark.parametrize("field", ["observability", "events"])
def test_service_rejects_each_invalid_optional_component(field):
    auth = build_authorization_service()
    generation = build_generation_request_service(
        authorization=auth, workspaces=WorkspaceRegistry()
    )
    kwargs = _valid_kwargs(auth, generation)
    kwargs[field] = "nope"
    with pytest.raises(DashboardServiceError):
        ExecutionDashboardService(**kwargs)  # type: ignore[arg-type]


def test_component_property_getters():
    auth, _, generation, dashboard = _stack()
    assert dashboard.generation is generation
    assert dashboard.registry is generation.registry
    assert dashboard.authorization is auth
    assert dashboard.health is not None
    assert dashboard.observability is None
    assert dashboard.access_evaluation_count == 0
    assert dashboard.view_count == 0
    assert dashboard.search_count == 0
    assert "generation.request.submitted" in dashboard.observed_generation_events
    assert "generation.requests.queue_depth" in dashboard.observed_generation_metrics


# --------------------------------------------------------------------------- #
# View / summary / queue / census / trend / health                            #
# --------------------------------------------------------------------------- #


def test_operator_can_view_dashboard_without_generation_grant():
    events = bootstrap_platform().events
    auth, workspaces, generation, dashboard = _stack(events=events)
    _seed(auth, workspaces, generation, tenant="acme")
    operator = _viewer(auth, tenant="acme")  # Operator: no generation-requests grant
    view = dashboard.view(operator.session_id, now=8, tenant="acme")
    assert view.summary.metrics.total == 1
    assert view.summary.queue.queue_depth == 1
    assert len(view.snapshots) == 1
    assert view.trend.total_transitions == 3
    assert dashboard.view_count == 1
    assert len(events.events_of(DASHBOARD_VIEWED_EVENT)) == 1


def test_summary_queue_census_trend_health_surfaces():
    auth, workspaces, generation, dashboard = _stack()
    _seed(auth, workspaces, generation, tenant="acme", drive="completed")
    viewer = _viewer(auth, tenant="acme")
    summary = dashboard.summary(viewer.session_id, now=8, tenant="acme")
    assert summary.metrics.completed == 1
    queue = dashboard.queue(viewer.session_id, now=8, tenant="acme")
    assert queue.terminal == 1
    census = dashboard.census(viewer.session_id, now=8, tenant="acme")
    assert census.total == 1
    trend = dashboard.trends(viewer.session_id, now=8, tenant="acme")
    assert trend.terminal_transitions == 1
    health = dashboard.health_view(viewer.session_id, now=8)
    assert health.healthy is True
    assert health.source_status in {"healthy", "degraded", "unhealthy"}


def test_view_denied_scoped_cross_tenant():
    auth, workspaces, generation, dashboard = _stack()
    _seed(auth, workspaces, generation, tenant="acme")
    partner = _viewer(auth, role=Role.PARTNER, subject="p@x", tenant="acme")
    with pytest.raises(DashboardAccessError):
        dashboard.view(partner.session_id, now=8, tenant="beta")


def test_summary_denied_scoped_cross_tenant():
    auth, workspaces, generation, dashboard = _stack()
    partner = _viewer(auth, role=Role.PARTNER, subject="p@x", tenant="acme")
    with pytest.raises(DashboardAccessError):
        dashboard.summary(partner.session_id, now=8, tenant="beta")


# --------------------------------------------------------------------------- #
# Request visibility                                                           #
# --------------------------------------------------------------------------- #


def test_list_snapshots_and_isolation():
    auth, workspaces, generation, dashboard = _stack()
    _seed(auth, workspaces, generation, tenant="acme", slug="a")
    _seed(auth, workspaces, generation, tenant="beta", slug="b")
    viewer = _viewer(auth, tenant="acme")
    snaps = dashboard.list_snapshots(viewer.session_id, now=8)
    assert all(s.tenant != "beta" for s in snaps)
    assert any(s.tenant == "acme" for s in snaps)


def test_list_snapshots_empty_for_invalid_and_unauthorized():
    auth, workspaces, generation, dashboard = _stack()
    _seed(auth, workspaces, generation, tenant="acme")
    assert dashboard.list_snapshots("UCOS-SESS-missing", now=8) == ()
    partner = _viewer(auth, role=Role.PARTNER, subject="p@x", tenant="acme")
    assert dashboard.list_snapshots(partner.session_id, now=8, tenant="beta") == ()


def test_snapshot_of_success_and_cross_tenant_denied():
    auth, workspaces, generation, dashboard = _stack()
    _, req_acme = _seed(auth, workspaces, generation, tenant="acme", slug="a")
    _, req_beta = _seed(auth, workspaces, generation, tenant="beta", slug="b")
    viewer = _viewer(auth, tenant="acme")
    snapshot = dashboard.snapshot_of(viewer.session_id, req_acme.request_id, now=8)
    assert snapshot.request_id == req_acme.request_id
    with pytest.raises(DashboardAccessError):
        dashboard.snapshot_of(viewer.session_id, req_beta.request_id, now=8)


def test_snapshot_of_unknown_request_fail_closed():
    auth, _, _, dashboard = _stack()
    viewer = _viewer(auth)
    with pytest.raises(Exception):  # noqa: B017 - registry error for unknown request
        dashboard.snapshot_of(viewer.session_id, "UCOS-GREQ-missing", now=8)


# --------------------------------------------------------------------------- #
# Access evaluation                                                            #
# --------------------------------------------------------------------------- #


def test_evaluate_access_granted_and_emitted():
    events = bootstrap_platform().events
    auth, workspaces, generation, dashboard = _stack(events=events)
    viewer = _viewer(auth, tenant="acme")
    access = dashboard.evaluate_access(
        viewer.session_id, DashboardAction.VIEW, now=8, tenant="acme"
    )
    assert access.granted is True
    assert access.access_id.startswith("UCOS-EDAC-")
    assert access.to_dict()["granted"] is True
    assert len(events.events_of(DASHBOARD_ACCESS_EVENT)) == 1


def test_evaluate_access_denied_scoped_cross_tenant():
    auth, _, _, dashboard = _stack()
    partner = _viewer(auth, role=Role.PARTNER, subject="p@x", tenant="acme")
    access = dashboard.evaluate_access(
        partner.session_id, DashboardAction.VIEW, now=8, tenant="beta"
    )
    assert access.granted is False
    assert access.reason == "tenant-scope-violation"


def test_evaluate_access_rejects_bad_action():
    auth, _, _, dashboard = _stack()
    viewer = _viewer(auth)
    with pytest.raises(DashboardServiceError):
        dashboard.evaluate_access(viewer.session_id, "view", now=8)  # type: ignore[arg-type]


# --------------------------------------------------------------------------- #
# Search                                                                       #
# --------------------------------------------------------------------------- #


def test_search_delegates_and_emits():
    events = bootstrap_platform().events
    auth, workspaces, generation, dashboard = _stack(events=events)
    _seed(auth, workspaces, generation, tenant="acme", slug="req-1")
    viewer = _viewer(auth, tenant="acme")
    resp = dashboard.search(viewer.session_id, "req-1", now=8, tenant="acme")
    assert resp.authorized is True
    assert dashboard.search_count == 1
    assert len(events.events_of(DASHBOARD_SEARCH_EVENT)) == 1


# --------------------------------------------------------------------------- #
# Health-changed / evidence / observability / to_dict                          #
# --------------------------------------------------------------------------- #


def test_health_changed_event_emitted_on_status_change(monkeypatch):
    events = bootstrap_platform().events
    auth, workspaces, generation, dashboard = _stack(events=events)
    _seed(auth, workspaces, generation, tenant="acme")
    viewer = _viewer(auth, tenant="acme")
    # Induce a projection drift so the dashboard health flips to UNHEALTHY.
    monkeypatch.setattr(
        GenerationRequestRegistry,
        "count_by_status",
        lambda self: {"submitted": 999},
        raising=True,
    )
    dashboard.health_view(viewer.session_id, now=9)
    assert len(events.events_of(DASHBOARD_HEALTH_CHANGED_EVENT)) == 1


def test_evidence_and_health_report_deterministic():
    def run() -> str:
        auth, workspaces, generation, dashboard = _stack()
        _seed(auth, workspaces, generation, tenant="acme", drive="completed")
        return dashboard.evidence().fingerprint()

    assert run() == run()
    auth, workspaces, generation, dashboard = _stack()
    _seed(auth, workspaces, generation, tenant="acme", drive="completed")
    evidence = dashboard.evidence()
    assert evidence.request_count == 1
    assert evidence.terminal_count == 1
    assert evidence.evidence_id.startswith("UCOS-EDEV-")
    assert dashboard.health_report()["healthy"] is True
    assert evidence.to_dict()["status_census"]["completed"] == 1


def test_to_dict_and_metrics_with_observability():
    events = bootstrap_platform().events
    observability = build_observability_service(events=events)
    auth, workspaces, generation, dashboard = _stack(events=events, observability=observability)
    _seed(auth, workspaces, generation, tenant="acme", drive="completed")
    viewer = _viewer(auth, tenant="acme")
    dashboard.view(viewer.session_id, now=8, tenant="acme")
    dashboard.summary(viewer.session_id, now=8, tenant="acme")
    dashboard.queue(viewer.session_id, now=8, tenant="acme")
    dashboard.census(viewer.session_id, now=8, tenant="acme")
    dashboard.trends(viewer.session_id, now=8, tenant="acme")
    dashboard.health_view(viewer.session_id, now=8)
    dashboard.search(viewer.session_id, "req-1", now=8, tenant="acme")
    summary = dashboard.to_dict()
    assert summary["request_count"] == 1
    assert summary["observability_bound"] is True
    assert dashboard.observability is observability
    metrics = observability.metrics
    assert metrics.value_of(METRIC_VIEWS) == 1.0
    assert metrics.value_of(METRIC_SUMMARIES) == 1.0
    assert metrics.value_of(METRIC_QUEUE_INSPECTIONS) == 1.0
    assert metrics.value_of(METRIC_CENSUS_VIEWS) == 1.0
    assert metrics.value_of(METRIC_TREND_VIEWS) == 1.0
    assert metrics.value_of(METRIC_HEALTH_INSPECTIONS) == 1.0
    assert metrics.value_of(METRIC_SEARCHES) == 1.0
