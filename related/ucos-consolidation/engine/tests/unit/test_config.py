"""Tests for TASK-000005 configuration loader."""

from __future__ import annotations

import json

import pytest

from engine.foundation.config.config import (
    Config,
    Environment,
    SecretRef,
    _coerce_secrets,
    load_config,
)
from engine.foundation.obs.errors import ConfigurationError, SecurityViolation


def test_environment_from_str_valid():
    assert Environment.from_str("Production") is Environment.PRODUCTION
    assert Environment.from_str(" staging ") is Environment.STAGING


def test_environment_from_str_invalid():
    with pytest.raises(ConfigurationError):
        Environment.from_str("moon")


def test_env_defaults_to_development():
    cfg = load_config(environ={})
    assert cfg.environment is Environment.DEVELOPMENT


def test_env_read_from_ucos_env():
    cfg = load_config(environ={"UCOS_ENV": "qa"})
    assert cfg.environment is Environment.QA


def test_env_prefix_values_loaded_and_lowercased():
    cfg = load_config(environ={"UCOS_ENV": "testing", "UCOS_MAX_WORKERS": "4", "OTHER": "x"})
    assert cfg.get("max_workers") == "4"
    assert "other" not in cfg


def test_file_then_env_precedence(tmp_path):
    path = tmp_path / "config.json"
    path.write_text(json.dumps({"region": "eu", "max_workers": "2"}), encoding="utf-8")
    cfg = load_config(
        environment=Environment.STAGING,
        config_file=path,
        environ={"UCOS_MAX_WORKERS": "8"},
    )
    assert cfg.get("region") == "eu"
    assert cfg.get_int("max_workers") == 8  # env overrides file


def test_require_missing_raises():
    cfg = load_config(environ={})
    with pytest.raises(ConfigurationError):
        cfg.require("nope")


def test_typed_getters():
    cfg = load_config(
        environ={
            "UCOS_COUNT": "10",
            "UCOS_RATIO": "1.5",
            "UCOS_ENABLED": "yes",
            "UCOS_DISABLED": "off",
        }
    )
    assert cfg.get_int("count") == 10
    assert cfg.get_float("ratio") == 1.5
    assert cfg.get_bool("enabled") is True
    assert cfg.get_bool("disabled") is False
    assert cfg.get_int("absent", 3) == 3
    assert cfg.get_float("absent", 2.0) == 2.0
    assert cfg.get_bool("absent", True) is True


def test_typed_getter_errors():
    cfg = load_config(environ={"UCOS_COUNT": "x", "UCOS_FLAG": "maybe", "UCOS_RATIO": "y"})
    with pytest.raises(ConfigurationError):
        cfg.get_int("count")
    with pytest.raises(ConfigurationError):
        cfg.get_bool("flag")
    with pytest.raises(ConfigurationError):
        cfg.get_float("ratio")


def test_inline_secret_rejected():
    with pytest.raises(SecurityViolation):
        load_config(environ={"UCOS_DB_PASSWORD": "hunter2"})


def test_secret_reference_wrapped_and_resolved(monkeypatch):
    monkeypatch.setenv("DB_PASSWORD_SOURCE", "s3cr3t")
    cfg = load_config(environ={"UCOS_DB_PASSWORD": "env://DB_PASSWORD_SOURCE"})
    ref = cfg.secret("db_password")
    assert isinstance(ref, SecretRef)
    assert ref.resolve() == "s3cr3t"
    # redacted view never exposes the secret
    assert cfg.as_dict()["db_password"] == "***"
    assert "s3cr3t" not in repr(ref)
    assert "s3cr3t" not in str(ref)


def test_secret_ref_validation():
    with pytest.raises(ConfigurationError):
        SecretRef("no-scheme")
    with pytest.raises(ConfigurationError):
        SecretRef("vault://x")  # unsupported scheme
    with pytest.raises(ConfigurationError):
        SecretRef("env://")  # empty locator


def test_secret_ref_missing_source():
    ref = SecretRef("env://DEFINITELY_ABSENT_VAR")
    with pytest.raises(ConfigurationError):
        ref.resolve()


def test_secret_accessor_on_non_secret():
    cfg = load_config(environ={"UCOS_REGION": "us"})
    with pytest.raises(ConfigurationError):
        cfg.secret("region")


def test_file_not_found():
    with pytest.raises(ConfigurationError):
        load_config(config_file="/nonexistent/path/config.json", environ={})


def test_unsupported_file_type(tmp_path):
    path = tmp_path / "config.yaml"
    path.write_text("region: us", encoding="utf-8")
    with pytest.raises(ConfigurationError):
        load_config(config_file=path, environ={})


def test_invalid_json(tmp_path):
    path = tmp_path / "config.json"
    path.write_text("{not json", encoding="utf-8")
    with pytest.raises(ConfigurationError):
        load_config(config_file=path, environ={})


def test_non_object_json_root(tmp_path):
    path = tmp_path / "config.json"
    path.write_text("[1, 2, 3]", encoding="utf-8")
    with pytest.raises(ConfigurationError):
        load_config(config_file=path, environ={})


def test_config_repr_and_contains():
    cfg = Config({"a": 1}, Environment.DEVELOPMENT)
    assert "development" in repr(cfg)
    assert "a" in cfg


def test_secret_ref_equality_and_hash():
    a = SecretRef("env://X")
    b = SecretRef("env://X")
    c = SecretRef("env://Y")
    # __eq__ true path, false path (differing locator), and non-SecretRef branch
    assert a == b
    assert a != c
    assert a != "env://X"
    # __hash__ makes equal refs interchangeable in sets/dicts
    assert hash(a) == hash(b)
    assert {a, b, c} == {a, c}


def test_secret_ref_resolve_rejects_unsupported_scheme():
    # The scheme is validated in __init__, so this defensive branch in resolve()
    # is only reachable if the slot is mutated after construction.
    ref = SecretRef("env://X")
    ref.scheme = "vault"
    with pytest.raises(ConfigurationError):
        ref.resolve()


def test_get_bool_returns_native_bool():
    # Values sourced from env are always strings; a Config built directly may hold
    # native booleans, which get_bool must return unchanged.
    cfg = Config({"on": True, "off": False}, Environment.DEVELOPMENT)
    assert cfg.get_bool("on") is True
    assert cfg.get_bool("off") is False


def test_coerce_secrets_preserves_existing_secret_ref():
    # A secret-typed key already carrying a SecretRef is passed through untouched.
    ref = SecretRef("env://DB")
    result = _coerce_secrets({"db_password": ref})
    assert result["db_password"] is ref
