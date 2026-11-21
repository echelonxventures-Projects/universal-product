"""EC2-TASK-000133 — Execution dashboard bootstrap tests (EC2-EPIC-008).

Covers composition onto a PlatformContext: reuse of identity/observability/generation,
contract publication into the Foundation service registry, cross-runtime health-check
registration (idempotent), the composition event, and end-to-end operability.
"""

from __future__ import annotations

from platform.blueprints.contracts import BlueprintFamily
from platform.execution_dashboard.bootstrap import (
    EXECUTION_DASHBOARD_BOOTSTRAP_EVENT,
    bootstrap_execution_dashboard,
)
from platform.execution_dashboard.contracts import EXECUTION_DASHBOARD_CONTRACTS
from platform.execution_dashboard.health import execution_dashboard_health_checks
from platform.execution_dashboard.service import ExecutionDashboardService
from platform.foundation.bootstrap import bootstrap_platform
from platform.foundation.identity import Principal, Role
from platform.generation.bootstrap import bootstrap_generation_requests
from platform.identity.service import bootstrap_identity
from platform.observability.service import bootstrap_observability


def _ctx():
    return bootstrap_platform()


def test_bootstrap_returns_service_and_publishes_contracts():
    ctx = _ctx()
    service = bootstrap_execution_dashboard(ctx)
    assert isinstance(service, ExecutionDashboardService)
    for ref in EXECUTION_DASHBOARD_CONTRACTS:
        assert ref.name in ctx.services


def test_bootstrap_registers_health_checks_and_emits_event():
    ctx = _ctx()
    obs = bootstrap_observability(ctx)
    bootstrap_execution_dashboard(ctx, observability=obs)
    for check in execution_dashboard_health_checks():
        assert check.name in obs.health
    assert len(ctx.events.events_of(EXECUTION_DASHBOARD_BOOTSTRAP_EVENT)) == 1


def test_bootstrap_is_idempotent_on_contracts_and_health():
    ctx = _ctx()
    auth = bootstrap_identity(ctx)
    obs = bootstrap_observability(ctx)
    gen = bootstrap_generation_requests(ctx, authorization=auth, observability=obs)
    bootstrap_execution_dashboard(ctx, authorization=auth, observability=obs, generation=gen)
    # Second bootstrap must not raise on duplicate contracts/health checks.
    bootstrap_execution_dashboard(ctx, authorization=auth, observability=obs, generation=gen)
    for ref in EXECUTION_DASHBOARD_CONTRACTS:
        assert ref.name in ctx.services


def test_bootstrapped_dashboard_is_operational_end_to_end():
    ctx = _ctx()
    auth = bootstrap_identity(ctx)
    gen = bootstrap_generation_requests(ctx, authorization=auth)
    dashboard = bootstrap_execution_dashboard(ctx, authorization=auth, generation=gen)
    arch = Principal.create("arch@x", [Role.ARCHITECT])
    sess = auth.establish_session(arch, issued_at=0, ttl=1000)
    ws = gen.workspaces.create("team", "Team", "arch@x")
    req = gen.submit_request(
        sess.session_id, "req", "UCOS-BLPR-1", ws.workspace_id, BlueprintFamily.DATA, now=1
    )
    gen.start_validation(sess.session_id, req.request_id, now=2)
    gen.approve(sess.session_id, req.request_id, now=3)
    gen.enqueue(sess.session_id, req.request_id, now=4)
    view = dashboard.view(sess.session_id, now=5)
    assert view.summary.queue.queue_depth == 1
    assert view.summary.metrics.total == 1
