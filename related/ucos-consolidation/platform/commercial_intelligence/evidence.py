"""UCOS-EPIC-014 — Business Evidence (Terminal T5).

Business Evidence is what makes a commercial determination auditable rather than merely
stated. This module carries both halves of it:

    * the **declared** business evidence a commercial surface claims — an
      :class:`EvidenceIndex` of content-addressed :class:`EvidenceEntry` records, one per
      commercial artefact, each naming its subject and the SHA-256 of the artefact it
      stands for. An entry without a well-formed digest is refused: an unaddressed claim
      is not evidence.
    * the **produced** business evidence of one commercial-intelligence run — a
      :class:`CommercialEvidence` record embedding the target, the verdict, the
      per-domain verdicts, the ordered findings, the counts and the derived certificate,
      so a downstream gate or dashboard consumes one self-contained artefact.

No wall-clock or ambient state enters either half, so an identical run reproduces a
byte-identical record and evidence hash (IMP-007 §5; Mandatory Rule 6 — every
determination yields evidence).
"""

from __future__ import annotations

import re
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from platform.commercial_intelligence.certification import CommercialCertificate
from platform.commercial_intelligence.contracts import CommercialIntelligenceReport
from platform.commercial_intelligence.errors import CommercialTargetError
from platform.foundation.contracts import content_hash
from typing import Any

#: The commercial-intelligence evidence record format identifier.
EVIDENCE_FORMAT = "ucos-commercial-intelligence-evidence/1.0.0"

#: The declared business-evidence index format identifier.
EVIDENCE_INDEX_FORMAT = "ucos-business-evidence-index/1.0.0"

_SHA256_PATTERN = re.compile(r"^[0-9a-f]{64}$")


@dataclass(frozen=True, slots=True)
class EvidenceEntry:
    """One content-addressed business-evidence claim."""

    evidence_id: str
    subject_id: str
    kind: str
    sha256: str

    def __post_init__(self) -> None:
        for name, value in (
            ("evidence_id", self.evidence_id),
            ("subject_id", self.subject_id),
            ("kind", self.kind),
        ):
            if not value:
                raise CommercialTargetError(
                    f"a business-evidence entry requires a {name}",
                    evidence_id=self.evidence_id,
                )
        if not _SHA256_PATTERN.match(self.sha256 or ""):
            raise CommercialTargetError(
                "a business-evidence entry requires the lower-case hex SHA-256 of the "
                "artefact it stands for — an unaddressed claim is not evidence",
                evidence_id=self.evidence_id,
            )

    @classmethod
    def from_mapping(cls, raw: Any) -> EvidenceEntry:
        if not isinstance(raw, Mapping):
            raise CommercialTargetError("a business-evidence entry must be a mapping")
        return cls(
            evidence_id=str(raw.get("evidence_id") or ""),
            subject_id=str(raw.get("subject_id") or ""),
            kind=str(raw.get("kind") or ""),
            sha256=str(raw.get("sha256") or ""),
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "evidence_id": self.evidence_id,
            "subject_id": self.subject_id,
            "kind": self.kind,
            "sha256": self.sha256,
        }


@dataclass(frozen=True, slots=True)
class EvidenceIndex:
    """An immutable, deterministically ordered index of declared business evidence."""

    entries: tuple[EvidenceEntry, ...] = ()

    def __post_init__(self) -> None:
        seen: set[str] = set()
        for entry in self.entries:
            if entry.evidence_id in seen:
                raise CommercialTargetError(
                    "duplicate evidence_id in the business-evidence index",
                    evidence_id=entry.evidence_id,
                )
            seen.add(entry.evidence_id)

    @classmethod
    def from_sequence(cls, raw: Any) -> EvidenceIndex:
        if isinstance(raw, str | bytes) or not isinstance(raw, Sequence):
            raise CommercialTargetError("a business-evidence index must be a sequence of entries")
        entries = tuple(
            sorted(
                (EvidenceEntry.from_mapping(item) for item in raw),
                key=lambda entry: entry.evidence_id,
            )
        )
        return cls(entries=entries)

    def subjects(self) -> tuple[str, ...]:
        return tuple(sorted({entry.subject_id for entry in self.entries}))

    def kinds(self) -> tuple[str, ...]:
        return tuple(sorted({entry.kind for entry in self.entries}))

    def for_subject(self, subject_id: str) -> tuple[EvidenceEntry, ...]:
        return tuple(entry for entry in self.entries if entry.subject_id == subject_id)

    def collisions(self) -> tuple[str, ...]:
        """Distinct evidence ids that stand for the *same* artefact digest and subject.

        Two entries claiming the same subject and the same digest are the same evidence
        recorded twice — a duplication defect, reported rather than silently deduplicated.
        """
        seen: dict[tuple[str, str], str] = {}
        collisions: list[str] = []
        for entry in self.entries:
            key = (entry.subject_id, entry.sha256)
            if key in seen:
                collisions.append(f"{entry.evidence_id} duplicates {seen[key]}")
            else:
                seen[key] = entry.evidence_id
        return tuple(collisions)

    def to_dict(self) -> dict[str, Any]:
        return {
            "index_format": EVIDENCE_INDEX_FORMAT,
            "entries": [entry.to_dict() for entry in self.entries],
            "total": len(self.entries),
            "subjects": list(self.subjects()),
            "kinds": list(self.kinds()),
            "collisions": list(self.collisions()),
        }

    def digest(self) -> str:
        return content_hash([entry.to_dict() for entry in self.entries])


@dataclass(frozen=True, slots=True)
class CommercialEvidence:
    """A deterministic, serializable, content-addressed Business Evidence Record."""

    target_id: str
    verdict: str
    passed: bool
    determination: str
    certified: bool
    target_digest: str
    report_sha256: str
    certificate_sha256: str
    domains_run: tuple[str, ...]
    domain_verdicts: dict[str, str]
    kind_verdicts: dict[str, str]
    checks_run: tuple[str, ...]
    counts: dict[str, int]
    findings: tuple[dict[str, Any], ...]
    blocking_failures: tuple[str, ...]
    advisory_failures: tuple[str, ...]
    certificate: dict[str, Any]
    authority: str
    disclosure: dict[str, Any]

    def _core(self) -> dict[str, Any]:
        return {
            "evidence_format": EVIDENCE_FORMAT,
            "target_id": self.target_id,
            "verdict": self.verdict,
            "passed": self.passed,
            "determination": self.determination,
            "certified": self.certified,
            "target_digest": self.target_digest,
            "report_sha256": self.report_sha256,
            "certificate_sha256": self.certificate_sha256,
            "domains_run": list(self.domains_run),
            "domain_verdicts": dict(self.domain_verdicts),
            "kind_verdicts": dict(self.kind_verdicts),
            "checks_run": list(self.checks_run),
            "counts": dict(self.counts),
            "findings": [dict(f) for f in self.findings],
            "blocking_failures": list(self.blocking_failures),
            "advisory_failures": list(self.advisory_failures),
            "certificate": dict(self.certificate),
            "authority": self.authority,
            "disclosure": dict(self.disclosure),
        }

    @property
    def evidence_sha256(self) -> str:
        """The deterministic content hash of the evidence record."""
        return content_hash(self._core())

    def to_dict(self) -> dict[str, Any]:
        return {**self._core(), "evidence_sha256": self.evidence_sha256}


def build_commercial_evidence(
    report: CommercialIntelligenceReport, certificate: CommercialCertificate | None = None
) -> CommercialEvidence:
    """Assemble a deterministic :class:`CommercialEvidence` from a report (and certificate)."""
    certificate = certificate or CommercialCertificate.from_report(report)
    return CommercialEvidence(
        target_id=report.target_id,
        verdict=report.verdict.value,
        passed=report.passed,
        determination=certificate.determination.value,
        certified=certificate.certified,
        target_digest=report.target_digest,
        report_sha256=report.report_sha256,
        certificate_sha256=certificate.certificate_sha256,
        domains_run=report.domains_run(),
        domain_verdicts=report.domain_verdicts(),
        kind_verdicts=report.kind_verdicts(),
        checks_run=tuple(f.check_id for f in report.all_findings),
        counts=report.counts(),
        findings=tuple(f.to_dict() for f in report.all_findings),
        blocking_failures=report.blocking_failures(),
        advisory_failures=report.advisory_failures(),
        certificate=certificate.to_dict(),
        authority=report.authority,
        disclosure=dict(report.disclosure),
    )


__all__ = [
    "EVIDENCE_FORMAT",
    "EVIDENCE_INDEX_FORMAT",
    "EvidenceEntry",
    "EvidenceIndex",
    "CommercialEvidence",
    "build_commercial_evidence",
]
