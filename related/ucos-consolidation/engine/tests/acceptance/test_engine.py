"""EPIC-VAL-002 — Repository Acceptance decision engine tests."""

from __future__ import annotations

import pytest

from engine.acceptance.contracts import (
    AcceptanceFinding,
    AcceptanceStatus,
    GateSeverity,
    GateStatus,
)
from engine.acceptance.engine import (
    AcceptanceEngine,
    accept_repository,
    enforce_acceptance,
)
from engine.acceptance.errors import AcceptanceRejectedError
from engine.acceptance.gates import AcceptanceGate

from .conftest import mutate


def test_accept_valid_subject_is_accepted(valid_subject):
    decision = AcceptanceEngine().accept(valid_subject)
    assert decision.status is AcceptanceStatus.ACCEPTED
    assert decision.accepted is True
    assert decision.blocking_failures == ()
    assert decision.advisory_failures == ()
    assert decision.record.accepted is True
    assert decision.record.verify_integrity() is True
    assert decision.acceptance_id == decision.record.acceptance_id
    assert decision.evidence_ref == valid_subject.digest()
    counts = decision.counts()
    assert counts["blocking_failed"] == 0
    assert counts["total"] == 20
    assert decision.to_dict()["accepted"] is True


def test_accept_is_deterministic_and_reproducible(valid_subject):
    a = AcceptanceEngine().accept(valid_subject)
    b = AcceptanceEngine().accept(valid_subject)
    assert a.acceptance_id == b.acceptance_id
    assert a.record.content_sha256 == b.record.content_sha256
    assert a.to_dict() == b.to_dict()


def test_reject_on_blocking_failure(valid_subject):
    decision = AcceptanceEngine().accept(mutate(valid_subject, freeze_blockers=("open-pr",)))
    assert decision.status is AcceptanceStatus.REJECTED
    assert decision.accepted is False
    assert "freeze-readiness" in decision.blocking_failures
    assert decision.record.accepted is False


def test_advisory_failure_does_not_block():
    class AdvisoryFail(AcceptanceGate):
        gate_id = "advisory-signal"
        severity = GateSeverity.ADVISORY

        def evaluate(self, subject):
            return AcceptanceFinding(self.gate_id, self.severity, GateStatus.FAIL, "advisory")

    from engine.acceptance.contracts import RepositorySubject

    subject = RepositorySubject(repository_id="R", epic_id="E")
    decision = AcceptanceEngine(gates=[AdvisoryFail()]).accept(subject)
    assert decision.status is AcceptanceStatus.ACCEPTED
    assert "advisory-signal" in decision.advisory_failures
    assert decision.blocking_failures == ()


def test_engine_gate_ids_sorted(valid_subject):
    engine = AcceptanceEngine()
    assert engine.gate_ids == tuple(sorted(engine.gate_ids))


def test_accept_repository_from_mapping(acceptable_facts):
    decision = accept_repository(acceptable_facts)
    assert decision.accepted is True


def test_accept_repository_from_subject(valid_subject):
    decision = accept_repository(valid_subject)
    assert decision.accepted is True


def test_enforce_acceptance_strict_raises_on_rejection(valid_subject):
    decision = AcceptanceEngine().accept(mutate(valid_subject, context_assimilated=False))
    with pytest.raises(AcceptanceRejectedError) as exc:
        enforce_acceptance(decision, strict=True)
    assert "context-assimilation" in exc.value.context["blocking_failures"]


def test_enforce_acceptance_strict_passes_on_acceptance(accepted_decision):
    assert enforce_acceptance(accepted_decision, strict=True) is accepted_decision


def test_enforce_acceptance_non_strict_returns_rejected(valid_subject):
    decision = AcceptanceEngine().accept(mutate(valid_subject, freeze_blockers=("x",)))
    # non-strict never raises, even on rejection
    assert enforce_acceptance(decision) is decision
