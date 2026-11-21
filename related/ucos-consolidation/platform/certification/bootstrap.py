"""EC2-TASK-000161 — Certification Console Bootstrap (EC2-EPIC-011).

Composes the Certification Console & Ledger Runtime onto a
:class:`~platform.foundation.bootstrap.PlatformContext`, registry-driven and
deterministic. It composes the platform end to end: the Identity Layer (L7) and
Observability Layer (L8) are bootstrapped onto the context if not supplied, then the
Certification Console Runtime (L3) is built over them. The bootstrap:

    1. reuses/creates the Identity ``AuthorizationService`` and Observability service;
    2. builds the :class:`~platform.certification.service.CertificationConsoleService`
       bound to the context event bus (so every console action is observed as a governed
       action);
    3. registers the console health checks into the Observability health registry
       (cross-runtime health integration, G1/G5/OP-C1);
    4. publishes the certification-console contracts into the Foundation service registry
       (EC2-EPIC-001, PL-05); and
    5. emits a deterministic ``certification.console.bootstrap.completed`` event.

It is idempotent on contracts and health checks, fail-closed, consumes EC-1
certification only by reference (read-only, L4), starts no server, opens no socket, and
never writes to the certified corpus (DP-03).
"""

from __future__ import annotations

from platform.certification.contracts import (
    CERTIFICATION_CONSOLE_CONTRACTS,
    ENGINE_CERTIFICATION_CONTRACT,
    default_certification_console_contracts,
)
from platform.certification.health import certification_console_health_checks
from platform.certification.service import (
    CertificationConsoleService,
    build_certification_console_service,
)
from platform.identity.service import AuthorizationService, bootstrap_identity
from platform.observability.service import ObservabilityService, bootstrap_observability
from typing import Any

#: The event emitted when the Certification Console Runtime is composed onto a context.
CERTIFICATION_CONSOLE_BOOTSTRAP_EVENT = "certification.console.bootstrap.completed"


def bootstrap_certification_console(
    context: Any,
    *,
    authorization: AuthorizationService | None = None,
    observability: ObservabilityService | None = None,
) -> CertificationConsoleService:
    """Compose the Certification Console & Ledger Runtime onto a :class:`PlatformContext`.

    The parameter is typed loosely to avoid a hard import cycle on the foundation
    bootstrap module. The console consumes ``engine.certification`` by reference through
    the L4 façade and surfaces certified certification output read-only.
    """
    from platform.foundation.services import ServiceDescriptor

    auth = authorization if authorization is not None else bootstrap_identity(context)
    obs = observability if observability is not None else bootstrap_observability(context)

    service = build_certification_console_service(
        authorization=auth,
        observability=obs,
        events=context.events,
    )

    # Cross-runtime health integration: register console checks into L8 (idempotent).
    for check in certification_console_health_checks():
        if check.name not in obs.health:
            obs.register_health_check(check)

    contracts = {c.name: c for c in default_certification_console_contracts()}
    for ref in CERTIFICATION_CONSOLE_CONTRACTS:
        if ref.name in context.services:
            continue
        caps: tuple[str, ...]
        if "search" in ref.name:
            caps = ("PC-13",)
        elif "ledger" in ref.name or "lineage" in ref.name or "trace" in ref.name:
            caps = ("PC-10", "PC-16")
        elif "service" in ref.name:
            caps = ("PC-10", "PC-13", "PC-16")
        else:
            caps = ("PC-10",)
        context.services.register(
            ServiceDescriptor(
                name=ref.name,
                contract=contracts[ref.name],
                capabilities=caps,
                description=f"Certification Console Runtime service: {ref.name}.",
            ),
            provider=lambda svc=service: svc,
        )

    context.events.publish(
        CERTIFICATION_CONSOLE_BOOTSTRAP_EVENT,
        source="platform.certification.bootstrap",
        subject=context.program_id,
        payload={
            "certification_console_contracts": [
                ref.name for ref in CERTIFICATION_CONSOLE_CONTRACTS
            ],
            "certification_console_group": "certification-ledger",
            "engine_certification_contract": ENGINE_CERTIFICATION_CONTRACT,
        },
    )
    return service


__all__ = ["CERTIFICATION_CONSOLE_BOOTSTRAP_EVENT", "bootstrap_certification_console"]
