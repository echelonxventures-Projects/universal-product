"""EC2-TASK-000152 — Validation Console Bootstrap (EC2-EPIC-010).

Composes the Validation Console Runtime onto a
:class:`~platform.foundation.bootstrap.PlatformContext`, registry-driven and
deterministic. It composes the platform end to end: the Identity Layer (L7) and
Observability Layer (L8) are bootstrapped onto the context if not supplied, then the
Validation Console Runtime (L3) is built over them. The bootstrap:

    1. reuses/creates the Identity ``AuthorizationService`` and Observability service;
    2. builds the :class:`~platform.validation.service.ValidationConsoleService` bound to
       the context event bus (so every console action is observed as a governed action);
    3. registers the console health checks into the Observability health registry
       (cross-runtime health integration, G1/G5/OP-C1);
    4. publishes the validation-console contracts into the Foundation service registry
       (EC2-EPIC-001, PL-05); and
    5. emits a deterministic ``validation.console.bootstrap.completed`` event.

It is idempotent on contracts and health checks, fail-closed, consumes EC-1 validation
only by reference (read-only, L4), starts no server, opens no socket, and never writes to
the certified corpus (DP-03).
"""

from __future__ import annotations

from platform.identity.service import AuthorizationService, bootstrap_identity
from platform.observability.service import ObservabilityService, bootstrap_observability
from platform.validation.contracts import (
    ENGINE_VALIDATION_CONTRACT,
    VALIDATION_CONSOLE_CONTRACTS,
    default_validation_console_contracts,
)
from platform.validation.health import validation_console_health_checks
from platform.validation.service import (
    ValidationConsoleService,
    build_validation_console_service,
)
from typing import Any

#: The event emitted when the Validation Console Runtime is composed onto a context.
VALIDATION_CONSOLE_BOOTSTRAP_EVENT = "validation.console.bootstrap.completed"


def bootstrap_validation_console(
    context: Any,
    *,
    authorization: AuthorizationService | None = None,
    observability: ObservabilityService | None = None,
) -> ValidationConsoleService:
    """Compose the Validation Console Runtime onto a :class:`PlatformContext`.

    The parameter is typed loosely to avoid a hard import cycle on the foundation
    bootstrap module. The console consumes ``engine.validation`` by reference through the
    L4 façade and surfaces certified validation output read-only.
    """
    from platform.foundation.services import ServiceDescriptor

    auth = authorization if authorization is not None else bootstrap_identity(context)
    obs = observability if observability is not None else bootstrap_observability(context)

    service = build_validation_console_service(
        authorization=auth,
        observability=obs,
        events=context.events,
    )

    # Cross-runtime health integration: register console checks into L8 (idempotent).
    for check in validation_console_health_checks():
        if check.name not in obs.health:
            obs.register_health_check(check)

    contracts = {c.name: c for c in default_validation_console_contracts()}
    for ref in VALIDATION_CONSOLE_CONTRACTS:
        if ref.name in context.services:
            continue
        caps: tuple[str, ...]
        if "search" in ref.name:
            caps = ("PC-13",)
        elif "trace" in ref.name:
            caps = ("PC-09", "PC-16")
        elif "service" in ref.name:
            caps = ("PC-09", "PC-13", "PC-16")
        else:
            caps = ("PC-09",)
        context.services.register(
            ServiceDescriptor(
                name=ref.name,
                contract=contracts[ref.name],
                capabilities=caps,
                description=f"Validation Console Runtime service: {ref.name}.",
            ),
            provider=lambda svc=service: svc,
        )

    context.events.publish(
        VALIDATION_CONSOLE_BOOTSTRAP_EVENT,
        source="platform.validation.bootstrap",
        subject=context.program_id,
        payload={
            "validation_console_contracts": [ref.name for ref in VALIDATION_CONSOLE_CONTRACTS],
            "validation_console_group": "validation-explorer",
            "engine_validation_contract": ENGINE_VALIDATION_CONTRACT,
        },
    )
    return service


__all__ = ["VALIDATION_CONSOLE_BOOTSTRAP_EVENT", "bootstrap_validation_console"]
