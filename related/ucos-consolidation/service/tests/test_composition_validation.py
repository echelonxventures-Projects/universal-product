"""EC3-B11-U06 — Composition validation tests (meta-validity V1…V5 + USL + SCO)."""

from __future__ import annotations

from dataclasses import replace

from service.composition import make_composition
from service.composition_meta import CompositionKind
from service.composition_traceability import build_composition_traceability
from service.composition_validation import (
    CompositionClassifiedCheck,
    CompositionComposesMembersCheck,
    CompositionContractBoundCheck,
    CompositionDataByReferenceCheck,
    CompositionIdentifiedCheck,
    CompositionInvocationByReferenceCheck,
    CompositionPlatformReuseCheck,
    CompositionTopologyValidCheck,
    CompositionTypedCheck,
    CompositionValidationSubject,
    CompositionValueFidelityCheck,
    FoundationReuseIntegrityCheck,
    FoundingAcyclicCheck,
    LifecycleValidCheck,
    MetaClassSingleCheck,
    MetaConstraintsCheck,
    MetaRelationshipsClosedCheck,
    NonConstitutiveCheck,
    ProvisionalDisclosureCheck,
    TechnologyIndependenceCheck,
    TraceabilityRootedCheck,
    composition_checks,
    validate_composition,
)

_MEMBERS = ("ENG-005:SOE-05:op.a", "ENG-005:SOE-05:op.b")
_CON = "ENG-005:SOE-03:contract"


def _c(**kw):
    base = dict(kind=CompositionKind.AGGREGATION, data_refs=("ENG-005:DF-2:composite",))
    base.update(kw)
    type_tag = base.pop("type_tag", "t")
    members = base.pop("member_refs", _MEMBERS)
    return make_composition(type_tag, members, _CON, **base)


def _subject(**overrides) -> CompositionValidationSubject:
    c = _c()
    trace = build_composition_traceability(c, unit="EC3-B11-U06", forward=(c.composition_id,))
    base = CompositionValidationSubject.from_composition(c, trace)
    return replace(base, **overrides) if overrides else base


def test_validate_composition_accepts_a_wellformed_composition():
    c = _c()
    trace = build_composition_traceability(c, unit="EC3-B11-U06", forward=(c.composition_id,))
    validation = validate_composition(c, trace)
    assert validation.accepted is True
    assert not validation.report.blocking_failures


def test_suite_has_twenty_checks_and_shared_gate_ids():
    ids = {c.check_id for c in composition_checks()}
    assert len(composition_checks()) == 20
    assert {
        "traceability-rooted",
        "meta-class-single",
        "foundation-reuse-integrity",
        "service-value-fidelity",
        "founding-acyclic",
        "meta-relationships-closed",
        "provisional-state-disclosure",
    } <= ids


def test_typed_check_fails_on_blank_type():
    assert CompositionTypedCheck().evaluate(_subject(type_tag=" ")).passed is False


def test_identified_check_fails_on_bad_prefix():
    assert CompositionIdentifiedCheck().evaluate(_subject(target_id="X")).passed is False


def test_identified_check_fails_on_missing_digest():
    assert CompositionIdentifiedCheck().evaluate(_subject(value_digest="")).passed is False


def test_value_fidelity_check_fails_on_bad_digest():
    assert CompositionValueFidelityCheck().evaluate(_subject(value_digest="zz")).passed is False


def test_classified_check_fails_outside_sxh06():
    assert CompositionClassifiedCheck().evaluate(_subject(kind="Bogus")).passed is False


def test_composes_members_check_fails_without_members():
    assert CompositionComposesMembersCheck().evaluate(_subject(composes_members=False)).passed is False


def test_topology_valid_check_fails_when_invalid():
    assert CompositionTopologyValidCheck().evaluate(_subject(topology_valid=False)).passed is False


def test_contract_bound_check_fails_without_contract():
    assert CompositionContractBoundCheck().evaluate(_subject(contract_bound=False)).passed is False


def test_platform_reuse_check_fails_without_reuse():
    assert CompositionPlatformReuseCheck().evaluate(_subject(platform_reuse=False)).passed is False


def test_data_by_reference_check_fails_when_not_data():
    assert CompositionDataByReferenceCheck().evaluate(_subject(data_by_reference=False)).passed is False


def test_invocation_by_reference_check_fails_when_absent():
    assert CompositionInvocationByReferenceCheck().evaluate(_subject(invocation_by_reference=False)).passed is False


def test_meta_class_single_check_fails_on_wrong_class():
    assert MetaClassSingleCheck().evaluate(_subject(meta_class="SMC-01")).passed is False


def test_meta_relationships_closed_check_fails_on_out_of_range():
    assert MetaRelationshipsClosedCheck().evaluate(_subject(relationships=("SMR-99",))).passed is False


def test_meta_constraints_check_fails_on_smk01():
    assert MetaConstraintsCheck().evaluate(_subject(type_tag="")).passed is False


def test_meta_constraints_check_fails_on_smk02():
    assert MetaConstraintsCheck().evaluate(_subject(contract_bound=False)).passed is False


def test_meta_constraints_check_fails_on_smk05_06_07():
    assert MetaConstraintsCheck().evaluate(_subject(references_resolve=False)).passed is False


def test_founding_acyclic_check_fails_when_cyclic():
    assert FoundingAcyclicCheck().evaluate(_subject(founding_acyclic=False)).passed is False


def test_lifecycle_valid_check_fails_on_bad_state():
    assert LifecycleValidCheck().evaluate(_subject(lifecycle_state="LIVE")).passed is False


def test_foundation_reuse_check_fails_on_redefinition():
    assert FoundationReuseIntegrityCheck().evaluate(_subject(redefines_foundation=True)).passed is False


def test_foundation_reuse_check_fails_on_missing_substrate():
    assert FoundationReuseIntegrityCheck().evaluate(_subject(substrate_refs=())).passed is False


def test_technology_independence_check_fails_when_technology_selected():
    assert TechnologyIndependenceCheck().evaluate(_subject(selects_technology=True)).passed is False


def test_non_constitutive_check_fails_on_authority():
    assert NonConstitutiveCheck().evaluate(_subject(confers_authority=True)).passed is False


def test_non_constitutive_check_fails_on_secret():
    assert NonConstitutiveCheck().evaluate(_subject(embeds_secret=True)).passed is False


def test_provisional_disclosure_check_fails_when_absent():
    assert ProvisionalDisclosureCheck().evaluate(_subject(disclosure={})).passed is False


def test_traceability_rooted_check_fails_on_empty_chain():
    assert TraceabilityRootedCheck().evaluate(_subject(provenance_chain=())).passed is False


def test_traceability_rooted_check_fails_on_wrong_root():
    assert TraceabilityRootedCheck().evaluate(
        _subject(provenance_chain=("SMC-01", "11-SERVICE@b7e7657"))
    ).passed is False


def test_traceability_rooted_check_fails_without_anchor():
    assert TraceabilityRootedCheck().evaluate(
        _subject(provenance_chain=("SMC-06", "SERVICE-001"))
    ).passed is False


def test_all_checks_pass_on_a_good_subject():
    s = _subject()
    for check in composition_checks():
        assert check.evaluate(s).passed is True, check.check_id


def test_technology_selecting_composition_is_rejected_end_to_end():
    c = _c(member_refs=("ENG-005:SOE-01:kafka.peer", "ENG-005:SOE-01:s2"), kind=CompositionKind.FEDERATION)
    trace = build_composition_traceability(c, unit="EC3-B11-U06", forward=(c.composition_id,))
    assert validate_composition(c, trace).accepted is False


def test_federation_and_delegation_validate_end_to_end():
    fed = _c(kind=CompositionKind.FEDERATION, member_refs=("ENG-005:SOE-01:s1", "ENG-005:SOE-01:s2"))
    dele = _c(kind=CompositionKind.DELEGATION, member_refs=("ENG-005:SOE-05:target",))
    for c in (fed, dele):
        trace = build_composition_traceability(c, unit="EC3-B11-U06", forward=(c.composition_id,))
        assert validate_composition(c, trace).accepted is True


def test_bad_topology_is_rejected_end_to_end():
    c = _c(kind=CompositionKind.DELEGATION, member_refs=_MEMBERS)
    trace = build_composition_traceability(c, unit="EC3-B11-U06", forward=(c.composition_id,))
    assert validate_composition(c, trace).accepted is False
