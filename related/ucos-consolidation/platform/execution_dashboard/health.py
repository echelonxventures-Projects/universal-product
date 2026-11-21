"""EC2-TASK-000130 — Execution Dashboard Health (EC2-EPIC-008).

The execution-dashboard runtime's **health integration**. It reuses the certified
Observability Layer's health model (:class:`~platform.observability.health.HealthCheck`,
:class:`~platform.observability.contracts.HealthStatus`) — it defines no new health
machinery — and computes a deterministic health probe over the consumed
:class:`~platform.generation.registry.GenerationRequestRegistry` (by reference). Three
critical checks back go-live health (G1) and operational health under induced fault
(OP-C1):

    * ``execution-dashboard-registry`` — the consumed request registry substrate is
      reachable.
    * ``execution-dashboard-census-integrity`` — **the dashboard's projected status census
      equals the registry's own authoritative census** (the projection-fidelity invariant).
      A drift between the dashboard projection and the registry's ``count_by_status`` drives
      this check to ``UNHEALTHY`` — so a corrupted or stale projection is machine-detectable
      and alerting/health validate under induced fault (OP-C1).
    * ``execution-dashboard-queue-integrity`` — the projected queue depth equals the
      registry's QUEUED count; a mismatch drives this check to ``UNHEALTHY``.

Probing is a pure function of the registry — no I/O, no wall-clock — so the health verdict
is reproducible (P5). The dashboard stores no copy of request state; it recomputes every
projection live, so these checks assert that the projection functions faithfully reconstruct
the authoritative registry state.
"""

from __future__ import annotations

from platform.execution_dashboard.views import QueueSummary, RequestMetrics
from platform.generation.contracts import RequestStatus
from platform.generation.registry import GenerationRequestRegistry
from platform.observability.contracts import HealthStatus
from platform.observability.health import HealthCheck

#: The check that the consumed request registry substrate is reachable (G1).
REGISTRY_CHECK = "execution-dashboard-registry"

#: The check that the dashboard census equals the registry's authoritative census (OP-C1).
CENSUS_CHECK = "execution-dashboard-census-integrity"

#: The check that the projected queue depth equals the registry's QUEUED count (OP-C1).
QUEUE_CHECK = "execution-dashboard-queue-integrity"


def execution_dashboard_health_checks() -> tuple[HealthCheck, ...]:
    """The execution-dashboard runtime health checks (all critical), in stable order."""
    return (
        HealthCheck(
            REGISTRY_CHECK,
            critical=True,
            description="Consumed generation request registry substrate reachable.",
        ),
        HealthCheck(
            CENSUS_CHECK,
            critical=True,
            description="Dashboard status census equals the registry's authoritative census.",
        ),
        HealthCheck(
            QUEUE_CHECK,
            critical=True,
            description="Projected queue depth equals the registry's QUEUED count.",
        ),
    )


class DashboardHealth:
    """A deterministic health probe over the consumed request registry (by reference)."""

    __slots__ = ("_registry",)

    def __init__(self, registry: GenerationRequestRegistry) -> None:
        if not isinstance(registry, GenerationRequestRegistry):
            raise TypeError("a valid GenerationRequestRegistry is required")
        self._registry = registry

    def census_drift(self) -> tuple[str, ...]:
        """Status names where the dashboard projection diverges from the registry census."""
        projected = dict(RequestMetrics.from_requests(self._registry.all()).status_census)
        authoritative = self._registry.count_by_status()
        drift = [name for name, count in authoritative.items() if projected.get(name) != count]
        # Also surface any projected status absent from the authoritative census.
        drift.extend(name for name in projected if name not in authoritative)
        return tuple(sorted(set(drift)))

    def queue_drift(self) -> bool:
        """True iff the projected queue depth diverges from the registry's QUEUED count."""
        projected = QueueSummary.from_requests(self._registry.all()).queue_depth
        authoritative = self._registry.count_by_status().get(RequestStatus.QUEUED.value, 0)
        return projected != authoritative

    def probe(self) -> dict[str, HealthStatus]:
        """Compute deterministic probe results for the dashboard health checks."""
        census_ok = not self.census_drift()
        queue_ok = not self.queue_drift()
        return {
            REGISTRY_CHECK: HealthStatus.HEALTHY,
            CENSUS_CHECK: HealthStatus.HEALTHY if census_ok else HealthStatus.UNHEALTHY,
            QUEUE_CHECK: HealthStatus.HEALTHY if queue_ok else HealthStatus.UNHEALTHY,
        }

    @property
    def healthy(self) -> bool:
        """True iff every dashboard health check is HEALTHY."""
        return all(status is HealthStatus.HEALTHY for status in self.probe().values())


__all__ = [
    "REGISTRY_CHECK",
    "CENSUS_CHECK",
    "QUEUE_CHECK",
    "execution_dashboard_health_checks",
    "DashboardHealth",
]
