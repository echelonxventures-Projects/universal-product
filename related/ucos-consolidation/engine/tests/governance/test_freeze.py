"""EPIC-VAL-003 — Architecture Freeze recommendation tests.

Covers the FREEZE decision and every DO-NOT-FREEZE rationale branch by composing the
real decision + readiness artifacts (and, for the defensive edge branches, minimal
hand-built readiness reports).
"""

from __future__ import annotations

from engine.acceptance.readiness import NOT_READY, READY, RepositoryReadiness
from engine.governance.contracts import RepositoryDecision, StageOutcome
from engine.governance.freeze import (
    DO_NOT_FREEZE,
    FREEZE,
    FREEZE_FORMAT,
    build_freeze_recommendation,
)
from engine.runtime.disclosure import build_disclosure


def _decision(*, v=(), c=(), a=()):
    return RepositoryDecision.create(
        repository_id="R",
        epic_id="E",
        validation=StageOutcome.of("validation", total=2, failures=v),
        certification=StageOutcome.of("certification", total=2, failures=c),
        acceptance=StageOutcome.of("acceptance", total=20, failures=a),
        disclosure=build_disclosure(),
    )


def _readiness(*, verdict=READY, blocking=()):
    return RepositoryReadiness(
        repository_id="R",
        epic_id="E",
        acceptance_id="UCOS-ACCEPT-E-abc",
        accepted=verdict == READY,
        freeze_ready=verdict == READY,
        verdict=verdict,
        gates_total=20,
        gates_passed=20 if verdict == READY else 19,
        gate_status={},
        blocking_failures=blocking,
        advisory_failures=(),
        authority="ENGINEERING-EXECUTION-ONLY",
        disclosure=build_disclosure(),
        readiness_sha256="deadbeef",
    )


def test_freeze_when_governed_and_ready(governed_report):
    rec = governed_report.freeze_recommendation
    assert rec.recommendation == FREEZE
    assert rec.freeze is True
    assert rec.rationale == ()
    assert rec.to_dict()["freeze_format"] == FREEZE_FORMAT


def test_do_not_freeze_uses_decision_reasons():
    decision = _decision(a=("freeze-readiness",))
    readiness = _readiness(verdict=NOT_READY, blocking=("freeze-readiness",))
    rec = build_freeze_recommendation(decision, readiness)
    assert rec.recommendation == DO_NOT_FREEZE
    assert rec.freeze is False
    assert "acceptance:freeze-readiness" in rec.rationale


def test_do_not_freeze_falls_back_to_readiness_blocking():
    """Governed decision (no blocking reasons) but a not-ready readiness → gate ids."""
    decision = _decision()  # governed, blocking_reasons empty
    assert decision.governed is True
    readiness = _readiness(verdict=NOT_READY, blocking=("coverage-complete",))
    rec = build_freeze_recommendation(decision, readiness)
    assert rec.recommendation == DO_NOT_FREEZE
    assert rec.rationale == ("acceptance:coverage-complete",)


def test_do_not_freeze_generic_marker():
    """No decision reasons and no readiness blocking → the generic fail-closed marker."""
    decision = _decision()  # governed, blocking_reasons empty
    readiness = _readiness(verdict=NOT_READY, blocking=())
    rec = build_freeze_recommendation(decision, readiness)
    assert rec.recommendation == DO_NOT_FREEZE
    assert rec.rationale == ("repository-not-governed",)


def test_freeze_recommendation_is_deterministic():
    decision = _decision()
    readiness = _readiness()
    a = build_freeze_recommendation(decision, readiness)
    b = build_freeze_recommendation(decision, readiness)
    assert a.recommendation_sha256 == b.recommendation_sha256
    assert a.to_dict() == b.to_dict()
