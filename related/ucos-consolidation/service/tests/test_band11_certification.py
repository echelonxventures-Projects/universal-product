"""EC3-B11-U12 — Band-11 completion certification + traceability tests."""

from __future__ import annotations

from service.band11 import make_band11_completion
from service.band11_certification import (
    ServiceComplianceReport,
    certify_band11,
    evaluate_band11_compliance,
)
from service.band11_meta import EXPECTED_UNITS, TRACE_BACKWARD_BAND
from service.band11_traceability import build_band11_traceability
from service.band11_validation import validate_band11
from engine.certification.ledger import CertificationLedger

_FULL_INTEGRATION = {
    "all_members_certified": True,
    "closure_SMI_01": True,
    "relationship_closure_SMI_02": True,
    "totality_SMI_03": True,
    "founding_acyclic_SMI_04": True,
    "reuse_by_reference_SMI_05": True,
    "non_constitutive_SMI_06": True,
    "non_projection_SMI_07": True,
    "map_resolves": True,
}


def _completion(type_tag: str = "ucos.core.band-completion"):
    return make_band11_completion(
        "ucos.service.band11.completion",
        type_tag,
        tuple((u, f"UCOS-CERT-{u}-{'a' * 16}", True) for u in EXPECTED_UNITS),
        meta_model_id="UCOS-METAMODEL-ucos.service.metamodel.universal-" + "b" * 16,
        integration=dict(_FULL_INTEGRATION),
        version="1.0.0",
    )


def _validation(type_tag: str = "ucos.core.band-completion"):
    c = _completion(type_tag)
    trace = build_band11_traceability(c, unit="EC3-B11-U12", forward=("a", "b"))
    return validate_band11(c, trace)


# ---------------------------------------------------------------------------
# Traceability
# ---------------------------------------------------------------------------


def test_band11_traceability_rooted_and_closed():
    c = _completion()
    trace = build_band11_traceability(c, unit="EC3-B11-U12", forward=(c.band_id, "report"))
    assert trace.rooted is True
    assert trace.closed is True
    assert trace.backward == TRACE_BACKWARD_BAND
    # every certified unit is cited in the substrate-reuse map (by reference)
    reuse = trace.to_dict()["substrate_reuse"]
    for unit in EXPECTED_UNITS:
        assert f"unit_{unit}" in reuse


# ---------------------------------------------------------------------------
# Compliance (C1…C7)
# ---------------------------------------------------------------------------


def test_compliance_all_pass_with_c5_materially_exercised():
    report = evaluate_band11_compliance(_validation())
    assert report.compliant is True
    conds = {c["id"]: c for c in report.conditions}
    assert set(conds) == {f"C{n}" for n in range(1, 8)}
    assert conds["C5"]["materially_exercised"] is True
    assert "note" in conds["C5"]


def test_compliance_fail_branch_when_technology_named():
    # A tech-named record fails band11-independence + non-constitutive → C6/C7 fail (others pass).
    report = evaluate_band11_compliance(_validation(type_tag="grpc-backed"))
    conds = {c["id"]: c["status"] for c in report.conditions}
    assert conds["C6"] == "fail"
    assert conds["C7"] == "fail"
    assert conds["C1"] == "pass"
    assert report.compliant is False


def test_service_compliance_report_to_dict():
    d = evaluate_band11_compliance(_validation()).to_dict()
    assert d["standard"] == "SERVICE-001 §12"
    assert d["compliant"] is True
    assert len(d["conditions"]) == 7


# ---------------------------------------------------------------------------
# Certification (CCE ten gates reused verbatim)
# ---------------------------------------------------------------------------


def test_certify_band11_is_certified_with_ten_gates_closed():
    cert = certify_band11(_validation(), version="1.0.0")
    assert cert.certified is True
    gates = {f.criterion_id: f.status for f in cert.decision.findings}
    assert set(gates) == {f"CC-{n}" for n in range(1, 11)}
    assert all(s == "pass" for s in gates.values())
    assert cert.decision.certification_id.startswith("UCOS-CERT-BAND-11-")
    assert cert.ledger.verify() is True


def test_certify_band11_accepts_provided_ledger():
    ledger = CertificationLedger()
    cert = certify_band11(_validation(), version="1.0.0", ledger=ledger)
    assert cert.ledger is ledger
    assert cert.certified is True


def test_certify_band11_not_certified_when_compliance_fails():
    # A tech-named record is validated-rejected → the CCE gates do not all close.
    cert = certify_band11(_validation(type_tag="grpc-backed"), version="1.0.0")
    assert cert.certified is False


def test_service_compliance_report_dataclass():
    rep = ServiceComplianceReport(target_id="t", conditions=({"id": "C1", "status": "pass"},))
    assert rep.compliant is True
    assert ServiceComplianceReport("t", ({"id": "C1", "status": "fail"},)).compliant is False
