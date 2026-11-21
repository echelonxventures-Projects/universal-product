"""UCOS-EPIC-004 — Measurement evidence (UCOS-UMA-001).

The deterministic, content-addressed evidence artifact the engine emits for a single
measurement run — the machine-consumable proof (for TRACK-001 / certification) of what
was measured over which Truth. It records the Truth fingerprint it measured, the
fingerprint of each engine result, the registry fingerprint, the headline figures, and
the health verdict. Evidence is a pure function of the run: identical Truth yields
byte-identical evidence (IMP-007 §5). Evidence describes Truth; it is never Truth.
"""

from __future__ import annotations

from dataclasses import dataclass
from platform.foundation.contracts import content_hash
from platform.measurement.errors import MeasurementEvidenceError
from typing import Any


@dataclass(frozen=True, slots=True)
class MeasurementEvidence:
    """An immutable, content-addressed snapshot of a measurement run over Truth."""

    truth_fingerprint: str
    enumeration_fingerprint: str
    metrics_fingerprint: str
    coverage_fingerprint: str
    gaps_fingerprint: str
    registry_fingerprint: str
    artifact_count: int
    relationship_count: int
    volume_count: int
    traceability_percentage: float
    fully_traced_count: int
    gap_count: int
    structural_gap_count: int
    health_status: str
    evidence_id: str = ""

    @classmethod
    def create(
        cls,
        *,
        truth_fingerprint: str,
        enumeration_fingerprint: str,
        metrics_fingerprint: str,
        coverage_fingerprint: str,
        gaps_fingerprint: str,
        registry_fingerprint: str,
        artifact_count: int,
        relationship_count: int,
        volume_count: int,
        traceability_percentage: float,
        fully_traced_count: int,
        gap_count: int,
        structural_gap_count: int,
        health_status: str,
    ) -> MeasurementEvidence:
        if not truth_fingerprint:
            raise MeasurementEvidenceError("evidence requires a Truth fingerprint")
        core = {
            "truth_fingerprint": truth_fingerprint,
            "enumeration_fingerprint": enumeration_fingerprint,
            "metrics_fingerprint": metrics_fingerprint,
            "coverage_fingerprint": coverage_fingerprint,
            "gaps_fingerprint": gaps_fingerprint,
            "registry_fingerprint": registry_fingerprint,
            "artifact_count": artifact_count,
            "relationship_count": relationship_count,
            "volume_count": volume_count,
            "traceability_percentage": traceability_percentage,
            "fully_traced_count": fully_traced_count,
            "gap_count": gap_count,
            "structural_gap_count": structural_gap_count,
            "health_status": health_status,
        }
        return cls(
            truth_fingerprint=truth_fingerprint,
            enumeration_fingerprint=enumeration_fingerprint,
            metrics_fingerprint=metrics_fingerprint,
            coverage_fingerprint=coverage_fingerprint,
            gaps_fingerprint=gaps_fingerprint,
            registry_fingerprint=registry_fingerprint,
            artifact_count=artifact_count,
            relationship_count=relationship_count,
            volume_count=volume_count,
            traceability_percentage=traceability_percentage,
            fully_traced_count=fully_traced_count,
            gap_count=gap_count,
            structural_gap_count=structural_gap_count,
            health_status=health_status,
            evidence_id=f"UCOS-UMAV-{content_hash(core)[:16]}",
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "evidence_id": self.evidence_id,
            "truth_fingerprint": self.truth_fingerprint,
            "enumeration_fingerprint": self.enumeration_fingerprint,
            "metrics_fingerprint": self.metrics_fingerprint,
            "coverage_fingerprint": self.coverage_fingerprint,
            "gaps_fingerprint": self.gaps_fingerprint,
            "registry_fingerprint": self.registry_fingerprint,
            "artifact_count": self.artifact_count,
            "relationship_count": self.relationship_count,
            "volume_count": self.volume_count,
            "traceability_percentage": self.traceability_percentage,
            "fully_traced_count": self.fully_traced_count,
            "gap_count": self.gap_count,
            "structural_gap_count": self.structural_gap_count,
            "health_status": self.health_status,
        }

    def fingerprint(self) -> str:
        return content_hash(self.to_dict())


__all__ = ["MeasurementEvidence"]
