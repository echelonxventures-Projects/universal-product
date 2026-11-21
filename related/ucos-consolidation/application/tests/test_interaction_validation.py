"""EC3-B12-U06 — Interaction validation tests (V1…V5 + UAL/INT checks; each pass + fail)."""

from __future__ import annotations

import dataclasses

import pytest

from application.interaction import make_interaction
from application.interaction_meta import InteractionKind, InteractionState
from application.interaction_traceability import build_traceability
from application.interaction_validation import (
    InteractionValidationSubject,
    interaction_checks,
    validate_interaction,
)
from engine.validation.contracts import Severity

FEATURE = "ENG-005:AMC-04:ucos.demo.feature.a"


def _valid_subject() -> InteractionValidationSubject:
    i = make_interaction("ucos.demo.interaction", FEATURE, kind=InteractionKind.COMMAND)
    trace = build_traceability(i, unit="EC3-B12-U06", forward=(i.interaction_id, "X"))
    return InteractionValidationSubject.from_interaction(i, trace)


def _find(subject, check_id):
    checks = {check.check_id: check for check in interaction_checks()}
    return checks[check_id].evaluate(subject)


def test_all_checks_pass_on_a_valid_interaction():
    subject = _valid_subject()
    for check in interaction_checks():
        finding = check.evaluate(subject)
        assert finding.passed, f"{check.check_id} unexpectedly failed"
        assert check.severity is Severity.BLOCKING


def test_full_validation_accepts_and_verdict_pass():
    i = make_interaction("ucos.demo.interaction", FEATURE)
    trace = build_traceability(i, unit="EC3-B12-U06", forward=(i.interaction_id, "X"))
    result = validate_interaction(i, trace)
    assert result.accepted is True
    assert result.report.verdict.value == "pass"
    assert result.report.target_id == i.interaction_id
    assert result.evidence is not None


def test_subject_projection_carries_meta_facts():
    subject = _valid_subject()
    assert subject.meta_class == "AMC-06"
    assert subject.blueprint_id == "AMC-06"
    assert subject.kind == "Command-Interaction"
    assert subject.direction == "command"
    assert subject.relationships == ("AMR-05", "AMR-06", "AMR-10", "AMR-11", "AMR-14")
    assert subject.disclosure  # EC-1 provisional-state disclosure present


# -- per-check failure branches (subject mutated directly; construction is fail-closed) --


def test_typed_check_fails_on_empty_type():
    s = dataclasses.replace(_valid_subject(), type_tag="")
    assert _find(s, "interaction-typed").passed is False


def test_identified_check_fails_on_bad_id_and_missing_digest():
    s = dataclasses.replace(_valid_subject(), target_id="BAD-ID")
    assert _find(s, "interaction-identified-objectbound").passed is False
    s2 = dataclasses.replace(_valid_subject(), value_digest="")
    assert _find(s2, "interaction-identified-objectbound").passed is False


def test_value_fidelity_check_fails_on_bad_digest():
    s = dataclasses.replace(_valid_subject(), value_digest="xyz")
    assert _find(s, "interaction-value-fidelity").passed is False


def test_classified_check_fails_outside_axh06():
    s = dataclasses.replace(_valid_subject(), kind="Bogus-Interaction")
    assert _find(s, "interaction-classified").passed is False


def test_direction_decidable_check_fails():
    s = dataclasses.replace(_valid_subject(), direction_is_decidable=False)
    assert _find(s, "interaction-direction-decidable").passed is False
    s2 = dataclasses.replace(_valid_subject(), direction="sideways")
    assert _find(s2, "interaction-direction-decidable").passed is False


def test_engages_feature_check_fails():
    s = dataclasses.replace(_valid_subject(), engages_feature=False, feature_ref="")
    assert _find(s, "interaction-engages-feature").passed is False


def test_surface_abstract_check_fails_on_missing_and_on_technology():
    s = dataclasses.replace(_valid_subject(), surface_ref="")
    assert _find(s, "interaction-surface-abstract").passed is False
    s2 = dataclasses.replace(_valid_subject(), surface_is_abstract=False)
    assert _find(s2, "interaction-surface-abstract").passed is False


def test_presents_data_check_fails():
    s = dataclasses.replace(_valid_subject(), presents_data=False, data_ref="")
    assert _find(s, "interaction-presents-data").passed is False


def test_holds_state_check_fails():
    s = dataclasses.replace(_valid_subject(), holds_state=False, state_ref="")
    assert _find(s, "interaction-holds-state").passed is False


def test_sole_engagement_check_fails():
    s = dataclasses.replace(_valid_subject(), sole_engagement_point=False)
    assert _find(s, "interaction-sole-engagement").passed is False


def test_meta_class_single_check_fails():
    s = dataclasses.replace(_valid_subject(), meta_class="AMC-05")
    assert _find(s, "meta-class-single").passed is False


def test_meta_relationships_closed_check_fails():
    s = dataclasses.replace(_valid_subject(), relationships=("AMR-99",))
    assert _find(s, "meta-relationships-closed").passed is False


def test_meta_constraints_check_fail_branches():
    # AMK-01 branch
    s1 = dataclasses.replace(_valid_subject(), value_digest="")
    assert _find(s1, "meta-constraints").passed is False
    # AMK-05/07 branch
    s2 = dataclasses.replace(_valid_subject(), references_resolve=False)
    assert _find(s2, "meta-constraints").passed is False
    # AMK-02 branch
    s3 = dataclasses.replace(_valid_subject(), presents_data=False)
    assert _find(s3, "meta-constraints").passed is False


def test_founding_acyclic_check_fails():
    s = dataclasses.replace(_valid_subject(), founding_acyclic=False)
    assert _find(s, "founding-acyclic").passed is False


def test_lifecycle_valid_check_fails():
    s = dataclasses.replace(_valid_subject(), lifecycle_state="BOGUS")
    assert _find(s, "lifecycle-valid").passed is False


def test_foundation_reuse_check_fail_branches():
    s1 = dataclasses.replace(_valid_subject(), redefines_foundation=True)
    assert _find(s1, "foundation-reuse-integrity").passed is False
    s2 = dataclasses.replace(_valid_subject(), substrate_refs=())
    assert _find(s2, "foundation-reuse-integrity").passed is False


def test_behavior_by_reference_check_fails():
    s = dataclasses.replace(_valid_subject(), behavior_ref="")
    assert _find(s, "behavior-by-reference").passed is False


def test_technology_independence_check_fails():
    s = dataclasses.replace(_valid_subject(), selects_technology=True)
    assert _find(s, "technology-independence").passed is False


def test_non_constitutive_check_fail_branches():
    s1 = dataclasses.replace(_valid_subject(), confers_authority=True)
    assert _find(s1, "non-constitutive").passed is False
    s2 = dataclasses.replace(_valid_subject(), embeds_secret=True)
    assert _find(s2, "non-constitutive").passed is False


def test_provisional_disclosure_check_fails_on_empty_disclosure():
    s = dataclasses.replace(_valid_subject(), disclosure={})
    assert _find(s, "provisional-state-disclosure").passed is False


def test_traceability_rooted_check_fail_branches():
    s1 = dataclasses.replace(_valid_subject(), provenance_chain=())
    assert _find(s1, "traceability-rooted").passed is False
    s2 = dataclasses.replace(_valid_subject(), provenance_chain=("WRONG-ROOT",))
    assert _find(s2, "traceability-rooted").passed is False
    s3 = dataclasses.replace(_valid_subject(), provenance_chain=("AMC-06",))
    assert _find(s3, "traceability-rooted").passed is False  # no anchor


def test_strict_mode_raises_on_a_rejected_interaction():
    # A subject-level rejection cannot occur at construction; drive rejection through a
    # technology-bearing feature ref (validation detects selects_technology).
    from engine.validation.errors import AcceptanceGateError

    techy = make_interaction("t", "ENG-005:AMC-04:react.view")
    trace = build_traceability(techy, unit="EC3-B12-U06", forward=(techy.interaction_id,))
    with pytest.raises(AcceptanceGateError):
        validate_interaction(techy, trace, strict=True)
