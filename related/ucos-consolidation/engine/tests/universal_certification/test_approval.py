"""UCOS-EPIC-006 — Approval workflow tests."""

from __future__ import annotations

import pytest

from engine.universal_certification import (
    ApprovalAction,
    ApprovalState,
    ApprovalWorkflow,
    UniversalCertificationEngine,
)
from engine.universal_certification.approval import GENESIS_HASH
from engine.universal_certification.errors import ApprovalWorkflowError

from .conftest import broken_evidence, mutate


@pytest.fixture
def not_certified_decision(subject):
    return UniversalCertificationEngine().certify(broken_evidence(subject))


def test_requires_a_decision():
    with pytest.raises(ApprovalWorkflowError):
        ApprovalWorkflow(object())  # type: ignore[arg-type]


def test_submit_then_approve_certified(certified_decision):
    wf = ApprovalWorkflow(certified_decision)
    assert wf.state is ApprovalState.DRAFT
    assert wf.head_hash == GENESIS_HASH
    wf.submit(actor="requester")
    assert wf.state is ApprovalState.PENDING
    record = wf.approve(actor="certification-admin", rationale="looks good")
    assert wf.state is ApprovalState.APPROVED
    assert wf.approved is True
    assert wf.is_terminal is True
    assert record.action is ApprovalAction.APPROVE
    assert wf.verify() is True


def test_cannot_approve_not_certified(not_certified_decision):
    wf = ApprovalWorkflow(not_certified_decision)
    wf.submit(actor="requester")
    with pytest.raises(ApprovalWorkflowError):
        wf.approve(actor="admin")
    assert wf.state is ApprovalState.PENDING


def test_reject_and_withdraw(certified_decision):
    wf = ApprovalWorkflow(certified_decision)
    wf.submit(actor="r")
    wf.reject(actor="admin", rationale="policy")
    assert wf.state is ApprovalState.REJECTED

    wf2 = ApprovalWorkflow(certified_decision)
    wf2.submit(actor="r")
    wf2.withdraw(actor="r", rationale="changed mind")
    assert wf2.state is ApprovalState.WITHDRAWN


def test_invalid_transitions(certified_decision):
    wf = ApprovalWorkflow(certified_decision)
    # cannot approve before submit
    with pytest.raises(ApprovalWorkflowError):
        wf.approve(actor="admin")
    wf.submit(actor="r")
    # cannot submit twice
    with pytest.raises(ApprovalWorkflowError):
        wf.submit(actor="r")
    wf.approve(actor="admin")
    # cannot act after terminal
    with pytest.raises(ApprovalWorkflowError):
        wf.reject(actor="admin")


def test_actor_and_rationale_validation(certified_decision):
    wf = ApprovalWorkflow(certified_decision)
    with pytest.raises(ApprovalWorkflowError):
        wf.submit(actor="")
    with pytest.raises(ApprovalWorkflowError):
        wf.submit(actor="r", rationale=123)  # type: ignore[arg-type]


def test_hash_chain_is_tamper_evident(certified_decision):
    wf = ApprovalWorkflow(certified_decision)
    wf.submit(actor="r")
    wf.approve(actor="admin")
    assert wf.verify() is True
    # tamper with a record via the private list
    original = wf._records[0]  # noqa: SLF001 - test introspection
    wf._records[0] = mutate(original, actor="attacker")  # noqa: SLF001
    assert wf.verify() is False


def test_broken_prev_link_breaks_approval_chain(certified_decision):
    wf = ApprovalWorkflow(certified_decision)
    wf.submit(actor="r")
    wf.approve(actor="admin")
    wf._records[1] = mutate(wf._records[1], prev_hash="f" * 64)  # noqa: SLF001
    assert wf.verify() is False


def test_to_dict_and_records_snapshot(certified_decision):
    wf = ApprovalWorkflow(certified_decision)
    wf.submit(actor="r")
    payload = wf.to_dict()
    assert payload["state"] == "pending"
    assert payload["certification_id"] == certified_decision.certification_id
    assert len(wf.records) == 1
