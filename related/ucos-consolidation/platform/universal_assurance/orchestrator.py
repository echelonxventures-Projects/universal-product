"""UCOS-EPIC-014 — The ten-stage Universal Assurance orchestrator (Terminal T7).

One conductor runs all ten owned capabilities in the mission's order and produces a single
immutable :class:`AssuranceOutcome`::

    Validation Planning → Validation Generation → Validation Execution
        → Evidence Collection → Certification Planning → Certification Execution
        → Certification Evidence → Certification Registry
        → Validation Intelligence → Certification Intelligence

Three invariants shape the ordering, and each resolves a genuine circularity rather than
papering over one:

    * **Measurement is staged.** Certification consumes only the metrics measured *before*
      it ran (:func:`~platform.universal_assurance.measurement.metrics_before`, derived
      from the stage order — never enumerated). The full measurement report, covering every
      stage, is the artifact and drives the run verdict.
    * **Evidence spans the run.** Every stage contributes to one collector. A bundle can
      never contain an artifact that describes itself, so certification intelligence assesses
      the bundle scoped to the stages that finished before it, and the final bundle — which
      additionally carries the intelligence and reproducibility records — is the emitted one.
    * **The registry commits to what exists.** A registry entry references the certification
      evidence bundle as it stood at registration; the registry snapshot then becomes an
      artifact of the final bundle.

Reproducibility is proven, not asserted: the deterministic core (planning through
certification execution, on freshly composed objects) is replayed the number of times the
policy demands and the canonical bytes are compared.

Fail-closed throughout: the run verdict is FAIL if any stage recorded a blocking shortfall,
any declared gate failed, or any declared metric could not be measured. The outcome asserts
``ENGINEERING-EXECUTION-ONLY`` authority and carries the EC-1 provisional-state disclosure
(DE-05 / IP-01) — it records engineering readiness, never constitutional finality.
"""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from platform.foundation.contracts import content_hash
from platform.universal_assurance.certification import (
    CertificationExecution,
    CertificationExecutor,
)
from platform.universal_assurance.contracts import (
    AssuranceReport,
    AssuranceStage,
    AssuranceSubject,
    StageRecord,
)
from platform.universal_assurance.determinism import (
    ReproducibilityReport,
    verify_reproducibility,
)
from platform.universal_assurance.errors import AssuranceExecutionError
from platform.universal_assurance.evidence import (
    EvidenceBundle,
    EvidenceCollector,
    write_bundle,
)
from platform.universal_assurance.execution import ValidationExecution, ValidationExecutor
from platform.universal_assurance.generation import GeneratedSuite, SuiteGenerator
from platform.universal_assurance.intelligence import (
    CertificationIntelligence,
    CertificationIntelligenceInput,
    CertificationIntelligenceReport,
    ValidationIntelligence,
    ValidationIntelligenceOutcome,
)
from platform.universal_assurance.measurement import (
    MeasurementReport,
    measure,
    merge_observations,
    metrics_before,
    subject_observations,
)
from platform.universal_assurance.planning import (
    AssurancePlan,
    CertificationPlanner,
    ValidationPlanner,
    evaluate_gates,
)
from platform.universal_assurance.policy import AssurancePolicy, load_default_policy
from platform.universal_assurance.registry import CertificationRegistry, RegistryEntry
from platform.validation_intelligence.evidence import build_validation_intelligence_evidence
from typing import Any

from engine.foundation.obs.logging import get_logger

_logger = get_logger("universal_assurance.orchestrator")

#: The assurance outcome format identifier.
OUTCOME_FORMAT = "ucos-assurance-outcome/1.0.0"

#: The reproducibility label for the deterministic-core replay.
REPLAY_LABEL = "assurance-deterministic-core"


def stages_before(stage: AssuranceStage) -> tuple[AssuranceStage, ...]:
    """Every stage that precedes ``stage`` in canonical order (derived, not enumerated)."""
    return tuple(s for s in AssuranceStage if s.order < stage.order)


@dataclass(frozen=True, slots=True)
class DeterministicCore:
    """The pure, replayable part of an assurance run (planning → certification execution).

    Everything here is a function of the subject and the policy alone: no collector, no
    registry, no filesystem. Replaying it must reproduce identical bytes, which is exactly
    what :mod:`platform.universal_assurance.determinism` checks.
    """

    validation_plan: AssurancePlan
    suite: GeneratedSuite
    validation_execution: ValidationExecution
    validation_intelligence: ValidationIntelligenceOutcome
    certification_plan: AssurancePlan
    interim_measurement: MeasurementReport
    certification_execution: CertificationExecution

    def observations(self) -> dict[str, float]:
        """Every observation the core stages published, merged deterministically."""
        return merge_observations(
            self.validation_plan.observations(),
            self.suite.observations(),
            self.validation_execution.observations(),
            self.validation_intelligence.observations(),
            self.certification_plan.observations(),
            self.certification_execution.observations(),
        )

    def payload(self) -> dict[str, Any]:
        """The canonical replay payload compared byte-for-byte across replays."""
        return {
            "validation_plan": self.validation_plan.to_dict(),
            "validation_suite": self.suite.to_dict(),
            "validation_execution": self.validation_execution.to_dict(),
            "validation_intelligence": self.validation_intelligence.to_dict(),
            "certification_plan": self.certification_plan.to_dict(),
            "interim_measurement": self.interim_measurement.to_dict(),
            "certification_execution": self.certification_execution.to_dict(),
        }

    def digest(self) -> str:
        return content_hash(self.payload())


@dataclass(frozen=True, slots=True)
class AssuranceOutcome:
    """The immutable, content-addressed outcome of a full ten-stage assurance run."""

    subject: AssuranceSubject
    policy_id: str
    policy_digest: str
    core: DeterministicCore
    measurement: MeasurementReport
    bundle: EvidenceBundle
    registry_snapshot: Mapping[str, Any]
    registry_entry: RegistryEntry | None
    certification_intelligence: CertificationIntelligenceReport
    reproducibility: ReproducibilityReport | None
    gates: tuple[Mapping[str, Any], ...]
    report: AssuranceReport
    outcome_sha256: str

    @classmethod
    def create(
        cls,
        *,
        subject: AssuranceSubject,
        policy: AssurancePolicy,
        core: DeterministicCore,
        measurement: MeasurementReport,
        bundle: EvidenceBundle,
        registry: CertificationRegistry,
        registry_entry: RegistryEntry | None,
        certification_intelligence: CertificationIntelligenceReport,
        reproducibility: ReproducibilityReport | None,
        gates: Iterable[Mapping[str, Any]],
        report: AssuranceReport,
    ) -> AssuranceOutcome:
        gate_records = tuple(dict(gate) for gate in gates)
        digest = content_hash(
            {
                "outcome_format": OUTCOME_FORMAT,
                "report_sha256": report.report_sha256,
                "core_digest": core.digest(),
                "measurement_sha256": measurement.report_sha256,
                "bundle_sha256": bundle.bundle_sha256,
                "registry_head": registry.head_hash,
                "certification_intelligence_sha256": (certification_intelligence.report_sha256),
                "reproducibility_sha256": (
                    reproducibility.report_sha256 if reproducibility is not None else ""
                ),
                "gates": [dict(gate) for gate in gate_records],
            }
        )
        return cls(
            subject=subject,
            policy_id=policy.identity.id,
            policy_digest=policy.digest(),
            core=core,
            measurement=measurement,
            bundle=bundle,
            registry_snapshot=registry.snapshot(),
            registry_entry=registry_entry,
            certification_intelligence=certification_intelligence,
            reproducibility=reproducibility,
            gates=gate_records,
            report=report,
            outcome_sha256=digest,
        )

    # -- derived properties ----------------------------------------------------

    @property
    def passed(self) -> bool:
        return self.report.passed

    @property
    def determination(self) -> str:
        return self.report.determination

    @property
    def certified(self) -> bool:
        return self.core.certification_execution.certified

    @property
    def certification_id(self) -> str:
        return self.core.certification_execution.certification_id

    def gates_passed(self) -> int:
        return sum(1 for gate in self.gates if gate.get("passed", False))

    def gates_failed(self) -> tuple[str, ...]:
        return tuple(str(gate["gate_id"]) for gate in self.gates if not gate.get("passed", False))

    def seal_line(self) -> str:
        """The single-line status seal, in the repository's programme-engine format."""
        counts = self.report.counts()
        return (
            f"{self.policy_id}: {self.determination} | "
            f"stages={counts['stages_passed']}/{counts['stages']} | "
            f"obligations={counts['obligations_satisfied']}/{counts['obligations_total']} | "
            f"gates={self.gates_passed()}/{len(self.gates)} | "
            f"evidence={self.bundle.counts()['artifacts']} | "
            f"certified={str(self.certified).lower()} | "
            f"reproducible={str(bool(self.reproducibility and self.reproducibility.byte_identical)).lower()} | "  # noqa: E501
            f"gate={self.report.gate.value} | seal={self.outcome_sha256[:16]}"
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "outcome_format": OUTCOME_FORMAT,
            "subject_id": self.subject.subject_id,
            "policy_id": self.policy_id,
            "policy_digest": self.policy_digest,
            "determination": self.determination,
            "passed": self.passed,
            "certified": self.certified,
            "certification_id": self.certification_id,
            "gates": [dict(gate) for gate in self.gates],
            "gates_failed": list(self.gates_failed()),
            "report": self.report.to_dict(),
            "dashboard": self.report.dashboard().to_dict(),
            "validation_plan": self.core.validation_plan.to_dict(),
            "validation_suite": self.core.suite.to_dict(),
            "validation_execution": self.core.validation_execution.to_dict(),
            "validation_intelligence": self.core.validation_intelligence.to_dict(),
            "certification_plan": self.core.certification_plan.to_dict(),
            "certification_execution": self.core.certification_execution.to_dict(),
            "certification_intelligence": self.certification_intelligence.to_dict(),
            "measurement": self.measurement.to_dict(),
            "evidence_bundle": self.bundle.to_dict(),
            "certification_registry": dict(self.registry_snapshot),
            "registry_entry": (
                self.registry_entry.to_dict() if self.registry_entry is not None else None
            ),
            "reproducibility": (
                self.reproducibility.to_dict() if self.reproducibility is not None else None
            ),
            "seal": self.seal_line(),
            "outcome_sha256": self.outcome_sha256,
        }


class AssuranceOrchestrator:
    """Runs all ten owned assurance capabilities over one subject under one policy."""

    __slots__ = (
        "_policy",
        "_registry",
        "_validation_planner",
        "_certification_planner",
        "_generator",
        "_validation_executor",
        "_validation_intelligence",
        "_certification_executor",
        "_certification_intelligence",
    )

    def __init__(
        self,
        policy: AssurancePolicy | None = None,
        *,
        registry: CertificationRegistry | None = None,
    ) -> None:
        resolved = policy if policy is not None else load_default_policy()
        if not isinstance(resolved, AssurancePolicy):
            raise AssuranceExecutionError("the orchestrator requires an AssurancePolicy")
        self._policy = resolved
        self._registry = (
            registry
            if registry is not None
            else CertificationRegistry(resolved.binding("registry_id"))
        )
        self._validation_planner = ValidationPlanner(resolved)
        self._certification_planner = CertificationPlanner(resolved)
        self._generator = SuiteGenerator()
        self._validation_executor = ValidationExecutor()
        self._validation_intelligence = ValidationIntelligence()
        self._certification_executor = CertificationExecutor(resolved)
        self._certification_intelligence = CertificationIntelligence()

    @property
    def policy(self) -> AssurancePolicy:
        return self._policy

    @property
    def registry(self) -> CertificationRegistry:
        return self._registry

    # -- the deterministic core ------------------------------------------------

    def core(self, subject: AssuranceSubject) -> DeterministicCore:
        """Run planning → generation → execution → intelligence → certification.

        Pure: no collector, no registry, no filesystem. Composed fresh on every call so a
        replay is genuinely independent of the first run.
        """
        if not isinstance(subject, AssuranceSubject):
            raise AssuranceExecutionError("an assurance run requires an AssuranceSubject")
        validation_plan = ValidationPlanner(self._policy).plan(subject)
        suite = SuiteGenerator().generate(validation_plan)
        validation_execution = ValidationExecutor().execute(suite, subject)
        validation_intelligence = ValidationIntelligence().analyze(suite, subject)
        certification_plan = CertificationPlanner(self._policy).plan(subject)

        pre_certification = merge_observations(
            subject_observations(subject.observations),
            validation_plan.observations(),
            suite.observations(),
            validation_execution.observations(),
            validation_intelligence.observations(),
            certification_plan.observations(),
        )
        interim_measurement = measure(
            subject_id=subject.subject_id,
            policy=self._policy,
            observations=pre_certification,
            metrics=metrics_before(self._policy, AssuranceStage.CERTIFICATION_EXECUTION),
        )
        certification_execution = CertificationExecutor(self._policy).execute(
            plan=certification_plan,
            subject=subject,
            validation_execution=validation_execution,
            measurement_report=interim_measurement,
        )
        return DeterministicCore(
            validation_plan=validation_plan,
            suite=suite,
            validation_execution=validation_execution,
            validation_intelligence=validation_intelligence,
            certification_plan=certification_plan,
            interim_measurement=interim_measurement,
            certification_execution=certification_execution,
        )

    # -- the full run ----------------------------------------------------------

    def run(
        self,
        subject: AssuranceSubject,
        *,
        replay: bool = True,
        evidence_dir: str | None = None,
    ) -> AssuranceOutcome:
        """Execute all ten stages and produce the immutable outcome."""
        core = self.core(subject)
        collector = EvidenceCollector(self._policy)
        self._collect_core(collector, subject, core)

        observations = merge_observations(
            subject_observations(subject.observations), core.observations()
        )

        registry_entry = self._register(subject, core, collector)
        collector.record(
            AssuranceStage.CERTIFICATION_REGISTRY,
            "certification-registry",
            self._registry.snapshot(),
        )
        observations = merge_observations(observations, self._registry.observations())

        reproducibility = self._replay(subject, core) if replay else None
        if reproducibility is not None:
            collector.record(
                AssuranceStage.CERTIFICATION_INTELLIGENCE,
                "reproducibility-report",
                reproducibility.to_dict(),
            )

        # An interim measurement artifact so the assessed bundle is itself complete; it is
        # re-recorded below with the final, whole-run measurement.
        interim = measure(
            subject_id=subject.subject_id, policy=self._policy, observations=observations
        )
        collector.record(
            AssuranceStage.EVIDENCE_COLLECTION, "measurement-report", interim.to_dict()
        )

        assessed = collector.bundle(
            subject_id=subject.subject_id,
            required_stages=stages_before(AssuranceStage.CERTIFICATION_INTELLIGENCE),
        )
        observations = merge_observations(observations, assessed.observations())

        certification_intelligence = self._certification_intelligence.analyze(
            CertificationIntelligenceInput(
                policy=self._policy,
                subject=subject,
                certification_plan=core.certification_plan,
                validation_execution=core.validation_execution,
                certification_execution=core.certification_execution,
                measurement_report=interim,
                bundle=assessed,
                registry=self._registry,
                reproducibility=reproducibility,
            )
        )
        collector.record(
            AssuranceStage.CERTIFICATION_INTELLIGENCE,
            "certification-intelligence-report",
            certification_intelligence.to_dict(),
        )
        observations = merge_observations(
            observations, certification_intelligence.observations(reproducibility)
        )

        measurement = measure(
            subject_id=subject.subject_id, policy=self._policy, observations=observations
        )
        collector.record(
            AssuranceStage.EVIDENCE_COLLECTION, "measurement-report", measurement.to_dict()
        )
        bundle = collector.bundle(subject_id=subject.subject_id)

        stage_records = self._stage_records(
            core=core,
            measurement=measurement,
            bundle=bundle,
            certification_intelligence=certification_intelligence,
        )
        report = AssuranceReport.create(
            subject_id=subject.subject_id,
            subject_digest=subject.digest(),
            policy_digest=self._policy.digest(),
            stage_records=stage_records,
        )
        gates = evaluate_gates(
            self._policy.gates,
            failed_obligations=self._all_failures(core),
            failed_stages=tuple(r.stage for r in stage_records if not r.passed),
        )
        outcome = AssuranceOutcome.create(
            subject=subject,
            policy=self._policy,
            core=core,
            measurement=measurement,
            bundle=bundle,
            registry=self._registry,
            registry_entry=registry_entry,
            certification_intelligence=certification_intelligence,
            reproducibility=reproducibility,
            gates=gates,
            report=report,
        )
        if evidence_dir:
            write_bundle(
                bundle,
                evidence_dir,
                forbidden_prefixes=self._policy.evidence.forbidden_write_prefixes,
            )
        _logger.info(
            "universal_assurance.run.completed",
            subject=subject.subject_id,
            determination=outcome.determination,
            certified=outcome.certified,
            stages_failed=report.counts()["stages_failed"],
        )
        return outcome

    # -- internals -------------------------------------------------------------

    def _collect_core(
        self,
        collector: EvidenceCollector,
        subject: AssuranceSubject,
        core: DeterministicCore,
    ) -> None:
        """Record every artifact the deterministic core produced."""
        collector.record(AssuranceStage.EVIDENCE_COLLECTION, "assurance-subject", subject.to_dict())
        collector.record(
            AssuranceStage.EVIDENCE_COLLECTION, "assurance-policy", self._policy.to_dict()
        )
        collector.record(
            AssuranceStage.VALIDATION_PLANNING,
            "validation-plan",
            core.validation_plan.to_dict(),
        )
        collector.record(
            AssuranceStage.VALIDATION_GENERATION, "validation-suite", core.suite.to_dict()
        )
        collector.record(
            AssuranceStage.VALIDATION_EXECUTION,
            "validation-report",
            core.validation_execution.to_dict(),
        )
        validation_evidence = core.validation_execution.evidence()
        collector.record(
            AssuranceStage.VALIDATION_EXECUTION,
            "validation-evidence",
            validation_evidence.to_dict() if validation_evidence is not None else {},
        )
        collector.record(
            AssuranceStage.CERTIFICATION_PLANNING,
            "certification-plan",
            core.certification_plan.to_dict(),
        )
        collector.record(
            AssuranceStage.CERTIFICATION_EXECUTION,
            "certification-decision",
            core.certification_execution.to_dict(),
        )
        decision = core.certification_execution.decision
        collector.record(
            AssuranceStage.CERTIFICATION_EXECUTION,
            "certificate",
            decision.certificate.to_dict() if decision is not None else {},
        )
        collector.record(
            AssuranceStage.CERTIFICATION_EVIDENCE,
            "certification-evidence",
            dict(core.certification_execution.evidence_payload),
        )
        collector.record(
            AssuranceStage.CERTIFICATION_EVIDENCE,
            "certification-audit-ledger",
            {
                "certification_id": core.certification_execution.certification_id,
                "entries": [dict(e) for e in core.certification_execution.audit_entries],
            },
        )
        intelligence_report = core.validation_intelligence.report
        collector.record(
            AssuranceStage.VALIDATION_INTELLIGENCE,
            "validation-intelligence-report",
            core.validation_intelligence.to_dict(),
        )
        collector.record(
            AssuranceStage.VALIDATION_INTELLIGENCE,
            "validation-intelligence-evidence",
            (
                build_validation_intelligence_evidence(intelligence_report).to_dict()
                if intelligence_report is not None
                else {}
            ),
        )

    def _register(
        self,
        subject: AssuranceSubject,
        core: DeterministicCore,
        collector: EvidenceCollector,
    ) -> RegistryEntry | None:
        """Register the certification, committing to the evidence that exists now."""
        execution = core.certification_execution
        if not execution.certification_id:
            return None
        certification_bundle = collector.bundle(subject_id=subject.subject_id, required_stages=())
        return self._registry.register(
            certification_id=execution.certification_id,
            subject_id=subject.subject_id,
            version=subject.version,
            certified=execution.certified,
            certificate_sha256=execution.certificate_sha256,
            certificate_intact=execution.certificate_intact,
            validation_plan_sha256=core.validation_plan.plan_sha256,
            certification_plan_sha256=core.certification_plan.plan_sha256,
            validation_execution_sha256=core.validation_execution.execution_sha256,
            certification_execution_sha256=execution.execution_sha256,
            evidence_id=certification_bundle.evidence_id,
            evidence_bundle_sha256=certification_bundle.bundle_sha256,
            policy_id=self._policy.identity.id,
            policy_digest=self._policy.digest(),
        )

    def _replay(self, subject: AssuranceSubject, core: DeterministicCore) -> ReproducibilityReport:
        """Replay the deterministic core and prove byte identity against the first run."""
        first = core.payload()
        replays = {"count": 0}

        def runner() -> Any:
            # The first replay reuses the completed core so the proof covers the *actual*
            # run, not merely two fresh runs that happen to agree with each other.
            if replays["count"] == 0:
                replays["count"] += 1
                return first
            replays["count"] += 1
            return self.core(subject).payload()

        return verify_reproducibility(
            runner,
            subject_id=subject.subject_id,
            label=REPLAY_LABEL,
            policy=self._policy.reproducibility,
        )

    @staticmethod
    def _all_failures(core: DeterministicCore) -> dict[str, str]:
        """Every failed obligation across validation, intelligence and certification."""
        failures: dict[str, str] = {}
        failures.update(core.validation_plan.failure_reasons_for_shortfalls())
        failures.update(core.certification_plan.failure_reasons_for_shortfalls())
        failures.update(core.validation_execution.failure_reasons())
        failures.update(core.validation_intelligence.failure_reasons())
        failures.update(core.certification_execution.failure_reasons())
        return failures

    def _stage_records(
        self,
        *,
        core: DeterministicCore,
        measurement: MeasurementReport,
        bundle: EvidenceBundle,
        certification_intelligence: CertificationIntelligenceReport,
    ) -> tuple[StageRecord, ...]:
        """Build one measured record per stage (obligations + policy metrics)."""
        execution = core.certification_execution
        specs: tuple[tuple[AssuranceStage, dict[str, Any]], ...] = (
            (
                AssuranceStage.VALIDATION_PLANNING,
                {
                    "total": len(core.validation_plan.planned),
                    "satisfied": len(core.validation_plan.satisfiable),
                    "blocking": core.validation_plan.blocking_shortfalls(),
                    "advisory": core.validation_plan.advisory_shortfalls(),
                    "artifact": core.validation_plan.plan_sha256,
                    "summary": core.validation_plan.counts(),
                },
            ),
            (
                AssuranceStage.VALIDATION_GENERATION,
                {
                    "total": len(core.suite.checks),
                    "satisfied": len(core.suite.bound_checks),
                    "blocking": core.suite.blocking_shortfalls(),
                    "advisory": core.suite.advisory_shortfalls(),
                    "artifact": core.suite.suite_sha256,
                    "summary": core.suite.counts(),
                },
            ),
            (
                AssuranceStage.VALIDATION_EXECUTION,
                {
                    "total": len(core.validation_execution.outcomes),
                    "satisfied": len(core.validation_execution.satisfied()),
                    "blocking": core.validation_execution.blocking_failures(),
                    "advisory": core.validation_execution.advisory_failures(),
                    "artifact": core.validation_execution.execution_sha256,
                    "summary": core.validation_execution.counts(),
                },
            ),
            (
                AssuranceStage.EVIDENCE_COLLECTION,
                {
                    "total": len(bundle.required_ids),
                    "satisfied": len(bundle.required_ids) - len(bundle.missing_required()),
                    "blocking": bundle.missing_required(),
                    "advisory": bundle.undeclared(),
                    "artifact": bundle.bundle_sha256,
                    "summary": bundle.counts(),
                },
            ),
            (
                AssuranceStage.CERTIFICATION_PLANNING,
                {
                    "total": len(core.certification_plan.planned),
                    "satisfied": len(core.certification_plan.satisfiable),
                    "blocking": core.certification_plan.blocking_shortfalls(),
                    "advisory": core.certification_plan.advisory_shortfalls(),
                    "artifact": core.certification_plan.plan_sha256,
                    "summary": core.certification_plan.counts(),
                },
            ),
            (
                AssuranceStage.CERTIFICATION_EXECUTION,
                {
                    "total": len(execution.outcomes),
                    "satisfied": len(execution.satisfied()),
                    "blocking": execution.blocking_failures() + execution.gates_failed(),
                    "advisory": execution.advisory_failures(),
                    "artifact": execution.execution_sha256,
                    "summary": execution.counts(),
                },
            ),
            (
                AssuranceStage.CERTIFICATION_EVIDENCE,
                {
                    "total": 1,
                    "satisfied": 1 if execution.evidence_sha256 else 0,
                    "blocking": () if execution.evidence_sha256 else ("certification-evidence",),
                    "advisory": (),
                    "artifact": execution.evidence_sha256,
                    "summary": {"audit_entries": len(execution.audit_entries)},
                },
            ),
            (
                AssuranceStage.CERTIFICATION_REGISTRY,
                {
                    "total": 1,
                    "satisfied": 1 if self._registry.verify() else 0,
                    "blocking": () if self._registry.verify() else ("registry-chain",),
                    "advisory": (),
                    "artifact": self._registry.fingerprint(),
                    "summary": self._registry.counts(),
                },
            ),
            (
                AssuranceStage.VALIDATION_INTELLIGENCE,
                {
                    "total": len(core.validation_intelligence.outcomes),
                    "satisfied": len(core.validation_intelligence.satisfied()),
                    "blocking": core.validation_intelligence.blocking_failures(),
                    "advisory": core.validation_intelligence.advisory_failures(),
                    "artifact": core.validation_intelligence.intelligence_sha256,
                    "summary": core.validation_intelligence.counts(),
                },
            ),
            (
                AssuranceStage.CERTIFICATION_INTELLIGENCE,
                {
                    "total": len(certification_intelligence.findings),
                    "satisfied": certification_intelligence.counts()["passed"],
                    "blocking": certification_intelligence.blocking_failures(),
                    "advisory": certification_intelligence.advisory_failures(),
                    "artifact": certification_intelligence.report_sha256,
                    "summary": certification_intelligence.counts(),
                },
            ),
        )
        return tuple(_stage_record(stage, spec, measurement) for stage, spec in specs)


def _stage_record(
    stage: AssuranceStage, spec: Mapping[str, Any], measurement: MeasurementReport
) -> StageRecord:
    """Fold the stage's own obligations together with its policy-declared metrics."""
    samples = measurement.samples_for(stage)
    metric_blocking = measurement.blocking_shortfalls(stage)
    metric_advisory = measurement.advisory_shortfalls(stage)
    satisfied_metrics = sum(1 for sample in samples if sample.satisfied)
    return StageRecord.create(
        stage=stage,
        obligations_total=int(spec["total"]) + len(samples),
        obligations_satisfied=int(spec["satisfied"]) + satisfied_metrics,
        blocking_failures=tuple(spec["blocking"]) + metric_blocking,
        advisory_failures=tuple(spec["advisory"]) + metric_advisory,
        artifact_sha256=str(spec["artifact"]),
        summary={
            **dict(spec["summary"]),
            "metrics": len(samples),
            "metrics_satisfied": satisfied_metrics,
        },
    )


__all__ = [
    "OUTCOME_FORMAT",
    "REPLAY_LABEL",
    "stages_before",
    "DeterministicCore",
    "AssuranceOutcome",
    "AssuranceOrchestrator",
]
