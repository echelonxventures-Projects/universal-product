"""UCOS-EPIC-013 — Validation Intelligence evidence generation (Terminal T5).

A **Validation Intelligence Evidence Record** captures, deterministically, the outcome
of a continuous-validation-intelligence run so it is auditable (IMP-007 §11; Mandatory
Rule 6 — every determination yields evidence). The record embeds no wall-clock or
ambient state, so an identical report produces a byte-identical record and evidence
hash.

It captures the target, the aggregate verdict, the per-dimension verdicts, the ordered
per-check findings, the counts, the explicit blocking/advisory failure lists, and the
two headline deliverable projections — the Compatibility Report and the Compliance
Report — so a downstream gate or dashboard consumes one self-contained artifact.
"""

from __future__ import annotations

from dataclasses import dataclass
from platform.foundation.contracts import content_hash
from platform.validation_intelligence.contracts import ValidationIntelligenceReport
from typing import Any

#: The validation-intelligence evidence record format identifier.
EVIDENCE_FORMAT = "ucos-validation-intelligence-evidence/1.0.0"


@dataclass(frozen=True, slots=True)
class ValidationIntelligenceEvidence:
    """A deterministic, serializable, content-addressed Validation Evidence Record."""

    target_id: str
    verdict: str
    passed: bool
    target_digest: str
    report_sha256: str
    dimensions_run: tuple[str, ...]
    dimension_verdicts: dict[str, str]
    checks_run: tuple[str, ...]
    counts: dict[str, int]
    findings: tuple[dict[str, Any], ...]
    blocking_failures: tuple[str, ...]
    advisory_failures: tuple[str, ...]
    compatible: bool
    compliant: bool
    compatibility_report: dict[str, Any]
    compliance_report: dict[str, Any]
    authority: str
    disclosure: dict[str, Any]

    def _core(self) -> dict[str, Any]:
        return {
            "evidence_format": EVIDENCE_FORMAT,
            "target_id": self.target_id,
            "verdict": self.verdict,
            "passed": self.passed,
            "target_digest": self.target_digest,
            "report_sha256": self.report_sha256,
            "dimensions_run": list(self.dimensions_run),
            "dimension_verdicts": dict(self.dimension_verdicts),
            "checks_run": list(self.checks_run),
            "counts": dict(self.counts),
            "findings": [dict(f) for f in self.findings],
            "blocking_failures": list(self.blocking_failures),
            "advisory_failures": list(self.advisory_failures),
            "compatible": self.compatible,
            "compliant": self.compliant,
            "compatibility_report": dict(self.compatibility_report),
            "compliance_report": dict(self.compliance_report),
            "authority": self.authority,
            "disclosure": dict(self.disclosure),
        }

    @property
    def evidence_sha256(self) -> str:
        """The deterministic content hash of the evidence record."""
        return content_hash(self._core())

    def to_dict(self) -> dict[str, Any]:
        return {**self._core(), "evidence_sha256": self.evidence_sha256}


def build_validation_intelligence_evidence(
    report: ValidationIntelligenceReport,
) -> ValidationIntelligenceEvidence:
    """Assemble a deterministic :class:`ValidationIntelligenceEvidence` from a report."""
    compatibility = report.compatibility_report()
    compliance = report.compliance_report()
    return ValidationIntelligenceEvidence(
        target_id=report.target_id,
        verdict=report.verdict.value,
        passed=report.passed,
        target_digest=report.target_digest,
        report_sha256=report.report_sha256,
        dimensions_run=report.dimensions_run(),
        dimension_verdicts=report.dimension_verdicts(),
        checks_run=tuple(f.check_id for f in report.all_findings),
        counts=report.counts(),
        findings=tuple(f.to_dict() for f in report.all_findings),
        blocking_failures=report.blocking_failures(),
        advisory_failures=report.advisory_failures(),
        compatible=compatibility.compatible,
        compliant=compliance.compliant,
        compatibility_report=compatibility.to_dict(),
        compliance_report=compliance.to_dict(),
        authority=report.authority,
        disclosure=dict(report.disclosure),
    )


__all__ = [
    "EVIDENCE_FORMAT",
    "ValidationIntelligenceEvidence",
    "build_validation_intelligence_evidence",
]
