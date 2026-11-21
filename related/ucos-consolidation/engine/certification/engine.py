"""TASK-000051 — Certification Decision (EPIC-008).

The :class:`CertificationEngine` runs a suite of criteria over a normalized
:class:`~engine.certification.contracts.CertificationSubject` and aggregates the
findings into a deterministic :class:`CertificationDecision` that carries an
**immutable, content-addressed** :class:`~engine.certification.contracts.CertificationRecord`.

The decision is *fail-closed* and *non-optimistic* (OP-CERT-001 discipline): the
status is **CERTIFIED** iff **no blocking criterion failed**; any blocking failure —
including absent validation evidence — yields **NOT-CERTIFIED**. Execution is
deterministic (IMP-007 §5): criteria run in stable id order and the record embeds no
wall-clock or ambient state, so an identical Validation Report + Validation Evidence
yields a byte-identical decision, record, and ``certification_id`` (reproducible
certification decisions).
"""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

from engine.certification.contracts import (
    CertificationClass,
    CertificationFinding,
    CertificationRecord,
    CertificationStatus,
    CertificationSubject,
)
from engine.certification.criteria import CertificationCriterion, default_criteria
from engine.foundation.contracts.disclosure import build_disclosure
from engine.foundation.obs.logging import get_logger
from engine.foundation.obs.telemetry import trace

if TYPE_CHECKING:  # pragma: no cover - typing only
    from engine.validation.contracts import ValidationReport
    from engine.validation.evidence import ValidationEvidence

_logger = get_logger("certification.engine")


@dataclass(frozen=True, slots=True)
class CertificationDecision:
    """The immutable outcome of a certification run over a subject."""

    target_id: str
    blueprint_id: str
    version: str
    status: CertificationStatus
    certification_class: CertificationClass
    record: CertificationRecord
    findings: tuple[CertificationFinding, ...]
    blocking_failures: tuple[str, ...]
    advisory_failures: tuple[str, ...]

    @property
    def certified(self) -> bool:
        return self.status is CertificationStatus.CERTIFIED

    @property
    def certification_id(self) -> str:
        return self.record.certification_id

    def counts(self) -> dict[str, int]:
        passed = sum(1 for f in self.findings if f.passed)
        return {
            "total": len(self.findings),
            "passed": passed,
            "failed": len(self.findings) - passed,
            "blocking_failed": len(self.blocking_failures),
            "advisory_failed": len(self.advisory_failures),
        }

    def to_dict(self) -> dict[str, Any]:
        return {
            "target_id": self.target_id,
            "blueprint_id": self.blueprint_id,
            "version": self.version,
            "status": self.status.value,
            "certified": self.certified,
            "certification_class": self.certification_class.value,
            "certification_id": self.certification_id,
            "counts": self.counts(),
            "findings": [f.to_dict() for f in self.findings],
            "blocking_failures": list(self.blocking_failures),
            "advisory_failures": list(self.advisory_failures),
            "record": self.record.to_dict(),
        }


class CertificationEngine:
    """Runs a deterministic suite of criteria and issues a certification decision."""

    __slots__ = ("_criteria",)

    def __init__(self, criteria: Iterable[CertificationCriterion] | None = None) -> None:
        selected = tuple(criteria) if criteria is not None else default_criteria()
        # Stable id order guarantees deterministic finding ordering.
        self._criteria = tuple(sorted(selected, key=lambda c: c.criterion_id))

    @property
    def criterion_ids(self) -> tuple[str, ...]:
        return tuple(c.criterion_id for c in self._criteria)

    def certify(self, subject: CertificationSubject) -> CertificationDecision:
        """Evaluate every criterion over ``subject`` and issue a decision + record."""
        with trace("certification.certify", target=subject.target_id):
            findings = tuple(c.evaluate(subject) for c in self._criteria)
            blocking = tuple(f.criterion_id for f in findings if f.is_blocking_failure)
            advisory = tuple(
                f.criterion_id
                for f in findings
                if f.status.value == "fail" and not f.is_blocking_failure
            )
            status = (
                CertificationStatus.NOT_CERTIFIED if blocking else CertificationStatus.CERTIFIED
            )
            record = CertificationRecord.create(
                target_id=subject.target_id,
                blueprint_id=subject.blueprint_id,
                version=subject.version,
                status=status,
                certification_class=subject.certification_class,
                evidence_ref=subject.evidence_sha256,
                criteria=findings,
                disclosure=build_disclosure(),
            )
            decision = CertificationDecision(
                target_id=subject.target_id,
                blueprint_id=subject.blueprint_id,
                version=subject.version,
                status=status,
                certification_class=subject.certification_class,
                record=record,
                findings=findings,
                blocking_failures=blocking,
                advisory_failures=advisory,
            )
        _logger.info(
            "certification.decided",
            target=subject.target_id,
            certification_id=record.certification_id,
            status=status.value,
            blocking_failed=len(blocking),
        )
        return decision


def certify_validation(
    report: ValidationReport,
    evidence: ValidationEvidence | None,
    *,
    version: str,
    certification_class: CertificationClass = CertificationClass.ENGINEERING_READINESS,
    criteria: Iterable[CertificationCriterion] | None = None,
) -> CertificationDecision:
    """Convenience: certify a Validation Report + Validation Evidence directly."""
    subject = CertificationSubject.from_validation(
        report, evidence, version=version, certification_class=certification_class
    )
    return CertificationEngine(criteria).certify(subject)


__all__ = ["CertificationDecision", "CertificationEngine", "certify_validation"]
