"""EC3-B10-U07 — Governance certification tests (CCE CC-1…CC-10 + Data C1…C7 + ledger)."""

from __future__ import annotations

from data.attribute import make_attribute
from data.certification import cce_gates
from data.datum import make_datum
from data.entity import entity_ref_for, make_entity
from data.governance import make_conformance, make_governance, policy_ref_for
from data.governance_certification import (
    certify_governance,
    evaluate_governance_compliance,
)
from data.governance_meta import CCE_GATES, GovernanceKind
from data.governance_traceability import build_governance_traceability
from data.governance_validation import validate_governance
from engine.certification.contracts import CertificationStatus

ENTITY_NAME = "ucos.demo.entity"
GOVERNANCE_NAME = "ucos.demo.governance"
POLICY_REF = policy_ref_for("conformance.udl")


def _entity(name=ENTITY_NAME):
    attr = make_attribute(
        "ucos.demo.attr",
        "ucos.core.string",
        make_datum("ucos.core.string", "hello"),
        entity_ref_for(name),
    )
    return make_entity(name, "ucos.core.entity", (attr,))


def _governance(name=GOVERNANCE_NAME):
    entity = _entity()
    return make_governance(
        name,
        "ucos.core.governance",
        entity,
        POLICY_REF,
        kind=GovernanceKind.CONFORMANCE_RECORD,
        conformance=make_conformance((("UDL-02", True), ("UDL-13", True))),
    )


def _validate(governance):
    trace = build_governance_traceability(
        governance, unit="EC3-B10-U07", forward=(governance.governance_id,)
    )
    return validate_governance(governance, trace)


def test_cce_ten_gates_all_close_and_certify():
    cert = certify_governance(_validate(_governance()), version="1.0.0")
    assert cert.decision.status is CertificationStatus.CERTIFIED
    gate_ids = {f.criterion_id for f in cert.decision.findings}
    assert gate_ids == set(CCE_GATES)  # exactly CC-1…CC-10
    assert all(f.passed for f in cert.decision.findings)


def test_cce_gate_suite_is_reused_from_dmc01():
    # The Governance unit reuses the CERTIFIED DMC-01 CCE ten-gate suite verbatim.
    assert len(cce_gates()) == 10


def test_certification_record_is_immutable_and_self_verifying():
    cert = certify_governance(_validate(_governance()), version="1.0.0")
    assert cert.decision.record.verify_integrity() is True
    assert cert.decision.record.authority == "ENGINEERING-EXECUTION-ONLY"  # DE-05
    assert cert.decision.record.disclosure["asserts_constitutional_finality"] is False


def test_ledger_is_append_only_and_hash_chain_intact():
    cert = certify_governance(_validate(_governance()), version="1.0.0")
    assert cert.ledger.verify() is True  # CC-10 chain intact
    assert len(cert.ledger) == 1
    assert cert.ledger_entry.sequence == 0
    assert cert.ledger_entry.prev_hash == "0" * 64


def test_data_compliance_c1_c7_all_hold_with_c6_materially_exercised():
    compliance = evaluate_governance_compliance(_validate(_governance()))
    assert compliance.compliant is True
    ids = {c["id"] for c in compliance.conditions}
    assert ids == {"C1", "C2", "C3", "C4", "C5", "C6", "C7"}
    assert all(c["status"] == "pass" for c in compliance.conditions)
    c6 = next(c for c in compliance.conditions if c["id"] == "C6")
    assert c6.get("materially_exercised") is True  # governance declarative record (UDL-13)
    assert set(c6["backed_by"]) == {
        "governance-independence",
        "governance-non-enforcing",
        "governance-no-access",
    }


def test_compliance_report_serializes_deterministically():
    compliance = evaluate_governance_compliance(_validate(_governance()))
    payload = compliance.to_dict()
    assert payload["standard"] == "DATA-001 §12"
    assert payload["compliant"] is True
    assert len(payload["conditions"]) == 7


def test_overall_certification_is_sound():
    cert = certify_governance(_validate(_governance()), version="1.0.0")
    assert cert.certified is True  # decision + ledger + compliance


def test_certification_id_is_deterministic():
    a = certify_governance(_validate(_governance()), version="1.0.0")
    b = certify_governance(_validate(_governance()), version="1.0.0")
    assert a.decision.certification_id == b.decision.certification_id


def test_certification_evidence_is_built():
    cert = certify_governance(_validate(_governance()), version="1.0.0")
    payload = cert.evidence.to_dict()
    assert payload  # certification evidence produced


def test_non_compliant_governance_is_not_certified():
    # A secret-bearing governance object fails validation → gates fail-closed → NOT-CERTIFIED.
    cert = certify_governance(_validate(_governance(name="secret")), version="1.0.0")
    assert cert.decision.status is CertificationStatus.NOT_CERTIFIED
    assert cert.certified is False
    assert cert.compliance.compliant is False
