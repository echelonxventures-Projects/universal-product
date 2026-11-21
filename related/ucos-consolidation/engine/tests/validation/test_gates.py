"""TASK-000049 — Validation acceptance gate tests."""

from __future__ import annotations

import pytest

from engine.validation import ValidationEngine, enforce_acceptance
from engine.validation.errors import AcceptanceGateError

from .conftest import mutate


def test_gate_accepts_passing_report(valid_subject):
    report = ValidationEngine().validate(valid_subject)
    decision = enforce_acceptance(report)
    assert decision.accepted is True
    assert decision.verdict == "pass"
    assert decision.blocking_failures == ()
    assert decision.to_dict()["accepted"] is True


def test_gate_rejects_report_with_blocking_failure(valid_subject):
    report = ValidationEngine().validate(mutate(valid_subject, provenance_chain=()))
    decision = enforce_acceptance(report)
    assert decision.accepted is False
    assert "provenance-chain" in decision.blocking_failures


def test_gate_strict_raises_on_rejection(valid_subject):
    report = ValidationEngine().validate(mutate(valid_subject, signature={}))
    with pytest.raises(AcceptanceGateError) as exc:
        enforce_acceptance(report, strict=True)
    assert "signature-present" in exc.value.context["blocking_failures"]


def test_gate_strict_passes_on_acceptance(valid_subject):
    report = ValidationEngine().validate(valid_subject)
    decision = enforce_acceptance(report, strict=True)
    assert decision.accepted is True


def test_gate_records_advisory_failures(valid_subject):
    report = ValidationEngine().validate(mutate(valid_subject, runtime_id="bad"))
    decision = enforce_acceptance(report)
    # advisory failure does not block acceptance but is recorded
    assert decision.accepted is True
    assert "identity-deterministic" in decision.advisory_failures
