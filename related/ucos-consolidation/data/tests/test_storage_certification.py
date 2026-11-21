"""EC3-B10-U05 — Storage certification tests (CCE CC-1…CC-10 + Data C1…C7 + ledger)."""

from __future__ import annotations

from data.attribute import make_attribute
from data.certification import cce_gates
from data.datum import make_datum
from data.entity import entity_ref_for, make_entity
from data.schema import entity_schema_for
from data.storage import make_storage, runtime_ref_for
from data.storage_certification import (
    certify_storage,
    evaluate_storage_compliance,
)
from data.storage_meta import CCE_GATES, DurabilityLevel, StorageKind
from data.storage_traceability import build_storage_traceability
from data.storage_validation import validate_storage
from engine.certification.contracts import CertificationStatus

ENTITY_NAME = "ucos.demo.entity"
STORAGE_NAME = "ucos.demo.storage"
RUNTIME_REF = runtime_ref_for("state.persist")


def _entity(name=ENTITY_NAME):
    attr = make_attribute(
        "ucos.demo.attr",
        "ucos.core.string",
        make_datum("ucos.core.string", "hello"),
        entity_ref_for(name),
    )
    return make_entity(name, "ucos.core.entity", (attr,))


def _storage(name=STORAGE_NAME):
    entity = _entity()
    schema = entity_schema_for(entity, name="ucos.demo.schema", type_tag="ucos.core.schema")
    return make_storage(
        name,
        "ucos.core.storage",
        ("locus.primary",),
        ((entity, schema),),
        RUNTIME_REF,
        kind=StorageKind.LOCAL,
        durability=DurabilityLevel.DURABLE,
    )


def _validate(storage):
    trace = build_storage_traceability(storage, unit="EC3-B10-U05", forward=(storage.storage_id,))
    return validate_storage(storage, trace)


def test_cce_ten_gates_all_close_and_certify():
    cert = certify_storage(_validate(_storage()), version="1.0.0")
    assert cert.decision.status is CertificationStatus.CERTIFIED
    gate_ids = {f.criterion_id for f in cert.decision.findings}
    assert gate_ids == set(CCE_GATES)  # exactly CC-1…CC-10
    assert all(f.passed for f in cert.decision.findings)


def test_cce_gate_suite_is_reused_from_dmc01():
    # The Storage unit reuses the CERTIFIED DMC-01 CCE ten-gate suite verbatim.
    assert len(cce_gates()) == 10


def test_certification_record_is_immutable_and_self_verifying():
    cert = certify_storage(_validate(_storage()), version="1.0.0")
    assert cert.decision.record.verify_integrity() is True
    assert cert.decision.record.authority == "ENGINEERING-EXECUTION-ONLY"  # DE-05
    assert cert.decision.record.disclosure["asserts_constitutional_finality"] is False


def test_ledger_is_append_only_and_hash_chain_intact():
    cert = certify_storage(_validate(_storage()), version="1.0.0")
    assert cert.ledger.verify() is True  # CC-10 chain intact
    assert len(cert.ledger) == 1
    assert cert.ledger_entry.sequence == 0
    assert cert.ledger_entry.prev_hash == "0" * 64


def test_data_compliance_c1_c7_all_hold_with_c6_materially_exercised():
    compliance = evaluate_storage_compliance(_validate(_storage()))
    assert compliance.compliant is True
    ids = {c["id"] for c in compliance.conditions}
    assert ids == {"C1", "C2", "C3", "C4", "C5", "C6", "C7"}
    assert all(c["status"] == "pass" for c in compliance.conditions)
    c6 = next(c for c in compliance.conditions if c["id"] == "C6")
    assert c6.get("materially_exercised") is True  # storage abstract topology (UDL-11)
    assert set(c6["backed_by"]) == {
        "storage-independence",
        "storage-topology-consistent",
        "storage-persistence-by-reference",
    }


def test_overall_certification_is_sound():
    cert = certify_storage(_validate(_storage()), version="1.0.0")
    assert cert.certified is True  # decision + ledger + compliance


def test_certification_id_is_deterministic():
    a = certify_storage(_validate(_storage()), version="1.0.0")
    b = certify_storage(_validate(_storage()), version="1.0.0")
    assert a.decision.certification_id == b.decision.certification_id


def test_non_compliant_storage_is_not_certified():
    # A secret-bearing topology fails validation → gates fail-closed → NOT-CERTIFIED.
    cert = certify_storage(_validate(_storage(name="secret")), version="1.0.0")
    assert cert.decision.status is CertificationStatus.NOT_CERTIFIED
    assert cert.certified is False
    assert cert.compliance.compliant is False
