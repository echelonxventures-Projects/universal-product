"""TASK-000019/000029 — Parse Engine tests."""

from __future__ import annotations

import json

import pytest

from engine.compiler.errors import ParseError
from engine.compiler.ir import BlueprintFamily
from engine.compiler.parser import (
    SUPPORTED_FAMILIES,
    ensure_supported,
    is_supported,
    parse,
    parse_bytes,
    parse_document,
    parse_text,
)


def test_parse_from_mapping_text_and_bytes(data_blueprint):
    ir = parse_document(data_blueprint)
    assert ir.blueprint_id == "BP-DATA-0001"
    text = json.dumps(data_blueprint)
    assert parse_text(text).blueprint_id == "BP-DATA-0001"
    assert parse_bytes(text.encode("utf-8")).blueprint_id == "BP-DATA-0001"
    assert parse(data_blueprint).name == "Customer"
    assert parse(text).name == "Customer"
    assert parse(text.encode("utf-8")).name == "Customer"


def test_parse_document_rejects_non_object():
    with pytest.raises(ParseError):
        parse_document([1, 2, 3])  # type: ignore[arg-type]


def test_parse_text_rejects_bad_json():
    with pytest.raises(ParseError):
        parse_text("{bad")


def test_parse_bytes_rejects_bad_utf8():
    with pytest.raises(ParseError):
        parse_bytes(b"\xff\xfe")


def test_parse_rejects_unknown_source_type():
    with pytest.raises(ParseError):
        parse(12345)  # type: ignore[arg-type]


def test_parse_maps_invariant_failure_to_parse_error(data_blueprint):
    broken = dict(data_blueprint)
    broken["entity"] = dict(broken["entity"])
    broken["entity"]["attributes"] = []  # entity must have >=1 attribute
    with pytest.raises(ParseError):
        parse_document(broken)


def test_supported_family_gate(data_blueprint):
    ir = parse_document(data_blueprint)
    assert is_supported(ir)
    assert ensure_supported(ir) is ir
    assert BlueprintFamily.DATA in SUPPORTED_FAMILIES


def test_ensure_supported_rejects_non_data_family(data_blueprint):
    event = dict(data_blueprint)
    event["blueprint_id"] = "BP-EVENT-000001"
    event["family"] = "BP-EVENT"
    ir = parse_document(event)
    assert not is_supported(ir)
    with pytest.raises(ParseError) as exc:
        ensure_supported(ir)
    assert exc.value.context["family"] == "BP-EVENT"
