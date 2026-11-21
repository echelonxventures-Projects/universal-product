"""EC2-TASK-000118 — Generation Request Bootstrap (EC2-EPIC-007).

Composes the Generation Request Runtime onto a
:class:`~platform.foundation.bootstrap.PlatformContext`, registry-driven and
deterministic. It composes the platform end to end: the Identity Layer (L7),
Observability Layer (L8), and Workspace Runtime (L3) are bootstrapped onto the context
if not supplied, then the Generation Request Runtime (L3) is built over them. The
bootstrap:

    1. reuses/creates the Identity ``AuthorizationService``, Observability service, and
       Workspace Runtime (requests are scoped to workspaces — parent binding);
    2. builds the :class:`~platform.generation.service.GenerationRequestService` bound to
       the context event bus (so every request action is observed as a governed action);
    3. registers the request health checks into the Observability health registry
       (cross-runtime health integration, G1/OP-C1);
    4. publishes the generation-request contracts into the Foundation service registry
       (EC2-EPIC-001, PL-05); and
    5. emits a deterministic ``generation.requests.bootstrap.completed`` event.

It is idempotent on contracts and health checks, fail-closed, binds EC-1 execution only
by reference (read-only, P10), starts no server, opens no socket, and never writes to
the certified corpus (DP-03).
"""

from __future__ import annotations

from platform.generation.contracts import (
    GENERATION_REQUEST_CONTRACTS,
    default_generation_request_contracts,
)
from platform.generation.dispatch import all_dispatch_contracts
from platform.generation.health import generation_request_health_checks
from platform.generation.service import (
    GenerationRequestService,
    build_generation_request_service,
)
from platform.identity.service import AuthorizationService, bootstrap_identity
from platform.observability.service import ObservabilityService, bootstrap_observability
from platform.workspace.bootstrap import bootstrap_workspace
from platform.workspace.service import WorkspaceService
from typing import Any

#: The event emitted when the Generation Request Runtime is composed onto a context.
GENERATION_REQUEST_BOOTSTRAP_EVENT = "generation.requests.bootstrap.completed"


def bootstrap_generation_requests(
    context: Any,
    *,
    authorization: AuthorizationService | None = None,
    observability: ObservabilityService | None = None,
    workspace: WorkspaceService | None = None,
) -> GenerationRequestService:
    """Compose the Generation Request Runtime onto a :class:`PlatformContext`.

    The parameter is typed loosely to avoid a hard import cycle on the foundation
    bootstrap module. The request runtime binds workspaces directly for parent-scope +
    isolation and references catalog blueprints (EPIC-006) by reference.
    """
    from platform.foundation.services import ServiceDescriptor

    auth = authorization if authorization is not None else bootstrap_identity(context)
    obs = observability if observability is not None else bootstrap_observability(context)
    workspace_service = (
        workspace
        if workspace is not None
        else bootstrap_workspace(context, authorization=auth, observability=obs)
    )

    service = build_generation_request_service(
        authorization=auth,
        workspaces=workspace_service.registry,
        observability=obs,
        events=context.events,
    )

    # Cross-runtime health integration: register request checks into L8 (idempotent).
    for check in generation_request_health_checks():
        if check.name not in obs.health:
            obs.register_health_check(check)

    contracts = {c.name: c for c in default_generation_request_contracts()}
    for ref in GENERATION_REQUEST_CONTRACTS:
        if ref.name in context.services:
            continue
        caps: tuple[str, ...]
        if "dispatch" in ref.name:
            caps = ("PC-07", "PC-16")
        elif "provenance" in ref.name:
            caps = ("PC-06", "PC-16")
        elif "search" in ref.name:
            caps = ("PC-13",)
        elif "status" in ref.name:
            caps = ("PC-06",)
        elif "service" in ref.name:
            caps = ("PC-06", "PC-07", "PC-16")
        else:
            caps = ("PC-06",)
        context.services.register(
            ServiceDescriptor(
                name=ref.name,
                contract=contracts[ref.name],
                capabilities=caps,
                description=f"Generation Request Runtime service: {ref.name}.",
            ),
            provider=lambda svc=service: svc,
        )

    context.events.publish(
        GENERATION_REQUEST_BOOTSTRAP_EVENT,
        source="platform.generation.bootstrap",
        subject=context.program_id,
        payload={
            "generation_request_contracts": [ref.name for ref in GENERATION_REQUEST_CONTRACTS],
            "generation_request_group": "generation-requests",
            "dispatch_contracts": list(all_dispatch_contracts()),
        },
    )
    return service


__all__ = ["GENERATION_REQUEST_BOOTSTRAP_EVENT", "bootstrap_generation_requests"]
