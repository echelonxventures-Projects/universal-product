"""EC2-TASK-000062 — Platform bootstrap architecture tests."""

from __future__ import annotations

from platform.foundation.bootstrap import (
    BOOTSTRAP_EVENT,
    PlatformContext,
    bootstrap_platform,
)
from platform.foundation.capabilities import CapabilityKind
from platform.foundation.config import load_platform_config
from platform.foundation.errors import BootstrapError

import pytest


def test_bootstrap_composes_foundation():
    ctx = bootstrap_platform(load_platform_config(environ={}))
    assert isinstance(ctx, PlatformContext)
    assert ctx.program_id == "EC-2"
    assert ctx.platform_name == "UCOS Platform"
    assert len(ctx.capabilities) == 31
    assert len(ctx.capabilities.of_kind(CapabilityKind.ENGINE)) == 13
    assert ctx.contracts is ctx.services.contracts


def test_bootstrap_emits_deterministic_event():
    ctx = bootstrap_platform(load_platform_config(environ={}))
    assert len(ctx.events) == 1
    event = ctx.events.events[0]
    assert event.event_type == BOOTSTRAP_EVENT
    assert event.payload["fingerprint"] == ctx.fingerprint()


def test_bootstrap_is_deterministic():
    a = bootstrap_platform(load_platform_config(environ={}))
    b = bootstrap_platform(load_platform_config(environ={}))
    assert a.fingerprint() == b.fingerprint()


def test_bootstrap_without_seed_is_empty_catalog():
    ctx = bootstrap_platform(load_platform_config(environ={}), seed_capabilities=False)
    assert len(ctx.capabilities) == 0


def test_bootstrap_default_config_loads():
    ctx = bootstrap_platform()
    assert ctx.config.environment.value in {
        "development",
        "testing",
        "qa",
        "staging",
        "production",
    }


def test_engine_contract_refs_exposed():
    ctx = bootstrap_platform(load_platform_config(environ={}))
    refs = ctx.engine_contract_refs()
    assert "engine.registry.read" in refs
    assert "engine.certification.certify" in refs


def test_summary_reports_composition():
    ctx = bootstrap_platform(load_platform_config(environ={}))
    summary = ctx.summary()
    assert summary["program_id"] == "EC-2"
    assert summary["capabilities"] == 31
    assert summary["engine_capabilities"] == 13
    assert summary["services"] == 0


def test_bootstrap_failclosed_on_bad_capability(monkeypatch):
    import platform.foundation.bootstrap as boot

    def _boom():
        raise ValueError("seed failure")

    monkeypatch.setattr(boot, "default_capability_catalog", _boom)
    with pytest.raises(BootstrapError) as exc:
        bootstrap_platform(load_platform_config(environ={}))
    assert exc.value.context["detail"] == "seed failure"


def test_bootstrap_reraises_bootstrap_error(monkeypatch):
    import platform.foundation.bootstrap as boot

    def _boom():
        raise BootstrapError("explicit bootstrap failure", detail="explicit")

    # a BootstrapError raised inside the try body is re-raised verbatim (not wrapped)
    monkeypatch.setattr(boot, "default_capability_catalog", _boom)
    with pytest.raises(BootstrapError) as exc:
        bootstrap_platform(load_platform_config(environ={}))
    assert exc.value.message == "explicit bootstrap failure"
    assert exc.value.context["detail"] == "explicit"
