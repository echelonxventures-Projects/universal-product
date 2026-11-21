"""EC3-B12-U04 — Feature validation tests (meta-validity V1…V5 + UAL/FEA conformance)."""

from __future__ import annotations

from dataclasses import replace

import pytest

from application.feature import make_feature
from application.feature_meta import FeatureKind, FeatureState
from application.feature_traceability import build_traceability
from application.feature_validation import (
    FeatureValidationSubject,
    feature_checks,
    validate_feature,
)
from engine.validation.errors import AcceptanceGateError

CAP = "ENG-005:AMC-02:ucos.demo.capability"
OPS = (
    "ENG-005:SF-2:ucos.demo.operation.a",
    "ENG-005:SF-2:ucos.demo.operation.b",
)
UNIT = "EC3-B12-U04"
FWD = ("f1", "f2")


def _subject(feat=None):
    feat = feat or make_feature("t", CAP, OPS, kind=FeatureKind.COMPOSITE)
    trace = build_traceability(feat, unit=UNIT, forward=FWD)
    return FeatureValidationSubject.from_feature(feat, trace)


def _trace(feat):
    return build_traceability(feat, unit=UNIT, forward=FWD)


def test_valid_feature_passes_all_checks_and_is_accepted():
    feat = make_feature("t", CAP, OPS, kind=FeatureKind.COMPOSITE)
    result = validate_feature(feat, _trace(feat))
    assert result.accepted is True
    assert result.report.verdict.value == "pass"
    assert all(f.passed for f in result.report.findings)


def test_suite_has_twentyfour_blocking_checks():
    checks = feature_checks()
    assert len(checks) == 24
    assert all(c.severity.name == "BLOCKING" for c in checks)
    ids = [c.check_id for c in checks]
    assert len(ids) == len(set(ids))


def test_all_check_ids_present():
    ids = {c.check_id for c in feature_checks()}
    assert ids == {
        "feature-typed",
        "feature-identified-objectbound",
        "feature-value-fidelity",
        "feature-classified",
        "feature-delivers-capability",
        "feature-consumes-operation",
        "feature-operations-partition",
        "feature-presents-data",
        "feature-engaged-through-interaction",
        "feature-owned-by-module",
        "feature-declaration-complete",
        "feature-delivery-side-consistent",
        "feature-engaged-before-executable",
        "meta-class-single",
        "meta-relationships-closed",
        "meta-constraints",
        "founding-acyclic",
        "lifecycle-valid",
        "foundation-reuse-integrity",
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
    assert _find(feature_checks(), "feature-typed").evaluate(subj).passed is False


def test_identified_check_fails_on_bad_prefix():
    subj = replace(_subject(), target_id="UCOS-MODULE-xyz")
    assert (
        _find(feature_checks(), "feature-identified-objectbound").evaluate(subj).passed is False
    )


def test_identified_check_fails_on_missing_digest():
    subj = replace(_subject(), value_digest="")
    assert (
        _find(feature_checks(), "feature-identified-objectbound").evaluate(subj).passed is False
    )


def test_value_fidelity_check_fails_on_bad_digest():
    subj = replace(_subject(), value_digest="not-a-hash")
    assert _find(feature_checks(), "feature-value-fidelity").evaluate(subj).passed is False


def test_classified_check_fails_on_unknown_kind():
    subj = replace(_subject(), kind="Bogus-Feature")
    assert _find(feature_checks(), "feature-classified").evaluate(subj).passed is False


def test_delivers_capability_fails_when_absent():
    subj = replace(_subject(), delivers_capability=False, capability_ref="")
    assert _find(feature_checks(), "feature-delivers-capability").evaluate(subj).passed is False


def test_consumes_operation_fails_when_none():
    subj = replace(_subject(), consumes_operations=False, composed_operation_count=0)
    assert _find(feature_checks(), "feature-consumes-operation").evaluate(subj).passed is False


def test_consumes_operation_fails_when_count_zero_even_if_flag_true():
    subj = replace(_subject(), consumes_operations=True, composed_operation_count=0)
    assert _find(feature_checks(), "feature-consumes-operation").evaluate(subj).passed is False


def test_operations_partition_fails_when_not_partition():
    subj = replace(_subject(), operations_are_partition=False)
    assert (
        _find(feature_checks(), "feature-operations-partition").evaluate(subj).passed is False
    )


def test_presents_data_fails_when_absent():
    subj = replace(_subject(), presents_data=False, data_ref="")
    assert _find(feature_checks(), "feature-presents-data").evaluate(subj).passed is False


def test_engaged_through_interaction_fails_when_absent():
    subj = replace(_subject(), is_engaged=False, interaction_ref="")
    finding = _find(feature_checks(), "feature-engaged-through-interaction").evaluate(subj)
    assert finding.passed is False


def test_owned_by_module_fails_when_absent():
    subj = replace(_subject(), is_owned=False, module_ref="")
    assert _find(feature_checks(), "feature-owned-by-module").evaluate(subj).passed is False


def test_declaration_complete_fails_when_incomplete():
    subj = replace(_subject(), declaration_complete=False)
    assert (
        _find(feature_checks(), "feature-declaration-complete").evaluate(subj).passed is False
    )


def test_delivery_side_consistent_fails_when_inconsistent():
    subj = replace(_subject(), delivery_side_is_consistent=False)
    finding = _find(feature_checks(), "feature-delivery-side-consistent").evaluate(subj)
    assert finding.passed is False


def test_engaged_before_executable_fails_when_unengaged():
    subj = replace(_subject(), engaged_before_executable=False, lifecycle_state="EXECUTABLE")
    finding = _find(feature_checks(), "feature-engaged-before-executable").evaluate(subj)
    assert finding.passed is False


def test_meta_class_check_fails_on_wrong_class():
    subj = replace(_subject(), meta_class="AMC-03")
    assert _find(feature_checks(), "meta-class-single").evaluate(subj).passed is False


def test_meta_relationships_check_fails_outside_closure():
    subj = replace(_subject(), relationships=("AMR-05", "AMR-99"))
    assert _find(feature_checks(), "meta-relationships-closed").evaluate(subj).passed is False


def test_meta_constraints_check_fails_when_reference_unresolved():
    subj = replace(_subject(), references_resolve=False)
    assert _find(feature_checks(), "meta-constraints").evaluate(subj).passed is False


def test_meta_constraints_check_fails_when_amk01_broken():
    subj = replace(_subject(), value_digest="")
    assert _find(feature_checks(), "meta-constraints").evaluate(subj).passed is False


def test_meta_constraints_check_fails_when_declaration_incomplete():
    subj = replace(_subject(), declaration_complete=False)
    assert _find(feature_checks(), "meta-constraints").evaluate(subj).passed is False


def test_founding_acyclic_check_fails_when_flag_false():
    subj = replace(_subject(), founding_acyclic=False)
    assert _find(feature_checks(), "founding-acyclic").evaluate(subj).passed is False


def test_lifecycle_check_fails_on_bad_state():
    subj = replace(_subject(), lifecycle_state="BOGUS")
    assert _find(feature_checks(), "lifecycle-valid").evaluate(subj).passed is False


def test_lifecycle_check_passes_for_every_valid_state():
    check = _find(feature_checks(), "lifecycle-valid")
    for st in FeatureState:
        subj = replace(_subject(), lifecycle_state=st.value)
        assert check.evaluate(subj).passed is True


def test_reuse_integrity_fails_on_redefinition():
    subj = replace(_subject(), redefines_foundation=True)
    assert _find(feature_checks(), "foundation-reuse-integrity").evaluate(subj).passed is False


def test_reuse_integrity_fails_on_missing_substrate():
    subj = replace(_subject(), substrate_refs=())
    assert _find(feature_checks(), "foundation-reuse-integrity").evaluate(subj).passed is False


def test_behavior_by_reference_fails_on_empty():
    subj = replace(_subject(), behavior_ref="")
    assert _find(feature_checks(), "behavior-by-reference").evaluate(subj).passed is False


def test_technology_independence_fails_when_technology_selected():
    subj = replace(_subject(), selects_technology=True)
    assert _find(feature_checks(), "technology-independence").evaluate(subj).passed is False


def test_non_constitutive_fails_on_authority():
    subj = replace(_subject(), confers_authority=True)
    assert _find(feature_checks(), "non-constitutive").evaluate(subj).passed is False


def test_non_constitutive_fails_on_secret():
    subj = replace(_subject(), embeds_secret=True)
    assert _find(feature_checks(), "non-constitutive").evaluate(subj).passed is False


def test_provisional_disclosure_fails_when_absent():
    subj = replace(_subject(), disclosure={})
    assert (
        _find(feature_checks(), "provisional-state-disclosure").evaluate(subj).passed is False
    )


def test_traceability_rooted_fails_on_empty_chain():
    subj = replace(_subject(), provenance_chain=())
    assert _find(feature_checks(), "traceability-rooted").evaluate(subj).passed is False


def test_traceability_rooted_fails_on_wrong_head():
    subj = replace(_subject(), provenance_chain=("WRONG", "12-APPLICATION@b7e7657"))
    assert _find(feature_checks(), "traceability-rooted").evaluate(subj).passed is False


def test_traceability_rooted_fails_without_anchor():
    subj = replace(_subject(), provenance_chain=("AMC-04", "APPLICATION-008"))
    assert _find(feature_checks(), "traceability-rooted").evaluate(subj).passed is False


def test_strict_validation_raises_on_bad_feature():
    # A technology-bearing feature forces a blocking failure → strict raises.
    techy = make_feature("t", CAP, ("ENG-005:SF-2:kafka.consumer",))
    good_trace = build_traceability(techy, unit=UNIT, forward=FWD)
    with pytest.raises(AcceptanceGateError):
        validate_feature(techy, good_trace, strict=True)
    # sanity: an empty-forward trace is not closed
    empty = build_traceability(make_feature("t", CAP, OPS), unit=UNIT, forward=())
    assert empty.closed is False
