"""EPIC-PLAT-003 — Resumable checkpoint tests (Terminal T5)."""

from __future__ import annotations

from platform.repository_operations.checkpoint import Checkpoint, CheckpointStore
from platform.repository_operations.errors import CheckpointError

import pytest


def test_checkpoint_to_dict_and_from_dict_roundtrip():
    cp = Checkpoint(config_digest="d", completed={"a": "e1"})
    assert Checkpoint.from_dict(cp.to_dict()) == cp


def test_checkpoint_from_dict_rejects_malformed():
    with pytest.raises(CheckpointError):
        Checkpoint.from_dict("x")  # type: ignore[arg-type]
    with pytest.raises(CheckpointError):
        Checkpoint.from_dict({"completed": {}})
    with pytest.raises(CheckpointError):
        Checkpoint.from_dict({"config_digest": "d", "completed": "no"})


def test_store_load_none_when_absent(tmp_path):
    store = CheckpointStore(tmp_path / "cp.json")
    assert store.path == tmp_path / "cp.json"
    assert store.load() is None


def test_store_save_and_load_roundtrip(tmp_path):
    store = CheckpointStore(tmp_path / "nested" / "cp.json")
    cp = Checkpoint(config_digest="d", completed={"a": "e1", "b": "e2"})
    store.save(cp)
    assert store.load() == cp


def test_store_load_malformed(tmp_path):
    path = tmp_path / "cp.json"
    path.write_text("{ not json", encoding="utf-8")
    store = CheckpointStore(path)
    with pytest.raises(CheckpointError):
        store.load()


def test_store_save_error_when_path_unwritable(tmp_path):
    # A path whose parent is a file (not a dir) cannot be created → OSError.
    blocker = tmp_path / "blocker"
    blocker.write_text("x", encoding="utf-8")
    store = CheckpointStore(blocker / "cp.json")
    with pytest.raises(CheckpointError):
        store.save(Checkpoint(config_digest="d", completed={}))
