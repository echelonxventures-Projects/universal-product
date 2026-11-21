"""EC3-B12-U05 — Workflow certification tests (CCE CC-1…CC-10 + Application C1…C7)."""

from __future__ import annotations

from application.workflow import make_workflow
from application.workflow_certification import (
    cce_gates,
    certify_workflow,
    evaluate_workflow_compliance,
)
from application.workflow_meta import REALIZATION_UNIT, WorkflowKind
from application.workflow_traceability import build_traceability
from application.workflow_validation import validate_workflow

SEQ = (
    "ENG-005:AMC-04:ucos.demo.feature.a",
    "ENG-005:AMC-04:ucos.demo.feature.b",
)
ONE_OP = ("ENG-005:SF-2:ucos.demo.operation.a",)


def _validated(workflow, *, forward=("fwd",)):
    trace = build_traceability(workflow, unit=REALIZATION_UNIT, forward=forward)
    return validate_workflow(workflow, trace)


def test_cce_gates_are_ten_and_ordered():
    gates = cce_gates()
    assert [g.criterion_id for g in gates] == [f"CC-{n}" for n in range(1, 11)]


def test_certify_valid_workflow_is_certified():
    validation = _validated(make_workflow("t", SEQ, ONE_OP, kind=WorkflowKind.PROCESS))
    cert = certify_workflow(validation, version="1.0.0")
    assert cert.certified is True
    gates = {f.criterion_id: f.passed for f in cert.decision.findings}
    assert all(gates.values())
    assert cert.decision.certification_id.startswith("UCOS-CERT-AMC-05-")
    assert cert.ledger.verify() is True
    assert cert.ledger_entry.sequence == 0


def test_compliance_all_seven_conditions_pass_with_c6_governing():
    validation = _validated(make_workflow("t", SEQ, ONE_OP))
    report = evaluate_workflow_compliance(validation)
    assert report.compliant is True
    ids = {c["id"] for c in report.conditions}
    assert ids == {f"C{n}" for n in range(1, 8)}
    # C6 is the governing condition for AMC-05 and carries the material note.
    c6 = next(c for c in report.conditions if c["id"] == "C6")
    assert c6["status"] == "pass"
    assert "governing" in c6["note"]
    assert "behavior-by-reference" in c6["backed_by"]
    assert "workflow-holds-state" in c6["backed_by"]
    # C3/C4/C5 carry scoping notes.
    for cid in ("C3", "C4", "C5"):
        assert next(c for c in report.conditions if c["id"] == cid)["note"]


def test_compliance_to_dict_shape():
    validation = _validated(make_workflow("t", SEQ, ONE_OP))
    payload = evaluate_workflow_compliance(validation).to_dict()
    assert payload["standard"] == "APPLICATION-001 §12"
    assert payload["compliant"] is True
    assert payload["target_id"].startswith("UCOS-WORKFLOW-")
    assert len(payload["conditions"]) == 7


def test_technology_bearing_workflow_is_not_certified():
    validation = _validated(make_workflow("t", ("ENG-005:AMC-04:temporal.wf",), ONE_OP))
    cert = certify_workflow(validation, version="1.0.0")
    assert cert.certified is False
    assert cert.compliance.compliant is False


def test_certification_appends_to_supplied_ledger():
    from engine.certification.ledger import CertificationLedger

    ledger = CertificationLedger()
    v1 = _validated(make_workflow("wf-a", SEQ, ONE_OP))
    v2 = _validated(make_workflow("wf-b", SEQ, ONE_OP))
    c1 = certify_workflow(v1, version="1.0.0", ledger=ledger)
    c2 = certify_workflow(v2, version="1.0.0", ledger=ledger)
    assert c1.ledger_entry.sequence == 0
    assert c2.ledger_entry.sequence == 1
    assert ledger.verify() is True


def test_certification_is_deterministic():
    v = _validated(make_workflow("t", SEQ, ONE_OP, kind=WorkflowKind.PROCESS))
    a = certify_workflow(v, version="1.0.0")
    b = certify_workflow(v, version="1.0.0")
    assert a.decision.certification_id == b.decision.certification_id



# --- per-gate negative coverage (crafted CertificationSubject) -------------------

from engine.certification.contracts import (  # noqa: E402
    CertificationClass,
    CertificationSubject,
    CriterionStatus,
)

from application.workflow_certification import (  # noqa: E402
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
)
from application.workflow_validation import workflow_checks  # noqa: E402

_ALL_CHECKS = tuple(c.check_id for c in workflow_checks())


def _good_subject(**overrides) -> CertificationSubject:
    """A crafted certification subject where every gate would otherwise close."""
    base = dict(
        target_id="UCOS-WORKFLOW-ucos.demo.workflow-0000000000000000",
        blueprint_id="AMC-05",
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


def test_all_gates_pass_on_good_subject():
    subject = _good_subject()
    for gate in cce_gates():
        assert gate.evaluate(subject).status is CriterionStatus.PASS, gate.criterion_id


def test_gate1_fails_on_orphan():
    assert Gate1Architecture().evaluate(
        _good_subject(blocking_failures=("traceability-rooted",))
    ).status is CriterionStatus.FAIL


def test_gate2_fails_on_broken_substrate():
    assert Gate2Dependencies().evaluate(
        _good_subject(blocking_failures=("foundation-reuse-integrity",))
    ).status is CriterionStatus.FAIL


def test_gate2_fails_when_operation_not_consumed():
    assert Gate2Dependencies().evaluate(
        _good_subject(blocking_failures=("workflow-consumes-operation",))
    ).status is CriterionStatus.FAIL


def test_gate2_fails_when_required_check_not_run():
    # A required check absent from checks_run is a "not-run" defect (fail-closed).
    assert Gate2Dependencies().evaluate(
        _good_subject(checks_run=())
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
