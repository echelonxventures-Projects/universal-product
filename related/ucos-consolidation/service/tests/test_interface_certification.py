"""EC3-B11-U04 — Interface certification tests (reused CCE CC-1…CC-10 + Service C1…C7)."""

from __future__ import annotations

from types import SimpleNamespace

from engine.certification.contracts import CertificationStatus
from engine.certification.ledger import CertificationLedger
from service.interface import make_interface
from service.interface_certification import certify_interface, evaluate_interface_compliance
from service.interface_meta import InterfaceKind
from service.interface_traceability import build_interface_traceability
from service.interface_validation import validate_interface
from service.service_meta import CCE_GATES

_SVC = "ENG-005:SOE-01:svc"
_OPS = ("ENG-005:SOE-05:op",)
_IO = ("ENG-005:DF-2:req", "ENG-005:DF-2:resp")


def _i(**kw):
    base = dict(
        type_tag="t", service_ref=_SVC, operations=_OPS, io_refs=_IO,
        endpoint_ref="ENG-005:locus:abstract",
    )
    base.update(kw)
    return make_interface(**base)


def _validate(interface):
    trace = build_interface_traceability(
        interface, unit="EC3-B11-U04", forward=(interface.interface_id,)
    )
    return validate_interface(interface, trace)


def test_cce_ten_gates_all_close_and_certify():
    cert = certify_interface(_validate(_i()), version="1.0.0")
    assert cert.decision.status is CertificationStatus.CERTIFIED
    assert {f.criterion_id for f in cert.decision.findings} == set(CCE_GATES)
    assert all(f.passed for f in cert.decision.findings)


def test_overall_certification_is_sound():
    cert = certify_interface(_validate(_i()), version="1.0.0")
    assert cert.certified is True
    assert cert.ledger.verify() is True


def test_certification_record_authority_is_engineering_only():
    cert = certify_interface(_validate(_i()), version="1.0.0")
    assert cert.decision.record.authority == "ENGINEERING-EXECUTION-ONLY"
    assert cert.decision.record.disclosure["asserts_constitutional_finality"] is False


def test_certification_id_is_deterministic():
    assert (
        certify_interface(_validate(_i()), version="1.0.0").decision.certification_id
        == certify_interface(_validate(_i()), version="1.0.0").decision.certification_id
    )


def test_interface_compliance_c1_c7_all_hold_with_notes():
    compliance = evaluate_interface_compliance(_validate(_i()))
    assert compliance.compliant is True
    by_id = {c["id"]: c for c in compliance.conditions}
    assert {c["id"] for c in compliance.conditions} == {f"C{n}" for n in range(1, 8)}
    for cid in ("C3", "C4", "C5", "C6"):
        assert "note" in by_id[cid], cid


def test_non_compliant_interface_is_not_certified():
    cert = certify_interface(_validate(_i(operations=("ENG-005:SOE-05:kafka.topic",))), version="1.0.0")
    assert cert.decision.status is CertificationStatus.NOT_CERTIFIED
    assert cert.certified is False
    assert cert.compliance.compliant is False


def test_supplied_ledger_is_reused():
    ledger = CertificationLedger()
    certify_interface(_validate(_i(type_tag="a")), version="1.0.0", ledger=ledger)
    certify_interface(_validate(_i(type_tag="b")), version="1.0.0", ledger=ledger)
    assert len(ledger) == 2


def test_compliance_fail_branch_when_backing_check_missing():
    fake = SimpleNamespace(
        report=SimpleNamespace(
            target_id="UCOS-INTERFACE-x-0000000000000000",
            findings=[SimpleNamespace(check_id="non-constitutive", passed=True)],
        )
    )
    compliance = evaluate_interface_compliance(fake)  # type: ignore[arg-type]
    assert compliance.compliant is False
    assert {c["id"]: c["status"] for c in compliance.conditions}["C1"] == "fail"


def test_all_kinds_certify():
    for kind in InterfaceKind:
        assert certify_interface(_validate(_i(kind=kind)), version="1.0.0").certified is True, kind
