"""UCOS-EPIC-005 — Universal Validation evidence generation (Terminal T5).

A **Validation Evidence Record** captures, deterministically, the outcome of a
universal validation run so it is auditable (IMP-007 §11; Mandatory Rule 6 — every
determination yields evidence). The record embeds no wall-clock or ambient state, so
an identical report produces a byte-identical record and evidence hash.

It captures the target, the aggregate verdict, the per-domain verdicts, the ordered
per-rule findings, the counts, and the explicit blocking/advisory failure lists that a
downstream gate or dashboard consumes.
"""

from __future__ import annotations

from dataclasses import dataclass
from platform.foundation.contracts import content_hash
from platform.universal_validation.contracts import ValidationReport
from typing import Any

#: The validation evidence record format identifier.
EVIDENCE_FORMAT = "ucos-universal-validation-evidence/1.0.0"


@dataclass(frozen=True, slots=True)
class ValidationEvidence:
    """A deterministic, serializable, content-addressed Validation Evidence Record."""

    target_id: str
    verdict: str
    passed: bool
    target_digest: str
    report_sha256: str
    domains_run: tuple[str, ...]
    domain_verdicts: dict[str, str]
    rules_run: tuple[str, ...]
    counts: dict[str, int]
    findings: tuple[dict[str, Any], ...]
    blocking_failures: tuple[str, ...]
    advisory_failures: tuple[str, ...]
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
            "domains_run": list(self.domains_run),
            "domain_verdicts": dict(self.domain_verdicts),
            "rules_run": list(self.rules_run),
            "counts": dict(self.counts),
            "findings": [dict(f) for f in self.findings],
            "blocking_failures": list(self.blocking_failures),
            "advisory_failures": list(self.advisory_failures),
            "authority": self.authority,
            "disclosure": dict(self.disclosure),
        }

    @property
    def evidence_sha256(self) -> str:
        """The deterministic content hash of the evidence record."""
        return content_hash(self._core())

    def to_dict(self) -> dict[str, Any]:
        return {**self._core(), "evidence_sha256": self.evidence_sha256}


def build_validation_evidence(report: ValidationReport) -> ValidationEvidence:
    """Assemble a deterministic :class:`ValidationEvidence` from a report."""
    return ValidationEvidence(
        target_id=report.target_id,
        verdict=report.verdict.value,
        passed=report.passed,
        target_digest=report.target_digest,
        report_sha256=report.report_sha256,
        domains_run=report.domains_run(),
        domain_verdicts=report.domain_verdicts(),
        rules_run=tuple(r.rule_id for r in report.all_results),
        counts=report.counts(),
        findings=tuple(r.to_dict() for r in report.all_results),
        blocking_failures=report.blocking_failures(),
        advisory_failures=report.advisory_failures(),
        authority=report.authority,
        disclosure=dict(report.disclosure),
    )


__all__ = [
    "EVIDENCE_FORMAT",
    "ValidationEvidence",
    "build_validation_evidence",
]
