"""TASK-000050 — Certification criteria tests."""

from __future__ import annotations

from engine.certification.criteria import (
    DisclosureValidatedCriterion,
    ValidationAcceptedCriterion,
    ValidationCompleteCriterion,
    ValidationEvidencePresentCriterion,
    VersionPinnedCriterion,
    default_criteria,
)

from .conftest import mutate


def test_default_suite_is_ordered_and_complete():
    ids = [c.criterion_id for c in default_criteria()]
    assert ids == sorted(ids)
    assert set(ids) == {
        "provisional-state-disclosed",
        "validation-accepted",
        "validation-complete",
        "validation-evidence-present",
        "version-pinned",
    }


def test_all_criteria_pass_for_valid_subject(valid_subject):
    for criterion in default_criteria():
        finding = criterion.evaluate(valid_subject)
        assert finding.passed, f"{criterion.criterion_id} unexpectedly failed"


def test_validation_accepted_fails_when_not_accepted(valid_subject):
    subject = mutate(valid_subject, validation_accepted=False, validation_verdict="fail")
    finding = ValidationAcceptedCriterion().evaluate(subject)
    assert finding.is_blocking_failure


def test_validation_accepted_fails_on_non_pass_verdict(valid_subject):
    subject = mutate(valid_subject, validation_verdict="fail")
    finding = ValidationAcceptedCriterion().evaluate(subject)
    assert finding.is_blocking_failure


def test_evidence_present_fails_when_absent(valid_subject):
    subject = mutate(valid_subject, evidence_present=False, evidence_sha256="")
    finding = ValidationEvidencePresentCriterion().evaluate(subject)
    assert finding.is_blocking_failure


def test_disclosure_criterion_fails_when_check_absent(valid_subject):
    subject = mutate(valid_subject, checks_run=("signature-present",))
    finding = DisclosureValidatedCriterion().evaluate(subject)
    assert finding.is_blocking_failure


def test_disclosure_criterion_fails_when_check_failed(valid_subject):
    subject = mutate(
        valid_subject,
        blocking_failures=("provisional-state-disclosure",),
    )
    finding = DisclosureValidatedCriterion().evaluate(subject)
    assert finding.is_blocking_failure


def test_version_pinned_fails_on_blank(valid_subject):
    subject = mutate(valid_subject, version="   ")
    finding = VersionPinnedCriterion().evaluate(subject)
    assert finding.is_blocking_failure


def test_validation_complete_is_advisory(valid_subject):
    subject = mutate(valid_subject, counts={"failed": 1, "total": 7})
    finding = ValidationCompleteCriterion().evaluate(subject)
    assert finding.status.value == "fail"
    assert finding.is_blocking_failure is False


def test_validation_complete_passes_when_none_failed(valid_subject):
    subject = mutate(valid_subject, counts={"failed": 0, "total": 7})
    finding = ValidationCompleteCriterion().evaluate(subject)
    assert finding.passed
