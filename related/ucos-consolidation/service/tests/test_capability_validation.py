"""EC3-B11-U02 — Capability validation tests (meta-validity V1…V5 + USL conformance).

Per-check negative coverage is achieved by constructing a crafted
:class:`~service.capability_validation.CapabilityValidationSubject` and flipping the
single signal each check evaluates, then calling the check's ``evaluate`` directly.
"""

from __future__ import annotations

from dataclasses import replace

from service.capability import make_capability
from service.capability_meta import CapabilityKind
from service.capability_traceability import build_capability_traceability
from service.capability_validation import (
    BehaviorByReferenceCheck,
    CapabilityClassifiedCheck,
    CapabilityIdentifiedCheck,
    CapabilityRealizedByCheck,
    CapabilityTypedCheck,
    CapabilityValidationSubject,
    CapabilityValueFidelityCheck,
    FoundationReuseIntegrityCheck,
    FoundingAcyclicCheck,
    LifecycleValidCheck,
    MetaClassSingleCheck,
    MetaConstraintsCheck,
    MetaRelationshipsClosedCheck,
    NonConstitutiveCheck,
    PlatformCompositionByReferenceCheck,
    ProvisionalDisclosureCheck,
    TechnologyIndependenceCheck,
    TraceabilityRootedCheck,
    capability_checks,
    validate_capability,
)
from service.service_meta import ServiceState


def _subject(**overrides) -> CapabilityValidationSubject:
    c = make_capability("t", service_ref="ENG-005:SMC-01:svc")
    trace = build_capability_traceability(c, unit="EC3-B11-U02", forward=(c.capability_id,))
    base = CapabilityValidationSubject.from_capability(c, trace)
    return replace(base, **overrides) if overrides else base


# --- happy path -------------------------------------------------------------


def test_validate_capability_accepts_a_wellformed_capability():
    c = make_capability("t", service_ref="ENG-005:SMC-01:svc")
    trace = build_capability_traceability(c, unit="EC3-B11-U02", forward=(c.capability_id,))
    validation = validate_capability(c, trace)
    assert validation.accepted is True
    assert validation.report.verdict.value == "pass"
    assert not validation.report.blocking_failures


def test_suite_has_seventeen_checks_and_the_shared_gate_ids():
    ids = {c.check_id for c in capability_checks()}
    assert len(capability_checks()) == 17
    # generic ids the reused CCE gates depend on must be present
    assert {
        "traceability-rooted",
        "meta-class-single",
        "foundation-reuse-integrity",
        "service-value-fidelity",
        "founding-acyclic",
        "meta-relationships-closed",
        "provisional-state-disclosure",
    } <= ids


def test_subject_projection_carries_meta_facts():
    s = _subject()
    assert s.meta_class == "SMC-02"
    assert s.target_id.startswith("UCOS-CAPABILITY-")
    assert s.blueprint_id == "SMC-02"


# --- per-check negative coverage -------------------------------------------


def test_typed_check_fails_on_blank_type():
    assert CapabilityTypedCheck().evaluate(_subject(type_tag="  ")).passed is False


def test_identified_check_fails_on_bad_prefix():
    assert CapabilityIdentifiedCheck().evaluate(_subject(target_id="X-1")).passed is False


def test_identified_check_fails_on_missing_digest():
    s = _subject(value_digest="")
    assert CapabilityIdentifiedCheck().evaluate(s).passed is False


def test_value_fidelity_check_fails_on_bad_digest():
    assert CapabilityValueFidelityCheck().evaluate(_subject(value_digest="zz")).passed is False


def test_classified_check_fails_outside_sxh02():
    assert CapabilityClassifiedCheck().evaluate(_subject(kind="Bogus")).passed is False


def test_realized_by_check_fails_on_blank_but_present_ref():
    assert CapabilityRealizedByCheck().evaluate(_subject(service_ref="   ")).passed is False


def test_realized_by_check_passes_when_unbound():
    assert CapabilityRealizedByCheck().evaluate(_subject(service_ref="")).passed is True


def test_meta_class_single_check_fails_on_wrong_class():
    assert MetaClassSingleCheck().evaluate(_subject(meta_class="SMC-01")).passed is False


def test_meta_relationships_closed_check_fails_on_out_of_range():
    assert (
        MetaRelationshipsClosedCheck().evaluate(_subject(relationships=("SMR-99",))).passed is False
    )


def test_meta_constraints_check_fails_on_smk01():
    assert MetaConstraintsCheck().evaluate(_subject(type_tag="")).passed is False


def test_meta_constraints_check_fails_on_unresolved_refs():
    assert MetaConstraintsCheck().evaluate(_subject(references_resolve=False)).passed is False


def test_founding_acyclic_check_fails_when_cyclic():
    assert FoundingAcyclicCheck().evaluate(_subject(founding_acyclic=False)).passed is False


def test_lifecycle_valid_check_fails_on_bad_state():
    assert LifecycleValidCheck().evaluate(_subject(lifecycle_state="LIVE")).passed is False


def test_foundation_reuse_check_fails_on_redefinition():
    assert (
        FoundationReuseIntegrityCheck().evaluate(_subject(redefines_foundation=True)).passed is False
    )


def test_foundation_reuse_check_fails_on_missing_substrate():
    assert FoundationReuseIntegrityCheck().evaluate(_subject(substrate_refs=())).passed is False


def test_platform_composition_check_fails_on_blank_ref():
    assert (
        PlatformCompositionByReferenceCheck().evaluate(_subject(platform_ref=" ")).passed is False
    )


def test_behavior_reference_check_fails_on_blank_ref():
    assert BehaviorByReferenceCheck().evaluate(_subject(behavior_ref="")).passed is False


def test_technology_independence_check_fails_when_technology_selected():
    assert (
        TechnologyIndependenceCheck().evaluate(_subject(selects_technology=True)).passed is False
    )


def test_non_constitutive_check_fails_on_authority():
    assert NonConstitutiveCheck().evaluate(_subject(confers_authority=True)).passed is False


def test_non_constitutive_check_fails_on_secret():
    assert NonConstitutiveCheck().evaluate(_subject(embeds_secret=True)).passed is False


def test_provisional_disclosure_check_fails_when_absent():
    assert ProvisionalDisclosureCheck().evaluate(_subject(disclosure={})).passed is False


def test_traceability_rooted_check_fails_on_empty_chain():
    assert TraceabilityRootedCheck().evaluate(_subject(provenance_chain=())).passed is False


def test_traceability_rooted_check_fails_on_wrong_root():
    s = _subject(provenance_chain=("SMC-01", "11-SERVICE@b7e7657"))
    assert TraceabilityRootedCheck().evaluate(s).passed is False


def test_traceability_rooted_check_fails_without_anchor():
    s = _subject(provenance_chain=("SMC-02", "SERVICE-001"))
    assert TraceabilityRootedCheck().evaluate(s).passed is False


def test_all_checks_pass_on_a_good_subject():
    s = _subject()
    for check in capability_checks():
        assert check.evaluate(s).passed is True, check.check_id


def test_technology_selecting_capability_is_rejected_end_to_end():
    c = make_capability("t", behavior_ref="ENG-005:RL-F2:kafka")
    trace = build_capability_traceability(c, unit="EC3-B11-U02", forward=(c.capability_id,))
    validation = validate_capability(c, trace)
    assert validation.accepted is False


def test_query_and_command_kinds_validate():
    for kind in (CapabilityKind.QUERY, CapabilityKind.COMMAND):
        c = make_capability("t", kind=kind, state=ServiceState.CONTRACTED)
        trace = build_capability_traceability(c, unit="EC3-B11-U02", forward=(c.capability_id,))
        assert validate_capability(c, trace).accepted is True
