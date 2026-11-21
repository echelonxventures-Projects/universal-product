"""EC2-TASK-000134 — Artifact Explorer bootstrap tests (EC2-EPIC-009).

Covers composition onto a PlatformContext: identity/observability/generation reuse,
contract publication (idempotent), cross-runtime health-check registration (idempotent),
and the deterministic bootstrap event — plus end-to-end consumption of the generation
runtime's registry/dispatch/provenance by reference.
"""

from __future__ import annotations

from platform.artifact_explorer.bootstrap import (
    ARTIFACT_EXPLORER_BOOTSTRAP_EVENT,
    bootstrap_artifact_explorer,
)
from platform.artifact_explorer.contracts import ARTIFACT_EXPLORER_CONTRACTS
from platform.artifact_explorer.health import REGISTRY_CHECK
from platform.artifact_explorer.service import ArtifactExplorerService
from platform.blueprints.contracts import BlueprintFamily
from platform.foundation.bootstrap import bootstrap_platform
from platform.foundation.identity import Principal, Role
from platform.generation.bootstrap import bootstrap_generation_requests
from platform.identity.service import bootstrap_identity
from platform.observability.service import bootstrap_observability


def test_bootstrap_with_all_defaults():
    ctx = bootstrap_platform()
    service = bootstrap_artifact_explorer(ctx)
    assert isinstance(service, ArtifactExplorerService)
    assert len(ctx.events.events_of(ARTIFACT_EXPLORER_BOOTSTRAP_EVENT)) == 1


def test_bootstrap_composes_and_publishes_contracts():
    ctx = bootstrap_platform()
    obs = bootstrap_observability(ctx)
    service = bootstrap_artifact_explorer(ctx, observability=obs)
    assert isinstance(service, ArtifactExplorerService)
    for ref in ARTIFACT_EXPLORER_CONTRACTS:
        assert ref.name in ctx.services
    assert REGISTRY_CHECK in obs.health
    assert len(ctx.events.events_of(ARTIFACT_EXPLORER_BOOTSTRAP_EVENT)) == 1


def test_bootstrap_reuses_supplied_generation_runtime():
    ctx = bootstrap_platform()
    auth = bootstrap_identity(ctx)
    obs = bootstrap_observability(ctx)
    generation = bootstrap_generation_requests(ctx, authorization=auth, observability=obs)
    service = bootstrap_artifact_explorer(
        ctx, authorization=auth, observability=obs, generation=generation
    )
    # The explorer consumes the generation runtime's ledgers by reference (identity).
    assert service.registry is generation.registry
    assert service.dispatch is generation.dispatch
    assert service.provenance is generation.provenance


def test_bootstrap_is_idempotent_on_contracts_and_health():
    ctx = bootstrap_platform()
    auth = bootstrap_identity(ctx)
    obs = bootstrap_observability(ctx)
    first = bootstrap_artifact_explorer(ctx, authorization=auth, observability=obs)
    second = bootstrap_artifact_explorer(ctx, authorization=auth, observability=obs)
    assert isinstance(first, ArtifactExplorerService)
    assert isinstance(second, ArtifactExplorerService)
    # Contracts and health checks are not duplicated on re-bootstrap.
    for ref in ARTIFACT_EXPLORER_CONTRACTS:
        assert ref.name in ctx.services


def test_bootstrap_explorer_consumes_generation_artifacts_end_to_end():
    ctx = bootstrap_platform()
    auth = bootstrap_identity(ctx)
    obs = bootstrap_observability(ctx)
    generation = bootstrap_generation_requests(ctx, authorization=auth, observability=obs)
    explorer = bootstrap_artifact_explorer(
        ctx, authorization=auth, observability=obs, generation=generation
    )
    arch = Principal.create("arch@x", [Role.ARCHITECT])
    sess = auth.establish_session(arch, issued_at=0, ttl=1000)
    ws = generation.workspaces.create("team", "Team", "arch@x")
    req = generation.submit_request(
        sess.session_id, "req-1", "UCOS-BLPR-1", ws.workspace_id, BlueprintFamily.DATA, now=1
    )
    generation.start_validation(sess.session_id, req.request_id, now=2)
    generation.approve(sess.session_id, req.request_id, now=3)
    generation.enqueue(sess.session_id, req.request_id, now=4)
    generation.dispatch_request(sess.session_id, req.request_id, now=5, content_hash="c0ffee")
    # The explorer immediately sees the artifact produced by EPIC-007 (by reference).
    view = explorer.get_artifact(sess.session_id, req.request_id, now=6)
    assert view.has_dispatch is True
    assert view.request_ref == req.request_id
