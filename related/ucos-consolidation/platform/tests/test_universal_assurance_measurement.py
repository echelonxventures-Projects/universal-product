"""UCOS-EPIC-014 — Assurance measurement tests.

The module claims to contain "no metric, no threshold and no comparator of its own", to
delegate every comparison to the reused ``Measurement`` so satisfaction "can never be
hand-set", and to treat an unobserved metric as *unsatisfied* rather than skipped.

The sharpest of those claims is the derived observation-coverage measurement: an
unmeasurable policy must become a **blocking** shortfall for the reused certifier, which
otherwise sees measurements and knows nothing about policy. These tests prove that
derived measurement appears, is blocking, and actually fails when a metric went
unobserved — i.e. that an unmeasurable run is genuinely uncertifiable.
"""

from __future__ import annotations

from platform.universal_assurance.contracts import AssuranceStage, Severity, Verdict
from platform.universal_assurance.errors import AssuranceMeasurementError
from platform.universal_assurance.measurement import (
    MEASUREMENT_FORMAT,
    OBSERVATION_COVERAGE_METRIC_ID,
    MeasurementReport,
    MetricSample,
    boolean_observation,
    certification_severity,
    measure,
    merge_observations,
    metrics_before,
    observation_names,
    samples_as_input,
    stage_metric_ids,
    subject_observations,
)
from platform.universal_assurance.policy import parse_policy

import pytest

from .universal_assurance_helpers import make_policy, policy_mapping

#: Observations that satisfy every metric the fixture policy declares.
SATISFYING = {"execution.blocking_failures": 0.0, "subject.coverage_line_percent": 95.0}


def _measure(observations=None, **kw):
    return measure(
        subject_id="S",
        policy=make_policy(),
        observations=SATISFYING if observations is None else observations,
        **kw,
    )


# -- severity projection ------------------------------------------------------


def test_assurance_severity_projects_onto_the_reused_certification_vocabulary():
    from engine.universal_certification.contracts import RuleSeverity

    assert certification_severity(Severity.BLOCKING) is RuleSeverity.BLOCKING
    assert certification_severity(Severity.ADVISORY) is RuleSeverity.ADVISORY


# -- sample evaluation --------------------------------------------------------


def test_a_satisfied_metric_is_decided_by_the_reused_measurement():
    report = _measure()
    sample = next(s for s in report.samples if s.metric_id == "M-EXEC")
    assert sample.observed is True
    assert sample.satisfied is True
    assert sample.value == 0.0
    assert report.verdict is Verdict.PASS


def test_a_metric_that_misses_its_threshold_is_a_shortfall():
    report = _measure({**SATISFYING, "execution.blocking_failures": 3.0})
    assert report.blocking_shortfalls() == ("M-EXEC",)
    assert report.verdict is Verdict.FAIL
    assert report.passed is False


def test_an_advisory_shortfall_does_not_fail_the_report():
    report = _measure({**SATISFYING, "subject.coverage_line_percent": 10.0})
    assert report.advisory_shortfalls() == ("M-COVERAGE",)
    assert report.blocking_shortfalls() == ()
    assert report.verdict is Verdict.PASS


def test_an_unobserved_metric_is_unsatisfied_never_skipped():
    report = _measure({})
    assert set(report.unobserved()) == {"M-EXEC", "M-COVERAGE"}
    assert all(s.satisfied is False for s in report.samples)
    assert report.counts()["sampled"] == 2
    assert report.verdict is Verdict.FAIL


@pytest.mark.parametrize("value", [True, False, "0", None])
def test_a_non_numeric_observation_is_treated_as_unobserved(value):
    """A boolean is an int in Python; silently comparing it would be a false measure."""
    report = _measure({"execution.blocking_failures": value})
    sample = next(s for s in report.samples if s.metric_id == "M-EXEC")
    assert sample.observed is False
    assert sample.satisfied is False


def test_satisfaction_cannot_be_hand_set_it_is_recomputed_from_the_comparison():
    from engine.universal_certification.contracts import MeasurementComparator

    sample = MetricSample(
        metric_id="M",
        stage=AssuranceStage.VALIDATION_EXECUTION,
        observation="o",
        comparator=MeasurementComparator.LE,
        threshold=0.0,
        severity=Severity.BLOCKING,
        observed=True,
        value=99.0,
        satisfied=True,  # a lie: 99.0 is not <= 0.0
        unit="count",
    )
    # Projecting onto the reused Measurement recomputes the verdict from the numbers,
    # so the hand-set field cannot survive contact with the certifier.
    assert sample.as_measurement().satisfied is False


def test_sample_shortfall_flags_are_severity_partitioned():
    blocking = next(s for s in _measure({}).samples if s.metric_id == "M-EXEC")
    advisory = next(s for s in _measure({}).samples if s.metric_id == "M-COVERAGE")
    assert blocking.is_blocking_shortfall is True
    assert blocking.is_advisory_shortfall is False
    assert advisory.is_advisory_shortfall is True
    assert advisory.is_blocking_shortfall is False


def test_sample_core_and_to_dict_agree():
    sample = _measure().samples[0]
    assert sample.core() == sample.to_dict()


# -- report scoping -----------------------------------------------------------


def test_metrics_can_be_scoped_to_a_stage():
    report = _measure(stage=AssuranceStage.VALIDATION_EXECUTION)
    assert {s.metric_id for s in report.samples} == {"M-EXEC", "M-COVERAGE"}
    empty = _measure(stage=AssuranceStage.CERTIFICATION_REGISTRY)
    assert empty.samples == ()
    assert empty.declared_total == 0


def test_an_explicit_metric_subset_is_still_policy_declared():
    policy = make_policy()
    subset = [m for m in policy.metrics if m.id == "M-EXEC"]
    report = _measure(metrics=subset)
    assert {s.metric_id for s in report.samples} == {"M-EXEC"}


def test_samples_for_a_stage_filters_the_report():
    report = _measure()
    assert len(report.samples_for(AssuranceStage.VALIDATION_EXECUTION)) == 2
    assert report.samples_for(AssuranceStage.CERTIFICATION_REGISTRY) == ()


def test_shortfalls_can_be_scoped_to_a_stage():
    report = _measure({})
    assert report.blocking_shortfalls(AssuranceStage.VALIDATION_EXECUTION) == ("M-EXEC",)
    assert report.blocking_shortfalls(AssuranceStage.CERTIFICATION_REGISTRY) == ()
    assert report.advisory_shortfalls(AssuranceStage.VALIDATION_EXECUTION) == ("M-COVERAGE",)


def test_observation_coverage_of_a_policy_declaring_no_metric_is_one():
    report = _measure(stage=AssuranceStage.CERTIFICATION_REGISTRY)
    assert report.observation_coverage() == 1.0


def test_observation_coverage_is_the_observed_over_sampled_ratio():
    assert _measure().observation_coverage() == 1.0
    assert _measure({"execution.blocking_failures": 0.0}).observation_coverage() == 0.5
    assert _measure({}).observation_coverage() == 0.0


def test_measure_rejects_anything_that_is_not_a_policy():
    with pytest.raises(AssuranceMeasurementError):
        measure(subject_id="S", policy="not-a-policy", observations={})


# -- the derived observation-coverage measurement ----------------------------


def test_the_derived_coverage_measurement_is_always_appended_for_the_certifier():
    measurements = _measure().to_certification_measurements()
    derived = [m for m in measurements if m.metric_id == OBSERVATION_COVERAGE_METRIC_ID]
    assert len(derived) == 1
    assert derived[0].satisfied is True


def test_an_unmeasurable_policy_becomes_a_blocking_shortfall_for_the_certifier():
    """The certifier sees measurements, not policy — this is how it learns."""
    from engine.universal_certification.contracts import RuleSeverity

    measurements = _measure({}).to_certification_measurements()
    derived = next(m for m in measurements if m.metric_id == OBSERVATION_COVERAGE_METRIC_ID)
    assert derived.satisfied is False
    assert derived.severity is RuleSeverity.BLOCKING
    assert derived.value == 0.0


def test_only_observed_samples_are_projected_to_the_certifier():
    measurements = _measure({"execution.blocking_failures": 0.0}).to_certification_measurements()
    ids = {m.metric_id for m in measurements}
    assert "M-EXEC" in ids
    assert "M-COVERAGE" not in ids
    assert OBSERVATION_COVERAGE_METRIC_ID in ids


def test_the_measurement_input_carries_its_declared_source():
    payload = _measure().to_measurement_input(source="test-suite")
    assert payload.source == "test-suite"


def test_samples_as_input_projects_an_arbitrary_sample_iterable():
    report = _measure({"execution.blocking_failures": 0.0})
    payload = samples_as_input(report.samples, source="ad-hoc")
    assert payload.source == "ad-hoc"
    assert {m.metric_id for m in payload.measurements} == {"M-EXEC"}


# -- observation plumbing -----------------------------------------------------


def test_merge_observations_is_deterministic_and_later_sources_win():
    merged = merge_observations({"b": 1, "a": 2}, {"b": 9})
    assert merged == {"a": 2.0, "b": 9.0}
    assert list(merged) == ["a", "b"]


def test_merge_observations_rejects_a_non_numeric_value():
    with pytest.raises(AssuranceMeasurementError):
        merge_observations({"k": "1"})


def test_merge_observations_rejects_a_boolean_masquerading_as_a_number():
    with pytest.raises(AssuranceMeasurementError):
        merge_observations({"k": True})


def test_merging_nothing_yields_nothing():
    assert merge_observations() == {}


def test_boolean_observations_project_onto_the_numeric_space():
    assert boolean_observation(True) == 1.0
    assert boolean_observation(False) == 0.0


def test_subject_observations_are_namespaced_so_they_cannot_overwrite_stage_facts():
    namespaced = subject_observations({"execution.blocking_failures": 99.0})
    assert namespaced == {"subject.execution.blocking_failures": 99.0}
    merged = merge_observations({"execution.blocking_failures": 0.0}, namespaced)
    assert merged["execution.blocking_failures"] == 0.0


def test_subject_observations_are_emitted_in_sorted_order():
    assert list(subject_observations({"b": 1, "a": 2})) == ["subject.a", "subject.b"]


# -- stage-derived metric selection ------------------------------------------


def test_metrics_before_a_stage_are_derived_from_the_stage_order():
    policy = make_policy()
    before = metrics_before(policy, AssuranceStage.CERTIFICATION_EXECUTION)
    assert {m.id for m in before} == {"M-EXEC", "M-COVERAGE"}
    assert metrics_before(policy, AssuranceStage.VALIDATION_PLANNING) == ()


def test_metrics_before_excludes_the_stage_itself():
    document = policy_mapping()
    document["metrics"][0]["stage"] = "certification-execution"
    policy = parse_policy(document)
    before = metrics_before(policy, AssuranceStage.CERTIFICATION_EXECUTION)
    assert "M-EXEC" not in {m.id for m in before}


def test_observation_names_lists_every_dependency_of_the_policy():
    assert observation_names(make_policy()) == (
        "execution.blocking_failures",
        "subject.coverage_line_percent",
    )


def test_stage_metric_ids_are_sorted():
    assert stage_metric_ids(make_policy(), AssuranceStage.VALIDATION_EXECUTION) == (
        "M-COVERAGE",
        "M-EXEC",
    )
    assert stage_metric_ids(make_policy(), AssuranceStage.CERTIFICATION_REGISTRY) == ()


# -- reproducibility ----------------------------------------------------------


def test_an_identical_policy_and_observation_set_reproduce_an_identical_report():
    first, second = _measure(), _measure()
    assert first.report_sha256 == second.report_sha256
    assert first.to_dict() == second.to_dict()


def test_the_report_hash_changes_when_an_observation_changes():
    moved = _measure({**SATISFYING, "execution.blocking_failures": 1.0})
    assert _measure().report_sha256 != moved.report_sha256


def test_the_report_hash_is_independent_of_observation_insertion_order():
    forward = _measure(dict(SATISFYING))
    reverse = _measure(dict(reversed(list(SATISFYING.items()))))
    assert forward.report_sha256 == reverse.report_sha256


def test_the_report_anchors_itself_to_the_policy_text():
    policy = make_policy()
    report = measure(subject_id="S", policy=policy, observations=SATISFYING)
    assert report.policy_digest == policy.digest()
    assert report.policy_id == policy.identity.id
    assert report.to_dict()["measurement_format"] == MEASUREMENT_FORMAT


def test_report_counts_reconcile():
    counts = _measure({"execution.blocking_failures": 5.0}).counts()
    assert counts["sampled"] == 2
    assert counts["observed"] + counts["unobserved"] == counts["sampled"]
    assert counts["blocking_shortfalls"] == 1


def test_a_measurement_report_is_immutable():
    report = _measure()
    with pytest.raises(Exception):  # noqa: B017 — frozen dataclass
        report.verdict = Verdict.FAIL  # type: ignore[misc]
    assert isinstance(report, MeasurementReport)
