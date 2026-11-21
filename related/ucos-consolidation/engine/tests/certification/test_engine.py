"""TASK-000051 — Certification decision engine tests."""

from __future__ import annotations

from engine.certification import CertificationStatus
from engine.certification.contracts import (
    CertificationFinding,
    CriterionSeverity,
    CriterionStatus,
)
from engine.certification.criteria import CertificationCriterion
from engine.certification.engine import (
    CertificationEngine,
    certify_validation,
)

from .conftest import mutate


def test_certify_valid_subject_is_certified(valid_subject):
    decision = CertificationEngine().certify(valid_subject)
    assert decision.status is CertificationStatus.CERTIFIED
    assert decision.certified is True
    assert decision.blocking_failures == ()
    assert decision.record.certified is True
    assert decision.record.verify_integrity() is True
    assert decision.certification_id == decision.record.certification_id
    counts = decision.counts()
    assert counts["blocking_failed"] == 0
    assert counts["total"] == len(decision.findings)


def test_certify_is_deterministic_and_reproducible(valid_subject):
    a = CertificationEngine().certify(valid_subject)
    b = CertificationEngine().certify(valid_subject)
    assert a.certification_id == b.certification_id
    assert a.record.content_sha256 == b.record.content_sha256
    assert a.to_dict() == b.to_dict()


def test_missing_evidence_yields_not_certified(valid_report, artifact_version):
    decision = certify_validation(valid_report, None, version=artifact_version)
    assert decision.status is CertificationStatus.NOT_CERTIFIED
    assert "validation-evidence-present" in decision.blocking_failures
    assert decision.record.certified is False


def test_not_certified_when_validation_rejected(valid_subject):
    subject = mutate(valid_subject, validation_accepted=False, validation_verdict="fail")
    decision = CertificationEngine().certify(subject)
    assert decision.status is CertificationStatus.NOT_CERTIFIED
    assert "validation-accepted" in decision.blocking_failures


def test_advisory_failure_does_not_block(valid_subject):
    subject = mutate(valid_subject, counts={"failed": 1, "total": 7})
    decision = CertificationEngine().certify(subject)
    assert decision.status is CertificationStatus.CERTIFIED
    assert "validation-complete" in decision.advisory_failures


def test_engine_accepts_custom_criteria(valid_subject):
    class AlwaysFail(CertificationCriterion):
        criterion_id = "always-fail"
        severity = CriterionSeverity.BLOCKING

        def evaluate(self, subject):
            return CertificationFinding(
                self.criterion_id, self.severity, CriterionStatus.FAIL, "nope"
            )

    engine = CertificationEngine(criteria=[AlwaysFail()])
    assert engine.criterion_ids == ("always-fail",)
    decision = engine.certify(valid_subject)
    assert decision.status is CertificationStatus.NOT_CERTIFIED


def test_certify_validation_convenience(valid_report, valid_evidence, artifact_version):
    decision = certify_validation(valid_report, valid_evidence, version=artifact_version)
    assert decision.certified is True
    assert decision.to_dict()["record"]["evidence_ref"] == decision.record.evidence_ref
