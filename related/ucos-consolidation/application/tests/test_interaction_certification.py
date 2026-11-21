"""EC3-B12-U06 — Interaction certification tests (CCE CC-1…CC-10 + Application C1…C7)."""

from __future__ import annotations

from types import SimpleNamespace

from application.interaction import make_interaction
from application.interaction_certification import (
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
    certify_interaction,
    evaluate_interaction_compliance,
)
from application.interaction_meta import InteractionKind
from application.interaction_traceability import build_traceability
from application.interaction_validation import validate_interaction

FEATURE = "ENG-005:AMC-04:ucos.demo.feature.a"

_ALL_CHECKS = (
    "traceability-rooted",
    "meta-class-single",
    "foundation-reuse-integrity",
    "interaction-presents-data",
    "interaction-value-fidelity",
    "founding-acyclic",
    "meta-relationships-closed",
    "provisional-state-disclosure",
)


def _ok_subject(**overrides) -> SimpleNamespace:
    base = dict(
        checks_run=set(_ALL_CHECKS),
        blocking_failures=set(),
        counts={"failed": 0},
        validation_accepted=True,
        validation_verdict="pass",
        evidence_present=True,
        evidence_sha256="a" * 64,
    )
    base.update(overrides)
    return SimpleNamespace(**base)


def _validated(interaction):
    trace = build_traceability(
        interaction, unit="EC3-B12-U06", forward=(interaction.interaction_id, "X")
    )
    return validate_interaction(interaction, trace)


# -- happy path: full certification over a valid interaction ----------------------


def test_certify_valid_interaction_is_certified_and_ledgered():
    validation = _validated(make_interaction("ucos.demo.interaction", FEATURE))
    cert = certify_interaction(validation, version="1.0.0")
    assert cert.certified is True
    assert cert.decision.certified is True
    assert cert.ledger.verify() is True
    assert cert.compliance.compliant is True
    assert cert.decision.certification_id.startswith("UCOS-CERT-AMC-06-")
    gates = {f.criterion_id: f.passed for f in cert.decision.findings}
    assert set(gates) == {f"CC-{n}" for n in range(1, 11)}
    assert all(gates.values())


def test_cce_gates_suite_has_ten_blocking_gates():
    gates = cce_gates()
    assert len(gates) == 10
    assert [g.criterion_id for g in gates] == [f"CC-{n}" for n in range(1, 11)]


# -- each gate: pass on ok subject, fail on a targeted defect ----------------------


def test_gate1_architecture_pass_and_fail():
    assert Gate1Architecture().evaluate(_ok_subject()).passed is True
    bad = _ok_subject(blocking_failures={"traceability-rooted"})
    assert Gate1Architecture().evaluate(bad).passed is False


def test_gate2_dependencies_pass_and_fail():
    assert Gate2Dependencies().evaluate(_ok_subject()).passed is True
    bad = _ok_subject(blocking_failures={"interaction-presents-data"})
    assert Gate2Dependencies().evaluate(bad).passed is False


def test_gate3_coverage_pass_and_fail():
    assert Gate3Coverage().evaluate(_ok_subject()).passed is True
    bad_checks = _ok_subject(blocking_failures={"founding-acyclic"})
    assert Gate3Coverage().evaluate(bad_checks).passed is False
    bad_count = _ok_subject(counts={"failed": 1})
    assert Gate3Coverage().evaluate(bad_count).passed is False


def test_gate4_validation_pass_and_fail():
    assert Gate4Validation().evaluate(_ok_subject()).passed is True
    bad = _ok_subject(validation_accepted=False, validation_verdict="fail")
    assert Gate4Validation().evaluate(bad).passed is False


def test_gate5_traceability_pass_and_fail():
    assert Gate5Traceability().evaluate(_ok_subject()).passed is True
    bad = _ok_subject(blocking_failures={"traceability-rooted"})
    assert Gate5Traceability().evaluate(bad).passed is False


def test_gate6_evidence_pass_and_fail():
    assert Gate6Evidence().evaluate(_ok_subject()).passed is True
    bad = _ok_subject(evidence_present=False, evidence_sha256="")
    assert Gate6Evidence().evaluate(bad).passed is False


def test_gate7_certification_ready_pass_and_fail():
    assert Gate7CertificationReady().evaluate(_ok_subject()).passed is True
    bad = _ok_subject(blocking_failures={"provisional-state-disclosure"})
    assert Gate7CertificationReady().evaluate(bad).passed is False


def test_gate8_readiness_pass_and_fail():
    assert Gate8Readiness().evaluate(_ok_subject()).passed is True
    bad = _ok_subject(blocking_failures={"non-constitutive"})
    assert Gate8Readiness().evaluate(bad).passed is False


def test_gate9_gap_zero_pass_and_fail():
    assert Gate9GapZero().evaluate(_ok_subject()).passed is True
    bad = _ok_subject(counts={"failed": 2})
    assert Gate9GapZero().evaluate(bad).passed is False


def test_gate10_completeness_pass_and_fail():
    assert Gate10Completeness().evaluate(_ok_subject()).passed is True
    bad = _ok_subject(validation_accepted=False)
    assert Gate10Completeness().evaluate(bad).passed is False


def test_gate_missing_required_check_is_flagged_not_run():
    # A required check that never ran → gate fails with a :not-run problem.
    bad = _ok_subject(checks_run=set())
    finding = Gate1Architecture().evaluate(bad)
    assert finding.passed is False


# -- Application compliance (C1…C7) -----------------------------------------------


def test_compliance_all_pass_with_governing_notes():
    validation = _validated(make_interaction("t", FEATURE, kind=InteractionKind.COMMAND))
    report = evaluate_interaction_compliance(validation)
    assert report.compliant is True
    conditions = {c["id"]: c for c in report.conditions}
    assert set(conditions) == {f"C{n}" for n in range(1, 8)}
    assert all(c["status"] == "pass" for c in conditions.values())
    # C4 is the governing materially-exercised condition (interaction typedness, UAL-11)
    assert "note" in conditions["C4"]
    assert "UAL-11" in conditions["C4"]["note"]
    # C3/C5/C6 carry scoping notes
    for cid in ("C3", "C5", "C6"):
        assert "note" in conditions[cid]


def test_compliance_report_to_dict_shape():
    validation = _validated(make_interaction("t", FEATURE))
    d = evaluate_interaction_compliance(validation).to_dict()
    assert d["standard"] == "APPLICATION-001 §12"
    assert d["compliant"] is True
    assert len(d["conditions"]) == 7


def test_compliance_fails_when_a_backing_check_fails():
    # A technology-bearing interaction fails technology-independence → C7 fails.
    techy = make_interaction("t", "ENG-005:AMC-04:vue.widget")
    validation = _validated(techy)
    report = evaluate_interaction_compliance(validation)
    conditions = {c["id"]: c["status"] for c in report.conditions}
    assert conditions["C7"] == "fail"
    assert report.compliant is False


def test_certification_not_certified_for_rejected_validation():
    techy = make_interaction("t", "ENG-005:AMC-04:react.view")
    validation = _validated(techy)
    cert = certify_interaction(validation, version="1.0.0")
    assert cert.certified is False
