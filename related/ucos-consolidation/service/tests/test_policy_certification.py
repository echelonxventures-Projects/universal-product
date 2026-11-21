"""EC3-B11-U09 — Policy certification tests (CCE CC-1…CC-10 + Service C1…C7)."""

from __future__ import annotations

from engine.certification.ledger import CertificationLedger
from service.policy import make_policy
from service.policy_certification import (
    certify_policy,
    evaluate_policy_compliance,
)
from service.policy_meta import PolicyKind
from service.policy_traceability import build_policy_traceability
from service.policy_validation import validate_policy

_CONTRACT = "ENG-005:SOE-03:ucos.service.contract.foundation"
_OP = "ENG-005:SOE-05:ucos.service.operation.foundation"


def _validated(self_founding: bool = False):
    if self_founding:
        p = make_policy("t", "ENG-005:SOE-09:t", kind=PolicyKind.AUTHORIZATION)
    else:
        p = make_policy(
            "ucos.service.policy.foundation",
            _CONTRACT,
            kind=PolicyKind.AUTHORIZATION,
            subject_refs=(_OP,),
            data_refs=("ENG-005:DF-2:ucos.data.entity.governed",),
        )
    trace = build_policy_traceability(p, unit="EC3-B11-U09", forward=(p.policy_id,))
    return validate_policy(p, trace)


def test_ten_gates_close_and_ledger_is_intact():
    cert = certify_policy(_validated(), version="1.0.0")
    assert cert.certified is True
    gates = {f.criterion_id: f.passed for f in cert.decision.findings}
    assert set(gates) == {f"CC-{n}" for n in range(1, 11)}
    assert all(gates.values())
    assert cert.ledger.verify() is True
    assert cert.decision.certification_id.startswith("UCOS-CERT-SMC-09-")


def test_compliance_c1_c7_all_pass_with_c6_c7_materially_exercised():
    compliance = evaluate_policy_compliance(_validated())
    conditions = {c["id"]: c for c in compliance.conditions}
    assert compliance.compliant is True
    assert set(conditions) == {f"C{n}" for n in range(1, 8)}
    assert "MATERIALLY EXERCISED" in conditions["C6"]["note"]
    assert "MATERIALLY EXERCISED" in conditions["C7"]["note"]


def test_self_founding_policy_fails_certification():
    cert = certify_policy(_validated(self_founding=True), version="1.0.0")
    assert cert.certified is False
    assert cert.compliance.compliant is False


def test_certification_appends_to_provided_ledger():
    ledger = CertificationLedger()
    certify_policy(_validated(), version="1.0.0", ledger=ledger)
    assert len(ledger.to_dict()["entries"]) == 1
