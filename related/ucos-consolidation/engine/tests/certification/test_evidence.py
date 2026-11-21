"""TASK-000052 — Certification evidence tests."""

from __future__ import annotations

from engine.certification.evidence import (
    EVIDENCE_FORMAT,
    build_certification_evidence,
)


def test_evidence_captures_decision(certified_decision):
    evidence = build_certification_evidence(certified_decision)
    assert evidence.certification_id == certified_decision.certification_id
    assert evidence.certified is True
    assert evidence.status == "certified"
    assert evidence.validation_evidence_ref == certified_decision.record.evidence_ref
    assert evidence.record_sha256 == certified_decision.record.content_sha256
    d = evidence.to_dict()
    assert d["evidence_format"] == EVIDENCE_FORMAT
    assert d["criteria_evaluated"] == list(evidence.criteria_evaluated)
    assert d["counts"] == evidence.counts


def test_evidence_is_deterministic(certified_decision):
    a = build_certification_evidence(certified_decision)
    b = build_certification_evidence(certified_decision)
    assert a.to_dict() == b.to_dict()
    assert a.content_sha256() == b.content_sha256()


def test_evidence_records_blocking_failures(valid_report, artifact_version):
    from engine.certification.engine import certify_validation

    decision = certify_validation(valid_report, None, version=artifact_version)
    evidence = build_certification_evidence(decision)
    assert evidence.certified is False
    assert "validation-evidence-present" in evidence.blocking_failures
