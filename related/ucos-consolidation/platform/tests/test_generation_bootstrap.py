"""EC2-TASK-000118 — Generation request bootstrap tests (EC2-EPIC-007).

Covers composition onto a PlatformContext: reuse of identity/observability/workspace,
contract publication into the Foundation service registry, cross-runtime health-check
registration (idempotent), the composition event, and end-to-end operability.
"""

from __future__ import annotations

from platform.blueprints.contracts import BlueprintFamily
from platform.foundation.bootstrap import bootstrap_platform
from platform.generation.bootstrap import (
    GENERATION_REQUEST_BOOTSTRAP_EVENT,
    bootstrap_generation_requests,
)
from platform.generation.contracts import GENERATION_REQUEST_CONTRACTS, RequestStatus
from platform.generation.health import generation_request_health_checks
from platform.generation.service import GenerationRequestService
from platform.identity.service import bootstrap_identity
from platform.observability.service import bootstrap_observability
from platform.workspace.bootstrap import bootstrap_workspace


def _ctx():
    return bootstrap_platform()


def test_bootstrap_returns_service_and_publishes_contracts():
    ctx = _ctx()
    service = bootstrap_generation_requests(ctx)
    assert isinstance(service, GenerationRequestService)
    for ref in GENERATION_REQUEST_CONTRACTS:
        assert ref.name in ctx.services


def test_bootstrap_registers_health_checks_and_emits_event():
    ctx = _ctx()
    obs = bootstrap_observability(ctx)
    bootstrap_generation_requests(ctx, observability=obs)
    for check in generation_request_health_checks():
        assert check.name in obs.health
    assert len(ctx.events.events_of(GENERATION_REQUEST_BOOTSTRAP_EVENT)) == 1


def test_bootstrap_is_idempotent_on_contracts_and_health():
    ctx = _ctx()
    auth = bootstrap_identity(ctx)
    obs = bootstrap_observability(ctx)
    ws = bootstrap_workspace(ctx, authorization=auth, observability=obs)
    bootstrap_generation_requests(ctx, authorization=auth, observability=obs, workspace=ws)
    # Second bootstrap must not raise on duplicate contracts/health checks.
    bootstrap_generation_requests(ctx, authorization=auth, observability=obs, workspace=ws)
    for ref in GENERATION_REQUEST_CONTRACTS:
        assert ref.name in ctx.services


def test_bootstrapped_service_is_operational_end_to_end():
    ctx = _ctx()
    auth = bootstrap_identity(ctx)
    service = bootstrap_generation_requests(ctx, authorization=auth)
    from platform.foundation.identity import Principal, Role

    arch = Principal.create("arch@x", [Role.ARCHITECT])
    sess = auth.establish_session(arch, issued_at=0, ttl=1000)
    ws = service.workspaces.create("team", "Team", "arch@x")
    req = service.submit_request(
        sess.session_id, "req", "UCOS-BLPR-1", ws.workspace_id, BlueprintFamily.DATA, now=1
    )
    service.start_validation(sess.session_id, req.request_id, now=2)
    service.approve(sess.session_id, req.request_id, now=3)
    service.enqueue(sess.session_id, req.request_id, now=4)
    service.dispatch_request(sess.session_id, req.request_id, now=5, content_hash="c0ffee")
    assert service.get_request(req.request_id).status is RequestStatus.DISPATCHED
