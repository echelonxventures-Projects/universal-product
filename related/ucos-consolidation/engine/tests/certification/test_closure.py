"""TASK-000054 — Program closure report tests."""

from __future__ import annotations

import pytest

from engine.certification.closure import (
    CERTIFICATION_ACCEPTANCE_ID,
    build_program_closure,
    certification_framework_status,
)
from engine.certification.errors import ProgramClosureError
from engine.certification.ledger import CertificationLedger, CertificationLedgerEntry


def test_a10_fails_for_empty_ledger():
    assert certification_framework_status(CertificationLedger()) == "FAIL"


def test_a10_passes_for_certified_ledger(certified_decision):
    ledger = CertificationLedger()
    ledger.append(certified_decision.record)
    assert certification_framework_status(ledger) == "PASS"


def test_a10_fails_when_any_entry_not_certified(valid_report, artifact_version):
    from engine.certification.engine import certify_validation

    ledger = CertificationLedger()
    not_certified = certify_validation(valid_report, None, version=artifact_version)
    ledger.append(not_certified.record)
    assert certification_framework_status(ledger) == "FAIL"


def test_program_closure_pass(certified_decision):
    ledger = CertificationLedger()
    ledger.append(certified_decision.record)
    report = build_program_closure(ledger)
    assert report.verdict == "PASS"
    assert report.passed is True
    assert report.acceptance_status(CERTIFICATION_ACCEPTANCE_ID) == "PASS"
    # every A1..A10 row is PASS
    assert all(a.status == "PASS" for a in report.acceptance)
    assert len(report.acceptance) == 10
    assert report.certifications[0]["certification_id"] == certified_decision.certification_id
    assert report.ledger_intact is True
    d = report.to_dict()
    assert d["closure_format"] == "ucos-program-closure/1.0.0"
    assert d["closure_sha256"] == report.closure_sha256


def test_program_closure_is_deterministic(certified_decision):
    l1 = CertificationLedger()
    l2 = CertificationLedger()
    l1.append(certified_decision.record)
    l2.append(certified_decision.record)
    assert build_program_closure(l1).to_dict() == build_program_closure(l2).to_dict()


def test_program_closure_fails_when_a10_fails(valid_report, artifact_version):
    from engine.certification.engine import certify_validation

    ledger = CertificationLedger()
    ledger.append(certify_validation(valid_report, None, version=artifact_version).record)
    report = build_program_closure(ledger)
    assert report.verdict == "FAIL"
    assert report.acceptance_status("A10") == "FAIL"


def test_acceptance_status_unknown_id_returns_none(certified_decision):
    ledger = CertificationLedger()
    ledger.append(certified_decision.record)
    report = build_program_closure(ledger)
    assert report.acceptance_status("A99") is None


def test_closure_raises_on_tampered_ledger(certified_decision):
    ledger = CertificationLedger()
    ledger.append(certified_decision.record)
    tampered = CertificationLedgerEntry(**{**ledger.entries[0].to_dict(), "entry_hash": "0" * 64})
    ledger._entries[0] = tampered  # noqa: SLF001 — test reaches into internals
    with pytest.raises(ProgramClosureError):
        build_program_closure(ledger)
