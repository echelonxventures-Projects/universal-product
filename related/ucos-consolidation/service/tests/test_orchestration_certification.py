"""EC3-B11-U07 — Orchestration certification tests (CCE CC-1…CC-10 + Service C1…C7)."""

from __future__ import annotations

from engine.certification.ledger import CertificationLedger
from service.orchestration import make_orchestration
from service.orchestration_certification import (
    certify_orchestration,
    evaluate_orchestration_compliance,
)
from service.orchestration_meta import OrchestrationKind
from service.orchestration_traceability import build_orchestration_traceability
from service.orchestration_validation import validate_orchestration

_STEPS = (
    "ENG-005:SOE-05:ucos.service.operation.foundation",
    "ENG-005:SOE-05:ucos.service.operation.secondary",
)


def _validated(cyclic: bool = False):
    if cyclic:
        o = make_orchestration("t", _STEPS,
                               dependencies=((_STEPS[0], _STEPS[1]), (_STEPS[1], _STEPS[0])),
                               kind=OrchestrationKind.CHOREOGRAPHED)
    else:
        o = make_orchestration("ucos.service.orchestration.foundation", _STEPS,
                               kind=OrchestrationKind.SEQUENTIAL,
                               dependencies=((_STEPS[1], _STEPS[0]),),
                               data_refs=("ENG-005:DF-2:ucos.data.entity.orchestrated",))
    trace = build_orchestration_traceability(o, unit="EC3-B11-U07", forward=(o.orchestration_id,))
    return validate_orchestration(o, trace)


def test_ten_gates_close_and_ledger_is_intact():
    cert = certify_orchestration(_validated(), version="1.0.0")
    assert cert.certified is True
    gates = {f.criterion_id: f.passed for f in cert.decision.findings}
    assert set(gates) == {f"CC-{n}" for n in range(1, 11)}
    assert all(gates.values())
    assert cert.ledger.verify() is True
    assert cert.decision.certification_id.startswith("UCOS-CERT-SMC-07-")


def test_compliance_c1_c7_all_pass_with_c5_c6_materially_exercised():
    compliance = evaluate_orchestration_compliance(_validated())
    conditions = {c["id"]: c for c in compliance.conditions}
    assert compliance.compliant is True
    assert set(conditions) == {f"C{n}" for n in range(1, 8)}
    assert "MATERIALLY EXERCISED" in conditions["C5"]["note"]
    assert "MATERIALLY EXERCISED" in conditions["C6"]["note"]


def test_cyclic_orchestration_fails_certification():
    cert = certify_orchestration(_validated(cyclic=True), version="1.0.0")
    assert cert.certified is False
    assert cert.compliance.compliant is False


def test_certification_appends_to_provided_ledger():
    ledger = CertificationLedger()
    certify_orchestration(_validated(), version="1.0.0", ledger=ledger)
    assert len(ledger.to_dict()["entries"]) == 1
