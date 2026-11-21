"""EC3-B10-U04 — Schema construct tests (DMC-05 + DSA-01…10 + UDL-10/03/04/12)."""

from __future__ import annotations

import pytest

from data.attribute import make_attribute
from data.datum import make_datum
from data.entity import entity_ref_for, make_entity
from data.schema import (
    DescribedRef,
    Schema,
    SchemaElement,
    SchemaError,
    element,
    entity_schema_for,
    make_schema,
    schema_ref_for,
)
from data.schema_meta import (
    SCHEMA_META_CLASS,
    SCHEMA_RELATIONSHIPS,
    SchemaKind,
    SchemaState,
)

ENTITY_NAME = "ucos.demo.entity"
SCHEMA_NAME = "ucos.demo.schema"


def _entity(name=ENTITY_NAME, attr_name="ucos.demo.attr", attr_type="ucos.core.string"):
    attr = make_attribute(
        attr_name,
        attr_type,
        make_datum(attr_type, f"value-of-{attr_name}"),
        entity_ref_for(name),
    )
    return make_entity(name, "ucos.core.entity", (attr,))


def _schema(**overrides):
    entity = overrides.pop("entity", _entity())
    return entity_schema_for(
        entity,
        name=overrides.pop("name", SCHEMA_NAME),
        type_tag=overrides.pop("type_tag", "ucos.core.schema"),
        **overrides,
    )


def test_schema_is_typed_named_identified_and_explicit():
    s = _schema()
    assert s.meta_class == SCHEMA_META_CLASS  # V1 (DMC-05)
    assert s.name == SCHEMA_NAME  # DSA-01 named
    assert s.type_tag == "ucos.core.schema"  # DSA-03 / UDL-03 typed
    assert s.schema_id.startswith("UCOS-SCHEMA-")  # UDL-04 identified (ENG-001)
    assert s.element_count == 1  # DSA-01 / UDL-10 explicit structure
    assert s.kind is SchemaKind.ENTITY  # DXH-05 classified


def test_schema_describes_entity_by_reference_not_owning():
    entity = _entity()
    s = _schema(entity=entity)
    assert s.described_subject_ids() == (entity.entity_id,)  # DMR-04 describes
    assert s.absorbs_described() is False  # DSA-09 / DMX-02 — referenced, not owned
    ref_dict = s.described_refs[0].to_dict()
    assert ref_dict["owned"] is False
    assert ref_dict["absorbing"] is False
    assert ref_dict["binding"] == "DMR-04:describes"


def test_described_ref_projects_only_identity_and_fingerprint():
    entity = _entity()
    ref = DescribedRef.from_entity(entity)
    assert ref.target_id == entity.entity_id
    assert ref.structure_digest == entity.structure_digest
    assert ref.name == entity.name
    assert ref.meta_class == "DMC-02"


def test_schema_identity_is_deterministic_and_structure_derived():
    a = _schema()
    b = _schema()
    c = _schema(name="different.schema")
    assert a.schema_id == b.schema_id  # same structure → same ENG-001 identity
    assert a.schema_id != c.schema_id  # different name → different identity


def test_schema_is_immutable_objecthood():
    s = _schema()
    with pytest.raises((AttributeError, TypeError)):
        s.name = "other"  # frozen object (ENG-002 objecthood)


def test_unnamed_schema_is_rejected_fail_closed():
    with pytest.raises(SchemaError):
        _schema(name="")  # DSA-01 — no unnamed schema
    with pytest.raises(SchemaError):
        _schema(name="   ")


def test_untyped_schema_is_rejected_fail_closed():
    with pytest.raises(SchemaError):
        _schema(type_tag="")  # DSA-03 / DSA-K1 / UDL-03


def test_schema_with_no_elements_is_rejected_fail_closed():
    entity = _entity()
    with pytest.raises(SchemaError):  # DSA-01 / UDL-10 — must declare explicit structure
        Schema(
            name=SCHEMA_NAME,
            type_tag="ucos.core.schema",
            kind=SchemaKind.ENTITY,
            elements=(),
            described_refs=(DescribedRef.from_entity(entity),),
        )


def test_schema_with_no_subject_is_rejected_fail_closed():
    with pytest.raises(SchemaError):  # DSA-02 — must describe ≥1 subject or compose ≥1 member
        Schema(
            name=SCHEMA_NAME,
            type_tag="ucos.core.schema",
            kind=SchemaKind.ENTITY,
            elements=(SchemaElement("x", "ucos.core.string"),),
            described_refs=(),
        )


def test_untyped_element_is_rejected_fail_closed():
    with pytest.raises(SchemaError):  # DSA-03 / DSA-C3 — every element references an ENG-004 type
        SchemaElement("x", "")


def test_duplicate_element_is_rejected_fail_closed():
    entity = _entity()
    with pytest.raises(SchemaError):  # DSA-02 / DSA-C2 — decidable membership
        Schema(
            name=SCHEMA_NAME,
            type_tag="ucos.core.schema",
            kind=SchemaKind.ENTITY,
            elements=(
                SchemaElement("dup", "ucos.core.string"),
                SchemaElement("dup", "ucos.core.int"),
            ),
            described_refs=(DescribedRef.from_entity(entity),),
        )


def test_schema_describes_must_be_a_certified_entity_reference():
    with pytest.raises(SchemaError):
        DescribedRef.from_entity(object())  # DMR-04 — describes a data.entity.Entity


def test_non_aggregate_may_not_compose_members():
    entity = _entity()
    with pytest.raises(SchemaError):  # DSA-05 — only Aggregate-Schema composes members
        Schema(
            name=SCHEMA_NAME,
            type_tag="ucos.core.schema",
            kind=SchemaKind.ENTITY,
            elements=(SchemaElement("x", "ucos.core.string"),),
            described_refs=(DescribedRef.from_entity(entity),),
            member_schema_refs=("UCOS-SCHEMA-other",),
        )


def test_aggregate_schema_composes_members_acyclically():
    entity = _entity()
    agg = make_schema(
        "ucos.demo.aggregate",
        "ucos.core.schema",
        (element("x", "ucos.core.string"),),
        (entity,),
        kind=SchemaKind.AGGREGATE,
        member_schema_refs=("UCOS-SCHEMA-member-one", "UCOS-SCHEMA-member-two"),
    )
    assert agg.kind is SchemaKind.AGGREGATE
    assert agg.member_schema_refs == ("UCOS-SCHEMA-member-one", "UCOS-SCHEMA-member-two")
    assert agg.is_founding_acyclic() is True  # DSA-C1 / DMK-03


def test_aggregate_without_members_is_rejected():
    entity = _entity()
    with pytest.raises(SchemaError):  # DSA-05 — an aggregate composes ≥1 member
        make_schema(
            "ucos.demo.aggregate",
            "ucos.core.schema",
            (element("x", "ucos.core.string"),),
            (entity,),
            kind=SchemaKind.AGGREGATE,
        )


def test_relationships_are_within_dmr_closure():
    s = _schema()
    assert set(s.meta_relationships()) <= set(SCHEMA_RELATIONSHIPS)  # V2
    assert s.meta_relationships() == ("DMR-04", "DMR-10")


def test_lifecycle_is_forward_only():
    s = _schema(state=SchemaState.DEFINED)
    active = s.transition(SchemaState.ACTIVE)
    assert active.state is SchemaState.ACTIVE
    with pytest.raises(SchemaError):
        active.transition(SchemaState.DEFINED)  # UDL-12 — no backward transition


def test_conformance_is_decidable_and_entity_conforms():
    entity = _entity()
    s = _schema(entity=entity)
    assert s.is_conformance_decidable() is True  # DSA-02
    assert s.conforms_entity(entity) is True  # DSA-C2 / DSA-C3 — derived structure conforms


def test_entity_not_described_does_not_conform():
    s = _schema(entity=_entity())
    other = _entity(name="ucos.demo.other")
    assert s.describes_subject(other.entity_id) is False
    assert s.conforms_entity(other) is False  # not described → not conformant


def test_entity_with_wrong_element_type_does_not_conform():
    entity = _entity(attr_name="field", attr_type="ucos.core.string")
    # a schema whose required element demands a different type than the entity provides
    s = make_schema(
        SCHEMA_NAME,
        "ucos.core.schema",
        (element("field", "ucos.core.int"),),
        (entity,),
    )
    assert s.conforms_entity(entity) is False  # DSA-C3 type mismatch → decidably non-conformant


def test_schema_ref_helper_matches_property():
    s = _schema()
    assert s.schema_ref == schema_ref_for(SCHEMA_NAME)
    assert s.schema_ref == f"UCOS-SCHEMA-REF:{SCHEMA_NAME}"


def test_founding_graph_is_acyclic():
    s = _schema()
    assert s.is_founding_acyclic() is True  # V4 / DMK-03 / DSA-C1


def test_versioned_evolution_is_recorded():
    s = _schema(version="2.1.0")
    assert s.version == "2.1.0"  # DSA-06
    with pytest.raises(SchemaError):
        _schema(version="")  # DSA-06 — explicit version required


def test_non_constitutive_and_no_secret():
    s = _schema()
    assert s.confers_authority() is False  # UDL-15 / DSA-09 / C7
    assert s.redefines_el1() is False  # UDL-02 / DMI-05
    assert s.selects_technology() is False  # UDL-11 / DSA-07 / DSA-K5
    assert s.embeds_secret() is False


def test_secret_bearing_schema_is_detected():
    leaky = _schema(name="password")
    assert leaky.embeds_secret() is True  # UDL-15 / RR-07


def test_schema_to_dict_records_substrate_reuse():
    s = _schema()
    payload = s.to_dict()
    assert payload["substrate_refs"] == ["ENG-001", "ENG-002", "ENG-004", "ENG-005"]
    assert payload["meta_class"] == "DMC-05"
    assert payload["absorbs_described"] is False
    assert payload["explicit"] is True
    assert payload["conformance_decidable"] is True


def test_schema_type_is_the_realized_construct():
    assert isinstance(_schema(), Schema)


# --------------------------------------------------------------------------------------
# Every constructor guard, shown refusing.
#
# WHY THIS EXISTS. `Schema.__post_init__`, `SchemaElement.__post_init__` and
# `DescribedRef.__post_init__` between them declare more than twenty `raise` statements —
# one per rule the construct claims to enforce at construction. The suite above builds
# valid constructs and asserts what they then do, so those guards were observed only NOT
# firing. A guard that never fires is `pass` with a docstring.
#
# The witnesses are DERIVED rather than enumerated (`engine.tests.assert_every_guard_can_refuse`
# mutates one declared field at a time and attributes each raise to the exact `raise`
# statement that executed, through the traceback rather than through the message text) so a
# guard added to any of these classes is proven on the commit that adds it, and a reworded
# message cannot silently retire a proof.
# --------------------------------------------------------------------------------------

from engine.tests import assert_every_guard_can_refuse  # noqa: E402


def test_every_schema_element_guard_can_refuse():
    assert_every_guard_can_refuse(element("field", "ucos.core.string"))


def test_every_described_ref_guard_can_refuse():
    assert_every_guard_can_refuse(_schema().described_refs[0])


def test_every_schema_guard_can_refuse():
    """Two modes, because an Aggregate-Schema and an Entity-Schema reach different guards:
    the member-composition rules are unreachable from a construct in the other mode."""
    entity_schema = _schema()
    aggregate = make_schema(
        "ucos.demo.aggregate",
        "ucos.core.schema",
        (element("x", "ucos.core.string"),),
        (_entity(),),
        kind=SchemaKind.AGGREGATE,
        member_schema_refs=("UCOS-SCHEMA-member-one",),
    )
    assert_every_guard_can_refuse(entity_schema, aggregate)


def test_a_missing_required_element_breaks_conformance() -> None:
    """DTA-07: conformance is decided by the required elements the entity lacks.

    The schema of one entity is a claim about THAT entity; presenting a second entity
    that does not bear the required attribute must fail the conformance decision, and
    a schema whose required arms never fire cannot be trusted to guard anything.
    """
    here = _entity("ucos.demo.entity-here")
    schema = entity_schema_for(here, name="ucos.demo.schema", type_tag="ucos.core.schema")
    assert schema.conforms_entity(here) is True

    # The same subject described by a schema that demands an element it does not bear:
    # this is the absence arm, and it must be reached through the *element* loop — the
    # describe-guard fires first for any other entity and proves nothing about elements.
    wider = make_schema(
        "ucos.demo.schema-absence",
        "ucos.core.schema",
        (
            SchemaElement(name="ucos.demo.attr", type_tag="ucos.core.string"),
            SchemaElement(name="ucos.demo.extra", type_tag="ucos.core.string", required=True),
        ),
        (here,),
    )
    assert wider.conforms_entity(here) is False


def test_schema_transition_refuses_a_state_that_is_not_a_lifecycle_member() -> None:
    """UDL-12 for the schema class."""
    schema = _schema(state=SchemaState.ACTIVE)
    with pytest.raises(SchemaError, match="DOS-01…05 state"):
        schema.transition("ACTIVE")  # type: ignore[arg-type]


def test_a_type_mismatch_on_a_required_element_breaks_conformance() -> None:
    """The second conformance refusal: the name is present, the type tag is not its own.

    DTA-07 is decided by name AND type — an entity that carries the element but under a
    different ENG-004 type is not the entity the schema describes, and the guard must say
    so on that arm, not only on absence.
    """
    here = _entity("ucos.demo.entity-type")
    same_name = _entity(
        "ucos.demo.entity-typed",
        attr_name="ucos.demo.attr",
        attr_type="ucos.core.number",
    )
    schema = entity_schema_for(
        here, name="ucos.demo.schema-typemismatch", type_tag="ucos.core.schema"
    )
    assert schema.conforms_entity(same_name) is False


def test_an_optional_element_may_be_absent_without_breaking_conformance() -> None:
    """required=False is the other side of the same decision.

    The conformance loop reads `el.required` for every element; without an optional
    element walking past the guard, the predicate has only ever been seen refusing, and a
    schema that cannot describe an entity missing an optional field is not optional at all.
    """
    entity = _entity("ucos.demo.entity-optional")
    schema = make_schema(
        "ucos.demo.schema-optional",
        "ucos.core.schema",
        (SchemaElement(name="ucos.demo.missing", type_tag="ucos.core.string", required=False),),
        (entity,),
    )
    assert schema.conforms_entity(entity) is True
