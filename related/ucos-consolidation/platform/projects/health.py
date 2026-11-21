"""EC2-TASK-000095 — Project Health (EC2-EPIC-005).

The project runtime's **health integration**. It reuses the certified Observability
Layer's health model (:class:`~platform.observability.health.HealthCheck`,
:class:`~platform.observability.contracts.HealthStatus`) — it defines no new health
machinery — and computes a deterministic health probe over the project registry and
association registry. Two critical checks back go-live health (G1) and operational
health under induced fault (OP-C1):

    * ``project-registry`` — the registry substrate is reachable.
    * ``project-association-integrity`` — every association references a registered
      project; an orphaned association (a fault) drives this check to ``UNHEALTHY``,
      so alerting/health validate under induced fault (OP-C1).

Probing is a pure function of the two registries — no I/O, no wall-clock — so the
health verdict is reproducible (P5).
"""

from __future__ import annotations

from platform.observability.contracts import HealthStatus
from platform.observability.health import HealthCheck
from platform.projects.associations import AssociationRegistry
from platform.projects.registry import ProjectRegistry

#: The check that the project registry substrate is reachable (G1).
REGISTRY_CHECK = "project-registry"

#: The check that every association references a registered project (OP-C1).
INTEGRITY_CHECK = "project-association-integrity"


def project_health_checks() -> tuple[HealthCheck, ...]:
    """The project runtime health checks (both critical), in stable order."""
    return (
        HealthCheck(
            REGISTRY_CHECK,
            critical=True,
            description="Project registry substrate reachable.",
        ),
        HealthCheck(
            INTEGRITY_CHECK,
            critical=True,
            description="Every association references a registered project.",
        ),
    )


class ProjectHealth:
    """A deterministic health probe over the project + association registries."""

    __slots__ = ("_registry", "_associations")

    def __init__(self, registry: ProjectRegistry, associations: AssociationRegistry) -> None:
        if not isinstance(registry, ProjectRegistry):
            raise TypeError("a valid ProjectRegistry is required")
        if not isinstance(associations, AssociationRegistry):
            raise TypeError("a valid AssociationRegistry is required")
        self._registry = registry
        self._associations = associations

    def orphaned_association_projects(self) -> tuple[str, ...]:
        """Project ids that have associations but are not registered (integrity faults)."""
        return tuple(pid for pid in self._associations.project_ids if pid not in self._registry)

    def probe(self) -> dict[str, HealthStatus]:
        """Compute deterministic probe results for the project health checks."""
        integrity_ok = not self.orphaned_association_projects()
        return {
            REGISTRY_CHECK: HealthStatus.HEALTHY,
            INTEGRITY_CHECK: (HealthStatus.HEALTHY if integrity_ok else HealthStatus.UNHEALTHY),
        }

    @property
    def healthy(self) -> bool:
        """True iff every project health check is HEALTHY."""
        return all(status is HealthStatus.HEALTHY for status in self.probe().values())


__all__ = [
    "REGISTRY_CHECK",
    "INTEGRITY_CHECK",
    "project_health_checks",
    "ProjectHealth",
]
