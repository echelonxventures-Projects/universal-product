"""EC2-TASK-000096 — Project bootstrap tests.

Covers the registry-driven composition of the Project Management Runtime onto a
PlatformContext: it publishes the six project contracts into the Foundation service
registry (PL-05), registers the project health checks into the Observability layer
(cross-runtime health, G1/OP-C1), emits a deterministic bootstrap event, is idempotent
on contracts and health checks, and composes identity + observability + workspace when
they are not supplied.
"""

from __future__ import annotations

from platform.foundation.bootstrap import bootstrap_platform
from platform.identity.service import build_authorization_service
from platform.observability.service import build_observability_service
from platform.projects.bootstrap import PROJECT_BOOTSTRAP_EVENT, bootstrap_projects
from platform.projects.contracts import PROJECT_CONTRACTS
from platform.projects.health import INTEGRITY_CHECK, REGISTRY_CHECK
from platform.projects.service import ProjectService
from platform.workspace.bootstrap import bootstrap_workspace


def test_bootstrap_publishes_contracts_and_emits_event():
    context = bootstrap_platform()
    service = bootstrap_projects(context)
    assert isinstance(service, ProjectService)
    for ref in PROJECT_CONTRACTS:
        assert ref.name in context.services
    assert "projects.associations.bind" in context.services
    assert "projects.search.query" in context.services
    assert "projects.runtime.service" in context.services
    assert len(context.events.events_of(PROJECT_BOOTSTRAP_EVENT)) == 1


def test_bootstrap_registers_health_checks_into_observability():
    context = bootstrap_platform()
    observability = build_observability_service(events=context.events)
    bootstrap_projects(context, observability=observability)
    assert REGISTRY_CHECK in observability.health
    assert INTEGRITY_CHECK in observability.health


def test_bootstrap_is_idempotent_on_contracts_and_health_checks():
    context = bootstrap_platform()
    authorization = build_authorization_service(events=context.events)
    observability = build_observability_service(events=context.events)
    bootstrap_projects(context, authorization=authorization, observability=observability)
    services_before = len(context.services)
    health_before = len(observability.health)
    bootstrap_projects(context, authorization=authorization, observability=observability)
    assert len(context.services) == services_before
    assert len(observability.health) == health_before


def test_bootstrap_composes_identity_observability_and_workspace_by_default():
    context = bootstrap_platform()
    service = bootstrap_projects(context)
    assert service.authorization is not None
    assert service.workspaces is not None
    assert service.registry is not None


def test_bootstrap_reuses_supplied_workspace_runtime():
    context = bootstrap_platform()
    authorization = build_authorization_service(events=context.events)
    observability = build_observability_service(events=context.events)
    workspace_service = bootstrap_workspace(
        context, authorization=authorization, observability=observability
    )
    service = bootstrap_projects(
        context,
        authorization=authorization,
        observability=observability,
        workspace=workspace_service,
    )
    # The project runtime binds the SAME workspace registry (parent-scope by reference).
    assert service.workspaces is workspace_service.registry
