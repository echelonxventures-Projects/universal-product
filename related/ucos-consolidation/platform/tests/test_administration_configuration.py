"""EC2-CAP-ADMIN-001 — Administrative configuration tests.

Covers the append-only operational configuration store: content-addressed settings,
scoped create/replace/get/remove, the append-only event log, value lookups with
defaults, scope listing, validation, determinism, and serialization.
"""

from __future__ import annotations

from platform.administration.configuration import (
    AdministrativeConfiguration,
    AdministrativeSetting,
)
from platform.administration.contracts import AdministrativeScope
from platform.administration.errors import AdministrationConfigurationError

import pytest


def test_setting_is_content_addressed_by_scope_tenant_key():
    a = AdministrativeSetting.create(AdministrativeScope.PLATFORM, "retention", "30d")
    b = AdministrativeSetting.create(AdministrativeScope.PLATFORM, "retention", "90d")
    # value does not change identity; scope+tenant+key does.
    assert a.setting_id == b.setting_id
    assert a.setting_id.startswith("UCOS-ASET-")
    c = AdministrativeSetting.create(AdministrativeScope.TENANT, "retention", "30d", tenant="acme")
    assert c.setting_id != a.setting_id


def test_setting_normalizes_key_and_rejects_bad_input():
    with pytest.raises(AdministrationConfigurationError):
        AdministrativeSetting.create(AdministrativeScope.PLATFORM, "", "v")
    with pytest.raises(AdministrationConfigurationError):
        AdministrativeSetting.create(AdministrativeScope.PLATFORM, "a b", "v")
    with pytest.raises(AdministrationConfigurationError):
        AdministrativeSetting.create(AdministrativeScope.PLATFORM, "k", 5)  # type: ignore[arg-type]
    with pytest.raises(AdministrationConfigurationError):
        AdministrativeSetting.create("platform", "k", "v")  # type: ignore[arg-type]


def test_set_creates_then_updates_and_records_events():
    config = AdministrativeConfiguration()
    created = config.set(AdministrativeScope.PLATFORM, "flag", "on", tick=1)
    assert created.value == "on"
    updated = config.set(AdministrativeScope.PLATFORM, "flag", "off", tick=2)
    assert updated.value == "off"
    actions = [e.action for e in config.events]
    assert actions == ["created", "updated"]
    assert config.events[0].to_dict()["action"] == "created"
    assert len(config) == 1


def test_get_and_has_and_value_of():
    config = AdministrativeConfiguration()
    config.set(AdministrativeScope.TENANT, "quota", "10", tick=1, tenant="acme")
    assert config.has(AdministrativeScope.TENANT, "quota", tenant="acme")
    assert config.get(AdministrativeScope.TENANT, "quota", tenant="acme").value == "10"
    assert config.value_of(AdministrativeScope.TENANT, "quota", tenant="acme") == "10"
    # a different tenant does not see it (scope isolation of the key space).
    assert not config.has(AdministrativeScope.TENANT, "quota", tenant="beta")
    assert config.value_of(AdministrativeScope.TENANT, "quota", tenant="beta", default="0") == "0"


def test_get_absent_is_fail_closed():
    config = AdministrativeConfiguration()
    with pytest.raises(AdministrationConfigurationError):
        config.get(AdministrativeScope.PLATFORM, "missing")


def test_get_rejects_bad_scope():
    config = AdministrativeConfiguration()
    with pytest.raises(AdministrationConfigurationError):
        config.get("platform", "k")  # type: ignore[arg-type]


def test_remove_setting_and_fail_closed_on_absent():
    config = AdministrativeConfiguration()
    config.set(AdministrativeScope.PLATFORM, "flag", "on", tick=1)
    removed = config.remove(AdministrativeScope.PLATFORM, "flag", tick=2)
    assert removed.key == "flag"
    assert not config.has(AdministrativeScope.PLATFORM, "flag")
    assert config.events[-1].action == "removed"
    with pytest.raises(AdministrationConfigurationError):
        config.remove(AdministrativeScope.PLATFORM, "flag", tick=3)


def test_settings_in_scope_is_ordered_and_tenant_filtered():
    config = AdministrativeConfiguration()
    config.set(AdministrativeScope.TENANT, "b", "1", tick=1, tenant="acme")
    config.set(AdministrativeScope.TENANT, "a", "2", tick=2, tenant="acme")
    config.set(AdministrativeScope.TENANT, "z", "3", tick=3, tenant="beta")
    keys = [s.key for s in config.settings_in(AdministrativeScope.TENANT, tenant="acme")]
    assert keys == ["a", "b"]


def test_settings_in_rejects_bad_scope():
    config = AdministrativeConfiguration()
    with pytest.raises(AdministrationConfigurationError):
        config.settings_in("platform")  # type: ignore[arg-type]


def test_all_and_to_dict_and_fingerprint_deterministic():
    def build() -> AdministrativeConfiguration:
        config = AdministrativeConfiguration()
        config.set(AdministrativeScope.PLATFORM, "a", "1", tick=1)
        config.set(AdministrativeScope.PLATFORM, "b", "2", tick=2)
        return config

    one, two = build(), build()
    assert one.fingerprint() == two.fingerprint()
    assert one.to_dict()["setting_count"] == 2
    assert [s.key for s in one.all()] == [s.key for s in two.all()]
