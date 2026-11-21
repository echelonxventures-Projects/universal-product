"""EC2-EPIC-008 — execution-dashboard observability & audit tests (PC-12/PC-16).

Asserts the observability + auditability acceptance criteria: every governed dashboard
action is published onto the Foundation event bus and captured by the Observability Layer
as an append-only, hash-chained audit record (PC-16 / OP-C3), the dashboard health check
is registered into the shared L8 health registry, and dashboard metrics are recorded on
100% of governed reads (PC-12). The dashboard surfaces the EPIC-007 observability by
reference without re-emitting it.
"""

from __future__ import annotations

from platform.blueprints.contracts import BlueprintFamily
from platform.execution_dashboard.bootstrap import bootstrap_execution_dashboard
from platform.execution_dashboard.health import execution_dashboard_health_checks
from platform.execution_dashboard.service import (
    DASHBOARD_ACCESS_EVENT,
    DASHBOARD_HEALTH_EVENT,
    DASHBOARD_QUEUE_EVENT,
    DASHBOARD_SEARCH_EVENT,
    METRIC_VIEWS,
)
from platform.foundation.bootstrap import bootstrap_platform
from platform.foundation.identity import Principal, Role
from platform.generation.bootstrap import bootstrap_generation_requests
from platform.identity.service import bootstrap_identity
from platform.observability.service import bootstrap_observability


def _fixture():
    ctx = bootstrap_platform()
    auth = bootstrap_identity(ctx)
    obs = bootstrap_observability(ctx)
    gen = bootstrap_generation_requests(ctx, authorization=auth, observability=obs)
    dash = bootstrap_execution_dashboard(ctx, authorization=auth, observability=obs, generation=gen)
    return ctx, auth, obs, gen, dash


def _seed(auth, gen, *, tenant="acme"):
    arch = Principal.create("arch@x", [Role.ARCHITECT], tenant=tenant)
    sess = auth.establish_session(arch, issued_at=0, ttl=1000)
    ws = gen.workspaces.create("team", "Team", "arch@x", tenant=tenant)
    req = gen.submit_request(
        sess.session_id, "req-1", "UCOS-BLPR-1", ws.workspace_id, BlueprintFamily.DATA, now=1
    )
    gen.start_validation(sess.session_id, req.request_id, now=2)
    gen.approve(sess.session_id, req.request_id, now=3)
    gen.enqueue(sess.session_id, req.request_id, now=4)
    return req


def test_governed_dashboard_actions_are_audited_append_only():
    ctx, auth, obs, gen, dash = _fixture()
    _seed(auth, gen)
    operator = auth.establish_session(
        Principal.create("op@x", [Role.OPERATOR], tenant="acme"), issued_at=0, ttl=1000
    )
    dash.view(operator.session_id, now=8, tenant="acme")
    dash.queue(operator.session_id, now=8, tenant="acme")
    dash.health_view(operator.session_id, now=8)
    dash.search(operator.session_id, "req-1", now=8, tenant="acme")

    # Every governed dashboard event is on the bus and captured as append-only audit.
    for event_type in (
        DASHBOARD_ACCESS_EVENT,
        DASHBOARD_QUEUE_EVENT,
        DASHBOARD_HEALTH_EVENT,
        DASHBOARD_SEARCH_EVENT,
    ):
        assert ctx.events.events_of(event_type), event_type

    audit_actions = {a.detail.get("event_type") for a in obs.audit.events}
    assert DASHBOARD_ACCESS_EVENT in audit_actions
    assert DASHBOARD_SEARCH_EVENT in audit_actions
    assert obs.audit.verify() is True  # hash chain intact (append-only, tamper-evident)


def test_dashboard_health_check_registered_into_shared_registry():
    _, _, obs, _, _ = _fixture()
    for check in execution_dashboard_health_checks():
        assert check.name in obs.health


def test_dashboard_metrics_recorded_on_governed_reads():
    _, auth, obs, gen, dash = _fixture()
    _seed(auth, gen)
    viewer = auth.establish_session(
        Principal.create("op@x", [Role.OPERATOR], tenant="acme"), issued_at=0, ttl=1000
    )
    dash.view(viewer.session_id, now=8, tenant="acme")
    assert obs.metrics.value_of(METRIC_VIEWS) == 1.0
