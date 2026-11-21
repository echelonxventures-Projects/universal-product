"""UCOS-EPIC-004 — Measurement health (UCOS-UMA-001).

Reuses the certified Observability health model (``HealthCheck``, ``HealthStatus``) — it
defines no new health machinery — and computes a deterministic probe over a measurement
run (the four engine results + the measurement registry). Five critical checks back the
engine's operational health:

    Integrity (always fail-closed → UNHEALTHY on any violation):
        * ``measurement-determinism``          — two independent recomputes must agree.
        * ``measurement-registry-consistency`` — a registry rebuilt from the recorded
          measurements must fingerprint identically (append-only, tamper-evident).

    Truth quality (surfaced from Truth; UNHEALTHY under ``strict`` policy, else DEGRADED):
        * ``structural-truth-gaps`` — referential-integrity defects present in Truth.
        * ``traceability-gaps``     — artifacts with an incomplete traceability chain.
        * ``ownership-gaps``        — artifacts with no assigned owner.

Probing is a pure function of the supplied results — no I/O, no wall-clock — so the
verdict is reproducible (IMP-007 §5). The engine never repairs Truth; it only reports.
"""

from __future__ import annotations

from platform.measurement.coverage import CoverageMeasurement
from platform.measurement.gaps import (
    INCOMPLETE_TRACEABILITY,
    UNASSIGNED_OWNER,
    GapReport,
)
from platform.measurement.registry import MeasurementRegistry
from platform.observability.contracts import HealthStatus
from platform.observability.health import HealthCheck

# Integrity checks (fail-closed → UNHEALTHY on violation).
DETERMINISM_CHECK = "measurement-determinism"
REGISTRY_CONSISTENCY_CHECK = "measurement-registry-consistency"

# Truth-quality checks (UNHEALTHY under strict policy, DEGRADED otherwise).
STRUCTURAL_GAPS_CHECK = "structural-truth-gaps"
TRACEABILITY_GAPS_CHECK = "traceability-gaps"
OWNERSHIP_GAPS_CHECK = "ownership-gaps"

_INTEGRITY_CHECKS = (DETERMINISM_CHECK, REGISTRY_CONSISTENCY_CHECK)
_QUALITY_CHECKS = (STRUCTURAL_GAPS_CHECK, TRACEABILITY_GAPS_CHECK, OWNERSHIP_GAPS_CHECK)


def measurement_health_checks() -> tuple[HealthCheck, ...]:
    """The five measurement health checks (all critical), in stable order."""
    d = "critical measurement check"
    return (
        HealthCheck(DETERMINISM_CHECK, critical=True, description=d),
        HealthCheck(REGISTRY_CONSISTENCY_CHECK, critical=True, description=d),
        HealthCheck(STRUCTURAL_GAPS_CHECK, critical=True, description=d),
        HealthCheck(TRACEABILITY_GAPS_CHECK, critical=True, description=d),
        HealthCheck(OWNERSHIP_GAPS_CHECK, critical=True, description=d),
    )


class MeasurementHealth:
    """A deterministic health probe over a measurement run + its registry."""

    __slots__ = ("_gap_report", "_coverage", "_registry", "_deterministic")

    def __init__(
        self,
        *,
        gap_report: GapReport,
        coverage: CoverageMeasurement,
        registry: MeasurementRegistry,
        deterministic: bool,
    ) -> None:
        if not isinstance(gap_report, GapReport):
            raise TypeError("a valid GapReport is required")
        if not isinstance(coverage, CoverageMeasurement):
            raise TypeError("a valid CoverageMeasurement is required")
        if not isinstance(registry, MeasurementRegistry):
            raise TypeError("a valid MeasurementRegistry is required")
        self._gap_report = gap_report
        self._coverage = coverage
        self._registry = registry
        self._deterministic = bool(deterministic)

    # -- fault surfaces ---------------------------------------------------------

    def registry_consistent(self) -> bool:
        """True iff a fresh registry replaying the recorded measurements matches.

        A tamper-evident consistency check: re-recording the recorded measurements into
        a new registry must reproduce the same fingerprint (append-only integrity).
        """
        try:
            rebuilt = MeasurementRegistry()
            rebuilt.record_all(self._registry.all())
            return rebuilt.fingerprint() == self._registry.fingerprint()
        except Exception:  # pragma: no cover - fail-closed on any rebuild error
            return False

    def structural_gap_count(self) -> int:
        return self._gap_report.structural_count

    def traceability_gap_count(self) -> int:
        return len(self._gap_report.of_type(INCOMPLETE_TRACEABILITY))

    def ownership_gap_count(self) -> int:
        return len(self._gap_report.of_type(UNASSIGNED_OWNER))

    # -- probe ------------------------------------------------------------------

    def probe(self, *, strict: bool = False) -> dict[str, HealthStatus]:
        """Compute the five measurement health statuses (fail-closed)."""
        gap_status = HealthStatus.UNHEALTHY if strict else HealthStatus.DEGRADED
        results: dict[str, HealthStatus] = {}
        results[DETERMINISM_CHECK] = (
            HealthStatus.HEALTHY if self._deterministic else HealthStatus.UNHEALTHY
        )
        results[REGISTRY_CONSISTENCY_CHECK] = (
            HealthStatus.HEALTHY if self.registry_consistent() else HealthStatus.UNHEALTHY
        )
        results[STRUCTURAL_GAPS_CHECK] = (
            gap_status if self.structural_gap_count() else HealthStatus.HEALTHY
        )
        results[TRACEABILITY_GAPS_CHECK] = (
            gap_status if self.traceability_gap_count() else HealthStatus.HEALTHY
        )
        results[OWNERSHIP_GAPS_CHECK] = (
            gap_status if self.ownership_gap_count() else HealthStatus.HEALTHY
        )
        return results

    @property
    def integrity_ok(self) -> bool:
        """True iff both integrity checks are HEALTHY (engine self-integrity)."""
        probe = self.probe(strict=False)
        return all(probe[c] is HealthStatus.HEALTHY for c in _INTEGRITY_CHECKS)

    def healthy(self, *, strict: bool = False) -> bool:
        """True iff every check is HEALTHY under the chosen policy."""
        return all(s is HealthStatus.HEALTHY for s in self.probe(strict=strict).values())


__all__ = [
    "DETERMINISM_CHECK",
    "REGISTRY_CONSISTENCY_CHECK",
    "STRUCTURAL_GAPS_CHECK",
    "TRACEABILITY_GAPS_CHECK",
    "OWNERSHIP_GAPS_CHECK",
    "measurement_health_checks",
    "MeasurementHealth",
]
