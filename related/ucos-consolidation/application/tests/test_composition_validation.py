"""EC3-B12-U08 — Composition validation tests (V1…V5 + UAL/CMP checks; each pass + fail)."""

from __future__ import annotations

import dataclasses

import pytest

from application.composition import make_composition
from application.composition_meta import CompositionKind
from application.composition_traceability import build_traceability
from application.composition_validation import (
    CompositionValidationSubject,
    composition_checks,
    validate_composition,
)
from engine.validation.contracts import Severity

MEMBERS = (
    "ENG-005:AMC-03:ucos.demo.module.a",
    "ENG-005:AMC-03:ucos.demo.module.b",
)
ASSEMBLED = "ENG-005:AMC-01:ucos.demo.application"


def _valid_subject() -> CompositionValidationSubject:
    c = make_composition("ucos.demo.composition", MEMBERS, assembled_ref=ASSEMBLED)
    trace = build_traceability(c, unit="EC3-B12-U08", forward=(c.composition_id, "X"))
    return CompositionValidationSubject.from_composition(c, trace)


def _find(subject, check_id):
    checks = {check.check_id: check for check in composition_checks()}
    return checks[check_id].evaluate(subject)


def test_all_checks_pass_on_a_valid_composition():
    subject = _valid_subject()
    for check in composition_checks():
        finding = check.evaluate(subject)
        assert finding.passed, f"{check.check_id} unexpectedly failed"
        assert check.severity is Severity.BLOCKING


def test_full_validation_accepts_and_verdict_pass():
    c = make_composition("ucos.demo.composition", MEMBERS, assembled_ref=ASSEMBLED)
    trace = build_traceability(c, unit="EC3-B12-U08", forward=(c.composition_id, "X"))
    result = validate_composition(c, trace)
    assert result.accepted is True
    assert result.report.verdict.value == "pass"
    assert result.report.target_id == c.composition_id
    assert result.evidence is not None


def test_subject_projection_carries_meta_facts():
    subject = _valid_subject()
    assert subject.meta_class == "AMC-08"
    assert subject.blueprint_id == "AMC-08"
    assert subject.kind == "Module-into-Application"
    assert subject.facet == "module-into-application"
    assert subject.relationships == ("AMR-02", "AMR-03", "AMR-07", "AMR-10", "AMR-12")
    assert subject.is_founding is True
    assert subject.founding_acyclic is True
    assert subject.disclosure  # EC-1 provisional-state disclosure present


def test_federation_subject_projection():
    peers = (
        "ENG-005:AMC-01:ucos.demo.app.alpha",
        "ENG-005:AMC-01:ucos.demo.app.beta",
    )
    fed = make_composition("t", peers, kind=CompositionKind.APPLICATION_FEDERATION,
                           assembled_ref="ENG-005:AMC-01:ucos.demo.federation")
    trace = build_traceability(fed, unit="EC3-B12-U08", forward=(fed.composition_id, "X"))
    subject = CompositionValidationSubject.from_composition(fed, trace)
    assert subject.is_federation is True
    assert subject.is_founding is False
    for check in composition_checks():
        assert check.evaluate(subject).passed, f"{check.check_id} failed for federation"


# -- per-check failure branches (subject mutated directly; construction is fail-closed) --


def test_typed_check_fails_on_empty_type():
    s = dataclasses.replace(_valid_subject(), type_tag="")
    assert _find(s, "composition-typed").passed is False


def test_identified_check_fails_on_bad_id_and_missing_digest():
    s = dataclasses.replace(_valid_subject(), target_id="BAD-ID")
    assert _find(s, "composition-identified-objectbound").passed is False
    s2 = dataclasses.replace(_valid_subject(), value_digest="")
    assert _find(s2, "composition-identified-objectbound").passed is False


def test_value_fidelity_check_fails_on_bad_digest():
    s = dataclasses.replace(_valid_subject(), value_digest="xyz")
    assert _find(s, "composition-value-fidelity").passed is False


def test_classified_check_fails_outside_axh08():
    s = dataclasses.replace(_valid_subject(), kind="Bogus")
    assert _find(s, "composition-classified").passed is False
    s2 = dataclasses.replace(_valid_subject(), facet="sideways")
    assert _find(s2, "composition-classified").passed is False


def test_assembles_members_check_fails():
    s = dataclasses.replace(_valid_subject(), assembles_members=False, assembled_member_count=0)
    assert _find(s, "composition-assembles-members").passed is False


def test_constituents_typed_check_fails():
    s = dataclasses.replace(_valid_subject(), members_are_partition=False)
    assert _find(s, "composition-constituents-typed").passed is False


def test_preserves_boundaries_check_fails():
    s = dataclasses.replace(_valid_subject(), preserves_boundaries=False)
    assert _find(s, "composition-preserves-boundaries").passed is False


def test_federation_by_reference_check_fails():
    s = dataclasses.replace(_valid_subject(), federation_is_by_reference=False)
    assert _find(s, "composition-federation-by-reference").passed is False


def test_no_new_connection_check_fails():
    s = dataclasses.replace(_valid_subject(), uses_new_connection_construct=True)
    assert _find(s, "composition-no-new-connection").passed is False


def test_composition_by_reference_check_fail_branches():
    s = dataclasses.replace(_valid_subject(), assembled_ref="")
    assert _find(s, "composition-by-reference").passed is False
    s2 = dataclasses.replace(_valid_subject(), binds_platform_composition=False)
    assert _find(s2, "composition-by-reference").passed is False


def test_behavior_by_reference_check_fail_branches():
    s = dataclasses.replace(_valid_subject(), behavior_ref="")
    assert _find(s, "composition-behavior-by-reference").passed is False
    s2 = dataclasses.replace(_valid_subject(), binds_runtime_event=False)
    assert _find(s2, "composition-behavior-by-reference").passed is False


def test_meta_class_single_check_fails():
    s = dataclasses.replace(_valid_subject(), meta_class="AMC-03")
    assert _find(s, "meta-class-single").passed is False


def test_meta_relationships_closed_check_fails():
    s = dataclasses.replace(_valid_subject(), relationships=("AMR-99",))
    assert _find(s, "meta-relationships-closed").passed is False


def test_meta_constraints_check_fail_branches():
    # AMK-01 branch
    s1 = dataclasses.replace(_valid_subject(), value_digest="")
    assert _find(s1, "meta-constraints").passed is False
    # AMK-05/06 branch
    s2 = dataclasses.replace(_valid_subject(), references_resolve=False)
    assert _find(s2, "meta-constraints").passed is False
    # AMK-02 branch
    s3 = dataclasses.replace(_valid_subject(), members_are_partition=False)
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
    s3 = dataclasses.replace(_valid_subject(), provenance_chain=("AMC-08",))
    assert _find(s3, "traceability-rooted").passed is False  # no anchor


def test_strict_mode_raises_on_a_rejected_composition():
    # A subject-level rejection cannot occur at construction; drive rejection through a
    # technology-bearing member ref (validation detects selects_technology).
    from engine.validation.errors import AcceptanceGateError

    techy = make_composition("t", ("ENG-005:AMC-03:webpack.bundle", MEMBERS[1]),
                             assembled_ref=ASSEMBLED)
    trace = build_traceability(techy, unit="EC3-B12-U08", forward=(techy.composition_id,))
    with pytest.raises(AcceptanceGateError):
        validate_composition(techy, trace, strict=True)
