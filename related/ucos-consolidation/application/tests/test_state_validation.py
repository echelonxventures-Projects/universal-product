"""EC3-B12-U07 — State validation tests (V1…V5 + UAL/STA checks; each pass + fail)."""

from __future__ import annotations

import dataclasses

import pytest

from application.state import make_state
from application.state_meta import StateKind
from application.state_traceability import build_traceability
from application.state_validation import (
    StateValidationSubject,
    state_checks,
    validate_state,
)
from engine.validation.contracts import Severity

HOLDER = "ENG-005:AMC-06:ucos.demo.interaction.a"


def _valid_subject() -> StateValidationSubject:
    s = make_state("ucos.demo.state", HOLDER, kind=StateKind.CONTEXT)
    trace = build_traceability(s, unit="EC3-B12-U07", forward=(s.state_id, "X"))
    return StateValidationSubject.from_state(s, trace)


def _find(subject, check_id):
    checks = {check.check_id: check for check in state_checks()}
    return checks[check_id].evaluate(subject)


def test_all_checks_pass_on_a_valid_state():
    subject = _valid_subject()
    for check in state_checks():
        finding = check.evaluate(subject)
        assert finding.passed, f"{check.check_id} unexpectedly failed"
        assert check.severity is Severity.BLOCKING


def test_full_validation_accepts_and_verdict_pass():
    s = make_state("ucos.demo.state", HOLDER)
    trace = build_traceability(s, unit="EC3-B12-U07", forward=(s.state_id, "X"))
    result = validate_state(s, trace)
    assert result.accepted is True
    assert result.report.verdict.value == "pass"
    assert result.report.target_id == s.state_id
    assert result.evidence is not None


def test_subject_projection_carries_meta_facts():
    subject = _valid_subject()
    assert subject.meta_class == "AMC-07"
    assert subject.blueprint_id == "AMC-07"
    assert subject.kind == "Context-State"
    assert subject.facet == "context"
    assert subject.relationships == ("AMR-06", "AMR-10", "AMR-11", "AMR-14")
    assert subject.participates_in_founding_edge is False
    assert subject.disclosure  # EC-1 provisional-state disclosure present


# -- per-check failure branches (subject mutated directly; construction is fail-closed) --


def test_typed_check_fails_on_empty_type():
    s = dataclasses.replace(_valid_subject(), type_tag="")
    assert _find(s, "state-typed").passed is False


def test_identified_check_fails_on_bad_id_and_missing_digest():
    s = dataclasses.replace(_valid_subject(), target_id="BAD-ID")
    assert _find(s, "state-identified-objectbound").passed is False
    s2 = dataclasses.replace(_valid_subject(), value_digest="")
    assert _find(s2, "state-identified-objectbound").passed is False


def test_value_fidelity_check_fails_on_bad_digest():
    s = dataclasses.replace(_valid_subject(), value_digest="xyz")
    assert _find(s, "state-value-fidelity").passed is False


def test_classified_check_fails_outside_axh07():
    s = dataclasses.replace(_valid_subject(), kind="Bogus-State")
    assert _find(s, "state-classified").passed is False
    s2 = dataclasses.replace(_valid_subject(), facet="sideways")
    assert _find(s2, "state-classified").passed is False


def test_held_check_fails():
    s = dataclasses.replace(_valid_subject(), is_held=False, holder_ref="")
    assert _find(s, "state-held-by").passed is False


def test_context_bound_check_fails_on_missing_and_on_technology():
    s = dataclasses.replace(_valid_subject(), context_ref="")
    assert _find(s, "state-context-bound").passed is False
    s2 = dataclasses.replace(_valid_subject(), context_bound=False)
    assert _find(s2, "state-context-bound").passed is False


def test_presents_data_check_fails():
    s = dataclasses.replace(_valid_subject(), presents_data=False, data_ref="")
    assert _find(s, "state-presents-data").passed is False


def test_binds_runtime_check_fails_on_missing_and_on_technology():
    s = dataclasses.replace(_valid_subject(), behavior_ref="")
    assert _find(s, "state-binds-runtime-state").passed is False
    s2 = dataclasses.replace(_valid_subject(), binds_runtime_state=False)
    assert _find(s2, "state-binds-runtime-state").passed is False


def test_lifecycle_decidable_check_fails():
    s = dataclasses.replace(_valid_subject(), lifecycle_decidable=False)
    assert _find(s, "state-lifecycle-decidable").passed is False


def test_transition_recorded_check_fails():
    s = dataclasses.replace(_valid_subject(), records_transitions=False)
    assert _find(s, "state-transition-recorded").passed is False


def test_meta_class_single_check_fails():
    s = dataclasses.replace(_valid_subject(), meta_class="AMC-06")
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
    s3 = dataclasses.replace(_valid_subject(), binds_runtime_state=False)
    assert _find(s3, "meta-constraints").passed is False


def test_founding_acyclic_check_fail_branches():
    s1 = dataclasses.replace(_valid_subject(), participates_in_founding_edge=True)
    assert _find(s1, "founding-acyclic").passed is False
    s2 = dataclasses.replace(_valid_subject(), founding_acyclic=False)
    assert _find(s2, "founding-acyclic").passed is False


def test_lifecycle_valid_check_fails():
    s = dataclasses.replace(_valid_subject(), lifecycle_state="BOGUS")
    assert _find(s, "lifecycle-valid").passed is False


def test_foundation_reuse_check_fail_branches():
    s1 = dataclasses.replace(_valid_subject(), redefines_foundation=True)
    assert _find(s1, "foundation-reuse-integrity").passed is False
    s2 = dataclasses.replace(_valid_subject(), substrate_refs=())
    assert _find(s2, "foundation-reuse-integrity").passed is False


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
    s3 = dataclasses.replace(_valid_subject(), provenance_chain=("AMC-07",))
    assert _find(s3, "traceability-rooted").passed is False  # no anchor


def test_strict_mode_raises_on_a_rejected_state():
    # A subject-level rejection cannot occur at construction; drive rejection through a
    # technology-bearing holder ref (validation detects selects_technology).
    from engine.validation.errors import AcceptanceGateError

    techy = make_state("t", "ENG-005:AMC-06:redis.session")
    trace = build_traceability(techy, unit="EC3-B12-U07", forward=(techy.state_id,))
    with pytest.raises(AcceptanceGateError):
        validate_state(techy, trace, strict=True)
