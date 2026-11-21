"""UCOS-EPIC-005 — Universal Validation config tests (Terminal T5)."""

from __future__ import annotations

import json
from platform.tests.universal_validation_helpers import passing_facts
from platform.universal_validation.config import (
    UniversalValidationConfig,
    load_config,
    parse_config,
)
from platform.universal_validation.contracts import ValidationDomain
from platform.universal_validation.errors import ValidationConfigError

import pytest


def _raw(**overrides):
    base = {"target_id": "T", "facts": passing_facts()}
    base.update(overrides)
    return base


def test_parse_config_builds_target():
    config = parse_config(_raw())
    target = config.build_target()
    assert target.target_id == "T"
    assert config.selected_domains() is None
    assert config.digest() == parse_config(_raw()).digest()


def test_parse_config_with_domain_subset():
    config = parse_config(_raw(domains=["quality", "runtime"]))
    assert config.selected_domains() == (ValidationDomain.QUALITY, ValidationDomain.RUNTIME)
    assert config.to_dict()["domains"] == ["quality", "runtime"]


@pytest.mark.parametrize(
    "raw",
    [
        [],  # not a mapping
        {"facts": {}},  # no target_id
        {"target_id": "T", "facts": []},  # facts not mapping
        {"target_id": "T", "domains": "quality"},  # domains not a list
        {"target_id": "T", "domains": ["nope"]},  # unknown domain
        {"target_id": "T", "domains": ["quality", "quality"]},  # duplicate domain
    ],
)
def test_parse_config_rejects_malformed(raw):
    with pytest.raises(ValidationConfigError):
        parse_config(raw)


def test_load_config_json(tmp_path):
    path = tmp_path / "validation.json"
    path.write_text(json.dumps(_raw()), encoding="utf-8")
    config = load_config(path)
    assert isinstance(config, UniversalValidationConfig)
    assert config.target_id == "T"


def test_load_config_toml(tmp_path):
    path = tmp_path / "validation.toml"
    path.write_text('target_id = "T"\ndomains = ["quality"]\n[facts]\n', encoding="utf-8")
    config = load_config(path)
    assert config.selected_domains() == (ValidationDomain.QUALITY,)


def test_load_config_missing_file(tmp_path):
    with pytest.raises(ValidationConfigError):
        load_config(tmp_path / "absent.json")


def test_load_config_unsupported_suffix(tmp_path):
    path = tmp_path / "validation.yaml"
    path.write_text("target_id: T", encoding="utf-8")
    with pytest.raises(ValidationConfigError):
        load_config(path)


def test_load_config_invalid_json(tmp_path):
    path = tmp_path / "validation.json"
    path.write_text("{not json", encoding="utf-8")
    with pytest.raises(ValidationConfigError):
        load_config(path)


def test_load_config_non_mapping_root(tmp_path):
    path = tmp_path / "validation.json"
    path.write_text("[1, 2, 3]", encoding="utf-8")
    with pytest.raises(ValidationConfigError):
        load_config(path)
