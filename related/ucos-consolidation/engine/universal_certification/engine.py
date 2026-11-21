"""UCOS-EPIC-006 — Universal Certification Engine (Terminal T6).

The :class:`UniversalCertificationEngine` runs the **Compliance Engine** and then a
suite of **Certification Rules** over a normalized
:class:`~engine.universal_certification.contracts.UniversalCertificationSubject`,
aggregating the findings into a deterministic :class:`CertificationDecision` that
carries an **immutable, content-addressed**
:class:`~engine.universal_certification.contracts.Certificate`.

The decision is *fail-closed* and *non-optimistic* (OP-CERT-001 discipline): the
status is **CERTIFIED** iff **no blocking rule failed**; any blocking failure — a
non-conformant compliance report, absent validation evidence, an unsatisfied blocking
measurement, an inconsistent repository truth, a missing disclosure — yields
**NOT-CERTIFIED**. Execution is deterministic (IMP-007 §5): compliance frames and
rules run in stable id order and the certificate embeds no wall-clock or ambient
state, so an identical set of consumed inputs yields a byte-identical decision,
certificate, and ``certification_id`` (reproducible certification).
"""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
from typing import Any

from engine.foundation.obs.logging import get_logger
from engine.foundation.obs.telemetry import trace
from engine.runtime.disclosure import build_disclosure
from engine.universal_certification.compliance import (
    ComplianceEngine,
    ComplianceFrame,
    ComplianceReport,
)
from engine.universal_certification.contracts import (
    Certificate,
    CertificationClass,
    CertificationStatus,
    MeasurementInput,
    RepositoryTruthInput,
    RuleFinding,
    UniversalCertificationSubject,
    ValidationInput,
)
from engine.universal_certification.rules import CertificationRule, default_rules

_logger = get_logger("universal_certification.engine")


@dataclass(frozen=True, slots=True)
class CertificationDecision:
    """The immutable outcome of a universal certification run over a subject."""

    target_id: str
    blueprint_id: str
    version: str
    status: CertificationStatus
    certification_class: CertificationClass
    certificate: Certificate
    compliance: ComplianceReport
    findings: tuple[RuleFinding, ...]
    blocking_failures: tuple[str, ...]
    advisory_failures: tuple[str, ...]

    @property
    def certified(self) -> bool:
        return self.status is CertificationStatus.CERTIFIED

    @property
    def certification_id(self) -> str:
        return self.certificate.certification_id

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
            "compliance": self.compliance.to_dict(),
            "certificate": self.certificate.to_dict(),
        }


class UniversalCertificationEngine:
    """Runs compliance + rules and issues an immutable, fail-closed certificate."""

    __slots__ = ("_compliance", "_rules")

    def __init__(
        self,
        *,
        rules: Iterable[CertificationRule] | None = None,
        frames: Iterable[ComplianceFrame] | None = None,
        compliance_engine: ComplianceEngine | None = None,
    ) -> None:
        selected = tuple(rules) if rules is not None else default_rules()
        # Stable id order guarantees deterministic finding ordering.
        self._rules = tuple(sorted(selected, key=lambda r: r.rule_id))
        if compliance_engine is not None:
            self._compliance = compliance_engine
        else:
            self._compliance = ComplianceEngine(frames)

    @property
    def rule_ids(self) -> tuple[str, ...]:
        return tuple(r.rule_id for r in self._rules)

    @property
    def frame_ids(self) -> tuple[str, ...]:
        return self._compliance.frame_ids

    def certify(self, subject: UniversalCertificationSubject) -> CertificationDecision:
        """Evaluate compliance + every rule over ``subject`` and issue a decision."""
        with trace("universal_certification.certify", target=subject.target_id):
            compliance = self._compliance.evaluate(subject)
            findings = tuple(r.evaluate(subject, compliance) for r in self._rules)
            blocking = tuple(f.rule_id for f in findings if f.is_blocking_failure)
            advisory = tuple(
                f.rule_id
                for f in findings
                if f.status.value == "fail" and not f.is_blocking_failure
            )
            status = (
                CertificationStatus.NOT_CERTIFIED if blocking else CertificationStatus.CERTIFIED
            )
            digests = subject.digests()
            certificate = Certificate.create(
                target_id=subject.target_id,
                blueprint_id=subject.blueprint_id,
                version=subject.version,
                status=status,
                certification_class=subject.certification_class,
                validation_evidence_ref=subject.validation.evidence_sha256,
                measurement_digest=digests["measurement"],
                repository_truth_digest=digests["repository_truth"],
                compliance_digest=compliance.digest(),
                rules=findings,
                disclosure=build_disclosure(),
            )
            decision = CertificationDecision(
                target_id=subject.target_id,
                blueprint_id=subject.blueprint_id,
                version=subject.version,
                status=status,
                certification_class=subject.certification_class,
                certificate=certificate,
                compliance=compliance,
                findings=findings,
                blocking_failures=blocking,
                advisory_failures=advisory,
            )
        _logger.info(
            "universal_certification.decided",
            target=subject.target_id,
            certification_id=certificate.certification_id,
            status=status.value,
            blocking_failed=len(blocking),
        )
        return decision

    def certify_inputs(
        self,
        *,
        validation: ValidationInput,
        measurement: MeasurementInput,
        repository_truth: RepositoryTruthInput,
        version: str,
        target_id: str | None = None,
        blueprint_id: str | None = None,
        certification_class: CertificationClass = CertificationClass.UNIVERSAL_READINESS,
    ) -> CertificationDecision:
        """Convenience: build a subject from raw inputs and certify it."""
        subject = UniversalCertificationSubject.create(
            validation=validation,
            measurement=measurement,
            repository_truth=repository_truth,
            version=version,
            target_id=target_id,
            blueprint_id=blueprint_id,
            certification_class=certification_class,
        )
        return self.certify(subject)


__all__ = ["CertificationDecision", "UniversalCertificationEngine"]
