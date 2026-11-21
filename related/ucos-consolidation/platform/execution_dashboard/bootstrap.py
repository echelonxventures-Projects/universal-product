"""EC2-TASK-000133 — Execution Dashboard Bootstrap (EC2-EPIC-008).

Composes the Execution Dashboard Runtime onto a
:class:`~platform.foundation.bootstrap.PlatformContext`, registry-driven and deterministic.
It composes the platform end to end: the Identity Layer (L7), Observability Layer (L8), and
Generation Request Runtime (L3, EPIC-007) are bootstrapped onto the context if not supplied,
then the Execution Dashboard Runtime (L3) is built over them. The bootstrap:

    1. reuses/creates the Identity ``AuthorizationService``, Observability service, and
       Generation Request Runtime (the dashboard's read source, consumed by reference);
    2. builds the :class:`~platform.execution_dashboard.service.ExecutionDashboardService`
       bound to the context event bus (so every dashboard action is observed as a governed
       action);
    3. registers the dashboard health checks into the Observability health registry
       (cross-runtime health integration, G1/OP-C1);
    4. publishes the execution-dashboard contracts into the Foundation service registry
       (EC2-EPIC-001, PL-05); and
    5. emits a deterministic ``dashboard.bootstrap.completed`` event.

It is idempotent on contracts and health checks, fail-closed, consumes EPIC-007 only by
reference (read-only, P10), starts no server, opens no socket, and never writes to the
certified corpus (DP-03).
"""

from __future__ import annotations

from platform.execution_dashboard.contracts import (
    EXECUTION_DASHBOARD_CONTRACTS,
    default_execution_dashboard_contracts,
)
from platform.execution_dashboard.health import execution_dashboard_health_checks
from platform.execution_dashboard.service import (
    ExecutionDashboardService,
    build_execution_dashboard_service,
)
from platform.generation.bootstrap import bootstrap_generation_requests
from platform.generation.service import GenerationRequestService
from platform.identity.service import AuthorizationService, bootstrap_identity
from platform.observability.service import ObservabilityService, bootstrap_observability
from typing import Any

#: The event emitted when the Execution Dashboard Runtime is composed onto a context.
EXECUTION_DASHBOARD_BOOTSTRAP_EVENT = "dashboard.bootstrap.completed"


def _capabilities_for(name: str) -> tuple[str, ...]:
    """The Program capability codes a dashboard service contract provides (by name)."""
    if "search" in name:
        return ("PC-08", "PC-13")
    if "health" in name:
        return ("PC-08", "PC-12")
    if "service" in name:
        return ("PC-08", "PC-12", "PC-13", "PC-16")
    return ("PC-08",)


def bootstrap_execution_dashboard(
    context: Any,
    *,
    authorization: AuthorizationService | None = None,
    observability: ObservabilityService | None = None,
    generation: GenerationRequestService | None = None,
) -> ExecutionDashboardService:
    """Compose the Execution Dashboard Runtime onto a :class:`PlatformContext`.

    The parameter is typed loosely to avoid a hard import cycle on the foundation
    bootstrap module. The dashboard consumes the Generation Request Runtime (EPIC-007) as
    its read source **by reference** and surfaces observability emitted by EPIC-013.
    """
    from platform.foundation.services import ServiceDescriptor

    auth = authorization if authorization is not None else bootstrap_identity(context)
    obs = observability if observability is not None else bootstrap_observability(context)
    generation_service = (
        generation
        if generation is not None
        else bootstrap_generation_requests(context, authorization=auth, observability=obs)
    )

    service = build_execution_dashboard_service(
        generation=generation_service,
        authorization=auth,
        observability=obs,
        events=context.events,
    )

    # Cross-runtime health integration: register dashboard checks into L8 (idempotent).
    for check in execution_dashboard_health_checks():
        if check.name not in obs.health:
            obs.register_health_check(check)

    contracts = {c.name: c for c in default_execution_dashboard_contracts()}
    for ref in EXECUTION_DASHBOARD_CONTRACTS:
        if ref.name in context.services:
            continue
        context.services.register(
            ServiceDescriptor(
                name=ref.name,
                contract=contracts[ref.name],
                capabilities=_capabilities_for(ref.name),
                description=f"Execution Dashboard Runtime service: {ref.name}.",
            ),
            provider=lambda svc=service: svc,
        )

    context.events.publish(
        EXECUTION_DASHBOARD_BOOTSTRAP_EVENT,
        source="platform.execution_dashboard.bootstrap",
        subject=context.program_id,
        payload={
            "execution_dashboard_contracts": [ref.name for ref in EXECUTION_DASHBOARD_CONTRACTS],
            "execution_dashboard_group": "execution-dashboard",
            "observed_generation_events": list(service.observed_generation_events),
            "observed_generation_metrics": list(service.observed_generation_metrics),
        },
    )
    return service


__all__ = ["EXECUTION_DASHBOARD_BOOTSTRAP_EVENT", "bootstrap_execution_dashboard"]
