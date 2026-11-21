"""EPIC-PLAT-003 — Repository Operations config loader tests (Terminal T5)."""

from __future__ import annotations

import json
from platform.repository_operations.config import load_config, parse_config
from platform.repository_operations.errors import OperationsConfigError

import pytest

_RAW = {
    "repository_id": "R",
    "epic_id": "E",
    "stages": [{"stage_id": "s1", "kind": "freeze", "params": {"paths": []}}],
}


def test_parse_config_returns_normalized_config():
    config = parse_config(_RAW)
    assert config.repository_id == "R"
    assert config.stages[0].stage_id == "s1"


def test_load_config_json(tmp_path):
    path = tmp_path / "ops.json"
    path.write_text(json.dumps(_RAW), encoding="utf-8")
    config = load_config(path)
    assert config.epic_id == "E"


def test_load_config_toml(tmp_path):
    path = tmp_path / "ops.toml"
    path.write_text(
        'repository_id = "R"\nepic_id = "E"\n[[stages]]\nstage_id = "s1"\nkind = "freeze"\n',
        encoding="utf-8",
    )
    config = load_config(path)
    assert config.stages[0].stage_id == "s1"


def test_load_config_missing_file(tmp_path):
    with pytest.raises(OperationsConfigError):
        load_config(tmp_path / "absent.json")


def test_load_config_unsupported_suffix(tmp_path):
    path = tmp_path / "ops.yaml"
    path.write_text("nope", encoding="utf-8")
    with pytest.raises(OperationsConfigError):
        load_config(path)


def test_load_config_invalid_json(tmp_path):
    path = tmp_path / "ops.json"
    path.write_text("{ not json", encoding="utf-8")
    with pytest.raises(OperationsConfigError):
        load_config(path)


def test_load_config_non_mapping_root(tmp_path):
    path = tmp_path / "ops.json"
    path.write_text(json.dumps([1, 2, 3]), encoding="utf-8")
    with pytest.raises(OperationsConfigError):
        load_config(path)
