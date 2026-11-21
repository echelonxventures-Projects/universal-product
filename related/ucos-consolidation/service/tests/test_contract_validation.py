"""EC3-B11-U03 — Contract validation tests (meta-validity V1…V5 + USL + SCN)."""

from __future__ import annotations

from dataclasses import replace

from service.contract import make_contract
from service.contract_meta import ContractKind
from service.contract_traceability import build_contract_traceability
from service.contract_validation import (
    ContractClassifiedCheck,
    ContractDeclaresEffectsFaultsCheck,
    ContractExplicitSpecCheck,
    ContractIdentifiedCheck,
    ContractIoIsDataCheck,
    ContractPolicyByReferenceCheck,
    ContractTypedCheck,
    ContractValidationSubject,
    ContractValueFidelityCheck,
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
    contract_checks,
    validate_contract,
)

_IN = ("ENG-005:DF-2:req",)
_OUT = ("ENG-005:DF-2:resp",)


def _c(**kw):
    base = dict(
        type_tag="t", inputs=_IN, outputs=_OUT, effects=("ENG-005:eff",),
        faults=("ENG-005:flt",), policy_ref="ENG-005:SOE-09:p",
    )
    base.update(kw)
    return make_contract(**base)


def _subject(**overrides) -> ContractValidationSubject:
    c = _c()
    trace = build_contract_traceability(c, unit="EC3-B11-U03", forward=(c.contract_id,))
    base = ContractValidationSubject.from_contract(c, trace)
    return replace(base, **overrides) if overrides else base


def test_validate_contract_accepts_a_wellformed_contract():
    c = _c()
    trace = build_contract_traceability(c, unit="EC3-B11-U03", forward=(c.contract_id,))
    validation = validate_contract(c, trace)
    assert validation.accepted is True
    assert not validation.report.blocking_failures


def test_suite_has_eighteen_checks_and_shared_gate_ids():
    ids = {c.check_id for c in contract_checks()}
    assert len(contract_checks()) == 18
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
    assert ContractTypedCheck().evaluate(_subject(type_tag=" ")).passed is False


def test_identified_check_fails_on_bad_prefix():
    assert ContractIdentifiedCheck().evaluate(_subject(target_id="X")).passed is False


def test_identified_check_fails_on_missing_digest():
    assert ContractIdentifiedCheck().evaluate(_subject(value_digest="")).passed is False


def test_value_fidelity_check_fails_on_bad_digest():
    assert ContractValueFidelityCheck().evaluate(_subject(value_digest="zz")).passed is False


def test_classified_check_fails_outside_sxh03():
    assert ContractClassifiedCheck().evaluate(_subject(kind="Bogus")).passed is False


def test_explicit_spec_check_fails_without_io():
    assert ContractExplicitSpecCheck().evaluate(_subject(specifies_io=False)).passed is False


def test_io_is_data_check_fails_when_not_data():
    assert ContractIoIsDataCheck().evaluate(_subject(io_is_data=False)).passed is False


def test_declares_effects_faults_check_fails_when_undeclared():
    assert (
        ContractDeclaresEffectsFaultsCheck()
        .evaluate(_subject(declares_effects_and_faults=False))
        .passed
        is False
    )


def test_policy_by_reference_check_fails_when_blank():
    assert ContractPolicyByReferenceCheck().evaluate(_subject(policy_by_reference=False)).passed is False


def test_meta_class_single_check_fails_on_wrong_class():
    assert MetaClassSingleCheck().evaluate(_subject(meta_class="SMC-01")).passed is False


def test_meta_relationships_closed_check_fails_on_out_of_range():
    assert MetaRelationshipsClosedCheck().evaluate(_subject(relationships=("SMR-99",))).passed is False


def test_meta_constraints_check_fails_on_smk01():
    assert MetaConstraintsCheck().evaluate(_subject(type_tag="")).passed is False


def test_meta_constraints_check_fails_on_smk02():
    assert MetaConstraintsCheck().evaluate(_subject(io_is_data=False)).passed is False


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
        _subject(provenance_chain=("SMC-03", "SERVICE-001"))
    ).passed is False


def test_all_checks_pass_on_a_good_subject():
    s = _subject()
    for check in contract_checks():
        assert check.evaluate(s).passed is True, check.check_id


def test_technology_selecting_contract_is_rejected_end_to_end():
    c = _c(inputs=("ENG-005:DF-2:kafka",))
    trace = build_contract_traceability(c, unit="EC3-B11-U03", forward=(c.contract_id,))
    assert validate_contract(c, trace).accepted is False


def test_service_and_composition_kinds_validate():
    for kind in (ContractKind.SERVICE, ContractKind.COMPOSITION):
        c = _c(kind=kind)
        trace = build_contract_traceability(c, unit="EC3-B11-U03", forward=(c.contract_id,))
        assert validate_contract(c, trace).accepted is True
