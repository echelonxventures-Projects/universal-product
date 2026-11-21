"""EC3-B10-U10 — Relationship certification tests (CC-1…CC-10 + C1…C7, C5 material)."""

from __future__ import annotations

from types import SimpleNamespace

from data.relationship_certification import (
    RelationshipCertification,
    certify_relationship,
    evaluate_relationship_compliance,
)
from data.relationship_realize import build_canonical_relationship
from data.relationship_traceability import build_relationship_traceability
from data.relationship_validation import RelationshipValidation, validate_relationship
from engine.certification.ledger import CertificationLedger

UNIT = "EC3-B10-U10"
VERSION = "1.0.0"


def _validation() -> RelationshipValidation:
    relationship = build_canonical_relationship()
    trace = build_relationship_traceability(
        relationship, unit=UNIT, forward=(relationship.relationship_id,)
    )
    return validate_relationship(relationship, trace)


def test_canonical_relationship_certified():
    cert = certify_relationship(_validation(), version=VERSION)
    assert isinstance(cert, RelationshipCertification)
    assert cert.certified is True
    assert cert.decision.certified is True
    assert cert.ledger.verify() is True


def test_all_ten_gates_closed():
    cert = certify_relationship(_validation(), version=VERSION)
    gates = {f.criterion_id: f.passed for f in cert.decision.findings}
    assert set(gates) == {f"CC-{n}" for n in range(1, 11)}
    assert all(gates.values())


def test_certification_id_is_dmc04():
    cert = certify_relationship(_validation(), version=VERSION)
    assert cert.decision.certification_id.startswith("UCOS-CERT-DMC-04-")


def test_ledger_chain_intact_and_appended():
    ledger = CertificationLedger()
    cert = certify_relationship(_validation(), version=VERSION, ledger=ledger)
    assert cert.ledger is ledger
    assert cert.ledger_entry.sequence == 0
    assert cert.ledger.verify() is True


def test_compliance_all_conditions_pass():
    compliance = evaluate_relationship_compliance(_validation())
    conditions = {c["id"]: c["status"] for c in compliance.conditions}
    assert set(conditions) == {f"C{n}" for n in range(1, 8)}
    assert all(v == "pass" for v in conditions.values())
    assert compliance.compliant is True


def test_c5_is_materially_exercised():
    compliance = evaluate_relationship_compliance(_validation())
    c5 = next(c for c in compliance.conditions if c["id"] == "C5")
    assert c5["materially_exercised"] is True
    assert "UDL-09" in c5["note"]
    assert c5["status"] == "pass"


def test_compliance_to_dict_shape():
    d = evaluate_relationship_compliance(_validation()).to_dict()
    assert d["standard"] == "DATA-001 §12"
    assert d["compliant"] is True
    assert len(d["conditions"]) == 7


def test_compliance_fails_when_a_check_fails():
    validation = _validation()
    # Re-derive compliance over a finding-set where the C7-backing check is flipped to
    # not-passed, proving compliance is fail-closed (DRA-C5 audit). Findings are projected
    # to lightweight stubs exposing the (check_id, passed) surface the evaluator reads.
    findings = tuple(
        SimpleNamespace(check_id=f.check_id, passed=f.check_id != "non-constitutive")
        for f in validation.report.findings
    )
    broken_report = SimpleNamespace(target_id=validation.report.target_id, findings=findings)
    broken = SimpleNamespace(report=broken_report)
    compliance = evaluate_relationship_compliance(broken)  # type: ignore[arg-type]
    c7 = next(c for c in compliance.conditions if c["id"] == "C7")
    assert c7["status"] == "fail"
    assert compliance.compliant is False
