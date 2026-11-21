"""ZG-P-02 — Coverage service (Universe→Code Coverage Instrument).

The single governed composition point for the coverage instrument. It ties the
:class:`~platform.coverage.engine.CoverageEngine`, its append-only
:class:`~platform.coverage.registry.CoverageRegistry`, the reused Observability
:class:`~platform.observability.health.HealthRegistry` (seeded with the nine coverage
checks), and the certification API into one deterministic, fail-closed instrument.

It is strictly **additive**: it creates no new authority, no alternate registry, and no
alternate governance/traceability system. It integrates with the existing governance
instruments (GOV-002/005/006, TRACK-001, STATUS-001, MIP-ZG-001) **by reference** — it
reads and cites them, replaces none. Every output is a pure function of repository
evidence, so :meth:`evidence` fingerprints byte-identically across processes (IMP-007 §5).
"""

from __future__ import annotations

from dataclasses import dataclass
from platform.coverage import certification as _cert
from platform.coverage.certification import CoverageCertification
from platform.coverage.contracts import COVERAGE_CONTRACTS, GOVERNANCE_AUTHORITIES
from platform.coverage.engine import (
    CoverageEngine,
    CoverageReconciliation,
    CoverageVerification,
)
from platform.coverage.errors import CoverageError
from platform.coverage.evidence import EvidenceSource
from platform.coverage.graph import CoverageGraph
from platform.coverage.health import CoverageHealth, coverage_health_checks
from platform.coverage.registry import CoverageRegistry
from platform.foundation.contracts import content_hash
from platform.observability.contracts import HealthStatus
from platform.observability.health import HealthRegistry
from typing import Any


@dataclass(frozen=True, slots=True)
class CoverageEvidence:
    """A deterministic, content-addressed snapshot of coverage instrument state."""

    graph_fingerprint: str
    registry_fingerprint: str
    node_count: int
    edge_count: int
    universe_percentage: float
    gap_count: int
    orphan_count: int
    health_status: str
    certification_status: str
    evidence_id: str = ""

    @classmethod
    def create(
        cls,
        *,
        graph_fingerprint: str,
        registry_fingerprint: str,
        node_count: int,
        edge_count: int,
        universe_percentage: float,
        gap_count: int,
        orphan_count: int,
        health_status: str,
        certification_status: str,
    ) -> CoverageEvidence:
        core = {
            "graph_fingerprint": graph_fingerprint,
            "registry_fingerprint": registry_fingerprint,
            "node_count": node_count,
            "edge_count": edge_count,
            "universe_percentage": universe_percentage,
            "gap_count": gap_count,
            "orphan_count": orphan_count,
            "health_status": health_status,
            "certification_status": certification_status,
        }
        return cls(
            graph_fingerprint=graph_fingerprint,
            registry_fingerprint=registry_fingerprint,
            node_count=node_count,
            edge_count=edge_count,
            universe_percentage=universe_percentage,
            gap_count=gap_count,
            orphan_count=orphan_count,
            health_status=health_status,
            certification_status=certification_status,
            evidence_id=f"UCOS-COVE-EV-{content_hash(core)[:16]}",
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "evidence_id": self.evidence_id,
            "graph_fingerprint": self.graph_fingerprint,
            "registry_fingerprint": self.registry_fingerprint,
            "node_count": self.node_count,
            "edge_count": self.edge_count,
            "universe_percentage": self.universe_percentage,
            "gap_count": self.gap_count,
            "orphan_count": self.orphan_count,
            "health_status": self.health_status,
            "certification_status": self.certification_status,
        }

    def fingerprint(self) -> str:
        return content_hash(self.to_dict())


class CoverageService:
    """The governed composition point for the Universe→Code Coverage Instrument."""

    __slots__ = ("_engine", "_health_registry")

    def __init__(
        self, engine: CoverageEngine, *, health_registry: HealthRegistry | None = None
    ) -> None:
        if not isinstance(engine, CoverageEngine):
            raise CoverageError("CoverageService requires a CoverageEngine")
        if health_registry is not None and not isinstance(health_registry, HealthRegistry):
            raise CoverageError("health_registry must be a HealthRegistry when provided")
        self._engine = engine
        if health_registry is None:
            health_registry = HealthRegistry()
            for check in coverage_health_checks():
                health_registry.register(check)
        self._health_registry = health_registry

    @property
    def engine(self) -> CoverageEngine:
        return self._engine

    @property
    def registry(self) -> CoverageRegistry:
        return self._engine.registry

    # -- coverage operations (mirror the engine surface) ------------------------

    def compute(self) -> CoverageGraph:
        return self._engine.compute()

    def verify(self) -> CoverageVerification:
        return self._engine.verify()

    def reconcile(self) -> CoverageReconciliation:
        return self._engine.reconcile()

    def fingerprint(self) -> str:
        return self._engine.fingerprint()

    def report(self) -> dict[str, Any]:
        return self._engine.report()

    # -- health -----------------------------------------------------------------

    def _health(self) -> CoverageHealth:
        graph = self._engine.compute()
        return CoverageHealth(graph, self._engine.registry)

    def health_report(self, *, strict: bool = False) -> dict[str, Any]:
        """The live coverage health endpoint (reuses the Observability model)."""
        return self._health_registry.endpoint(self._health().probe(strict=strict))

    def health_status(self, *, strict: bool = False) -> HealthStatus:
        return self._health_registry.report(self._health().probe(strict=strict)).status

    # -- certification ----------------------------------------------------------

    def certify(self, *, strict: bool = True) -> CoverageCertification:
        """Produce the fail-closed coverage certification (G4 evidence)."""
        return _cert.assess(self._engine, strict=strict)

    # -- evidence ---------------------------------------------------------------

    def evidence(self, *, strict: bool = False) -> CoverageEvidence:
        """Produce deterministic coverage evidence over the current repository state."""
        graph = self._engine.compute()
        health = CoverageHealth(graph, self._engine.registry)
        health_report = self._health_registry.report(health.probe(strict=strict))
        cert = self.certify(strict=strict)
        return CoverageEvidence.create(
            graph_fingerprint=graph.fingerprint(),
            registry_fingerprint=self._engine.registry.fingerprint(),
            node_count=len(graph),
            edge_count=len(graph.edges()),
            universe_percentage=cert.coverage_percentage,
            gap_count=len(graph.gaps()),
            orphan_count=len(graph.orphans()),
            health_status=health_report.status.value,
            certification_status=cert.coverage_certification_status,
        )

    # -- governance integration (by reference) ----------------------------------

    def to_dict(self) -> dict[str, Any]:
        return {
            "instrument": "UCOS-COVERAGE-INSTRUMENT",
            "contracts": [ref.to_dict() for ref in COVERAGE_CONTRACTS],
            "governance_authorities": list(GOVERNANCE_AUTHORITIES),
            "health_checks": list(self._health_registry.names),
            "registry_fingerprint": self._engine.registry.fingerprint(),
        }


def build_coverage_service(source: EvidenceSource) -> CoverageService:
    """Default composition of the coverage instrument over an evidence ``source``."""
    if not isinstance(source, EvidenceSource):
        raise CoverageError("build_coverage_service requires an EvidenceSource")
    return CoverageService(CoverageEngine(source))


__all__ = ["CoverageEvidence", "CoverageService", "build_coverage_service"]
