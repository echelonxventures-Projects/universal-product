"""EC3-B11-U07 — Orchestration validation tests (meta-validity V1…V5 + USL + SOO)."""

from __future__ import annotations

from typing import Any

from engine.runtime.disclosure import build_disclosure
from service.orchestration import make_orchestration
from service.orchestration_meta import ORCHESTRATION_RELATIONSHIPS, OrchestrationKind
from service.orchestration_traceability import build_orchestration_traceability
from service.orchestration_validation import (
    FoundationReuseIntegrityCheck,
    FoundingAcyclicCheck,
    LifecycleValidCheck,
    MetaClassSingleCheck,
    MetaConstraintsCheck,
    MetaRelationshipsClosedCheck,
    NonConstitutiveCheck,
    OrchestrationClassifiedCheck,
    OrchestrationContractBoundCheck,
    OrchestrationCoordinatesStepsCheck,
    OrchestrationCoordinationAcyclicCheck,
    OrchestrationDataByReferenceCheck,
    OrchestrationIdentifiedCheck,
    OrchestrationRuntimeReuseCheck,
    OrchestrationTopologyValidCheck,
    OrchestrationTypedCheck,
    OrchestrationValidationSubject,
    OrchestrationValueFidelityCheck,
    ProvisionalDisclosureCheck,
    TechnologyIndependenceCheck,
    TraceabilityRootedCheck,
    orchestration_checks,
    validate_orchestration,
)

_STEPS = (
    "ENG-005:SOE-05:ucos.service.operation.foundation",
    "ENG-005:SOE-05:ucos.service.operation.secondary",
)


def _orc():
    return make_orchestration(
        "ucos.service.orchestration.foundation",
        _STEPS,
        kind=OrchestrationKind.SEQUENTIAL,
        dependencies=((_STEPS[1], _STEPS[0]),),
        data_refs=("ENG-005:DF-2:ucos.data.entity.orchestrated",),
    )


def _trace(o):
    return build_orchestration_traceability(o, unit="EC3-B11-U07", forward=(o.orchestration_id,))


def _subject(**overrides: Any) -> OrchestrationValidationSubject:
    o = _orc()
    base: dict[str, Any] = dict(
        target_id=o.orchestration_id,
        blueprint_id="SMC-07",
        meta_class="SMC-07",
        type_tag=o.type_tag,
        kind=o.kind.value,
        value_digest=o.value_digest,
        step_refs=o.step_refs,
        dependencies=o.dependencies,
        execution_plan=o.execution_plan(),
        contract_ref=o.contract_ref,
        behavior_ref=o.behavior_ref,
        data_refs=o.data_refs,
        runtime_concern="RUNTIME-009",
        relationships=o.meta_relationships(),
        lifecycle_state=o.state.value,
        coordination_acyclic=True,
        founding_acyclic=True,
        coordinates_steps=True,
        topology_valid=True,
        contract_bound=True,
        runtime_reuse_valid=True,
        behavior_by_reference=True,
        data_by_reference=True,
        references_resolve=True,
        confers_authority=False,
        selects_technology=False,
        embeds_secret=False,
        redefines_foundation=False,
        substrate_refs=("ENG-001", "RL-F2", "DF-2"),
        provenance_chain=("SMC-07", "SOE-07", "11-SERVICE@b7e7657"),
        disclosure=build_disclosure(),
    )
    base.update(overrides)
    return OrchestrationValidationSubject(**base)


# -- end-to-end -------------------------------------------------------------


def test_validate_canonical_orchestration_accepted():
    o = _orc()
    result = validate_orchestration(o, _trace(o))
    assert result.accepted is True
    assert not result.report.blocking_failures


def test_validate_cyclic_orchestration_rejected():
    o = make_orchestration("t", _STEPS, dependencies=((_STEPS[0], _STEPS[1]), (_STEPS[1], _STEPS[0])),
                           kind=OrchestrationKind.CHOREOGRAPHED)
    result = validate_orchestration(o, _trace(o))
    assert result.accepted is False
    ids = {f.check_id for f in result.report.blocking_failures}
    assert "orchestration-coordination-acyclic" in ids


def test_suite_has_twenty_checks():
    assert len(orchestration_checks()) == 20


# -- per-check pass/fail ----------------------------------------------------


def test_typed_check():
    assert OrchestrationTypedCheck().evaluate(_subject()).passed is True
    assert OrchestrationTypedCheck().evaluate(_subject(type_tag="  ")).passed is False


def test_identified_check():
    assert OrchestrationIdentifiedCheck().evaluate(_subject()).passed is True
    assert OrchestrationIdentifiedCheck().evaluate(_subject(target_id="X")).passed is False
    assert OrchestrationIdentifiedCheck().evaluate(_subject(value_digest="")).passed is False


def test_value_fidelity_check():
    assert OrchestrationValueFidelityCheck().evaluate(_subject()).passed is True
    assert OrchestrationValueFidelityCheck().evaluate(_subject(value_digest="zz")).passed is False


def test_classified_check():
    assert OrchestrationClassifiedCheck().evaluate(_subject()).passed is True
    assert OrchestrationClassifiedCheck().evaluate(_subject(kind="Nope")).passed is False


def test_coordinates_steps_check():
    assert OrchestrationCoordinatesStepsCheck().evaluate(_subject()).passed is True
    assert OrchestrationCoordinatesStepsCheck().evaluate(_subject(coordinates_steps=False)).passed is False


def test_coordination_acyclic_check():
    assert OrchestrationCoordinationAcyclicCheck().evaluate(_subject()).passed is True
    assert OrchestrationCoordinationAcyclicCheck().evaluate(_subject(coordination_acyclic=False)).passed is False


def test_topology_valid_check():
    assert OrchestrationTopologyValidCheck().evaluate(_subject()).passed is True
    assert OrchestrationTopologyValidCheck().evaluate(_subject(topology_valid=False)).passed is False


def test_contract_bound_check():
    assert OrchestrationContractBoundCheck().evaluate(_subject()).passed is True
    assert OrchestrationContractBoundCheck().evaluate(_subject(contract_bound=False)).passed is False


def test_runtime_reuse_check():
    assert OrchestrationRuntimeReuseCheck().evaluate(_subject()).passed is True
    assert OrchestrationRuntimeReuseCheck().evaluate(_subject(runtime_reuse_valid=False)).passed is False


def test_data_by_reference_check():
    assert OrchestrationDataByReferenceCheck().evaluate(_subject()).passed is True
    assert OrchestrationDataByReferenceCheck().evaluate(_subject(data_by_reference=False)).passed is False


def test_meta_class_single_check():
    assert MetaClassSingleCheck().evaluate(_subject()).passed is True
    assert MetaClassSingleCheck().evaluate(_subject(meta_class="SMC-06")).passed is False


def test_meta_relationships_closed_check():
    assert MetaRelationshipsClosedCheck().evaluate(_subject()).passed is True
    bad = _subject(relationships=(*ORCHESTRATION_RELATIONSHIPS, "SMR-99"))
    assert MetaRelationshipsClosedCheck().evaluate(bad).passed is False


def test_meta_constraints_check():
    assert MetaConstraintsCheck().evaluate(_subject()).passed is True
    assert MetaConstraintsCheck().evaluate(_subject(type_tag="")).passed is False
    assert MetaConstraintsCheck().evaluate(_subject(contract_bound=False)).passed is False
    assert MetaConstraintsCheck().evaluate(_subject(references_resolve=False)).passed is False


def test_founding_acyclic_check():
    assert FoundingAcyclicCheck().evaluate(_subject()).passed is True
    assert FoundingAcyclicCheck().evaluate(_subject(founding_acyclic=False)).passed is False


def test_lifecycle_valid_check():
    assert LifecycleValidCheck().evaluate(_subject()).passed is True
    assert LifecycleValidCheck().evaluate(_subject(lifecycle_state="BOGUS")).passed is False


def test_foundation_reuse_integrity_check():
    assert FoundationReuseIntegrityCheck().evaluate(_subject()).passed is True
    assert FoundationReuseIntegrityCheck().evaluate(_subject(redefines_foundation=True)).passed is False
    assert FoundationReuseIntegrityCheck().evaluate(_subject(substrate_refs=())).passed is False


def test_technology_independence_check():
    assert TechnologyIndependenceCheck().evaluate(_subject()).passed is True
    assert TechnologyIndependenceCheck().evaluate(_subject(selects_technology=True)).passed is False


def test_non_constitutive_check():
    assert NonConstitutiveCheck().evaluate(_subject()).passed is True
    assert NonConstitutiveCheck().evaluate(_subject(confers_authority=True)).passed is False
    assert NonConstitutiveCheck().evaluate(_subject(embeds_secret=True)).passed is False


def test_provisional_disclosure_check():
    assert ProvisionalDisclosureCheck().evaluate(_subject()).passed is True
    assert ProvisionalDisclosureCheck().evaluate(_subject(disclosure={})).passed is False


def test_traceability_rooted_check():
    assert TraceabilityRootedCheck().evaluate(_subject()).passed is True
    assert TraceabilityRootedCheck().evaluate(_subject(provenance_chain=())).passed is False
    assert TraceabilityRootedCheck().evaluate(_subject(provenance_chain=("X", "Y"))).passed is False
    no_anchor = _subject(provenance_chain=("SMC-07", "SOE-07"))
    assert TraceabilityRootedCheck().evaluate(no_anchor).passed is False
