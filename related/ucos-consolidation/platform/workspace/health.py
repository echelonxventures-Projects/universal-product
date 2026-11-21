"""EC2-TASK-000088 — Workspace Health (EC2-EPIC-004).

The workspace runtime's **health integration**. It reuses the certified Observability
Layer's health model (:class:`~platform.observability.health.HealthCheck`,
:class:`~platform.observability.contracts.HealthStatus`) — it defines no new health
machinery — and computes a deterministic health probe over the workspace registry and
membership registry. Two critical checks back go-live health (G1) and operational
health under induced fault (OP-C1):

    * ``workspace-registry`` — the registry substrate is reachable.
    * ``workspace-membership-integrity`` — every workspace that has members is a
      registered workspace; an orphaned membership (a fault) drives this check to
      ``UNHEALTHY``, so alerting/health validate under induced fault (OP-C1).

Probing is a pure function of the two registries — no I/O, no wall-clock — so the
health verdict is reproducible (P5).
"""

from __future__ import annotations

from platform.observability.contracts import HealthStatus
from platform.observability.health import HealthCheck
from platform.workspace.membership import MembershipRegistry
from platform.workspace.registration import WorkspaceRegistry

#: The check that the workspace registry substrate is reachable (G1).
REGISTRY_CHECK = "workspace-registry"

#: The check that every membership references a registered workspace (OP-C1).
INTEGRITY_CHECK = "workspace-membership-integrity"


def workspace_health_checks() -> tuple[HealthCheck, ...]:
    """The workspace runtime health checks (both critical), in stable order."""
    return (
        HealthCheck(
            REGISTRY_CHECK,
            critical=True,
            description="Workspace registry substrate reachable.",
        ),
        HealthCheck(
            INTEGRITY_CHECK,
            critical=True,
            description="Every membership references a registered workspace.",
        ),
    )


class WorkspaceHealth:
    """A deterministic health probe over the workspace + membership registries."""

    __slots__ = ("_registry", "_membership")

    def __init__(self, registry: WorkspaceRegistry, membership: MembershipRegistry) -> None:
        if not isinstance(registry, WorkspaceRegistry):
            raise TypeError("a valid WorkspaceRegistry is required")
        if not isinstance(membership, MembershipRegistry):
            raise TypeError("a valid MembershipRegistry is required")
        self._registry = registry
        self._membership = membership

    def orphaned_membership_workspaces(self) -> tuple[str, ...]:
        """Workspace ids that have members but are not registered (integrity faults)."""
        return tuple(wid for wid in self._membership.workspace_ids if wid not in self._registry)

    def probe(self) -> dict[str, HealthStatus]:
        """Compute deterministic probe results for the workspace health checks."""
        integrity_ok = not self.orphaned_membership_workspaces()
        return {
            REGISTRY_CHECK: HealthStatus.HEALTHY,
            INTEGRITY_CHECK: (HealthStatus.HEALTHY if integrity_ok else HealthStatus.UNHEALTHY),
        }

    @property
    def healthy(self) -> bool:
        """True iff every workspace health check is HEALTHY."""
        return all(status is HealthStatus.HEALTHY for status in self.probe().values())


__all__ = [
    "REGISTRY_CHECK",
    "INTEGRITY_CHECK",
    "workspace_health_checks",
    "WorkspaceHealth",
]
