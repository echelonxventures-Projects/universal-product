"""EC2-TASK-000096 — Project Bootstrap (EC2-EPIC-005).

Composes the Project Management Runtime onto a
:class:`~platform.foundation.bootstrap.PlatformContext`, registry-driven and
deterministic. It composes the platform end to end: the Identity Layer (L7),
Observability Layer (L8), and Workspace Runtime (L3) are bootstrapped onto the context
if not supplied, then the Project Management Runtime (L3) is built over them. The
bootstrap:

    1. reuses/creates the Identity ``AuthorizationService``, Observability service, and
       Workspace Runtime (projects are scoped to workspaces — parent binding);
    2. builds the :class:`~platform.projects.service.ProjectService` bound to the
       context event bus (so every project action is observed as a governed action);
    3. registers the project health checks into the Observability health registry
       (cross-runtime health integration, G1/OP-C1);
    4. publishes the project contracts into the Foundation service registry
       (EC2-EPIC-001, PL-05); and
    5. emits a deterministic ``projects.bootstrap.completed`` event.

It is idempotent on contracts and health checks, fail-closed, resolves no downstream
(blueprint/request/artifact) runtime, starts no server, opens no socket, and never
writes to the certified corpus (DP-03).
"""

from __future__ import annotations

from platform.identity.service import AuthorizationService, bootstrap_identity
from platform.observability.service import ObservabilityService, bootstrap_observability
from platform.projects.contracts import PROJECT_CONTRACTS, default_project_contracts
from platform.projects.health import project_health_checks
from platform.projects.service import ProjectService, build_project_service
from platform.workspace.bootstrap import bootstrap_workspace
from platform.workspace.service import WorkspaceService
from typing import Any

#: The event emitted when the Project Management Runtime is composed onto a context.
PROJECT_BOOTSTRAP_EVENT = "projects.bootstrap.completed"


def bootstrap_projects(
    context: Any,
    *,
    authorization: AuthorizationService | None = None,
    observability: ObservabilityService | None = None,
    workspace: WorkspaceService | None = None,
) -> ProjectService:
    """Compose the Project Management Runtime onto a :class:`PlatformContext`.

    The parameter is typed loosely to avoid a hard import cycle on the foundation
    bootstrap module.
    """
    from platform.foundation.services import ServiceDescriptor

    auth = authorization if authorization is not None else bootstrap_identity(context)
    obs = observability if observability is not None else bootstrap_observability(context)
    workspace_service = (
        workspace
        if workspace is not None
        else bootstrap_workspace(context, authorization=auth, observability=obs)
    )

    service = build_project_service(
        authorization=auth,
        workspaces=workspace_service.registry,
        observability=obs,
        events=context.events,
    )

    # Cross-runtime health integration: register project checks into L8 (idempotent).
    for check in project_health_checks():
        if check.name not in obs.health:
            obs.register_health_check(check)

    contracts = {c.name: c for c in default_project_contracts()}
    for ref in PROJECT_CONTRACTS:
        if ref.name in context.services:
            continue
        caps: tuple[str, ...]
        if "associations" in ref.name:
            caps = ("PC-03",)
        elif "search" in ref.name:
            caps = ("PC-13",)
        elif "service" in ref.name:
            caps = ("PC-03", "PC-16")
        else:
            caps = ("PC-03",)
        context.services.register(
            ServiceDescriptor(
                name=ref.name,
                contract=contracts[ref.name],
                capabilities=caps,
                description=f"Project Management Runtime service: {ref.name}.",
            ),
            provider=lambda svc=service: svc,
        )

    context.events.publish(
        PROJECT_BOOTSTRAP_EVENT,
        source="platform.projects.bootstrap",
        subject=context.program_id,
        payload={
            "project_contracts": [ref.name for ref in PROJECT_CONTRACTS],
            "project_group": "workspace-project-lifecycle",
        },
    )
    return service


__all__ = ["PROJECT_BOOTSTRAP_EVENT", "bootstrap_projects"]
