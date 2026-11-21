"""EC3-B11-U10 — Security certification tests (CCE CC-1…CC-10 + Service C1…C7)."""

from __future__ import annotations

from engine.certification.ledger import CertificationLedger
from service.security import make_security
from service.security_certification import (
    certify_security,
    evaluate_security_compliance,
)
from service.security_meta import SecurityKind
from service.security_traceability import build_security_traceability
from service.security_validation import validate_security

_OP = "ENG-005:SOE-05:ucos.service.operation.foundation"
_POLICY = "ENG-005:SOE-09:ucos.service.policy.foundation"


def _validated(self_founding: bool = False):
    if self_founding:
        s = make_security("t", ("ENG-005:SOE-10:t",), kind=SecurityKind.CONFIDENTIALITY)
    else:
        s = make_security(
            "ucos.service.security.foundation",
            (_OP,),
            kind=SecurityKind.CONFIDENTIALITY,
            policy_refs=(_POLICY,),
            data_refs=("ENG-005:DF-2:ucos.data.entity.governed",),
        )
    trace = build_security_traceability(s, unit="EC3-B11-U10", forward=(s.security_id,))
    return validate_security(s, trace)


def test_ten_gates_close_and_ledger_is_intact():
    cert = certify_security(_validated(), version="1.0.0")
    assert cert.certified is True
    gates = {f.criterion_id: f.passed for f in cert.decision.findings}
    assert set(gates) == {f"CC-{n}" for n in range(1, 11)}
    assert all(gates.values())
    assert cert.ledger.verify() is True
    assert cert.decision.certification_id.startswith("UCOS-CERT-SMC-10-")


def test_compliance_c1_c7_all_pass_with_c6_c7_materially_exercised():
    compliance = evaluate_security_compliance(_validated())
    conditions = {c["id"]: c for c in compliance.conditions}
    assert compliance.compliant is True
    assert set(conditions) == {f"C{n}" for n in range(1, 8)}
    assert "MATERIALLY EXERCISED" in conditions["C6"]["note"]
    assert "MATERIALLY EXERCISED" in conditions["C7"]["note"]


def test_self_founding_security_fails_certification():
    cert = certify_security(_validated(self_founding=True), version="1.0.0")
    assert cert.certified is False
    assert cert.compliance.compliant is False


def test_certification_appends_to_provided_ledger():
    ledger = CertificationLedger()
    certify_security(_validated(), version="1.0.0", ledger=ledger)
    assert len(ledger.to_dict()["entries"]) == 1
