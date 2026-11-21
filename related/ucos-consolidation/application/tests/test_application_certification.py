"""EC3-B12-U01 — Application certification tests (CCE CC-1…CC-10 + Application C1…C7)."""

from __future__ import annotations

from engine.certification.contracts import (
    CertificationClass,
    CertificationSubject,
    CriterionStatus,
)
from application.application import make_application
from application.application_certification import (
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
    certify_application,
    evaluate_application_compliance,
)
from application.application_traceability import build_traceability
from application.application_validation import application_checks, validate_application

CAP_REF = "ENG-005:CAPABILITY:ucos.demo.capability"
UNIT = "EC3-B12-U01"
FWD = ("f1", "f2")

_ALL_CHECKS = tuple(c.check_id for c in application_checks())


def _validated(app=None):
    app = app or make_application("t", CAP_REF)
    trace = build_traceability(app, unit=UNIT, forward=FWD)
    return validate_application(app, trace)


def _good_subject(**overrides) -> CertificationSubject:
    """A crafted certification subject where every gate would otherwise close."""
    base = dict(
        target_id="UCOS-APPLICATION-ucos.demo.application-0000000000000000",
        blueprint_id="AMC-01",
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


def test_cce_suite_has_ten_blocking_gates():
    gates = cce_gates()
    assert len(gates) == 10
    ids = [g.criterion_id for g in gates]
    assert ids == [f"CC-{n}" for n in range(1, 11)]
    assert all(g.severity.name == "BLOCKING" for g in gates)


def test_certify_application_certifies_valid_application():
    cert = certify_application(_validated(), version="1.0.0")
    assert cert.certified is True
    assert cert.decision.certified is True
    assert cert.ledger.verify() is True
    assert cert.compliance.compliant is True
    assert cert.decision.certification_id.startswith("UCOS-CERT-AMC-01-")


def test_all_ten_gates_pass_for_valid_application():
    cert = certify_application(_validated(), version="1.0.0")
    gate_results = {f.criterion_id: f.passed for f in cert.decision.findings}
    assert all(gate_results.values())
    assert set(gate_results) == {f"CC-{n}" for n in range(1, 11)}


def test_ledger_entry_is_recorded_and_chain_intact():
    cert = certify_application(_validated(), version="1.0.0")
    assert cert.ledger_entry is not None
    assert cert.ledger.verify() is True


def test_compliance_report_all_conditions_pass():
    report = evaluate_application_compliance(_validated())
    assert report.compliant is True
    ids = [c["id"] for c in report.conditions]
    assert ids == ["C1", "C2", "C3", "C4", "C5", "C6", "C7"]
    for c in report.conditions:
        assert c["status"] == "pass"
        assert c["backed_by"]


def test_compliance_c3_and_c4_carry_scope_notes():
    report = evaluate_application_compliance(_validated())
    by_id = {c["id"]: c for c in report.conditions}
    assert "note" in by_id["C3"]
    assert "AMC-04" in by_id["C3"]["note"]
    assert "note" in by_id["C4"]
    assert "AMC-03/04/06" in by_id["C4"]["note"]


def test_compliance_report_serializes_deterministically():
    report = evaluate_application_compliance(_validated())
    payload = report.to_dict()
    assert payload["standard"] == "APPLICATION-001 §12"
    assert payload["compliant"] is True
    assert payload["compliance_format"] == "ucos-application-compliance/1.0.0"
    assert payload["target_id"].startswith("UCOS-APPLICATION-")


def test_compliance_fails_when_a_backing_check_fails():
    # A technology-bearing application fails technology-independence → C7 fails.
    techy = make_application("t", "ENG-005:CAPABILITY:kafka.stream")
    trace = build_traceability(techy, unit=UNIT, forward=FWD)
    validation = validate_application(techy, trace)
    report = evaluate_application_compliance(validation)
    by_id = {c["id"]: c for c in report.conditions}
    assert by_id["C7"]["status"] == "fail"
    assert report.compliant is False


def test_certification_not_certified_for_rejected_application():
    techy = make_application("t", "ENG-005:CAPABILITY:kafka.stream")
    trace = build_traceability(techy, unit=UNIT, forward=FWD)
    validation = validate_application(techy, trace)
    cert = certify_application(validation, version="1.0.0")
    assert cert.certified is False


def test_certification_reuses_supplied_ledger():
    from engine.certification.ledger import CertificationLedger

    ledger = CertificationLedger()
    c1 = certify_application(_validated(make_application("a", CAP_REF)), version="1.0.0", ledger=ledger)
    c2 = certify_application(_validated(make_application("b", CAP_REF)), version="1.0.0", ledger=ledger)
    assert c1.ledger is ledger
    assert c2.ledger is ledger
    assert ledger.verify() is True



# --- per-gate negative coverage (crafted CertificationSubject) -------------


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
