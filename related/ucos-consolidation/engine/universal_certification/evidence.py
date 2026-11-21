"""UCOS-EPIC-006 — Certification Evidence (Terminal T6).

A **Universal Certification Evidence Record** captures, deterministically, the outcome
of a universal certification determination so it is auditable (IMP-007 §11; Mandatory
Rule 6 — every determination yields evidence). The record embeds no wall-clock or
ambient state, so an identical decision produces a byte-identical record.

It captures the certification identity + status, the class and readiness standard, the
ordered per-rule findings and counts, the explicit blocking-failure list, and — the
point of a *universal* engine — the **references to the three reproducible consumed
evidences it aggregates**: the validation evidence hash, the measurement digest, the
repository-truth digest, and the compliance report digest, plus the content hash of the
immutable certificate. This closes the evidence chain

    {Validation Evidence, Measurement, Repository Truth} → Compliance → Certificate
    → Certification Evidence

so a certification is reproducible and traceable to every input it consumed
(URS-L-21 reproducibility).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from engine.universal_certification.contracts import content_hash
from engine.universal_certification.engine import CertificationDecision

#: The universal certification evidence record format identifier.
EVIDENCE_FORMAT = "ucos-universal-certification-evidence/1.0.0"


@dataclass(frozen=True, slots=True)
class CertificationEvidence:
    """A deterministic, serializable Universal Certification Evidence Record."""

    certification_id: str
    target_id: str
    blueprint_id: str
    version: str
    status: str
    certified: bool
    certification_class: str
    standard: str
    standard_version: str
    rules_evaluated: tuple[str, ...]
    counts: dict[str, int]
    findings: tuple[dict[str, Any], ...]
    blocking_failures: tuple[str, ...]
    validation_evidence_ref: str
    measurement_digest: str
    repository_truth_digest: str
    compliance_digest: str
    compliance_status: str
    certificate_sha256: str

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
            "rules_evaluated": list(self.rules_evaluated),
            "counts": dict(self.counts),
            "findings": [dict(f) for f in self.findings],
            "blocking_failures": list(self.blocking_failures),
            "validation_evidence_ref": self.validation_evidence_ref,
            "measurement_digest": self.measurement_digest,
            "repository_truth_digest": self.repository_truth_digest,
            "compliance_digest": self.compliance_digest,
            "compliance_status": self.compliance_status,
            "certificate_sha256": self.certificate_sha256,
        }

    def content_sha256(self) -> str:
        """The deterministic content hash of this evidence record."""
        return content_hash(self.to_dict())


def build_certification_evidence(decision: CertificationDecision) -> CertificationEvidence:
    """Assemble a deterministic :class:`CertificationEvidence` from a decision."""
    certificate = decision.certificate
    return CertificationEvidence(
        certification_id=certificate.certification_id,
        target_id=decision.target_id,
        blueprint_id=decision.blueprint_id,
        version=decision.version,
        status=decision.status.value,
        certified=decision.certified,
        certification_class=decision.certification_class.value,
        standard=certificate.standard,
        standard_version=certificate.standard_version,
        rules_evaluated=tuple(f.rule_id for f in decision.findings),
        counts=decision.counts(),
        findings=tuple(f.to_dict() for f in decision.findings),
        blocking_failures=tuple(decision.blocking_failures),
        validation_evidence_ref=certificate.validation_evidence_ref,
        measurement_digest=certificate.measurement_digest,
        repository_truth_digest=certificate.repository_truth_digest,
        compliance_digest=certificate.compliance_digest,
        compliance_status=decision.compliance.status.value,
        certificate_sha256=certificate.content_sha256,
    )


__all__ = [
    "EVIDENCE_FORMAT",
    "CertificationEvidence",
    "build_certification_evidence",
]
