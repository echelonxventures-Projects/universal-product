"""Tests for the Universal Portal application read model (UCOS-EPIC-008 / T8)."""

from __future__ import annotations

from platform.universal_portal.applications import (
    ApplicationDescriptor,
    ApplicationRegistry,
    ApplicationView,
)
from platform.universal_portal.contracts import PortalApplication
from platform.universal_portal.errors import ApplicationBindingError

import pytest


def test_empty_registry_binds_nothing_but_enumerates_all():
    reg = ApplicationRegistry()
    assert reg.bound_count == 0
    assert len(reg.applications()) == 8
    assert all(not d.bound for d in reg.descriptors())


def test_registry_binds_provider_and_reports_snapshot():
    reg = ApplicationRegistry({PortalApplication.ADMINISTRATION_PORTAL: lambda: _Svc({"k": "v"})})
    assert reg.is_bound(PortalApplication.ADMINISTRATION_PORTAL)
    assert reg.bound_count == 1
    assert reg.snapshot(PortalApplication.ADMINISTRATION_PORTAL) == {"k": "v"}
    assert reg.snapshot(PortalApplication.VALIDATION_DASHBOARD) is None


class _Svc:
    def __init__(self, payload):
        self._payload = payload

    def to_dict(self):
        return self._payload


def test_registry_rejects_bad_key():
    with pytest.raises(ApplicationBindingError):
        ApplicationRegistry({"nope": lambda: _Svc({})})


def test_registry_rejects_non_callable_provider():
    with pytest.raises(ApplicationBindingError):
        ApplicationRegistry({PortalApplication.ADMINISTRATION_PORTAL: 123})


def test_is_bound_rejects_bad_input():
    with pytest.raises(ApplicationBindingError):
        ApplicationRegistry().is_bound("nope")


def test_snapshot_requires_to_dict_provider():
    reg = ApplicationRegistry({PortalApplication.ADMINISTRATION_PORTAL: lambda: object()})
    with pytest.raises(ApplicationBindingError):
        reg.snapshot(PortalApplication.ADMINISTRATION_PORTAL)


def test_snapshot_requires_dict_result():
    reg = ApplicationRegistry({PortalApplication.ADMINISTRATION_PORTAL: lambda: _Svc(["x"])})
    with pytest.raises(ApplicationBindingError):
        reg.snapshot(PortalApplication.ADMINISTRATION_PORTAL)


def test_snapshot_rejects_bad_input():
    with pytest.raises(ApplicationBindingError):
        ApplicationRegistry().snapshot("nope")


def test_descriptor_reflects_binding_and_serializes():
    reg = ApplicationRegistry({PortalApplication.MEASUREMENT_DASHBOARD: lambda: _Svc({})})
    d = reg.descriptor(PortalApplication.MEASUREMENT_DASHBOARD)
    assert isinstance(d, ApplicationDescriptor)
    assert d.bound is True
    body = d.to_dict()
    assert body["application"] == "measurement-dashboard"
    assert body["required_permission"] == "read"
    assert body["consumed_contracts"]


def test_registry_fingerprint_is_deterministic_and_binding_sensitive():
    empty = ApplicationRegistry().fingerprint()
    bound = ApplicationRegistry(
        {PortalApplication.ADMINISTRATION_PORTAL: lambda: _Svc({})}
    ).fingerprint()
    assert empty == ApplicationRegistry().fingerprint()
    assert empty != bound


def test_registry_helpers():
    reg = ApplicationRegistry()
    assert reg.group(PortalApplication.VALIDATION_DASHBOARD).value == "validation-explorer"
    assert reg.section(PortalApplication.VALIDATION_DASHBOARD).value == "dashboards"
    assert reg.title(PortalApplication.VALIDATION_DASHBOARD) == "Validation Dashboard"
    assert reg.permission(PortalApplication.VALIDATION_DASHBOARD).value == "read"
    assert reg.consumed_contracts(PortalApplication.VALIDATION_DASHBOARD)
    assert reg.surface(PortalApplication.VALIDATION_DASHBOARD).application is (
        PortalApplication.VALIDATION_DASHBOARD
    )


def test_application_view_served_semantics_and_content_address():
    served = ApplicationView.create(
        PortalApplication.ADMINISTRATION_PORTAL,
        authorized=True,
        available=True,
        reason="permit",
        snapshot={"ok": True},
    )
    assert served.served is True
    assert served.view_id.startswith("UCOS-T8VEW-")
    assert served.to_dict()["served"] is True

    denied = ApplicationView.create(
        PortalApplication.ADMINISTRATION_PORTAL,
        authorized=False,
        available=True,
        reason="no-grant",
        snapshot=None,
    )
    assert denied.served is False
    assert denied.snapshot is None

    unbound = ApplicationView.create(
        PortalApplication.ADMINISTRATION_PORTAL,
        authorized=True,
        available=False,
        reason="permit",
        snapshot=None,
    )
    assert unbound.served is False


def test_registry_to_dict_counts():
    reg = ApplicationRegistry({PortalApplication.ADMINISTRATION_PORTAL: lambda: _Svc({})})
    body = reg.to_dict()
    assert body["application_count"] == 8
    assert body["bound_count"] == 1
    assert len(body["applications"]) == 8


def test_descriptor_rejects_bad_input():
    with pytest.raises(ApplicationBindingError):
        ApplicationRegistry().descriptor("nope")
