"""EC3-B10-U01 — Datum construct tests (DMC-01 + DMK-01/02 + UDL-03/04/05/06/12)."""

from __future__ import annotations

import pytest

from data.datum import Datum, DatumError, make_datum
from data.meta import DATUM_META_CLASS, DATUM_RELATIONSHIPS, DatumKind, DatumState


def test_datum_is_typed_identified_and_value_bearing():
    d = make_datum("ucos.core.string", "hello")
    assert d.meta_class == DATUM_META_CLASS  # V1
    assert d.type_tag == "ucos.core.string"  # UDL-03 typed
    assert d.datum_id.startswith("UCOS-DATUM-")  # UDL-04 identified (ENG-001)
    assert len(d.value_digest) == 64  # UDL-06 value fidelity (ENG-003)
    assert d.kind is DatumKind.PRIMITIVE  # DXH-01 classified


def test_datum_identity_is_deterministic_and_value_derived():
    a = make_datum("t", "v")
    b = make_datum("t", "v")
    c = make_datum("t", "w")
    assert a.datum_id == b.datum_id  # same value → same ENG-001 identity (determinism)
    assert a.datum_id != c.datum_id  # different value → different identity


def test_datum_is_immutable_objecthood():
    d = make_datum("t", "v")
    with pytest.raises((AttributeError, TypeError)):
        d.type_tag = "other"  # frozen object (ENG-002 objecthood)


def test_untyped_datum_is_rejected_fail_closed():
    with pytest.raises(DatumError):
        make_datum("", "v")  # UDL-03 — no untyped datum may exist
    with pytest.raises(DatumError):
        make_datum("   ", "v")


def test_non_value_faithful_payload_is_rejected():
    with pytest.raises(DatumError):
        make_datum("t", object())  # UDL-06 — value must round-trip ENG-003 encoding


def test_circular_value_is_rejected_guaranteeing_acyclicity():
    cycle: dict = {}
    cycle["self"] = cycle
    with pytest.raises(DatumError):
        make_datum("t", cycle, kind=DatumKind.COMPOSITE)  # V4 / DMK-03


def test_relationships_are_within_dmr_closure():
    d = make_datum("t", "v")
    assert set(d.meta_relationships()) <= set(DATUM_RELATIONSHIPS)  # V2
    assert d.meta_relationships() == ("DMR-02", "DMR-09", "DMR-10")


def test_lifecycle_is_forward_only():
    d = make_datum("t", "v", state=DatumState.DEFINED)
    active = d.transition(DatumState.ACTIVE)
    assert active.state is DatumState.ACTIVE
    with pytest.raises(DatumError):
        active.transition(DatumState.DEFINED)  # UDL-12 — no backward transition


def test_derived_datum_requires_provenance():
    with pytest.raises(DatumError):
        make_datum("t", "v", kind=DatumKind.DERIVED)  # DMG-03 provenance required
    d = make_datum("t", "v", kind=DatumKind.DERIVED, derived_from=("UCOS-DATUM-x-0",))
    assert d.derived_from == ("UCOS-DATUM-x-0",)
    with pytest.raises(DatumError):
        make_datum("t", "v", kind=DatumKind.PRIMITIVE, derived_from=("x",))


def test_non_constitutive_and_no_secret():
    d = make_datum("t", "v")
    assert d.confers_authority() is False  # UDL-15 / C7
    assert d.redefines_el1() is False  # UDL-02 / DMI-05
    assert d.embeds_secret() is False


def test_secret_bearing_datum_is_detected():
    leaky = make_datum("credential", {"password": "hunter2"})
    assert leaky.embeds_secret() is True  # UDL-15 / RR-07


def test_datum_to_dict_records_substrate_reuse():
    d = make_datum("t", "v")
    payload = d.to_dict()
    assert payload["substrate_refs"] == ["ENG-001", "ENG-002", "ENG-003", "ENG-004"]
    assert payload["meta_class"] == "DMC-01"


def test_datum_type_is_the_realized_construct():
    assert isinstance(make_datum("t", 1), Datum)


def test_the_datum_guards_refuse_a_kind_or_state_that_is_not_typed() -> None:
    """DXH-01 and UDL-12 are type facts first — both refusals and the transition guard (UDL-12).

    A string that reads like an enum member is not one: kind, state and transition target are
    each refused before any ordering question is asked, because a mistyped state would otherwise
    fail as an IndexError inside the lifecycle table instead of as the guard it is.
    """

    with pytest.raises(DatumError, match="DXH-01 DatumKind"):
        make_datum("t", "v", kind="PRIMITIVE")  # type: ignore[arg-type]
    with pytest.raises(DatumError, match="DatumState"):
        make_datum("t", "v", state="DEFINED")  # type: ignore[arg-type]
    live = make_datum("t", "v")
    live = live.transition(DatumState.ACTIVE)
    with pytest.raises(DatumError, match="DOS-01"):
        live.transition("ACTIVE")  # type: ignore[arg-type]
