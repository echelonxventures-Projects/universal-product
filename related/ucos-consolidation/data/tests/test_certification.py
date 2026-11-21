"""EC3-B10-U01 — Certification tests (CCE CC-1…CC-10 + Data C1…C7 + ledger)."""

from __future__ import annotations

from data.certification import (
    cce_gates,
    certify_datum,
    evaluate_data_compliance,
)
from data.datum import make_datum
from data.meta import CCE_GATES
from data.traceability import build_traceability
from data.validation import validate_datum
from engine.certification.contracts import CertificationStatus, CertificationSubject


def _validate(datum):
    trace = build_traceability(datum, unit="EC3-B10-U01", forward=(datum.datum_id,))
    return validate_datum(datum, trace)


def test_cce_ten_gates_all_close_and_certify():
    validation = _validate(make_datum("t", "v"))
    cert = certify_datum(validation, version="1.0.0")
    assert cert.decision.status is CertificationStatus.CERTIFIED
    gate_ids = {f.criterion_id for f in cert.decision.findings}
    assert gate_ids == set(CCE_GATES)  # exactly CC-1…CC-10
    assert all(f.passed for f in cert.decision.findings)
    assert len(cce_gates()) == 10


def test_certification_record_is_immutable_and_self_verifying():
    cert = certify_datum(_validate(make_datum("t", "v")), version="1.0.0")
    assert cert.decision.record.verify_integrity() is True
    assert cert.decision.record.authority == "ENGINEERING-EXECUTION-ONLY"  # DE-05
    disclosure = cert.decision.record.disclosure
    assert disclosure["asserts_constitutional_finality"] is False


def test_ledger_is_append_only_and_hash_chain_intact():
    cert = certify_datum(_validate(make_datum("t", "v")), version="1.0.0")
    assert cert.ledger.verify() is True  # CC-10 chain intact
    assert len(cert.ledger) == 1
    assert cert.ledger_entry.sequence == 0
    assert cert.ledger_entry.prev_hash == "0" * 64


def test_data_compliance_c1_c7_all_hold():
    compliance = evaluate_data_compliance(_validate(make_datum("t", "v")))
    assert compliance.compliant is True
    ids = {c["id"] for c in compliance.conditions}
    assert ids == {"C1", "C2", "C3", "C4", "C5", "C6", "C7"}
    assert all(c["status"] == "pass" for c in compliance.conditions)


def test_overall_certification_is_sound():
    cert = certify_datum(_validate(make_datum("t", "v")), version="1.0.0")
    assert cert.certified is True  # decision + ledger + compliance


def test_certification_id_is_deterministic():
    a = certify_datum(_validate(make_datum("t", "v")), version="1.0.0")
    b = certify_datum(_validate(make_datum("t", "v")), version="1.0.0")
    assert a.decision.certification_id == b.decision.certification_id


def test_non_compliant_datum_is_not_certified():
    # A secret-bearing datum fails validation → gates fail-closed → NOT-CERTIFIED.
    validation = _validate(make_datum("credential", {"secret": "x"}))
    cert = certify_datum(validation, version="1.0.0")
    assert cert.decision.status is CertificationStatus.NOT_CERTIFIED
    assert cert.certified is False
    assert cert.compliance.compliant is False


def test_a_gate_refuses_a_required_check_that_never_ran_or_blocked() -> None:
    """_checks_ok answers in both directions — absent is not-run, failed is failed.

    The gates are aggregations over validation output; each has an arm for a check that
    was never executed and another for one that executed and blocked. Both must refuse:
    a gate that only ever reported "not-run" would pass an artifact whose check ran and
    failed, and a gate that ignored absence would certify an unmeasured subject.
    """
    from dataclasses import replace

    datum = make_datum("t", "v")
    trace = build_traceability(datum, unit="EC3-B10-U01", forward=(datum.datum_id,))
    validation = validate_datum(datum, trace)
    base = CertificationSubject.from_validation(validation.report, None, version="1.0.0")
    gate = next(g for g in cce_gates() if g.required_checks)

    absent = replace(base, checks_run=())
    ok, problems = gate._checks_ok(absent)
    assert ok is False
    assert all(p.endswith(":not-run") for p in problems)

    blocked = replace(base, blocking_failures=tuple(gate.required_checks))
    ok, problems = gate._checks_ok(blocked)
    assert ok is False
    assert all(p.endswith(":failed") for p in problems)

    evidence_gate = next(g for g in cce_gates() if g.criterion_id == "CC-6")
    finding = evidence_gate.evaluate(replace(base, evidence_present=False))
    assert not finding.passed
    assert "validation evidence absent" in finding.message
