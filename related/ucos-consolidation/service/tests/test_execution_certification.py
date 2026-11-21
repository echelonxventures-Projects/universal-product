"""EC3-B11-U08 — Execution certification tests (CCE CC-1…CC-10 + Service C1…C7)."""

from __future__ import annotations

from engine.certification.ledger import CertificationLedger
from service.execution import make_execution
from service.execution_certification import (
    certify_execution,
    evaluate_execution_compliance,
)
from service.execution_meta import ExecutionKind
from service.execution_traceability import build_execution_traceability
from service.execution_validation import validate_execution

_OP = "ENG-005:SOE-05:ucos.service.operation.foundation"


def _validated(self_founding: bool = False):
    if self_founding:
        e = make_execution("t", "ENG-005:SOE-08:t", kind=ExecutionKind.SYNCHRONOUS)
    else:
        e = make_execution("ucos.service.execution.foundation", _OP,
                           kind=ExecutionKind.SYNCHRONOUS,
                           data_refs=("ENG-005:DF-2:ucos.data.entity.executed",))
    trace = build_execution_traceability(e, unit="EC3-B11-U08", forward=(e.execution_id,))
    return validate_execution(e, trace)


def test_ten_gates_close_and_ledger_is_intact():
    cert = certify_execution(_validated(), version="1.0.0")
    assert cert.certified is True
    gates = {f.criterion_id: f.passed for f in cert.decision.findings}
    assert set(gates) == {f"CC-{n}" for n in range(1, 11)}
    assert all(gates.values())
    assert cert.ledger.verify() is True
    assert cert.decision.certification_id.startswith("UCOS-CERT-SMC-08-")


def test_compliance_c1_c7_all_pass_with_c3_c6_materially_exercised():
    compliance = evaluate_execution_compliance(_validated())
    conditions = {c["id"]: c for c in compliance.conditions}
    assert compliance.compliant is True
    assert set(conditions) == {f"C{n}" for n in range(1, 8)}
    assert "MATERIALLY EXERCISED" in conditions["C3"]["note"]
    assert "MATERIALLY EXERCISED" in conditions["C6"]["note"]


def test_self_founding_execution_fails_certification():
    cert = certify_execution(_validated(self_founding=True), version="1.0.0")
    assert cert.certified is False
    assert cert.compliance.compliant is False


def test_certification_appends_to_provided_ledger():
    ledger = CertificationLedger()
    certify_execution(_validated(), version="1.0.0", ledger=ledger)
    assert len(ledger.to_dict()["entries"]) == 1
