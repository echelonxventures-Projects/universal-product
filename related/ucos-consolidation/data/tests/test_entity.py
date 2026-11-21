"""EC3-B10-U03 — Entity construct tests (DMC-02 + DEA-01…06 + UDL-07/03/04/12)."""

from __future__ import annotations

import pytest

from data.attribute import make_attribute
from data.datum import make_datum
from data.entity import (
    AttributeRef,
    Entity,
    EntityError,
    entity_ref_for,
    make_entity,
)
from data.entity_meta import (
    ENTITY_META_CLASS,
    ENTITY_RELATIONSHIPS,
    EntityKind,
    EntityState,
)

ENTITY_NAME = "ucos.demo.entity"


def _borne_attr(name="ucos.demo.attr", bearing=None):
    return make_attribute(
        name,
        "ucos.core.string",
        make_datum("ucos.core.string", f"value-of-{name}"),
        bearing if bearing is not None else entity_ref_for(ENTITY_NAME),
    )


def _entity(**overrides):
    name = overrides.get("name", ENTITY_NAME)
    # By default the borne attribute is bound to *this* entity's boundary (DEA-C2),
    # so a name override carries through to the borne attribute's bearing reference.
    attributes = overrides.pop("attributes", (_borne_attr(bearing=entity_ref_for(name)),))
    kwargs = dict(name=ENTITY_NAME, type_tag="ucos.core.entity")
    kwargs.update(overrides)
    return make_entity(
        kwargs.pop("name"),
        kwargs.pop("type_tag"),
        attributes,
        **kwargs,
    )


def test_entity_is_typed_named_identified_and_attribute_bearing():
    e = _entity()
    assert e.meta_class == ENTITY_META_CLASS  # V1 (DMC-02)
    assert e.name == ENTITY_NAME  # DEA-02 named
    assert e.type_tag == "ucos.core.entity"  # DEA-01 / UDL-03 typed
    assert e.entity_id.startswith("UCOS-ENTITY-")  # UDL-04 identified (ENG-001)
    assert e.attribute_count == 1  # DEA-03 bounded set
    assert e.kind is EntityKind.MASTER  # DXH-02 classified


def test_entity_bears_attributes_by_reference_not_owning():
    attr = _borne_attr()
    e = _entity(attributes=(attr,))
    assert e.borne_attribute_ids() == (attr.attribute_id,)  # DMR-01 bears the CERTIFIED Attribute
    assert e.absorbs_attributes() is False  # DEA-04 / DMX-02 — referenced, not owned
    ref_dict = e.attribute_refs[0].to_dict()
    assert ref_dict["owned"] is False
    assert ref_dict["absorbing"] is False


def test_attribute_ref_projects_only_identity_and_fingerprint():
    attr = _borne_attr()
    ref = AttributeRef.from_attribute(attr)
    assert ref.attribute_id == attr.attribute_id
    assert ref.structure_digest == attr.structure_digest
    assert ref.name == attr.name
    assert ref.type_tag == attr.type_tag
    assert ref.bearing_entity_ref == attr.bearing_entity_ref


def test_entity_identity_is_deterministic_and_structure_derived():
    a = _entity()
    b = _entity()
    c = _entity(
        name="different.entity",
        attributes=(_borne_attr(bearing=entity_ref_for("different.entity")),),
    )
    assert a.entity_id == b.entity_id  # same structure → same ENG-001 identity
    assert a.entity_id != c.entity_id  # different name/structure → different identity


def test_entity_is_immutable_objecthood():
    e = _entity()
    with pytest.raises((AttributeError, TypeError)):
        e.name = "other"  # frozen object (ENG-002 objecthood)


def test_unnamed_entity_is_rejected_fail_closed():
    with pytest.raises(EntityError):
        _entity(name="")  # DEA-02 — no unnamed entity
    with pytest.raises(EntityError):
        _entity(name="   ")


def test_untyped_entity_is_rejected_fail_closed():
    with pytest.raises(EntityError):
        _entity(type_tag="")  # DEA-01 / UDL-03 — no untyped entity


def test_entity_with_no_attributes_is_rejected_fail_closed():
    with pytest.raises(EntityError):
        _entity(attributes=())  # DEA-03 / DEA-04 / UDL-07 — must bear a bounded set


def test_entity_boundary_rejects_foreign_attribute():
    # DEA-C2 — an attribute borne by another entity cannot be in this entity's boundary.
    foreign = _borne_attr(bearing=entity_ref_for("some.other.entity"))
    with pytest.raises(EntityError):
        _entity(attributes=(foreign,))


def test_entity_rejects_duplicate_attribute_member():
    # DEA-C1 — membership is decidable: no duplicate attribute names.
    a1 = _borne_attr(name="dup")
    a2 = _borne_attr(name="dup")
    with pytest.raises(EntityError):
        _entity(attributes=(a1, a2))


def test_entity_bears_must_be_a_certified_attribute_reference():
    with pytest.raises(EntityError):
        AttributeRef.from_attribute(object())  # DMR-01 — bears a data.attribute.Attribute


def test_relationships_are_within_dmr_closure():
    e = _entity()
    assert set(e.meta_relationships()) <= set(ENTITY_RELATIONSHIPS)  # V2
    assert e.meta_relationships() == ("DMR-01", "DMR-04", "DMR-10")


def test_lifecycle_is_forward_only():
    e = _entity(state=EntityState.DEFINED)
    active = e.transition(EntityState.ACTIVE)
    assert active.state is EntityState.ACTIVE
    with pytest.raises(EntityError):
        active.transition(EntityState.DEFINED)  # UDL-12 — no backward transition


def test_boundedness_predicate():
    e = _entity()
    assert e.is_bounded() is True  # DEA-03 / UDL-07 — explicit, decidable, non-empty


def test_founding_graph_is_acyclic():
    e = _entity()
    assert e.is_founding_acyclic() is True  # V4 / DMK-03 / UDL-09 / DEA-C3


def test_schema_reference_is_optional_and_recorded():
    e = _entity(schema_ref="UCOS-SCHEMA-REF:ucos.demo.schema")  # DMR-04 deferred reference
    assert e.is_schema_described() is True
    assert e.schema_ref == "UCOS-SCHEMA-REF:ucos.demo.schema"
    assert _entity().is_schema_described() is False


def test_non_constitutive_and_no_secret():
    e = _entity()
    assert e.confers_authority() is False  # UDL-15 / DEA-09 / C7
    assert e.redefines_el1() is False  # UDL-02 / DMI-05
    assert e.selects_technology() is False  # UDL-11 / DEA-K5
    assert e.embeds_secret() is False


def test_secret_bearing_entity_is_detected():
    leaky = _entity(name="password")
    assert leaky.embeds_secret() is True  # UDL-15 / RR-07


def test_entity_to_dict_records_substrate_reuse():
    e = _entity()
    payload = e.to_dict()
    assert payload["substrate_refs"] == ["ENG-001", "ENG-002", "ENG-004", "ENG-005"]
    assert payload["meta_class"] == "DMC-02"
    assert payload["absorbs_attributes"] is False
    assert payload["bounded"] is True


def test_entity_type_is_the_realized_construct():
    assert isinstance(_entity(), Entity)


def test_multi_attribute_entity_is_bounded():
    a1 = _borne_attr(name="ucos.demo.attr.one")
    a2 = _borne_attr(name="ucos.demo.attr.two")
    e = _entity(attributes=(a1, a2))
    assert e.attribute_count == 2
    assert e.is_bounded() is True
    assert set(e.borne_attribute_ids()) == {a1.attribute_id, a2.attribute_id}


# --------------------------------------------------------------------------------------
# Every constructor guard, shown refusing (see data/tests/test_schema.py for the argument).
# --------------------------------------------------------------------------------------

from engine.tests import assert_every_guard_can_refuse  # noqa: E402


def test_every_attribute_ref_guard_can_refuse():
    assert_every_guard_can_refuse(_entity().attribute_refs[0])


def test_every_entity_guard_can_refuse():
    assert_every_guard_can_refuse(_entity())


def test_entity_transition_refuses_a_state_that_is_not_a_lifecycle_member() -> None:
    """UDL-12 for the entity class: a string that names a state is not one."""

    entity = make_entity("ENT-T-01", "TYPE", state=EntityState.ACTIVE)
    with pytest.raises(EntityError, match="DOS-01…05 state"):
        entity.transition("ACTIVE")  # type: ignore[arg-type]


def test_entity_transition_refuses_a_state_that_is_not_a_lifecycle_member() -> None:
    """UDL-12 for the entity: a mistyped target is refused before any ordering question."""
    entity = _entity(state=EntityState.ACTIVE)
    with pytest.raises(EntityError, match="DOS-01…05 state"):
        entity.transition("ACTIVE")  # type: ignore[arg-type]
