"""EC2-TASK-000131 — Artifact Explorer Health (EC2-EPIC-009).

The artifact-explorer runtime's **health integration**. It reuses the certified
Observability Layer's health model (:class:`~platform.observability.health.HealthCheck`,
:class:`~platform.observability.contracts.HealthStatus`) — it defines no new health
machinery — and computes a deterministic health probe over the consumed generation
request registry, dispatch ledger, and provenance ledger. Three critical checks back
go-live health (G1) and operational health under induced fault (OP-C1):

    * ``artifact-explorer-registry`` — the request registry substrate is reachable.
    * ``artifact-explorer-provenance-integrity`` — **every consumed provenance references
      a registered request** (no dangling provenance reference). A provenance whose
      ``request_ref`` is not registered drives this check to ``UNHEALTHY``.
    * ``artifact-explorer-dispatch-integrity`` — **every consumed dispatch references a
      registered request** (no dangling dispatch reference). An orphaned dispatch drives
      this check to ``UNHEALTHY``.

Probing is a pure function of the three ledgers — no I/O, no wall-clock — so the health
verdict is reproducible (P5). The explorer never mutates the consumed records; the
checks are read-only referential-integrity probes.
"""

from __future__ import annotations

from platform.generation.dispatch import DispatchLedger
from platform.generation.provenance import ProvenanceLedger
from platform.generation.registry import GenerationRequestRegistry
from platform.observability.contracts import HealthStatus
from platform.observability.health import HealthCheck

#: The check that the request registry substrate is reachable (G1).
REGISTRY_CHECK = "artifact-explorer-registry"

#: The check that every consumed provenance references a registered request (OP-C1).
PROVENANCE_CHECK = "artifact-explorer-provenance-integrity"

#: The check that every consumed dispatch references a registered request (OP-C1).
DISPATCH_CHECK = "artifact-explorer-dispatch-integrity"


def artifact_explorer_health_checks() -> tuple[HealthCheck, ...]:
    """The artifact-explorer runtime health checks (all critical), in stable order."""
    return (
        HealthCheck(
            REGISTRY_CHECK,
            critical=True,
            description="Artifact-explorer request registry substrate reachable.",
        ),
        HealthCheck(
            PROVENANCE_CHECK,
            critical=True,
            description="Every consumed provenance references a registered request.",
        ),
        HealthCheck(
            DISPATCH_CHECK,
            critical=True,
            description="Every consumed dispatch references a registered request.",
        ),
    )


class ExplorerHealth:
    """A deterministic read-only integrity probe over the consumed EC2-EPIC-007 ledgers."""

    __slots__ = ("_registry", "_dispatch", "_provenance")

    def __init__(
        self,
        registry: GenerationRequestRegistry,
        dispatch: DispatchLedger,
        provenance: ProvenanceLedger,
    ) -> None:
        if not isinstance(registry, GenerationRequestRegistry):
            raise TypeError("a valid GenerationRequestRegistry is required")
        if not isinstance(dispatch, DispatchLedger):
            raise TypeError("a valid DispatchLedger is required")
        if not isinstance(provenance, ProvenanceLedger):
            raise TypeError("a valid ProvenanceLedger is required")
        self._registry = registry
        self._dispatch = dispatch
        self._provenance = provenance

    def orphaned_provenance(self) -> tuple[str, ...]:
        """Request ids that have provenance but are not registered (integrity faults)."""
        return tuple(ref for ref in self._provenance.request_refs if ref not in self._registry)

    def orphaned_dispatches(self) -> tuple[str, ...]:
        """Request ids that have a dispatch but are not registered (integrity faults)."""
        return tuple(ref for ref in self._dispatch.request_refs if ref not in self._registry)

    def probe(self) -> dict[str, HealthStatus]:
        """Compute deterministic probe results for the explorer health checks."""
        provenance_ok = not self.orphaned_provenance()
        dispatch_ok = not self.orphaned_dispatches()
        return {
            REGISTRY_CHECK: HealthStatus.HEALTHY,
            PROVENANCE_CHECK: (HealthStatus.HEALTHY if provenance_ok else HealthStatus.UNHEALTHY),
            DISPATCH_CHECK: (HealthStatus.HEALTHY if dispatch_ok else HealthStatus.UNHEALTHY),
        }

    @property
    def healthy(self) -> bool:
        """True iff every explorer health check is HEALTHY."""
        return all(status is HealthStatus.HEALTHY for status in self.probe().values())


__all__ = [
    "REGISTRY_CHECK",
    "PROVENANCE_CHECK",
    "DISPATCH_CHECK",
    "artifact_explorer_health_checks",
    "ExplorerHealth",
]
