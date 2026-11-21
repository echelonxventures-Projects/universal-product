"""TASK-000050 — Certification contracts tests."""

from __future__ import annotations

import pytest

from engine.certification.contracts import (
    CERTIFICATION_AUTHORITY,
    CertificationClass,
    CertificationFinding,
    CertificationRecord,
    CertificationRequest,
    CertificationStatus,
    CertificationSubject,
    CriterionSeverity,
    CriterionStatus,
    canonical_json,
    content_hash,
)
from engine.certification.errors import (
    CertificationIntegrityError,
    CertificationSubjectError,
)
from engine.runtime.disclosure import build_disclosure

from .conftest import mutate


def test_canonical_json_is_stable_and_sorted():
    a = canonical_json({"b": 1, "a": 2})
    b = canonical_json({"a": 2, "b": 1})
    assert a == b == '{"a":2,"b":1}'
    assert content_hash({"a": 1}) == content_hash({"a": 1})
    assert content_hash({"a": 1}) != content_hash({"a": 2})


def test_request_to_dict():
    req = CertificationRequest(target_id="T", version="1.0.0")
    assert req.to_dict() == {
        "target_id": "T",
        "version": "1.0.0",
        "certification_class": "engineering-readiness",
        "strict": False,
    }


def test_finding_properties():
    ok = CertificationFinding("c", CriterionSeverity.BLOCKING, CriterionStatus.PASS)
    assert ok.passed is True and ok.is_blocking_failure is False
    bad = CertificationFinding("c", CriterionSeverity.BLOCKING, CriterionStatus.FAIL)
    assert bad.passed is False and bad.is_blocking_failure is True
    adv = CertificationFinding("c", CriterionSeverity.ADVISORY, CriterionStatus.FAIL)
    assert adv.is_blocking_failure is False
    assert set(ok.to_dict()) == {"criterion_id", "severity", "status", "message", "details"}


def test_subject_from_validation_is_pure_projection(valid_report, valid_evidence):
    subject = CertificationSubject.from_validation(valid_report, valid_evidence, version="1.0.0")
    assert subject.target_id == valid_report.target_id
    assert subject.blueprint_id == valid_report.blueprint_id
    assert subject.version == "1.0.0"
    assert subject.validation_accepted is True
    assert subject.validation_verdict == "pass"
    assert subject.evidence_present is True
    assert len(subject.evidence_sha256) == 64
    assert "provisional-state-disclosure" in subject.checks_run
    assert set(subject.to_dict()) >= {"target_id", "evidence_sha256", "counts"}


def test_subject_tolerates_missing_evidence(valid_report):
    subject = CertificationSubject.from_validation(valid_report, None, version="1.0.0")
    assert subject.evidence_present is False
    assert subject.evidence_sha256 == ""


def test_subject_rejects_empty_report():
    class _Empty:
        target_id = ""

    with pytest.raises(CertificationSubjectError):
        CertificationSubject.from_validation(_Empty(), None, version="1.0.0")


def test_subject_rejects_mismatched_evidence(valid_report, valid_evidence):
    other = dataclass_replace_target(valid_evidence, "OTHER-TARGET")
    with pytest.raises(CertificationSubjectError) as exc:
        CertificationSubject.from_validation(valid_report, other, version="1.0.0")
    assert exc.value.context["evidence_target"] == "OTHER-TARGET"


def dataclass_replace_target(evidence, target_id):
    import dataclasses

    return dataclasses.replace(evidence, target_id=target_id)


def test_record_is_content_addressed_and_deterministic():
    findings = (CertificationFinding("x", CriterionSeverity.BLOCKING, CriterionStatus.PASS),)
    kwargs = dict(
        target_id="UCOS-RUN-BP-DATA-0001-abc",
        blueprint_id="BP-DATA-0001",
        version="1.0.0",
        status=CertificationStatus.CERTIFIED,
        certification_class=CertificationClass.ENGINEERING_READINESS,
        evidence_ref="e" * 64,
        criteria=findings,
        disclosure=build_disclosure(),
    )
    a = CertificationRecord.create(**kwargs)
    b = CertificationRecord.create(**kwargs)
    assert a.certification_id == b.certification_id
    assert a.content_sha256 == b.content_sha256
    assert a.certification_id.startswith("UCOS-CERT-BP-DATA-0001-")
    assert a.authority == CERTIFICATION_AUTHORITY
    assert a.certified is True
    assert a.verify_integrity() is True
    a.require_integrity()  # does not raise


def test_record_detects_mutation():
    record = CertificationRecord.create(
        target_id="T",
        blueprint_id="BP-DATA-0001",
        version="1.0.0",
        status=CertificationStatus.CERTIFIED,
        certification_class=CertificationClass.ENGINEERING_READINESS,
        evidence_ref="e" * 64,
        criteria=(),
        disclosure=build_disclosure(),
    )
    # object.__setattr__ bypasses frozen to simulate tampering
    object.__setattr__(record, "version", "9.9.9")
    assert record.verify_integrity() is False
    with pytest.raises(CertificationIntegrityError):
        record.require_integrity()


def test_record_to_dict_roundtrips_fields():
    record = CertificationRecord.create(
        target_id="T",
        blueprint_id="BP",
        version="1.0.0",
        status=CertificationStatus.NOT_CERTIFIED,
        certification_class=CertificationClass.ENGINEERING_READINESS,
        evidence_ref="",
        criteria=(),
        disclosure=build_disclosure(),
    )
    d = record.to_dict()
    assert d["status"] == "not-certified"
    assert d["certified"] is False
    assert d["content_sha256"] == record.content_sha256


def test_subject_mutation_helper(valid_subject):
    changed = mutate(valid_subject, version="2.0.0")
    assert changed.version == "2.0.0"
    assert valid_subject.version != "2.0.0"
