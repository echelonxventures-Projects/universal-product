"""EC3-B12-U01 — Application validation tests (meta-validity V1…V5 + UAL conformance)."""

from __future__ import annotations

from dataclasses import replace

import pytest

from application.application import make_application
from application.application_meta import ApplicationState
from application.application_traceability import build_traceability
from application.application_validation import (
    ApplicationValidationSubject,
    application_checks,
    validate_application,
)
from engine.validation.errors import AcceptanceGateError

CAP_REF = "ENG-005:CAPABILITY:ucos.demo.capability"
UNIT = "EC3-B12-U01"
FWD = ("f1", "f2")


def _subject(app=None):
    app = app or make_application("t", CAP_REF)
    trace = build_traceability(app, unit=UNIT, forward=FWD)
    return ApplicationValidationSubject.from_application(app, trace)


def _trace(app):
    return build_traceability(app, unit=UNIT, forward=FWD)


def test_valid_application_passes_all_checks_and_is_accepted():
    app = make_application("t", CAP_REF)
    result = validate_application(app, _trace(app))
    assert result.accepted is True
    assert result.report.verdict.value == "pass"
    assert all(f.passed for f in result.report.findings)


def test_suite_has_seventeen_blocking_checks():
    checks = application_checks()
    assert len(checks) == 17
    assert all(c.severity.name == "BLOCKING" for c in checks)
    # check ids are unique
    ids = [c.check_id for c in checks]
    assert len(ids) == len(set(ids))


def test_all_check_ids_present():
    ids = {c.check_id for c in application_checks()}
    assert ids == {
        "application-typed",
        "application-identified-objectbound",
        "application-value-fidelity",
        "application-classified",
        "application-delivers-capability",
        "meta-class-single",
        "meta-relationships-closed",
        "meta-constraints",
        "founding-acyclic",
        "lifecycle-valid",
        "foundation-reuse-integrity",
        "composition-by-reference",
        "behavior-by-reference",
        "technology-independence",
        "non-constitutive",
        "provisional-state-disclosure",
        "traceability-rooted",
    }


def _find(checks, cid):
    return next(c for c in checks if c.check_id == cid)


def test_typed_check_fails_on_empty_type():
    subj = replace(_subject(), type_tag="")
    finding = _find(application_checks(), "application-typed").evaluate(subj)
    assert finding.passed is False


def test_identified_check_fails_on_bad_prefix():
    subj = replace(_subject(), target_id="UCOS-SERVICE-xyz")
    finding = _find(application_checks(), "application-identified-objectbound").evaluate(subj)
    assert finding.passed is False


def test_identified_check_fails_on_missing_digest():
    subj = replace(_subject(), value_digest="")
    finding = _find(application_checks(), "application-identified-objectbound").evaluate(subj)
    assert finding.passed is False


def test_value_fidelity_check_fails_on_bad_digest():
    subj = replace(_subject(), value_digest="not-a-hash")
    finding = _find(application_checks(), "application-value-fidelity").evaluate(subj)
    assert finding.passed is False


def test_classified_check_fails_on_unknown_kind():
    subj = replace(_subject(), kind="Bogus-Application")
    finding = _find(application_checks(), "application-classified").evaluate(subj)
    assert finding.passed is False


def test_delivers_capability_fails_on_empty_ref():
    subj = replace(_subject(), capability_ref="  ")
    finding = _find(application_checks(), "application-delivers-capability").evaluate(subj)
    assert finding.passed is False


def test_meta_class_check_fails_on_wrong_class():
    subj = replace(_subject(), meta_class="AMC-02")
    finding = _find(application_checks(), "meta-class-single").evaluate(subj)
    assert finding.passed is False


def test_meta_relationships_check_fails_outside_closure():
    subj = replace(_subject(), relationships=("AMR-01", "AMR-99"))
    finding = _find(application_checks(), "meta-relationships-closed").evaluate(subj)
    assert finding.passed is False


def test_meta_constraints_check_fails_when_reference_unresolved():
    subj = replace(_subject(), references_resolve=False)
    finding = _find(application_checks(), "meta-constraints").evaluate(subj)
    assert finding.passed is False


def test_meta_constraints_check_fails_when_amk01_broken():
    subj = replace(_subject(), value_digest="")
    finding = _find(application_checks(), "meta-constraints").evaluate(subj)
    assert finding.passed is False


def test_founding_acyclic_check_fails_when_flag_false():
    subj = replace(_subject(), founding_acyclic=False)
    finding = _find(application_checks(), "founding-acyclic").evaluate(subj)
    assert finding.passed is False


def test_lifecycle_check_fails_on_bad_state():
    subj = replace(_subject(), lifecycle_state="BOGUS")
    finding = _find(application_checks(), "lifecycle-valid").evaluate(subj)
    assert finding.passed is False


def test_lifecycle_check_passes_for_every_valid_state():
    check = _find(application_checks(), "lifecycle-valid")
    for st in ApplicationState:
        subj = replace(_subject(), lifecycle_state=st.value)
        assert check.evaluate(subj).passed is True


def test_reuse_integrity_fails_on_redefinition():
    subj = replace(_subject(), redefines_foundation=True)
    finding = _find(application_checks(), "foundation-reuse-integrity").evaluate(subj)
    assert finding.passed is False


def test_reuse_integrity_fails_on_missing_substrate():
    subj = replace(_subject(), substrate_refs=())
    finding = _find(application_checks(), "foundation-reuse-integrity").evaluate(subj)
    assert finding.passed is False


def test_composition_by_reference_fails_on_empty():
    subj = replace(_subject(), composition_ref="")
    finding = _find(application_checks(), "composition-by-reference").evaluate(subj)
    assert finding.passed is False


def test_behavior_by_reference_fails_on_empty():
    subj = replace(_subject(), behavior_ref="")
    finding = _find(application_checks(), "behavior-by-reference").evaluate(subj)
    assert finding.passed is False


def test_technology_independence_fails_when_technology_selected():
    subj = replace(_subject(), selects_technology=True)
    finding = _find(application_checks(), "technology-independence").evaluate(subj)
    assert finding.passed is False


def test_non_constitutive_fails_on_authority():
    subj = replace(_subject(), confers_authority=True)
    finding = _find(application_checks(), "non-constitutive").evaluate(subj)
    assert finding.passed is False


def test_non_constitutive_fails_on_secret():
    subj = replace(_subject(), embeds_secret=True)
    finding = _find(application_checks(), "non-constitutive").evaluate(subj)
    assert finding.passed is False


def test_provisional_disclosure_fails_when_absent():
    subj = replace(_subject(), disclosure={})
    finding = _find(application_checks(), "provisional-state-disclosure").evaluate(subj)
    assert finding.passed is False


def test_traceability_rooted_fails_on_empty_chain():
    subj = replace(_subject(), provenance_chain=())
    finding = _find(application_checks(), "traceability-rooted").evaluate(subj)
    assert finding.passed is False


def test_traceability_rooted_fails_on_wrong_head():
    subj = replace(_subject(), provenance_chain=("WRONG", "12-APPLICATION@b7e7657"))
    finding = _find(application_checks(), "traceability-rooted").evaluate(subj)
    assert finding.passed is False


def test_traceability_rooted_fails_without_anchor():
    subj = replace(_subject(), provenance_chain=("AMC-01", "APPLICATION-005"))
    finding = _find(application_checks(), "traceability-rooted").evaluate(subj)
    assert finding.passed is False


def test_strict_validation_raises_on_bad_application(monkeypatch):
    # Build a valid app then corrupt its subject via a broken trace (empty chain)
    app = make_application("t", CAP_REF)
    trace = build_traceability(app, unit=UNIT, forward=())  # forward empty → not closed
    # forward-empty doesn't fail validation checks; instead craft a rejected report:
    # use a technology-bearing capability to force a blocking failure.
    techy = make_application("t", "ENG-005:CAPABILITY:kafka.stream")
    good_trace = build_traceability(techy, unit=UNIT, forward=FWD)
    with pytest.raises(AcceptanceGateError):
        validate_application(techy, good_trace, strict=True)
    # sanity: the empty-forward trace is not closed
    assert trace.closed is False
