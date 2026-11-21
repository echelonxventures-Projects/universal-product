"""UCOS-EPIC-004 — Measurement service (UCOS-UMA-001).

The single governed composition point for the Universal Measurement Engine. It ties the
four measurement engines (Enumeration, Metrics, Coverage, Gap), the append-only
:class:`~platform.measurement.registry.MeasurementRegistry`, the reused Observability
:class:`~platform.observability.health.HealthRegistry` (seeded with the five measurement
checks), and deterministic evidence generation into one fail-closed instrument — the
operational instantiation of **UCOS-UMA-001**.

It is strictly **additive** and, by construction, **creates no Truth**: it reads a
read-only :class:`~platform.measurement.source.TruthSource`, measures it, and records the
measurements in its own disjoint (``UCOS-UMA*``) namespace. It integrates with the
governance instruments (GOV-002/005, TRACK-001, STATUS-001, DP-03) **by reference** — it
reads and cites them, authors none. Every output is a pure function of Registry Truth, so
evidence fingerprints byte-identically across processes (IMP-007 §5).
"""

from __future__ import annotations

from dataclasses import dataclass
from platform.foundation.contracts import content_hash
from platform.measurement.contracts import (
    GOVERNANCE_AUTHORITIES,
    MEASUREMENT_CONTRACTS,
    UMA_ID,
    Measurement,
)
from platform.measurement.coverage import CoverageEngine, CoverageMeasurement
from platform.measurement.enumeration import Enumeration, EnumerationEngine
from platform.measurement.errors import MeasurementError
from platform.measurement.evidence import MeasurementEvidence
from platform.measurement.gaps import GapEngine, GapReport
from platform.measurement.health import MeasurementHealth, measurement_health_checks
from platform.measurement.metrics import MetricsEngine, MetricSet
from platform.measurement.registry import MeasurementRegistry
from platform.measurement.source import TruthSnapshot, TruthSource
from platform.observability.contracts import HealthStatus
from platform.observability.health import HealthRegistry
from typing import Any


@dataclass(frozen=True, slots=True)
class MeasurementRun:
    """An immutable, content-addressed result of one complete measurement pass."""

    enumeration: Enumeration
    metrics: MetricSet
    coverage: CoverageMeasurement
    gaps: GapReport
    truth_fingerprint: str
    run_id: str = ""

    @classmethod
    def create(
        cls,
        *,
        enumeration: Enumeration,
        metrics: MetricSet,
        coverage: CoverageMeasurement,
        gaps: GapReport,
        truth_fingerprint: str,
    ) -> MeasurementRun:
        core = {
            "enumeration": enumeration.fingerprint(),
            "metrics": metrics.fingerprint(),
            "coverage": coverage.fingerprint(),
            "gaps": gaps.fingerprint(),
            "truth_fingerprint": truth_fingerprint,
        }
        return cls(
            enumeration=enumeration,
            metrics=metrics,
            coverage=coverage,
            gaps=gaps,
            truth_fingerprint=truth_fingerprint,
            run_id=f"UCOS-UMAR-{content_hash(core)[:16]}",
        )

    def measurements(self) -> tuple[Measurement, ...]:
        """The four kind-level measurements produced by this run (stable order)."""
        return (
            self.enumeration.as_measurement(),
            self.metrics.as_measurement(),
            self.coverage.as_measurement(),
            self.gaps.as_measurement(),
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "run_id": self.run_id,
            "truth_fingerprint": self.truth_fingerprint,
            "enumeration": self.enumeration.to_dict(),
            "metrics": self.metrics.to_dict(),
            "coverage": self.coverage.to_dict(),
            "gaps": self.gaps.to_dict(),
        }

    def fingerprint(self) -> str:
        return content_hash(self.to_dict())


class MeasurementService:
    """The governed composition point for the Universal Measurement Engine (UCOS-UMA-001)."""

    __slots__ = ("_source", "_registry", "_health_registry")

    def __init__(
        self,
        source: TruthSource,
        *,
        registry: MeasurementRegistry | None = None,
        health_registry: HealthRegistry | None = None,
    ) -> None:
        if not isinstance(source, TruthSource):
            raise MeasurementError("MeasurementService requires a TruthSource")
        if registry is not None and not isinstance(registry, MeasurementRegistry):
            raise MeasurementError("registry must be a MeasurementRegistry when provided")
        if health_registry is not None and not isinstance(health_registry, HealthRegistry):
            raise MeasurementError("health_registry must be a HealthRegistry when provided")
        self._source = source
        self._registry = registry if registry is not None else MeasurementRegistry()
        if health_registry is None:
            health_registry = HealthRegistry()
            for check in measurement_health_checks():
                health_registry.register(check)
        self._health_registry = health_registry

    @property
    def uma_id(self) -> str:
        return UMA_ID

    @property
    def registry(self) -> MeasurementRegistry:
        return self._registry

    # -- individual engine surfaces --------------------------------------------

    def _snapshot(self) -> TruthSnapshot:
        snapshot = self._source.snapshot()
        if not isinstance(snapshot, TruthSnapshot):  # pragma: no cover - defensive
            raise MeasurementError("TruthSource returned a non-TruthSnapshot")
        return snapshot

    def enumerate(self) -> Enumeration:
        return EnumerationEngine(self._snapshot()).enumerate()

    def metrics(self) -> MetricSet:
        return MetricsEngine(self._snapshot()).measure()

    def coverage(self) -> CoverageMeasurement:
        return CoverageEngine(self._snapshot()).measure()

    def gaps(self) -> GapReport:
        return GapEngine(self._snapshot()).detect()

    # -- full run (records into the append-only registry) -----------------------

    def measure(self) -> MeasurementRun:
        """Run all four engines over one Truth snapshot and record the measurements."""
        snapshot = self._snapshot()
        run = MeasurementRun.create(
            enumeration=EnumerationEngine(snapshot).enumerate(),
            metrics=MetricsEngine(snapshot).measure(),
            coverage=CoverageEngine(snapshot).measure(),
            gaps=GapEngine(snapshot).detect(),
            truth_fingerprint=snapshot.fingerprint(),
        )
        self._registry.record_all(run.measurements())
        return run

    def fingerprint(self) -> str:
        """The deterministic fingerprint of a fresh measurement run over current Truth."""
        snapshot = self._snapshot()
        run = MeasurementRun.create(
            enumeration=EnumerationEngine(snapshot).enumerate(),
            metrics=MetricsEngine(snapshot).measure(),
            coverage=CoverageEngine(snapshot).measure(),
            gaps=GapEngine(snapshot).detect(),
            truth_fingerprint=snapshot.fingerprint(),
        )
        return run.fingerprint()

    def _is_deterministic(self) -> bool:
        """True iff two independent recomputes over Truth fingerprint identically."""
        return self.fingerprint() == self.fingerprint()

    def report(self) -> dict[str, Any]:
        """The full, deterministic measurement report over the current Truth."""
        run = self.measure()
        return {
            "uma_id": UMA_ID,
            "run_id": run.run_id,
            "truth_fingerprint": run.truth_fingerprint,
            "counts": run.enumeration.counts,
            "metric_count": len(run.metrics),
            "traceability": {
                "overall_percentage": run.coverage.overall_percentage,
                "fully_traced_count": run.coverage.fully_traced_count,
                "fully_traced_percentage": run.coverage.fully_traced_percentage,
            },
            "gaps": {
                "total": run.gaps.total,
                "structural": run.gaps.structural_count,
                "completeness": run.gaps.completeness_count,
                "by_type": dict(run.gaps.by_type),
            },
            "registry_fingerprint": self._registry.fingerprint(),
        }

    # -- health -----------------------------------------------------------------

    def _health(self) -> MeasurementHealth:
        run = self.measure()
        return MeasurementHealth(
            gap_report=run.gaps,
            coverage=run.coverage,
            registry=self._registry,
            deterministic=self._is_deterministic(),
        )

    def health_report(self, *, strict: bool = False) -> dict[str, Any]:
        """The live measurement health endpoint (reuses the Observability model)."""
        return self._health_registry.endpoint(self._health().probe(strict=strict))

    def health_status(self, *, strict: bool = False) -> HealthStatus:
        return self._health_registry.report(self._health().probe(strict=strict)).status

    # -- evidence ---------------------------------------------------------------

    def evidence(self, *, strict: bool = False) -> MeasurementEvidence:
        """Produce deterministic measurement evidence over the current Truth."""
        snapshot = self._snapshot()
        enumeration = EnumerationEngine(snapshot).enumerate()
        metrics = MetricsEngine(snapshot).measure()
        coverage = CoverageEngine(snapshot).measure()
        gaps = GapEngine(snapshot).detect()
        run = MeasurementRun.create(
            enumeration=enumeration,
            metrics=metrics,
            coverage=coverage,
            gaps=gaps,
            truth_fingerprint=snapshot.fingerprint(),
        )
        self._registry.record_all(run.measurements())
        health = MeasurementHealth(
            gap_report=gaps,
            coverage=coverage,
            registry=self._registry,
            deterministic=self._is_deterministic(),
        )
        health_report = self._health_registry.report(health.probe(strict=strict))
        return MeasurementEvidence.create(
            truth_fingerprint=snapshot.fingerprint(),
            enumeration_fingerprint=enumeration.fingerprint(),
            metrics_fingerprint=metrics.fingerprint(),
            coverage_fingerprint=coverage.fingerprint(),
            gaps_fingerprint=gaps.fingerprint(),
            registry_fingerprint=self._registry.fingerprint(),
            artifact_count=snapshot.artifact_count,
            relationship_count=snapshot.relationship_count,
            volume_count=snapshot.volume_count,
            traceability_percentage=coverage.overall_percentage,
            fully_traced_count=coverage.fully_traced_count,
            gap_count=gaps.total,
            structural_gap_count=gaps.structural_count,
            health_status=health_report.status.value,
        )

    # -- governance integration (by reference) ----------------------------------

    def to_dict(self) -> dict[str, Any]:
        return {
            "instrument": UMA_ID,
            "contracts": [ref.to_dict() for ref in MEASUREMENT_CONTRACTS],
            "governance_authorities": list(GOVERNANCE_AUTHORITIES),
            "health_checks": list(self._health_registry.names),
            "registry_fingerprint": self._registry.fingerprint(),
        }


def build_measurement_service(source: TruthSource) -> MeasurementService:
    """Default composition of the Universal Measurement Engine over a Truth ``source``."""
    if not isinstance(source, TruthSource):
        raise MeasurementError("build_measurement_service requires a TruthSource")
    return MeasurementService(source)


__all__ = ["MeasurementRun", "MeasurementService", "build_measurement_service"]
