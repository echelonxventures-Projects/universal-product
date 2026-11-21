"""EC3-B11-U04 — Interface validation tests (meta-validity V1…V5 + USL + SIN)."""

from __future__ import annotations

from dataclasses import replace

from service.interface import make_interface
from service.interface_meta import InterfaceKind
from service.interface_traceability import build_interface_traceability
from service.interface_validation import (
    FoundationReuseIntegrityCheck,
    FoundingAcyclicCheck,
    InterfaceBehaviorByReferenceCheck,
    InterfaceClassifiedCheck,
    InterfaceEndpointAbstractCheck,
    InterfaceExposedByServiceCheck,
    InterfaceIdentifiedCheck,
    InterfaceIoIsDataCheck,
    InterfaceSoleSurfaceCheck,
    InterfaceTypedCheck,
    InterfaceValidationSubject,
    InterfaceValueFidelityCheck,
    LifecycleValidCheck,
    MetaClassSingleCheck,
    MetaConstraintsCheck,
    MetaRelationshipsClosedCheck,
    NonConstitutiveCheck,
    ProvisionalDisclosureCheck,
    TechnologyIndependenceCheck,
    TraceabilityRootedCheck,
    interface_checks,
    validate_interface,
)

_SVC = "ENG-005:SOE-01:svc"
_OPS = ("ENG-005:SOE-05:op",)
_IO = ("ENG-005:DF-2:req", "ENG-005:DF-2:resp")


def _i(**kw):
    base = dict(
        type_tag="t", service_ref=_SVC, operations=_OPS, io_refs=_IO,
        endpoint_ref="ENG-005:locus:abstract",
    )
    base.update(kw)
    return make_interface(**base)


def _subject(**overrides) -> InterfaceValidationSubject:
    i = _i()
    trace = build_interface_traceability(i, unit="EC3-B11-U04", forward=(i.interface_id,))
    base = InterfaceValidationSubject.from_interface(i, trace)
    return replace(base, **overrides) if overrides else base


def test_validate_interface_accepts_a_wellformed_interface():
    i = _i()
    trace = build_interface_traceability(i, unit="EC3-B11-U04", forward=(i.interface_id,))
    validation = validate_interface(i, trace)
    assert validation.accepted is True
    assert not validation.report.blocking_failures


def test_suite_has_nineteen_checks_and_shared_gate_ids():
    ids = {c.check_id for c in interface_checks()}
    assert len(interface_checks()) == 19
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
    assert InterfaceTypedCheck().evaluate(_subject(type_tag=" ")).passed is False


def test_identified_check_fails_on_bad_prefix():
    assert InterfaceIdentifiedCheck().evaluate(_subject(target_id="X")).passed is False


def test_identified_check_fails_on_missing_digest():
    assert InterfaceIdentifiedCheck().evaluate(_subject(value_digest="")).passed is False


def test_value_fidelity_check_fails_on_bad_digest():
    assert InterfaceValueFidelityCheck().evaluate(_subject(value_digest="zz")).passed is False


def test_classified_check_fails_outside_sxh04():
    assert InterfaceClassifiedCheck().evaluate(_subject(kind="Bogus")).passed is False


def test_exposed_by_service_check_fails_without_service():
    assert InterfaceExposedByServiceCheck().evaluate(_subject(exposed_by_service=False)).passed is False


def test_sole_surface_check_fails_without_operations():
    assert InterfaceSoleSurfaceCheck().evaluate(_subject(is_sole_surface=False)).passed is False


def test_io_is_data_check_fails_when_not_data():
    assert InterfaceIoIsDataCheck().evaluate(_subject(io_is_data=False)).passed is False


def test_endpoint_abstract_check_fails_when_blank_present():
    assert InterfaceEndpointAbstractCheck().evaluate(_subject(endpoint_is_abstract=False)).passed is False


def test_behavior_by_reference_check_fails_when_absent():
    assert InterfaceBehaviorByReferenceCheck().evaluate(_subject(behavior_by_reference=False)).passed is False


def test_meta_class_single_check_fails_on_wrong_class():
    assert MetaClassSingleCheck().evaluate(_subject(meta_class="SMC-01")).passed is False


def test_meta_relationships_closed_check_fails_on_out_of_range():
    assert MetaRelationshipsClosedCheck().evaluate(_subject(relationships=("SMR-99",))).passed is False


def test_meta_constraints_check_fails_on_smk01():
    assert MetaConstraintsCheck().evaluate(_subject(type_tag="")).passed is False


def test_meta_constraints_check_fails_on_smk05():
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
        _subject(provenance_chain=("SMC-04", "SERVICE-001"))
    ).passed is False


def test_all_checks_pass_on_a_good_subject():
    s = _subject()
    for check in interface_checks():
        assert check.evaluate(s).passed is True, check.check_id


def test_technology_selecting_interface_is_rejected_end_to_end():
    i = _i(operations=("ENG-005:SOE-05:kafka.topic",))
    trace = build_interface_traceability(i, unit="EC3-B11-U04", forward=(i.interface_id,))
    assert validate_interface(i, trace).accepted is False


def test_event_and_stream_kinds_validate():
    for kind in (InterfaceKind.EVENT, InterfaceKind.STREAM):
        i = _i(kind=kind)
        trace = build_interface_traceability(i, unit="EC3-B11-U04", forward=(i.interface_id,))
        assert validate_interface(i, trace).accepted is True
