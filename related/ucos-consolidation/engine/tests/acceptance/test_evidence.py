"""EPIC-VAL-002 — Repository Acceptance evidence tests."""

from __future__ import annotations

from engine.acceptance.engine import AcceptanceEngine
from engine.acceptance.evidence import (
    EVIDENCE_FORMAT,
    build_acceptance_evidence,
)

from .conftest import mutate


def test_evidence_captures_accepted_decision(accepted_decision):
    evidence = build_acceptance_evidence(accepted_decision)
    assert evidence.accepted is True
    assert evidence.acceptance_id == accepted_decision.acceptance_id
    assert evidence.subject_ref == accepted_decision.record.evidence_ref
    assert evidence.record_sha256 == accepted_decision.record.content_sha256
    assert len(evidence.gates_evaluated) == 20
    assert evidence.blocking_failures == ()
    d = evidence.to_dict()
    assert d["evidence_format"] == EVIDENCE_FORMAT
    assert d["accepted"] is True


def test_evidence_is_deterministic(accepted_decision):
    a = build_acceptance_evidence(accepted_decision)
    b = build_acceptance_evidence(accepted_decision)
    assert a.to_dict() == b.to_dict()
    assert a.content_sha256() == b.content_sha256()


def test_evidence_records_rejection(valid_subject):
    decision = AcceptanceEngine().accept(mutate(valid_subject, freeze_blockers=("blk",)))
    evidence = build_acceptance_evidence(decision)
    assert evidence.accepted is False
    assert "freeze-readiness" in evidence.blocking_failures
    assert evidence.status == "rejected"
