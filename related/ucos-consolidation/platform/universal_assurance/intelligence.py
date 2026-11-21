"""UCOS-EPIC-014 — Validation Intelligence & Certification Intelligence (Terminal T7).

The two capabilities this package **owns** outright.

**Validation Intelligence** (:class:`ValidationIntelligence`) expands validation beyond
static rule execution. It does not re-implement that reasoning: it composes the *reused*
:class:`~platform.validation_intelligence.engine.ContinuousValidationIntelligenceEngine`
— cross-capability consistency, repository completeness, contract/runtime/version
compatibility, architecture/governance compliance — scoped to exactly the dimensions the
**policy** planned, and reconciles every dimension finding back to the obligation that
demanded it under the *policy's* severity. What it adds over the reused engine is the
policy binding, the plan-coverage determination, and the fail-closed treatment of a planned
dimension that never got analyzed.

**Certification Intelligence** (:class:`CertificationIntelligence`) is new. Nothing in the
reused platform answers *"is this certification trustworthy?"* — the certifier answers only
*"do the rules pass?"*. This engine reasons over the whole assurance run and decides seven
orthogonal dimensions:

    * **readiness** — every certification criterion satisfied and every declared gate passed,
    * **criteria coverage** — every declared criterion planned, bound and actually evaluated,
    * **measurement coverage** — every declared metric observed and satisfied,
    * **evidence integrity** — the bundle is complete and every digest recomputes,
    * **certificate integrity** — the certificate verifies against its own content hash,
    * **registry integrity** — the append-only chain verifies and the certification is
      registered, with any policy drift surfaced explicitly, and
    * **reproducibility** — independent replays of the run are byte-identical.

Both engines are **fail-closed** (an undecidable dimension records FAIL, never a pass),
**measurable** (each publishes ``observations()`` the policy's metrics decide), and
**reproducible** (content-addressed over cores that exclude wall-clock).
"""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from dataclasses import dataclass, field
from enum import Enum
from platform.foundation.contracts import content_hash
from platform.universal_assurance.certification import CertificationExecution
from platform.universal_assurance.contracts import (
    ASSURANCE_AUTHORITY,
    AssuranceSubject,
    ObligationKind,
    Outcome,
    Severity,
    Verdict,
)
from platform.universal_assurance.determinism import ReproducibilityReport
from platform.universal_assurance.errors import AssuranceIntelligenceError
from platform.universal_assurance.evidence import EvidenceBundle
from platform.universal_assurance.execution import ObligationOutcome, ValidationExecution
from platform.universal_assurance.generation import GeneratedSuite
from platform.universal_assurance.measurement import MeasurementReport
from platform.universal_assurance.planning import AssurancePlan
from platform.universal_assurance.policy import AssurancePolicy
from platform.universal_assurance.registry import CertificationRegistry
from platform.validation_intelligence.contracts import (
    FindingStatus,
    IntelligenceDimension,
    ValidationIntelligenceReport,
)
from platform.validation_intelligence.engine import ContinuousValidationIntelligenceEngine
from platform.validation_intelligence.evidence import build_validation_intelligence_evidence
from typing import Any

from engine.foundation.obs.logging import get_logger
from engine.foundation.obs.telemetry import trace

_logger = get_logger("universal_assurance.intelligence")

#: Format identifiers for the two intelligence records.
VALIDATION_INTELLIGENCE_FORMAT = "ucos-assurance-validation-intelligence/1.0.0"
CERTIFICATION_INTELLIGENCE_FORMAT = "ucos-assurance-certification-intelligence/1.0.0"

#: Fail-closed reasons recorded when a planned dimension could not be decided.
REASON_NOT_ANALYZED = "not-analyzed"
REASON_UNBOUND = "unbound"
REASON_NO_REPORT = "no-intelligence-report"


# --------------------------------------------------------------------------- #
# Validation Intelligence                                                      #
# --------------------------------------------------------------------------- #


@dataclass(frozen=True, slots=True)
class ValidationIntelligenceOutcome:
    """An immutable, content-addressed record of one policy-governed intelligence run."""

    intelligence_id: str
    subject_id: str
    plan_id: str
    suite_id: str
    policy_digest: str
    verdict: Verdict
    outcomes: tuple[ObligationOutcome, ...]
    dimensions_analyzed: tuple[str, ...]
    dimension_verdicts: Mapping[str, str]
    compatible: bool
    compliant: bool
    report: ValidationIntelligenceReport | None
    report_sha256: str
    evidence_sha256: str
    intelligence_sha256: str

    @staticmethod
    def _core(
        *,
        subject_id: str,
        plan_id: str,
        suite_id: str,
        policy_digest: str,
        verdict: Verdict,
        outcomes: tuple[ObligationOutcome, ...],
        dimensions_analyzed: tuple[str, ...],
        dimension_verdicts: Mapping[str, str],
        compatible: bool,
        compliant: bool,
        report_sha256: str,
        evidence_sha256: str,
    ) -> dict[str, Any]:
        return {
            "intelligence_format": VALIDATION_INTELLIGENCE_FORMAT,
            "subject_id": subject_id,
            "plan_id": plan_id,
            "suite_id": suite_id,
            "policy_digest": policy_digest,
            "verdict": verdict.value,
            "outcomes": [outcome.core() for outcome in outcomes],
            "dimensions_analyzed": list(dimensions_analyzed),
            "dimension_verdicts": dict(dimension_verdicts),
            "compatible": compatible,
            "compliant": compliant,
            "report_sha256": report_sha256,
            "evidence_sha256": evidence_sha256,
        }

    @classmethod
    def create(
        cls,
        *,
        subject_id: str,
        plan_id: str,
        suite_id: str,
        policy_digest: str,
        outcomes: Iterable[ObligationOutcome],
        report: ValidationIntelligenceReport | None,
    ) -> ValidationIntelligenceOutcome:
        """Aggregate reconciled dimension outcomes into a content-addressed record."""
        ordered = tuple(sorted(outcomes, key=lambda o: (o.ref, o.obligation_id)))
        verdict = Verdict.FAIL if any(o.is_blocking_failure for o in ordered) else Verdict.PASS
        dimensions = report.dimensions_run() if report is not None else ()
        verdicts = report.dimension_verdicts() if report is not None else {}
        compatibility = report.compatibility_report() if report is not None else None
        compliance = report.compliance_report() if report is not None else None
        evidence_sha256 = (
            build_validation_intelligence_evidence(report).evidence_sha256
            if report is not None
            else ""
        )
        core = cls._core(
            subject_id=subject_id,
            plan_id=plan_id,
            suite_id=suite_id,
            policy_digest=policy_digest,
            verdict=verdict,
            outcomes=ordered,
            dimensions_analyzed=dimensions,
            dimension_verdicts=verdicts,
            compatible=bool(compatibility is not None and compatibility.compatible),
            compliant=bool(compliance is not None and compliance.compliant),
            report_sha256=report.report_sha256 if report is not None else "",
            evidence_sha256=evidence_sha256,
        )
        digest = content_hash(core)
        return cls(
            intelligence_id=f"UCOS-VINTEL-{digest[:16]}",
            subject_id=subject_id,
            plan_id=plan_id,
            suite_id=suite_id,
            policy_digest=policy_digest,
            verdict=verdict,
            outcomes=ordered,
            dimensions_analyzed=dimensions,
            dimension_verdicts=verdicts,
            compatible=bool(compatibility is not None and compatibility.compatible),
            compliant=bool(compliance is not None and compliance.compliant),
            report=report,
            report_sha256=report.report_sha256 if report is not None else "",
            evidence_sha256=evidence_sha256,
            intelligence_sha256=digest,
        )

    @property
    def passed(self) -> bool:
        return self.verdict is Verdict.PASS

    def blocking_failures(self) -> tuple[str, ...]:
        return tuple(o.obligation_id for o in self.outcomes if o.is_blocking_failure)

    def advisory_failures(self) -> tuple[str, ...]:
        return tuple(o.obligation_id for o in self.outcomes if o.is_advisory_failure)

    def satisfied(self) -> tuple[str, ...]:
        return tuple(o.obligation_id for o in self.outcomes if o.passed)

    def dimension_coverage(self) -> float:
        """The analyzed/planned dimension-obligation ratio (1.0 when none planned)."""
        if not self.outcomes:
            return 1.0
        return sum(1 for o in self.outcomes if o.executed) / len(self.outcomes)

    def counts(self) -> dict[str, int]:
        return {
            "obligations": len(self.outcomes),
            "satisfied": len(self.satisfied()),
            "executed": sum(1 for o in self.outcomes if o.executed),
            "blocking_failed": len(self.blocking_failures()),
            "advisory_failed": len(self.advisory_failures()),
            "dimensions_analyzed": len(self.dimensions_analyzed),
        }

    def observations(self) -> dict[str, float]:
        counts = self.counts()
        return {
            "validation_intelligence.obligations": float(counts["obligations"]),
            "validation_intelligence.satisfied": float(counts["satisfied"]),
            "validation_intelligence.blocking_failures": float(counts["blocking_failed"]),
            "validation_intelligence.advisory_failures": float(counts["advisory_failed"]),
            "validation_intelligence.dimension_coverage": self.dimension_coverage(),
            "validation_intelligence.compatible": 1.0 if self.compatible else 0.0,
            "validation_intelligence.compliant": 1.0 if self.compliant else 0.0,
        }

    def failure_reasons(self) -> dict[str, str]:
        return {
            o.obligation_id: o.implementation_status or o.outcome.value
            for o in self.outcomes
            if not o.passed
        }

    def to_dict(self) -> dict[str, Any]:
        return {
            "intelligence_format": VALIDATION_INTELLIGENCE_FORMAT,
            "intelligence_id": self.intelligence_id,
            "subject_id": self.subject_id,
            "plan_id": self.plan_id,
            "suite_id": self.suite_id,
            "policy_digest": self.policy_digest,
            "verdict": self.verdict.value,
            "passed": self.passed,
            "counts": self.counts(),
            "dimension_coverage": self.dimension_coverage(),
            "dimensions_analyzed": list(self.dimensions_analyzed),
            "dimension_verdicts": dict(self.dimension_verdicts),
            "compatible": self.compatible,
            "compliant": self.compliant,
            "blocking_failures": list(self.blocking_failures()),
            "advisory_failures": list(self.advisory_failures()),
            "outcomes": [o.to_dict() for o in self.outcomes],
            "report": self.report.to_dict() if self.report is not None else None,
            "report_sha256": self.report_sha256,
            "evidence_sha256": self.evidence_sha256,
            "observations": self.observations(),
            "intelligence_sha256": self.intelligence_sha256,
        }


class ValidationIntelligence:
    """**Validation Intelligence** — the reused analyzer suite under policy governance."""

    __slots__ = ("_engine_factory",)

    def __init__(self, engine_factory: Any = None) -> None:
        self._engine_factory = engine_factory or _default_intelligence_engine

    def analyze(
        self, suite: GeneratedSuite, subject: AssuranceSubject
    ) -> ValidationIntelligenceOutcome:
        """Analyze the planned dimensions and reconcile findings to obligations."""
        if not isinstance(suite, GeneratedSuite):
            raise AssuranceIntelligenceError("validation intelligence requires a GeneratedSuite")
        if not isinstance(subject, AssuranceSubject):
            raise AssuranceIntelligenceError("validation intelligence requires an AssuranceSubject")
        dimension_checks = tuple(
            check for check in suite.checks if check.kind is ObligationKind.INTELLIGENCE_DIMENSION
        )
        report: ValidationIntelligenceReport | None = None
        if suite.dimensions:
            with trace("universal_assurance.validation_intelligence", subject=subject.subject_id):
                engine = self._engine_factory(suite.dimensions)
                report = engine.analyze(subject.build_intelligence_target())

        outcomes = tuple(_reconcile_dimension(check, report) for check in dimension_checks)
        outcome = ValidationIntelligenceOutcome.create(
            subject_id=subject.subject_id,
            plan_id=suite.plan_id,
            suite_id=suite.suite_id,
            policy_digest=suite.policy_digest,
            outcomes=outcomes,
            report=report,
        )
        _logger.info(
            "universal_assurance.validation_intelligence.completed",
            subject=subject.subject_id,
            verdict=outcome.verdict.value,
            dimensions=len(outcome.dimensions_analyzed),
            blocking_failed=len(outcome.blocking_failures()),
        )
        return outcome


def _default_intelligence_engine(
    dimensions: Iterable[IntelligenceDimension],
) -> ContinuousValidationIntelligenceEngine:
    """Compose the reused intelligence engine scoped to exactly the planned dimensions."""
    return ContinuousValidationIntelligenceEngine(dimensions=tuple(dimensions))


def _reconcile_dimension(
    check: Any, report: ValidationIntelligenceReport | None
) -> ObligationOutcome:
    """Reconcile one planned dimension obligation under the *policy's* severity."""
    if not check.bound:
        return ObligationOutcome.unmet(check, reason=check.unbound_reason or REASON_UNBOUND)
    if report is None:
        return ObligationOutcome.unmet(check, reason=REASON_NO_REPORT)
    dimension_report = next(
        (r for r in report.dimension_reports if r.dimension.value == check.ref), None
    )
    if dimension_report is None:
        return ObligationOutcome.unmet(check, reason=REASON_NOT_ANALYZED)
    failures = tuple(
        finding.check_id
        for finding in dimension_report.findings
        if finding.status is FindingStatus.FAIL
    )
    passed = not failures
    return ObligationOutcome(
        obligation_id=check.obligation_id,
        ref=check.ref,
        severity=check.policy_severity,
        outcome=Outcome.PASS if passed else Outcome.FAIL,
        executed=True,
        message=(
            f"dimension '{check.ref}' is clean"
            if passed
            else f"dimension '{check.ref}' has failing checks"
        ),
        implementation_status=dimension_report.verdict.value,
        details={"failing_checks": list(failures)},
    )


# --------------------------------------------------------------------------- #
# Certification Intelligence                                                   #
# --------------------------------------------------------------------------- #


class CertificationIntelligenceDimension(str, Enum):
    """The seven orthogonal dimensions of certification trustworthiness."""

    READINESS = "certification_readiness"
    CRITERIA_COVERAGE = "criteria_coverage"
    MEASUREMENT_COVERAGE = "measurement_coverage"
    EVIDENCE_INTEGRITY = "evidence_integrity"
    CERTIFICATE_INTEGRITY = "certificate_integrity"
    REGISTRY_INTEGRITY = "registry_integrity"
    REPRODUCIBILITY = "reproducibility"

    @property
    def order(self) -> int:
        return _CI_ORDER[self]


_CI_ORDER: dict[CertificationIntelligenceDimension, int] = {
    d: i for i, d in enumerate(CertificationIntelligenceDimension)
}


@dataclass(frozen=True, slots=True)
class CertificationFinding:
    """The immutable outcome of one certification-intelligence check."""

    check_id: str
    dimension: CertificationIntelligenceDimension
    severity: Severity
    outcome: Outcome
    message: str
    details: Mapping[str, Any] = field(default_factory=dict)

    @property
    def passed(self) -> bool:
        return self.outcome is Outcome.PASS

    @property
    def is_blocking_failure(self) -> bool:
        return self.outcome is Outcome.FAIL and self.severity is Severity.BLOCKING

    @property
    def is_advisory_failure(self) -> bool:
        return self.outcome is Outcome.FAIL and self.severity is Severity.ADVISORY

    def core(self) -> dict[str, Any]:
        return {
            "check_id": self.check_id,
            "dimension": self.dimension.value,
            "severity": self.severity.value,
            "outcome": self.outcome.value,
            "message": self.message,
        }

    def to_dict(self) -> dict[str, Any]:
        return {**self.core(), "details": dict(self.details)}


@dataclass(frozen=True, slots=True)
class CertificationIntelligenceInput:
    """Everything certification intelligence reasons over (a pure projection of the run)."""

    policy: AssurancePolicy
    subject: AssuranceSubject
    certification_plan: AssurancePlan
    validation_execution: ValidationExecution
    certification_execution: CertificationExecution
    measurement_report: MeasurementReport
    bundle: EvidenceBundle
    registry: CertificationRegistry
    reproducibility: ReproducibilityReport | None = None


@dataclass(frozen=True, slots=True)
class CertificationIntelligenceReport:
    """An immutable, content-addressed certification-trustworthiness determination."""

    intelligence_id: str
    subject_id: str
    policy_id: str
    policy_digest: str
    verdict: Verdict
    findings: tuple[CertificationFinding, ...]
    authority: str
    report_sha256: str

    @staticmethod
    def _core(
        *,
        subject_id: str,
        policy_id: str,
        policy_digest: str,
        verdict: Verdict,
        findings: tuple[CertificationFinding, ...],
        authority: str,
    ) -> dict[str, Any]:
        return {
            "intelligence_format": CERTIFICATION_INTELLIGENCE_FORMAT,
            "subject_id": subject_id,
            "policy_id": policy_id,
            "policy_digest": policy_digest,
            "verdict": verdict.value,
            "findings": [finding.core() for finding in findings],
            "authority": authority,
        }

    @classmethod
    def create(
        cls,
        *,
        subject_id: str,
        policy_id: str,
        policy_digest: str,
        findings: Iterable[CertificationFinding],
    ) -> CertificationIntelligenceReport:
        ordered = tuple(sorted(findings, key=lambda f: (f.dimension.order, f.check_id)))
        verdict = Verdict.FAIL if any(f.is_blocking_failure for f in ordered) else Verdict.PASS
        core = cls._core(
            subject_id=subject_id,
            policy_id=policy_id,
            policy_digest=policy_digest,
            verdict=verdict,
            findings=ordered,
            authority=ASSURANCE_AUTHORITY,
        )
        digest = content_hash(core)
        return cls(
            intelligence_id=f"UCOS-CINTEL-{digest[:16]}",
            subject_id=subject_id,
            policy_id=policy_id,
            policy_digest=policy_digest,
            verdict=verdict,
            findings=ordered,
            authority=ASSURANCE_AUTHORITY,
            report_sha256=digest,
        )

    @property
    def passed(self) -> bool:
        return self.verdict is Verdict.PASS

    def blocking_failures(self) -> tuple[str, ...]:
        return tuple(f.check_id for f in self.findings if f.is_blocking_failure)

    def advisory_failures(self) -> tuple[str, ...]:
        return tuple(f.check_id for f in self.findings if f.is_advisory_failure)

    def dimensions_run(self) -> tuple[str, ...]:
        seen: dict[str, None] = {}
        for finding in self.findings:
            seen.setdefault(finding.dimension.value, None)
        return tuple(seen)

    def dimension_verdicts(self) -> dict[str, str]:
        verdicts: dict[str, str] = {}
        for finding in self.findings:
            key = finding.dimension.value
            if finding.is_blocking_failure:
                verdicts[key] = Verdict.FAIL.value
            else:
                verdicts.setdefault(key, Verdict.PASS.value)
        return verdicts

    def readiness(self) -> float:
        """The passed/total finding ratio — the headline trustworthiness measure."""
        if not self.findings:
            return 0.0
        return sum(1 for f in self.findings if f.passed) / len(self.findings)

    def counts(self) -> dict[str, int]:
        return {
            "findings": len(self.findings),
            "passed": sum(1 for f in self.findings if f.passed),
            "failed": sum(1 for f in self.findings if not f.passed),
            "blocking_failed": len(self.blocking_failures()),
            "advisory_failed": len(self.advisory_failures()),
            "dimensions": len(self.dimensions_run()),
        }

    def observations(
        self, reproducibility: ReproducibilityReport | None = None
    ) -> dict[str, float]:
        counts = self.counts()
        byte_identical = 1.0 if (reproducibility and reproducibility.byte_identical) else 0.0
        return {
            "certification_intelligence.findings": float(counts["findings"]),
            "certification_intelligence.passed": float(counts["passed"]),
            "certification_intelligence.blocking_failures": float(counts["blocking_failed"]),
            "certification_intelligence.advisory_failures": float(counts["advisory_failed"]),
            "certification_intelligence.readiness": self.readiness(),
            "certification_intelligence.byte_identical": byte_identical,
        }

    def to_dict(self) -> dict[str, Any]:
        return {
            "intelligence_format": CERTIFICATION_INTELLIGENCE_FORMAT,
            "intelligence_id": self.intelligence_id,
            "subject_id": self.subject_id,
            "policy_id": self.policy_id,
            "policy_digest": self.policy_digest,
            "verdict": self.verdict.value,
            "passed": self.passed,
            "readiness": self.readiness(),
            "counts": self.counts(),
            "dimensions_run": list(self.dimensions_run()),
            "dimension_verdicts": self.dimension_verdicts(),
            "blocking_failures": list(self.blocking_failures()),
            "advisory_failures": list(self.advisory_failures()),
            "findings": [finding.to_dict() for finding in self.findings],
            "authority": self.authority,
            "report_sha256": self.report_sha256,
        }


def _finding(
    dimension: CertificationIntelligenceDimension,
    check_id: str,
    *,
    ok: bool,
    message: str,
    severity: Severity = Severity.BLOCKING,
    **details: Any,
) -> CertificationFinding:
    return CertificationFinding(
        check_id=check_id,
        dimension=dimension,
        severity=severity,
        outcome=Outcome.PASS if ok else Outcome.FAIL,
        message=message,
        details=details,
    )


class CertificationIntelligence:
    """**Certification Intelligence** — decides whether a certification is trustworthy."""

    __slots__ = ()

    def analyze(self, request: CertificationIntelligenceInput) -> CertificationIntelligenceReport:
        """Reason over the whole run and produce the trustworthiness determination."""
        if not isinstance(request, CertificationIntelligenceInput):
            raise AssuranceIntelligenceError(
                "certification intelligence requires a CertificationIntelligenceInput"
            )
        findings: list[CertificationFinding] = []
        findings.extend(self._readiness(request))
        findings.extend(self._criteria_coverage(request))
        findings.extend(self._measurement_coverage(request))
        findings.extend(self._evidence_integrity(request))
        findings.extend(self._certificate_integrity(request))
        findings.extend(self._registry_integrity(request))
        findings.extend(self._reproducibility(request))
        report = CertificationIntelligenceReport.create(
            subject_id=request.subject.subject_id,
            policy_id=request.policy.identity.id,
            policy_digest=request.policy.digest(),
            findings=findings,
        )
        _logger.info(
            "universal_assurance.certification_intelligence.completed",
            subject=request.subject.subject_id,
            verdict=report.verdict.value,
            readiness=report.readiness(),
            blocking_failed=len(report.blocking_failures()),
        )
        return report

    # -- dimensions ------------------------------------------------------------

    @staticmethod
    def _readiness(request: CertificationIntelligenceInput) -> tuple[CertificationFinding, ...]:
        dim = CertificationIntelligenceDimension.READINESS
        execution = request.certification_execution
        blocking = execution.blocking_failures()
        gates_failed = execution.gates_failed()
        return (
            _finding(
                dim,
                "certification_readiness.criteria-satisfied",
                ok=not blocking,
                message=(
                    "every blocking certification criterion is satisfied"
                    if not blocking
                    else "blocking certification criteria are unsatisfied"
                ),
                blocking_failures=list(blocking),
            ),
            _finding(
                dim,
                "certification_readiness.gates-passed",
                ok=not gates_failed,
                message=(
                    "every declared certification gate passed"
                    if not gates_failed
                    else "declared certification gates failed"
                ),
                gates_failed=list(gates_failed),
                gate_pass_ratio=execution.gate_pass_ratio(),
            ),
            _finding(
                dim,
                "certification_readiness.certified",
                ok=execution.certified,
                message=(
                    "the reused certifier issued a CERTIFIED decision"
                    if execution.certified
                    else "no CERTIFIED decision was issued"
                ),
                certification_id=execution.certification_id,
            ),
            _finding(
                dim,
                "certification_readiness.validation-accepted",
                ok=request.validation_execution.passed,
                message=(
                    "validation accepted the subject"
                    if request.validation_execution.passed
                    else "validation did not accept the subject"
                ),
                blocking_failures=list(request.validation_execution.blocking_failures()),
            ),
        )

    @staticmethod
    def _criteria_coverage(
        request: CertificationIntelligenceInput,
    ) -> tuple[CertificationFinding, ...]:
        dim = CertificationIntelligenceDimension.CRITERIA_COVERAGE
        plan = request.certification_plan
        execution = request.certification_execution
        planned_ids = set(plan.obligation_ids())
        evaluated = {o.obligation_id for o in execution.outcomes if o.executed}
        not_evaluated = tuple(sorted(planned_ids - evaluated))
        shortfalls = plan.blocking_shortfalls()
        return (
            _finding(
                dim,
                "criteria_coverage.plan-complete",
                ok=plan.coverage() >= 1.0,
                message=(
                    "every declared certification obligation was planned"
                    if plan.coverage() >= 1.0
                    else "the certification plan does not cover every declared obligation"
                ),
                coverage=plan.coverage(),
                declared=plan.declared_total,
                planned=len(plan.planned),
            ),
            _finding(
                dim,
                "criteria_coverage.plan-decidable",
                ok=not shortfalls,
                message=(
                    "every planned certification obligation is decidable"
                    if not shortfalls
                    else "planned certification obligations are undecidable"
                ),
                blocking_shortfalls=list(shortfalls),
            ),
            _finding(
                dim,
                "criteria_coverage.all-evaluated",
                ok=not not_evaluated,
                message=(
                    "every planned certification obligation was evaluated"
                    if not not_evaluated
                    else "planned certification obligations were never evaluated"
                ),
                not_evaluated=list(not_evaluated),
            ),
        )

    @staticmethod
    def _measurement_coverage(
        request: CertificationIntelligenceInput,
    ) -> tuple[CertificationFinding, ...]:
        dim = CertificationIntelligenceDimension.MEASUREMENT_COVERAGE
        report = request.measurement_report
        unobserved = report.unobserved()
        shortfalls = report.blocking_shortfalls()
        advisory = report.advisory_shortfalls()
        return (
            _finding(
                dim,
                "measurement_coverage.all-observed",
                ok=not unobserved,
                message=(
                    "every declared metric was observed"
                    if not unobserved
                    else "declared metrics were never observed"
                ),
                unobserved=list(unobserved),
                observation_coverage=report.observation_coverage(),
            ),
            _finding(
                dim,
                "measurement_coverage.blocking-satisfied",
                ok=not shortfalls,
                message=(
                    "every blocking metric is satisfied"
                    if not shortfalls
                    else "blocking metrics fell short of their thresholds"
                ),
                blocking_shortfalls=list(shortfalls),
            ),
            _finding(
                dim,
                "measurement_coverage.advisory-satisfied",
                ok=not advisory,
                message=(
                    "every advisory metric is satisfied"
                    if not advisory
                    else "advisory metrics fell short of their thresholds"
                ),
                severity=Severity.ADVISORY,
                advisory_shortfalls=list(advisory),
            ),
        )

    @staticmethod
    def _evidence_integrity(
        request: CertificationIntelligenceInput,
    ) -> tuple[CertificationFinding, ...]:
        dim = CertificationIntelligenceDimension.EVIDENCE_INTEGRITY
        bundle = request.bundle
        missing = bundle.missing_required()
        undeclared = bundle.undeclared()
        return (
            _finding(
                dim,
                "evidence_integrity.required-present",
                ok=not missing,
                message=(
                    "every policy-required evidence artifact is present"
                    if not missing
                    else "policy-required evidence artifacts are missing"
                ),
                missing=list(missing),
            ),
            _finding(
                dim,
                "evidence_integrity.manifest-intact",
                ok=bundle.manifest_intact,
                message=(
                    "every evidence digest recomputes"
                    if bundle.manifest_intact
                    else "an evidence digest does not match its payload"
                ),
                evidence_id=bundle.evidence_id,
                bundle_sha256=bundle.bundle_sha256,
            ),
            _finding(
                dim,
                "evidence_integrity.no-undeclared",
                ok=not undeclared,
                message=(
                    "every collected artifact is policy-declared"
                    if not undeclared
                    else "artifacts were collected that the policy never declared"
                ),
                severity=Severity.ADVISORY,
                undeclared=list(undeclared),
            ),
        )

    @staticmethod
    def _certificate_integrity(
        request: CertificationIntelligenceInput,
    ) -> tuple[CertificationFinding, ...]:
        dim = CertificationIntelligenceDimension.CERTIFICATE_INTEGRITY
        execution = request.certification_execution
        has_evidence = bool(execution.evidence_sha256)
        audited = bool(execution.audit_entries)
        return (
            _finding(
                dim,
                "certificate_integrity.content-hash-verifies",
                ok=execution.certificate_intact,
                message=(
                    "the certificate verifies against its own content hash"
                    if execution.certificate_intact
                    else "the certificate does not verify (absent or mutated)"
                ),
                certificate_sha256=execution.certificate_sha256,
            ),
            _finding(
                dim,
                "certificate_integrity.evidence-referenced",
                ok=has_evidence,
                message=(
                    "certification evidence is present and referenced"
                    if has_evidence
                    else "no certification evidence record was produced"
                ),
                evidence_sha256=execution.evidence_sha256,
            ),
            _finding(
                dim,
                "certificate_integrity.audit-trail",
                ok=audited,
                message=(
                    "the certification run left an audit trail"
                    if audited
                    else "the certification run left no audit trail"
                ),
                audit_entries=len(execution.audit_entries),
            ),
        )

    @staticmethod
    def _registry_integrity(
        request: CertificationIntelligenceInput,
    ) -> tuple[CertificationFinding, ...]:
        dim = CertificationIntelligenceDimension.REGISTRY_INTEGRITY
        registry = request.registry
        execution = request.certification_execution
        intact = registry.verify()
        registered = (
            execution.certification_id != ""
            and registry.get(execution.certification_id) is not None
        )
        drift = registry.policy_drift(request.policy.digest())
        return (
            _finding(
                dim,
                "registry_integrity.chain-verifies",
                ok=intact,
                message=(
                    "the certification registry hash chain verifies"
                    if intact
                    else "the certification registry hash chain is broken"
                ),
                registry_id=registry.registry_id,
                head_hash=registry.head_hash,
                entries=len(registry),
            ),
            _finding(
                dim,
                "registry_integrity.certification-registered",
                ok=registered,
                message=(
                    "the certification is registered and discoverable"
                    if registered
                    else "the certification is not registered"
                ),
                certification_id=execution.certification_id,
            ),
            _finding(
                dim,
                "registry_integrity.no-policy-drift",
                ok=not drift,
                message=(
                    "every registered certification was authorized by this policy text"
                    if not drift
                    else "registered certifications were authorized by a different policy text"
                ),
                severity=Severity.ADVISORY,
                drifted=list(drift),
            ),
        )

    @staticmethod
    def _reproducibility(
        request: CertificationIntelligenceInput,
    ) -> tuple[CertificationFinding, ...]:
        dim = CertificationIntelligenceDimension.REPRODUCIBILITY
        report = request.reproducibility
        required = request.policy.reproducibility.byte_identical_required
        if report is None:
            return (
                _finding(
                    dim,
                    "reproducibility.replays-byte-identical",
                    ok=not required,
                    message=(
                        "the policy requires byte identity but no replay was performed"
                        if required
                        else "the policy does not require byte identity"
                    ),
                    replays=0,
                ),
            )
        return (
            _finding(
                dim,
                "reproducibility.replays-byte-identical",
                ok=report.passed,
                message=(
                    f"{report.replays} replays are byte-identical"
                    if report.byte_identical
                    else "independent replays diverged"
                ),
                replays=report.replays,
                distinct_digests=list(report.distinct_digests),
            ),
            _finding(
                dim,
                "reproducibility.replay-count-met",
                ok=report.replays >= request.policy.reproducibility.replays,
                message=(
                    "the policy's replay count was met"
                    if report.replays >= request.policy.reproducibility.replays
                    else "fewer replays were performed than the policy requires"
                ),
                performed=report.replays,
                required=request.policy.reproducibility.replays,
            ),
        )


__all__ = [
    "VALIDATION_INTELLIGENCE_FORMAT",
    "CERTIFICATION_INTELLIGENCE_FORMAT",
    "REASON_NOT_ANALYZED",
    "REASON_UNBOUND",
    "REASON_NO_REPORT",
    "ValidationIntelligenceOutcome",
    "ValidationIntelligence",
    "CertificationIntelligenceDimension",
    "CertificationFinding",
    "CertificationIntelligenceInput",
    "CertificationIntelligenceReport",
    "CertificationIntelligence",
]
