"""EC2-TASK-000088 — Workspace bootstrap tests.

Covers the registry-driven composition of the Workspace Runtime onto a PlatformContext:
it publishes the six workspace contracts into the Foundation service registry (PL-05),
registers the workspace health checks into the Observability layer (cross-runtime
health, G1/OP-C1), emits a deterministic bootstrap event, is idempotent on contracts
and health checks, and composes identity + observability when they are not supplied.
"""

from __future__ import annotations

from platform.foundation.bootstrap import bootstrap_platform
from platform.identity.service import build_authorization_service
from platform.observability.service import build_observability_service
from platform.workspace.bootstrap import WORKSPACE_BOOTSTRAP_EVENT, bootstrap_workspace
from platform.workspace.contracts import WORKSPACE_CONTRACTS
from platform.workspace.health import INTEGRITY_CHECK, REGISTRY_CHECK
from platform.workspace.service import WorkspaceService


def test_bootstrap_publishes_contracts_and_emits_event():
    context = bootstrap_platform()
    service = bootstrap_workspace(context)
    assert isinstance(service, WorkspaceService)
    for ref in WORKSPACE_CONTRACTS:
        assert ref.name in context.services
    assert "workspace.isolation.evaluate" in context.services
    assert "workspace.search.query" in context.services
    assert len(context.events.events_of(WORKSPACE_BOOTSTRAP_EVENT)) == 1


def test_bootstrap_registers_health_checks_into_observability():
    context = bootstrap_platform()
    observability = build_observability_service(events=context.events)
    bootstrap_workspace(context, observability=observability)
    assert REGISTRY_CHECK in observability.health
    assert INTEGRITY_CHECK in observability.health


def test_bootstrap_is_idempotent_on_contracts_and_health_checks():
    context = bootstrap_platform()
    authorization = build_authorization_service(events=context.events)
    observability = build_observability_service(events=context.events)
    bootstrap_workspace(context, authorization=authorization, observability=observability)
    services_before = len(context.services)
    health_before = len(observability.health)
    # Re-composing must not duplicate contracts or health checks.
    bootstrap_workspace(context, authorization=authorization, observability=observability)
    assert len(context.services) == services_before
    assert len(observability.health) == health_before


def test_bootstrap_composes_identity_and_observability_by_default():
    context = bootstrap_platform()
    # No authorization/observability supplied — the bootstrap composes them.
    service = bootstrap_workspace(context)
    assert service.authorization is not None
    assert service.registry is not None
