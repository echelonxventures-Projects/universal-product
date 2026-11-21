"""UCOS-EPIC-006 — Certification evidence tests."""

from __future__ import annotations

from engine.universal_certification import (
    EVIDENCE_FORMAT,
    UniversalCertificationEngine,
    build_certification_evidence,
)


def test_evidence_references_every_consumed_input(certified_decision):
    evidence = build_certification_evidence(certified_decision)
    cert = certified_decision.certificate
    assert evidence.validation_evidence_ref == cert.validation_evidence_ref
    assert evidence.measurement_digest == cert.measurement_digest
    assert evidence.repository_truth_digest == cert.repository_truth_digest
    assert evidence.compliance_digest == cert.compliance_digest
    assert evidence.certificate_sha256 == cert.content_sha256
    assert evidence.compliance_status == "conformant"
    assert evidence.to_dict()["evidence_format"] == EVIDENCE_FORMAT


def test_evidence_is_deterministic(subject):
    a = build_certification_evidence(UniversalCertificationEngine().certify(subject))
    b = build_certification_evidence(UniversalCertificationEngine().certify(subject))
    assert a.content_sha256() == b.content_sha256()
    assert a.to_dict() == b.to_dict()


def test_evidence_captures_rules_and_counts(certified_decision):
    evidence = build_certification_evidence(certified_decision)
    assert evidence.rules_evaluated == tuple(f.rule_id for f in certified_decision.findings)
    assert evidence.counts == certified_decision.counts()
    assert evidence.blocking_failures == ()
