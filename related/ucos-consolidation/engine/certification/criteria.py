"""TASK-000050 — Certification architecture: criteria (EPIC-008).

A certification **criterion** is an immutable, deterministic predicate over a
:class:`~engine.certification.contracts.CertificationSubject`. Each criterion has a
stable id, a severity, and an ``evaluate`` method returning a
:class:`~engine.certification.contracts.CertificationFinding`. Criteria are pure
functions of the subject — no secrets, no registry mutation, no wall-clock — so
identical subjects yield identical findings.

The built-in suite is *sound*: because the subject is projected purely from a
Validation Report + Validation Evidence, every criterion **aggregates the validation
verdict** (it re-judges no artifact — TP-01). The suite requires that validation
accepted the artifact, that reproducible validation evidence is present, that the
EC-1 provisional-state disclosure invariant was validated (DE-05), and that the
certification is version-pinned (URS-L-20). The architecture is open: callers may
supply their own criteria to the engine.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, ClassVar

from engine.certification.contracts import (
    CertificationFinding,
    CertificationSubject,
    CriterionSeverity,
    CriterionStatus,
)

#: The validation check id that proves the EC-1 provisional-state disclosure (DE-05).
_DISCLOSURE_CHECK_ID = "provisional-state-disclosure"


class CertificationCriterion(ABC):
    """The common contract for a single certification criterion (architecture unit)."""

    criterion_id: ClassVar[str]
    severity: ClassVar[CriterionSeverity]
    description: ClassVar[str] = ""

    @abstractmethod
    def evaluate(self, subject: CertificationSubject) -> CertificationFinding:
        """Return a finding for ``subject`` (never raises for a well-formed subject)."""
        raise NotImplementedError  # pragma: no cover

    # -- helpers ---------------------------------------------------------------

    def _passed(self, message: str = "", **details: Any) -> CertificationFinding:
        return CertificationFinding(
            criterion_id=self.criterion_id,
            severity=self.severity,
            status=CriterionStatus.PASS,
            message=message or f"{self.criterion_id} satisfied",
            details=details,
        )

    def _failed(self, message: str, **details: Any) -> CertificationFinding:
        return CertificationFinding(
            criterion_id=self.criterion_id,
            severity=self.severity,
            status=CriterionStatus.FAIL,
            message=message,
            details=details,
        )


class ValidationAcceptedCriterion(CertificationCriterion):
    """Validation accepted the artifact — the core certification aggregation."""

    criterion_id = "validation-accepted"
    severity = CriterionSeverity.BLOCKING
    description = "The upstream validation verdict is PASS with no blocking failure."

    def evaluate(self, subject: CertificationSubject) -> CertificationFinding:
        if not subject.validation_accepted or subject.validation_verdict != "pass":
            return self._failed(
                "validation did not accept the artifact",
                verdict=subject.validation_verdict,
                blocking_failures=list(subject.blocking_failures),
            )
        return self._passed(verdict=subject.validation_verdict)


class ValidationEvidencePresentCriterion(CertificationCriterion):
    """Reproducible validation evidence is present and referenced (soundness)."""

    criterion_id = "validation-evidence-present"
    severity = CriterionSeverity.BLOCKING
    description = "A validation evidence record is present and content-hashable."

    def evaluate(self, subject: CertificationSubject) -> CertificationFinding:
        if not subject.evidence_present or not subject.evidence_sha256:
            return self._failed("validation evidence is absent; cannot certify")
        return self._passed(evidence_sha256=subject.evidence_sha256)


class DisclosureValidatedCriterion(CertificationCriterion):
    """The EC-1 provisional-state disclosure invariant was validated (DE-05)."""

    criterion_id = "provisional-state-disclosed"
    severity = CriterionSeverity.BLOCKING
    description = "Validation ran and passed the EC-1 provisional-state disclosure check."

    def evaluate(self, subject: CertificationSubject) -> CertificationFinding:
        if _DISCLOSURE_CHECK_ID not in subject.checks_run:
            return self._failed(
                "provisional-state disclosure was not validated",
                check_id=_DISCLOSURE_CHECK_ID,
            )
        if _DISCLOSURE_CHECK_ID in subject.blocking_failures:
            return self._failed(
                "provisional-state disclosure validation failed",
                check_id=_DISCLOSURE_CHECK_ID,
            )
        return self._passed(check_id=_DISCLOSURE_CHECK_ID)


class VersionPinnedCriterion(CertificationCriterion):
    """The certification is pinned to a concrete artifact version (URS-L-20)."""

    criterion_id = "version-pinned"
    severity = CriterionSeverity.BLOCKING
    description = "A non-empty version pin is present so the record is version-scoped."

    def evaluate(self, subject: CertificationSubject) -> CertificationFinding:
        if not subject.version.strip():
            return self._failed("certification is not version-pinned")
        return self._passed(version=subject.version)


class ValidationCompleteCriterion(CertificationCriterion):
    """Every validation check passed, including advisory checks (advisory signal)."""

    criterion_id = "validation-complete"
    severity = CriterionSeverity.ADVISORY
    description = "No validation check failed, including advisory checks."

    def evaluate(self, subject: CertificationSubject) -> CertificationFinding:
        failed = int(subject.counts.get("failed", 0))
        if failed:
            return self._failed("one or more validation checks failed", failed=failed)
        return self._passed(total=int(subject.counts.get("total", 0)))


def default_criteria() -> tuple[CertificationCriterion, ...]:
    """Return the built-in certification suite, ordered deterministically by id."""
    criteria: tuple[CertificationCriterion, ...] = (
        DisclosureValidatedCriterion(),
        ValidationAcceptedCriterion(),
        ValidationCompleteCriterion(),
        ValidationEvidencePresentCriterion(),
        VersionPinnedCriterion(),
    )
    return tuple(sorted(criteria, key=lambda c: c.criterion_id))


__all__ = [
    "CertificationCriterion",
    "ValidationAcceptedCriterion",
    "ValidationEvidencePresentCriterion",
    "DisclosureValidatedCriterion",
    "VersionPinnedCriterion",
    "ValidationCompleteCriterion",
    "default_criteria",
]
