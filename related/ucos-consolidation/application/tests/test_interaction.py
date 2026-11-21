"""EC3-B12-U06 — Interaction construct tests (AMC-06 + AMK-01/02/03/05/07/08 + UAL-11)."""

from __future__ import annotations

import pytest

from application.interaction import (
    Interaction,
    InteractionError,
    make_interaction,
)
from application.interaction_meta import (
    INTERACTION_META_CLASS,
    INTERACTION_RELATIONSHIPS,
    InteractionKind,
    InteractionState,
)

FEATURE = "ENG-005:AMC-04:ucos.demo.feature.a"
SURFACE = "ENG-005:SURFACE:ucos.demo.surface"
DATA = "ENG-005:DF-2:ucos.demo.exchange"
STATE = "ENG-005:AMC-07:ucos.demo.state"
BEHAVIOR = "ENG-005:RL-F2:runtime.interaction-exchange"


def test_interaction_is_typed_identified_engages_and_presents():
    i = make_interaction("ucos.demo.interaction", FEATURE)
    assert i.meta_class == INTERACTION_META_CLASS  # V1 (AMC-06)
    assert i.type_tag == "ucos.demo.interaction"  # UAL-03/11 typed
    assert i.interaction_id.startswith("UCOS-INTERACTION-")  # UAL-04 identified (ENG-001)
    assert len(i.value_digest) == 64  # ENG-003 value fidelity
    assert i.kind is InteractionKind.INPUT  # AXH-06 classified (default)
    assert i.direction() == "input"  # INT-07 direction
    assert i.engages_feature() is True  # AMR-05 / INT-04 (founding)
    assert i.presents_data() is True  # AMR-14 / INT-06
    assert i.holds_state() is True  # AMR-06
    assert i.surface_is_abstract() is True  # INT-03 / INT-C1
    assert i.is_sole_engagement_point() is True  # INT-04 / INT-C2


def test_interaction_identity_is_deterministic_and_core_derived():
    a = make_interaction("t", FEATURE)
    b = make_interaction("t", FEATURE)
    c = make_interaction("t", "ENG-005:AMC-04:ucos.other.feature")
    assert a.interaction_id == b.interaction_id  # same core → same ENG-001 identity
    assert a.interaction_id != c.interaction_id  # different feature → different identity


def test_direction_is_identity_defining_across_kinds():
    a = make_interaction("t", FEATURE, kind=InteractionKind.COMMAND)
    b = make_interaction("t", FEATURE, kind=InteractionKind.QUERY)
    assert a.interaction_id != b.interaction_id  # kind/direction is part of identity


def test_interaction_is_immutable_objecthood():
    i = make_interaction("t", FEATURE)
    with pytest.raises((AttributeError, TypeError)):
        i.type_tag = "other"  # frozen object (ENG-002 objecthood)


def test_untyped_interaction_is_rejected_fail_closed():
    with pytest.raises(InteractionError):
        make_interaction("", FEATURE)  # UAL-03/11 — no untyped interaction may exist
    with pytest.raises(InteractionError):
        make_interaction("   ", FEATURE)


def test_non_string_type_tag_is_rejected():
    with pytest.raises(InteractionError):
        Interaction(  # type: ignore[arg-type]
            type_tag=object(),
            kind=InteractionKind.INPUT,
            feature_ref=FEATURE,
        )


def test_bad_kind_is_rejected_fail_closed():
    with pytest.raises(InteractionError):
        Interaction(  # type: ignore[arg-type]
            type_tag="t", kind="not-a-kind", feature_ref=FEATURE
        )


def test_interaction_without_feature_is_rejected():
    with pytest.raises(InteractionError):
        make_interaction("t", "")  # AMR-05 / INT-04 — must engage a feature
    with pytest.raises(InteractionError):
        make_interaction("t", "   ")


def test_interaction_without_surface_is_rejected():
    with pytest.raises(InteractionError):
        make_interaction("t", FEATURE, surface_ref="")  # INT-03 / INT-C1


def test_interaction_without_data_is_rejected():
    with pytest.raises(InteractionError):
        make_interaction("t", FEATURE, data_ref="")  # AMR-14 / INT-06


def test_missing_state_or_behavior_reference_is_rejected():
    with pytest.raises(InteractionError):
        make_interaction("t", FEATURE, state_ref="")  # AMR-06 / AMK-05
    with pytest.raises(InteractionError):
        make_interaction("t", FEATURE, behavior_ref="")  # AMR-11 / UAL-10


def test_bad_state_is_rejected_fail_closed():
    with pytest.raises(InteractionError):
        Interaction(
            type_tag="t",
            kind=InteractionKind.INPUT,
            feature_ref=FEATURE,
            state="BAD",  # type: ignore[arg-type]
        )


def test_technology_bearing_surface_is_rejected_at_construction():
    # INT-03 / INT-C1 / UAL-11 — an abstract surface names no rendering technology.
    with pytest.raises(InteractionError):
        make_interaction("t", FEATURE, surface_ref="ENG-005:SURFACE:react.component")
    with pytest.raises(InteractionError):
        make_interaction("t", FEATURE, surface_ref="ENG-005:SURFACE:html.canvas")


def test_interaction_cannot_engage_its_own_binding_as_feature():
    # INT-C3 / AMK-03 founding acyclicity guard (non-absorption).
    with pytest.raises(InteractionError):
        make_interaction("t", SURFACE, surface_ref=SURFACE)
    with pytest.raises(InteractionError):
        make_interaction("t", DATA, data_ref=DATA)
    with pytest.raises(InteractionError):
        make_interaction("t", STATE, state_ref=STATE)
    with pytest.raises(InteractionError):
        make_interaction("t", BEHAVIOR, behavior_ref=BEHAVIOR)


def test_relationships_are_within_amr_closure():
    i = make_interaction("t", FEATURE)
    assert set(i.meta_relationships()) <= set(f"AMR-{n:02d}" for n in range(1, 15))  # V2
    assert i.meta_relationships() == ("AMR-05", "AMR-06", "AMR-10", "AMR-11", "AMR-14")
    assert i.meta_relationships() == INTERACTION_RELATIONSHIPS


def test_interaction_uses_engaged_through_and_presents_but_not_delivers_or_sequences():
    # The distinctive AMC-06 relationship set: uses AMR-05 (engaged-through, founding) +
    # AMR-14 (presents-data) + AMR-06 (holds-state) and does NOT use AMR-01 (delivers),
    # AMR-03 (groups), AMR-04 (sequenced-by), AMR-13 (consumes-operation), or AMR-07/12.
    rels = set(make_interaction("t", FEATURE).meta_relationships())
    assert {"AMR-05", "AMR-06", "AMR-14"} <= rels
    for absent in ("AMR-01", "AMR-02", "AMR-03", "AMR-04", "AMR-07", "AMR-12", "AMR-13"):
        assert absent not in rels


def test_all_interaction_kinds_construct_and_map_direction():
    assert make_interaction("t", FEATURE, kind=InteractionKind.INPUT).direction() == "input"
    assert make_interaction("t", FEATURE, kind=InteractionKind.COMMAND).direction() == "command"
    assert make_interaction("t", FEATURE, kind=InteractionKind.QUERY).direction() == "query"
    assert make_interaction("t", FEATURE, kind=InteractionKind.RESPONSE).direction() == "response"


def test_kind_class_reflects_direction():
    assert make_interaction("t", FEATURE, kind=InteractionKind.QUERY).kind_class() == "query"


def test_direction_is_decidable():
    assert make_interaction("t", FEATURE).direction_is_decidable() is True  # INT-07


def test_engages_and_engaged_feature():
    i = make_interaction("t", FEATURE)
    assert i.engaged_feature() == FEATURE  # AMR-05
    assert i.engages(FEATURE) is True
    assert i.engages("ENG-005:AMC-04:not-engaged") is False


def test_references_resolve_and_founding_acyclic():
    i = make_interaction("t", FEATURE)
    assert i.references_resolve() is True  # AOI-03 / AMK-05/07
    assert i.is_founding_acyclic() is True  # V4 / AMK-03 / INT-C3


def test_lifecycle_is_forward_only():
    i = make_interaction("t", FEATURE, state=InteractionState.DEFINED)
    composed = i.transition(InteractionState.COMPOSED)
    assert composed.state is InteractionState.COMPOSED
    ctx = composed.transition(InteractionState.CONTEXTUALIZED)
    assert ctx.state is InteractionState.CONTEXTUALIZED
    executable = ctx.transition(InteractionState.EXECUTABLE)
    assert executable.state is InteractionState.EXECUTABLE
    with pytest.raises(InteractionError):
        executable.transition(InteractionState.DEFINED)  # UAL-12 — no backward


def test_transition_to_same_state_is_allowed():
    i = make_interaction("t", FEATURE, state=InteractionState.COMPOSED)
    same = i.transition(InteractionState.COMPOSED)  # not backward (forward-or-equal)
    assert same.state is InteractionState.COMPOSED


def test_transition_rejects_non_state_target():
    i = make_interaction("t", FEATURE)
    with pytest.raises(InteractionError):
        i.transition("EXECUTABLE")  # type: ignore[arg-type]


def test_state_does_not_change_identity():
    a = make_interaction("t", FEATURE, state=InteractionState.DEFINED)
    b = make_interaction("t", FEATURE, state=InteractionState.COMPOSED)
    assert a.interaction_id == b.interaction_id  # identity is core-derived, not state


def test_non_constitutive_and_no_secret_no_technology():
    i = make_interaction("t", FEATURE)
    assert i.confers_authority() is False  # UAL-15 / INT-09 / C7
    assert i.redefines_foundation() is False  # UAL-02 / AMI-05
    assert i.selects_technology() is False  # UAL-11/15 (abstract references only)
    assert i.embeds_secret() is False


def test_technology_bearing_interaction_is_detected():
    # A technology marker in a non-surface ref is detected by selects_technology()
    # (the surface itself is rejected at construction; here the feature ref carries it).
    techy = make_interaction("t", "ENG-005:AMC-04:angular.module")
    assert techy.selects_technology() is True  # UAL-11/15 — concrete UI framework named


def test_secret_bearing_interaction_is_detected():
    leaky = make_interaction("t", "ENG-005:AMC-04:password-reset")
    assert leaky.embeds_secret() is True  # UAL-15 / RR-07


def test_interaction_to_dict_records_substrate_reuse():
    i = make_interaction("t", FEATURE, kind=InteractionKind.COMMAND)
    payload = i.to_dict()
    assert payload["substrate_refs"] == [
        "ENG-001",
        "ENG-002",
        "ENG-003",
        "ENG-004",
        "ENG-005",
        "RL-F2",
        "DF-2",
    ]
    assert payload["meta_class"] == "AMC-06"
    assert payload["kind"] == "Command-Interaction"
    assert payload["direction"] == "command"
    assert payload["surface_abstract"] is True
    assert payload["presents_data"] is True
    assert payload["holds_state"] is True
    assert payload["engages_feature"] is True
    assert payload["sole_engagement_point"] is True
    assert payload["feature_ref"] == FEATURE


def test_canonical_core_excludes_state_and_id():
    i = make_interaction("t", FEATURE)
    core = i.canonical_core()
    assert "state" not in core  # lifecycle is not identity-defining
    assert "interaction_id" not in core
    assert core["meta_class"] == "AMC-06"
    assert core["feature_ref"] == FEATURE
    assert core["direction"] == "input"


def test_interaction_type_is_the_realized_construct():
    assert isinstance(make_interaction("t", FEATURE), Interaction)
