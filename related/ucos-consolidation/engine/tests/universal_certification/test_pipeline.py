"""UCOS-EPIC-006 — Certification pipeline (end-to-end) tests."""

from __future__ import annotations

from engine.universal_certification import (
    ApprovalState,
    AuditEventType,
    CertificationPipeline,
)

from .conftest import broken_evidence


def test_run_certified_with_approver_is_approved(subject):
    outcome = CertificationPipeline().run(subject, approver="certification-admin", rationale="ok")
    assert outcome.certified is True
    assert outcome.approved is True
    assert outcome.approval.state is ApprovalState.APPROVED
    assert outcome.certificate.verify_integrity() is True
    event_types = {e["event_type"] for e in outcome.audit_entries}
    assert AuditEventType.CERTIFIED.value in event_types
    assert AuditEventType.CERTIFICATE_ISSUED.value in event_types
    assert AuditEventType.EVIDENCE_RECORDED.value in event_types
    assert AuditEventType.APPROVAL_SUBMITTED.value in event_types
    assert AuditEventType.APPROVED.value in event_types


def test_run_certified_without_approver_stays_pending(subject):
    outcome = CertificationPipeline().run(subject)
    assert outcome.certified is True
    assert outcome.approved is False
    assert outcome.approval.state is ApprovalState.PENDING


def test_run_no_auto_submit_stays_draft(subject):
    outcome = CertificationPipeline().run(subject, auto_submit=False)
    assert outcome.approval.state is ApprovalState.DRAFT


def test_run_not_certified_is_never_submitted(subject):
    outcome = CertificationPipeline().run(broken_evidence(subject), approver="admin")
    assert outcome.certified is False
    assert outcome.approved is False
    assert outcome.approval.state is ApprovalState.DRAFT
    event_types = {e["event_type"] for e in outcome.audit_entries}
    assert AuditEventType.NOT_CERTIFIED.value in event_types
    assert AuditEventType.APPROVAL_SUBMITTED.value not in event_types


def test_pipeline_audit_ledger_accumulates_and_verifies(subject):
    pipeline = CertificationPipeline()
    pipeline.run(subject, approver="admin")
    pipeline.run(subject, approver="admin")
    assert pipeline.audit.verify() is True
    assert len(pipeline.audit) > 0


def test_outcome_is_deterministic(subject):
    a = CertificationPipeline().run(subject, approver="admin", rationale="r")
    b = CertificationPipeline().run(subject, approver="admin", rationale="r")
    assert a.to_dict() == b.to_dict()


def test_pipeline_exposes_engine(subject):
    pipeline = CertificationPipeline()
    assert pipeline.engine.rule_ids == CertificationPipeline().engine.rule_ids
