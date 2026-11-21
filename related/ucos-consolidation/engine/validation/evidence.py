"""TASK-000048 — Validation Evidence Generation (EPIC-007).

A **Validation Evidence Record** captures, deterministically, the outcome of a
validation run so it is auditable (IMP-007 §11; Mandatory Rule 6 — every
determination yields evidence). The record embeds no wall-clock or ambient state,
so an identical report produces a byte-identical record.

It captures the target, the blueprint, the aggregate verdict, the ordered
per-check findings, the counts, and the explicit blocking-failure list that an
acceptance gate consumes (TASK-000049).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from engine.validation.contracts import ValidationReport

#: The validation evidence record format identifier.
EVIDENCE_FORMAT = "ucos-validation-evidence/1.0.0"


@dataclass(frozen=True, slots=True)
class ValidationEvidence:
    """A deterministic, serializable Validation Evidence Record."""

    target_id: str
    blueprint_id: str
    verdict: str
    accepted: bool
    checks_run: tuple[str, ...]
    counts: dict[str, int]
    findings: tuple[dict[str, Any], ...]
    blocking_failures: tuple[str, ...]

    def to_dict(self) -> dict[str, Any]:
        return {
            "evidence_format": EVIDENCE_FORMAT,
            "target_id": self.target_id,
            "blueprint_id": self.blueprint_id,
            "verdict": self.verdict,
            "accepted": self.accepted,
            "checks_run": list(self.checks_run),
            "counts": dict(self.counts),
            "findings": [dict(f) for f in self.findings],
            "blocking_failures": list(self.blocking_failures),
        }


def build_validation_evidence(report: ValidationReport) -> ValidationEvidence:
    """Assemble a deterministic :class:`ValidationEvidence` from a report."""
    return ValidationEvidence(
        target_id=report.target_id,
        blueprint_id=report.blueprint_id,
        verdict=report.verdict.value,
        accepted=report.accepted,
        checks_run=tuple(f.check_id for f in report.findings),
        counts=report.counts(),
        findings=tuple(f.to_dict() for f in report.findings),
        blocking_failures=tuple(f.check_id for f in report.blocking_failures),
    )


__all__ = [
    "EVIDENCE_FORMAT",
    "ValidationEvidence",
    "build_validation_evidence",
]
