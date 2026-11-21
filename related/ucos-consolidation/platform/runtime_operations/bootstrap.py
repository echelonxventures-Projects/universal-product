"""EC2-TASK-000172 — Runtime Operations Bootstrap (EC2-EPIC-012).

Composes the Runtime Operations Runtime onto a
:class:`~platform.foundation.bootstrap.PlatformContext`, registry-driven and
deterministic. It composes the platform end to end: the Identity Layer (L7) and
Observability Layer (L8) are bootstrapped onto the context if not supplied, then the
Runtime Operations Runtime (L8) is built over them. The bootstrap:

    1. reuses/creates the Identity ``AuthorizationService`` and Observability service;
    2. builds the :class:`~platform.runtime_operations.service.RuntimeOperationsService`
       bound to the context event bus (so every governed operation is observed);
    3. registers the runtime health checks into the Observability health registry
       (cross-runtime health integration, G1/G5/OP-C1);
    4. publishes the runtime-operations contracts into the Foundation service registry
       (EC2-EPIC-001, PL-05); and
    5. emits a deterministic ``runtime.operations.bootstrap.completed`` event.

It is idempotent on contracts and health checks, fail-closed, consumes EC-1 runtime and
platform certification only by reference (read-only, L4), governs and records only (no
deployment logic), starts no server, opens no socket, and never writes to the certified
corpus (DP-03).
"""

from __future__ import annotations

from platform.identity.service import AuthorizationService, bootstrap_identity
from platform.observability.service import ObservabilityService, bootstrap_observability
from platform.runtime_operations.contracts import (
    ENGINE_RUNTIME_ASSEMBLE_CONTRACT,
    ENGINE_RUNTIME_DEPLOY_CONTRACT,
    RUNTIME_OPERATIONS_CONTRACTS,
    default_runtime_operations_contracts,
)
from platform.runtime_operations.health import runtime_operations_health_checks
from platform.runtime_operations.service import (
    RuntimeOperationsService,
    build_runtime_operations_service,
)
from typing import Any

#: The event emitted when the Runtime Operations Runtime is composed onto a context.
RUNTIME_OPERATIONS_BOOTSTRAP_EVENT = "runtime.operations.bootstrap.completed"


def bootstrap_runtime_operations(
    context: Any,
    *,
    authorization: AuthorizationService | None = None,
    observability: ObservabilityService | None = None,
) -> RuntimeOperationsService:
    """Compose the Runtime Operations Runtime onto a :class:`PlatformContext`.

    The parameter is typed loosely to avoid a hard import cycle on the foundation
    bootstrap module. The runtime consumes ``engine.runtime`` by reference through the L4
    façade and governs deploy/rollback of CERTIFIED units record-only.
    """
    from platform.foundation.services import ServiceDescriptor

    auth = authorization if authorization is not None else bootstrap_identity(context)
    obs = observability if observability is not None else bootstrap_observability(context)

    service = build_runtime_operations_service(
        authorization=auth,
        observability=obs,
        events=context.events,
    )

    # Cross-runtime health integration: register runtime checks into L8 (idempotent).
    for check in runtime_operations_health_checks():
        if check.name not in obs.health:
            obs.register_health_check(check)

    contracts = {c.name: c for c in default_runtime_operations_contracts()}
    for ref in RUNTIME_OPERATIONS_CONTRACTS:
        if ref.name in context.services:
            continue
        caps: tuple[str, ...]
        if "search" in ref.name:
            caps = ("PC-13",)
        elif "ledger" in ref.name or "lineage" in ref.name:
            caps = ("PC-11", "PC-16")
        elif "service" in ref.name or "operations.orchestrate" in ref.name:
            caps = ("PC-11", "PC-13", "PC-16")
        else:
            caps = ("PC-11",)
        context.services.register(
            ServiceDescriptor(
                name=ref.name,
                contract=contracts[ref.name],
                capabilities=caps,
                description=f"Runtime Operations Runtime service: {ref.name}.",
            ),
            provider=lambda svc=service: svc,
        )

    context.events.publish(
        RUNTIME_OPERATIONS_BOOTSTRAP_EVENT,
        source="platform.runtime_operations.bootstrap",
        subject=context.program_id,
        payload={
            "runtime_operations_contracts": [ref.name for ref in RUNTIME_OPERATIONS_CONTRACTS],
            "runtime_operations_group": "runtime-operations",
            "engine_runtime_contracts": [
                ENGINE_RUNTIME_ASSEMBLE_CONTRACT,
                ENGINE_RUNTIME_DEPLOY_CONTRACT,
            ],
        },
    )
    return service


__all__ = ["RUNTIME_OPERATIONS_BOOTSTRAP_EVENT", "bootstrap_runtime_operations"]
