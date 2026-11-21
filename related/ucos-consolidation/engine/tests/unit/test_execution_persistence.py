"""EPIC-RTE-002 — Execution Persistence unit tests."""

from __future__ import annotations

import pytest

from engine.runtime.execution.checkpoint import checkpoint
from engine.runtime.execution.coordinator import coordinate
from engine.runtime.execution.errors import PersistenceError
from engine.runtime.execution.persistence import (
    Serialisable,
    from_json,
    persist_checkpoint,
    persist_run,
    persist_snapshot,
    restore_checkpoint,
    to_json,
)
from engine.runtime.execution.snapshot import snapshot


def test_to_json_is_canonical_and_sorted():
    blob = to_json({"b": 1, "a": 2})
    assert blob == '{"a":2,"b":1}'


def test_to_json_accepts_serialisable(composition):
    cp = checkpoint(coordinate(composition))
    assert to_json(cp) == to_json(cp.to_dict())


def test_from_json_round_trip():
    assert from_json('{"a":1}') == {"a": 1}


def test_from_json_rejects_invalid_json():
    with pytest.raises(PersistenceError) as exc:
        from_json("{not json")
    assert exc.value.code == "RT-EXEC-PERS-001"


def test_from_json_rejects_non_object():
    with pytest.raises(PersistenceError):
        from_json("[1, 2, 3]")


def test_checkpoint_round_trip(composition):
    cp = checkpoint(coordinate(composition), through_stage=1)
    restored = restore_checkpoint(persist_checkpoint(cp))
    assert restored == cp


def test_persist_snapshot_and_run(composition):
    run = coordinate(composition)
    assert persist_run(run.to_dict())
    assert persist_snapshot(snapshot(run))


def test_serialisable_protocol_is_runtime_checkable(composition):
    cp = checkpoint(coordinate(composition))
    assert isinstance(cp, Serialisable)
    assert not isinstance(object(), Serialisable)
