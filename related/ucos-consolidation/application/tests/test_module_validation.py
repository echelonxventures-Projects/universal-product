"""EC3-B12-U03 — Module validation tests (meta-validity V1…V5 + UAL/MOD conformance)."""

from __future__ import annotations

from dataclasses import replace

import pytest

from application.module import make_module
from application.module_meta import ModuleState
from application.module_traceability import build_traceability
from application.module_validation import (
    ModuleValidationSubject,
    module_checks,
    validate_module,
)
from engine.validation.errors import AcceptanceGateError

FEATS = (
    "ENG-005:AMC-04:ucos.demo.feature.a",
    "ENG-005:AMC-04:ucos.demo.feature.b",
)
UNIT = "EC3-B12-U03"
FWD = ("f1", "f2")


def _subject(mod=None):
    mod = mod or make_module("t", FEATS)
    trace = build_traceability(mod, unit=UNIT, forward=FWD)
    return ModuleValidationSubject.from_module(mod, trace)


def _trace(mod):
    return build_traceability(mod, unit=UNIT, forward=FWD)


def test_valid_module_passes_all_checks_and_is_accepted():
    mod = make_module("t", FEATS)
    result = validate_module(mod, _trace(mod))
    assert result.accepted is True
    assert result.report.verdict.value == "pass"
    assert all(f.passed for f in result.report.findings)


def test_suite_has_twenty_blocking_checks():
    checks = module_checks()
    assert len(checks) == 20
    assert all(c.severity.name == "BLOCKING" for c in checks)
    ids = [c.check_id for c in checks]
    assert len(ids) == len(set(ids))


def test_all_check_ids_present():
    ids = {c.check_id for c in module_checks()}
    assert ids == {
        "module-typed",
        "module-identified-objectbound",
        "module-value-fidelity",
        "module-classified",
        "module-groups-features",
        "module-ownership-partition",
        "module-bounded",
        "module-cohesive",
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
    finding = _find(module_checks(), "module-typed").evaluate(subj)
    assert finding.passed is False


def test_identified_check_fails_on_bad_prefix():
    subj = replace(_subject(), target_id="UCOS-CAPABILITY-xyz")
    finding = _find(module_checks(), "module-identified-objectbound").evaluate(subj)
    assert finding.passed is False


def test_identified_check_fails_on_missing_digest():
    subj = replace(_subject(), value_digest="")
    finding = _find(module_checks(), "module-identified-objectbound").evaluate(subj)
    assert finding.passed is False


def test_value_fidelity_check_fails_on_bad_digest():
    subj = replace(_subject(), value_digest="not-a-hash")
    finding = _find(module_checks(), "module-value-fidelity").evaluate(subj)
    assert finding.passed is False


def test_classified_check_fails_on_unknown_kind():
    subj = replace(_subject(), kind="Bogus-Module")
    finding = _find(module_checks(), "module-classified").evaluate(subj)
    assert finding.passed is False


def test_groups_features_fails_when_no_feature():
    subj = replace(_subject(), groups_features=False, owned_feature_count=0)
    finding = _find(module_checks(), "module-groups-features").evaluate(subj)
    assert finding.passed is False


def test_groups_features_fails_when_count_zero_even_if_flag_true():
    subj = replace(_subject(), groups_features=True, owned_feature_count=0)
    finding = _find(module_checks(), "module-groups-features").evaluate(subj)
    assert finding.passed is False


def test_ownership_partition_fails_when_not_partition():
    subj = replace(_subject(), ownership_is_partition=False)
    finding = _find(module_checks(), "module-ownership-partition").evaluate(subj)
    assert finding.passed is False


def test_bounded_check_fails_when_not_bounded():
    subj = replace(_subject(), bounded=False)
    finding = _find(module_checks(), "module-bounded").evaluate(subj)
    assert finding.passed is False


def test_cohesive_check_fails_when_not_cohesive():
    subj = replace(_subject(), cohesive=False)
    finding = _find(module_checks(), "module-cohesive").evaluate(subj)
    assert finding.passed is False


def test_meta_class_check_fails_on_wrong_class():
    subj = replace(_subject(), meta_class="AMC-01")
    finding = _find(module_checks(), "meta-class-single").evaluate(subj)
    assert finding.passed is False


def test_meta_relationships_check_fails_outside_closure():
    subj = replace(_subject(), relationships=("AMR-03", "AMR-99"))
    finding = _find(module_checks(), "meta-relationships-closed").evaluate(subj)
    assert finding.passed is False


def test_meta_constraints_check_fails_when_reference_unresolved():
    subj = replace(_subject(), references_resolve=False)
    finding = _find(module_checks(), "meta-constraints").evaluate(subj)
    assert finding.passed is False


def test_meta_constraints_check_fails_when_amk01_broken():
    subj = replace(_subject(), value_digest="")
    finding = _find(module_checks(), "meta-constraints").evaluate(subj)
    assert finding.passed is False


def test_founding_acyclic_check_fails_when_flag_false():
    subj = replace(_subject(), founding_acyclic=False)
    finding = _find(module_checks(), "founding-acyclic").evaluate(subj)
    assert finding.passed is False


def test_lifecycle_check_fails_on_bad_state():
    subj = replace(_subject(), lifecycle_state="BOGUS")
    finding = _find(module_checks(), "lifecycle-valid").evaluate(subj)
    assert finding.passed is False


def test_lifecycle_check_passes_for_every_valid_state():
    check = _find(module_checks(), "lifecycle-valid")
    for st in ModuleState:
        subj = replace(_subject(), lifecycle_state=st.value)
        assert check.evaluate(subj).passed is True


def test_reuse_integrity_fails_on_redefinition():
    subj = replace(_subject(), redefines_foundation=True)
    finding = _find(module_checks(), "foundation-reuse-integrity").evaluate(subj)
    assert finding.passed is False


def test_reuse_integrity_fails_on_missing_substrate():
    subj = replace(_subject(), substrate_refs=())
    finding = _find(module_checks(), "foundation-reuse-integrity").evaluate(subj)
    assert finding.passed is False


def test_composition_by_reference_fails_on_empty_application():
    subj = replace(_subject(), application_ref="")
    finding = _find(module_checks(), "composition-by-reference").evaluate(subj)
    assert finding.passed is False


def test_composition_by_reference_fails_on_empty_composition():
    subj = replace(_subject(), composition_ref="")
    finding = _find(module_checks(), "composition-by-reference").evaluate(subj)
    assert finding.passed is False


def test_behavior_by_reference_fails_on_empty():
    subj = replace(_subject(), behavior_ref="")
    finding = _find(module_checks(), "behavior-by-reference").evaluate(subj)
    assert finding.passed is False


def test_technology_independence_fails_when_technology_selected():
    subj = replace(_subject(), selects_technology=True)
    finding = _find(module_checks(), "technology-independence").evaluate(subj)
    assert finding.passed is False


def test_non_constitutive_fails_on_authority():
    subj = replace(_subject(), confers_authority=True)
    finding = _find(module_checks(), "non-constitutive").evaluate(subj)
    assert finding.passed is False


def test_non_constitutive_fails_on_secret():
    subj = replace(_subject(), embeds_secret=True)
    finding = _find(module_checks(), "non-constitutive").evaluate(subj)
    assert finding.passed is False


def test_provisional_disclosure_fails_when_absent():
    subj = replace(_subject(), disclosure={})
    finding = _find(module_checks(), "provisional-state-disclosure").evaluate(subj)
    assert finding.passed is False


def test_traceability_rooted_fails_on_empty_chain():
    subj = replace(_subject(), provenance_chain=())
    finding = _find(module_checks(), "traceability-rooted").evaluate(subj)
    assert finding.passed is False


def test_traceability_rooted_fails_on_wrong_head():
    subj = replace(_subject(), provenance_chain=("WRONG", "12-APPLICATION@b7e7657"))
    finding = _find(module_checks(), "traceability-rooted").evaluate(subj)
    assert finding.passed is False


def test_traceability_rooted_fails_without_anchor():
    subj = replace(_subject(), provenance_chain=("AMC-03", "APPLICATION-007"))
    finding = _find(module_checks(), "traceability-rooted").evaluate(subj)
    assert finding.passed is False


def test_strict_validation_raises_on_bad_module():
    # A technology-bearing module forces a blocking failure → strict raises.
    techy = make_module("t", ("ENG-005:AMC-04:kafka.consumer",))
    good_trace = build_traceability(techy, unit=UNIT, forward=FWD)
    with pytest.raises(AcceptanceGateError):
        validate_module(techy, good_trace, strict=True)
    # sanity: an empty-forward trace is not closed
    empty = build_traceability(make_module("t", FEATS), unit=UNIT, forward=())
    assert empty.closed is False
