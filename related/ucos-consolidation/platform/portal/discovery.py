"""EC2-TASK-000078 — Portal Platform-Services Access (EC2-EPIC-003).

Two portal capabilities that expose the rest of the platform through the shell:

    * :class:`ServiceDirectory` — the **service discovery + capability access model**.
      A pure, deterministic read model over the Platform Foundation
      :class:`~platform.foundation.services.ServiceRegistry` and
      :class:`~platform.foundation.capabilities.CapabilityCatalog` (EC2-EPIC-001): it
      lists the services published by every composed layer (identity, observability,
      portal, …), resolves which services provide a given platform capability
      (PC-01…PC-18), and never mutates or starts anything.

    * :class:`ObservabilityView` — the **observability integration** (health, runtime,
      and monitoring visibility). It surfaces the EC2-EPIC-013 Observability Layer's
      live health endpoint (G1), governed-action runtime evidence, and monitoring
      snapshot into the portal — but only to callers the Identity Layer authorizes
      with READ on the ``monitoring-observability`` capability group (§3.2 row 12).
      Fail-closed: an unauthorized caller, or a portal with no bound observability
      layer, is denied.
"""

from __future__ import annotations

from collections.abc import Mapping
from platform.foundation.capabilities import CapabilityCatalog
from platform.foundation.contracts import content_hash
from platform.foundation.identity import Permission
from platform.foundation.services import ServiceDescriptor, ServiceRegistry
from platform.identity.contracts import CapabilityGroup
from platform.observability.contracts import HealthStatus
from platform.observability.service import ObservabilityService
from platform.portal.access import PortalAccessGateway
from platform.portal.errors import ServiceDiscoveryError
from typing import Any

#: The capability group a caller must hold READ on to see observability views.
OBSERVABILITY_GROUP = CapabilityGroup.MONITORING_OBSERVABILITY


class ServiceDirectory:
    """A deterministic, read-only discovery view over platform services + capabilities."""

    __slots__ = ("_services", "_capabilities")

    def __init__(self, services: ServiceRegistry, capabilities: CapabilityCatalog) -> None:
        if not isinstance(services, ServiceRegistry):
            raise ServiceDiscoveryError("a valid ServiceRegistry is required")
        if not isinstance(capabilities, CapabilityCatalog):
            raise ServiceDiscoveryError("a valid CapabilityCatalog is required")
        self._services = services
        self._capabilities = capabilities

    @property
    def service_names(self) -> tuple[str, ...]:
        """Every discoverable service name in deterministic order."""
        return self._services.names

    def services(self) -> tuple[ServiceDescriptor, ...]:
        """Every discoverable service descriptor in deterministic order."""
        return self._services.descriptors()

    def describe(self, name: str) -> ServiceDescriptor:
        """Resolve a single service descriptor (fail-closed on unknown)."""
        if name not in self._services:
            raise ServiceDiscoveryError("no such service", name=name)
        return self._services.descriptor(name)

    def services_for_capability(self, capability_id: str) -> tuple[ServiceDescriptor, ...]:
        """The services that provide platform capability ``capability_id`` (PC-*).

        Deterministic (service-name order). Validates the capability exists so an
        unknown capability id fails closed rather than silently returning nothing.
        """
        if capability_id not in self._capabilities:
            raise ServiceDiscoveryError("no such capability", capability_id=capability_id)
        return tuple(
            descriptor
            for descriptor in self._services.descriptors()
            if capability_id in descriptor.capabilities
        )

    def capability_ids(self) -> tuple[str, ...]:
        """Every platform/engine capability id in deterministic order."""
        return self._capabilities.ids

    def to_dict(self) -> dict[str, Any]:
        return {
            "service_count": len(self._services),
            "services": [d.to_dict() for d in self.services()],
            "capabilities": self._capabilities.to_dict(),
        }

    def fingerprint(self) -> str:
        return content_hash(self.to_dict())


class ObservabilityView:
    """Authorization-gated portal view over the Observability Layer (L8)."""

    __slots__ = ("_gateway", "_observability")

    def __init__(
        self,
        gateway: PortalAccessGateway,
        observability: ObservabilityService | None = None,
    ) -> None:
        if not isinstance(gateway, PortalAccessGateway):
            raise ServiceDiscoveryError("a valid PortalAccessGateway is required")
        if observability is not None and not isinstance(observability, ObservabilityService):
            raise ServiceDiscoveryError(
                "observability must be an ObservabilityService when provided"
            )
        self._gateway = gateway
        self._observability = observability

    @property
    def bound(self) -> bool:
        """True iff an observability layer is bound to this view."""
        return self._observability is not None

    def _require(self, session_id: str, *, now: int, tenant: str | None) -> ObservabilityService:
        """Authorize the caller and return the bound service (fail-closed)."""
        if self._observability is None:
            raise ServiceDiscoveryError("no observability layer bound to the portal")
        decision = self._gateway.authorize(
            session_id, OBSERVABILITY_GROUP, Permission.READ, now=now, tenant=tenant
        )
        if not decision.permitted:
            raise ServiceDiscoveryError(
                "observability view denied",
                session_id=session_id,
                reason=decision.reason,
            )
        return self._observability

    def health(
        self,
        session_id: str,
        results: Mapping[str, HealthStatus],
        *,
        now: int,
        tenant: str | None = None,
    ) -> dict[str, Any]:
        """The live platform health endpoint (G1), gated on observability READ."""
        service = self._require(session_id, now=now, tenant=tenant)
        return service.health_endpoint(results)

    def runtime(self, session_id: str, *, now: int, tenant: str | None = None) -> dict[str, Any]:
        """Runtime visibility: governed-action count + observability evidence."""
        service = self._require(session_id, now=now, tenant=tenant)
        evidence = service.evidence()
        return {
            "governed_action_count": service.governed_action_count,
            "observed_fraction": service.observed_fraction(),
            "audit_chain_intact": evidence.audit_chain_intact,
            "evidence_id": evidence.evidence_id,
        }

    def monitoring(self, session_id: str, *, now: int, tenant: str | None = None) -> dict[str, Any]:
        """Monitoring visibility: the deterministic metric snapshot."""
        service = self._require(session_id, now=now, tenant=tenant)
        return service.metrics.snapshot()


__all__ = ["OBSERVABILITY_GROUP", "ServiceDirectory", "ObservabilityView"]
