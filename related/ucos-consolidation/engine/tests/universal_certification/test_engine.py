"""UCOS-EPIC-006 — Universal Certification Engine decision tests."""

from __future__ import annotations

from engine.universal_certification import (
    CertificationStatus,
    Measurement,
    MeasurementComparator,
    MeasurementInput,
    RuleSeverity,
    UniversalCertificationEngine,
)
from engine.universal_certification.contracts import RuleFinding, RuleStatus
from engine.universal_certification.rules import CertificationRule

from .conftest import (
    broken_evidence,
    inconsistent_repository_truth,
    mutate,
    shortfall_measurement,
)


def test_certify_conformant_subject_is_certified(subject):
    decision = UniversalCertificationEngine().certify(subject)
    assert decision.status is CertificationStatus.CERTIFIED
    assert decision.certified is True
    assert decision.blocking_failures == ()
    assert decision.certificate.certified is True
    assert decision.certificate.verify_integrity() is True
    assert decision.certification_id == decision.certificate.certification_id
    assert decision.compliance.conformant is True
    counts = decision.counts()
    assert counts["blocking_failed"] == 0
    assert counts["total"] == len(decision.findings)


def test_certify_is_deterministic_and_reproducible(subject):
    a = UniversalCertificationEngine().certify(subject)
    b = UniversalCertificationEngine().certify(subject)
    assert a.certification_id == b.certification_id
    assert a.certificate.content_sha256 == b.certificate.content_sha256
    assert a.to_dict() == b.to_dict()


def test_missing_evidence_yields_not_certified(subject):
    decision = UniversalCertificationEngine().certify(broken_evidence(subject))
    assert decision.status is CertificationStatus.NOT_CERTIFIED
    assert "validation-evidence-present" in decision.blocking_failures
    assert decision.certificate.certified is False


def test_measurement_shortfall_yields_not_certified(subject):
    bad = mutate(subject, measurement=shortfall_measurement())
    decision = UniversalCertificationEngine().certify(bad)
    assert decision.status is CertificationStatus.NOT_CERTIFIED
    assert "measurements-satisfied" in decision.blocking_failures


def test_inconsistent_repository_truth_yields_not_certified(subject):
    bad = mutate(subject, repository_truth=inconsistent_repository_truth())
    decision = UniversalCertificationEngine().certify(bad)
    assert decision.status is CertificationStatus.NOT_CERTIFIED
    assert "repository-truth-consistent" in decision.blocking_failures


def test_advisory_failure_does_not_block(subject):
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
    decision = UniversalCertificationEngine().certify(bad)
    assert decision.status is CertificationStatus.CERTIFIED
    assert "measurement-complete" in decision.advisory_failures


def test_engine_accepts_custom_rules(subject):
    class AlwaysFail(CertificationRule):
        rule_id = "always-fail"
        severity = RuleSeverity.BLOCKING

        def evaluate(self, subject, compliance):
            return RuleFinding(self.rule_id, self.severity, RuleStatus.FAIL, "nope")

    engine = UniversalCertificationEngine(rules=[AlwaysFail()])
    assert engine.rule_ids == ("always-fail",)
    decision = engine.certify(subject)
    assert decision.status is CertificationStatus.NOT_CERTIFIED


def test_certify_inputs_convenience(validation_input, measurement_input, repository_truth_input):
    decision = UniversalCertificationEngine().certify_inputs(
        validation=validation_input,
        measurement=measurement_input,
        repository_truth=repository_truth_input,
        version="1.0.0",
    )
    assert decision.certified is True
    assert decision.compliance.conformant is True


def test_engine_accepts_explicit_compliance_engine(subject):
    from engine.universal_certification import ComplianceEngine

    engine = UniversalCertificationEngine(compliance_engine=ComplianceEngine())
    assert engine.certify(subject).certified is True


def test_engine_frame_and_rule_ids(subject):
    engine = UniversalCertificationEngine()
    assert len(engine.rule_ids) == 10
    assert len(engine.frame_ids) == 5
