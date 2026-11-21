"""Tests for TASK-000010 registry source resolver (EPIC-002)."""

from __future__ import annotations

import json

import pytest

from engine.registry.errors import RegistryDataError, RegistrySourceError
from engine.registry.source import (
    ARTIFACTS_FILE,
    RegistrySource,
    default_data_dir,
)


def test_default_data_dir_points_at_book_data():
    path = default_data_dir()
    assert path.as_posix().endswith("00-BOOK/DATA")


def test_source_requires_existing_directory(tmp_path):
    with pytest.raises(RegistrySourceError):
        RegistrySource(tmp_path / "does-not-exist")


def test_source_rejects_file_as_dir(tmp_path):
    a_file = tmp_path / "afile.json"
    a_file.write_text("{}", encoding="utf-8")
    with pytest.raises(RegistrySourceError):
        RegistrySource(a_file)


def test_data_dir_property(source, data_dir):
    assert source.data_dir == data_dir.resolve()


def test_exists_and_path_for(source):
    assert source.exists(ARTIFACTS_FILE)
    assert not source.exists("missing.json")
    assert source.path_for(ARTIFACTS_FILE).name == ARTIFACTS_FILE


def test_path_for_rejects_traversal(source):
    with pytest.raises(RegistrySourceError):
        source.path_for("../escape.json")


def test_read_json_missing_file(source):
    with pytest.raises(RegistrySourceError):
        source.read_json("missing.json")


def test_read_json_invalid_json(tmp_path):
    (tmp_path / "bad.json").write_text("{not json", encoding="utf-8")
    src = RegistrySource(tmp_path)
    with pytest.raises(RegistryDataError):
        src.read_json("bad.json")


def test_read_document_ok(source):
    envelope, records = source.read_document(ARTIFACTS_FILE, root_key="artifacts")
    assert envelope["count"] == len(records)
    assert isinstance(records, list) and records


def test_read_document_root_not_object(tmp_path):
    (tmp_path / "list.json").write_text("[]", encoding="utf-8")
    src = RegistrySource(tmp_path)
    with pytest.raises(RegistryDataError):
        src.read_document("list.json", root_key="artifacts")


def test_read_document_missing_records(tmp_path):
    (tmp_path / "nokey.json").write_text(json.dumps({"count": 0}), encoding="utf-8")
    src = RegistrySource(tmp_path)
    with pytest.raises(RegistryDataError):
        src.read_document("nokey.json", root_key="artifacts")


def test_custom_data_dir_not_within_frozen_corpus(source):
    # A tmp_path substrate is outside the repo corpus boundary.
    assert source.is_within_frozen_corpus() is False


def test_real_data_dir_is_within_frozen_corpus(real_data_dir):
    src = RegistrySource(real_data_dir)
    assert src.is_within_frozen_corpus() is True
