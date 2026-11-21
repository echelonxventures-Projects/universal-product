"""TASK-000018/000029 — deterministic IR serialization tests."""

from __future__ import annotations

import json

import pytest

from engine.compiler.errors import SerializationError
from engine.compiler.parser import parse_document
from engine.compiler.serialization import (
    deserialize,
    from_dict,
    serialize,
    serialize_bytes,
    to_canonical_dict,
)


def test_round_trip_is_byte_identical(data_blueprint):
    ir = parse_document(data_blueprint)
    once = serialize(ir)
    twice = serialize(deserialize(once))
    assert once == twice
    assert serialize_bytes(ir) == once.encode("utf-8")


def test_serialize_is_sorted_and_compact(data_blueprint):
    ir = parse_document(data_blueprint)
    text = serialize(ir)
    # compact separators: no ", " or ": " spacing
    assert ", " not in text
    assert '": ' not in text
    # keys sorted at top level
    decoded = json.loads(text)
    assert list(decoded) == sorted(decoded)


def test_canonical_dict_preserves_entity_shape(data_blueprint):
    ir = parse_document(data_blueprint)
    canonical = to_canonical_dict(ir)
    assert canonical["entity"]["attributes"][0]["name"] == "id"
    assert canonical["entity"]["relationships"][0]["target"] == "BP-DATA-0002"
    assert canonical["provenance"]["canonical_source"] == "UCOS-DAT-000007"


def test_deserialize_rejects_bad_json():
    with pytest.raises(SerializationError):
        deserialize("{not json")


def test_from_dict_requires_object():
    with pytest.raises(SerializationError):
        from_dict([])  # type: ignore[arg-type]


def test_from_dict_missing_required_field(data_blueprint):
    broken = dict(data_blueprint)
    del broken["certification"]
    with pytest.raises(SerializationError) as exc:
        from_dict(broken)
    assert exc.value.context["field"] == "certification"


def test_from_dict_invariant_violation_becomes_serialization_error(data_blueprint):
    broken = json.loads(json.dumps(data_blueprint))
    # remove the only primary key so the entity is still parseable but the IR
    # invariant (family prefix etc.) still holds — instead break the family prefix.
    broken["blueprint_id"] = "BP-EVENT-9"
    with pytest.raises(SerializationError):
        from_dict(broken)


def test_entity_and_provenance_must_be_objects(data_blueprint):
    broken = dict(data_blueprint)
    broken["provenance"] = "nope"
    with pytest.raises(SerializationError):
        from_dict(broken)
    broken2 = dict(data_blueprint)
    broken2["entity"] = "nope"
    with pytest.raises(SerializationError):
        from_dict(broken2)


def test_entity_attributes_must_be_a_list(data_blueprint):
    broken = dict(data_blueprint)
    broken["entity"] = dict(broken["entity"])
    broken["entity"]["attributes"] = "nope"
    with pytest.raises(SerializationError):
        from_dict(broken)


def test_certification_must_be_an_object(data_blueprint):
    broken = dict(data_blueprint)
    broken["certification"] = "CERTIFIED"
    with pytest.raises(SerializationError):
        from_dict(broken)
