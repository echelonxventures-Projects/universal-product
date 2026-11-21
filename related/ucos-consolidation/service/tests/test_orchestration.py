"""EC3-B11-U07 — Universal Orchestration construct tests (SMC-07).

Covers construction fail-closed guards, the deterministic coordination graph (acyclicity,
self-dependency + unresolved-edge rejection, per-kind topology, execution plan), identity/
value determinism, non-constitutiveness, lifecycle, and serialization.
"""

from __future__ import annotations

import pytest

from service.orchestration import (
    DEFAULT_CONTRACT_REF,
    Orchestration,
    _default_behavior_ref,
    make_orchestration,
)
from service.orchestration_meta import (
    KIND_RUNTIME_CONCERN,
    ORCHESTRATION_RELATIONSHIPS,
    OrchestrationKind,
)
from service.service import ServiceError
from service.service_meta import ServiceState

_STEPS = (
    "ENG-005:SOE-05:ucos.service.operation.foundation",
    "ENG-005:SOE-05:ucos.service.operation.secondary",
    "ENG-005:SOE-05:ucos.service.operation.tertiary",
)
_CHAIN = ((_STEPS[1], _STEPS[0]), (_STEPS[2], _STEPS[1]))


def _seq() -> Orchestration:
    return make_orchestration(
        "ucos.service.orchestration.foundation",
        _STEPS,
        kind=OrchestrationKind.SEQUENTIAL,
        dependencies=_CHAIN,
        data_refs=("ENG-005:DF-2:ucos.data.entity.orchestrated",),
    )


# -- construction guards ----------------------------------------------------


def test_untyped_orchestration_rejected():
    with pytest.raises(ServiceError, match="typed"):
        make_orchestration("  ", _STEPS)


def test_bad_kind_rejected():
    with pytest.raises(ServiceError, match="OrchestrationKind"):
        Orchestration(type_tag="t", kind="Sequential", step_refs=_STEPS)  # type: ignore[arg-type]


def test_empty_steps_rejected():
    with pytest.raises(ServiceError, match="coordinates ≥1 step"):
        make_orchestration("t", ())


def test_non_tuple_steps_rejected():
    with pytest.raises(ServiceError, match="tuple of ENG-005 references"):
        make_orchestration("t", ["a", "b"])  # type: ignore[arg-type]


def test_blank_step_entry_rejected():
    with pytest.raises(ServiceError, match="entries must be non-empty"):
        make_orchestration("t", ("ok", "  "))


def test_non_tuple_dependencies_rejected():
    with pytest.raises(ServiceError, match="tuple of \\(dependent"):
        make_orchestration("t", _STEPS, dependencies=[(_STEPS[1], _STEPS[0])])  # type: ignore[arg-type]


def test_bad_edge_shape_rejected():
    with pytest.raises(ServiceError, match="2-tuples"):
        make_orchestration("t", _STEPS, dependencies=((_STEPS[0],),))  # type: ignore[arg-type]


def test_blank_edge_endpoint_rejected():
    with pytest.raises(ServiceError, match="endpoints must be non-empty"):
        make_orchestration("t", _STEPS, dependencies=(("", _STEPS[0]),))


def test_blank_contract_rejected():
    with pytest.raises(ServiceError, match="contract_ref"):
        make_orchestration("t", _STEPS, contract_ref="   ")


def test_non_tuple_data_refs_rejected():
    with pytest.raises(ServiceError, match="tuple of ENG-005 references"):
        make_orchestration("t", _STEPS, data_refs=["x"])  # type: ignore[arg-type]


def test_bad_state_rejected():
    with pytest.raises(ServiceError, match="ServiceState"):
        Orchestration(type_tag="t", kind=OrchestrationKind.PARALLEL, step_refs=_STEPS, state="X")  # type: ignore[arg-type]


# -- identity + defaults ----------------------------------------------------


def test_identity_is_deterministic_and_prefixed():
    a, b = _seq(), _seq()
    assert a.orchestration_id == b.orchestration_id
    assert a.orchestration_id.startswith("UCOS-ORCHESTRATION-")
    assert len(a.value_digest) == 64


def test_self_ref_form():
    assert _seq().self_ref == "ENG-005:SOE-07:ucos.service.orchestration.foundation"


def test_meta_class_and_relationships():
    o = _seq()
    assert o.meta_class == "SMC-07"
    assert o.meta_relationships() == ORCHESTRATION_RELATIONSHIPS


@pytest.mark.parametrize("kind", list(OrchestrationKind))
def test_default_behavior_ref_matches_kind(kind):
    ref = _default_behavior_ref(kind)
    assert KIND_RUNTIME_CONCERN[kind] in ref
    o = make_orchestration("t", _STEPS[:2], kind=kind)
    assert o.runtime_reuse_valid() is True


def test_explicit_behavior_ref_preserved():
    o = make_orchestration("t", _STEPS[:2], behavior_ref="ENG-005:RL-F2:RUNTIME-013.orchestration",
                           kind=OrchestrationKind.PARALLEL)
    assert o.behavior_ref == "ENG-005:RL-F2:RUNTIME-013.orchestration"
    assert o.contract_ref == DEFAULT_CONTRACT_REF


# -- deterministic coordination graph ---------------------------------------


def test_sequential_chain_execution_plan_is_total_order():
    o = _seq()
    assert o.execution_plan() == _STEPS
    assert o.coordination_levels() == ((_STEPS[0],), (_STEPS[1],), (_STEPS[2],))
    assert o.is_coordination_acyclic() is True
    assert o.is_founding_acyclic() is True
    assert o.topology_valid() is True


def test_cyclic_graph_is_rejected_by_plan():
    o = make_orchestration("t", (_STEPS[0], _STEPS[1]),
                           dependencies=((_STEPS[0], _STEPS[1]), (_STEPS[1], _STEPS[0])),
                           kind=OrchestrationKind.CHOREOGRAPHED)
    assert o.coordination_levels() == ()
    assert o.execution_plan() == ()
    assert o.is_coordination_acyclic() is False
    assert o.is_founding_acyclic() is False
    assert o.topology_valid() is False


def test_self_dependency_rejected_by_plan():
    o = make_orchestration("t", (_STEPS[0], _STEPS[1]),
                           dependencies=((_STEPS[0], _STEPS[0]),),
                           kind=OrchestrationKind.CHOREOGRAPHED)
    assert o.coordination_levels() == ()
    assert o.dependencies_resolve() is False


def test_unresolved_edge_endpoint_rejected_by_plan():
    o = make_orchestration("t", (_STEPS[0], _STEPS[1]),
                           dependencies=(("ENG-005:SOE-05:ghost", _STEPS[0]),),
                           kind=OrchestrationKind.CHOREOGRAPHED)
    assert o.coordination_levels() == ()
    assert o.dependencies_resolve() is False
    assert o.references_resolve() is False


def test_parallel_topology_requires_no_dependencies():
    ok = make_orchestration("t", (_STEPS[0], _STEPS[1]), kind=OrchestrationKind.PARALLEL)
    assert ok.topology_valid() is True
    assert ok.coordination_levels() == ((_STEPS[0], _STEPS[1]),)
    # parallel with a dependency is not concurrent → invalid
    bad = make_orchestration("t", (_STEPS[0], _STEPS[1]),
                             dependencies=((_STEPS[1], _STEPS[0]),),
                             kind=OrchestrationKind.PARALLEL)
    assert bad.topology_valid() is False
    # parallel needs ≥2 steps
    single = make_orchestration("t", (_STEPS[0],), kind=OrchestrationKind.PARALLEL)
    assert single.topology_valid() is False


def test_sequential_with_branching_is_not_total_order():
    # foundation → {secondary, tertiary}: two ready at a level → not a strict chain
    o = make_orchestration("t", _STEPS,
                           dependencies=((_STEPS[1], _STEPS[0]), (_STEPS[2], _STEPS[0])),
                           kind=OrchestrationKind.SEQUENTIAL)
    assert o.is_coordination_acyclic() is True
    assert o.topology_valid() is False


def test_choreographed_topology_requires_two_steps():
    single = make_orchestration("t", (_STEPS[0],), kind=OrchestrationKind.CHOREOGRAPHED)
    assert single.topology_valid() is False
    partial = make_orchestration("t", (_STEPS[0], _STEPS[1], _STEPS[2]),
                                 dependencies=((_STEPS[2], _STEPS[0]),),
                                 kind=OrchestrationKind.CHOREOGRAPHED)
    assert partial.topology_valid() is True


# -- obligations ------------------------------------------------------------


def test_obligation_predicates_hold_for_canonical():
    o = _seq()
    assert o.coordinates_steps() is True
    assert o.steps_contracted() is True
    assert o.contract_bound() is True
    assert o.runtime_reuse_valid() is True
    assert o.behavior_by_reference() is True
    assert o.data_by_reference() is True
    assert o.references_resolve() is True
    assert o.redefines_foundation() is False
    assert o.confers_authority() is False


def test_runtime_reuse_invalid_when_wrong_concern():
    o = make_orchestration("t", _STEPS[:2], behavior_ref="ENG-005:RL-F2:RUNTIME-999.other",
                           kind=OrchestrationKind.SEQUENTIAL)
    assert o.runtime_reuse_valid() is False


def test_selects_technology_detected():
    o = make_orchestration("t", ("ENG-005:SOE-05:kafka.step", _STEPS[1]),
                           kind=OrchestrationKind.PARALLEL)
    assert o.selects_technology() is True


def test_embeds_secret_detected():
    o = make_orchestration("t", ("ENG-005:SOE-05:password.step", _STEPS[1]),
                           kind=OrchestrationKind.PARALLEL)
    assert o.embeds_secret() is True


def test_clean_orchestration_has_no_tech_or_secret():
    o = _seq()
    assert o.selects_technology() is False
    assert o.embeds_secret() is False


# -- lifecycle --------------------------------------------------------------


def test_forward_transition_ok():
    o = _seq().transition(ServiceState.CONTRACTED)
    assert o.state is ServiceState.CONTRACTED


def test_backward_transition_rejected():
    o = _seq().transition(ServiceState.EXECUTABLE)
    with pytest.raises(ServiceError, match="forward-only"):
        o.transition(ServiceState.DEFINED)


def test_bad_transition_target_rejected():
    with pytest.raises(ServiceError, match="ServiceState"):
        _seq().transition("EXECUTABLE")  # type: ignore[arg-type]


# -- serialization ----------------------------------------------------------


def test_to_dict_is_complete_and_deterministic():
    d = _seq().to_dict()
    assert d["meta_class"] == "SMC-07"
    assert d["kind"] == OrchestrationKind.SEQUENTIAL.value
    assert d["execution_plan"] == list(_STEPS)
    assert d["coordination_levels"] == [[_STEPS[0]], [_STEPS[1]], [_STEPS[2]]]
    assert d["runtime_concern"] == "RUNTIME-009"
    assert d["dependencies"] == [list(e) for e in _CHAIN]
    assert d["relationships"] == list(ORCHESTRATION_RELATIONSHIPS)
    assert "RL-F2" in d["substrate_refs"] and "DF-2" in d["substrate_refs"]
