"""EC2-CAP-ADMIN-001 — Administrative Health (Administration Runtime).

The administration runtime's **health integration**. It reuses the certified
Observability Layer's health model
(:class:`~platform.observability.health.HealthCheck`,
:class:`~platform.observability.contracts.HealthStatus`) — it defines no new health
machinery — and computes a deterministic health probe over the configuration store and
the administrative membership registry. Two critical checks back go-live health (G1)
and operational health under induced fault (OP-C1):

    * ``administration-configuration`` — the configuration substrate is reachable.
    * ``administration-membership-integrity`` — every tenant/workspace-scoped
      administrator names a tenant boundary; an inconsistent (scope↔tenant) membership
      is a fault that drives this check to ``UNHEALTHY``, so alerting/health validate
      under induced fault (OP-C1).

Probing is a pure function of the two registries — no I/O, no wall-clock — so the
health verdict is reproducible (P5).
"""

from __future__ import annotations

from platform.administration.configuration import AdministrativeConfiguration
from platform.administration.membership import (
    AdministrativeMember,
    AdministrativeMembershipRegistry,
)
from platform.observability.contracts import HealthStatus
from platform.observability.health import HealthCheck

#: The check that the configuration substrate is reachable (G1).
CONFIGURATION_CHECK = "administration-configuration"

#: The check that every scoped administrator names a tenant boundary (OP-C1).
INTEGRITY_CHECK = "administration-membership-integrity"


def administration_health_checks() -> tuple[HealthCheck, ...]:
    """The administration runtime health checks (both critical), in stable order."""
    return (
        HealthCheck(
            CONFIGURATION_CHECK,
            critical=True,
            description="Administrative configuration substrate reachable.",
        ),
        HealthCheck(
            INTEGRITY_CHECK,
            critical=True,
            description="Every tenant/workspace administrator names a tenant boundary.",
        ),
    )


class AdministrationHealth:
    """A deterministic health probe over the configuration + membership registries."""

    __slots__ = ("_configuration", "_membership")

    def __init__(
        self,
        configuration: AdministrativeConfiguration,
        membership: AdministrativeMembershipRegistry,
    ) -> None:
        if not isinstance(configuration, AdministrativeConfiguration):
            raise TypeError("a valid AdministrativeConfiguration is required")
        if not isinstance(membership, AdministrativeMembershipRegistry):
            raise TypeError("a valid AdministrativeMembershipRegistry is required")
        self._configuration = configuration
        self._membership = membership

    def inconsistent_members(self) -> tuple[AdministrativeMember, ...]:
        """Scoped administrators missing a tenant boundary (integrity faults)."""
        return tuple(m for m in self._membership.all() if not m.is_consistent)

    def probe(self) -> dict[str, HealthStatus]:
        """Compute deterministic probe results for the administration health checks."""
        integrity_ok = not self.inconsistent_members()
        return {
            CONFIGURATION_CHECK: HealthStatus.HEALTHY,
            INTEGRITY_CHECK: (HealthStatus.HEALTHY if integrity_ok else HealthStatus.UNHEALTHY),
        }

    @property
    def healthy(self) -> bool:
        """True iff every administration health check is HEALTHY."""
        return all(status is HealthStatus.HEALTHY for status in self.probe().values())


__all__ = [
    "CONFIGURATION_CHECK",
    "INTEGRITY_CHECK",
    "administration_health_checks",
    "AdministrationHealth",
]
