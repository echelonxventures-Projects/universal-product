"""EC3-B11-U05 — Operation validation tests (meta-validity V1…V5 + USL + SOP)."""

from __future__ import annotations

from dataclasses import replace

from service.operation import make_operation
from service.operation_meta import EffectKind, OperationKind
from service.operation_traceability import build_operation_traceability
from service.operation_validation import (
    FoundationReuseIntegrityCheck,
    FoundingAcyclicCheck,
    LifecycleValidCheck,
    MetaClassSingleCheck,
    MetaConstraintsCheck,
    MetaRelationshipsClosedCheck,
    NonConstitutiveCheck,
    OperationBehaviorByReferenceCheck,
    OperationClassifiedCheck,
    OperationContractBoundCheck,
    OperationEffectHonestCheck,
    OperationExecutionByReferenceCheck,
    OperationIdentifiedCheck,
    OperationInterfaceAddressedCheck,
    OperationIoIsDataCheck,
    OperationProvidedByServiceCheck,
    OperationSignatureBoundedCheck,
    OperationTypedCheck,
    OperationValidationSubject,
    OperationValueFidelityCheck,
    ProvisionalDisclosureCheck,
    TechnologyIndependenceCheck,
    TraceabilityRootedCheck,
    operation_checks,
    validate_operation,
)

_SVC = "ENG-005:SOE-01:svc"
_CON = "ENG-005:SOE-03:contract"
_IFACE = "ENG-005:SOE-04:iface"


def _o(**kw):
    base = dict(
        kind=OperationKind.COMMAND,
        input_refs=("ENG-005:DF-2:req",),
        output_refs=("ENG-005:DF-2:resp",),
        effects=(EffectKind.WRITE,),
        faults=("ucos.fault.bad-input",),
    )
    base.update(kw)
    type_tag = base.pop("type_tag", "t")
    return make_operation(type_tag, _SVC, _CON, _IFACE, **base)


def _subject(**overrides) -> OperationValidationSubject:
    o = _o()
    trace = build_operation_traceability(o, unit="EC3-B11-U05", forward=(o.operation_id,))
    base = OperationValidationSubject.from_operation(o, trace)
    return replace(base, **overrides) if overrides else base


def test_validate_operation_accepts_a_wellformed_operation():
    o = _o()
    trace = build_operation_traceability(o, unit="EC3-B11-U05", forward=(o.operation_id,))
    validation = validate_operation(o, trace)
    assert validation.accepted is True
    assert not validation.report.blocking_failures


def test_suite_has_twentytwo_checks_and_shared_gate_ids():
    ids = {c.check_id for c in operation_checks()}
    assert len(operation_checks()) == 22
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
    assert OperationTypedCheck().evaluate(_subject(type_tag=" ")).passed is False


def test_identified_check_fails_on_bad_prefix():
    assert OperationIdentifiedCheck().evaluate(_subject(target_id="X")).passed is False


def test_identified_check_fails_on_missing_digest():
    assert OperationIdentifiedCheck().evaluate(_subject(value_digest="")).passed is False


def test_value_fidelity_check_fails_on_bad_digest():
    assert OperationValueFidelityCheck().evaluate(_subject(value_digest="zz")).passed is False


def test_classified_check_fails_outside_sxh05():
    assert OperationClassifiedCheck().evaluate(_subject(kind="Bogus")).passed is False


def test_provided_by_service_check_fails_without_service():
    assert OperationProvidedByServiceCheck().evaluate(_subject(provided_by_service=False)).passed is False


def test_contract_bound_check_fails_without_contract():
    assert OperationContractBoundCheck().evaluate(_subject(contract_bound=False)).passed is False


def test_interface_addressed_check_fails_without_interface():
    assert OperationInterfaceAddressedCheck().evaluate(_subject(interface_addressed=False)).passed is False


def test_signature_bounded_check_fails_when_unbounded():
    assert OperationSignatureBoundedCheck().evaluate(_subject(signature_bounded=False)).passed is False


def test_effect_honest_check_fails_when_dishonest():
    assert OperationEffectHonestCheck().evaluate(_subject(effects_honest=False)).passed is False


def test_effect_honest_check_fails_on_unknown_effect():
    assert OperationEffectHonestCheck().evaluate(_subject(effects=("teleport",))).passed is False


def test_io_is_data_check_fails_when_not_data():
    assert OperationIoIsDataCheck().evaluate(_subject(io_is_data=False)).passed is False


def test_execution_by_reference_check_fails_when_absent():
    assert OperationExecutionByReferenceCheck().evaluate(_subject(execution_by_reference=False)).passed is False


def test_behavior_by_reference_check_fails_when_absent():
    assert OperationBehaviorByReferenceCheck().evaluate(_subject(behavior_by_reference=False)).passed is False


def test_meta_class_single_check_fails_on_wrong_class():
    assert MetaClassSingleCheck().evaluate(_subject(meta_class="SMC-01")).passed is False


def test_meta_relationships_closed_check_fails_on_out_of_range():
    assert MetaRelationshipsClosedCheck().evaluate(_subject(relationships=("SMR-99",))).passed is False


def test_meta_constraints_check_fails_on_smk01():
    assert MetaConstraintsCheck().evaluate(_subject(type_tag="")).passed is False


def test_meta_constraints_check_fails_on_smk02():
    assert MetaConstraintsCheck().evaluate(_subject(signature_bounded=False)).passed is False


def test_meta_constraints_check_fails_on_smk04():
    assert MetaConstraintsCheck().evaluate(_subject(interface_addressed=False)).passed is False


def test_meta_constraints_check_fails_on_smk05_07():
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
        _subject(provenance_chain=("SMC-05", "SERVICE-001"))
    ).passed is False


def test_all_checks_pass_on_a_good_subject():
    s = _subject()
    for check in operation_checks():
        assert check.evaluate(s).passed is True, check.check_id


def test_technology_selecting_operation_is_rejected_end_to_end():
    o = _o(input_refs=("ENG-005:DF-2:kafka.topic",))
    trace = build_operation_traceability(o, unit="EC3-B11-U05", forward=(o.operation_id,))
    assert validate_operation(o, trace).accepted is False


def test_query_and_event_operations_validate():
    for kind, effect in (
        (OperationKind.QUERY, EffectKind.READ),
        (OperationKind.EVENT, EffectKind.EMIT),
    ):
        o = _o(kind=kind, effects=(effect,))
        trace = build_operation_traceability(o, unit="EC3-B11-U05", forward=(o.operation_id,))
        assert validate_operation(o, trace).accepted is True


def test_dishonest_query_is_rejected_end_to_end():
    o = _o(kind=OperationKind.QUERY, effects=(EffectKind.WRITE,))
    trace = build_operation_traceability(o, unit="EC3-B11-U05", forward=(o.operation_id,))
    assert validate_operation(o, trace).accepted is False
