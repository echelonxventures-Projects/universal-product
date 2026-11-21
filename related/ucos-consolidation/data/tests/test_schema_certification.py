"""EC3-B10-U04 — Schema certification tests (CCE CC-1…CC-10 + Data C1…C7 + ledger)."""

from __future__ import annotations

from data.attribute import make_attribute
from data.certification import cce_gates
from data.datum import make_datum
from data.entity import entity_ref_for, make_entity
from data.schema import entity_schema_for
from data.schema_certification import (
    certify_schema,
    evaluate_schema_compliance,
)
from data.schema_meta import CCE_GATES
from data.schema_traceability import build_schema_traceability
from data.schema_validation import validate_schema
from engine.certification.contracts import CertificationStatus

ENTITY_NAME = "ucos.demo.entity"
SCHEMA_NAME = "ucos.demo.schema"


def _entity(name=ENTITY_NAME):
    attr = make_attribute(
        "ucos.demo.attr",
        "ucos.core.string",
        make_datum("ucos.core.string", "hello"),
        entity_ref_for(name),
    )
    return make_entity(name, "ucos.core.entity", (attr,))


def _schema(name=SCHEMA_NAME):
    return entity_schema_for(_entity(), name=name, type_tag="ucos.core.schema")


def _validate(schema):
    trace = build_schema_traceability(schema, unit="EC3-B10-U04", forward=(schema.schema_id,))
    return validate_schema(schema, trace)


def test_cce_ten_gates_all_close_and_certify():
    cert = certify_schema(_validate(_schema()), version="1.0.0")
    assert cert.decision.status is CertificationStatus.CERTIFIED
    gate_ids = {f.criterion_id for f in cert.decision.findings}
    assert gate_ids == set(CCE_GATES)  # exactly CC-1…CC-10
    assert all(f.passed for f in cert.decision.findings)


def test_cce_gate_suite_is_reused_from_dmc01():
    # The Schema unit reuses the CERTIFIED DMC-01 CCE ten-gate suite verbatim.
    assert len(cce_gates()) == 10


def test_certification_record_is_immutable_and_self_verifying():
    cert = certify_schema(_validate(_schema()), version="1.0.0")
    assert cert.decision.record.verify_integrity() is True
    assert cert.decision.record.authority == "ENGINEERING-EXECUTION-ONLY"  # DE-05
    assert cert.decision.record.disclosure["asserts_constitutional_finality"] is False


def test_ledger_is_append_only_and_hash_chain_intact():
    cert = certify_schema(_validate(_schema()), version="1.0.0")
    assert cert.ledger.verify() is True  # CC-10 chain intact
    assert len(cert.ledger) == 1
    assert cert.ledger_entry.sequence == 0
    assert cert.ledger_entry.prev_hash == "0" * 64


def test_data_compliance_c1_c7_all_hold_with_c4_materially_exercised():
    compliance = evaluate_schema_compliance(_validate(_schema()))
    assert compliance.compliant is True
    ids = {c["id"] for c in compliance.conditions}
    assert ids == {"C1", "C2", "C3", "C4", "C5", "C6", "C7"}
    assert all(c["status"] == "pass" for c in compliance.conditions)
    c4 = next(c for c in compliance.conditions if c["id"] == "C4")
    assert c4.get("materially_exercised") is True  # explicit schema structure (UDL-10)
    assert set(c4["backed_by"]) == {
        "schema-named",
        "schema-typed",
        "schema-explicit-structure",
        "schema-elements-typed",
        "schema-conformance-decidable",
    }


def test_overall_certification_is_sound():
    cert = certify_schema(_validate(_schema()), version="1.0.0")
    assert cert.certified is True  # decision + ledger + compliance


def test_certification_id_is_deterministic():
    a = certify_schema(_validate(_schema()), version="1.0.0")
    b = certify_schema(_validate(_schema()), version="1.0.0")
    assert a.decision.certification_id == b.decision.certification_id


def test_non_compliant_schema_is_not_certified():
    # A secret-bearing schema fails validation → gates fail-closed → NOT-CERTIFIED.
    cert = certify_schema(_validate(_schema(name="secret")), version="1.0.0")
    assert cert.decision.status is CertificationStatus.NOT_CERTIFIED
    assert cert.certified is False
    assert cert.compliance.compliant is False
