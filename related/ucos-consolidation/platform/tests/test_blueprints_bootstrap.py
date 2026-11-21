"""EC2-TASK-000107 — Blueprint bootstrap tests (EC2-EPIC-006).

Covers composition onto a PlatformContext: reuse of identity/observability/workspace,
contract publication into the Foundation service registry, cross-runtime health-check
registration (idempotent), the composition event, and end-to-end operability.
"""

from __future__ import annotations

from platform.blueprints.bootstrap import BLUEPRINT_BOOTSTRAP_EVENT, bootstrap_blueprints
from platform.blueprints.contracts import BLUEPRINT_CONTRACTS, BlueprintFamily
from platform.blueprints.health import blueprint_health_checks
from platform.blueprints.service import BlueprintService
from platform.foundation.bootstrap import bootstrap_platform
from platform.foundation.identity import Principal, Role
from platform.identity.service import bootstrap_identity
from platform.observability.service import bootstrap_observability
from platform.workspace.bootstrap import bootstrap_workspace


def _ctx():
    return bootstrap_platform()


def test_bootstrap_returns_service_and_publishes_contracts():
    ctx = _ctx()
    service = bootstrap_blueprints(ctx)
    assert isinstance(service, BlueprintService)
    for ref in BLUEPRINT_CONTRACTS:
        assert ref.name in ctx.services


def test_bootstrap_registers_health_checks_and_emits_event():
    ctx = _ctx()
    obs = bootstrap_observability(ctx)
    bootstrap_blueprints(ctx, observability=obs)
    for check in blueprint_health_checks():
        assert check.name in obs.health
    assert len(ctx.events.events_of(BLUEPRINT_BOOTSTRAP_EVENT)) == 1


def test_bootstrap_is_idempotent_on_contracts_and_health():
    ctx = _ctx()
    auth = bootstrap_identity(ctx)
    obs = bootstrap_observability(ctx)
    ws = bootstrap_workspace(ctx, authorization=auth, observability=obs)
    bootstrap_blueprints(ctx, authorization=auth, observability=obs, workspace=ws)
    # Second bootstrap must not raise on duplicate contracts/health checks.
    bootstrap_blueprints(ctx, authorization=auth, observability=obs, workspace=ws)
    for ref in BLUEPRINT_CONTRACTS:
        assert ref.name in ctx.services


def test_bootstrapped_service_is_operational_end_to_end():
    ctx = _ctx()
    auth = bootstrap_identity(ctx)
    service = bootstrap_blueprints(ctx, authorization=auth)
    arch = Principal.create("arch@x", [Role.ARCHITECT])
    sess = auth.establish_session(arch, issued_at=0, ttl=1000)
    ws = service.workspaces.create("team", "Team", "arch@x")
    bp = service.author_blueprint(
        sess.session_id, "bp", "BP", ws.workspace_id, BlueprintFamily.DATA, now=1
    )
    service.classify(sess.session_id, bp.blueprint_id, BlueprintFamily.DATA, now=2)
    service.validate(sess.session_id, bp.blueprint_id, now=3)
    assert service.registry.get(bp.blueprint_id).status.value == "validated"
