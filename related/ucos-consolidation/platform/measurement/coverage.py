"""UCOS-EPIC-004 — Coverage Engine (UCOS-UMA-001).

Measures **traceability-chain coverage** across the thirteen ordered stages of the
Registry traceability spine (``requirement → … → operations``). For every artifact it
reads which stages carry at least one reference, then reports per-stage coverage, the
count of fully-traced artifacts, and the overall mean stage coverage.

This is complementary to the Universe→Code coverage instrument (``platform.coverage``):
that instrument measures the universe→code spine; this one measures the *per-artifact
traceability chain* recorded in Registry Truth. Both are pure, deterministic functions
of their input and author no Truth. Coverage here is a **measurement of** the corpus's
own recorded traceability — it never fabricates a trace reference.
"""

from __future__ import annotations

from dataclasses import dataclass
from platform.foundation.contracts import content_hash
from platform.measurement.contracts import Measurement, MeasurementKind
from platform.measurement.errors import CoverageMeasurementError
from platform.measurement.source import TruthSnapshot
from typing import Any

from engine.registry.models import TRACE_STAGES


def _percent(part: int, whole: int) -> float:
    """Deterministic percentage (0.0 when the population is empty)."""
    if whole <= 0:
        return 0.0
    return round(100.0 * part / whole, 4)


@dataclass(frozen=True, slots=True)
class CoverageMeasurement:
    """An immutable, content-addressed traceability-coverage measurement."""

    artifact_total: int
    per_stage: dict[str, dict[str, float]]
    fully_traced_count: int
    fully_traced_percentage: float
    overall_percentage: float
    coverage_id: str = ""

    @classmethod
    def create(
        cls,
        *,
        artifact_total: int,
        per_stage: dict[str, dict[str, float]],
        fully_traced_count: int,
        fully_traced_percentage: float,
        overall_percentage: float,
    ) -> CoverageMeasurement:
        ordered_stage = {stage: per_stage[stage] for stage in TRACE_STAGES if stage in per_stage}
        core = {
            "artifact_total": artifact_total,
            "per_stage": ordered_stage,
            "fully_traced_count": fully_traced_count,
            "fully_traced_percentage": fully_traced_percentage,
            "overall_percentage": overall_percentage,
        }
        return cls(
            artifact_total=artifact_total,
            per_stage=ordered_stage,
            fully_traced_count=fully_traced_count,
            fully_traced_percentage=fully_traced_percentage,
            overall_percentage=overall_percentage,
            coverage_id=f"UCOS-UMAC-{content_hash(core)[:16]}",
        )

    def stage_percentage(self, stage: str) -> float:
        """The coverage percentage recorded for a traceability ``stage`` (fail-closed)."""
        if stage not in self.per_stage:
            raise CoverageMeasurementError("unknown traceability stage", stage=stage)
        return self.per_stage[stage]["percentage"]

    def to_dict(self) -> dict[str, Any]:
        return {
            "coverage_id": self.coverage_id,
            "artifact_total": self.artifact_total,
            "per_stage": {s: dict(v) for s, v in self.per_stage.items()},
            "fully_traced_count": self.fully_traced_count,
            "fully_traced_percentage": self.fully_traced_percentage,
            "overall_percentage": self.overall_percentage,
        }

    def fingerprint(self) -> str:
        return content_hash(self.to_dict())

    def as_measurement(self) -> Measurement:
        """Wrap the coverage measurement as a recordable :class:`Measurement`."""
        return Measurement.create(
            MeasurementKind.COVERAGE,
            "registry.traceability",
            summary=(
                f"{self.overall_percentage}% mean stage coverage; "
                f"{self.fully_traced_count}/{self.artifact_total} fully traced"
            ),
            payload=self.to_dict(),
        )


class CoverageEngine:
    """Deterministically measures traceability-chain coverage from a Truth snapshot."""

    __slots__ = ("_snapshot",)

    def __init__(self, snapshot: TruthSnapshot) -> None:
        if not isinstance(snapshot, TruthSnapshot):
            raise CoverageMeasurementError("CoverageEngine requires a TruthSnapshot")
        self._snapshot = snapshot

    def measure(self) -> CoverageMeasurement:
        """Compute per-stage and overall traceability coverage (pure, deterministic)."""
        arts = self._snapshot.artifacts
        total = len(arts)

        stage_populated: dict[str, int] = {stage: 0 for stage in TRACE_STAGES}
        fully_traced = 0
        for artifact in arts:
            populated_here = 0
            for stage in TRACE_STAGES:
                if artifact.traceability.stage(stage):
                    stage_populated[stage] += 1
                    populated_here += 1
            if populated_here == len(TRACE_STAGES):
                fully_traced += 1

        per_stage: dict[str, dict[str, float]] = {
            stage: {
                "populated": float(stage_populated[stage]),
                "total": float(total),
                "percentage": _percent(stage_populated[stage], total),
            }
            for stage in TRACE_STAGES
        }
        # Overall mean stage coverage = mean of per-stage percentages.
        overall = (
            round(sum(v["percentage"] for v in per_stage.values()) / len(TRACE_STAGES), 4)
            if total
            else 0.0
        )
        return CoverageMeasurement.create(
            artifact_total=total,
            per_stage=per_stage,
            fully_traced_count=fully_traced,
            fully_traced_percentage=_percent(fully_traced, total),
            overall_percentage=overall,
        )


__all__ = ["CoverageMeasurement", "CoverageEngine"]
