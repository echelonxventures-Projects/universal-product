"""EPIC-VAL-002 — Repository Acceptance Evidence (Terminal T3).

An **Acceptance Evidence Record** captures, deterministically, the outcome of a
repository acceptance determination so it is auditable (IMP-007 §11; Mandatory
Rule 6 — every determination yields evidence). The record embeds no wall-clock or
ambient state, so an identical acceptance decision produces a byte-identical record.

It captures the acceptance identity + status, the acceptance standard, the ordered
per-gate findings, the counts, the explicit blocking-failure list, the reference to
the reproducible assimilated-subject digest it aggregates, and the content hash of
the immutable acceptance record — closing the evidence chain
subject → decision → acceptance evidence.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from engine.acceptance.contracts import content_hash
from engine.acceptance.engine import AcceptanceDecision

#: The acceptance evidence record format identifier.
EVIDENCE_FORMAT = "ucos-acceptance-evidence/1.0.0"


@dataclass(frozen=True, slots=True)
class AcceptanceEvidence:
    """A deterministic, serializable Repository Acceptance Evidence Record."""

    acceptance_id: str
    repository_id: str
    epic_id: str
    status: str
    accepted: bool
    standard: str
    standard_version: str
    gates_evaluated: tuple[str, ...]
    counts: dict[str, int]
    findings: tuple[dict[str, Any], ...]
    blocking_failures: tuple[str, ...]
    advisory_failures: tuple[str, ...]
    subject_ref: str
    record_sha256: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "evidence_format": EVIDENCE_FORMAT,
            "acceptance_id": self.acceptance_id,
            "repository_id": self.repository_id,
            "epic_id": self.epic_id,
            "status": self.status,
            "accepted": self.accepted,
            "standard": self.standard,
            "standard_version": self.standard_version,
            "gates_evaluated": list(self.gates_evaluated),
            "counts": dict(self.counts),
            "findings": [dict(f) for f in self.findings],
            "blocking_failures": list(self.blocking_failures),
            "advisory_failures": list(self.advisory_failures),
            "subject_ref": self.subject_ref,
            "record_sha256": self.record_sha256,
        }

    def content_sha256(self) -> str:
        """The deterministic content hash of this evidence record."""
        return content_hash(self.to_dict())


def build_acceptance_evidence(decision: AcceptanceDecision) -> AcceptanceEvidence:
    """Assemble a deterministic :class:`AcceptanceEvidence` from a decision."""
    record = decision.record
    return AcceptanceEvidence(
        acceptance_id=record.acceptance_id,
        repository_id=decision.repository_id,
        epic_id=decision.epic_id,
        status=decision.status.value,
        accepted=decision.accepted,
        standard=record.standard,
        standard_version=record.standard_version,
        gates_evaluated=tuple(f.gate_id for f in decision.findings),
        counts=decision.counts(),
        findings=tuple(f.to_dict() for f in decision.findings),
        blocking_failures=tuple(decision.blocking_failures),
        advisory_failures=tuple(decision.advisory_failures),
        subject_ref=record.evidence_ref,
        record_sha256=record.content_sha256,
    )


__all__ = [
    "EVIDENCE_FORMAT",
    "AcceptanceEvidence",
    "build_acceptance_evidence",
]
