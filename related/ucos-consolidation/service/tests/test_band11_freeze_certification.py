"""EC3-B11-U13 — Band-11 freeze certification tests (CCE gates + C1…C7)."""

from __future__ import annotations

from service.band11_freeze import make_band11_freeze
from service.band11_freeze_certification import (
    Band11FreezeCertification,
    certify_band11_freeze,
    evaluate_freeze_compliance,
)
from service.band11_freeze_meta import EXPECTED_FROZEN_UNITS
from service.band11_freeze_traceability import build_band11_freeze_traceability
from service.band11_freeze_validation import validate_band11_freeze

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
_BAND_CERT = "UCOS-CERT-BAND-11-" + "a" * 16


def _freeze(**kw):
    params = dict(
        name="ucos.service.band11.freeze",
        type_tag="ucos.core.band-freeze",
        unit_certifications=tuple(
            (u, f"UCOS-CERT-{u}-{'a' * 16}", True) for u in EXPECTED_FROZEN_UNITS
        ),
        band_completion_id="UCOS-BAND11-ucos.service.band11.completion-" + "b" * 16,
        band_completion_certification_id=_BAND_CERT,
        meta_model_id="UCOS-METAMODEL-ucos.service.metamodel.universal-" + "c" * 16,
        integration=dict(_FULL_INTEGRATION),
        version="1.0.0",
    )
    params.update(kw)
    return make_band11_freeze(
        params.pop("name"), params.pop("type_tag"), params.pop("unit_certifications"), **params
    )


def _validation(freeze):
    trace = build_band11_freeze_traceability(freeze, unit="EC3-B11-U13", forward=("a", "b"))
    return validate_band11_freeze(freeze, trace)


def test_compliance_all_pass_and_c5_materially_exercised():
    report = evaluate_freeze_compliance(_validation(_freeze()))
    assert report.compliant is True
    conds = {c["id"]: c for c in report.conditions}
    assert set(conds) == {f"C{n}" for n in range(1, 8)}
    assert conds["C5"]["materially_exercised"] is True
    assert "note" in conds["C5"]
    d = report.to_dict()
    assert d["standard"] == "SERVICE-001 §12"
    assert d["compliant"] is True


def test_compliance_fails_on_technology_named_freeze():
    # a tech-named freeze fails freeze-independence (C6) and non-constitutive (C7)
    report = evaluate_freeze_compliance(_validation(_freeze(type_tag="grpc-backed-freeze")))
    conds = {c["id"]: c["status"] for c in report.conditions}
    assert conds["C6"] == "fail"
    assert conds["C7"] == "fail"
    assert report.compliant is False


def test_certify_band11_freeze_certified():
    cert = certify_band11_freeze(_validation(_freeze()), version="1.0.0")
    assert isinstance(cert, Band11FreezeCertification)
    assert cert.certified is True
    assert cert.decision.certified is True
    assert cert.ledger.verify() is True
    assert cert.compliance.compliant is True
    assert cert.decision.certification_id.startswith("UCOS-CERT-BAND-11-FREEZE-")
    gates = {f.criterion_id: f.passed for f in cert.decision.findings}
    assert gates == {f"CC-{n}": True for n in range(1, 11)}


def test_certify_band11_freeze_not_certified_on_invalid_freeze():
    cert = certify_band11_freeze(_validation(_freeze(type_tag="grpc-backed-freeze")), version="1.0.0")
    assert cert.certified is False
    assert cert.compliance.compliant is False
