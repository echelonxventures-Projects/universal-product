"""EC3-B11-U02 — Capability certification tests (reused CCE CC-1…CC-10 + Service C1…C7).

The CCE ten gates are reused verbatim from ``service.service_certification`` (already
covered there); here we exercise ``certify_capability`` and the capability-specific
compliance mapping (including the fail and note branches).
"""

from __future__ import annotations

from types import SimpleNamespace

from engine.certification.contracts import CertificationStatus
from engine.certification.ledger import CertificationLedger
from service.capability import make_capability
from service.capability_certification import (
    certify_capability,
    evaluate_capability_compliance,
)
from service.capability_meta import CapabilityKind
from service.capability_traceability import build_capability_traceability
from service.capability_validation import validate_capability
from service.service_meta import CCE_GATES


def _validate(capability):
    trace = build_capability_traceability(
        capability, unit="EC3-B11-U02", forward=(capability.capability_id,)
    )
    return validate_capability(capability, trace)


def test_cce_ten_gates_all_close_and_certify():
    cert = certify_capability(_validate(make_capability("t", service_ref="ENG-005:SMC-01:s")), version="1.0.0")
    assert cert.decision.status is CertificationStatus.CERTIFIED
    assert {f.criterion_id for f in cert.decision.findings} == set(CCE_GATES)  # CC-1…CC-10
    assert all(f.passed for f in cert.decision.findings)


def test_overall_certification_is_sound():
    cert = certify_capability(_validate(make_capability("t")), version="1.0.0")
    assert cert.certified is True  # decision + ledger + compliance
    assert cert.ledger.verify() is True
    assert cert.ledger_entry.sequence == 0


def test_certification_record_authority_is_engineering_only():
    cert = certify_capability(_validate(make_capability("t")), version="1.0.0")
    assert cert.decision.record.authority == "ENGINEERING-EXECUTION-ONLY"
    assert cert.decision.record.disclosure["asserts_constitutional_finality"] is False


def test_certification_id_is_deterministic():
    a = certify_capability(_validate(make_capability("t")), version="1.0.0")
    b = certify_capability(_validate(make_capability("t")), version="1.0.0")
    assert a.decision.certification_id == b.decision.certification_id


def test_capability_compliance_c1_c7_all_hold_with_notes():
    compliance = evaluate_capability_compliance(_validate(make_capability("t")))
    assert compliance.compliant is True
    assert {c["id"] for c in compliance.conditions} == {f"C{n}" for n in range(1, 8)}
    by_id = {c["id"]: c for c in compliance.conditions}
    assert "note" in by_id["C3"]
    assert "note" in by_id["C4"]
    assert compliance.to_dict()["standard"] == "SERVICE-001 §12"


def test_non_compliant_capability_is_not_certified():
    # A technology-selecting capability fails validation → gates fail-closed.
    cert = certify_capability(
        _validate(make_capability("t", behavior_ref="ENG-005:RL-F2:kafka")), version="1.0.0"
    )
    assert cert.decision.status is CertificationStatus.NOT_CERTIFIED
    assert cert.certified is False
    assert cert.compliance.compliant is False


def test_supplied_ledger_is_reused():
    ledger = CertificationLedger()
    certify_capability(_validate(make_capability("a")), version="1.0.0", ledger=ledger)
    certify_capability(_validate(make_capability("b")), version="1.0.0", ledger=ledger)
    assert len(ledger) == 2


def test_compliance_fail_branch_when_backing_check_missing():
    # A validation whose findings omit the C1-backing checks yields a failing C1.
    fake = SimpleNamespace(
        report=SimpleNamespace(
            target_id="UCOS-CAPABILITY-x-0000000000000000",
            findings=[SimpleNamespace(check_id="non-constitutive", passed=True)],
        )
    )
    compliance = evaluate_capability_compliance(fake)  # type: ignore[arg-type]
    assert compliance.compliant is False
    by_id = {c["id"]: c["status"] for c in compliance.conditions}
    assert by_id["C1"] == "fail"


def test_all_kinds_certify():
    for kind in CapabilityKind:
        cert = certify_capability(_validate(make_capability("t", kind=kind)), version="1.0.0")
        assert cert.certified is True, kind
