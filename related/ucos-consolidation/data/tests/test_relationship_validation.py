"""EC3-B10-U10 — Relationship validation tests (V1…V5 + UDL + DRA + shared-check reuse)."""

from __future__ import annotations

from dataclasses import replace

from data.relationship_realize import build_canonical_relationship
from data.relationship_traceability import build_relationship_traceability
from data.relationship_validation import (
    RelationshipValidationSubject,
    relationship_checks,
    validate_relationship,
)
from engine.tests import assert_every_check_can_refuse
from engine.validation.contracts import Severity

UNIT = "EC3-B10-U10"


def _trace(relationship):
    return build_relationship_traceability(
        relationship, unit=UNIT, forward=(relationship.relationship_id,)
    )


def _subject(**overrides):
    relationship = build_canonical_relationship()
    subject = RelationshipValidationSubject.from_relationship(relationship, _trace(relationship))
    return replace(subject, **overrides) if overrides else subject


def _run(subject):
    return {c.check_id: c.evaluate(subject).passed for c in relationship_checks()}


# ---------------------------------------------------------------------------
# Happy path — full acceptance
# ---------------------------------------------------------------------------


def test_canonical_relationship_validation_accepted():
    relationship = build_canonical_relationship()
    result = validate_relationship(relationship, _trace(relationship))
    assert result.accepted is True
    assert result.report.verdict.value == "pass"
    assert all(f.passed for f in result.report.findings)


def test_all_checks_blocking():
    assert all(c.severity is Severity.BLOCKING for c in relationship_checks())


def test_every_check_passes_on_canonical_subject():
    results = _run(_subject())
    assert all(results.values()), [k for k, v in results.items() if not v]


def test_strict_acceptance_does_not_raise_on_valid():
    relationship = build_canonical_relationship()
    result = validate_relationship(relationship, _trace(relationship), strict=True)
    assert result.accepted is True


def test_shared_check_ids_present_for_cce_reuse():
    ids = {c.check_id for c in relationship_checks()}
    shared = {
        "meta-class-single",
        "meta-relationships-closed",
        "data-value-fidelity",
        "founding-acyclic",
        "provisional-state-disclosure",
        "traceability-rooted",
        "foundation-reuse-integrity",
    }
    assert shared <= ids


# ---------------------------------------------------------------------------
# Per-check failure branches (each blocking check has a failing input)
# ---------------------------------------------------------------------------


def test_typed_check_fails_on_empty_type():
    assert _run(_subject(type_tag=" "))["relationship-typed"] is False


def test_typed_check_fails_on_missing_kind():
    assert _run(_subject(typed=False, kind=""))["relationship-typed"] is False


def test_named_check_fails_on_empty_name():
    assert _run(_subject(name=""))["relationship-named"] is False


def test_identified_check_fails_on_bad_id():
    assert _run(_subject(target_id="BAD-ID"))["relationship-identified"] is False


def test_value_fidelity_fails_on_bad_digest():
    assert _run(_subject(value_digest="short"))["data-value-fidelity"] is False


def test_relates_endpoints_fails_on_non_certified():
    assert _run(_subject(source_id="bad"))["relationship-relates-endpoints"] is False


def test_relates_endpoints_fails_when_absorbing():
    assert _run(_subject(absorbs_endpoints=True))["relationship-relates-endpoints"] is False


def test_by_reference_fails_when_not_reference():
    assert _run(_subject(by_reference=False))["relationship-by-reference"] is False


def test_by_reference_fails_when_redefines_el1():
    assert _run(_subject(redefines_el1=True))["relationship-by-reference"] is False


def test_cardinality_check_fails_when_not_explicit():
    assert _run(_subject(cardinality_explicit=False))["relationship-cardinality-explicit"] is False


def test_directionality_check_fails_when_undeclared():
    assert (
        _run(_subject(directionality_declared=False))["relationship-directionality-declared"]
        is False
    )


def test_referential_integrity_fails_when_unresolved():
    assert _run(_subject(endpoints_resolve=False))["relationship-referential-integrity"] is False


def test_founding_acyclic_rule_fails_when_self_founding():
    assert (
        _run(_subject(founding_acyclic_rule=False))["relationship-founding-acyclic-rule"] is False
    )


def test_non_absorbing_fails_when_absorbing():
    assert _run(_subject(absorbs_endpoints=True))["relationship-non-absorbing"] is False


def test_binds_policy_fails_on_bad_ref():
    assert _run(_subject(policy_ref="nope"))["relationship-binds-policy-by-reference"] is False


def test_binds_policy_fails_when_not_by_reference():
    assert (
        _run(_subject(navigates_by_reference=False))["relationship-binds-policy-by-reference"]
        is False
    )


def test_versioned_check_fails_on_empty_version():
    assert _run(_subject(version=" "))["relationship-versioned"] is False


def test_meta_class_single_fails_on_wrong_class():
    assert _run(_subject(meta_class="DMC-99"))["meta-class-single"] is False


def test_meta_relationships_closed_fails_on_outside_relationship():
    assert _run(_subject(relationships=("DMR-99",)))["meta-relationships-closed"] is False


def test_meta_constraints_fails_when_any_unsatisfied():
    assert _run(_subject(confers_authority=True))["meta-constraints"] is False


def test_founding_acyclic_shared_fails():
    assert _run(_subject(founding_acyclic=False))["founding-acyclic"] is False


def test_valid_state_fails_on_bad_state():
    assert _run(_subject(relationship_state="BOGUS"))["relationship-valid"] is False


def test_foundation_reuse_fails_when_redefines():
    assert _run(_subject(redefines_el1=True))["foundation-reuse-integrity"] is False


def test_foundation_reuse_fails_when_no_substrate():
    assert _run(_subject(substrate_refs=()))["foundation-reuse-integrity"] is False


def test_foundation_reuse_fails_when_absorbing():
    assert _run(_subject(absorbs_endpoints=True))["foundation-reuse-integrity"] is False


def test_foundation_reuse_fails_when_not_by_reference():
    assert _run(_subject(binds_policy_by_reference=False))["foundation-reuse-integrity"] is False


def test_independence_fails_when_names_technology():
    assert _run(_subject(names_technology=True))["relationship-independence"] is False


def test_independence_fails_when_selects_technology():
    assert _run(_subject(selects_technology=True))["relationship-independence"] is False


def test_independence_fails_when_image_reference():
    assert _run(_subject(image_reference="registry/img:1"))["relationship-independence"] is False


def test_non_constitutive_fails_on_authority():
    assert _run(_subject(confers_authority=True))["non-constitutive"] is False


def test_non_constitutive_fails_on_secret():
    assert _run(_subject(embeds_secret=True))["non-constitutive"] is False


def test_non_constitutive_fails_on_technology():
    assert _run(_subject(selects_technology=True))["non-constitutive"] is False


def test_provisional_disclosure_fails_when_absent():
    assert _run(_subject(disclosure={}))["provisional-state-disclosure"] is False


def test_traceability_rooted_fails_on_empty_chain():
    assert _run(_subject(provenance_chain=()))["traceability-rooted"] is False


def test_traceability_rooted_fails_on_wrong_root():
    assert _run(_subject(provenance_chain=("DMC-99", "10-DATA@x")))["traceability-rooted"] is False


def test_traceability_rooted_fails_without_anchor():
    assert _run(_subject(provenance_chain=("DMC-04", "DATA-008")))["traceability-rooted"] is False


def test_every_check_can_refuse_something():
    """Each declared check has a reachable failure arm — see engine/tests/__init__.py."""
    assert_every_check_can_refuse(_subject(), relationship_checks())
