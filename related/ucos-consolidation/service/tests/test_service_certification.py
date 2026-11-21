"""EC3-B11-U01 — Certification tests (CCE CC-1…CC-10 + Service C1…C7 + ledger).

Per-gate negative coverage is achieved by constructing a crafted
:class:`engine.certification.contracts.CertificationSubject` and flipping the single
signal each gate aggregates, then calling the gate's ``evaluate`` directly.
"""

from __future__ import annotations

from engine.certification.contracts import (
    CertificationClass,
    CertificationStatus,
    CertificationSubject,
    CriterionStatus,
)
from service.service import make_service
from service.service_certification import (
    Gate1Architecture,
    Gate2Dependencies,
    Gate3Coverage,
    Gate4Validation,
    Gate5Traceability,
    Gate6Evidence,
    Gate7CertificationReady,
    Gate8Readiness,
    Gate9GapZero,
    Gate10Completeness,
    cce_gates,
    certify_service,
    evaluate_service_compliance,
)
from service.service_meta import CCE_GATES
from service.service_traceability import build_traceability
from service.service_validation import service_checks, validate_service

CAP_REF = "ENG-005:CAPABILITY:ucos.demo.capability"

_ALL_CHECKS = tuple(c.check_id for c in service_checks())


def _validate(service):
    trace = build_traceability(service, unit="EC3-B11-U01", forward=(service.service_id,))
    return validate_service(service, trace)


def _good_subject(**overrides) -> CertificationSubject:
    """A crafted certification subject where every gate would otherwise close."""
    base = dict(
        target_id="UCOS-SERVICE-ucos.demo.service-0000000000000000",
        blueprint_id="SMC-01",
        version="1.0.0",
        certification_class=CertificationClass.ENGINEERING_READINESS,
        validation_verdict="pass",
        validation_accepted=True,
        checks_run=_ALL_CHECKS,
        blocking_failures=(),
        counts={"failed": 0, "total": len(_ALL_CHECKS)},
        evidence_present=True,
        evidence_sha256="a" * 64,
    )
    base.update(overrides)
    return CertificationSubject(**base)


# --- happy path -------------------------------------------------------------


def test_cce_ten_gates_all_close_and_certify():
    cert = certify_service(_validate(make_service("t", CAP_REF)), version="1.0.0")
    assert cert.decision.status is CertificationStatus.CERTIFIED
    assert {f.criterion_id for f in cert.decision.findings} == set(CCE_GATES)  # CC-1…CC-10
    assert all(f.passed for f in cert.decision.findings)
    assert len(cce_gates()) == 10


def test_certification_record_is_immutable_and_self_verifying():
    cert = certify_service(_validate(make_service("t", CAP_REF)), version="1.0.0")
    assert cert.decision.record.verify_integrity() is True
    assert cert.decision.record.authority == "ENGINEERING-EXECUTION-ONLY"  # DE-05
    assert cert.decision.record.disclosure["asserts_constitutional_finality"] is False


def test_ledger_is_append_only_and_hash_chain_intact():
    cert = certify_service(_validate(make_service("t", CAP_REF)), version="1.0.0")
    assert cert.ledger.verify() is True  # CC-10 chain intact
    assert len(cert.ledger) == 1
    assert cert.ledger_entry.sequence == 0
    assert cert.ledger_entry.prev_hash == "0" * 64


def test_service_compliance_c1_c7_all_hold():
    compliance = evaluate_service_compliance(_validate(make_service("t", CAP_REF)))
    assert compliance.compliant is True
    assert {c["id"] for c in compliance.conditions} == {f"C{n}" for n in range(1, 8)}
    assert all(c["status"] == "pass" for c in compliance.conditions)
    payload = compliance.to_dict()
    assert payload["standard"] == "SERVICE-001 §12"
    assert payload["compliant"] is True


def test_overall_certification_is_sound():
    cert = certify_service(_validate(make_service("t", CAP_REF)), version="1.0.0")
    assert cert.certified is True  # decision + ledger + compliance


def test_certification_id_is_deterministic():
    a = certify_service(_validate(make_service("t", CAP_REF)), version="1.0.0")
    b = certify_service(_validate(make_service("t", CAP_REF)), version="1.0.0")
    assert a.decision.certification_id == b.decision.certification_id


def test_non_compliant_service_is_not_certified():
    # A technology-selecting service fails validation → gates fail-closed → NOT-CERTIFIED.
    cert = certify_service(_validate(make_service("t", "ENG-005:CAPABILITY:kafka")), version="1.0.0")
    assert cert.decision.status is CertificationStatus.NOT_CERTIFIED
    assert cert.certified is False
    assert cert.compliance.compliant is False


def test_supplied_ledger_is_reused():
    from engine.certification.ledger import CertificationLedger

    ledger = CertificationLedger()
    certify_service(_validate(make_service("t", CAP_REF)), version="1.0.0", ledger=ledger)
    certify_service(_validate(make_service("t", "ENG-005:CAPABILITY:other")), version="1.0.0", ledger=ledger)
    assert len(ledger) == 2


# --- per-gate negative coverage --------------------------------------------


def test_gate1_fails_on_orphan():
    assert Gate1Architecture().evaluate(
        _good_subject(blocking_failures=("traceability-rooted",))
    ).status is CriterionStatus.FAIL


def test_gate2_fails_on_broken_substrate():
    assert Gate2Dependencies().evaluate(
        _good_subject(blocking_failures=("foundation-reuse-integrity",))
    ).status is CriterionStatus.FAIL


def test_gate3_fails_on_structural_violation():
    assert Gate3Coverage().evaluate(
        _good_subject(blocking_failures=("founding-acyclic",), counts={"failed": 1})
    ).status is CriterionStatus.FAIL


def test_gate4_fails_when_validation_not_accepted():
    assert Gate4Validation().evaluate(
        _good_subject(validation_accepted=False, validation_verdict="fail")
    ).status is CriterionStatus.FAIL


def test_gate5_fails_on_broken_lineage():
    assert Gate5Traceability().evaluate(
        _good_subject(blocking_failures=("traceability-rooted",))
    ).status is CriterionStatus.FAIL


def test_gate6_fails_when_evidence_absent():
    assert Gate6Evidence().evaluate(
        _good_subject(evidence_present=False, evidence_sha256="")
    ).status is CriterionStatus.FAIL


def test_gate7_fails_when_disclosure_absent():
    assert Gate7CertificationReady().evaluate(
        _good_subject(blocking_failures=("provisional-state-disclosure",))
    ).status is CriterionStatus.FAIL


def test_gate8_fails_on_blockers():
    assert Gate8Readiness().evaluate(
        _good_subject(blocking_failures=("some-check",))
    ).status is CriterionStatus.FAIL


def test_gate9_fails_on_open_gap():
    assert Gate9GapZero().evaluate(
        _good_subject(counts={"failed": 2})
    ).status is CriterionStatus.FAIL


def test_gate10_fails_when_prerequisites_open():
    assert Gate10Completeness().evaluate(
        _good_subject(validation_accepted=False)
    ).status is CriterionStatus.FAIL


def test_all_gates_pass_on_good_subject():
    subject = _good_subject()
    for gate in cce_gates():
        assert gate.evaluate(subject).status is CriterionStatus.PASS, gate.criterion_id


def test_gate_reports_a_required_check_that_did_not_run():
    # A required check absent from checks_run is a "not-run" defect (fail-closed).
    assert Gate2Dependencies().evaluate(
        _good_subject(checks_run=())
    ).status is CriterionStatus.FAIL
