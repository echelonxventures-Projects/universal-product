"""EC2-TASK-000107 — Blueprint Bootstrap (EC2-EPIC-006).

Composes the Blueprint Catalog & Management Runtime onto a
:class:`~platform.foundation.bootstrap.PlatformContext`, registry-driven and
deterministic. It composes the platform end to end: the Identity Layer (L7),
Observability Layer (L8), Workspace Runtime (L3), and Project Management Runtime (L3)
are bootstrapped onto the context if not supplied, then the Blueprint Runtime (L3/L6)
is built over them. The bootstrap:

    1. reuses/creates the Identity ``AuthorizationService``, Observability service,
       Workspace Runtime (blueprints are scoped to workspaces — parent binding), and
       Project Management Runtime (the ``AssociationKind.BLUEPRINT`` seam, §6);
    2. builds the :class:`~platform.blueprints.service.BlueprintService` bound to the
       context event bus (so every blueprint action is observed as a governed action);
    3. registers the blueprint health checks into the Observability health registry
       (cross-runtime health integration, G1/OP-C1);
    4. publishes the blueprint contracts into the Foundation service registry
       (EC2-EPIC-001, PL-05); and
    5. emits a deterministic ``blueprints.bootstrap.completed`` event.

It is idempotent on contracts and health checks, fail-closed, consumes EC-1
classification only by reference (read-only, P10), starts no server, opens no socket,
and never writes to the certified corpus (DP-03).
"""

from __future__ import annotations

from platform.blueprints.contracts import BLUEPRINT_CONTRACTS, default_blueprint_contracts
from platform.blueprints.health import blueprint_health_checks
from platform.blueprints.service import BlueprintService, build_blueprint_service
from platform.identity.service import AuthorizationService, bootstrap_identity
from platform.observability.service import ObservabilityService, bootstrap_observability
from platform.projects.service import ProjectService
from platform.workspace.bootstrap import bootstrap_workspace
from platform.workspace.service import WorkspaceService
from typing import Any

#: The event emitted when the Blueprint Runtime is composed onto a context.
BLUEPRINT_BOOTSTRAP_EVENT = "blueprints.bootstrap.completed"


def bootstrap_blueprints(
    context: Any,
    *,
    authorization: AuthorizationService | None = None,
    observability: ObservabilityService | None = None,
    workspace: WorkspaceService | None = None,
    projects: ProjectService | None = None,
) -> BlueprintService:
    """Compose the Blueprint Catalog & Management Runtime onto a :class:`PlatformContext`.

    The parameter is typed loosely to avoid a hard import cycle on the foundation
    bootstrap module. ``projects`` is accepted for composition completeness (the
    EPIC-005 ``AssociationKind.BLUEPRINT`` seam); the blueprint runtime binds workspaces
    directly for parent-scope + isolation and owns the blueprint side of associations
    by reference (§6.3).
    """
    from platform.foundation.services import ServiceDescriptor

    auth = authorization if authorization is not None else bootstrap_identity(context)
    obs = observability if observability is not None else bootstrap_observability(context)
    workspace_service = (
        workspace
        if workspace is not None
        else bootstrap_workspace(context, authorization=auth, observability=obs)
    )

    service = build_blueprint_service(
        authorization=auth,
        workspaces=workspace_service.registry,
        observability=obs,
        events=context.events,
    )

    # Cross-runtime health integration: register blueprint checks into L8 (idempotent).
    for check in blueprint_health_checks():
        if check.name not in obs.health:
            obs.register_health_check(check)

    contracts = {c.name: c for c in default_blueprint_contracts()}
    for ref in BLUEPRINT_CONTRACTS:
        if ref.name in context.services:
            continue
        caps: tuple[str, ...]
        if "classification" in ref.name or "validation" in ref.name:
            caps = ("PC-04",)
        elif "catalog" in ref.name:
            caps = ("PC-05",)
        elif "provenance" in ref.name:
            caps = ("PC-05", "PC-16")
        elif "search" in ref.name:
            caps = ("PC-13",)
        elif "associations" in ref.name:
            caps = ("PC-05",)
        elif "service" in ref.name:
            caps = ("PC-04", "PC-05", "PC-16")
        else:
            caps = ("PC-05",)
        context.services.register(
            ServiceDescriptor(
                name=ref.name,
                contract=contracts[ref.name],
                capabilities=caps,
                description=f"Blueprint Catalog & Management Runtime service: {ref.name}.",
            ),
            provider=lambda svc=service: svc,
        )

    context.events.publish(
        BLUEPRINT_BOOTSTRAP_EVENT,
        source="platform.blueprints.bootstrap",
        subject=context.program_id,
        payload={
            "blueprint_contracts": [ref.name for ref in BLUEPRINT_CONTRACTS],
            "blueprint_groups": ["blueprint-authoring", "blueprint-catalog"],
            "classification_contracts": ["engine.registry.read", "engine.compiler.compile"],
        },
    )
    return service


__all__ = ["BLUEPRINT_BOOTSTRAP_EVENT", "bootstrap_blueprints"]
