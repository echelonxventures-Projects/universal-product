"""EC2-TASK-000088 — Workspace Bootstrap (EC2-EPIC-004).

Composes the Workspace Runtime onto a
:class:`~platform.foundation.bootstrap.PlatformContext`, registry-driven and
deterministic. It composes the platform end to end: the Identity Layer (L7) and
Observability Layer (L8) are bootstrapped onto the context if not supplied, then the
Workspace Runtime (L3) is built over them. The bootstrap:

    1. reuses/creates the Identity ``AuthorizationService`` and Observability service;
    2. builds the :class:`~platform.workspace.service.WorkspaceService` bound to the
       context event bus (so every workspace action is observed as a governed action);
    3. registers the workspace health checks into the Observability health registry
       (cross-runtime health integration, G1/OP-C1);
    4. publishes the workspace contracts into the Foundation service registry
       (EC2-EPIC-001, PL-05); and
    5. emits a deterministic ``workspace.bootstrap.completed`` event.

It is idempotent on contracts and health checks, fail-closed, starts no server, opens
no socket, and never writes to the certified corpus (DP-03).
"""

from __future__ import annotations

from platform.identity.service import AuthorizationService, bootstrap_identity
from platform.observability.service import ObservabilityService, bootstrap_observability
from platform.workspace.contracts import WORKSPACE_CONTRACTS, default_workspace_contracts
from platform.workspace.health import workspace_health_checks
from platform.workspace.service import WorkspaceService, build_workspace_service
from typing import Any

#: The event emitted when the Workspace Runtime is composed onto a context.
WORKSPACE_BOOTSTRAP_EVENT = "workspace.bootstrap.completed"


def bootstrap_workspace(
    context: Any,
    *,
    authorization: AuthorizationService | None = None,
    observability: ObservabilityService | None = None,
) -> WorkspaceService:
    """Compose the Workspace Runtime onto a :class:`PlatformContext` (registry-driven).

    The parameter is typed loosely to avoid a hard import cycle on the foundation
    bootstrap module.
    """
    from platform.foundation.services import ServiceDescriptor

    auth = authorization if authorization is not None else bootstrap_identity(context)
    obs = observability if observability is not None else bootstrap_observability(context)

    service = build_workspace_service(authorization=auth, observability=obs, events=context.events)

    # Cross-runtime health integration: register workspace checks into L8 (idempotent).
    for check in workspace_health_checks():
        if check.name not in obs.health:
            obs.register_health_check(check)

    contracts = {c.name: c for c in default_workspace_contracts()}
    for ref in WORKSPACE_CONTRACTS:
        if ref.name in context.services:
            continue
        if "isolation" in ref.name:
            caps = ("PC-03", "PC-16")
        elif "search" in ref.name:
            caps = ("PC-13",)
        else:
            caps = ("PC-03",)
        context.services.register(
            ServiceDescriptor(
                name=ref.name,
                contract=contracts[ref.name],
                capabilities=caps,
                description=f"Workspace Runtime service: {ref.name}.",
            ),
            provider=lambda svc=service: svc,
        )

    context.events.publish(
        WORKSPACE_BOOTSTRAP_EVENT,
        source="platform.workspace.bootstrap",
        subject=context.program_id,
        payload={
            "workspace_contracts": [ref.name for ref in WORKSPACE_CONTRACTS],
            "workspace_group": "workspace-project-lifecycle",
        },
    )
    return service


__all__ = ["WORKSPACE_BOOTSTRAP_EVENT", "bootstrap_workspace"]
