"""TASK-000052 — Certification Evidence Generation (EPIC-008).

A **Certification Evidence Record** captures, deterministically, the outcome of a
certification determination so it is auditable (IMP-007 §11; Mandatory Rule 6 —
every determination yields evidence). The record embeds no wall-clock or ambient
state, so an identical certification decision produces a byte-identical record.

It captures the certification identity + status, the class and readiness standard,
the ordered per-criterion findings, the counts, the explicit blocking-failure list,
the **reference to the reproducible validation evidence** it aggregates, and the
content hash of the immutable certification record — closing the evidence chain
Validation Evidence → Certification Evidence (URS-L-21 reproducibility).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from engine.certification.contracts import content_hash
from engine.certification.engine import CertificationDecision

#: The certification evidence record format identifier.
EVIDENCE_FORMAT = "ucos-certification-evidence/1.0.0"


@dataclass(frozen=True, slots=True)
class CertificationEvidence:
    """A deterministic, serializable Certification Evidence Record."""

    certification_id: str
    target_id: str
    blueprint_id: str
    version: str
    status: str
    certified: bool
    certification_class: str
    standard: str
    standard_version: str
    criteria_evaluated: tuple[str, ...]
    counts: dict[str, int]
    findings: tuple[dict[str, Any], ...]
    blocking_failures: tuple[str, ...]
    validation_evidence_ref: str
    record_sha256: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "evidence_format": EVIDENCE_FORMAT,
            "certification_id": self.certification_id,
            "target_id": self.target_id,
            "blueprint_id": self.blueprint_id,
            "version": self.version,
            "status": self.status,
            "certified": self.certified,
            "certification_class": self.certification_class,
            "standard": self.standard,
            "standard_version": self.standard_version,
            "criteria_evaluated": list(self.criteria_evaluated),
            "counts": dict(self.counts),
            "findings": [dict(f) for f in self.findings],
            "blocking_failures": list(self.blocking_failures),
            "validation_evidence_ref": self.validation_evidence_ref,
            "record_sha256": self.record_sha256,
        }

    def content_sha256(self) -> str:
        """The deterministic content hash of this evidence record."""
        return content_hash(self.to_dict())


def build_certification_evidence(decision: CertificationDecision) -> CertificationEvidence:
    """Assemble a deterministic :class:`CertificationEvidence` from a decision."""
    record = decision.record
    return CertificationEvidence(
        certification_id=record.certification_id,
        target_id=decision.target_id,
        blueprint_id=decision.blueprint_id,
        version=decision.version,
        status=decision.status.value,
        certified=decision.certified,
        certification_class=decision.certification_class.value,
        standard=record.standard,
        standard_version=record.standard_version,
        criteria_evaluated=tuple(f.criterion_id for f in decision.findings),
        counts=decision.counts(),
        findings=tuple(f.to_dict() for f in decision.findings),
        blocking_failures=tuple(decision.blocking_failures),
        validation_evidence_ref=record.evidence_ref,
        record_sha256=record.content_sha256,
    )


__all__ = [
    "EVIDENCE_FORMAT",
    "CertificationEvidence",
    "build_certification_evidence",
]
