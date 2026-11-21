"""EC3-B12-U10 — Governance validation tests (V1…V5 + UAL/GOV checks; each pass + fail)."""

from __future__ import annotations

import dataclasses

import pytest

from application.governance import make_governance
from application.governance_meta import GovernanceKind
from application.governance_traceability import build_traceability
from application.governance_validation import (
    GovernanceValidationSubject,
    governance_checks,
    validate_governance,
)
from engine.validation.contracts import Severity

SUBJECTS = (
    "ENG-005:AMC-01:ucos.demo.application",
    "ENG-005:AMC-04:ucos.demo.feature",
)
SECURITY = ("ENG-005:AMC-09:ucos.demo.security.record",)
STATES = ("ENG-005:AMC-07:ucos.demo.state.lifecycle",)


def _record():
    return make_governance(
        "ucos.demo.governance",
        SUBJECTS,
        kind=GovernanceKind.CONFORMANCE,
        security_refs=SECURITY,
    )


def _valid_subject() -> GovernanceValidationSubject:
    g = _record()
    trace = build_traceability(g, unit="EC3-B12-U10", forward=(g.governance_id, "X"))
    return GovernanceValidationSubject.from_governance(g, trace)


def _find(subject, check_id):
    checks = {check.check_id: check for check in governance_checks()}
    return checks[check_id].evaluate(subject)


def test_all_checks_pass_on_a_valid_governance_record():
    subject = _valid_subject()
    for check in governance_checks():
        finding = check.evaluate(subject)
        assert finding.passed, f"{check.check_id} unexpectedly failed"
        assert check.severity is Severity.BLOCKING


def test_full_validation_accepts_and_verdict_pass():
    g = _record()
    trace = build_traceability(g, unit="EC3-B12-U10", forward=(g.governance_id, "X"))
    result = validate_governance(g, trace)
    assert result.accepted is True
    assert result.report.verdict.value == "pass"
    assert result.report.target_id == g.governance_id
    assert result.evidence is not None


def test_subject_projection_carries_meta_facts():
    subject = _valid_subject()
    assert subject.meta_class == "AMC-10"
    assert subject.blueprint_id == "AMC-10"
    assert subject.kind == "Conformance-Record"
    assert subject.facet == "conformance"
    assert subject.relationships == ("AMR-06", "AMR-08", "AMR-09", "AMR-10")
    assert subject.is_founding is False
    assert subject.founding_acyclic is True
    assert subject.evaluative_nonenforcing is True
    assert subject.disclosure  # EC-1 provisional-state disclosure present


def test_lifecycle_record_with_state_still_validates():
    life = make_governance(
        "t", SUBJECTS, kind=GovernanceKind.LIFECYCLE, state_refs=STATES
    )
    trace = build_traceability(life, unit="EC3-B12-U10", forward=(life.governance_id, "X"))
    subject = GovernanceValidationSubject.from_governance(life, trace)
    for check in governance_checks():
        assert check.evaluate(subject).passed, f"{check.check_id} failed for lifecycle record"


# -- per-check failure branches (subject mutated directly; construction is fail-closed) --


def test_typed_check_fails_on_empty_type():
    s = dataclasses.replace(_valid_subject(), type_tag="")
    assert _find(s, "governance-typed").passed is False


def test_identified_check_fails_on_bad_id_and_missing_digest():
    s = dataclasses.replace(_valid_subject(), target_id="BAD-ID")
    assert _find(s, "governance-identified-objectbound").passed is False
    s2 = dataclasses.replace(_valid_subject(), value_digest="")
    assert _find(s2, "governance-identified-objectbound").passed is False


def test_value_fidelity_check_fails_on_bad_digest():
    s = dataclasses.replace(_valid_subject(), value_digest="xyz")
    assert _find(s, "governance-value-fidelity").passed is False


def test_classified_check_fails_outside_axh10():
    s = dataclasses.replace(_valid_subject(), kind="Bogus")
    assert _find(s, "governance-classified").passed is False
    s2 = dataclasses.replace(_valid_subject(), facet="sideways")
    assert _find(s2, "governance-classified").passed is False


def test_governs_boundary_check_fails():
    s = dataclasses.replace(_valid_subject(), governs_boundary=False, subject_refs=())
    assert _find(s, "governance-governs-boundary").passed is False


def test_evaluative_nonenforcing_check_fail_branches():
    s1 = dataclasses.replace(_valid_subject(), evaluative_nonenforcing=False)
    assert _find(s1, "governance-evaluative-nonenforcing").passed is False
    s2 = dataclasses.replace(_valid_subject(), enforces=True)
    assert _find(s2, "governance-evaluative-nonenforcing").passed is False
    s3 = dataclasses.replace(_valid_subject(), ratifies=True)
    assert _find(s3, "governance-evaluative-nonenforcing").passed is False


def test_secures_by_reference_check_fails():
    s = dataclasses.replace(_valid_subject(), secures_by_reference=False)
    assert _find(s, "governance-secures-by-reference").passed is False


def test_behavior_by_reference_check_fail_branches():
    s = dataclasses.replace(_valid_subject(), behavior_ref="")
    assert _find(s, "governance-behavior-by-reference").passed is False
    s2 = dataclasses.replace(_valid_subject(), behavior_by_reference=False)
    assert _find(s2, "governance-behavior-by-reference").passed is False
    s3 = dataclasses.replace(_valid_subject(), binds_runtime_policy=False)
    assert _find(s3, "governance-behavior-by-reference").passed is False


def test_state_by_reference_check_fails():
    s = dataclasses.replace(_valid_subject(), state_by_reference=False)
    assert _find(s, "governance-state-by-reference").passed is False


def test_no_new_connection_check_fails():
    s = dataclasses.replace(_valid_subject(), uses_new_connection_construct=True)
    assert _find(s, "governance-no-new-connection").passed is False


def test_meta_class_single_check_fails():
    s = dataclasses.replace(_valid_subject(), meta_class="AMC-09")
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
    # AMK-02 branch (governs_boundary)
    s3 = dataclasses.replace(_valid_subject(), governs_boundary=False)
    assert _find(s3, "meta-constraints").passed is False
    # AMK-02 branch (precedence_decidable)
    s4 = dataclasses.replace(_valid_subject(), precedence_decidable=False)
    assert _find(s4, "meta-constraints").passed is False


def test_founding_acyclic_check_fail_branches():
    s = dataclasses.replace(_valid_subject(), founding_acyclic=False)
    assert _find(s, "founding-acyclic").passed is False
    s2 = dataclasses.replace(_valid_subject(), is_founding=True)
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
    s3 = dataclasses.replace(_valid_subject(), provenance_chain=("AMC-10",))
    assert _find(s3, "traceability-rooted").passed is False  # no anchor


def test_strict_mode_raises_on_a_rejected_governance_record():
    # A subject-level rejection cannot occur at construction; drive rejection through a
    # technology-bearing subject ref (validation detects selects_technology).
    from engine.validation.errors import AcceptanceGateError

    techy = make_governance("t", ("ENG-005:AMC-01:camunda.workflow", SUBJECTS[1]))
    trace = build_traceability(techy, unit="EC3-B12-U10", forward=(techy.governance_id,))
    with pytest.raises(AcceptanceGateError):
        validate_governance(techy, trace, strict=True)
