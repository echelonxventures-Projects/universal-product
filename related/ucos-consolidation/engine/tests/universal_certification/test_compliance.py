"""UCOS-EPIC-006 — Compliance Engine tests."""

from __future__ import annotations

from engine.universal_certification import (
    ComplianceEngine,
    ComplianceFrame,
    ComplianceStatus,
    MeasurementInput,
    RuleSeverity,
    UniversalCertificationSubject,
    default_frames,
)
from engine.universal_certification.contracts import ComplianceFinding

from .conftest import inconsistent_repository_truth, mutate, shortfall_measurement


def _subject(validation, measurement, repository_truth, version="1.0.0"):
    return UniversalCertificationSubject.create(
        validation=validation,
        measurement=measurement,
        repository_truth=repository_truth,
        version=version,
    )


def test_default_frames_are_sorted_and_five():
    ids = [f.frame_id for f in default_frames()]
    assert ids == sorted(ids)
    assert len(ids) == 5


def test_conformant_subject_is_conformant(subject):
    report = ComplianceEngine().evaluate(subject)
    assert report.conformant is True
    assert report.status is ComplianceStatus.CONFORMANT
    assert report.non_conformances == ()
    assert report.counts()["blocking_non_conformant"] == 0
    assert report.digest() == report.digest()


def test_validation_rejection_is_non_conformant(subject):
    bad = mutate(subject.validation, accepted=False, verdict="fail")
    report = ComplianceEngine().evaluate(mutate(subject, validation=bad))
    assert report.conformant is False
    assert "validation-conformance" in report.non_conformances


def test_missing_evidence_is_non_conformant(subject):
    bad = mutate(subject.validation, evidence_present=False, evidence_sha256="")
    report = ComplianceEngine().evaluate(mutate(subject, validation=bad))
    assert "validation-evidence-conformance" in report.non_conformances


def test_disclosure_absent_is_non_conformant(subject):
    bad = mutate(subject.validation, checks_run=())
    report = ComplianceEngine().evaluate(mutate(subject, validation=bad))
    assert "disclosure-conformance" in report.non_conformances


def test_measurement_shortfall_is_non_conformant(subject):
    report = ComplianceEngine().evaluate(mutate(subject, measurement=shortfall_measurement()))
    assert "measurement-conformance" in report.non_conformances


def test_empty_measurements_is_non_conformant(subject):
    report = ComplianceEngine().evaluate(mutate(subject, measurement=MeasurementInput.create(())))
    assert "measurement-conformance" in report.non_conformances


def test_inconsistent_repository_truth_is_non_conformant(subject):
    report = ComplianceEngine().evaluate(
        mutate(subject, repository_truth=inconsistent_repository_truth())
    )
    assert "repository-truth-conformance" in report.non_conformances


def test_custom_frame_suite():
    class AlwaysNonConformant(ComplianceFrame):
        frame_id = "always-nc"
        severity = RuleSeverity.BLOCKING

        def evaluate(self, subject):
            return ComplianceFinding(
                self.frame_id, self.severity, ComplianceStatus.NON_CONFORMANT, "no"
            )

    engine = ComplianceEngine(frames=[AlwaysNonConformant()])
    assert engine.frame_ids == ("always-nc",)


def test_advisory_nonconformance_does_not_block(subject):
    class AdvisoryNC(ComplianceFrame):
        frame_id = "advisory-nc"
        severity = RuleSeverity.ADVISORY

        def evaluate(self, subject):
            return ComplianceFinding(
                self.frame_id, self.severity, ComplianceStatus.NON_CONFORMANT, "meh"
            )

    report = ComplianceEngine(frames=[AdvisoryNC()]).evaluate(subject)
    assert report.conformant is True
    assert report.non_conformances == ()
    assert report.to_dict()["counts"]["non_conformant"] == 1
