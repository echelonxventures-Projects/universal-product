"""UCOS-EPIC-014 — Certification Execution & Certification Evidence (Terminal T7).

Two more owned capabilities. **Certification Execution** runs the policy-derived
certification plan on the **reused**
:class:`~engine.universal_certification.pipeline.CertificationPipeline`, and
**Certification Evidence** is the deterministic record that pipeline emits, captured here
and bound back to the policy obligations that authorized it.

This package issues no certificate of its own and re-judges nothing. The certificate, the
hash-chained approval workflow, the append-only audit ledger, the compliance engine and
the ten certification rules all come from :mod:`engine.universal_certification`. What this
capability adds is everything the reused certifier cannot know:

    * **Input adaptation.** The reused certifier consumes a ``ValidationInput`` /
      ``MeasurementInput`` / ``RepositoryTruthInput`` triple. Those are projected here from
      the policy-governed :class:`~platform.universal_assurance.execution.ValidationExecution`,
      the :class:`~platform.universal_assurance.measurement.MeasurementReport`, and the
      subject's repository-truth attestation — so the two engines meet without either
      knowing the other's identifiers.
    * **Declared disclosure binding.** The certifier proves the EC-1 disclosure by looking
      for a *named* check id; the mapping from this platform's disclosure rule to that check
      id is read from the policy's ``bindings`` block, never hardcoded.
    * **Criterion reconciliation + policy severity.** Every certification finding is matched
      back to the obligation that demanded it, under the *policy's* severity.
    * **Gate evaluation.** The policy's gates are evaluated over the reconciled outcomes; a
      certificate that fails a declared gate closes the certification stage even if the
      reused rule suite alone would have passed.

Fail-closed throughout: an unbindable criterion, a malformed repository-truth attestation,
or a missing validation evidence record yields recorded blocking failures and no
certification — never a silent pass. Reproducible throughout: an identical plan over an
identical execution reproduces a byte-identical ``execution_sha256`` (IMP-007 §5).
"""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from platform.foundation.contracts import content_hash
from platform.universal_assurance.contracts import (
    AssuranceSubject,
    ObligationKind,
    Outcome,
    Severity,
    Verdict,
)
from platform.universal_assurance.errors import AssuranceExecutionError
from platform.universal_assurance.execution import ObligationOutcome, ValidationExecution
from platform.universal_assurance.measurement import MeasurementReport
from platform.universal_assurance.planning import (
    REASON_UNSATISFIABLE as PLAN_REASON_UNSATISFIABLE,
)
from platform.universal_assurance.planning import AssurancePlan, gate_outcomes
from platform.universal_assurance.policy import AssurancePolicy
from typing import Any

from engine.foundation.obs.logging import get_logger
from engine.foundation.obs.telemetry import trace
from engine.universal_certification.audit import CertificationAuditLedger
from engine.universal_certification.compliance import ComplianceFrame, default_frames
from engine.universal_certification.contracts import (
    CertificationClass,
    RepositoryTruthInput,
    RuleStatus,
    UniversalCertificationSubject,
    ValidationInput,
)
from engine.universal_certification.engine import (
    CertificationDecision,
    UniversalCertificationEngine,
)
from engine.universal_certification.errors import UniversalCertificationError
from engine.universal_certification.pipeline import CertificationPipeline
from engine.universal_certification.rules import CertificationRule, default_rules

_logger = get_logger("universal_assurance.certification")

#: The certification-execution record format identifier.
CERTIFICATION_EXECUTION_FORMAT = "ucos-assurance-certification-execution/1.0.0"

#: Fail-closed reconciliation reasons (recorded as data, never raised).
REASON_UNKNOWN_CRITERION = "unknown-certification-criterion"
REASON_UNKNOWN_FRAME = "unknown-certification-frame"
#: Reused from planning: the same condition must not carry two spellings.
REASON_UNSATISFIABLE = PLAN_REASON_UNSATISFIABLE
REASON_NOT_EVALUATED = "not-evaluated"
REASON_NO_DECISION = "no-certification-decision"
REASON_MALFORMED_REPOSITORY_TRUTH = "malformed-repository-truth"


class CriterionCatalog:
    """A read-only index of the reused certification rules and compliance frames."""

    __slots__ = ("_rules", "_frames")

    def __init__(
        self,
        rules: Iterable[CertificationRule] | None = None,
        *,
        frames: Iterable[ComplianceFrame] | None = None,
    ) -> None:
        self._rules = {
            rule.rule_id: rule for rule in (tuple(rules) if rules is not None else default_rules())
        }
        self._frames = {
            frame.frame_id: frame
            for frame in (tuple(frames) if frames is not None else default_frames())
        }

    @property
    def rule_ids(self) -> tuple[str, ...]:
        return tuple(sorted(self._rules))

    @property
    def frame_ids(self) -> tuple[str, ...]:
        return tuple(sorted(self._frames))

    def rule(self, ref: str) -> CertificationRule | None:
        return self._rules.get(ref)

    def frame(self, ref: str) -> ComplianceFrame | None:
        return self._frames.get(ref)

    def to_dict(self) -> dict[str, Any]:
        return {"rules": list(self.rule_ids), "frames": list(self.frame_ids)}


def build_validation_input(
    *,
    subject: AssuranceSubject,
    execution: ValidationExecution,
    policy: AssurancePolicy,
) -> ValidationInput:
    """Project the policy-governed validation execution onto the reused certifier's input.

    ``counts`` is expressed in the reused certifier's vocabulary (``total`` / ``passed`` /
    ``failed``) so its advisory ``validation-complete`` rule reads the *obligation*
    outcomes — the policy-governed truth — rather than raw rule results.
    """
    evidence = execution.evidence()
    evidence_sha256 = content_hash(evidence.to_dict()) if evidence is not None else ""
    counts = execution.counts()
    return ValidationInput(
        target_id=subject.subject_id,
        blueprint_id=subject.blueprint_id,
        verdict=execution.verdict.value,
        accepted=execution.passed,
        checks_run=execution.checks_run(
            disclosure_rule=policy.binding("disclosure_rule"),
            disclosure_check_id=policy.binding("disclosure_check_id"),
        ),
        blocking_failures=execution.blocking_failed_refs(),
        counts={
            "total": counts["obligations"],
            "passed": counts["satisfied"],
            "failed": counts["unsatisfied"],
            "blocking_failed": counts["blocking_failed"],
            "advisory_failed": counts["advisory_failed"],
        },
        evidence_present=evidence is not None,
        evidence_sha256=evidence_sha256,
    )


def build_repository_truth_input(subject: AssuranceSubject) -> RepositoryTruthInput | None:
    """Project the subject's repository-truth attestation, or ``None`` when malformed.

    A malformed attestation is reported as data (``None`` → recorded blocking failures),
    never as a swallowed exception and never as a pass.
    """
    raw = subject.repository_truth
    if not isinstance(raw, Mapping) or not raw:
        return None
    gaps = raw.get("gaps") or {}
    if not isinstance(gaps, Mapping):
        return None
    try:
        return RepositoryTruthInput.create(
            snapshot_id=str(raw.get("snapshot_id", "")),
            content_sha256=str(raw.get("content_sha256", "")),
            total_concepts=raw.get("total_concepts", 0),
            homed_concepts=raw.get("homed_concepts", 0),
            gaps=dict(gaps),
            closed=bool(raw.get("closed", False)),
        )
    except UniversalCertificationError:
        return None


@dataclass(frozen=True, slots=True)
class CertificationExecution:
    """An immutable, content-addressed record of one policy-governed certification run."""

    execution_id: str
    subject_id: str
    plan_id: str
    policy_digest: str
    verdict: Verdict
    certified: bool
    certification_id: str
    certificate_sha256: str
    certificate_intact: bool
    outcomes: tuple[ObligationOutcome, ...]
    gates: tuple[Mapping[str, Any], ...]
    decision: CertificationDecision | None
    evidence_sha256: str
    evidence_payload: Mapping[str, Any]
    audit_entries: tuple[Mapping[str, Any], ...]
    execution_sha256: str

    @staticmethod
    def _core(
        *,
        subject_id: str,
        plan_id: str,
        policy_digest: str,
        verdict: Verdict,
        certified: bool,
        certification_id: str,
        certificate_sha256: str,
        certificate_intact: bool,
        outcomes: tuple[ObligationOutcome, ...],
        gates: tuple[Mapping[str, Any], ...],
        evidence_sha256: str,
    ) -> dict[str, Any]:
        return {
            "execution_format": CERTIFICATION_EXECUTION_FORMAT,
            "subject_id": subject_id,
            "plan_id": plan_id,
            "policy_digest": policy_digest,
            "verdict": verdict.value,
            "certified": certified,
            "certification_id": certification_id,
            "certificate_sha256": certificate_sha256,
            "certificate_intact": certificate_intact,
            "outcomes": [outcome.core() for outcome in outcomes],
            "gates": [dict(gate) for gate in gates],
            "evidence_sha256": evidence_sha256,
        }

    @classmethod
    def create(
        cls,
        *,
        subject_id: str,
        plan_id: str,
        policy_digest: str,
        outcomes: Iterable[ObligationOutcome],
        gates: Iterable[Mapping[str, Any]],
        decision: CertificationDecision | None,
        evidence_sha256: str = "",
        evidence_payload: Mapping[str, Any] | None = None,
        audit_entries: Iterable[Mapping[str, Any]] = (),
    ) -> CertificationExecution:
        """Aggregate reconciled criteria and gates into a content-addressed record.

        The verdict is fail-closed and **policy-governed**: FAIL iff any blocking
        obligation failed, any declared gate failed, or no certification was issued.
        """
        ordered = tuple(sorted(outcomes, key=lambda o: (o.ref, o.obligation_id)))
        gate_records = tuple(gates)
        certificate = decision.certificate if decision is not None else None
        certified = bool(decision is not None and decision.certified)
        intact = bool(certificate is not None and certificate.verify_integrity())
        gates_failed = any(not gate.get("passed", False) for gate in gate_records)
        blocking = any(o.is_blocking_failure for o in ordered)
        verdict = (
            Verdict.FAIL
            if (blocking or gates_failed or not certified or not intact)
            else Verdict.PASS
        )
        core = cls._core(
            subject_id=subject_id,
            plan_id=plan_id,
            policy_digest=policy_digest,
            verdict=verdict,
            certified=certified,
            certification_id=certificate.certification_id if certificate is not None else "",
            certificate_sha256=certificate.content_sha256 if certificate is not None else "",
            certificate_intact=intact,
            outcomes=ordered,
            gates=gate_records,
            evidence_sha256=evidence_sha256,
        )
        digest = content_hash(core)
        return cls(
            execution_id=f"UCOS-CEXEC-{digest[:16]}",
            subject_id=subject_id,
            plan_id=plan_id,
            policy_digest=policy_digest,
            verdict=verdict,
            certified=certified,
            certification_id=certificate.certification_id if certificate is not None else "",
            certificate_sha256=certificate.content_sha256 if certificate is not None else "",
            certificate_intact=intact,
            outcomes=ordered,
            gates=gate_records,
            decision=decision,
            evidence_sha256=evidence_sha256,
            evidence_payload=dict(evidence_payload or {}),
            audit_entries=tuple(dict(entry) for entry in audit_entries),
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

    def satisfied(self) -> tuple[str, ...]:
        return tuple(o.obligation_id for o in self.outcomes if o.passed)

    def gates_failed(self) -> tuple[str, ...]:
        return tuple(str(gate["gate_id"]) for gate in self.gates if not gate.get("passed", False))

    def gate_pass_ratio(self) -> float:
        """The passed/declared gate ratio (1.0 when the plan declares no gate)."""
        if not self.gates:
            return 1.0
        passed = sum(1 for gate in self.gates if gate.get("passed", False))
        return passed / len(self.gates)

    def counts(self) -> dict[str, int]:
        return {
            "obligations": len(self.outcomes),
            "satisfied": len(self.satisfied()),
            "unsatisfied": len(self.outcomes) - len(self.satisfied()),
            "blocking_failed": len(self.blocking_failures()),
            "advisory_failed": len(self.advisory_failures()),
            "gates": len(self.gates),
            "gates_failed": len(self.gates_failed()),
            "audit_entries": len(self.audit_entries),
        }

    def observations(self) -> dict[str, float]:
        """The numeric facts the policy's certification metrics are evaluated against."""
        counts = self.counts()
        return {
            "certification.obligations": float(counts["obligations"]),
            "certification.satisfied": float(counts["satisfied"]),
            "certification.blocking_failures": float(counts["blocking_failed"]),
            "certification.advisory_failures": float(counts["advisory_failed"]),
            "certification.gate_pass_ratio": self.gate_pass_ratio(),
            "certification.certified": 1.0 if self.certified else 0.0,
            "certification_evidence.certificate_intact": 1.0 if self.certificate_intact else 0.0,
            "certification_evidence.audit_entries": float(counts["audit_entries"]),
        }

    def failure_reasons(self) -> dict[str, str]:
        return {
            o.obligation_id: o.implementation_status or o.outcome.value
            for o in self.outcomes
            if not o.passed
        }

    def to_dict(self) -> dict[str, Any]:
        return {
            "execution_format": CERTIFICATION_EXECUTION_FORMAT,
            "execution_id": self.execution_id,
            "subject_id": self.subject_id,
            "plan_id": self.plan_id,
            "policy_digest": self.policy_digest,
            "verdict": self.verdict.value,
            "passed": self.passed,
            "certified": self.certified,
            "certification_id": self.certification_id,
            "certificate_sha256": self.certificate_sha256,
            "certificate_intact": self.certificate_intact,
            "counts": self.counts(),
            "gate_pass_ratio": self.gate_pass_ratio(),
            "blocking_failures": list(self.blocking_failures()),
            "advisory_failures": list(self.advisory_failures()),
            "gates": [dict(gate) for gate in self.gates],
            "outcomes": [o.to_dict() for o in self.outcomes],
            "decision": self.decision.to_dict() if self.decision is not None else None,
            "evidence_sha256": self.evidence_sha256,
            "evidence": dict(self.evidence_payload),
            "audit_entries": [dict(entry) for entry in self.audit_entries],
            "observations": self.observations(),
            "execution_sha256": self.execution_sha256,
        }


class CertificationExecutor:
    """**Certification Execution** — runs the certification plan on the reused pipeline."""

    __slots__ = ("_policy", "_catalog")

    def __init__(
        self,
        policy: AssurancePolicy,
        *,
        catalog: CriterionCatalog | None = None,
    ) -> None:
        if not isinstance(policy, AssurancePolicy):
            raise AssuranceExecutionError("certification execution requires an AssurancePolicy")
        self._policy = policy
        self._catalog = catalog if catalog is not None else CriterionCatalog()

    @property
    def policy(self) -> AssurancePolicy:
        return self._policy

    @property
    def catalog(self) -> CriterionCatalog:
        return self._catalog

    def execute(
        self,
        *,
        plan: AssurancePlan,
        subject: AssuranceSubject,
        validation_execution: ValidationExecution,
        measurement_report: MeasurementReport,
    ) -> CertificationExecution:
        """Certify ``subject`` under ``plan``, reconciling findings to obligations."""
        self._require_inputs(plan, subject, validation_execution, measurement_report)

        bound_rules, bound_frames, unbound = self._bind(plan)
        truth = build_repository_truth_input(subject)
        if truth is None:
            return self._malformed_truth(plan)

        decision, evidence_sha256, evidence_payload, audit_entries = self._run_pipeline(
            subject=subject,
            validation_execution=validation_execution,
            measurement_report=measurement_report,
            truth=truth,
            rules=bound_rules,
            frames=bound_frames,
        )
        outcomes = self._reconcile(plan, decision, unbound)
        failure_reasons = {
            o.obligation_id: o.implementation_status or o.outcome.value
            for o in outcomes
            if not o.passed
        }
        execution = CertificationExecution.create(
            subject_id=subject.subject_id,
            plan_id=plan.plan_id,
            policy_digest=plan.policy_digest,
            outcomes=outcomes,
            gates=gate_outcomes(plan, failure_reasons),
            decision=decision,
            evidence_sha256=evidence_sha256,
            evidence_payload=evidence_payload,
            audit_entries=audit_entries,
        )
        _logger.info(
            "universal_assurance.certification_execution.completed",
            subject=subject.subject_id,
            verdict=execution.verdict.value,
            certified=execution.certified,
            blocking_failed=len(execution.blocking_failures()),
        )
        return execution

    # -- internals -------------------------------------------------------------

    @staticmethod
    def _require_inputs(
        plan: AssurancePlan,
        subject: AssuranceSubject,
        validation_execution: ValidationExecution,
        measurement_report: MeasurementReport,
    ) -> None:
        if not isinstance(plan, AssurancePlan):
            raise AssuranceExecutionError("certification execution requires an AssurancePlan")
        if not isinstance(subject, AssuranceSubject):
            raise AssuranceExecutionError("certification execution requires an AssuranceSubject")
        if not isinstance(validation_execution, ValidationExecution):
            raise AssuranceExecutionError("certification execution requires a ValidationExecution")
        if not isinstance(measurement_report, MeasurementReport):
            raise AssuranceExecutionError("certification execution requires a MeasurementReport")

    def _bind(
        self, plan: AssurancePlan
    ) -> tuple[tuple[CertificationRule, ...], tuple[ComplianceFrame, ...], dict[str, str]]:
        """Resolve planned criteria/frames against the reused catalogue (fail-closed)."""
        rules: dict[str, CertificationRule] = {}
        frames: dict[str, ComplianceFrame] = {}
        unbound: dict[str, str] = {}
        for item in plan.planned:
            obligation = item.obligation
            if obligation.kind is ObligationKind.CERTIFICATION_CRITERION:
                if not item.satisfiable:
                    unbound[obligation.id] = REASON_UNSATISFIABLE
                    continue
                rule = self._catalog.rule(obligation.ref)
                if rule is None:
                    unbound[obligation.id] = REASON_UNKNOWN_CRITERION
                    continue
                rules[rule.rule_id] = rule
            elif obligation.kind is ObligationKind.CERTIFICATION_FRAME:
                if not item.satisfiable:
                    unbound[obligation.id] = REASON_UNSATISFIABLE
                    continue
                frame = self._catalog.frame(obligation.ref)
                if frame is None:
                    unbound[obligation.id] = REASON_UNKNOWN_FRAME
                    continue
                frames[frame.frame_id] = frame
        return (
            tuple(rules[key] for key in sorted(rules)),
            tuple(frames[key] for key in sorted(frames)),
            unbound,
        )

    def _run_pipeline(
        self,
        *,
        subject: AssuranceSubject,
        validation_execution: ValidationExecution,
        measurement_report: MeasurementReport,
        truth: RepositoryTruthInput,
        rules: tuple[CertificationRule, ...],
        frames: tuple[ComplianceFrame, ...],
    ) -> tuple[CertificationDecision | None, str, Mapping[str, Any], tuple[Mapping[str, Any], ...]]:
        if not rules or not frames:
            return None, "", {}, ()
        certification_class = CertificationClass(self._policy.binding("certification_class"))
        certification_subject = UniversalCertificationSubject.create(
            validation=build_validation_input(
                subject=subject, execution=validation_execution, policy=self._policy
            ),
            measurement=measurement_report.to_measurement_input(
                source=self._policy.binding("measurement_source")
            ),
            repository_truth=truth,
            version=subject.version,
            target_id=subject.subject_id,
            blueprint_id=subject.blueprint_id,
            certification_class=certification_class,
        )
        pipeline = CertificationPipeline(
            UniversalCertificationEngine(rules=rules, frames=frames),
            audit=CertificationAuditLedger(),
        )
        with trace("universal_assurance.certification_execution", subject=subject.subject_id):
            outcome = pipeline.run(
                certification_subject,
                submitter=self._policy.binding("submitter"),
                auto_submit=True,
            )
        return (
            outcome.decision,
            outcome.evidence.content_sha256(),
            outcome.evidence.to_dict(),
            outcome.audit_entries,
        )

    def _reconcile(
        self,
        plan: AssurancePlan,
        decision: CertificationDecision | None,
        unbound: Mapping[str, str],
    ) -> tuple[ObligationOutcome, ...]:
        """Match every planned criterion/frame to its finding under the policy severity."""
        rule_findings = {
            finding.rule_id: finding
            for finding in (decision.findings if decision is not None else ())
        }
        frame_findings = {
            finding.frame_id: finding
            for finding in (decision.compliance.findings if decision is not None else ())
        }
        outcomes: list[ObligationOutcome] = []
        for item in plan.planned:
            obligation = item.obligation
            if obligation.kind not in (
                ObligationKind.CERTIFICATION_CRITERION,
                ObligationKind.CERTIFICATION_FRAME,
            ):
                continue
            reason = unbound.get(obligation.id)
            if reason is not None:
                outcomes.append(_unmet(obligation.id, obligation.ref, obligation.severity, reason))
                continue
            if decision is None:
                outcomes.append(
                    _unmet(obligation.id, obligation.ref, obligation.severity, REASON_NO_DECISION)
                )
                continue
            if obligation.kind is ObligationKind.CERTIFICATION_CRITERION:
                finding = rule_findings.get(obligation.ref)
                if finding is None:
                    outcomes.append(
                        _unmet(
                            obligation.id,
                            obligation.ref,
                            obligation.severity,
                            REASON_NOT_EVALUATED,
                        )
                    )
                    continue
                outcomes.append(
                    ObligationOutcome(
                        obligation_id=obligation.id,
                        ref=obligation.ref,
                        severity=obligation.severity,
                        outcome=(
                            Outcome.PASS if finding.status is RuleStatus.PASS else Outcome.FAIL
                        ),
                        executed=True,
                        message=finding.message,
                        implementation_status=finding.status.value,
                        details=dict(finding.details),
                    )
                )
                continue
            frame = frame_findings.get(obligation.ref)
            if frame is None:
                outcomes.append(
                    _unmet(obligation.id, obligation.ref, obligation.severity, REASON_NOT_EVALUATED)
                )
                continue
            outcomes.append(
                ObligationOutcome(
                    obligation_id=obligation.id,
                    ref=obligation.ref,
                    severity=obligation.severity,
                    outcome=Outcome.PASS if frame.conformant else Outcome.FAIL,
                    executed=True,
                    message=frame.message,
                    implementation_status=frame.status.value,
                    details=dict(frame.details),
                )
            )
        return tuple(outcomes)

    def _malformed_truth(self, plan: AssurancePlan) -> CertificationExecution:
        """Fail closed when the repository-truth attestation cannot be assimilated."""
        outcomes = tuple(
            _unmet(
                item.obligation.id,
                item.obligation.ref,
                item.obligation.severity,
                REASON_MALFORMED_REPOSITORY_TRUTH,
            )
            for item in plan.planned
            if item.obligation.kind
            in (ObligationKind.CERTIFICATION_CRITERION, ObligationKind.CERTIFICATION_FRAME)
        )
        failure_reasons = {o.obligation_id: o.implementation_status for o in outcomes}
        return CertificationExecution.create(
            subject_id=plan.subject_id,
            plan_id=plan.plan_id,
            policy_digest=plan.policy_digest,
            outcomes=outcomes,
            gates=gate_outcomes(plan, failure_reasons),
            decision=None,
        )


def _unmet(obligation_id: str, ref: str, severity: Severity, reason: str) -> ObligationOutcome:
    return ObligationOutcome(
        obligation_id=obligation_id,
        ref=ref,
        severity=severity,
        outcome=Outcome.FAIL,
        executed=False,
        message=f"certification obligation {obligation_id} was not decided ({reason})",
        implementation_status=reason,
    )


__all__ = [
    "CERTIFICATION_EXECUTION_FORMAT",
    "REASON_UNKNOWN_CRITERION",
    "REASON_UNKNOWN_FRAME",
    "REASON_UNSATISFIABLE",
    "REASON_NOT_EVALUATED",
    "REASON_NO_DECISION",
    "REASON_MALFORMED_REPOSITORY_TRUTH",
    "CriterionCatalog",
    "build_validation_input",
    "build_repository_truth_input",
    "CertificationExecution",
    "CertificationExecutor",
]
