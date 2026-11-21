"""EC2-TASK-000056 — Platform configuration tests."""

from __future__ import annotations

from platform.foundation.config import (
    DEFAULT_API_VERSION,
    PlatformConfig,
    load_platform_config,
)
from platform.foundation.errors import PlatformConfigError

import pytest


def test_load_defaults():
    cfg = load_platform_config(environ={})
    assert cfg.program_id == "EC-2"
    assert cfg.platform_name == "UCOS Platform"
    assert cfg.api_version == DEFAULT_API_VERSION
    assert cfg.multi_tenant is True
    assert cfg.environment.value == "development"


def test_env_overrides_are_applied():
    environ = {
        "UCOS_ENV": "staging",
        "UCOS_PLATFORM_NAME": "UCOS Platform (staging)",
        "UCOS_PLATFORM_API_VERSION": "2.0.0",
        "UCOS_PLATFORM_MULTI_TENANT": "false",
    }
    cfg = load_platform_config(environ=environ)
    assert cfg.environment.value == "staging"
    assert cfg.platform_name == "UCOS Platform (staging)"
    assert cfg.api_version == "2.0.0"
    assert cfg.multi_tenant is False


def test_fingerprint_is_deterministic_and_redacted():
    a = load_platform_config(environ={"UCOS_DB_TOKEN": "env://DB_TOKEN"})
    b = load_platform_config(environ={"UCOS_DB_TOKEN": "env://DB_TOKEN"})
    assert a.fingerprint() == b.fingerprint()
    # secret rendered redacted, never raw
    assert a.to_dict()["settings"]["db_token"] == "***"


def test_secret_accessor_returns_reference():
    cfg = load_platform_config(environ={"UCOS_API_KEY": "env://API_KEY"})
    ref = cfg.secret("api_key")
    assert ref.scheme == "env" and ref.locator == "API_KEY"


def test_get_passthrough():
    cfg = load_platform_config(environ={"UCOS_FEATURE_X": "on"})
    assert cfg.get("feature_x") == "on"
    assert cfg.get("missing", "default") == "default"


def test_from_config_rejects_non_config():
    with pytest.raises(PlatformConfigError):
        PlatformConfig.from_config(object())
