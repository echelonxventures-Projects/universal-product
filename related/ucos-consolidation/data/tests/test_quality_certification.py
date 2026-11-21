"""EC3-B10-U08 — Quality certification tests (CCE CC-1…CC-10 + Data C1…C7 + ledger)."""

from __future__ import annotations

from data.attribute import make_attribute
from data.certification import cce_gates
from data.datum import make_datum
from data.entity import entity_ref_for, make_entity
from data.quality import make_measurements, make_quality, policy_ref_for
from data.quality_certification import (
    certify_quality,
    evaluate_quality_compliance,
)
from data.quality_meta import CCE_GATES, QualityKind
from data.quality_traceability import build_quality_traceability
from data.quality_validation import validate_quality
from engine.certification.contracts import CertificationStatus

ENTITY_NAME = "ucos.demo.entity"
QUALITY_NAME = "ucos.demo.quality"
POLICY_REF = policy_ref_for("quality.udl")
SCHEMA_REF = "UCOS-SCHEMA-REF:ucos.demo.schema"


def _entity(name=ENTITY_NAME):
    attr = make_attribute(
        "ucos.demo.attr",
        "ucos.core.string",
        make_datum("ucos.core.string", "hello"),
        entity_ref_for(name),
    )
    return make_entity(name, "ucos.core.entity", (attr,))


def _quality(name=QUALITY_NAME):
    entity = _entity()
    return make_quality(
        name,
        "ucos.core.quality",
        entity,
        POLICY_REF,
        kind=QualityKind.COMPLETENESS_MEASURE,
        measurements=make_measurements((("completeness", True, 100),)),
        schema_ref=SCHEMA_REF,
    )


def _validate(quality):
    trace = build_quality_traceability(quality, unit="EC3-B10-U08", forward=(quality.quality_id,))
    return validate_quality(quality, trace)


def test_cce_ten_gates_all_close_and_certify():
    cert = certify_quality(_validate(_quality()), version="1.0.0")
    assert cert.decision.status is CertificationStatus.CERTIFIED
    gate_ids = {f.criterion_id for f in cert.decision.findings}
    assert gate_ids == set(CCE_GATES)  # exactly CC-1…CC-10
    assert all(f.passed for f in cert.decision.findings)


def test_cce_gate_suite_is_reused_from_dmc01():
    # The Quality unit reuses the CERTIFIED DMC-01 CCE ten-gate suite verbatim.
    assert len(cce_gates()) == 10


def test_certification_record_is_immutable_and_self_verifying():
    cert = certify_quality(_validate(_quality()), version="1.0.0")
    assert cert.decision.record.verify_integrity() is True
    assert cert.decision.record.authority == "ENGINEERING-EXECUTION-ONLY"  # DE-05
    assert cert.decision.record.disclosure["asserts_constitutional_finality"] is False


def test_ledger_is_append_only_and_hash_chain_intact():
    cert = certify_quality(_validate(_quality()), version="1.0.0")
    assert cert.ledger.verify() is True  # CC-10 chain intact
    assert len(cert.ledger) == 1
    assert cert.ledger_entry.sequence == 0
    assert cert.ledger_entry.prev_hash == "0" * 64


def test_data_compliance_c1_c7_all_hold_with_c6_materially_exercised():
    compliance = evaluate_quality_compliance(_validate(_quality()))
    assert compliance.compliant is True
    ids = {c["id"] for c in compliance.conditions}
    assert ids == {"C1", "C2", "C3", "C4", "C5", "C6", "C7"}
    assert all(c["status"] == "pass" for c in compliance.conditions)
    c6 = next(c for c in compliance.conditions if c["id"] == "C6")
    assert c6.get("materially_exercised") is True  # quality evaluative record (UDL-14)
    assert set(c6["backed_by"]) == {
        "quality-independence",
        "quality-non-remediating",
        "quality-evaluative",
    }


def test_compliance_report_serializes_deterministically():
    compliance = evaluate_quality_compliance(_validate(_quality()))
    payload = compliance.to_dict()
    assert payload["standard"] == "DATA-001 §12"
    assert payload["compliant"] is True
    assert len(payload["conditions"]) == 7


def test_overall_certification_is_sound():
    cert = certify_quality(_validate(_quality()), version="1.0.0")
    assert cert.certified is True  # decision + ledger + compliance


def test_certification_id_is_deterministic():
    a = certify_quality(_validate(_quality()), version="1.0.0")
    b = certify_quality(_validate(_quality()), version="1.0.0")
    assert a.decision.certification_id == b.decision.certification_id


def test_certification_evidence_is_built():
    cert = certify_quality(_validate(_quality()), version="1.0.0")
    payload = cert.evidence.to_dict()
    assert payload  # certification evidence produced


def test_non_compliant_quality_is_not_certified():
    # A secret-bearing quality object fails validation → gates fail-closed → NOT-CERTIFIED.
    cert = certify_quality(_validate(_quality(name="secret")), version="1.0.0")
    assert cert.decision.status is CertificationStatus.NOT_CERTIFIED
    assert cert.certified is False
    assert cert.compliance.compliant is False
