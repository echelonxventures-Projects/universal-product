"""EC2-TASK-000134 — Artifact Explorer Bootstrap (EC2-EPIC-009).

Composes the Artifact Explorer Runtime onto a
:class:`~platform.foundation.bootstrap.PlatformContext`, registry-driven and
deterministic. It composes the platform end to end: the Identity Layer (L7), Observability
Layer (L8), and the Generation Request Runtime (EC2-EPIC-007, L3 — the producer of the
artifact/dispatch/provenance references) are bootstrapped onto the context if not
supplied, then the Artifact Explorer Runtime (L3) is built **over** them, consuming their
records by reference. The bootstrap:

    1. reuses/creates the Identity ``AuthorizationService``, Observability service, and
       the Generation Request Runtime (the explorer consumes its registry/dispatch/
       provenance by reference);
    2. builds the :class:`~platform.artifact_explorer.service.ArtifactExplorerService`
       bound to the context event bus (so every navigation is observed as a governed
       action);
    3. registers the explorer health checks into the Observability health registry
       (cross-runtime health integration, G1/OP-C1);
    4. publishes the artifact-explorer contracts into the Foundation service registry
       (EC2-EPIC-001, PL-05); and
    5. emits a deterministic ``artifact.explorer.bootstrap.completed`` event.

It is idempotent on contracts and health checks, fail-closed, read-only over all consumed
records, generates no artifact, mutates no artifact, executes no engine, starts no server,
opens no socket, and never writes to the certified corpus (DP-03).
"""

from __future__ import annotations

from platform.artifact_explorer.contracts import (
    ARTIFACT_EXPLORER_CONTRACTS,
    default_artifact_explorer_contracts,
)
from platform.artifact_explorer.health import artifact_explorer_health_checks
from platform.artifact_explorer.service import (
    ArtifactExplorerService,
    build_artifact_explorer_service,
)
from platform.generation.bootstrap import bootstrap_generation_requests
from platform.generation.service import GenerationRequestService
from platform.identity.service import AuthorizationService, bootstrap_identity
from platform.observability.service import ObservabilityService, bootstrap_observability
from typing import Any

#: The event emitted when the Artifact Explorer Runtime is composed onto a context.
ARTIFACT_EXPLORER_BOOTSTRAP_EVENT = "artifact.explorer.bootstrap.completed"


def bootstrap_artifact_explorer(
    context: Any,
    *,
    authorization: AuthorizationService | None = None,
    observability: ObservabilityService | None = None,
    generation: GenerationRequestService | None = None,
) -> ArtifactExplorerService:
    """Compose the Artifact Explorer Runtime onto a :class:`PlatformContext`.

    The parameter is typed loosely to avoid a hard import cycle on the foundation
    bootstrap module. The explorer consumes the EC2-EPIC-007 Generation Request Runtime's
    registry, dispatch ledger, and provenance ledger **by reference** (read-only).
    """
    from platform.foundation.services import ServiceDescriptor

    auth = authorization if authorization is not None else bootstrap_identity(context)
    obs = observability if observability is not None else bootstrap_observability(context)
    generation_service = (
        generation
        if generation is not None
        else bootstrap_generation_requests(context, authorization=auth, observability=obs)
    )

    service = build_artifact_explorer_service(
        authorization=auth,
        registry=generation_service.registry,
        dispatch=generation_service.dispatch,
        provenance=generation_service.provenance,
        observability=obs,
        events=context.events,
    )

    # Cross-runtime health integration: register explorer checks into L8 (idempotent).
    for check in artifact_explorer_health_checks():
        if check.name not in obs.health:
            obs.register_health_check(check)

    contracts = {c.name: c for c in default_artifact_explorer_contracts()}
    for ref in ARTIFACT_EXPLORER_CONTRACTS:
        if ref.name in context.services:
            continue
        caps: tuple[str, ...]
        if "search" in ref.name:
            caps = ("PC-13",)
        elif "trace" in ref.name or "provenance" in ref.name or "lineage" in ref.name:
            caps = ("PC-08", "PC-16")
        elif "service" in ref.name:
            caps = ("PC-08", "PC-13", "PC-16")
        else:
            caps = ("PC-08",)
        context.services.register(
            ServiceDescriptor(
                name=ref.name,
                contract=contracts[ref.name],
                capabilities=caps,
                description=f"Artifact Explorer Runtime service: {ref.name}.",
            ),
            provider=lambda svc=service: svc,
        )

    context.events.publish(
        ARTIFACT_EXPLORER_BOOTSTRAP_EVENT,
        source="platform.artifact_explorer.bootstrap",
        subject=context.program_id,
        payload={
            "artifact_explorer_contracts": [ref.name for ref in ARTIFACT_EXPLORER_CONTRACTS],
            "artifact_explorer_group": "artifact-explorer",
        },
    )
    return service


__all__ = ["ARTIFACT_EXPLORER_BOOTSTRAP_EVENT", "bootstrap_artifact_explorer"]
