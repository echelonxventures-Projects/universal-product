"""EC3-B10-U02 — Attribute construct tests (DMC-03 + DAA-01…07 + UDL-08/06/03/12)."""

from __future__ import annotations

import pytest

from data.attribute import (
    Attribute,
    AttributeError_,
    DatumValueRef,
    make_attribute,
)
from data.attribute_meta import (
    ATTRIBUTE_META_CLASS,
    ATTRIBUTE_RELATIONSHIPS,
    AttributeKind,
    AttributeState,
)
from data.datum import make_datum


def _value_datum():
    return make_datum("ucos.core.string", "hello")


def _attr(**overrides):
    kwargs = dict(
        name="ucos.demo.attr",
        type_tag="ucos.core.string",
        value=_value_datum(),
        bearing_entity_ref="UCOS-ENTITY-REF:demo",
    )
    kwargs.update(overrides)
    return make_attribute(
        kwargs.pop("name"),
        kwargs.pop("type_tag"),
        kwargs.pop("value"),
        kwargs.pop("bearing_entity_ref"),
        **kwargs,
    )


def test_attribute_is_typed_named_single_bearing_and_value_bearing():
    a = _attr()
    assert a.meta_class == ATTRIBUTE_META_CLASS  # V1 (DMC-03)
    assert a.name == "ucos.demo.attr"  # DAA-04 named
    assert a.type_tag == "ucos.core.string"  # DAA-01 / UDL-08 typed
    assert a.attribute_id.startswith("UCOS-ATTR-")  # UDL-04 identified (ENG-001)
    assert a.bearing_entity_ref == "UCOS-ENTITY-REF:demo"  # DMR-01 single bearing
    assert len(a.value_digest) == 64  # UDL-06 value fidelity (ENG-003)
    assert a.kind is AttributeKind.DESCRIPTIVE  # DXH-03 classified


def test_attribute_values_datum_by_reference_not_absorbing():
    d = _value_datum()
    a = _attr(value=d)
    assert a.value_ref.datum_id == d.datum_id  # DMR-02 values the CERTIFIED Datum
    assert a.value_ref.value_digest == d.value_digest  # references its ENG-003 value
    assert a.absorbs_value() is False  # DMX-02 non-absorbing
    # the attribute stores only the reference, never the datum's raw value/model
    assert "value" not in a.value_ref.to_dict()


def test_value_ref_projects_only_identity_and_digest():
    d = _value_datum()
    ref = DatumValueRef.from_datum(d)
    assert ref.datum_id == d.datum_id
    assert ref.type_tag == d.type_tag
    assert ref.to_dict()["absorbing"] is False


def test_attribute_identity_is_deterministic_and_structure_derived():
    a = _attr()
    b = _attr()
    c = _attr(name="different.name")
    assert a.attribute_id == b.attribute_id  # same structure → same ENG-001 identity
    assert a.attribute_id != c.attribute_id  # different name → different identity


def test_attribute_is_immutable_objecthood():
    a = _attr()
    with pytest.raises((AttributeError, TypeError)):
        a.name = "other"  # frozen object (ENG-002 objecthood)


def test_unnamed_attribute_is_rejected_fail_closed():
    with pytest.raises(AttributeError_):
        _attr(name="")  # DAA-04 / UDL-08 — no unnamed attribute
    with pytest.raises(AttributeError_):
        _attr(name="   ")


def test_untyped_attribute_is_rejected_fail_closed():
    with pytest.raises(AttributeError_):
        _attr(type_tag="")  # DAA-01 / UDL-08 — no untyped attribute


def test_unbound_attribute_is_rejected_fail_closed():
    with pytest.raises(AttributeError_):
        _attr(bearing_entity_ref="")  # DAA-02 — never floats free


def test_nullability_must_be_declared_bool():
    with pytest.raises(AttributeError_):
        _attr(nullable="yes")  # DAA-05 — declared explicitly, never implicit/coerced
    a = _attr(nullable=True)
    assert a.nullable is True


def test_value_must_be_a_certified_datum_reference():
    with pytest.raises(AttributeError_):
        DatumValueRef.from_datum(object())  # DMR-02 — values a data.datum.Datum


def test_relationships_are_within_dmr_closure():
    a = _attr()
    assert set(a.meta_relationships()) <= set(ATTRIBUTE_RELATIONSHIPS)  # V2
    assert a.meta_relationships() == ("DMR-01", "DMR-02", "DMR-04", "DMR-08", "DMR-09")


def test_lifecycle_is_forward_only():
    a = _attr(state=AttributeState.DEFINED)
    active = a.transition(AttributeState.ACTIVE)
    assert active.state is AttributeState.ACTIVE
    with pytest.raises(AttributeError_):
        active.transition(AttributeState.DEFINED)  # UDL-12 — no backward transition


def test_relational_attribute_requires_reference_by_reference():
    with pytest.raises(AttributeError_):
        _attr(kind=AttributeKind.RELATIONAL)  # DAA-07 — must reference a target entity
    a = _attr(kind=AttributeKind.RELATIONAL, references_entity="UCOS-ENTITY-REF:other")
    assert a.references_entity == "UCOS-ENTITY-REF:other"
    with pytest.raises(AttributeError_):
        _attr(kind=AttributeKind.DESCRIPTIVE, references_entity="UCOS-ENTITY-REF:other")


def test_derived_attribute_requires_provenance():
    with pytest.raises(AttributeError_):
        _attr(kind=AttributeKind.DERIVED)  # DAA-06 — provenance required
    a = _attr(kind=AttributeKind.DERIVED, derived_from=("UCOS-ATTR-x-0",))
    assert a.derived_from == ("UCOS-ATTR-x-0",)
    with pytest.raises(AttributeError_):
        _attr(kind=AttributeKind.DESCRIPTIVE, derived_from=("x",))


def test_founding_graph_is_acyclic():
    a = _attr()
    assert a.is_founding_acyclic() is True  # V4 / DMK-03 / UDL-09


def test_non_constitutive_and_no_secret():
    a = _attr()
    assert a.confers_authority() is False  # UDL-15 / DAA-09 / C7
    assert a.redefines_el1() is False  # UDL-02 / DMI-05
    assert a.selects_technology() is False  # UDL-11 / DAA-K5
    assert a.embeds_secret() is False


def test_secret_bearing_attribute_is_detected():
    leaky = _attr(name="password")
    assert leaky.embeds_secret() is True  # UDL-15 / RR-07


def test_attribute_to_dict_records_substrate_reuse():
    a = _attr()
    payload = a.to_dict()
    assert payload["substrate_refs"] == ["ENG-001", "ENG-003", "ENG-004", "ENG-005"]
    assert payload["meta_class"] == "DMC-03"
    assert payload["absorbs_value"] is False


def test_attribute_type_is_the_realized_construct():
    assert isinstance(_attr(), Attribute)


# --------------------------------------------------------------------------------------
# Every constructor guard, shown refusing (see data/tests/test_schema.py for the argument).
# --------------------------------------------------------------------------------------

from engine.tests import assert_every_guard_can_refuse  # noqa: E402


def test_every_datum_value_ref_guard_can_refuse():
    assert_every_guard_can_refuse(_attr().value_ref)


def test_every_attribute_guard_can_refuse():
    assert_every_guard_can_refuse(_attr())


def test_attribute_transition_refuses_a_state_that_is_not_a_lifecycle_member() -> None:
    """UDL-12: a forward-only transition is a type fact before it is an order fact (DSS-01…05)."""

    attribute = make_attribute(
        "ATTR-T-01", "TYPE", make_datum("t", "v"), state=AttributeState.ACTIVE
    )
    with pytest.raises(AttributeError_, match="DOS-01…05 state"):
        attribute.transition("ACTIVE")  # type: ignore[arg-type]


def test_attribute_transition_refuses_a_state_that_is_not_a_lifecycle_member() -> None:
    """UDL-12: forward-only is a type fact first — a string naming ACTIVE is not the state."""
    attribute = _attr(state=AttributeState.ACTIVE)
    with pytest.raises(AttributeError_, match="DOS-01…05 state"):
        attribute.transition("ACTIVE")  # type: ignore[arg-type]
