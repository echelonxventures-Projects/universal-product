"""UCOS-EPIC-006 — Certification rule tests."""

from __future__ import annotations

from engine.universal_certification import (
    ComplianceEngine,
    Measurement,
    MeasurementComparator,
    MeasurementInput,
    RuleSeverity,
    default_rules,
)
from engine.universal_certification.rules import (
    ComplianceConformantRule,
    DisclosurePresentRule,
    MeasurementCompleteRule,
    MeasurementsPresentRule,
    MeasurementsSatisfiedRule,
    RepositoryTruthConsistentRule,
    ValidationAcceptedRule,
    ValidationCompleteRule,
    ValidationEvidencePresentRule,
    VersionPinnedRule,
)

from .conftest import (
    broken_evidence,
    inconsistent_repository_truth,
    mutate,
    shortfall_measurement,
)


def _compliance(subject):
    return ComplianceEngine().evaluate(subject)


def test_default_rules_are_sorted_and_ten():
    ids = [r.rule_id for r in default_rules()]
    assert ids == sorted(ids)
    assert len(ids) == 10


def test_all_rules_pass_for_conformant_subject(subject):
    compliance = _compliance(subject)
    for rule in default_rules():
        assert rule.evaluate(subject, compliance).passed is True


def test_compliance_conformant_rule_fails_when_non_conformant(subject):
    bad = mutate(subject.validation, accepted=False, verdict="fail")
    bad_subject = mutate(subject, validation=bad)
    compliance = _compliance(bad_subject)
    assert ComplianceConformantRule().evaluate(bad_subject, compliance).passed is False


def test_validation_accepted_rule_fails(subject):
    bad = mutate(subject, validation=mutate(subject.validation, accepted=False, verdict="fail"))
    assert ValidationAcceptedRule().evaluate(bad, _compliance(subject)).passed is False


def test_validation_evidence_rule_fails(subject):
    bad = broken_evidence(subject)
    assert ValidationEvidencePresentRule().evaluate(bad, _compliance(subject)).passed is False


def test_measurements_present_rule_fails(subject):
    bad = mutate(subject, measurement=MeasurementInput.create(()))
    assert MeasurementsPresentRule().evaluate(bad, _compliance(subject)).passed is False


def test_measurements_satisfied_rule_fails(subject):
    bad = mutate(subject, measurement=shortfall_measurement())
    assert MeasurementsSatisfiedRule().evaluate(bad, _compliance(subject)).passed is False


def test_repository_truth_rule_fails(subject):
    bad = mutate(subject, repository_truth=inconsistent_repository_truth())
    assert RepositoryTruthConsistentRule().evaluate(bad, _compliance(subject)).passed is False


def test_disclosure_rule_fails(subject):
    bad = mutate(subject, validation=mutate(subject.validation, checks_run=()))
    assert DisclosurePresentRule().evaluate(bad, _compliance(subject)).passed is False


def test_version_pinned_rule_fails(subject):
    bad = mutate(subject, version="   ")
    assert VersionPinnedRule().evaluate(bad, _compliance(subject)).passed is False


def test_measurement_complete_advisory_rule(subject):
    advisory_shortfall = MeasurementInput.create(
        (
            Measurement.evaluate(
                metric_id="ok",
                value=1,
                threshold=0,
                comparator=MeasurementComparator.GE,
            ),
            Measurement.evaluate(
                metric_id="adv",
                value=1,
                threshold=0,
                comparator=MeasurementComparator.LE,
                severity=RuleSeverity.ADVISORY,
            ),
        )
    )
    bad = mutate(subject, measurement=advisory_shortfall)
    finding = MeasurementCompleteRule().evaluate(bad, _compliance(subject))
    assert finding.passed is False
    assert finding.severity is RuleSeverity.ADVISORY


def test_validation_complete_advisory_rule(subject):
    bad = mutate(subject, validation=mutate(subject.validation, counts={"failed": 1, "total": 5}))
    finding = ValidationCompleteRule().evaluate(bad, _compliance(subject))
    assert finding.passed is False
    assert finding.severity is RuleSeverity.ADVISORY
