"""EC3-B12-U07 — State construct tests (AMC-07 + AMK-01/02/05/07/08 + UAL-12)."""

from __future__ import annotations

import pytest

from application.state import (
    State,
    StateError,
    make_state,
)
from application.state_meta import (
    STATE_META_CLASS,
    STATE_RELATIONSHIPS,
    StateKind,
    StateLifecycle,
)

HOLDER = "ENG-005:AMC-06:ucos.demo.interaction.a"
CONTEXT = "ENG-005:CONTEXT:ucos.demo.context"
DATA = "ENG-005:DF-2:ucos.demo.state.data"
BEHAVIOR = "ENG-005:RL-F2:runtime.state-transition"


def test_state_is_typed_identified_held_and_context_bound():
    s = make_state("ucos.demo.state", HOLDER)
    assert s.meta_class == STATE_META_CLASS  # V1 (AMC-07)
    assert s.type_tag == "ucos.demo.state"  # UAL-03 / STA-01 typed
    assert s.state_id.startswith("UCOS-STATE-")  # UAL-04 identified (ENG-001)
    assert len(s.value_digest) == 64  # ENG-003 value fidelity
    assert s.kind is StateKind.INTERACTION  # AXH-07 classified (default)
    assert s.facet() == "interaction"  # AXH-07 facet
    assert s.is_held() is True  # AMR-06 held-by
    assert s.presents_data() is True  # AMR-14 / STA-C4
    assert s.binds_runtime_state() is True  # AMR-11 / STA-03 (governing)
    assert s.context_is_bound() is True  # STA-06 / STA-C3 (distinctive)
    assert s.lifecycle_is_decidable() is True  # STA-07
    assert s.records_transitions() is True  # STA-05


def test_state_identity_is_deterministic_and_core_derived():
    a = make_state("t", HOLDER)
    b = make_state("t", HOLDER)
    c = make_state("t", "ENG-005:AMC-06:ucos.other.interaction")
    assert a.state_id == b.state_id  # same core → same ENG-001 identity
    assert a.state_id != c.state_id  # different holder → different identity


def test_kind_is_identity_defining_across_kinds():
    a = make_state("t", HOLDER, kind=StateKind.LIFECYCLE)
    b = make_state("t", HOLDER, kind=StateKind.CONTEXT)
    assert a.state_id != b.state_id  # kind/facet is part of identity


def test_state_is_immutable_objecthood():
    s = make_state("t", HOLDER)
    with pytest.raises((AttributeError, TypeError)):
        s.type_tag = "other"  # frozen object (ENG-002 objecthood)


def test_untyped_state_is_rejected_fail_closed():
    with pytest.raises(StateError):
        make_state("", HOLDER)  # UAL-03 / STA-01 — no untyped state may exist
    with pytest.raises(StateError):
        make_state("   ", HOLDER)


def test_non_string_type_tag_is_rejected():
    with pytest.raises(StateError):
        State(  # type: ignore[arg-type]
            type_tag=object(),
            kind=StateKind.INTERACTION,
            holder_ref=HOLDER,
        )


def test_bad_kind_is_rejected_fail_closed():
    with pytest.raises(StateError):
        State(  # type: ignore[arg-type]
            type_tag="t", kind="not-a-kind", holder_ref=HOLDER
        )


def test_state_without_holder_is_rejected():
    with pytest.raises(StateError):
        make_state("t", "")  # AMR-06 / AOR-06 — must be held by a construct
    with pytest.raises(StateError):
        make_state("t", "   ")


def test_state_without_context_is_rejected():
    with pytest.raises(StateError):
        make_state("t", HOLDER, context_ref="")  # STA-06 / STA-C3


def test_state_without_data_is_rejected():
    with pytest.raises(StateError):
        make_state("t", HOLDER, data_ref="")  # AMR-14 / STA-C4


def test_missing_behavior_reference_is_rejected():
    with pytest.raises(StateError):
        make_state("t", HOLDER, behavior_ref="")  # AMR-11 / STA-03


def test_bad_state_lifecycle_is_rejected_fail_closed():
    with pytest.raises(StateError):
        State(
            type_tag="t",
            kind=StateKind.INTERACTION,
            holder_ref=HOLDER,
            state="BAD",  # type: ignore[arg-type]
        )


def test_technology_bearing_context_is_rejected_at_construction():
    # STA-06 / STA-09 / STA-K5 — the declared context names no state store/technology.
    with pytest.raises(StateError):
        make_state("t", HOLDER, context_ref="ENG-005:CONTEXT:redis.session")
    with pytest.raises(StateError):
        make_state("t", HOLDER, context_ref="ENG-005:CONTEXT:localStorage.scope")


def test_technology_bearing_behavior_is_rejected_at_construction():
    # STA-03 / STA-C5 / STA-K5 — the RUNTIME state binding references RL-F2, not a tech.
    with pytest.raises(StateError):
        make_state("t", HOLDER, behavior_ref="ENG-005:RL-F2:redux.store")
    with pytest.raises(StateError):
        make_state("t", HOLDER, behavior_ref="ENG-005:RL-F2:xstate.machine")


def test_state_cannot_be_held_by_its_own_binding():
    # AMK-08 non-absorption guard.
    with pytest.raises(StateError):
        make_state("t", CONTEXT, context_ref=CONTEXT)
    with pytest.raises(StateError):
        make_state("t", DATA, data_ref=DATA)
    with pytest.raises(StateError):
        make_state("t", BEHAVIOR, behavior_ref=BEHAVIOR)


def test_relationships_are_within_amr_closure():
    s = make_state("t", HOLDER)
    assert set(s.meta_relationships()) <= set(f"AMR-{n:02d}" for n in range(1, 15))  # V2
    assert s.meta_relationships() == ("AMR-06", "AMR-10", "AMR-11", "AMR-14")
    assert s.meta_relationships() == STATE_RELATIONSHIPS


def test_state_uses_held_binds_presents_but_not_delivers_groups_engages_sequences():
    # The distinctive AMC-07 relationship set: uses AMR-06 (held-by) + AMR-11 (behaves-as)
    # + AMR-14 (presents-data) + AMR-10 (identified-by) and does NOT use AMR-01 (delivers),
    # AMR-03 (groups), AMR-04 (sequenced-by), AMR-05 (engaged-through), or AMR-07/12/13.
    rels = set(make_state("t", HOLDER).meta_relationships())
    assert {"AMR-06", "AMR-11", "AMR-14"} <= rels
    for absent in ("AMR-01", "AMR-02", "AMR-03", "AMR-04", "AMR-05", "AMR-07", "AMR-12", "AMR-13"):
        assert absent not in rels


def test_state_participates_in_no_founding_edge():
    # AMK-03 satisfied vacuously — a state uses no founding relationship (AMR-02/03/05).
    s = make_state("t", HOLDER)
    assert s.participates_in_founding_edge() is False
    assert s.is_founding_acyclic() is True  # V4 (vacuous / structural)


def test_all_state_kinds_construct_and_map_facet():
    assert make_state("t", HOLDER, kind=StateKind.LIFECYCLE).facet() == "lifecycle"
    assert make_state("t", HOLDER, kind=StateKind.INTERACTION).facet() == "interaction"
    assert make_state("t", HOLDER, kind=StateKind.CONTEXT).facet() == "context"


def test_kind_class_reflects_facet():
    assert make_state("t", HOLDER, kind=StateKind.CONTEXT).kind_class() == "context"


def test_held_by_and_is_held_by():
    s = make_state("t", HOLDER)
    assert s.held_by() == HOLDER  # AMR-06
    assert s.is_held_by(HOLDER) is True
    assert s.is_held_by("ENG-005:AMC-06:not-the-holder") is False


def test_declared_context_and_references_resolve():
    s = make_state("t", HOLDER)
    assert s.declared_context() == "ENG-005:CONTEXT:ucos.application.state.context.primary"
    assert s.references_resolve() is True  # AOI-03 / AMK-05/07


def test_lifecycle_is_forward_only():
    s = make_state("t", HOLDER, state=StateLifecycle.DEFINED)
    composed = s.transition(StateLifecycle.COMPOSED)
    assert composed.state is StateLifecycle.COMPOSED
    ctx = composed.transition(StateLifecycle.CONTEXTUALIZED)
    assert ctx.state is StateLifecycle.CONTEXTUALIZED
    executable = ctx.transition(StateLifecycle.EXECUTABLE)
    assert executable.state is StateLifecycle.EXECUTABLE
    with pytest.raises(StateError):
        executable.transition(StateLifecycle.DEFINED)  # UAL-12 / STA-04 — no backward


def test_transition_to_same_state_is_allowed():
    s = make_state("t", HOLDER, state=StateLifecycle.COMPOSED)
    same = s.transition(StateLifecycle.COMPOSED)  # not backward (forward-or-equal)
    assert same.state is StateLifecycle.COMPOSED


def test_transition_rejects_non_state_target():
    s = make_state("t", HOLDER)
    with pytest.raises(StateError):
        s.transition("EXECUTABLE")  # type: ignore[arg-type]


def test_transition_event_records_transition():
    # STA-05 / STA-C2 / §7 — every transition is recorded as a RUNTIME event by reference.
    s = make_state("t", HOLDER, state=StateLifecycle.DEFINED)
    event = s.transition_event(StateLifecycle.COMPOSED)
    assert event["record"] == "state-transitioned"  # AOV-07
    assert event["binding"] == "ENG-005:RL-F2:runtime.state-record"  # §7 RUNTIME event by ref
    assert event["from"] == "DEFINED"
    assert event["to"] == "COMPOSED"
    assert event["state_id"].startswith("UCOS-STATE-")


def test_transition_event_rejects_backward():
    s = make_state("t", HOLDER, state=StateLifecycle.EXECUTABLE)
    with pytest.raises(StateError):
        s.transition_event(StateLifecycle.DEFINED)  # UAL-12 / STA-04


def test_state_does_not_change_identity():
    a = make_state("t", HOLDER, state=StateLifecycle.DEFINED)
    b = make_state("t", HOLDER, state=StateLifecycle.COMPOSED)
    assert a.state_id == b.state_id  # identity is core-derived, not lifecycle


def test_non_constitutive_and_no_secret_no_technology():
    s = make_state("t", HOLDER)
    assert s.confers_authority() is False  # UAL-15 / STA-09 / C7
    assert s.redefines_foundation() is False  # UAL-02 / AMI-05
    assert s.selects_technology() is False  # UAL-15 / STA-09 (abstract references only)
    assert s.embeds_secret() is False


def test_technology_bearing_state_is_detected():
    # A technology marker in the holder ref is detected by selects_technology()
    # (context/behavior are rejected at construction; here the holder carries it).
    techy = make_state("t", "ENG-005:AMC-06:mongodb.session")
    assert techy.selects_technology() is True  # UAL-15 / STA-09 — concrete store named


def test_secret_bearing_state_is_detected():
    leaky = make_state("t", "ENG-005:AMC-06:password-reset")
    assert leaky.embeds_secret() is True  # UAL-15 / RR-07


def test_state_to_dict_records_substrate_reuse():
    s = make_state("t", HOLDER, kind=StateKind.CONTEXT)
    payload = s.to_dict()
    assert payload["substrate_refs"] == [
        "ENG-001",
        "ENG-002",
        "ENG-003",
        "ENG-004",
        "ENG-005",
        "RL-F2",
        "DF-2",
    ]
    assert payload["meta_class"] == "AMC-07"
    assert payload["kind"] == "Context-State"
    assert payload["facet"] == "context"
    assert payload["context_bound"] is True
    assert payload["binds_runtime_state"] is True
    assert payload["presents_data"] is True
    assert payload["is_held"] is True
    assert payload["lifecycle_decidable"] is True
    assert payload["records_transitions"] is True
    assert payload["holder_ref"] == HOLDER


def test_canonical_core_excludes_lifecycle_and_id():
    s = make_state("t", HOLDER)
    core = s.canonical_core()
    assert "state" not in core  # lifecycle is not identity-defining
    assert "state_id" not in core
    assert core["meta_class"] == "AMC-07"
    assert core["holder_ref"] == HOLDER
    assert core["facet"] == "interaction"


def test_state_type_is_the_realized_construct():
    assert isinstance(make_state("t", HOLDER), State)
