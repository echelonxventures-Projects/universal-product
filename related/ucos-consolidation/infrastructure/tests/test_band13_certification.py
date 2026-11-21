"""EC3-B13-U11 — Band-13 completion certification tests (CCE gates + C1…C7 compliance)."""

from __future__ import annotations

from infrastructure.band13 import make_band13_completion
from infrastructure.band13_certification import (
    Band13Certification,
    InfrastructureComplianceReport,
    certify_band13,
    evaluate_band13_compliance,
)
from infrastructure.band13_meta import EXPECTED_UNITS
from infrastructure.band13_traceability import build_band13_traceability
from infrastructure.band13_validation import validate_band13

_FULL_INTEGRATION = {
    "all_concerns_certified": True,
    "leaf_closure_complete": True,
    "graph_downward_only": True,
    "graph_acyclic": True,
    "all_nodes_present": True,
    "ownership_disjoint": True,
    "all_edges_certified": True,
    "uimm_determination_complete": True,
}


def _validation():
    completion = make_band13_completion(
        "ucos.infrastructure.band13.completion",
        "ucos.core.band-completion",
        tuple((u, "a" * 64, True) for u in EXPECTED_UNITS),
        meta_model_id="b" * 64,
        integration=dict(_FULL_INTEGRATION),
        version="1.0.0",
    )
    trace = build_band13_traceability(
        completion, unit="EC3-B13-U11", forward=(completion.band_id, "X", "Y", "Z")
    )
    return validate_band13(completion, trace)


def test_certify_band13_is_certified_and_ledgered():
    cert = certify_band13(_validation(), version="1.0.0")
    assert isinstance(cert, Band13Certification)
    assert cert.certified is True
    assert cert.decision.certified is True
    assert cert.ledger.verify() is True
    assert cert.decision.certification_id.startswith("UCOS-CERT-BAND-13-")
    # all ten CCE gates closed
    gates = {f.criterion_id: f.passed for f in cert.decision.findings}
    assert gates == {f"CC-{n}": True for n in range(1, 11)}


def test_compliance_all_conditions_pass_and_c5_materially_exercised():
    report = evaluate_band13_compliance(_validation())
    assert isinstance(report, InfrastructureComplianceReport)
    assert report.compliant is True
    conditions = {c["id"]: c for c in report.conditions}
    assert set(conditions) == {f"C{n}" for n in range(1, 8)}
    assert all(c["status"] == "pass" for c in report.conditions)
    assert conditions["C5"].get("materially_exercised") is True
    assert "note" in conditions["C5"]


def test_compliance_report_to_dict_shape():
    d = evaluate_band13_compliance(_validation()).to_dict()
    assert d["standard"] == "INFRASTRUCTURE-001 §12"
    assert d["compliant"] is True
    assert len(d["conditions"]) == 7
