"""EC2-CAP-ADMIN-001 — Administration Bootstrap (Administration Runtime).

Composes the Administration Runtime onto a
:class:`~platform.foundation.bootstrap.PlatformContext`, registry-driven and
deterministic. It composes the platform end to end: the Identity Layer (L7) and
Observability Layer (L8) are bootstrapped onto the context if not supplied, then the
Administration Runtime is built over them. The bootstrap:

    1. reuses/creates the Identity ``AuthorizationService`` and Observability service;
    2. builds the :class:`~platform.administration.service.AdministrationService` bound
       to the context event bus (so every administrative action is observed as a
       governed action — append-only audit, OP-C3);
    3. registers the administration health checks into the Observability health
       registry (cross-runtime health integration, G1/OP-C1);
    4. publishes the administration contracts into the Foundation service registry
       (EC2-EPIC-001, PL-05); and
    5. emits a deterministic ``administration.bootstrap.completed`` event.

It is idempotent on contracts and health checks, fail-closed, administrative-only,
starts no server, opens no socket, and never writes to the certified corpus (DP-03).
"""

from __future__ import annotations

from platform.administration.contracts import (
    ADMINISTRATION_CONTRACTS,
    default_administration_contracts,
)
from platform.administration.health import administration_health_checks
from platform.administration.service import AdministrationService, build_administration_service
from platform.identity.service import AuthorizationService, bootstrap_identity
from platform.observability.service import ObservabilityService, bootstrap_observability
from typing import Any

#: The event emitted when the Administration Runtime is composed onto a context.
ADMINISTRATION_BOOTSTRAP_EVENT = "administration.bootstrap.completed"


def bootstrap_administration(
    context: Any,
    *,
    authorization: AuthorizationService | None = None,
    observability: ObservabilityService | None = None,
) -> AdministrationService:
    """Compose the Administration Runtime onto a :class:`PlatformContext`.

    The parameter is typed loosely to avoid a hard import cycle on the foundation
    bootstrap module.
    """
    from platform.foundation.services import ServiceDescriptor

    auth = authorization if authorization is not None else bootstrap_identity(context)
    obs = observability if observability is not None else bootstrap_observability(context)

    service = build_administration_service(
        authorization=auth, observability=obs, events=context.events
    )

    # Cross-runtime health integration: register admin checks into L8 (idempotent).
    for check in administration_health_checks():
        if check.name not in obs.health:
            obs.register_health_check(check)

    contracts = {c.name: c for c in default_administration_contracts()}
    for ref in ADMINISTRATION_CONTRACTS:
        if ref.name in context.services:
            continue
        if "audit" in ref.name:
            caps = ("PC-15", "PC-16")
        elif "search" in ref.name:
            caps = ("PC-15", "PC-13")
        else:
            caps = ("PC-15",)
        context.services.register(
            ServiceDescriptor(
                name=ref.name,
                contract=contracts[ref.name],
                capabilities=caps,
                description=f"Administration Runtime service: {ref.name}.",
            ),
            provider=lambda svc=service: svc,
        )

    context.events.publish(
        ADMINISTRATION_BOOTSTRAP_EVENT,
        source="platform.administration.bootstrap",
        subject=context.program_id,
        payload={
            "administration_contracts": [ref.name for ref in ADMINISTRATION_CONTRACTS],
            "administration_group": "administration-policy",
        },
    )
    return service


__all__ = ["ADMINISTRATION_BOOTSTRAP_EVENT", "bootstrap_administration"]
