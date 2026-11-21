"""EC3-B11-U05 — Operation certification tests (reused CCE CC-1…CC-10 + Service C1…C7)."""

from __future__ import annotations

from types import SimpleNamespace

from engine.certification.contracts import CertificationStatus
from engine.certification.ledger import CertificationLedger
from service.operation import make_operation
from service.operation_certification import certify_operation, evaluate_operation_compliance
from service.operation_meta import EffectKind, OperationKind
from service.operation_traceability import build_operation_traceability
from service.operation_validation import validate_operation
from service.service_meta import CCE_GATES

_SVC = "ENG-005:SOE-01:svc"
_CON = "ENG-005:SOE-03:contract"
_IFACE = "ENG-005:SOE-04:iface"


def _o(**kw):
    base = dict(
        kind=OperationKind.COMMAND,
        input_refs=("ENG-005:DF-2:req",),
        output_refs=("ENG-005:DF-2:resp",),
        effects=(EffectKind.WRITE,),
        faults=("ucos.fault.bad-input",),
    )
    base.update(kw)
    type_tag = base.pop("type_tag", "t")
    return make_operation(type_tag, _SVC, _CON, _IFACE, **base)


def _validate(operation):
    trace = build_operation_traceability(
        operation, unit="EC3-B11-U05", forward=(operation.operation_id,)
    )
    return validate_operation(operation, trace)


def test_cce_ten_gates_all_close_and_certify():
    cert = certify_operation(_validate(_o()), version="1.0.0")
    assert cert.decision.status is CertificationStatus.CERTIFIED
    assert {f.criterion_id for f in cert.decision.findings} == set(CCE_GATES)
    assert all(f.passed for f in cert.decision.findings)


def test_overall_certification_is_sound():
    cert = certify_operation(_validate(_o()), version="1.0.0")
    assert cert.certified is True
    assert cert.ledger.verify() is True


def test_certification_record_authority_is_engineering_only():
    cert = certify_operation(_validate(_o()), version="1.0.0")
    assert cert.decision.record.authority == "ENGINEERING-EXECUTION-ONLY"
    assert cert.decision.record.disclosure["asserts_constitutional_finality"] is False


def test_certification_id_is_deterministic():
    assert (
        certify_operation(_validate(_o()), version="1.0.0").decision.certification_id
        == certify_operation(_validate(_o()), version="1.0.0").decision.certification_id
    )


def test_operation_compliance_c1_c7_all_hold_with_notes():
    compliance = evaluate_operation_compliance(_validate(_o()))
    assert compliance.compliant is True
    by_id = {c["id"]: c for c in compliance.conditions}
    assert {c["id"] for c in compliance.conditions} == {f"C{n}" for n in range(1, 8)}
    for cid in ("C3", "C4", "C5", "C6"):
        assert "note" in by_id[cid], cid


def test_non_compliant_operation_is_not_certified():
    cert = certify_operation(_validate(_o(input_refs=("ENG-005:DF-2:kafka.topic",))), version="1.0.0")
    assert cert.decision.status is CertificationStatus.NOT_CERTIFIED
    assert cert.certified is False
    assert cert.compliance.compliant is False


def test_supplied_ledger_is_reused():
    ledger = CertificationLedger()
    certify_operation(_validate(_o(type_tag="a")), version="1.0.0", ledger=ledger)
    certify_operation(_validate(_o(type_tag="b")), version="1.0.0", ledger=ledger)
    assert len(ledger) == 2


def test_compliance_fail_branch_when_backing_check_missing():
    fake = SimpleNamespace(
        report=SimpleNamespace(
            target_id="UCOS-OPERATION-x-0000000000000000",
            findings=[SimpleNamespace(check_id="non-constitutive", passed=True)],
        )
    )
    compliance = evaluate_operation_compliance(fake)  # type: ignore[arg-type]
    assert compliance.compliant is False
    assert {c["id"]: c["status"] for c in compliance.conditions}["C1"] == "fail"


def test_all_kinds_certify():
    for kind, effect in (
        (OperationKind.QUERY, EffectKind.READ),
        (OperationKind.COMMAND, EffectKind.WRITE),
        (OperationKind.EVENT, EffectKind.EMIT),
    ):
        assert certify_operation(
            _validate(_o(kind=kind, effects=(effect,))), version="1.0.0"
        ).certified is True, kind
