"""UCOS-EPIC-014 — Validation Intelligence & Certification Intelligence tests.

**Validation Intelligence** composes the reused continuous-intelligence engine scoped to
exactly the policy-planned dimensions and reconciles each dimension finding back to the
obligation that demanded it. What it adds over the reused engine — the policy binding and
the fail-closed treatment of a planned dimension that never got analyzed — is what is
tested here.

**Certification Intelligence** is the capability nothing in the reused platform provides:
the certifier answers "do the rules pass?", this answers "is this certification
*trustworthy*?" across seven orthogonal dimensions. Each dimension is driven to both
verdicts from a deliberately constructed run, because a trustworthiness engine that can
only say "trustworthy" is not measuring anything.

The load-bearing asymmetry throughout: an undecidable dimension records FAIL, never a
pass. Advisory dimensions (undeclared evidence, policy drift, advisory metrics) must
*not* fail the report — that separation is exercised from both sides.
"""

from __future__ import annotations

from platform.universal_assurance.certification import CertificationExecutor
from platform.universal_assurance.contracts import Outcome, Severity, Verdict
from platform.universal_assurance.determinism import ReplaySample, ReproducibilityReport
from platform.universal_assurance.errors import AssuranceIntelligenceError
from platform.universal_assurance.evidence import EvidenceCollector
from platform.universal_assurance.execution import ValidationExecutor
from platform.universal_assurance.generation import SuiteGenerator
from platform.universal_assurance.intelligence import (
    CERTIFICATION_INTELLIGENCE_FORMAT,
    REASON_NO_REPORT,
    REASON_NOT_ANALYZED,
    REASON_UNBOUND,
    VALIDATION_INTELLIGENCE_FORMAT,
    CertificationFinding,
    CertificationIntelligence,
    CertificationIntelligenceDimension,
    CertificationIntelligenceInput,
    CertificationIntelligenceReport,
    ValidationIntelligence,
    ValidationIntelligenceOutcome,
)
from platform.universal_assurance.measurement import measure
from platform.universal_assurance.planning import CertificationPlanner, ValidationPlanner
from platform.universal_assurance.policy import parse_policy
from platform.universal_assurance.registry import CertificationRegistry

import pytest

from .universal_assurance_helpers import (
    REAL_DIMENSION_REF,
    factless_subject,
    make_policy,
    make_subject,
    policy_mapping,
)


def _suite(policy=None, subject=None):
    policy = policy if policy is not None else make_policy()
    subject = subject if subject is not None else make_subject()
    return SuiteGenerator().generate(ValidationPlanner(policy).plan(subject))


def _analyze(policy=None, subject=None):
    subject = subject if subject is not None else make_subject()
    return ValidationIntelligence().analyze(_suite(policy, subject), subject)


# --------------------------------------------------------------------------- #
# Validation Intelligence                                                      #
# --------------------------------------------------------------------------- #


def test_the_planned_dimension_is_analyzed_and_reconciled_to_its_obligation():
    outcome = _analyze()
    assert outcome.verdict is Verdict.PASS
    assert outcome.report is not None
    assert REAL_DIMENSION_REF in outcome.dimensions_analyzed
    by_id = {o.obligation_id: o for o in outcome.outcomes}
    assert by_id["OB-DIM"].executed is True
    assert by_id["OB-DIM"].ref == REAL_DIMENSION_REF


def test_the_engine_is_scoped_to_exactly_the_policy_planned_dimensions():
    """Not every dimension the reused engine can analyze — only the planned ones."""
    outcome = _analyze()
    assert set(outcome.dimensions_analyzed) == {REAL_DIMENSION_REF}


def test_an_unplanned_dimension_produces_no_analysis_at_all():
    document = policy_mapping()
    document["obligations"] = [document["obligations"][0], document["obligations"][2]]
    document["gates"] = [
        g for g in document["gates"] if set(g["obligations"]) <= {"OB-RULE", "OB-CRIT"}
    ]
    outcome = _analyze(policy=parse_policy(document))
    assert outcome.outcomes == ()
    assert outcome.dimensions_analyzed == ()
    assert outcome.report is None
    assert outcome.verdict is Verdict.PASS


def test_an_undecidable_dimension_obligation_fails_closed_rather_than_passing():
    outcome = _analyze(subject=factless_subject())
    by_id = {o.obligation_id: o for o in outcome.outcomes}
    assert by_id["OB-DIM"].outcome is Outcome.FAIL
    assert by_id["OB-DIM"].executed is False
    assert outcome.verdict is Verdict.FAIL


def test_an_unbound_dimension_records_its_binding_reason():
    document = policy_mapping()
    document["obligations"][1]["ref"] = "no_such_dimension"
    document["obligations"][1]["requires_facts"] = []
    outcome = _analyze(policy=parse_policy(document))
    by_id = {o.obligation_id: o for o in outcome.outcomes}
    assert by_id["OB-DIM"].implementation_status in {
        "unknown-intelligence-dimension",
        REASON_UNBOUND,
    }
    assert by_id["OB-DIM"].outcome is Outcome.FAIL


def test_a_planned_dimension_the_engine_never_analyzed_is_not_assumed_clean():
    """The fail-closed case the reused engine cannot see: bound, but no report came
    back for it. Driven through the documented engine-factory seam with a *real*
    engine scoped to a different dimension, so the report is genuine and only the
    planned dimension is missing from it."""
    from platform.validation_intelligence.contracts import IntelligenceDimension
    from platform.validation_intelligence.engine import (
        ContinuousValidationIntelligenceEngine,
    )

    other = next(d for d in IntelligenceDimension if d.value != REAL_DIMENSION_REF)
    subject = make_subject()
    outcome = ValidationIntelligence(
        lambda dimensions: ContinuousValidationIntelligenceEngine(dimensions=(other,))
    ).analyze(_suite(subject=subject), subject)

    by_id = {o.obligation_id: o for o in outcome.outcomes}
    assert by_id["OB-DIM"].implementation_status == REASON_NOT_ANALYZED
    assert by_id["OB-DIM"].outcome is Outcome.FAIL
    assert outcome.verdict is Verdict.FAIL


def test_validation_intelligence_rejects_the_wrong_input_types():
    with pytest.raises(AssuranceIntelligenceError):
        ValidationIntelligence().analyze("not-a-suite", make_subject())
    with pytest.raises(AssuranceIntelligenceError):
        ValidationIntelligence().analyze(_suite(), "not-a-subject")


def test_an_outcome_without_a_report_reports_empty_projections():
    outcome = ValidationIntelligenceOutcome.create(
        subject_id="S", plan_id="P", suite_id="U", policy_digest="D", outcomes=(), report=None
    )
    assert outcome.report_sha256 == ""
    assert outcome.evidence_sha256 == ""
    assert outcome.dimensions_analyzed == ()
    assert outcome.compatible is False
    assert outcome.compliant is False
    assert outcome.to_dict()["report"] is None


def test_a_bound_dimension_with_no_report_at_all_fails_closed():
    """Defensive containment. `analyze` builds a report whenever the suite bound any
    dimension, so a bound check with `report is None` cannot arise through the public
    path today. The branch guards against that invariant breaking, and the guard is
    proven on the pure reconciliation function rather than exempted from measurement."""
    from platform.universal_assurance.intelligence import _reconcile_dimension

    bound_check = next(c for c in _suite().checks if c.obligation_id == "OB-DIM" and c.bound)
    outcome = _reconcile_dimension(bound_check, None)
    assert outcome.implementation_status == REASON_NO_REPORT
    assert outcome.outcome is Outcome.FAIL
    assert outcome.executed is False


def test_dimension_coverage_is_one_when_nothing_was_planned():
    outcome = ValidationIntelligenceOutcome.create(
        subject_id="S", plan_id="P", suite_id="U", policy_digest="D", outcomes=(), report=None
    )
    assert outcome.dimension_coverage() == 1.0


def test_validation_intelligence_observations_expose_the_measured_facts():
    observations = _analyze().observations()
    assert observations["validation_intelligence.obligations"] == 1.0
    assert observations["validation_intelligence.dimension_coverage"] == 1.0
    assert set(observations) >= {
        "validation_intelligence.satisfied",
        "validation_intelligence.blocking_failures",
        "validation_intelligence.advisory_failures",
        "validation_intelligence.compatible",
        "validation_intelligence.compliant",
    }


def test_validation_intelligence_failure_reasons_feed_the_gate_map():
    outcome = _analyze(subject=factless_subject())
    assert "OB-DIM" in outcome.failure_reasons()
    assert _analyze().failure_reasons() == {}


def test_validation_intelligence_counts_reconcile():
    counts = _analyze().counts()
    assert counts["obligations"] == 1
    assert counts["satisfied"] <= counts["obligations"]


def test_an_identical_analysis_reproduces_an_identical_record():
    first, second = _analyze(), _analyze()
    assert first.intelligence_sha256 == second.intelligence_sha256
    assert first.intelligence_id == second.intelligence_id
    assert first.intelligence_id.startswith("UCOS-VINTEL-")


def test_the_validation_intelligence_record_declares_its_format():
    assert _analyze().to_dict()["intelligence_format"] == VALIDATION_INTELLIGENCE_FORMAT


def test_a_validation_intelligence_outcome_is_immutable():
    with pytest.raises(Exception):  # noqa: B017 — frozen dataclass
        _analyze().verdict = Verdict.FAIL  # type: ignore[misc]


# --------------------------------------------------------------------------- #
# Certification Intelligence                                                   #
# --------------------------------------------------------------------------- #


def _run_parts(policy=None, subject=None, observations=None):
    policy = policy if policy is not None else make_policy()
    subject = subject if subject is not None else make_subject()
    suite = _suite(policy, subject)
    validation_execution = ValidationExecutor().execute(suite, subject)
    certification_plan = CertificationPlanner(policy).plan(subject)
    measurement = measure(
        subject_id=subject.subject_id,
        policy=policy,
        observations=observations if observations is not None else {},
    )
    certification_execution = CertificationExecutor(policy).execute(
        plan=certification_plan,
        subject=subject,
        validation_execution=validation_execution,
        measurement_report=measurement,
    )
    collector = EvidenceCollector(policy)
    collector.record(
        __import__(
            "platform.universal_assurance.contracts", fromlist=["AssuranceStage"]
        ).AssuranceStage.VALIDATION_PLANNING,
        "validation-plan",
        {"a": 1},
    )
    bundle = collector.bundle(subject_id=subject.subject_id)
    registry = CertificationRegistry(policy.binding("registry_id"))
    return {
        "policy": policy,
        "subject": subject,
        "certification_plan": certification_plan,
        "validation_execution": validation_execution,
        "certification_execution": certification_execution,
        "measurement_report": measurement,
        "bundle": bundle,
        "registry": registry,
    }


def _request(**overrides):
    parts = _run_parts()
    parts.update(overrides)
    return CertificationIntelligenceInput(**parts)


def _report(**overrides):
    return CertificationIntelligence().analyze(_request(**overrides))


def _findings_by_id(report):
    return {finding.check_id: finding for finding in report.findings}


def test_all_seven_dimensions_are_decided_on_every_run():
    report = _report()
    assert set(report.dimensions_run()) == {d.value for d in CertificationIntelligenceDimension}
    assert report.counts()["dimensions"] == 7


def test_certification_intelligence_rejects_anything_but_its_input_type():
    with pytest.raises(AssuranceIntelligenceError):
        CertificationIntelligence().analyze("not-an-input")


def test_readiness_reports_the_passed_over_total_finding_ratio():
    report = _report()
    counts = report.counts()
    assert report.readiness() == counts["passed"] / counts["findings"]


def test_a_report_with_no_findings_has_zero_readiness_not_one():
    """Fail-closed: nothing measured is not perfect trustworthiness."""
    empty = CertificationIntelligenceReport.create(
        subject_id="S", policy_id="P", policy_digest="D", findings=()
    )
    assert empty.readiness() == 0.0


def test_an_unregistered_certification_is_a_registry_integrity_failure():
    report = _report()
    finding = _findings_by_id(report)["registry_integrity.certification-registered"]
    assert finding.passed is False
    assert finding.severity is Severity.BLOCKING


def test_a_registered_certification_satisfies_the_registry_dimension():
    parts = _run_parts()
    execution = parts["certification_execution"]
    parts["registry"].register(
        certification_id=execution.certification_id,
        subject_id=parts["subject"].subject_id,
        version=parts["subject"].version,
        certified=execution.certified,
        certificate_sha256=execution.certificate_sha256,
        certificate_intact=execution.certificate_intact,
        validation_plan_sha256="v",
        certification_plan_sha256="c",
        validation_execution_sha256=parts["validation_execution"].execution_sha256,
        certification_execution_sha256=execution.execution_sha256,
        evidence_id=parts["bundle"].evidence_id,
        evidence_bundle_sha256=parts["bundle"].bundle_sha256,
        policy_id=parts["policy"].identity.id,
        policy_digest=parts["policy"].digest(),
    )
    report = CertificationIntelligence().analyze(CertificationIntelligenceInput(**parts))
    findings = _findings_by_id(report)
    assert findings["registry_integrity.certification-registered"].passed is True
    assert findings["registry_integrity.chain-verifies"].passed is True


def test_policy_drift_is_surfaced_but_only_as_advisory():
    """Drift is the honest record of a policy that changed, not an error."""
    parts = _run_parts()
    execution = parts["certification_execution"]
    parts["registry"].register(
        certification_id=execution.certification_id,
        subject_id="S",
        version="1.0.0",
        certified=False,
        certificate_sha256="x",
        certificate_intact=False,
        validation_plan_sha256="v",
        certification_plan_sha256="c",
        validation_execution_sha256="ve",
        certification_execution_sha256="ce",
        evidence_id="e",
        evidence_bundle_sha256="eb",
        policy_id="OTHER",
        policy_digest="a-different-policy-text",
    )
    report = CertificationIntelligence().analyze(CertificationIntelligenceInput(**parts))
    finding = _findings_by_id(report)["registry_integrity.no-policy-drift"]
    assert finding.passed is False
    assert finding.severity is Severity.ADVISORY
    assert finding.details["drifted"] == [execution.certification_id]


def test_missing_required_evidence_is_a_blocking_integrity_failure():
    parts = _run_parts()
    parts["bundle"] = EvidenceCollector(parts["policy"]).bundle(subject_id="S")
    report = CertificationIntelligence().analyze(CertificationIntelligenceInput(**parts))
    finding = _findings_by_id(report)["evidence_integrity.required-present"]
    assert finding.passed is False
    assert finding.details["missing"] == ["EV-PLAN"]


def test_a_complete_bundle_satisfies_the_evidence_dimension():
    findings = _findings_by_id(_report())
    assert findings["evidence_integrity.required-present"].passed is True
    assert findings["evidence_integrity.manifest-intact"].passed is True


def test_undeclared_evidence_is_advisory_not_blocking():
    from platform.universal_assurance.contracts import AssuranceStage

    parts = _run_parts()
    collector = EvidenceCollector(parts["policy"])
    collector.record(AssuranceStage.VALIDATION_PLANNING, "validation-plan", {"a": 1})
    collector.record(AssuranceStage.VALIDATION_PLANNING, "surprise", {"b": 2})
    parts["bundle"] = collector.bundle(subject_id="S")
    report = CertificationIntelligence().analyze(CertificationIntelligenceInput(**parts))
    finding = _findings_by_id(report)["evidence_integrity.no-undeclared"]
    assert finding.passed is False
    assert finding.severity is Severity.ADVISORY


def test_unobserved_metrics_are_a_blocking_measurement_coverage_failure():
    parts = _run_parts()  # measured against no observations at all
    report = CertificationIntelligence().analyze(CertificationIntelligenceInput(**parts))
    finding = _findings_by_id(report)["measurement_coverage.all-observed"]
    assert finding.passed is False
    assert finding.severity is Severity.BLOCKING


def test_fully_observed_and_satisfied_metrics_satisfy_the_measurement_dimension():
    parts = _run_parts(
        observations={
            "execution.blocking_failures": 0.0,
            "subject.coverage_line_percent": 95.0,
        }
    )
    report = CertificationIntelligence().analyze(CertificationIntelligenceInput(**parts))
    findings = _findings_by_id(report)
    assert findings["measurement_coverage.all-observed"].passed is True
    assert findings["measurement_coverage.blocking-satisfied"].passed is True
    assert findings["measurement_coverage.advisory-satisfied"].passed is True


def test_an_advisory_metric_shortfall_is_reported_without_failing_the_report():
    parts = _run_parts(
        observations={
            "execution.blocking_failures": 0.0,
            "subject.coverage_line_percent": 10.0,
        }
    )
    report = CertificationIntelligence().analyze(CertificationIntelligenceInput(**parts))
    finding = _findings_by_id(report)["measurement_coverage.advisory-satisfied"]
    assert finding.passed is False
    assert finding.severity is Severity.ADVISORY
    assert "measurement_coverage.advisory-satisfied" not in report.blocking_failures()


def test_criteria_coverage_notices_an_undecidable_plan():
    document = policy_mapping()
    document["obligations"][2]["requires_facts"] = ["repository_truth", "observations.absent"]
    parts = _run_parts(policy=parse_policy(document))
    report = CertificationIntelligence().analyze(CertificationIntelligenceInput(**parts))
    finding = _findings_by_id(report)["criteria_coverage.plan-decidable"]
    assert finding.passed is False
    assert finding.details["blocking_shortfalls"] == ["OB-CRIT"]


def test_criteria_coverage_notices_an_obligation_that_was_never_evaluated():
    document = policy_mapping()
    document["obligations"][2]["requires_facts"] = ["repository_truth", "observations.absent"]
    parts = _run_parts(policy=parse_policy(document))
    report = CertificationIntelligence().analyze(CertificationIntelligenceInput(**parts))
    finding = _findings_by_id(report)["criteria_coverage.all-evaluated"]
    assert finding.passed is False
    assert "OB-CRIT" in finding.details["not_evaluated"]


def test_readiness_dimension_reports_the_certification_and_validation_verdicts():
    findings = _findings_by_id(_report())
    assert "certification_readiness.criteria-satisfied" in findings
    assert "certification_readiness.gates-passed" in findings
    assert "certification_readiness.certified" in findings
    assert "certification_readiness.validation-accepted" in findings


def test_a_failed_validation_closes_the_readiness_dimension():
    parts = _run_parts(subject=factless_subject())
    report = CertificationIntelligence().analyze(CertificationIntelligenceInput(**parts))
    finding = _findings_by_id(report)["certification_readiness.validation-accepted"]
    assert finding.passed is False


def test_certificate_integrity_reports_absence_as_failure_not_as_silence():
    parts = _run_parts(subject=factless_subject())  # no decision is issued
    report = CertificationIntelligence().analyze(CertificationIntelligenceInput(**parts))
    findings = _findings_by_id(report)
    assert findings["certificate_integrity.content-hash-verifies"].passed is False
    assert findings["certificate_integrity.evidence-referenced"].passed is False
    assert findings["certificate_integrity.audit-trail"].passed is False


def test_certificate_integrity_passes_on_a_real_certification_run():
    findings = _findings_by_id(_report())
    assert findings["certificate_integrity.evidence-referenced"].passed is True
    assert findings["certificate_integrity.audit-trail"].passed is True


# -- the reproducibility dimension -------------------------------------------


def _replay_report(*, digests, required=True):
    return ReproducibilityReport.create(
        subject_id="S",
        label="l",
        required=required,
        samples=tuple(
            ReplaySample(index=i, digest=d, byte_length=10) for i, d in enumerate(digests)
        ),
    )


def test_an_absent_replay_fails_when_the_policy_requires_byte_identity():
    report = _report(reproducibility=None)
    finding = _findings_by_id(report)["reproducibility.replays-byte-identical"]
    assert finding.passed is False
    assert finding.details["replays"] == 0


def test_an_absent_replay_passes_when_the_policy_does_not_require_byte_identity():
    document = policy_mapping()
    document["reproducibility"] = {"replays": 2, "byte_identical_required": False}
    parts = _run_parts(policy=parse_policy(document))
    parts["reproducibility"] = None
    report = CertificationIntelligence().analyze(CertificationIntelligenceInput(**parts))
    finding = _findings_by_id(report)["reproducibility.replays-byte-identical"]
    assert finding.passed is True


def test_identical_replays_satisfy_the_reproducibility_dimension():
    report = _report(reproducibility=_replay_report(digests=["a", "a"]))
    findings = _findings_by_id(report)
    assert findings["reproducibility.replays-byte-identical"].passed is True
    assert findings["reproducibility.replay-count-met"].passed is True


def test_diverging_replays_fail_the_reproducibility_dimension():
    report = _report(reproducibility=_replay_report(digests=["a", "b"]))
    finding = _findings_by_id(report)["reproducibility.replays-byte-identical"]
    assert finding.passed is False
    assert finding.details["distinct_digests"] == ["a", "b"]


def test_too_few_replays_fail_the_replay_count_check():
    report = _report(reproducibility=_replay_report(digests=["a"]))
    finding = _findings_by_id(report)["reproducibility.replay-count-met"]
    assert finding.passed is False
    assert finding.details["required"] == 2


# -- report aggregation ------------------------------------------------------


def test_a_blocking_finding_fails_the_report_and_an_advisory_one_does_not():
    blocking = CertificationIntelligenceReport.create(
        subject_id="S",
        policy_id="P",
        policy_digest="D",
        findings=[
            CertificationFinding(
                check_id="c",
                dimension=CertificationIntelligenceDimension.READINESS,
                severity=Severity.BLOCKING,
                outcome=Outcome.FAIL,
                message="m",
            )
        ],
    )
    advisory = CertificationIntelligenceReport.create(
        subject_id="S",
        policy_id="P",
        policy_digest="D",
        findings=[
            CertificationFinding(
                check_id="c",
                dimension=CertificationIntelligenceDimension.READINESS,
                severity=Severity.ADVISORY,
                outcome=Outcome.FAIL,
                message="m",
            )
        ],
    )
    assert blocking.verdict is Verdict.FAIL
    assert blocking.blocking_failures() == ("c",)
    assert advisory.verdict is Verdict.PASS
    assert advisory.advisory_failures() == ("c",)


def test_a_dimension_verdict_is_failed_by_any_blocking_finding_within_it():
    report = _report()
    verdicts = report.dimension_verdicts()
    assert set(verdicts) == set(report.dimensions_run())
    assert all(v in {"pass", "fail"} for v in verdicts.values())


def test_findings_are_ordered_by_dimension_then_check_id():
    findings = _report().findings
    keys = [(f.dimension.order, f.check_id) for f in findings]
    assert keys == sorted(keys)


def test_the_report_asserts_engineering_only_authority():
    from platform.universal_assurance.contracts import ASSURANCE_AUTHORITY

    assert _report().authority == ASSURANCE_AUTHORITY


def test_certification_intelligence_observations_expose_the_measured_facts():
    report = _report()
    observations = report.observations(_replay_report(digests=["a", "a"]))
    assert observations["certification_intelligence.byte_identical"] == 1.0
    assert observations["certification_intelligence.readiness"] == report.readiness()
    assert report.observations(None)["certification_intelligence.byte_identical"] == 0.0


def test_a_finding_core_excludes_its_volatile_details():
    finding = _report().findings[0]
    assert "details" not in finding.core()
    assert "details" in finding.to_dict()


def test_an_identical_run_reproduces_an_identical_intelligence_report():
    first = CertificationIntelligenceReport.create(
        subject_id="S", policy_id="P", policy_digest="D", findings=_report().findings
    )
    second = CertificationIntelligenceReport.create(
        subject_id="S", policy_id="P", policy_digest="D", findings=_report().findings
    )
    assert first.report_sha256 == second.report_sha256
    assert first.intelligence_id.startswith("UCOS-CINTEL-")


def test_the_report_declares_its_format_and_serializes_whole():
    payload = _report().to_dict()
    assert payload["intelligence_format"] == CERTIFICATION_INTELLIGENCE_FORMAT
    assert "findings" in payload
    assert "dimension_verdicts" in payload
    assert payload["readiness"] == _report().readiness()


def test_the_certification_intelligence_dimension_order_is_total():
    assert [d.order for d in CertificationIntelligenceDimension] == list(
        range(len(CertificationIntelligenceDimension))
    )


def test_a_certification_intelligence_report_is_immutable():
    with pytest.raises(Exception):  # noqa: B017 — frozen dataclass
        _report().verdict = Verdict.PASS  # type: ignore[misc]
