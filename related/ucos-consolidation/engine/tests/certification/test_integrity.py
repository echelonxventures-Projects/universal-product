"""Constitutional certification integrity tests (EPIC-008 strengthening).

Exercises the additive integrity layer over a *population* of certification
determinations: duplicate detection (zero duplicate certification / evidence),
overlap detection, drift detection, evidence↔record traceability, completeness,
the append-only dedup-aware register, the fail-closed enforcement gate, and
deterministic evidence generation. Drives the real Certification Engine over the
genuine validated artifact assembled by the package conftest.
"""

from __future__ import annotations

import dataclasses

import pytest

from engine.certification import (
    CertificationEngine,
    ConstitutionalIntegrityError,
    DuplicateCertificationError,
    build_certification_evidence,
)
from engine.certification.contracts import CriterionSeverity, CriterionStatus
from engine.certification.integrity import (
    INTEGRITY_EVIDENCE_FORMAT,
    INTEGRITY_REPORT_FORMAT,
    CertificationRegister,
    IntegrityFinding,
    IntegrityReport,
    build_integrity_evidence,
    enforce_integrity,
    verify_certification_integrity,
)

from .conftest import mutate


# --------------------------------------------------------------------------- helpers
def _pair(subject):
    """Certify ``subject`` and return its (record, evidence) pair."""
    decision = CertificationEngine().certify(subject)
    return decision.record, build_certification_evidence(decision)


def _finding(report: IntegrityReport, check_id: str) -> IntegrityFinding:
    return next(f for f in report.findings if f.check_id == check_id)


# --------------------------------------------------------------------------- clean population
def test_clean_population_passes_all_checks(valid_subject):
    record_a, evidence_a = _pair(valid_subject)
    record_b, evidence_b = _pair(mutate(valid_subject, target_id="UCOS-RUN-OTHER-0002"))
    report = verify_certification_integrity(
        [record_a, record_b],
        [evidence_a, evidence_b],
        expected_targets={record_a.target_id, record_b.target_id},
    )
    assert report.passed is True
    assert report.blocking_failures == ()
    assert report.records_examined == 2
    assert report.evidence_examined == 2
    assert all(f.status is CriterionStatus.PASS for f in report.findings)
    # findings are emitted in stable id order (determinism)
    assert [f.check_id for f in report.findings] == sorted(f.check_id for f in report.findings)
    assert report.to_dict()["report_format"] == INTEGRITY_REPORT_FORMAT
    assert report.to_dict()["verdict"] == "pass"


def test_verify_is_deterministic(valid_subject):
    record, evidence = _pair(valid_subject)
    a = verify_certification_integrity([record], [evidence])
    b = verify_certification_integrity([record], [evidence])
    assert a.to_dict() == b.to_dict()


# --------------------------------------------------------------------------- duplicate cert
def test_duplicate_certification_detected(valid_subject):
    # same (target_id, version) certified under two different blueprints → two
    # distinct certification ids for one subject == duplicate certification.
    record_a, evidence_a = _pair(valid_subject)
    record_b, evidence_b = _pair(mutate(valid_subject, blueprint_id="BP-OTHER"))
    assert record_a.target_id == record_b.target_id
    assert record_a.version == record_b.version
    assert record_a.certification_id != record_b.certification_id
    report = verify_certification_integrity([record_a, record_b], [evidence_a, evidence_b])
    dup = _finding(report, "no-duplicate-certification")
    assert dup.status is CriterionStatus.FAIL
    assert dup.details["subjects_certified_more_than_once"]
    assert report.passed is False


def test_id_content_conflict_detected(valid_subject):
    record, evidence = _pair(valid_subject)
    forged = dataclasses.replace(record, content_sha256="0" * 64)  # same id, new hash
    report = verify_certification_integrity([record, forged], [evidence])
    dup = _finding(report, "no-duplicate-certification")
    assert dup.status is CriterionStatus.FAIL
    assert record.certification_id in dup.details["id_content_conflicts"]
    # a forged record also trips the integrity check
    assert _finding(report, "record-integrity").status is CriterionStatus.FAIL


# --------------------------------------------------------------------------- duplicate evidence
def test_duplicate_evidence_detected(valid_subject):
    record, evidence = _pair(valid_subject)
    report = verify_certification_integrity([record], [evidence, evidence])
    dup = _finding(report, "no-duplicate-evidence")
    assert dup.status is CriterionStatus.FAIL
    assert record.certification_id in dup.details["duplicate_evidence_for"]


# --------------------------------------------------------------------------- overlap
def test_overlapping_certification_detected(valid_subject):
    # same target certified under two versions → overlapping active certifications.
    record_a, evidence_a = _pair(valid_subject)
    record_b, evidence_b = _pair(mutate(valid_subject, version="2.0.0"))
    assert record_a.target_id == record_b.target_id
    report = verify_certification_integrity([record_a, record_b], [evidence_a, evidence_b])
    overlap = _finding(report, "no-overlapping-certification")
    assert overlap.status is CriterionStatus.FAIL
    assert record_a.target_id in overlap.details["targets_with_multiple_certified"]


# --------------------------------------------------------------------------- drift
def test_certification_drift_detected(valid_subject):
    record_a, evidence_a = _pair(valid_subject)
    record_b, evidence_b = _pair(mutate(valid_subject, blueprint_id="BP-DRIFT"))
    report = verify_certification_integrity([record_a, record_b], [evidence_a, evidence_b])
    drift = _finding(report, "no-certification-drift")
    assert drift.status is CriterionStatus.FAIL
    assert (
        f"{record_a.target_id}@{record_a.version}"
        in drift.details["subjects_with_divergent_records"]
    )


# --------------------------------------------------------------------------- traceability
def test_traceability_orphan_evidence(valid_subject):
    _record, evidence = _pair(valid_subject)
    report = verify_certification_integrity([], [evidence])
    trace = _finding(report, "evidence-record-traceability")
    assert trace.status is CriterionStatus.FAIL
    assert evidence.certification_id in trace.details["orphan_evidence"]


def test_traceability_missing_evidence(valid_subject):
    record, _evidence = _pair(valid_subject)
    report = verify_certification_integrity([record], [])
    trace = _finding(report, "evidence-record-traceability")
    assert trace.status is CriterionStatus.FAIL
    assert any("no evidence" in p for p in trace.details["problems"])


def test_traceability_broken_validation_chain(valid_subject):
    record, evidence = _pair(valid_subject)
    broken = dataclasses.replace(evidence, validation_evidence_ref="tampered")
    report = verify_certification_integrity([record], [broken])
    trace = _finding(report, "evidence-record-traceability")
    assert trace.status is CriterionStatus.FAIL
    assert any("chain broken" in p for p in trace.details["problems"])


def test_traceability_validation_evidence_index(valid_subject):
    record, evidence = _pair(valid_subject)
    # index that does NOT contain the referenced validation evidence
    missing = verify_certification_integrity([record], [evidence], validation_evidence_index={})
    assert _finding(missing, "evidence-record-traceability").status is CriterionStatus.FAIL
    # index that DOES resolve the reference
    present = verify_certification_integrity(
        [record], [evidence], validation_evidence_index={record.evidence_ref: "vref"}
    )
    assert _finding(present, "evidence-record-traceability").status is CriterionStatus.PASS


def test_traceability_ignores_repeated_evidence_for_pairing(valid_subject):
    # a repeated evidence entry (duplicate) must not itself break pairing/traceability
    record, evidence = _pair(valid_subject)
    report = verify_certification_integrity([record], [evidence, evidence])
    assert _finding(report, "evidence-record-traceability").status is CriterionStatus.PASS


# --------------------------------------------------------------------------- completeness
def test_completeness_missing_expected_target(valid_subject):
    record, evidence = _pair(valid_subject)
    report = verify_certification_integrity(
        [record], [evidence], expected_targets={record.target_id, "UCOS-RUN-ABSENT"}
    )
    comp = _finding(report, "certification-completeness")
    assert comp.status is CriterionStatus.FAIL
    assert "UCOS-RUN-ABSENT" in comp.details["uncertified_expected_targets"]


def test_completeness_certified_without_validation_evidence(valid_subject):
    record, evidence = _pair(valid_subject)
    stripped = dataclasses.replace(record, evidence_ref="")
    report = verify_certification_integrity([stripped], [evidence])
    comp = _finding(report, "certification-completeness")
    assert comp.status is CriterionStatus.FAIL
    incomplete = comp.details["incomplete_certifications"]
    assert any("without validation evidence" in c for c in incomplete)


def test_completeness_certified_without_evidence_record(valid_subject):
    record, _evidence = _pair(valid_subject)
    report = verify_certification_integrity([record], [])
    comp = _finding(report, "certification-completeness")
    assert comp.status is CriterionStatus.FAIL
    assert any("without evidence record" in c for c in comp.details["incomplete_certifications"])


def test_completeness_certified_evidence_with_blocking_failures(valid_subject):
    record, evidence = _pair(valid_subject)
    flawed = dataclasses.replace(evidence, blocking_failures=("some-check",))
    report = verify_certification_integrity([record], [flawed])
    comp = _finding(report, "certification-completeness")
    assert comp.status is CriterionStatus.FAIL
    assert any("blocking failures" in c for c in comp.details["incomplete_certifications"])


def test_completeness_skips_not_certified_records(valid_subject):
    subject = mutate(valid_subject, validation_accepted=False, validation_verdict="fail")
    record, evidence = _pair(subject)  # NOT_CERTIFIED
    report = verify_certification_integrity([record], [evidence])
    # a not-certified record is not "incomplete"; completeness passes for it
    assert _finding(report, "certification-completeness").status is CriterionStatus.PASS


# --------------------------------------------------------------------------- record integrity
def test_record_integrity_detects_tamper(valid_subject):
    record, evidence = _pair(valid_subject)
    object.__setattr__(record, "version", "9.9.9")  # break the content hash
    report = verify_certification_integrity([record], [evidence])
    integ = _finding(report, "record-integrity")
    assert integ.status is CriterionStatus.FAIL
    assert record.certification_id in integ.details["tampered"]


# --------------------------------------------------------------------------- register (fail-closed)
def test_register_adds_and_is_idempotent(valid_subject):
    register = CertificationRegister()
    record, evidence = _pair(valid_subject)
    assert register.register(record, evidence) is True
    assert register.register(record, evidence) is False  # idempotent no-op
    assert len(register) == 1
    assert register.records == (record,)
    assert register.evidences == (evidence,)
    assert register.to_dict()["count"] == 1
    assert record.certification_id in register.to_dict()["certification_ids"]


def test_register_rejects_conflicting_subject(valid_subject):
    register = CertificationRegister()
    record_a, evidence_a = _pair(valid_subject)
    record_b, evidence_b = _pair(mutate(valid_subject, blueprint_id="BP-OTHER"))
    register.register(record_a, evidence_a)
    with pytest.raises(DuplicateCertificationError):
        register.register(record_b, evidence_b)
    assert len(register) == 1


def test_register_rejects_mismatched_evidence_id(valid_subject):
    register = CertificationRegister()
    record, evidence = _pair(valid_subject)
    wrong = dataclasses.replace(evidence, certification_id="UCOS-CERT-WRONG-0000")
    with pytest.raises(DuplicateCertificationError):
        register.register(record, wrong)


def test_register_rejects_mismatched_evidence_hash(valid_subject):
    register = CertificationRegister()
    record, evidence = _pair(valid_subject)
    wrong = dataclasses.replace(evidence, record_sha256="0" * 64)
    with pytest.raises(DuplicateCertificationError):
        register.register(record, wrong)


def test_register_rejects_tampered_record(valid_subject):
    from engine.certification.errors import CertificationIntegrityError

    register = CertificationRegister()
    record, evidence = _pair(valid_subject)
    object.__setattr__(record, "version", "9.9.9")
    with pytest.raises(CertificationIntegrityError):
        register.register(record, evidence)


def test_register_verify_delegates_to_batch_suite(valid_subject):
    register = CertificationRegister()
    record, evidence = _pair(valid_subject)
    register.register(record, evidence)
    report = register.verify(expected_targets={record.target_id})
    assert report.passed is True


# --------------------------------------------------------------------------- enforcement gate
def test_enforce_returns_report_when_passing(valid_subject):
    record, evidence = _pair(valid_subject)
    report = verify_certification_integrity([record], [evidence])
    assert enforce_integrity(report, strict=True) is report


def test_enforce_raises_on_blocking_failure(valid_subject):
    record, _evidence = _pair(valid_subject)
    report = verify_certification_integrity([record], [])  # missing evidence
    assert report.passed is False
    with pytest.raises(ConstitutionalIntegrityError):
        enforce_integrity(report, strict=True)


def test_enforce_non_strict_does_not_raise(valid_subject):
    record, _evidence = _pair(valid_subject)
    report = verify_certification_integrity([record], [])
    assert enforce_integrity(report, strict=False) is report


# --------------------------------------------------------------------------- evidence generation
def test_build_integrity_evidence_is_deterministic(valid_subject):
    record, evidence = _pair(valid_subject)
    report = verify_certification_integrity([record], [evidence])
    a = build_integrity_evidence(report)
    b = build_integrity_evidence(report)
    assert a.to_dict() == b.to_dict()
    assert a.content_sha256() == b.content_sha256()
    doc = a.to_dict()
    assert doc["evidence_format"] == INTEGRITY_EVIDENCE_FORMAT
    assert doc["verdict"] == "pass"
    assert doc["passed"] is True
    assert set(doc["checks_evaluated"]) == {f.check_id for f in report.findings}


# --------------------------------------------------------------------------- finding / report units
def test_integrity_finding_serialization_and_props():
    passing = IntegrityFinding(
        check_id="c", severity=CriterionSeverity.BLOCKING, status=CriterionStatus.PASS
    )
    assert passing.passed is True
    assert passing.is_blocking_failure is False
    failing = IntegrityFinding(
        check_id="c", severity=CriterionSeverity.BLOCKING, status=CriterionStatus.FAIL
    )
    assert failing.is_blocking_failure is True
    assert failing.to_dict()["status"] == "fail"


def test_advisory_failure_does_not_block_report():
    advisory = IntegrityFinding(
        check_id="advisory-check",
        severity=CriterionSeverity.ADVISORY,
        status=CriterionStatus.FAIL,
    )
    report = IntegrityReport(findings=(advisory,), records_examined=0, evidence_examined=0)
    assert report.passed is True  # advisory failure never blocks (fail-closed on blocking only)
    assert report.blocking_failures == ()
    assert report.advisory_failures == ("advisory-check",)
    assert report.counts()["advisory_failed"] == 1
