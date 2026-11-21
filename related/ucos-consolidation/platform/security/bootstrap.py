"""EC2-CAP-SEC-001 — Security Runtime bootstrap (composition entry points).

Composes the implemented Security Runtime sub-capabilities onto a
:class:`~platform.foundation.bootstrap.PlatformContext`, additively and
deterministically:

    * :func:`bootstrap_security_classification` — **SEC-CLASS** (Phase 1): reuses the
      certified L7 Identity Layer as the enforcement seam the classification runtime
      resolves references against (no authorization logic created/invoked); publishes
      the SEC-CLASS contracts; emits ``security.classification.bootstrap.completed``.
    * :func:`bootstrap_security_intelligence` — **SEC-INTEL** (Phase 2): builds the
      record-only intelligence runtime bound to the context event bus; publishes the
      SEC-INTEL contracts; emits ``security.intelligence.bootstrap.completed``.
    * :func:`bootstrap_security_registry` — **SEC-REG** (Phase 3): builds the seven
      §17 record-only registries bound to the context event bus; publishes the
      SEC-REG contracts; emits ``security.registry.bootstrap.completed``.
    * :func:`bootstrap_security_observability` — **SEC-OBS** (Phase 4): shapes the
      ``security`` signal dimension + telemetry through the certified L8 Observability
      Layer; publishes the SEC-OBS contracts; emits
      ``security.observability.bootstrap.completed``.
    * :func:`bootstrap_security_certification` — **SEC-CERT** (Phase 5): builds the
      record-only §18 certification runtime bound to the context event bus; publishes
      the SEC-CERT contracts; emits ``security.certification.bootstrap.completed``.
    * :func:`bootstrap_security_zone` — **SEC-ZONE** (Phase 6): builds the record-only
      UMB-015 five-zone / seven-control posture runtime bound to the context event bus;
      publishes the SEC-ZONE contracts; emits ``security.zone.bootstrap.completed``.

Each composition binds its service to the context event bus so every recorded action
is a governed event the L8 Observability Layer can audit (PC-16).

Scope guardrail: these compose the six record-only Security Runtime sub-capabilities
(**SEC-CLASS, SEC-INTEL, SEC-REG, SEC-OBS, SEC-CERT, SEC-ZONE**). They start no server,
open no socket, render no UI, write nothing to the certified corpus (DP-03). They
authorize, ratify, and enact nothing (RG-02 / AR-04).
"""

from __future__ import annotations

from platform.foundation.services import ServiceDescriptor
from platform.identity.service import AuthorizationService, bootstrap_identity
from platform.observability.service import ObservabilityService, build_observability_service
from platform.security.certification import (
    SecurityCertificationService,
    build_security_certification_service,
)
from platform.security.contracts import (
    SECURITY_CERTIFICATION_CONTRACTS,
    SECURITY_CLASSIFICATION_CONTRACTS,
    SECURITY_INTELLIGENCE_CONTRACTS,
    SECURITY_OBSERVABILITY_CONTRACTS,
    SECURITY_REGISTRY_CONTRACTS,
    SECURITY_ZONE_CONTRACTS,
    default_security_certification_contracts,
    default_security_classification_contracts,
    default_security_intelligence_contracts,
    default_security_observability_contracts,
    default_security_registry_contracts,
    default_security_zone_contracts,
)
from platform.security.errors import SecurityBootstrapError
from platform.security.intelligence import (
    SecurityIntelligenceService,
    build_security_intelligence_service,
)
from platform.security.observability import (
    SecurityObservabilityService,
    build_security_observability_service,
)
from platform.security.registries import (
    SecurityRegistryService,
    build_security_registry_service,
)
from platform.security.service import (
    SecurityClassificationService,
    build_security_classification_service,
)
from platform.security.zones import (
    SecurityZoneService,
    build_security_zone_service,
)
from typing import Any

#: The event emitted when the Security Classification Runtime is composed.
SECURITY_CLASSIFICATION_BOOTSTRAP_EVENT = "security.classification.bootstrap.completed"

#: The event emitted when the Security Intelligence Runtime is composed.
SECURITY_INTELLIGENCE_BOOTSTRAP_EVENT = "security.intelligence.bootstrap.completed"

#: The event emitted when the Security Registry Runtime is composed.
SECURITY_REGISTRY_BOOTSTRAP_EVENT = "security.registry.bootstrap.completed"

#: The event emitted when the Security Observability Runtime is composed.
SECURITY_OBSERVABILITY_BOOTSTRAP_EVENT = "security.observability.bootstrap.completed"

#: The event emitted when the Security Certification Runtime is composed.
SECURITY_CERTIFICATION_BOOTSTRAP_EVENT = "security.certification.bootstrap.completed"

#: The event emitted when the Zone & Control Posture Runtime is composed.
SECURITY_ZONE_BOOTSTRAP_EVENT = "security.zone.bootstrap.completed"


def bootstrap_security_classification(
    context: Any,
    *,
    authorization: AuthorizationService | None = None,
) -> SecurityClassificationService:
    """Compose the Security Classification Runtime onto a :class:`PlatformContext`.

    Args:
        context: the composed Platform Foundation context (provides ``services``,
            ``events``, and ``program_id``).
        authorization: an already-composed L7 :class:`AuthorizationService`; when
            ``None`` the certified Identity Layer is bootstrapped onto ``context``
            (idempotent) and reused as the enforcement seam.

    Raises:
        SecurityBootstrapError: on any composition failure (fail-closed).
    """
    try:
        seam = authorization if authorization is not None else bootstrap_identity(context)
        service = build_security_classification_service(authorization=seam, events=context.events)

        contracts = {c.name: c for c in default_security_classification_contracts()}
        for ref in SECURITY_CLASSIFICATION_CONTRACTS:
            if ref.name in context.services:
                continue
            context.services.register(
                ServiceDescriptor(
                    name=ref.name,
                    contract=contracts[ref.name],
                    capabilities=("PC-02", "PC-16"),
                    description=f"Security Classification Runtime service: {ref.name}.",
                ),
                provider=lambda svc=service: svc,
            )
    except SecurityBootstrapError:
        raise
    except Exception as exc:  # noqa: BLE001 — normalize into a fail-closed error
        raise SecurityBootstrapError(
            "security classification runtime bootstrap failed", detail=str(exc)
        ) from exc

    context.events.publish(
        SECURITY_CLASSIFICATION_BOOTSTRAP_EVENT,
        source="platform.security.bootstrap",
        subject=context.program_id,
        payload={
            "classification_contracts": [ref.name for ref in SECURITY_CLASSIFICATION_CONTRACTS],
            "authorization_bound": service.authorization_bound,
            "ledger_fingerprint": service.ledger.fingerprint(),
        },
    )
    return service


def bootstrap_security_intelligence(
    context: Any,
) -> SecurityIntelligenceService:
    """Compose the Security Intelligence Runtime onto a :class:`PlatformContext`.

    Builds the :class:`~platform.security.intelligence.SecurityIntelligenceService`
    bound to the context event bus (so every recorded finding and roll-up is a
    governed event the L8 Observability Layer can audit), publishes the SEC-INTEL
    contracts into the foundation service registry (contract-first, PL-05), and emits
    a deterministic ``security.intelligence.bootstrap.completed`` event. It records
    and rolls up only; it authorizes, ratifies, and enacts nothing (RG-02 / AR-04),
    stores no secret value (SEC-04 / RR-07), and writes nothing to the corpus (DP-03).

    Raises:
        SecurityBootstrapError: on any composition failure (fail-closed).
    """
    try:
        service = build_security_intelligence_service(events=context.events)

        contracts = {c.name: c for c in default_security_intelligence_contracts()}
        for ref in SECURITY_INTELLIGENCE_CONTRACTS:
            if ref.name in context.services:
                continue
            context.services.register(
                ServiceDescriptor(
                    name=ref.name,
                    contract=contracts[ref.name],
                    capabilities=("PC-02", "PC-16"),
                    description=f"Security Intelligence Runtime service: {ref.name}.",
                ),
                provider=lambda svc=service: svc,
            )
    except SecurityBootstrapError:
        raise
    except Exception as exc:  # noqa: BLE001 — normalize into a fail-closed error
        raise SecurityBootstrapError(
            "security intelligence runtime bootstrap failed", detail=str(exc)
        ) from exc

    context.events.publish(
        SECURITY_INTELLIGENCE_BOOTSTRAP_EVENT,
        source="platform.security.bootstrap",
        subject=context.program_id,
        payload={
            "intelligence_contracts": [ref.name for ref in SECURITY_INTELLIGENCE_CONTRACTS],
            "ledger_fingerprint": service.ledger.fingerprint(),
        },
    )
    return service


def bootstrap_security_registry(
    context: Any,
) -> SecurityRegistryService:
    """Compose the Security Registry Runtime onto a :class:`PlatformContext`.

    Builds the :class:`~platform.security.registries.SecurityRegistryService` bound to
    the context event bus (so every recorded registry entry is a governed event the L8
    Observability Layer can audit), publishes the SEC-REG contracts into the foundation
    service registry (contract-first, PL-05), and emits a deterministic
    ``security.registry.bootstrap.completed`` event. The seven §17 registries record
    only; they ratify and enact nothing (RG-02 / AR-04), store no secret value
    (SEC-04 / RR-07), and write nothing to the corpus (DP-03).

    Raises:
        SecurityBootstrapError: on any composition failure (fail-closed).
    """
    try:
        service = build_security_registry_service(events=context.events)

        contracts = {c.name: c for c in default_security_registry_contracts()}
        for ref in SECURITY_REGISTRY_CONTRACTS:
            if ref.name in context.services:
                continue
            context.services.register(
                ServiceDescriptor(
                    name=ref.name,
                    contract=contracts[ref.name],
                    capabilities=("PC-02", "PC-16"),
                    description=f"Security Registry Runtime service: {ref.name}.",
                ),
                provider=lambda svc=service: svc,
            )
    except SecurityBootstrapError:
        raise
    except Exception as exc:  # noqa: BLE001 — normalize into a fail-closed error
        raise SecurityBootstrapError(
            "security registry runtime bootstrap failed", detail=str(exc)
        ) from exc

    context.events.publish(
        SECURITY_REGISTRY_BOOTSTRAP_EVENT,
        source="platform.security.bootstrap",
        subject=context.program_id,
        payload={
            "registry_contracts": [ref.name for ref in SECURITY_REGISTRY_CONTRACTS],
            "registry_count": len(service.registries.kinds),
            "set_fingerprint": service.registries.fingerprint(),
        },
    )
    return service


def bootstrap_security_observability(
    context: Any,
    *,
    observability: ObservabilityService | None = None,
) -> SecurityObservabilityService:
    """Compose the Security Observability Runtime onto a :class:`PlatformContext`.

    Shapes the ``security`` signal dimension + telemetry **through** a certified L8
    :class:`~platform.observability.service.ObservabilityService` (reused, never
    duplicated). When ``observability`` is ``None`` a fresh L8 layer is composed via
    the certified :func:`build_observability_service`; SEC-OBS defines no second
    telemetry stack. Publishes the SEC-OBS contracts (contract-first, PL-05) and emits
    a deterministic ``security.observability.bootstrap.completed`` event. Records only;
    it authorizes/ratifies/enacts nothing (RG-02 / AR-04), stores no secret (SEC-04 /
    RR-07), and writes nothing to the corpus (DP-03).

    Raises:
        SecurityBootstrapError: on any composition failure (fail-closed).
    """
    try:
        obs = observability if observability is not None else build_observability_service()
        service = build_security_observability_service(observability=obs, events=context.events)

        contracts = {c.name: c for c in default_security_observability_contracts()}
        for ref in SECURITY_OBSERVABILITY_CONTRACTS:
            if ref.name in context.services:
                continue
            context.services.register(
                ServiceDescriptor(
                    name=ref.name,
                    contract=contracts[ref.name],
                    capabilities=("PC-12", "PC-16"),
                    description=f"Security Observability Runtime service: {ref.name}.",
                ),
                provider=lambda svc=service: svc,
            )
    except SecurityBootstrapError:
        raise
    except Exception as exc:  # noqa: BLE001 — normalize into a fail-closed error
        raise SecurityBootstrapError(
            "security observability runtime bootstrap failed", detail=str(exc)
        ) from exc

    context.events.publish(
        SECURITY_OBSERVABILITY_BOOTSTRAP_EVENT,
        source="platform.security.bootstrap",
        subject=context.program_id,
        payload={
            "observability_contracts": [ref.name for ref in SECURITY_OBSERVABILITY_CONTRACTS],
            "signal_dimension": "security",
            "ledger_fingerprint": service.ledger.fingerprint(),
        },
    )
    return service


def bootstrap_security_certification(
    context: Any,
) -> SecurityCertificationService:
    """Compose the Security Certification Runtime onto a :class:`PlatformContext`.

    Builds the :class:`~platform.security.certification.SecurityCertificationService`
    bound to the context event bus (so every recorded certification is a governed event
    the L8 Observability Layer can audit), publishes the SEC-CERT contracts
    (contract-first, PL-05), and emits a deterministic
    ``security.certification.bootstrap.completed`` event. Certification is record-only,
    immutable, evidence-backed, and non-constitutive (STATUS-001 §2); it authorizes,
    ratifies, and enacts nothing (RG-02 / AR-04), stores no secret (SEC-04 / RR-07), and
    writes nothing to the corpus (DP-03).

    Raises:
        SecurityBootstrapError: on any composition failure (fail-closed).
    """
    try:
        service = build_security_certification_service(events=context.events)

        contracts = {c.name: c for c in default_security_certification_contracts()}
        for ref in SECURITY_CERTIFICATION_CONTRACTS:
            if ref.name in context.services:
                continue
            context.services.register(
                ServiceDescriptor(
                    name=ref.name,
                    contract=contracts[ref.name],
                    capabilities=("PC-02", "PC-16"),
                    description=f"Security Certification Runtime service: {ref.name}.",
                ),
                provider=lambda svc=service: svc,
            )
    except SecurityBootstrapError:
        raise
    except Exception as exc:  # noqa: BLE001 — normalize into a fail-closed error
        raise SecurityBootstrapError(
            "security certification runtime bootstrap failed", detail=str(exc)
        ) from exc

    context.events.publish(
        SECURITY_CERTIFICATION_BOOTSTRAP_EVENT,
        source="platform.security.bootstrap",
        subject=context.program_id,
        payload={
            "certification_contracts": [ref.name for ref in SECURITY_CERTIFICATION_CONTRACTS],
            "ledger_fingerprint": service.ledger.fingerprint(),
        },
    )
    return service


def bootstrap_security_zone(
    context: Any,
) -> SecurityZoneService:
    """Compose the Zone & Control Posture Runtime onto a :class:`PlatformContext`.

    Builds the :class:`~platform.security.zones.SecurityZoneService` bound to the
    context event bus (so every recorded posture is a governed event the L8
    Observability Layer can audit), publishes the SEC-ZONE contracts (contract-first,
    PL-05), and emits a deterministic ``security.zone.bootstrap.completed`` event. Zones
    and controls are policy configuration, not compiled ceilings (UMB-015 §4); posture
    evaluation is record-only and authorizes/ratifies/enacts nothing (RG-02 / AR-04),
    stores no secret (SEC-04 / RR-07), and writes nothing to the corpus (DP-03).

    Raises:
        SecurityBootstrapError: on any composition failure (fail-closed).
    """
    try:
        service = build_security_zone_service(events=context.events)

        contracts = {c.name: c for c in default_security_zone_contracts()}
        for ref in SECURITY_ZONE_CONTRACTS:
            if ref.name in context.services:
                continue
            context.services.register(
                ServiceDescriptor(
                    name=ref.name,
                    contract=contracts[ref.name],
                    capabilities=("PC-02", "PC-16"),
                    description=f"Zone & Control Posture Runtime service: {ref.name}.",
                ),
                provider=lambda svc=service: svc,
            )
    except SecurityBootstrapError:
        raise
    except Exception as exc:  # noqa: BLE001 — normalize into a fail-closed error
        raise SecurityBootstrapError(
            "security zone runtime bootstrap failed", detail=str(exc)
        ) from exc

    context.events.publish(
        SECURITY_ZONE_BOOTSTRAP_EVENT,
        source="platform.security.bootstrap",
        subject=context.program_id,
        payload={
            "zone_contracts": [ref.name for ref in SECURITY_ZONE_CONTRACTS],
            "zone_count": len(service.zone_policies()),
            "control_count": len(service.control_policies()),
            "ledger_fingerprint": service.ledger.fingerprint(),
        },
    )
    return service


__all__ = [
    "SECURITY_CLASSIFICATION_BOOTSTRAP_EVENT",
    "bootstrap_security_classification",
    "SECURITY_INTELLIGENCE_BOOTSTRAP_EVENT",
    "bootstrap_security_intelligence",
    "SECURITY_REGISTRY_BOOTSTRAP_EVENT",
    "bootstrap_security_registry",
    "SECURITY_OBSERVABILITY_BOOTSTRAP_EVENT",
    "bootstrap_security_observability",
    "SECURITY_CERTIFICATION_BOOTSTRAP_EVENT",
    "bootstrap_security_certification",
    "SECURITY_ZONE_BOOTSTRAP_EVENT",
    "bootstrap_security_zone",
]
