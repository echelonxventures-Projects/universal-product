"""EC3-B10-U06 — Lifecycle construct tests (DMC-07 + DLA-01…10 + UDL-12/03/04)."""

from __future__ import annotations

import pytest

from data.attribute import make_attribute
from data.datum import make_datum
from data.entity import entity_ref_for, make_entity
from data.lifecycle import (
    GovernedSubjectRef,
    Lifecycle,
    LifecycleError,
    Transition,
    forward_transitions,
    guard_ref_for,
    make_lifecycle,
    runtime_ref_for,
)
from data.lifecycle_meta import (
    LIFECYCLE_META_CLASS,
    LIFECYCLE_RELATIONSHIPS,
    LifecycleState,
    StateFacet,
)

ENTITY_NAME = "ucos.demo.entity"
LIFECYCLE_NAME = "ucos.demo.lifecycle"
STATE_REF = runtime_ref_for("state.defined")


def _entity(name=ENTITY_NAME):
    attr = make_attribute(
        "ucos.demo.attr",
        "ucos.core.string",
        make_datum("ucos.core.string", "hello"),
        entity_ref_for(name),
    )
    return make_entity(name, "ucos.core.entity", (attr,))


def _lifecycle(**overrides):
    entity = overrides.pop("entity", None) or _entity()
    kwargs = dict(
        current_state=overrides.pop("current_state", LifecycleState.DEFINED),
    )
    kwargs.update(overrides)
    transitions = kwargs.pop("transitions", forward_transitions())
    state_ref = kwargs.pop("state_ref", STATE_REF)
    name = kwargs.pop("name", LIFECYCLE_NAME)
    type_tag = kwargs.pop("type_tag", "ucos.core.lifecycle")
    return make_lifecycle(name, type_tag, entity, transitions, state_ref, **kwargs)


def test_lifecycle_is_typed_named_identified_and_classified():
    lc = _lifecycle()
    assert lc.meta_class == LIFECYCLE_META_CLASS  # V1 (DMC-07)
    assert lc.name == LIFECYCLE_NAME  # named
    assert lc.type_tag == "ucos.core.lifecycle"  # UDL-03 typed
    assert lc.lifecycle_id.startswith("UCOS-LIFECYCLE-")  # UDL-04 identified (ENG-001)
    assert lc.facet is StateFacet.DEFINITIONAL  # DXH-07 classified (DEFINED)
    assert lc.is_classified() is True


def test_lifecycle_transitions_entity_by_reference_not_owning():
    entity = _entity()
    lc = _lifecycle(entity=entity)
    assert lc.transitioned_entity_id() == entity.entity_id  # DMR-06 transitions
    assert lc.absorbs_subject() is False  # DLA-07 / DMX-02 — referenced, not owned
    ref_dict = lc.subject_ref.to_dict()
    assert ref_dict["owned"] is False
    assert ref_dict["binding"] == "DMR-06:transitions"


def test_governed_subject_ref_requires_certified_entity():
    with pytest.raises(LifecycleError):  # DMR-06
        GovernedSubjectRef.from_entity(object())


def test_states_are_the_closed_forward_only_set():
    lc = _lifecycle()
    assert lc.states_are_closed() is True  # DLA-02 / DOS-01…05
    assert [s.value for s in lc.states()] == [
        "DEFINED",
        "ACTIVE",
        "DEPRECATED",
        "SUPERSEDED",
        "RETIRED",
    ]


def test_transitions_are_forward_only_guarded_and_recorded():
    lc = _lifecycle()
    assert lc.is_forward_only() is True  # DLA-01 / DLA-C1
    assert lc.transitions_are_guarded() is True  # DLA-04 / DLA-C2
    assert lc.transitions_are_recorded() is True  # DLA-03 / DMR-11
    assert lc.guards_are_non_enforcing() is True  # DLA-K4


def test_lifecycle_binds_runtime_by_reference():
    lc = _lifecycle()
    assert lc.binds_runtime_by_reference() is True  # DMR-11 / DLA-07 / DOB-02
    assert lc.state_ref.startswith("UCOS-RUNTIME-REF:")


def test_lifecycle_identity_is_deterministic_and_structure_derived():
    a = _lifecycle()
    b = _lifecycle()
    c = _lifecycle(name="different.lifecycle")
    assert a.lifecycle_id == b.lifecycle_id  # same structure → same ENG-001 identity
    assert a.lifecycle_id != c.lifecycle_id  # different name → different identity


def test_lifecycle_is_immutable_objecthood():
    lc = _lifecycle()
    with pytest.raises((AttributeError, TypeError)):
        lc.name = "other"  # frozen object (ENG-002 objecthood)


def test_unnamed_lifecycle_is_rejected_fail_closed():
    with pytest.raises(LifecycleError):
        _lifecycle(name="")


def test_untyped_lifecycle_is_rejected_fail_closed():
    with pytest.raises(LifecycleError):
        _lifecycle(type_tag="")  # DLA-K1 / UDL-03


def test_lifecycle_with_no_transitions_is_rejected_fail_closed():
    with pytest.raises(LifecycleError):
        _lifecycle(transitions=())  # DLA-C1 — ≥1 forward-only transition required


def test_backward_transition_is_rejected_at_construction():
    with pytest.raises(LifecycleError):  # DLA-01 / DLA-C1 — forward-only
        Transition(
            from_state=LifecycleState.ACTIVE,
            to_state=LifecycleState.DEFINED,
            guard_ref=guard_ref_for("g"),
            event_ref=runtime_ref_for("e"),
        )


def test_unguarded_transition_is_rejected():
    with pytest.raises(LifecycleError):  # DLA-04 / DLA-K4
        Transition(
            from_state=LifecycleState.DEFINED,
            to_state=LifecycleState.ACTIVE,
            guard_ref="not-a-guard",
            event_ref=runtime_ref_for("e"),
        )


def test_unrecorded_transition_is_rejected():
    with pytest.raises(LifecycleError):  # DLA-03 / DMR-11
        Transition(
            from_state=LifecycleState.DEFINED,
            to_state=LifecycleState.ACTIVE,
            guard_ref=guard_ref_for("g"),
            event_ref="not-a-runtime-event",
        )


def test_duplicate_transition_is_rejected():
    dup = Transition(
        from_state=LifecycleState.DEFINED,
        to_state=LifecycleState.ACTIVE,
        guard_ref=guard_ref_for("g"),
        event_ref=runtime_ref_for("e"),
    )
    with pytest.raises(LifecycleError):  # DLA-C1
        _lifecycle(transitions=(dup, dup))


def test_lifecycle_naming_a_workflow_technology_is_rejected_fail_closed():
    # UDL-12 / DLA-09 / DLA-K5 — abstract state progression only; names no engine/product.
    with pytest.raises(LifecycleError):
        _lifecycle(name="airflow.dag")
    with pytest.raises(LifecycleError):
        _lifecycle(type_tag="camunda.bpmn")
    with pytest.raises(LifecycleError):
        _lifecycle(state_ref=runtime_ref_for("temporal.io.workflow"))


def test_relationships_are_within_dmr_closure():
    lc = _lifecycle()
    assert set(lc.meta_relationships()) <= set(LIFECYCLE_RELATIONSHIPS)  # V2
    assert lc.meta_relationships() == ("DMR-06", "DMR-10", "DMR-11")


def test_progression_is_forward_only_along_declared_transitions():
    lc = _lifecycle(current_state=LifecycleState.DEFINED)
    active = lc.transition(LifecycleState.ACTIVE)
    assert active.current_state is LifecycleState.ACTIVE
    with pytest.raises(LifecycleError):
        active.transition(LifecycleState.DEFINED)  # UDL-12 / DLA-01 — no backward


def test_progression_to_undeclared_transition_is_rejected():
    lc = _lifecycle(
        transitions=(
            Transition(
                from_state=LifecycleState.DEFINED,
                to_state=LifecycleState.ACTIVE,
                guard_ref=guard_ref_for("g"),
                event_ref=runtime_ref_for("e"),
            ),
        )
    )
    active = lc.transition(LifecycleState.ACTIVE)
    with pytest.raises(LifecycleError):  # DLA-C2 — transition not declared
        active.transition(LifecycleState.RETIRED)


def test_forward_skip_transition_is_permitted():
    # DLA-C1 — forward skips permitted; declare DEFINED→RETIRED directly.
    lc = _lifecycle(
        transitions=(
            Transition(
                from_state=LifecycleState.DEFINED,
                to_state=LifecycleState.RETIRED,
                guard_ref=guard_ref_for("g"),
                event_ref=runtime_ref_for("e"),
            ),
        )
    )
    retired = lc.transition(LifecycleState.RETIRED)
    assert retired.current_state is LifecycleState.RETIRED


def test_single_state_invariant_holds():
    lc = _lifecycle()
    assert lc.is_single_state() is True  # DLA-C5
    assert lc.current_state is LifecycleState.DEFINED


def test_retention_is_represented_as_terminal_state():
    lc = _lifecycle()
    assert lc.represents_retention() is True  # DLA-06 / DLA-C3 — terminal-state records


def test_supersession_lineage_is_recorded():
    lc = _lifecycle(version="2.0.0", supersedes="UCOS-LIFECYCLE-old-0000000000000000")
    assert lc.version == "2.0.0"  # DLA-08
    assert lc.supersedes == "UCOS-LIFECYCLE-old-0000000000000000"  # DLA-05 / DLA-C4
    with pytest.raises(LifecycleError):
        _lifecycle(version="")


def test_founding_graph_is_acyclic():
    lc = _lifecycle()
    assert lc.is_founding_acyclic() is True  # V4 / DMK-03


def test_invalid_state_ref_is_rejected():
    with pytest.raises(LifecycleError):  # DMR-11 / DLA-07 — must bind a RUNTIME reference
        _lifecycle(state_ref="not-a-runtime-ref")


def test_subject_without_certified_entity_id_is_rejected():
    bad_ref = GovernedSubjectRef(
        entity_id="NOT-AN-ENTITY",
        structure_digest="a" * 64,
        name="x",
        type_tag="t",
        meta_class="DMC-02",
    )
    with pytest.raises(LifecycleError):  # DMR-06
        make_lifecycle("lc", "ucos.core.lifecycle", bad_ref, forward_transitions(), STATE_REF)


def test_non_constitutive_and_no_secret():
    lc = _lifecycle()
    assert lc.confers_authority() is False  # UDL-15 / DLA-09 / C7
    assert lc.redefines_el1() is False  # UDL-02 / DMI-05
    assert lc.selects_technology() is False  # UDL-12 / DLA-K5 (abstract progression)
    assert lc.embeds_secret() is False


def test_secret_bearing_lifecycle_is_detected():
    leaky = _lifecycle(name="password")
    assert leaky.embeds_secret() is True  # UDL-15 / RR-07


def test_lifecycle_to_dict_records_substrate_reuse():
    lc = _lifecycle()
    payload = lc.to_dict()
    assert payload["substrate_refs"] == ["ENG-001", "ENG-002", "ENG-004", "ENG-005"]
    assert payload["meta_class"] == "DMC-07"
    assert payload["absorbs_subject"] is False
    assert payload["forward_only"] is True
    assert payload["transitions_guarded"] is True
    assert payload["transitions_recorded"] is True
    assert payload["names_technology"] is False
    assert payload["states_closed"] is True


def test_lifecycle_type_is_the_realized_construct():
    assert isinstance(_lifecycle(), Lifecycle)


def test_forward_transitions_builds_the_full_chain():
    chain = forward_transitions()
    assert len(chain) == 4  # DEFINED→ACTIVE→DEPRECATED→SUPERSEDED→RETIRED
    assert all(t.is_forward_only for t in chain)
    pairs = [(t.from_state.value, t.to_state.value) for t in chain]
    assert pairs == [
        ("DEFINED", "ACTIVE"),
        ("ACTIVE", "DEPRECATED"),
        ("DEPRECATED", "SUPERSEDED"),
        ("SUPERSEDED", "RETIRED"),
    ]


def test_transition_between_non_states_is_rejected():
    with pytest.raises(LifecycleError):  # DLA-02
        Transition(
            from_state="DEFINED",  # not a LifecycleState
            to_state=LifecycleState.ACTIVE,
            guard_ref=guard_ref_for("g"),
            event_ref=runtime_ref_for("e"),
        )


def test_non_governed_subject_ref_is_rejected():
    with pytest.raises(LifecycleError):  # DMR-06
        Lifecycle(
            name="lc",
            type_tag="ucos.core.lifecycle",
            subject_ref="not-a-ref",
            transitions=forward_transitions(),
            state_ref=STATE_REF,
        )


def test_subject_without_structural_digest_is_rejected():
    bad_ref = GovernedSubjectRef(
        entity_id="UCOS-ENTITY-x-0000000000000000",
        structure_digest="short",  # not a 64-hex digest
        name="x",
        type_tag="t",
        meta_class="DMC-02",
    )
    with pytest.raises(LifecycleError):  # UDL-06
        make_lifecycle("lc", "ucos.core.lifecycle", bad_ref, forward_transitions(), STATE_REF)


def test_non_transition_member_is_rejected():
    with pytest.raises(LifecycleError):  # DLA-01
        _lifecycle(transitions=("not-a-transition",))


def test_non_state_current_state_is_rejected():
    with pytest.raises(LifecycleError):  # UDL-12
        _lifecycle(current_state="DEFINED")  # str, not LifecycleState


def test_non_string_supersedes_is_rejected():
    with pytest.raises(LifecycleError):  # DLA-05
        _lifecycle(supersedes=123)


def test_transition_to_non_state_is_rejected():
    lc = _lifecycle()
    with pytest.raises(LifecycleError):  # UDL-12
        lc.transition("ACTIVE")  # str, not LifecycleState
