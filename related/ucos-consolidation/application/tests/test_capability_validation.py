"""EC3-B12-U02 — Capability validation tests (meta-validity V1…V5 + UAL/CAP conformance)."""

from __future__ import annotations

from dataclasses import replace

import pytest

from application.capability import make_capability
from application.capability_meta import CapabilityState
from application.capability_traceability import build_traceability
from application.capability_validation import (
    CapabilityValidationSubject,
    capability_checks,
    validate_capability,
)
from engine.validation.errors import AcceptanceGateError

OP_REF = "ENG-005:SF-2:ucos.demo.operation"
UNIT = "EC3-B12-U02"
FWD = ("f1", "f2")


def _subject(cap=None):
    cap = cap or make_capability("t", OP_REF)
    trace = build_traceability(cap, unit=UNIT, forward=FWD)
    return CapabilityValidationSubject.from_capability(cap, trace)


def _trace(cap):
    return build_traceability(cap, unit=UNIT, forward=FWD)


def test_valid_capability_passes_all_checks_and_is_accepted():
    cap = make_capability("t", OP_REF)
    result = validate_capability(cap, _trace(cap))
    assert result.accepted is True
    assert result.report.verdict.value == "pass"
    assert all(f.passed for f in result.report.findings)


def test_suite_has_nineteen_blocking_checks():
    checks = capability_checks()
    assert len(checks) == 19
    assert all(c.severity.name == "BLOCKING" for c in checks)
    ids = [c.check_id for c in checks]
    assert len(ids) == len(set(ids))


def test_all_check_ids_present():
    ids = {c.check_id for c in capability_checks()}
    assert ids == {
        "capability-typed",
        "capability-identified-objectbound",
        "capability-value-fidelity",
        "capability-classified",
        "capability-consumes-operation",
        "capability-presents-data",
        "capability-bounded",
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
    finding = _find(capability_checks(), "capability-typed").evaluate(subj)
    assert finding.passed is False


def test_identified_check_fails_on_bad_prefix():
    subj = replace(_subject(), target_id="UCOS-APPLICATION-xyz")
    finding = _find(capability_checks(), "capability-identified-objectbound").evaluate(subj)
    assert finding.passed is False


def test_identified_check_fails_on_missing_digest():
    subj = replace(_subject(), value_digest="")
    finding = _find(capability_checks(), "capability-identified-objectbound").evaluate(subj)
    assert finding.passed is False


def test_value_fidelity_check_fails_on_bad_digest():
    subj = replace(_subject(), value_digest="not-a-hash")
    finding = _find(capability_checks(), "capability-value-fidelity").evaluate(subj)
    assert finding.passed is False


def test_classified_check_fails_on_unknown_kind():
    subj = replace(_subject(), kind="Bogus-Capability")
    finding = _find(capability_checks(), "capability-classified").evaluate(subj)
    assert finding.passed is False


def test_consumes_operation_fails_on_empty_ref():
    subj = replace(_subject(), consumes_operation=False, operation_ref="  ")
    finding = _find(capability_checks(), "capability-consumes-operation").evaluate(subj)
    assert finding.passed is False


def test_consumes_operation_fails_when_ref_blank_even_if_flag_true():
    subj = replace(_subject(), consumes_operation=True, operation_ref="   ")
    finding = _find(capability_checks(), "capability-consumes-operation").evaluate(subj)
    assert finding.passed is False


def test_presents_data_fails_on_empty_ref():
    subj = replace(_subject(), data_ref="  ")
    finding = _find(capability_checks(), "capability-presents-data").evaluate(subj)
    assert finding.passed is False


def test_bounded_check_fails_when_not_bounded():
    subj = replace(_subject(), bounded=False)
    finding = _find(capability_checks(), "capability-bounded").evaluate(subj)
    assert finding.passed is False


def test_meta_class_check_fails_on_wrong_class():
    subj = replace(_subject(), meta_class="AMC-01")
    finding = _find(capability_checks(), "meta-class-single").evaluate(subj)
    assert finding.passed is False


def test_meta_relationships_check_fails_outside_closure():
    subj = replace(_subject(), relationships=("AMR-13", "AMR-99"))
    finding = _find(capability_checks(), "meta-relationships-closed").evaluate(subj)
    assert finding.passed is False


def test_meta_constraints_check_fails_when_reference_unresolved():
    subj = replace(_subject(), references_resolve=False)
    finding = _find(capability_checks(), "meta-constraints").evaluate(subj)
    assert finding.passed is False


def test_meta_constraints_check_fails_when_amk01_broken():
    subj = replace(_subject(), value_digest="")
    finding = _find(capability_checks(), "meta-constraints").evaluate(subj)
    assert finding.passed is False


def test_founding_acyclic_check_fails_when_flag_false():
    subj = replace(_subject(), founding_acyclic=False)
    finding = _find(capability_checks(), "founding-acyclic").evaluate(subj)
    assert finding.passed is False


def test_lifecycle_check_fails_on_bad_state():
    subj = replace(_subject(), lifecycle_state="BOGUS")
    finding = _find(capability_checks(), "lifecycle-valid").evaluate(subj)
    assert finding.passed is False


def test_lifecycle_check_passes_for_every_valid_state():
    check = _find(capability_checks(), "lifecycle-valid")
    for st in CapabilityState:
        subj = replace(_subject(), lifecycle_state=st.value)
        assert check.evaluate(subj).passed is True


def test_reuse_integrity_fails_on_redefinition():
    subj = replace(_subject(), redefines_foundation=True)
    finding = _find(capability_checks(), "foundation-reuse-integrity").evaluate(subj)
    assert finding.passed is False


def test_reuse_integrity_fails_on_missing_substrate():
    subj = replace(_subject(), substrate_refs=())
    finding = _find(capability_checks(), "foundation-reuse-integrity").evaluate(subj)
    assert finding.passed is False


def test_composition_by_reference_fails_on_empty():
    subj = replace(_subject(), composition_ref="")
    finding = _find(capability_checks(), "composition-by-reference").evaluate(subj)
    assert finding.passed is False


def test_behavior_by_reference_fails_on_empty():
    subj = replace(_subject(), behavior_ref="")
    finding = _find(capability_checks(), "behavior-by-reference").evaluate(subj)
    assert finding.passed is False


def test_technology_independence_fails_when_technology_selected():
    subj = replace(_subject(), selects_technology=True)
    finding = _find(capability_checks(), "technology-independence").evaluate(subj)
    assert finding.passed is False


def test_non_constitutive_fails_on_authority():
    subj = replace(_subject(), confers_authority=True)
    finding = _find(capability_checks(), "non-constitutive").evaluate(subj)
    assert finding.passed is False


def test_non_constitutive_fails_on_secret():
    subj = replace(_subject(), embeds_secret=True)
    finding = _find(capability_checks(), "non-constitutive").evaluate(subj)
    assert finding.passed is False


def test_provisional_disclosure_fails_when_absent():
    subj = replace(_subject(), disclosure={})
    finding = _find(capability_checks(), "provisional-state-disclosure").evaluate(subj)
    assert finding.passed is False


def test_traceability_rooted_fails_on_empty_chain():
    subj = replace(_subject(), provenance_chain=())
    finding = _find(capability_checks(), "traceability-rooted").evaluate(subj)
    assert finding.passed is False


def test_traceability_rooted_fails_on_wrong_head():
    subj = replace(_subject(), provenance_chain=("WRONG", "12-APPLICATION@b7e7657"))
    finding = _find(capability_checks(), "traceability-rooted").evaluate(subj)
    assert finding.passed is False


def test_traceability_rooted_fails_without_anchor():
    subj = replace(_subject(), provenance_chain=("AMC-02", "APPLICATION-006"))
    finding = _find(capability_checks(), "traceability-rooted").evaluate(subj)
    assert finding.passed is False


def test_strict_validation_raises_on_bad_capability():
    # A technology-bearing capability forces a blocking failure → strict raises.
    techy = make_capability("t", "ENG-005:SF-2:kafka.stream")
    good_trace = build_traceability(techy, unit=UNIT, forward=FWD)
    with pytest.raises(AcceptanceGateError):
        validate_capability(techy, good_trace, strict=True)
    # sanity: an empty-forward trace is not closed
    empty = build_traceability(make_capability("t", OP_REF), unit=UNIT, forward=())
    assert empty.closed is False
