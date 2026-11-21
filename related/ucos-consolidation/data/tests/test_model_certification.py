"""EC3-B10-U11 — Meta-model certification tests (CCE CC-1…CC-10 + Data C1…C7)."""

from __future__ import annotations

from data.model_certification import (
    certify_model,
    evaluate_model_compliance,
)
from data.model_traceability import build_model_traceability
from data.model_validation import validate_model
from data.tests.test_model import a_model


def _validation(model=None):
    model = model or a_model()
    trace = build_model_traceability(model, unit="EC3-B10-U11", forward=("f",))
    return validate_model(model, trace)


# ---------------------------------------------------------------------------
# CCE ten gates (CC-1…CC-10)
# ---------------------------------------------------------------------------


def test_metamodel_is_certified_all_ten_gates_close():
    cert = certify_model(_validation(), version="1.0.0")
    assert cert.certified is True
    gates = {f.criterion_id: f.passed for f in cert.decision.findings}
    assert gates == {f"CC-{n}": True for n in range(1, 11)}
    assert cert.decision.certification_id.startswith("UCOS-CERT-UDM-")


def test_certification_ledger_is_intact_and_appended():
    cert = certify_model(_validation(), version="1.0.0")
    assert cert.ledger.verify() is True
    assert cert.ledger_entry.certification_id == cert.decision.certification_id


def test_certification_is_deterministic():
    a = certify_model(_validation(), version="1.0.0")
    b = certify_model(_validation(), version="1.0.0")
    assert a.decision.certification_id == b.decision.certification_id


# ---------------------------------------------------------------------------
# Data compliance (C1…C7)
# ---------------------------------------------------------------------------


def test_data_compliance_c1_c7_all_pass_with_c5_material():
    compliance = evaluate_model_compliance(_validation())
    assert compliance.compliant is True
    by_id = {c["id"]: c for c in compliance.conditions}
    assert set(by_id) == {f"C{n}" for n in range(1, 8)}
    assert all(c["status"] == "pass" for c in compliance.conditions)
    # C5 (meta-relationship closure + founding acyclic + map resolves) materially exercised
    assert by_id["C5"]["materially_exercised"] is True
    assert "note" in by_id["C5"]


def test_data_compliance_to_dict_shape():
    d = evaluate_model_compliance(_validation()).to_dict()
    assert d["standard"] == "DATA-001 §12"
    assert d["compliant"] is True
    assert len(d["conditions"]) == 7


def test_certified_property_requires_compliance_and_ledger():
    cert = certify_model(_validation(), version="1.0.0")
    # certified is the conjunction of decision.certified + ledger intact + compliant
    assert cert.certified == (
        cert.decision.certified and cert.ledger.verify() and cert.compliance.compliant
    )
