"""EC2-TASK-000106 — Blueprint Health (EC2-EPIC-006).

The blueprint runtime's **health integration**. It reuses the certified Observability
Layer's health model (:class:`~platform.observability.health.HealthCheck`,
:class:`~platform.observability.contracts.HealthStatus`) — it defines no new health
machinery — and computes a deterministic health probe over the blueprint registry, the
provenance ledger, and the association registry. Three critical checks back go-live
health (G1) and operational health under induced fault (OP-C1):

    * ``blueprint-registry`` — the registry substrate is reachable.
    * ``blueprint-provenance-integrity`` — **every cataloged blueprint carries
      provenance** (the link-4 admissibility invariant, §5/§10). A cataloged blueprint
      missing provenance (a fault) drives this check to ``UNHEALTHY``, so
      alerting/health validate under induced fault (OP-C1).
    * ``blueprint-association-integrity`` — every association references a registered
      blueprint; an orphaned association drives this check to ``UNHEALTHY``.

Probing is a pure function of the three registries — no I/O, no wall-clock — so the
health verdict is reproducible (P5).
"""

from __future__ import annotations

from platform.blueprints.associations import BlueprintAssociationRegistry
from platform.blueprints.contracts import BlueprintStatus
from platform.blueprints.provenance import ProvenanceLedger
from platform.blueprints.registry import BlueprintRegistry
from platform.observability.contracts import HealthStatus
from platform.observability.health import HealthCheck

#: The check that the blueprint registry substrate is reachable (G1).
REGISTRY_CHECK = "blueprint-registry"

#: The check that every cataloged blueprint carries link-4 provenance (§5/§10, OP-C1).
PROVENANCE_CHECK = "blueprint-provenance-integrity"

#: The check that every association references a registered blueprint (OP-C1).
INTEGRITY_CHECK = "blueprint-association-integrity"

#: The lifecycle states that require provenance to be admissible in the catalog.
_CATALOG_VISIBLE: frozenset[BlueprintStatus] = frozenset(
    {BlueprintStatus.CATALOGUED, BlueprintStatus.SUPERSEDED}
)


def blueprint_health_checks() -> tuple[HealthCheck, ...]:
    """The blueprint runtime health checks (all critical), in stable order."""
    return (
        HealthCheck(
            REGISTRY_CHECK,
            critical=True,
            description="Blueprint registry substrate reachable.",
        ),
        HealthCheck(
            PROVENANCE_CHECK,
            critical=True,
            description="Every cataloged blueprint carries link-4 provenance.",
        ),
        HealthCheck(
            INTEGRITY_CHECK,
            critical=True,
            description="Every association references a registered blueprint.",
        ),
    )


class BlueprintHealth:
    """A deterministic health probe over the blueprint / provenance / association stores."""

    __slots__ = ("_registry", "_provenance", "_associations")

    def __init__(
        self,
        registry: BlueprintRegistry,
        provenance: ProvenanceLedger,
        associations: BlueprintAssociationRegistry,
    ) -> None:
        if not isinstance(registry, BlueprintRegistry):
            raise TypeError("a valid BlueprintRegistry is required")
        if not isinstance(provenance, ProvenanceLedger):
            raise TypeError("a valid ProvenanceLedger is required")
        if not isinstance(associations, BlueprintAssociationRegistry):
            raise TypeError("a valid BlueprintAssociationRegistry is required")
        self._registry = registry
        self._provenance = provenance
        self._associations = associations

    def uncited_catalogued_blueprints(self) -> tuple[str, ...]:
        """Cataloged blueprint ids lacking provenance (link-4 admissibility faults)."""
        return tuple(
            b.blueprint_id
            for b in self._registry.all()
            if b.status in _CATALOG_VISIBLE and not self._provenance.has(b.blueprint_id)
        )

    def orphaned_association_blueprints(self) -> tuple[str, ...]:
        """Blueprint ids that have associations but are not registered (integrity faults)."""
        return tuple(bid for bid in self._associations.blueprint_ids if bid not in self._registry)

    def probe(self) -> dict[str, HealthStatus]:
        """Compute deterministic probe results for the blueprint health checks."""
        provenance_ok = not self.uncited_catalogued_blueprints()
        integrity_ok = not self.orphaned_association_blueprints()
        return {
            REGISTRY_CHECK: HealthStatus.HEALTHY,
            PROVENANCE_CHECK: (HealthStatus.HEALTHY if provenance_ok else HealthStatus.UNHEALTHY),
            INTEGRITY_CHECK: (HealthStatus.HEALTHY if integrity_ok else HealthStatus.UNHEALTHY),
        }

    @property
    def healthy(self) -> bool:
        """True iff every blueprint health check is HEALTHY."""
        return all(status is HealthStatus.HEALTHY for status in self.probe().values())


__all__ = [
    "REGISTRY_CHECK",
    "PROVENANCE_CHECK",
    "INTEGRITY_CHECK",
    "blueprint_health_checks",
    "BlueprintHealth",
]
