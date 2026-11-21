"""EC3-B12-U08 — Composition construct tests (AMC-08 + AMK-01/02/03/05/06/08 + UAL-09)."""

from __future__ import annotations

import pytest

from application.composition import (
    Composition,
    CompositionError,
    has_cycle,
    make_composition,
)
from application.composition_meta import (
    COMPOSITION_META_CLASS,
    COMPOSITION_RELATIONSHIPS,
    CompositionKind,
    CompositionState,
)

MEMBERS = (
    "ENG-005:AMC-03:ucos.demo.module.a",
    "ENG-005:AMC-03:ucos.demo.module.b",
)
ASSEMBLED = "ENG-005:AMC-01:ucos.demo.application"
PLATFORM = "ENG-005:PL-F2:PLATFORM-009.composition"
BEHAVIOR = "ENG-005:RL-F2:runtime.composition-emit"


def test_composition_is_typed_identified_assembling_and_founding_acyclic():
    c = make_composition("ucos.demo.composition", MEMBERS, assembled_ref=ASSEMBLED)
    assert c.meta_class == COMPOSITION_META_CLASS  # V1 (AMC-08)
    assert c.type_tag == "ucos.demo.composition"  # UAL-03 / CMP-01 typed
    assert c.composition_id.startswith("UCOS-COMPOSITION-")  # UAL-04 identified (ENG-001)
    assert len(c.value_digest) == 64  # ENG-003 value fidelity
    assert c.kind is CompositionKind.MODULE_INTO_APPLICATION  # AXH-08 classified (default)
    assert c.facet() == "module-into-application"  # AXH-08 facet
    assert c.assembles_members() is True  # AMR-07 defining
    assert c.assembled_member_count() == 2
    assert c.is_founding_acyclic() is True  # V4 / AMK-03 / UAL-09 (governing, material)
    assert c.participates_in_founding_edge() is True  # founding kind
    assert c.preserves_boundaries() is True  # CMP-06 / CMP-C3
    assert c.binds_platform_composition() is True  # AMR-12 / CMP-C5
    assert c.binds_runtime_event() is True  # §7 / AMK-05


def test_composition_identity_is_deterministic_and_core_derived():
    a = make_composition("t", MEMBERS, assembled_ref=ASSEMBLED)
    b = make_composition("t", tuple(reversed(MEMBERS)), assembled_ref=ASSEMBLED)
    c = make_composition("t", MEMBERS, assembled_ref="ENG-005:AMC-01:ucos.other.app")
    assert a.composition_id == b.composition_id  # member order is not identity-defining
    assert a.composition_id != c.composition_id  # different assembled whole → different id


def test_kind_is_identity_defining_across_kinds():
    a = make_composition("t", MEMBERS, kind=CompositionKind.MODULE_INTO_APPLICATION,
                         assembled_ref=ASSEMBLED)
    b = make_composition("t", MEMBERS, kind=CompositionKind.APPLICATION_FEDERATION,
                         assembled_ref=ASSEMBLED)
    assert a.composition_id != b.composition_id  # kind/facet is part of identity


def test_composition_is_immutable_objecthood():
    c = make_composition("t", MEMBERS, assembled_ref=ASSEMBLED)
    with pytest.raises((AttributeError, TypeError)):
        c.type_tag = "other"  # frozen object (ENG-002 objecthood)


def test_untyped_composition_is_rejected_fail_closed():
    with pytest.raises(CompositionError):
        make_composition("", MEMBERS, assembled_ref=ASSEMBLED)  # UAL-03 / CMP-01
    with pytest.raises(CompositionError):
        make_composition("   ", MEMBERS, assembled_ref=ASSEMBLED)


def test_non_string_type_tag_is_rejected():
    with pytest.raises(CompositionError):
        Composition(  # type: ignore[arg-type]
            type_tag=object(),
            kind=CompositionKind.MODULE_INTO_APPLICATION,
            member_refs=MEMBERS,
        )


def test_bad_kind_is_rejected_fail_closed():
    with pytest.raises(CompositionError):
        Composition(  # type: ignore[arg-type]
            type_tag="t", kind="not-a-kind", member_refs=MEMBERS
        )


def test_member_refs_must_be_a_tuple():
    with pytest.raises(CompositionError):
        Composition(  # type: ignore[arg-type]
            type_tag="t",
            kind=CompositionKind.MODULE_INTO_APPLICATION,
            member_refs=["not", "a", "tuple"],
        )


def test_empty_member_is_rejected():
    with pytest.raises(CompositionError):
        make_composition("t", ("",), assembled_ref=ASSEMBLED)  # CMP-K2
    with pytest.raises(CompositionError):
        make_composition("t", ("   ",), assembled_ref=ASSEMBLED)


def test_founding_kind_requires_at_least_one_member():
    with pytest.raises(CompositionError):
        make_composition("t", (), assembled_ref=ASSEMBLED)  # CMP-C4 topology (≥1)


def test_federation_requires_at_least_two_peers():
    # CMP-C4 — a federation composes ≥2 peer applications.
    with pytest.raises(CompositionError):
        make_composition(
            "t",
            ("ENG-005:AMC-01:ucos.demo.app.only",),
            kind=CompositionKind.APPLICATION_FEDERATION,
            assembled_ref="ENG-005:AMC-01:ucos.demo.federation",
        )


def test_duplicate_members_are_rejected_partition():
    dup = ("ENG-005:AMC-03:ucos.demo.module.a", "ENG-005:AMC-03:ucos.demo.module.a")
    with pytest.raises(CompositionError):
        make_composition("t", dup, assembled_ref=ASSEMBLED)  # CMP-C3 / CMP-06


def test_missing_assembled_reference_is_rejected():
    with pytest.raises(CompositionError):
        make_composition("t", MEMBERS, assembled_ref="")  # AMR-07
    with pytest.raises(CompositionError):
        make_composition("t", MEMBERS, assembled_ref="   ")


def test_missing_composition_reference_is_rejected():
    with pytest.raises(CompositionError):
        make_composition("t", MEMBERS, assembled_ref=ASSEMBLED, composition_ref="")  # AMR-12


def test_missing_behavior_reference_is_rejected():
    with pytest.raises(CompositionError):
        make_composition("t", MEMBERS, assembled_ref=ASSEMBLED, behavior_ref="")  # §7 / UAL-10


def test_bad_lifecycle_state_is_rejected_fail_closed():
    with pytest.raises(CompositionError):
        Composition(
            type_tag="t",
            kind=CompositionKind.MODULE_INTO_APPLICATION,
            member_refs=MEMBERS,
            state="BAD",  # type: ignore[arg-type]
        )


def test_self_founding_is_rejected_non_absorption():
    # CMP-C1 / CMP-C3 — the assembled whole cannot be one of its own constituents.
    with pytest.raises(CompositionError):
        make_composition("t", (ASSEMBLED, MEMBERS[0]), assembled_ref=ASSEMBLED)


def test_relationships_are_within_amr_closure():
    c = make_composition("t", MEMBERS, assembled_ref=ASSEMBLED)
    assert set(c.meta_relationships()) <= {f"AMR-{n:02d}" for n in range(1, 15)}  # V2
    assert c.meta_relationships() == ("AMR-02", "AMR-03", "AMR-07", "AMR-10", "AMR-12")
    assert c.meta_relationships() == COMPOSITION_RELATIONSHIPS


def test_composition_uses_assembly_relationships_but_not_deliver_hold_consume_present():
    # AMC-08 relationship set: uses AMR-02/03/07 (assembly) + AMR-10 (id) + AMR-12
    # (composed-as) and does NOT use AMR-01 (delivers), AMR-04 (sequenced-by), AMR-05
    # (engaged-through), AMR-06 (holds-state), AMR-13 (consumes-operation), AMR-14
    # (presents-data).
    rels = set(make_composition("t", MEMBERS, assembled_ref=ASSEMBLED).meta_relationships())
    assert {"AMR-02", "AMR-03", "AMR-07", "AMR-12"} <= rels
    for absent in ("AMR-01", "AMR-04", "AMR-05", "AMR-06", "AMR-08", "AMR-09", "AMR-13", "AMR-14"):
        assert absent not in rels


# -- founding-acyclic material graph (AMK-03 / CMP-C1 / UAL-09) --------------------


def test_has_cycle_detects_acyclic_graph():
    assert has_cycle((("a", "b"), ("b", "c"))) is False  # a→b→c is a DAG


def test_has_cycle_detects_back_edge():
    assert has_cycle((("a", "b"), ("b", "a"))) is True  # a→b→a is a cycle


def test_has_cycle_detects_self_loop():
    assert has_cycle((("a", "a"),)) is True  # self-founding is a cycle


def test_has_cycle_on_empty_graph_is_false():
    assert has_cycle(()) is False  # empty founding graph (federation) is acyclic


def test_founding_edges_point_members_to_assembled():
    c = make_composition("t", MEMBERS, kind=CompositionKind.FEATURE_INTO_MODULE,
                         assembled_ref="ENG-005:AMC-03:ucos.demo.module.whole")
    edges = c.founding_edges()
    assert len(edges) == 2
    for src, dst in edges:
        assert src in MEMBERS
        assert dst == "ENG-005:AMC-03:ucos.demo.module.whole"
    assert c.founding_relationship() == "AMR-03"  # Feature-into-Module reuses groups


def test_module_into_application_founding_relationship_is_composed_of():
    c = make_composition("t", MEMBERS, assembled_ref=ASSEMBLED)
    assert c.founding_relationship() == "AMR-02"  # Module-into-Application reuses composed-of


# -- federation (peer, non-founding) ----------------------------------------------


def test_federation_is_peer_non_founding_and_acyclic():
    peers = (
        "ENG-005:AMC-01:ucos.demo.app.alpha",
        "ENG-005:AMC-01:ucos.demo.app.beta",
    )
    fed = make_composition(
        "t", peers, kind=CompositionKind.APPLICATION_FEDERATION,
        assembled_ref="ENG-005:AMC-01:ucos.demo.federation",
    )
    assert fed.is_federation() is True  # CMP-07
    assert fed.participates_in_founding_edge() is False  # peer, non-founding
    assert fed.founding_edges() == ()  # empty founding graph
    assert fed.is_founding_acyclic() is True  # vacuously acyclic
    assert fed.founding_relationship() == "AMR-07"  # assembled-by (reference-only)
    assert fed.federation_is_by_reference() is True  # CMP-C4 (≥2, by reference)


def test_founding_kind_is_not_a_federation():
    c = make_composition("t", MEMBERS, assembled_ref=ASSEMBLED)
    assert c.is_federation() is False
    assert c.federation_is_by_reference() is True  # vacuously true for non-federations


# -- reference / membership accessors ---------------------------------------------


def test_assembled_by_and_assembles():
    c = make_composition("t", MEMBERS, assembled_ref=ASSEMBLED)
    assert c.assembled_by() == ASSEMBLED  # AMR-07
    assert c.assembles(MEMBERS[0]) is True
    assert c.assembles("ENG-005:AMC-03:not-a-member") is False


def test_references_resolve_and_no_new_connection():
    c = make_composition("t", MEMBERS, assembled_ref=ASSEMBLED)
    assert c.references_resolve() is True  # AOI-03 / AMK-05/06
    assert c.uses_new_connection_construct() is False  # CMP-04 / CMP-C2 (all ENG-005 refs)
    assert c.members_are_partition() is True


# -- lifecycle (UAL-12, forward-only) ---------------------------------------------


def test_lifecycle_is_forward_only():
    c = make_composition("t", MEMBERS, assembled_ref=ASSEMBLED, state=CompositionState.DEFINED)
    composed = c.transition(CompositionState.COMPOSED)
    assert composed.state is CompositionState.COMPOSED
    ctx = composed.transition(CompositionState.CONTEXTUALIZED)
    executable = ctx.transition(CompositionState.EXECUTABLE)
    assert executable.state is CompositionState.EXECUTABLE
    with pytest.raises(CompositionError):
        executable.transition(CompositionState.DEFINED)  # UAL-12 — no backward


def test_transition_to_same_state_is_allowed():
    c = make_composition("t", MEMBERS, assembled_ref=ASSEMBLED, state=CompositionState.COMPOSED)
    same = c.transition(CompositionState.COMPOSED)  # forward-or-equal
    assert same.state is CompositionState.COMPOSED


def test_transition_rejects_non_state_target():
    c = make_composition("t", MEMBERS, assembled_ref=ASSEMBLED)
    with pytest.raises(CompositionError):
        c.transition("EXECUTABLE")  # type: ignore[arg-type]


def test_composition_does_not_change_identity_across_lifecycle():
    a = make_composition("t", MEMBERS, assembled_ref=ASSEMBLED, state=CompositionState.DEFINED)
    b = make_composition("t", MEMBERS, assembled_ref=ASSEMBLED, state=CompositionState.COMPOSED)
    assert a.composition_id == b.composition_id  # identity is core-derived, not lifecycle


# -- non-constitutiveness (UAL-15 / CMP-09) ---------------------------------------


def test_non_constitutive_and_no_secret_no_technology():
    c = make_composition("t", MEMBERS, assembled_ref=ASSEMBLED)
    assert c.confers_authority() is False  # UAL-15 / CMP-09 / C7
    assert c.redefines_foundation() is False  # UAL-02 / AMI-05
    assert c.selects_technology() is False  # UAL-15 (abstract references only)
    assert c.embeds_secret() is False


def test_technology_bearing_composition_is_detected():
    techy = make_composition("t", ("ENG-005:AMC-03:webpack.bundle", MEMBERS[1]),
                             assembled_ref=ASSEMBLED)
    assert techy.selects_technology() is True  # UAL-15 / CMP-09 — bundler named


def test_secret_bearing_composition_is_detected():
    leaky = make_composition("t", ("ENG-005:AMC-03:api_key-module", MEMBERS[1]),
                             assembled_ref=ASSEMBLED)
    assert leaky.embeds_secret() is True  # UAL-15 / RR-07


def test_composition_to_dict_records_substrate_reuse():
    c = make_composition("t", MEMBERS, assembled_ref=ASSEMBLED)
    payload = c.to_dict()
    assert payload["substrate_refs"] == [
        "ENG-001",
        "ENG-002",
        "ENG-003",
        "ENG-004",
        "ENG-005",
        "RL-F2",
        "PL-F2",
    ]
    assert payload["meta_class"] == "AMC-08"
    assert payload["kind"] == "Module-into-Application"
    assert payload["facet"] == "module-into-application"
    assert payload["is_founding"] is True
    assert payload["is_federation"] is False
    assert payload["founding_acyclic"] is True
    assert payload["preserves_boundaries"] is True
    assert payload["binds_platform_composition"] is True
    assert payload["binds_runtime_event"] is True
    assert payload["assembled_member_count"] == 2
    assert payload["founding_relationship"] == "AMR-02"


def test_canonical_core_excludes_lifecycle_and_id():
    c = make_composition("t", MEMBERS, assembled_ref=ASSEMBLED)
    core = c.canonical_core()
    assert "state" not in core  # lifecycle is not identity-defining
    assert "composition_id" not in core
    assert core["meta_class"] == "AMC-08"
    assert core["assembled_ref"] == ASSEMBLED
    assert core["facet"] == "module-into-application"


def test_composition_type_is_the_realized_construct():
    assert isinstance(make_composition("t", MEMBERS, assembled_ref=ASSEMBLED), Composition)
