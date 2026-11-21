"""EPIC-VAL-002 — Repository Readiness (freeze-readiness) tests."""

from __future__ import annotations

from engine.acceptance.engine import AcceptanceEngine
from engine.acceptance.readiness import (
    NOT_READY,
    READINESS_FORMAT,
    READY,
    build_repository_readiness,
)

from .conftest import mutate


def test_readiness_ready_for_accepted_decision(accepted_decision):
    readiness = build_repository_readiness(accepted_decision)
    assert readiness.freeze_ready is True
    assert readiness.verdict == READY
    assert readiness.ready is True
    assert readiness.gates_total == 20
    assert readiness.gates_passed == 20
    assert readiness.blocking_failures == ()
    assert readiness.gate_status["coverage-complete"] == "pass"
    d = readiness.to_dict()
    assert d["readiness_format"] == READINESS_FORMAT
    assert d["readiness_sha256"] == readiness.readiness_sha256
    assert d["verdict"] == READY


def test_readiness_not_ready_for_rejected_decision(valid_subject):
    decision = AcceptanceEngine().accept(mutate(valid_subject, freeze_blockers=("open-pr",)))
    readiness = build_repository_readiness(decision)
    assert readiness.freeze_ready is False
    assert readiness.verdict == NOT_READY
    assert readiness.ready is False
    assert "freeze-readiness" in readiness.blocking_failures
    assert readiness.gate_status["freeze-readiness"] == "fail"


def test_readiness_is_deterministic(accepted_decision):
    a = build_repository_readiness(accepted_decision)
    b = build_repository_readiness(accepted_decision)
    assert a.to_dict() == b.to_dict()
    assert a.readiness_sha256 == b.readiness_sha256
