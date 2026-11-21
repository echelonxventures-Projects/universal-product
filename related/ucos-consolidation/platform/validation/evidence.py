"""EC2-TASK-000148 — Validation Console Evidence (EC2-EPIC-010).

The deterministic, content-addressed record of the validation-console runtime state
(evidence). It embeds no wall-clock and no ambient state, so an identical runtime state
(records, inspections, access evaluations, health) yields a byte-identical
:class:`ValidationConsoleEvidence` and fingerprint (P5 / Mandatory Rule 6 — every
determination yields evidence). It is distinct from the per-target EC-1
:class:`~engine.validation.evidence.ValidationEvidence` (which the console surfaces by
reference): this is *runtime* evidence over the console itself.
"""

from __future__ import annotations

from dataclasses import dataclass
from platform.foundation.contracts import content_hash
from typing import Any


@dataclass(frozen=True, slots=True)
class ValidationConsoleEvidence:
    """A deterministic, content-addressed record of console runtime state (evidence)."""

    registry_fingerprint: str
    record_count: int
    accepted_count: int
    rejected_count: int
    inspection_count: int
    access_evaluation_count: int
    verdict_census: tuple[tuple[str, int], ...]
    health_status: str
    evidence_id: str = ""

    @classmethod
    def create(
        cls,
        *,
        registry_fingerprint: str,
        record_count: int,
        accepted_count: int,
        rejected_count: int,
        inspection_count: int,
        access_evaluation_count: int,
        verdict_census: tuple[tuple[str, int], ...],
        health_status: str,
    ) -> ValidationConsoleEvidence:
        core = {
            "registry_fingerprint": registry_fingerprint,
            "record_count": record_count,
            "accepted_count": accepted_count,
            "rejected_count": rejected_count,
            "inspection_count": inspection_count,
            "access_evaluation_count": access_evaluation_count,
            "verdict_census": [list(pair) for pair in verdict_census],
            "health_status": health_status,
        }
        return cls(
            registry_fingerprint=registry_fingerprint,
            record_count=record_count,
            accepted_count=accepted_count,
            rejected_count=rejected_count,
            inspection_count=inspection_count,
            access_evaluation_count=access_evaluation_count,
            verdict_census=verdict_census,
            health_status=health_status,
            evidence_id=f"UCOS-VEVD-{content_hash(core)[:16]}",
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "evidence_id": self.evidence_id,
            "registry_fingerprint": self.registry_fingerprint,
            "record_count": self.record_count,
            "accepted_count": self.accepted_count,
            "rejected_count": self.rejected_count,
            "inspection_count": self.inspection_count,
            "access_evaluation_count": self.access_evaluation_count,
            "verdict_census": {name: count for name, count in self.verdict_census},
            "health_status": self.health_status,
        }

    def fingerprint(self) -> str:
        return content_hash(self.to_dict())


__all__ = ["ValidationConsoleEvidence"]
