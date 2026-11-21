"""UCOS-EPIC-014 — Validation Execution (Terminal T7).

The fourth owned capability. **Validation Execution** runs a
:class:`~platform.universal_assurance.generation.GeneratedSuite` on the **reused**
:class:`~platform.universal_validation.engine.UniversalValidationEngine` and then
*reconciles* every raw rule result back to the policy obligation that demanded it.

This package contributes **no rule runtime of its own**: the engine, the rules, the
domain aggregation, the content-addressed report and the evidence record all come from
:mod:`platform.universal_validation` (the mission's reuse mandate). What this capability
adds — and what the reused executor cannot know — is the *policy binding*:

    * **Obligation reconciliation.** Every planned, bound obligation is matched to the
      rule result for its ref. An obligation whose rule did not execute is recorded as a
      fail-closed ``not-executed`` failure, never as a pass.
    * **Policy severity governs.** The reused rule carries its own severity; the policy
      carries the *authoritative* one. Where they diverge, the policy wins — so a rule
      the platform ships as advisory can be enforced as blocking by policy without
      forking the implementation, and vice versa.
    * **Unbound obligations fail.** An obligation with no implementation, or one whose
      required facts were absent at planning time, is a blocking failure if the policy
      declared it blocking.
    * **Measurable & reproducible.** :meth:`ValidationExecution.observations` emits the
      numeric facts the policy's execution metrics decide, and the execution embeds no
      wall-clock, so an identical suite over an identical subject reproduces a
      byte-identical ``execution_sha256`` (IMP-007 §5).
"""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from dataclasses import dataclass, field
from platform.foundation.contracts import content_hash
from platform.universal_assurance.contracts import (
    AssuranceSubject,
    ObligationKind,
    Outcome,
    Severity,
    Verdict,
)
from platform.universal_assurance.errors import AssuranceExecutionError
from platform.universal_assurance.generation import GeneratedCheck, GeneratedSuite
from platform.universal_validation.contracts import (
    RuleResult,
    RuleStatus,
    ValidationReport,
)
from platform.universal_validation.engine import UniversalValidationEngine
from platform.universal_validation.evidence import (
    ValidationEvidence,
    build_validation_evidence,
)
from platform.universal_validation.rules import ValidationRule
from typing import Any

from engine.foundation.obs.logging import get_logger
from engine.foundation.obs.telemetry import trace

_logger = get_logger("universal_assurance.execution")

#: The validation-execution record format identifier.
EXECUTION_FORMAT = "ucos-assurance-validation-execution/1.0.0"

#: Fail-closed reconciliation reasons (recorded as data, never raised).
REASON_NOT_EXECUTED = "not-executed"
REASON_UNBOUND = "unbound"
REASON_NO_SUITE = "no-executable-suite"


@dataclass(frozen=True, slots=True)
class ObligationOutcome:
    """The reconciled, policy-governed outcome of one planned validation obligation."""

    obligation_id: str
    ref: str
    severity: Severity
    outcome: Outcome
    executed: bool
    message: str = ""
    implementation_status: str = ""
    details: Mapping[str, Any] = field(default_factory=dict)

    @classmethod
    def from_result(
        cls, check: GeneratedCheck, result: RuleResult, *, severity: Severity
    ) -> ObligationOutcome:
        """Reconcile a reused rule result under the *policy's* severity."""
        return cls(
            obligation_id=check.obligation_id,
            ref=check.ref,
            severity=severity,
            outcome=Outcome.PASS if result.status is RuleStatus.PASS else Outcome.FAIL,
            executed=True,
            message=result.message,
            implementation_status=result.status.value,
            details=dict(result.details),
        )

    @classmethod
    def unmet(cls, check: GeneratedCheck, *, reason: str, message: str = "") -> ObligationOutcome:
        """Record a fail-closed outcome for an obligation that could not be decided."""
        return cls(
            obligation_id=check.obligation_id,
            ref=check.ref,
            severity=check.policy_severity,
            outcome=Outcome.FAIL,
            executed=False,
            message=message or f"obligation {check.obligation_id} was not decided ({reason})",
            implementation_status=reason,
        )

    @property
    def passed(self) -> bool:
        return self.outcome is Outcome.PASS

    @property
    def is_blocking_failure(self) -> bool:
        return self.outcome is Outcome.FAIL and self.severity is Severity.BLOCKING

    @property
    def is_advisory_failure(self) -> bool:
        return self.outcome is Outcome.FAIL and self.severity is Severity.ADVISORY

    @property
    def severity_escalated(self) -> bool:
        """True iff the policy enforced a stricter verdict than the implementation."""
        return (
            self.executed
            and self.severity is Severity.BLOCKING
            and self.implementation_status == RuleStatus.FAIL.value
        )

    def core(self) -> dict[str, Any]:
        return {
            "obligation_id": self.obligation_id,
            "ref": self.ref,
            "severity": self.severity.value,
            "outcome": self.outcome.value,
            "executed": self.executed,
            "implementation_status": self.implementation_status,
            "message": self.message,
        }

    def to_dict(self) -> dict[str, Any]:
        return {**self.core(), "details": dict(self.details)}


@dataclass(frozen=True, slots=True)
class ValidationExecution:
    """An immutable, content-addressed record of one policy-governed validation run."""

    execution_id: str
    subject_id: str
    plan_id: str
    suite_id: str
    policy_digest: str
    verdict: Verdict
    outcomes: tuple[ObligationOutcome, ...]
    rules_executed: tuple[str, ...]
    report: ValidationReport | None
    report_sha256: str
    domain_verdicts: Mapping[str, str]
    execution_sha256: str

    @staticmethod
    def _core(
        *,
        subject_id: str,
        plan_id: str,
        suite_id: str,
        policy_digest: str,
        verdict: Verdict,
        outcomes: tuple[ObligationOutcome, ...],
        rules_executed: tuple[str, ...],
        report_sha256: str,
        domain_verdicts: Mapping[str, str],
    ) -> dict[str, Any]:
        return {
            "execution_format": EXECUTION_FORMAT,
            "subject_id": subject_id,
            "plan_id": plan_id,
            "suite_id": suite_id,
            "policy_digest": policy_digest,
            "verdict": verdict.value,
            "outcomes": [outcome.core() for outcome in outcomes],
            "rules_executed": list(rules_executed),
            "report_sha256": report_sha256,
            "domain_verdicts": dict(domain_verdicts),
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
        report: ValidationReport | None,
    ) -> ValidationExecution:
        """Aggregate reconciled outcomes into a content-addressed execution record.

        The verdict is fail-closed and **policy-governed**: FAIL iff any obligation the
        *policy* marked blocking did not pass.
        """
        ordered = tuple(sorted(outcomes, key=lambda o: (o.ref, o.obligation_id)))
        verdict = Verdict.FAIL if any(o.is_blocking_failure for o in ordered) else Verdict.PASS
        rules_executed = tuple(
            sorted({r.rule_id for r in (report.all_results if report is not None else ())})
        )
        report_sha256 = report.report_sha256 if report is not None else ""
        domain_verdicts = report.domain_verdicts() if report is not None else {}
        core = cls._core(
            subject_id=subject_id,
            plan_id=plan_id,
            suite_id=suite_id,
            policy_digest=policy_digest,
            verdict=verdict,
            outcomes=ordered,
            rules_executed=rules_executed,
            report_sha256=report_sha256,
            domain_verdicts=domain_verdicts,
        )
        digest = content_hash(core)
        return cls(
            execution_id=f"UCOS-VEXEC-{digest[:16]}",
            subject_id=subject_id,
            plan_id=plan_id,
            suite_id=suite_id,
            policy_digest=policy_digest,
            verdict=verdict,
            outcomes=ordered,
            rules_executed=rules_executed,
            report=report,
            report_sha256=report_sha256,
            domain_verdicts=domain_verdicts,
            execution_sha256=digest,
        )

    # -- derived, measurable properties ----------------------------------------

    @property
    def passed(self) -> bool:
        return self.verdict is Verdict.PASS

    def blocking_failures(self) -> tuple[str, ...]:
        return tuple(o.obligation_id for o in self.outcomes if o.is_blocking_failure)

    def advisory_failures(self) -> tuple[str, ...]:
        return tuple(o.obligation_id for o in self.outcomes if o.is_advisory_failure)

    def not_executed(self) -> tuple[str, ...]:
        return tuple(o.obligation_id for o in self.outcomes if not o.executed)

    def satisfied(self) -> tuple[str, ...]:
        return tuple(o.obligation_id for o in self.outcomes if o.passed)

    def obligation_coverage(self) -> float:
        """The executed/planned obligation ratio (1.0 when nothing was planned)."""
        if not self.outcomes:
            return 1.0
        return sum(1 for o in self.outcomes if o.executed) / len(self.outcomes)

    def evidence(self) -> ValidationEvidence | None:
        """The reused Validation Evidence Record for the run (``None`` without a report)."""
        if self.report is None:
            return None
        return build_validation_evidence(self.report)

    def checks_run(self, *, disclosure_rule: str, disclosure_check_id: str) -> tuple[str, ...]:
        """The check ids the reused certifier consumes, in canonical order.

        The reused certification engine proves the EC-1 disclosure by looking for a
        *named* check id. The mapping from this platform's disclosure rule id to that
        check id is declared in the policy's ``bindings`` — never hardcoded here — so the
        certifier's contract is satisfied without either side knowing the other's ids.
        """
        ids = set(self.rules_executed)
        if disclosure_rule in ids and disclosure_rule not in self.failed_refs():
            ids.add(disclosure_check_id)
        return tuple(sorted(ids))

    def failed_refs(self) -> tuple[str, ...]:
        """The refs of obligations that did not pass (policy-governed)."""
        return tuple(sorted({o.ref for o in self.outcomes if not o.passed}))

    def blocking_failed_refs(self) -> tuple[str, ...]:
        return tuple(sorted({o.ref for o in self.outcomes if o.is_blocking_failure}))

    def counts(self) -> dict[str, int]:
        return {
            "obligations": len(self.outcomes),
            "satisfied": len(self.satisfied()),
            "unsatisfied": len(self.outcomes) - len(self.satisfied()),
            "executed": sum(1 for o in self.outcomes if o.executed),
            "not_executed": len(self.not_executed()),
            "blocking_failed": len(self.blocking_failures()),
            "advisory_failed": len(self.advisory_failures()),
            "rules_executed": len(self.rules_executed),
        }

    def observations(self) -> dict[str, float]:
        """The numeric facts the policy's execution metrics are evaluated against."""
        counts = self.counts()
        return {
            "execution.obligations": float(counts["obligations"]),
            "execution.satisfied": float(counts["satisfied"]),
            "execution.executed": float(counts["executed"]),
            "execution.not_executed": float(counts["not_executed"]),
            "execution.obligation_coverage": self.obligation_coverage(),
            "execution.blocking_failures": float(counts["blocking_failed"]),
            "execution.advisory_failures": float(counts["advisory_failed"]),
            "execution.rules_executed": float(counts["rules_executed"]),
        }

    def failure_reasons(self) -> dict[str, str]:
        """A map of ``obligation id -> reason`` for every unmet obligation (for gates)."""
        return {
            o.obligation_id: o.implementation_status or o.outcome.value
            for o in self.outcomes
            if not o.passed
        }

    def to_dict(self) -> dict[str, Any]:
        return {
            "execution_format": EXECUTION_FORMAT,
            "execution_id": self.execution_id,
            "subject_id": self.subject_id,
            "plan_id": self.plan_id,
            "suite_id": self.suite_id,
            "policy_digest": self.policy_digest,
            "verdict": self.verdict.value,
            "passed": self.passed,
            "counts": self.counts(),
            "obligation_coverage": self.obligation_coverage(),
            "domain_verdicts": dict(self.domain_verdicts),
            "rules_executed": list(self.rules_executed),
            "blocking_failures": list(self.blocking_failures()),
            "advisory_failures": list(self.advisory_failures()),
            "not_executed": list(self.not_executed()),
            "outcomes": [o.to_dict() for o in self.outcomes],
            "report_sha256": self.report_sha256,
            "report": self.report.to_dict() if self.report is not None else None,
            "observations": self.observations(),
            "execution_sha256": self.execution_sha256,
        }


class ValidationExecutor:
    """**Validation Execution** — runs a generated suite on the reused engine."""

    __slots__ = ("_engine_factory",)

    def __init__(self, engine_factory: Any = None) -> None:
        """``engine_factory`` builds the reused engine from a rule tuple (test seam)."""
        self._engine_factory = engine_factory or _default_engine_factory

    def execute(self, suite: GeneratedSuite, subject: AssuranceSubject) -> ValidationExecution:
        """Execute ``suite`` over ``subject`` and reconcile results to obligations."""
        if not isinstance(suite, GeneratedSuite):
            raise AssuranceExecutionError("validation execution requires a GeneratedSuite")
        if not isinstance(subject, AssuranceSubject):
            raise AssuranceExecutionError("validation execution requires an AssuranceSubject")

        rule_checks = tuple(
            check for check in suite.checks if check.kind is ObligationKind.VALIDATION_RULE
        )
        report: ValidationReport | None = None
        if suite.rules:
            with trace("universal_assurance.validation_execution", subject=subject.subject_id):
                engine = self._engine_factory(suite.rules)
                report = engine.validate(subject.build_validation_target())

        results_by_ref: dict[str, RuleResult] = {}
        if report is not None:
            for result in report.all_results:
                results_by_ref[result.rule_id] = result

        outcomes: list[ObligationOutcome] = []
        for check in rule_checks:
            if not check.bound:
                outcomes.append(
                    ObligationOutcome.unmet(
                        check,
                        reason=check.unbound_reason or REASON_UNBOUND,
                        message=(
                            f"obligation {check.obligation_id} has no bound implementation "
                            f"({check.unbound_reason or REASON_UNBOUND})"
                        ),
                    )
                )
                continue
            result = results_by_ref.get(check.ref)
            if result is None:
                reason = REASON_NO_SUITE if report is None else REASON_NOT_EXECUTED
                outcomes.append(ObligationOutcome.unmet(check, reason=reason))
                continue
            outcomes.append(
                ObligationOutcome.from_result(check, result, severity=check.policy_severity)
            )

        execution = ValidationExecution.create(
            subject_id=subject.subject_id,
            plan_id=suite.plan_id,
            suite_id=suite.suite_id,
            policy_digest=suite.policy_digest,
            outcomes=outcomes,
            report=report,
        )
        _logger.info(
            "universal_assurance.validation_execution.completed",
            subject=subject.subject_id,
            verdict=execution.verdict.value,
            obligations=len(execution.outcomes),
            blocking_failed=len(execution.blocking_failures()),
        )
        return execution


def _default_engine_factory(rules: Iterable[ValidationRule]) -> UniversalValidationEngine:
    """Compose the reused Universal Validation Engine over exactly the generated rules."""
    return UniversalValidationEngine(tuple(rules))


__all__ = [
    "EXECUTION_FORMAT",
    "REASON_NOT_EXECUTED",
    "REASON_UNBOUND",
    "REASON_NO_SUITE",
    "ObligationOutcome",
    "ValidationExecution",
    "ValidationExecutor",
]
