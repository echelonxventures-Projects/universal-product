"""EC3-B12-U09 — Security validation tests (V1…V5 + UAL/SEC checks; each pass + fail)."""

from __future__ import annotations

import dataclasses

import pytest

from application.security import make_security
from application.security_meta import SecurityKind
from application.security_traceability import build_traceability
from application.security_validation import (
    SecurityValidationSubject,
    security_checks,
    validate_security,
)
from engine.validation.contracts import Severity

SUBJECTS = (
    "ENG-005:AMC-01:ucos.demo.application",
    "ENG-005:AMC-04:ucos.demo.feature",
)
GOVERNANCE = ("ENG-005:AMC-10:ucos.demo.governance.policy",)
DATA = ("ENG-005:DF-2:DATA-014.confidentiality.datum",)


def _record():
    return make_security(
        "ucos.demo.security",
        SUBJECTS,
        kind=SecurityKind.CONFIDENTIALITY,
        governance_refs=GOVERNANCE,
        data_refs=DATA,
    )


def _valid_subject() -> SecurityValidationSubject:
    s = _record()
    trace = build_traceability(s, unit="EC3-B12-U09", forward=(s.security_id, "X"))
    return SecurityValidationSubject.from_security(s, trace)


def _find(subject, check_id):
    checks = {check.check_id: check for check in security_checks()}
    return checks[check_id].evaluate(subject)


def test_all_checks_pass_on_a_valid_security_record():
    subject = _valid_subject()
    for check in security_checks():
        finding = check.evaluate(subject)
        assert finding.passed, f"{check.check_id} unexpectedly failed"
        assert check.severity is Severity.BLOCKING


def test_full_validation_accepts_and_verdict_pass():
    s = _record()
    trace = build_traceability(s, unit="EC3-B12-U09", forward=(s.security_id, "X"))
    result = validate_security(s, trace)
    assert result.accepted is True
    assert result.report.verdict.value == "pass"
    assert result.report.target_id == s.security_id
    assert result.evidence is not None


def test_subject_projection_carries_meta_facts():
    subject = _valid_subject()
    assert subject.meta_class == "AMC-09"
    assert subject.blueprint_id == "AMC-09"
    assert subject.kind == "Confidentiality-Record"
    assert subject.facet == "confidentiality"
    assert subject.relationships == ("AMR-08", "AMR-09", "AMR-10", "AMR-14")
    assert subject.is_founding is False
    assert subject.founding_acyclic is True
    assert subject.evaluative_nonenforcing is True
    assert subject.disclosure  # EC-1 provisional-state disclosure present


def test_authorization_record_without_data_still_validates():
    authz = make_security("t", SUBJECTS, kind=SecurityKind.AUTHORIZATION)
    trace = build_traceability(authz, unit="EC3-B12-U09", forward=(authz.security_id, "X"))
    subject = SecurityValidationSubject.from_security(authz, trace)
    for check in security_checks():
        assert check.evaluate(subject).passed, f"{check.check_id} failed for authz record"


# -- per-check failure branches (subject mutated directly; construction is fail-closed) --


def test_typed_check_fails_on_empty_type():
    s = dataclasses.replace(_valid_subject(), type_tag="")
    assert _find(s, "security-typed").passed is False


def test_identified_check_fails_on_bad_id_and_missing_digest():
    s = dataclasses.replace(_valid_subject(), target_id="BAD-ID")
    assert _find(s, "security-identified-objectbound").passed is False
    s2 = dataclasses.replace(_valid_subject(), value_digest="")
    assert _find(s2, "security-identified-objectbound").passed is False


def test_value_fidelity_check_fails_on_bad_digest():
    s = dataclasses.replace(_valid_subject(), value_digest="xyz")
    assert _find(s, "security-value-fidelity").passed is False


def test_classified_check_fails_outside_axh09():
    s = dataclasses.replace(_valid_subject(), kind="Bogus")
    assert _find(s, "security-classified").passed is False
    s2 = dataclasses.replace(_valid_subject(), facet="sideways")
    assert _find(s2, "security-classified").passed is False


def test_classifies_boundary_check_fails():
    s = dataclasses.replace(_valid_subject(), classifies_boundary=False, subject_refs=())
    assert _find(s, "security-classifies-boundary").passed is False


def test_evaluative_nonenforcing_check_fail_branches():
    s1 = dataclasses.replace(_valid_subject(), evaluative_nonenforcing=False)
    assert _find(s1, "security-evaluative-nonenforcing").passed is False
    s2 = dataclasses.replace(_valid_subject(), grants_access=True)
    assert _find(s2, "security-evaluative-nonenforcing").passed is False


def test_governance_by_reference_check_fails():
    s = dataclasses.replace(_valid_subject(), governed_by_reference=False)
    assert _find(s, "security-governance-by-reference").passed is False


def test_behavior_by_reference_check_fail_branches():
    s = dataclasses.replace(_valid_subject(), behavior_ref="")
    assert _find(s, "security-behavior-by-reference").passed is False
    s2 = dataclasses.replace(_valid_subject(), behavior_by_reference=False)
    assert _find(s2, "security-behavior-by-reference").passed is False
    s3 = dataclasses.replace(_valid_subject(), binds_runtime_policy=False)
    assert _find(s3, "security-behavior-by-reference").passed is False


def test_data_by_reference_check_fail_branches():
    s = dataclasses.replace(_valid_subject(), data_by_reference=False)
    assert _find(s, "security-data-by-reference").passed is False
    s2 = dataclasses.replace(_valid_subject(), data_security_reuse=False)
    assert _find(s2, "security-data-by-reference").passed is False


def test_no_new_connection_check_fails():
    s = dataclasses.replace(_valid_subject(), uses_new_connection_construct=True)
    assert _find(s, "security-no-new-connection").passed is False


def test_meta_class_single_check_fails():
    s = dataclasses.replace(_valid_subject(), meta_class="AMC-08")
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
    # AMK-02 branch (classifies_boundary)
    s3 = dataclasses.replace(_valid_subject(), classifies_boundary=False)
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
    s3 = dataclasses.replace(_valid_subject(), provenance_chain=("AMC-09",))
    assert _find(s3, "traceability-rooted").passed is False  # no anchor


def test_strict_mode_raises_on_a_rejected_security_record():
    # A subject-level rejection cannot occur at construction; drive rejection through a
    # technology-bearing subject ref (validation detects selects_technology).
    from engine.validation.errors import AcceptanceGateError

    techy = make_security("t", ("ENG-005:AMC-01:oauth.provider", SUBJECTS[1]))
    trace = build_traceability(techy, unit="EC3-B12-U09", forward=(techy.security_id,))
    with pytest.raises(AcceptanceGateError):
        validate_security(techy, trace, strict=True)
