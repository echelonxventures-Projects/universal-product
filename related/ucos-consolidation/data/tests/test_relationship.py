"""EC3-B10-U10 — Relationship construct tests (DMC-04 + DRA-01…10 + UDL-09/03/04)."""

from __future__ import annotations

import pytest

from data.attribute import make_attribute
from data.datum import make_datum
from data.entity import entity_ref_for, make_entity
from data.relationship import (
    ENDPOINT_META_CLASS,
    POLICY_REF_PREFIX,
    EntityEndpointRef,
    RelationshipError,
    RelationshipObject,
    make_relationship,
    policy_ref_for,
)
from data.relationship_meta import (
    DIRECTION_FOR_KIND,
    RELATIONSHIP_META_CLASS,
    RELATIONSHIP_RELATIONSHIPS,
    RelationshipCardinality,
    RelationshipDirection,
    RelationshipKind,
    RelationshipState,
    RelationshipVerdict,
)

SOURCE_NAME = "ucos.demo.source"
TARGET_NAME = "ucos.demo.target"
REL_NAME = "ucos.demo.relationship"
POLICY_REF = policy_ref_for("relationship.navigation")


def _entity(name):
    attr = make_attribute(
        f"{name}.attr",
        "ucos.core.string",
        make_datum("ucos.core.string", "hello"),
        entity_ref_for(name),
    )
    return make_entity(name, "ucos.core.entity", (attr,))


def _relationship(**overrides):
    source = overrides.pop("source", None) or _entity(SOURCE_NAME)
    target = overrides.pop("target", None) or _entity(TARGET_NAME)
    kwargs = dict(
        kind=overrides.pop("kind", RelationshipKind.ASSOCIATION),
        cardinality=overrides.pop("cardinality", RelationshipCardinality.MANY_TO_MANY),
    )
    kwargs.update(overrides)
    policy_ref = kwargs.pop("policy_ref", POLICY_REF)
    name = kwargs.pop("name", REL_NAME)
    type_tag = kwargs.pop("type_tag", "ucos.core.relationship")
    return make_relationship(name, type_tag, source, target, policy_ref, **kwargs)


# ---------------------------------------------------------------------------
# Identity / typing / classification
# ---------------------------------------------------------------------------


def test_relationship_is_typed_named_identified_and_classified():
    r = _relationship()
    assert r.meta_class == RELATIONSHIP_META_CLASS  # V1 (DMC-04)
    assert r.name == REL_NAME
    assert r.type_tag == "ucos.core.relationship"  # UDL-03 typed
    assert r.relationship_id.startswith("UCOS-RELATIONSHIP-")  # UDL-04 identified (ENG-001)
    assert r.kind is RelationshipKind.ASSOCIATION  # DXH-04 classified
    assert r.is_typed() is True
    assert r.meta_relationships() == RELATIONSHIP_RELATIONSHIPS


def test_relationship_is_an_eng005_reference():
    r = _relationship()
    assert r.is_by_reference() is True  # DRA-01 / UDL-09
    assert r.redefines_el1() is False  # UDL-02


def test_relationship_id_is_deterministic():
    assert _relationship().relationship_id == _relationship().relationship_id


# ---------------------------------------------------------------------------
# Endpoints (DMR-03) + referential integrity (DRA-05)
# ---------------------------------------------------------------------------


def test_relationship_relates_two_certified_entities_by_reference():
    source, target = _entity(SOURCE_NAME), _entity(TARGET_NAME)
    r = _relationship(source=source, target=target)
    assert r.source_id() == source.entity_id  # DMR-03 relates
    assert r.target_id() == target.entity_id
    assert r.endpoint_ids() == (source.entity_id, target.entity_id)
    assert r.relates_entities(target.entity_id, source.entity_id) is True  # unordered
    assert r.relates_entities("x", "y") is False
    assert r.absorbs_endpoints() is False  # DRA-C5 / DMX-02 — referenced, not owned
    assert r.endpoints_resolve() is True  # DRA-05
    assert r.endpoints_distinct() is True


def test_endpoint_ref_from_entity_requires_entity():
    with pytest.raises(RelationshipError):  # DMR-03
        EntityEndpointRef.from_entity(object())


def test_endpoint_ref_to_dict_and_resolves():
    ref = EntityEndpointRef.from_entity(_entity(SOURCE_NAME))
    d = ref.to_dict()
    assert d["binding"] == "DMR-03:relates"
    assert d["owned"] is False and d["absorbing"] is False
    assert d["resolves"] is True


@pytest.mark.parametrize(
    "ref",
    [
        EntityEndpointRef("not-ucos", "a" * 64, "n", "t", ENDPOINT_META_CLASS),  # bad id prefix
        EntityEndpointRef("UCOS-ENTITY-x", "short", "n", "t", ENDPOINT_META_CLASS),  # bad digest
        EntityEndpointRef("UCOS-ENTITY-x", "z" * 64, "n", "t", ENDPOINT_META_CLASS),  # non-hex
        EntityEndpointRef("UCOS-ENTITY-x", "a" * 64, "n", "t", "DMC-99"),  # wrong meta-class
    ],
)
def test_endpoint_ref_does_not_resolve(ref):
    assert ref.resolves() is False  # DRA-05 / DRA-C2


# ---------------------------------------------------------------------------
# Cardinality (DRA-04) + directionality (DRA-06)
# ---------------------------------------------------------------------------


def test_relationship_declares_explicit_cardinality():
    r = _relationship(cardinality=RelationshipCardinality.ONE_TO_MANY)
    assert r.cardinality is RelationshipCardinality.ONE_TO_MANY
    assert r.cardinality_explicit() is True  # DRA-04 / DRA-C3


def test_relationship_directionality_declared_consistently():
    r = _relationship()  # Association → PEER
    assert r.is_peer() is True
    assert r.direction is RelationshipDirection.PEER
    assert r.directionality_declared() is True  # DRA-06


def test_association_direction_defaults_to_peer():
    r = make_relationship(
        REL_NAME, "ucos.core.relationship", _entity(SOURCE_NAME), _entity(TARGET_NAME), POLICY_REF
    )
    assert r.direction is DIRECTION_FOR_KIND[RelationshipKind.ASSOCIATION]


# ---------------------------------------------------------------------------
# Founding / acyclicity (DRA-03)
# ---------------------------------------------------------------------------


def test_composition_is_founding_and_acyclic_between_distinct_entities():
    r = _relationship(kind=RelationshipKind.COMPOSITION, direction=RelationshipDirection.DIRECTED)
    assert r.is_founding() is True  # DRA-03
    assert r.is_peer() is False
    assert r.founding_acyclic_rule() is True  # founding + distinct endpoints
    assert r.is_founding_acyclic() is True  # V4 / DMK-03


def test_reference_kind_is_directed_and_non_founding():
    r = _relationship(kind=RelationshipKind.REFERENCE, direction=RelationshipDirection.DIRECTED)
    assert r.is_founding() is False
    assert r.founding_acyclic_rule() is True  # non-founding path (DRA-C4)


def test_association_founding_acyclic_rule_is_non_founding_path():
    r = _relationship()  # Association, non-founding
    assert r.is_founding() is False
    assert r.founding_acyclic_rule() is True


# ---------------------------------------------------------------------------
# Behavior binding (DMR-11 / §7)
# ---------------------------------------------------------------------------


def test_relationship_binds_navigation_by_reference():
    r = _relationship()
    assert r.binds_policy_by_reference() is True  # DMR-11 / §7 / DRA-K3
    assert r.policy_ref.startswith(f"{POLICY_REF_PREFIX}:")
    assert r.navigates_by_reference() is True
    assert r.enforces() is False  # UDL-09 / DRA-09 — enacts nothing
    assert r.is_recorded() is True  # DOV-08


# ---------------------------------------------------------------------------
# Schema description (DRA-07 / DMR-04)
# ---------------------------------------------------------------------------


def test_relationship_schema_describable_reference_obligation():
    assert _relationship().is_schema_describable() is False  # optional, empty by default
    r = _relationship(schema_ref="UCOS-SCHEMA-REF:relationship")
    assert r.is_schema_describable() is True  # DRA-07
    assert r.is_founding_acyclic() is True  # schema_ref recorded but acyclic


# ---------------------------------------------------------------------------
# Non-constitutiveness (UDL-09/15 / DRA-09)
# ---------------------------------------------------------------------------


def test_relationship_confers_no_authority_selects_no_technology():
    r = _relationship()
    assert r.confers_authority() is False  # DRA-09
    assert r.names_technology() is False  # UDL-09/11 / DRA-K5
    assert r.selects_technology() is False
    assert r.embeds_secret() is False


def test_relationship_embeds_secret_detected():
    r = _relationship(name="ucos.demo.password.relationship")  # secret marker in canonical core
    assert r.embeds_secret() is True  # UDL-15 / RR-07


# ---------------------------------------------------------------------------
# Serialization
# ---------------------------------------------------------------------------


def test_relationship_to_dict_is_complete_and_deterministic():
    r = _relationship()
    d = r.to_dict()
    assert d["relationship_id"] == r.relationship_id
    assert d["meta_class"] == RELATIONSHIP_META_CLASS
    assert d["kind"] == "Association"
    assert d["cardinality"] == "N:M"
    assert d["direction"] == "peer"
    assert d["by_reference"] is True
    assert d["endpoints_resolve"] is True
    assert d["founding"] is False
    assert d["source_ref"]["binding"] == "DMR-03:relates"
    assert d["substrate_refs"] == ["ENG-001", "ENG-002", "ENG-004", "ENG-005"]


# ---------------------------------------------------------------------------
# Lifecycle (UDL-12, forward-only)
# ---------------------------------------------------------------------------


def test_relationship_lifecycle_is_forward_only():
    r = _relationship()
    active = r.transition(RelationshipState.ACTIVE)
    assert active.state is RelationshipState.ACTIVE
    with pytest.raises(RelationshipError):  # UDL-12 — no backward transition
        active.transition(RelationshipState.DEFINED)


def test_relationship_transition_rejects_non_state():
    with pytest.raises(RelationshipError):
        _relationship().transition("ACTIVE")


# ---------------------------------------------------------------------------
# Fail-closed construction (DRA-K1…K5 / DRA-C1…C3 / DRA-06)
# ---------------------------------------------------------------------------


def test_rejects_empty_name():
    with pytest.raises(RelationshipError):
        _relationship(name="  ")


def test_rejects_empty_type_tag():
    with pytest.raises(RelationshipError):
        _relationship(type_tag="")


def test_rejects_bad_kind():
    with pytest.raises(RelationshipError):
        _relationship(kind="Association")


def test_rejects_source_not_endpoint_ref():
    with pytest.raises(RelationshipError):  # source endpoint relates a CERTIFIED entity
        RelationshipObject(
            name=REL_NAME,
            type_tag="ucos.core.relationship",
            kind=RelationshipKind.ASSOCIATION,
            source_ref=object(),  # type: ignore[arg-type]
            target_ref=EntityEndpointRef.from_entity(_entity(TARGET_NAME)),
            cardinality=RelationshipCardinality.MANY_TO_MANY,
            direction=RelationshipDirection.PEER,
            policy_ref=POLICY_REF,
        )


def test_rejects_target_not_endpoint_ref():
    with pytest.raises(RelationshipError):
        RelationshipObject(
            name=REL_NAME,
            type_tag="ucos.core.relationship",
            kind=RelationshipKind.ASSOCIATION,
            source_ref=EntityEndpointRef.from_entity(_entity(SOURCE_NAME)),
            target_ref=object(),  # type: ignore[arg-type]
            cardinality=RelationshipCardinality.MANY_TO_MANY,
            direction=RelationshipDirection.PEER,
            policy_ref=POLICY_REF,
        )


def test_rejects_unresolved_source_endpoint():
    bad = EntityEndpointRef("not-ucos", "a" * 64, "n", "t", ENDPOINT_META_CLASS)
    with pytest.raises(RelationshipError):  # DRA-05 / DRA-C2
        make_relationship(REL_NAME, "ucos.core.relationship", bad, _entity(TARGET_NAME), POLICY_REF)


def test_rejects_unresolved_target_endpoint():
    bad = EntityEndpointRef("UCOS-ENTITY-x", "a" * 64, "n", "t", "DMC-99")
    with pytest.raises(RelationshipError):  # DRA-05 / DRA-C2 — target checked after source
        make_relationship(REL_NAME, "ucos.core.relationship", _entity(SOURCE_NAME), bad, POLICY_REF)


def test_rejects_bad_cardinality():
    with pytest.raises(RelationshipError):  # DRA-04 / DRA-C3
        _relationship(cardinality="N:M")


def test_rejects_bad_direction_type():
    with pytest.raises(RelationshipError):  # DRA-06
        _relationship(direction="peer")


def test_rejects_direction_inconsistent_with_kind():
    with pytest.raises(RelationshipError):  # DRA-06 — Association must be peer
        _relationship(kind=RelationshipKind.ASSOCIATION, direction=RelationshipDirection.DIRECTED)


def test_rejects_founding_self_relation():
    same = _entity(SOURCE_NAME)
    with pytest.raises(RelationshipError):  # DRA-03 / DRA-C1 — no self-founding
        make_relationship(
            REL_NAME,
            "ucos.core.relationship",
            same,
            same,
            POLICY_REF,
            kind=RelationshipKind.COMPOSITION,
            direction=RelationshipDirection.DIRECTED,
        )


def test_peer_association_permits_self_relation_non_founding():
    same = _entity(SOURCE_NAME)
    r = make_relationship(REL_NAME, "ucos.core.relationship", same, same, POLICY_REF)
    assert r.endpoints_distinct() is False  # DRA-C4 — peer may relate same (non-founding)
    assert r.founding_acyclic_rule() is True


def test_rejects_bad_policy_ref():
    with pytest.raises(RelationshipError):  # DMR-11 / DRA-K3
        _relationship(policy_ref="navigation")


def test_rejects_bad_verdict():
    with pytest.raises(RelationshipError):  # DOV-08
        _relationship(verdict="pass")


def test_rejects_bad_state():
    with pytest.raises(RelationshipError):  # UDL-12
        _relationship(state="DEFINED")


def test_rejects_empty_version():
    with pytest.raises(RelationshipError):  # DRA-08
        _relationship(version=" ")


def test_rejects_bad_supersedes():
    with pytest.raises(RelationshipError):  # DRA-08
        _relationship(supersedes=123)


def test_rejects_bad_schema_ref():
    with pytest.raises(RelationshipError):  # DRA-07 / DMR-04
        _relationship(schema_ref=123)


def test_rejects_technology_marker():
    with pytest.raises(RelationshipError):  # UDL-09 / DRA-K5 — names a join/foreign-key tech
        _relationship(type_tag="ucos.core.sql.join")


def test_verdict_and_supersedes_recorded():
    r = _relationship(verdict=RelationshipVerdict.PASS, supersedes="UCOS-RELATIONSHIP-old")
    assert r.verdict is RelationshipVerdict.PASS
    assert r.supersedes == "UCOS-RELATIONSHIP-old"
