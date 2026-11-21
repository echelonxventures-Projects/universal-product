"""EPIC-VAL-003 — Unified Governance Evidence (Terminal T3).

A **Governance Evidence Record** captures, deterministically, the outcome of a full
repository governance run so it is auditable (IMP-007 §11; Mandatory Rule 6 — every
determination yields evidence). It is the *unified* evidence artifact the mission
requires: it closes the whole evidence chain end to end —

    per-unit Validation Evidence → per-unit Certification Evidence →
    repository Acceptance Evidence → the append-only Certification Ledger

— into a single, content-addressed record. Every stage evidence record is embedded
verbatim *and* referenced by its content hash, so the governance root hash is a
tamper-evident commitment over every subordinate determination (full traceability).

The record embeds no wall-clock or ambient state, so an identical governance run
produces a byte-identical evidence record.
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

from engine.governance.contracts import content_hash

if TYPE_CHECKING:  # pragma: no cover - typing only
    from engine.acceptance.evidence import AcceptanceEvidence
    from engine.certification.ledger import CertificationLedger
    from engine.governance.report import GovernedUnit

#: The unified governance evidence record format identifier.
EVIDENCE_FORMAT = "ucos-governance-evidence/1.0.0"


@dataclass(frozen=True, slots=True)
class GovernanceEvidence:
    """A deterministic, serializable unified Governance Evidence Record."""

    repository_id: str
    epic_id: str
    unit_ids: tuple[str, ...]
    validation_evidence: tuple[dict[str, Any], ...]
    certification_evidence: tuple[dict[str, Any], ...]
    acceptance_evidence: dict[str, Any]
    ledger: dict[str, Any]
    validation_evidence_refs: tuple[str, ...]
    certification_evidence_refs: tuple[str, ...]
    acceptance_evidence_ref: str
    ledger_head: str
    counts: dict[str, int]
    evidence_sha256: str

    def _core(self) -> dict[str, Any]:
        return {
            "repository_id": self.repository_id,
            "epic_id": self.epic_id,
            "unit_ids": list(self.unit_ids),
            "validation_evidence": [dict(e) for e in self.validation_evidence],
            "certification_evidence": [dict(e) for e in self.certification_evidence],
            "acceptance_evidence": dict(self.acceptance_evidence),
            "ledger": dict(self.ledger),
            "validation_evidence_refs": list(self.validation_evidence_refs),
            "certification_evidence_refs": list(self.certification_evidence_refs),
            "acceptance_evidence_ref": self.acceptance_evidence_ref,
            "ledger_head": self.ledger_head,
            "counts": dict(self.counts),
        }

    def to_dict(self) -> dict[str, Any]:
        return {
            "evidence_format": EVIDENCE_FORMAT,
            **self._core(),
            "evidence_sha256": self.evidence_sha256,
        }

    def recompute_hash(self) -> str:
        """Recompute the content hash from the current field values."""
        return content_hash(self._core())

    def verify_integrity(self) -> bool:
        """Return True iff the stored content hash matches a recomputation."""
        return self.recompute_hash() == self.evidence_sha256


def build_governance_evidence(
    *,
    repository_id: str,
    epic_id: str,
    units: Sequence[GovernedUnit],
    acceptance_evidence: AcceptanceEvidence,
    ledger: CertificationLedger,
) -> GovernanceEvidence:
    """Assemble the unified governance evidence from the per-stage evidence chain."""
    validation_evidence = tuple(u.validation_evidence.to_dict() for u in units)
    certification_evidence = tuple(u.certification_evidence.to_dict() for u in units)
    validation_evidence_refs = tuple(content_hash(e) for e in validation_evidence)
    certification_evidence_refs = tuple(u.certification_evidence.content_sha256() for u in units)
    acceptance_dict = acceptance_evidence.to_dict()
    counts = {
        "units": len(units),
        "validated": sum(1 for u in units if u.validated),
        "certified": sum(1 for u in units if u.certified),
    }
    core = {
        "repository_id": repository_id,
        "epic_id": epic_id,
        "unit_ids": [u.unit_id for u in units],
        "validation_evidence": [dict(e) for e in validation_evidence],
        "certification_evidence": [dict(e) for e in certification_evidence],
        "acceptance_evidence": dict(acceptance_dict),
        "ledger": ledger.to_dict(),
        "validation_evidence_refs": list(validation_evidence_refs),
        "certification_evidence_refs": list(certification_evidence_refs),
        "acceptance_evidence_ref": acceptance_evidence.content_sha256(),
        "ledger_head": ledger.head_hash,
        "counts": dict(counts),
    }
    return GovernanceEvidence(
        repository_id=repository_id,
        epic_id=epic_id,
        unit_ids=tuple(u.unit_id for u in units),
        validation_evidence=validation_evidence,
        certification_evidence=certification_evidence,
        acceptance_evidence=acceptance_dict,
        ledger=ledger.to_dict(),
        validation_evidence_refs=validation_evidence_refs,
        certification_evidence_refs=certification_evidence_refs,
        acceptance_evidence_ref=acceptance_evidence.content_sha256(),
        ledger_head=ledger.head_hash,
        counts=counts,
        evidence_sha256=content_hash(core),
    )


__all__ = [
    "EVIDENCE_FORMAT",
    "GovernanceEvidence",
    "build_governance_evidence",
]
