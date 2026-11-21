"""UCOS-EPIC-006 — Compliance Engine (Terminal T6).

The **Compliance Engine** expresses conformance frames as declarative, deterministic
predicates over a :class:`~engine.universal_certification.contracts.UniversalCertificationSubject`
and aggregates them into an immutable, content-addressed :class:`ComplianceReport`
(MIP Part 15 — compliance frames are policy, measured by observation). A frame is a
pure function of the subject: no secrets, no registry mutation, no wall-clock — so an
identical subject yields identical frame findings.

Every built-in frame **aggregates** an upstream verdict already present in the
subject's consumed inputs (validation acceptance + evidence, measurement satisfaction,
repository-truth consistency, provisional-state disclosure): the engine re-judges no
artifact (TP-01). The architecture is open — callers may supply their own frames. The
report is *fail-closed*: it is CONFORMANT iff **no blocking frame reported a
non-conformance**.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Iterable
from dataclasses import dataclass
from typing import Any, ClassVar

from engine.foundation.obs.logging import get_logger
from engine.foundation.obs.telemetry import trace
from engine.universal_certification.contracts import (
    ComplianceFinding,
    ComplianceStatus,
    RuleSeverity,
    UniversalCertificationSubject,
    content_hash,
)

_logger = get_logger("universal_certification.compliance")

#: The compliance report record format identifier.
COMPLIANCE_REPORT_FORMAT = "ucos-universal-compliance-report/1.0.0"


class ComplianceFrame(ABC):
    """The common contract for a single compliance frame (a conformance predicate)."""

    frame_id: ClassVar[str]
    severity: ClassVar[RuleSeverity]
    description: ClassVar[str] = ""

    @abstractmethod
    def evaluate(self, subject: UniversalCertificationSubject) -> ComplianceFinding:
        """Return a finding for ``subject`` (never raises for a well-formed subject)."""
        raise NotImplementedError  # pragma: no cover

    # -- helpers ---------------------------------------------------------------

    def _conformant(self, message: str = "", **details: Any) -> ComplianceFinding:
        return ComplianceFinding(
            frame_id=self.frame_id,
            severity=self.severity,
            status=ComplianceStatus.CONFORMANT,
            message=message or f"{self.frame_id} conformant",
            details=details,
        )

    def _nonconformant(self, message: str, **details: Any) -> ComplianceFinding:
        return ComplianceFinding(
            frame_id=self.frame_id,
            severity=self.severity,
            status=ComplianceStatus.NON_CONFORMANT,
            message=message,
            details=details,
        )


class ValidationConformanceFrame(ComplianceFrame):
    """Validation accepted the target with a PASS verdict."""

    frame_id = "validation-conformance"
    severity = RuleSeverity.BLOCKING
    description = "The consumed validation verdict is PASS and the target was accepted."

    def evaluate(self, subject: UniversalCertificationSubject) -> ComplianceFinding:
        v = subject.validation
        if not v.accepted or v.verdict != "pass":
            return self._nonconformant(
                "validation did not accept the target",
                verdict=v.verdict,
                blocking_failures=list(v.blocking_failures),
            )
        return self._conformant(verdict=v.verdict)


class ValidationEvidenceFrame(ComplianceFrame):
    """Reproducible validation evidence is present and referenced."""

    frame_id = "validation-evidence-conformance"
    severity = RuleSeverity.BLOCKING
    description = "A validation evidence record is present and content-hashable."

    def evaluate(self, subject: UniversalCertificationSubject) -> ComplianceFinding:
        v = subject.validation
        if not v.evidence_present or not v.evidence_sha256:
            return self._nonconformant("validation evidence is absent; cannot certify")
        return self._conformant(evidence_sha256=v.evidence_sha256)


class MeasurementConformanceFrame(ComplianceFrame):
    """Every blocking measurement is satisfied against its threshold."""

    frame_id = "measurement-conformance"
    severity = RuleSeverity.BLOCKING
    description = "All blocking measurements are satisfied (measurement over assertion)."

    def evaluate(self, subject: UniversalCertificationSubject) -> ComplianceFinding:
        m = subject.measurement
        if not m.present:
            return self._nonconformant("no measurements were consumed; cannot certify")
        shortfalls = m.blocking_shortfalls
        if shortfalls:
            return self._nonconformant(
                "one or more blocking measurements fell short",
                blocking_shortfalls=list(shortfalls),
            )
        return self._conformant(counts=m.counts())


class RepositoryTruthConformanceFrame(ComplianceFrame):
    """The repository-truth attestation is closed, fully homed, and gap-free."""

    frame_id = "repository-truth-conformance"
    severity = RuleSeverity.BLOCKING
    description = "The repository-truth closure is consistent (closed, homed, zero gaps)."

    def evaluate(self, subject: UniversalCertificationSubject) -> ComplianceFinding:
        rt = subject.repository_truth
        if not rt.consistent:
            return self._nonconformant(
                "repository truth is not consistent",
                closed=rt.closed,
                fully_homed=rt.fully_homed,
                open_gap_categories=list(rt.open_gap_categories),
                gap_total=rt.gap_total,
            )
        return self._conformant(total_concepts=rt.total_concepts, snapshot_id=rt.snapshot_id)


class DisclosureConformanceFrame(ComplianceFrame):
    """The EC-1 provisional-state disclosure invariant was validated (DE-05)."""

    frame_id = "disclosure-conformance"
    severity = RuleSeverity.BLOCKING
    description = "Validation ran and passed the EC-1 provisional-state disclosure check."

    def evaluate(self, subject: UniversalCertificationSubject) -> ComplianceFinding:
        if not subject.validation.disclosure_validated:
            return self._nonconformant("provisional-state disclosure was not validated")
        return self._conformant()


def default_frames() -> tuple[ComplianceFrame, ...]:
    """Return the built-in compliance frame suite, ordered deterministically by id."""
    frames: tuple[ComplianceFrame, ...] = (
        DisclosureConformanceFrame(),
        MeasurementConformanceFrame(),
        RepositoryTruthConformanceFrame(),
        ValidationConformanceFrame(),
        ValidationEvidenceFrame(),
    )
    return tuple(sorted(frames, key=lambda f: f.frame_id))


@dataclass(frozen=True, slots=True)
class ComplianceReport:
    """An immutable, content-addressed aggregate of a compliance evaluation."""

    target_id: str
    blueprint_id: str
    version: str
    status: ComplianceStatus
    findings: tuple[ComplianceFinding, ...]
    non_conformances: tuple[str, ...]

    @property
    def conformant(self) -> bool:
        return self.status is ComplianceStatus.CONFORMANT

    def counts(self) -> dict[str, int]:
        conformant = sum(1 for f in self.findings if f.conformant)
        blocking = sum(1 for f in self.findings if f.is_blocking_nonconformance)
        return {
            "total": len(self.findings),
            "conformant": conformant,
            "non_conformant": len(self.findings) - conformant,
            "blocking_non_conformant": blocking,
        }

    def to_dict(self) -> dict[str, Any]:
        return {
            "report_format": COMPLIANCE_REPORT_FORMAT,
            "target_id": self.target_id,
            "blueprint_id": self.blueprint_id,
            "version": self.version,
            "status": self.status.value,
            "conformant": self.conformant,
            "counts": self.counts(),
            "findings": [f.to_dict() for f in self.findings],
            "non_conformances": list(self.non_conformances),
        }

    def digest(self) -> str:
        """The deterministic content hash of this compliance report."""
        return content_hash(self.to_dict())


class ComplianceEngine:
    """Runs a deterministic suite of compliance frames over a subject (fail-closed)."""

    __slots__ = ("_frames",)

    def __init__(self, frames: Iterable[ComplianceFrame] | None = None) -> None:
        selected = tuple(frames) if frames is not None else default_frames()
        self._frames = tuple(sorted(selected, key=lambda f: f.frame_id))

    @property
    def frame_ids(self) -> tuple[str, ...]:
        return tuple(f.frame_id for f in self._frames)

    def evaluate(self, subject: UniversalCertificationSubject) -> ComplianceReport:
        """Evaluate every frame over ``subject`` and aggregate a compliance report."""
        with trace("universal_certification.compliance", target=subject.target_id):
            findings = tuple(f.evaluate(subject) for f in self._frames)
            non_conformances = tuple(f.frame_id for f in findings if f.is_blocking_nonconformance)
            status = (
                ComplianceStatus.NON_CONFORMANT if non_conformances else ComplianceStatus.CONFORMANT
            )
            report = ComplianceReport(
                target_id=subject.target_id,
                blueprint_id=subject.blueprint_id,
                version=subject.version,
                status=status,
                findings=findings,
                non_conformances=non_conformances,
            )
        _logger.info(
            "universal_certification.compliance.evaluated",
            target=subject.target_id,
            status=status.value,
            blocking_non_conformant=len(non_conformances),
        )
        return report


__all__ = [
    "COMPLIANCE_REPORT_FORMAT",
    "ComplianceFrame",
    "ValidationConformanceFrame",
    "ValidationEvidenceFrame",
    "MeasurementConformanceFrame",
    "RepositoryTruthConformanceFrame",
    "DisclosureConformanceFrame",
    "default_frames",
    "ComplianceReport",
    "ComplianceEngine",
]
