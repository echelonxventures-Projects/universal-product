"""EC3-B11-U03 — Contract certification tests (reused CCE CC-1…CC-10 + Service C1…C7)."""

from __future__ import annotations

from types import SimpleNamespace

from engine.certification.contracts import CertificationStatus
from engine.certification.ledger import CertificationLedger
from service.contract import make_contract
from service.contract_certification import certify_contract, evaluate_contract_compliance
from service.contract_meta import ContractKind
from service.contract_traceability import build_contract_traceability
from service.contract_validation import validate_contract
from service.service_meta import CCE_GATES

_IN = ("ENG-005:DF-2:req",)
_OUT = ("ENG-005:DF-2:resp",)


def _c(**kw):
    base = dict(type_tag="t", inputs=_IN, outputs=_OUT, effects=("ENG-005:e",), faults=("ENG-005:f",))
    base.update(kw)
    return make_contract(**base)


def _validate(contract):
    trace = build_contract_traceability(contract, unit="EC3-B11-U03", forward=(contract.contract_id,))
    return validate_contract(contract, trace)


def test_cce_ten_gates_all_close_and_certify():
    cert = certify_contract(_validate(_c()), version="1.0.0")
    assert cert.decision.status is CertificationStatus.CERTIFIED
    assert {f.criterion_id for f in cert.decision.findings} == set(CCE_GATES)
    assert all(f.passed for f in cert.decision.findings)


def test_overall_certification_is_sound():
    cert = certify_contract(_validate(_c()), version="1.0.0")
    assert cert.certified is True
    assert cert.ledger.verify() is True


def test_certification_record_authority_is_engineering_only():
    cert = certify_contract(_validate(_c()), version="1.0.0")
    assert cert.decision.record.authority == "ENGINEERING-EXECUTION-ONLY"
    assert cert.decision.record.disclosure["asserts_constitutional_finality"] is False


def test_certification_id_is_deterministic():
    assert (
        certify_contract(_validate(_c()), version="1.0.0").decision.certification_id
        == certify_contract(_validate(_c()), version="1.0.0").decision.certification_id
    )


def test_contract_compliance_c1_c7_all_hold_with_notes():
    compliance = evaluate_contract_compliance(_validate(_c()))
    assert compliance.compliant is True
    by_id = {c["id"]: c for c in compliance.conditions}
    assert {c["id"] for c in compliance.conditions} == {f"C{n}" for n in range(1, 8)}
    for cid in ("C3", "C4", "C5", "C6"):
        assert "note" in by_id[cid], cid


def test_non_compliant_contract_is_not_certified():
    cert = certify_contract(_validate(_c(inputs=("ENG-005:DF-2:kafka",))), version="1.0.0")
    assert cert.decision.status is CertificationStatus.NOT_CERTIFIED
    assert cert.certified is False
    assert cert.compliance.compliant is False


def test_supplied_ledger_is_reused():
    ledger = CertificationLedger()
    certify_contract(_validate(_c(type_tag="a")), version="1.0.0", ledger=ledger)
    certify_contract(_validate(_c(type_tag="b")), version="1.0.0", ledger=ledger)
    assert len(ledger) == 2


def test_compliance_fail_branch_when_backing_check_missing():
    fake = SimpleNamespace(
        report=SimpleNamespace(
            target_id="UCOS-CONTRACT-x-0000000000000000",
            findings=[SimpleNamespace(check_id="non-constitutive", passed=True)],
        )
    )
    compliance = evaluate_contract_compliance(fake)  # type: ignore[arg-type]
    assert compliance.compliant is False
    assert {c["id"]: c["status"] for c in compliance.conditions}["C1"] == "fail"


def test_all_kinds_certify():
    for kind in ContractKind:
        assert certify_contract(_validate(_c(kind=kind)), version="1.0.0").certified is True, kind
