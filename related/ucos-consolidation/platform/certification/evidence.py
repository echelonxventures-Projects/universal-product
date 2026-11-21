"""EC2-TASK-000157 — Certification Console Evidence (EC2-EPIC-011).

The deterministic, content-addressed record of the certification-console runtime state
(evidence). It embeds no wall-clock and no ambient state, so an identical runtime state
(records, ledger, inspections, access evaluations, health) yields a byte-identical
:class:`CertificationConsoleEvidence` and fingerprint (P5 / Mandatory Rule 6 — every
determination yields evidence). It is distinct from the per-target EC-1
:class:`~engine.certification.evidence.CertificationEvidence` (which the console surfaces
by reference): this is *runtime* evidence over the console itself.
"""

from __future__ import annotations

from dataclasses import dataclass
from platform.foundation.contracts import content_hash
from typing import Any


@dataclass(frozen=True, slots=True)
class CertificationConsoleEvidence:
    """A deterministic, content-addressed record of console runtime state (evidence)."""

    registry_fingerprint: str
    ledger_fingerprint: str
    record_count: int
    certified_count: int
    not_certified_count: int
    ledger_entry_count: int
    ledger_intact: bool
    inspection_count: int
    access_evaluation_count: int
    status_census: tuple[tuple[str, int], ...]
    health_status: str
    evidence_id: str = ""

    @classmethod
    def create(
        cls,
        *,
        registry_fingerprint: str,
        ledger_fingerprint: str,
        record_count: int,
        certified_count: int,
        not_certified_count: int,
        ledger_entry_count: int,
        ledger_intact: bool,
        inspection_count: int,
        access_evaluation_count: int,
        status_census: tuple[tuple[str, int], ...],
        health_status: str,
    ) -> CertificationConsoleEvidence:
        core = {
            "registry_fingerprint": registry_fingerprint,
            "ledger_fingerprint": ledger_fingerprint,
            "record_count": record_count,
            "certified_count": certified_count,
            "not_certified_count": not_certified_count,
            "ledger_entry_count": ledger_entry_count,
            "ledger_intact": ledger_intact,
            "inspection_count": inspection_count,
            "access_evaluation_count": access_evaluation_count,
            "status_census": [list(pair) for pair in status_census],
            "health_status": health_status,
        }
        return cls(
            registry_fingerprint=registry_fingerprint,
            ledger_fingerprint=ledger_fingerprint,
            record_count=record_count,
            certified_count=certified_count,
            not_certified_count=not_certified_count,
            ledger_entry_count=ledger_entry_count,
            ledger_intact=ledger_intact,
            inspection_count=inspection_count,
            access_evaluation_count=access_evaluation_count,
            status_census=status_census,
            health_status=health_status,
            evidence_id=f"UCOS-CEVD-{content_hash(core)[:16]}",
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "evidence_id": self.evidence_id,
            "registry_fingerprint": self.registry_fingerprint,
            "ledger_fingerprint": self.ledger_fingerprint,
            "record_count": self.record_count,
            "certified_count": self.certified_count,
            "not_certified_count": self.not_certified_count,
            "ledger_entry_count": self.ledger_entry_count,
            "ledger_intact": self.ledger_intact,
            "inspection_count": self.inspection_count,
            "access_evaluation_count": self.access_evaluation_count,
            "status_census": {name: count for name, count in self.status_census},
            "health_status": self.health_status,
        }

    def fingerprint(self) -> str:
        return content_hash(self.to_dict())


__all__ = ["CertificationConsoleEvidence"]
