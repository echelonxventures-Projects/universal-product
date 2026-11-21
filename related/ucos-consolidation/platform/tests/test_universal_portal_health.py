"""Tests for the Universal Portal health report (UCOS-EPIC-008 / T8)."""

from __future__ import annotations

from platform.tests.universal_portal_helpers import core_providers
from platform.universal_portal.applications import ApplicationRegistry
from platform.universal_portal.contracts import PortalApplication
from platform.universal_portal.errors import UniversalPortalServiceError
from platform.universal_portal.health import (
    UniversalPortalHealth,
    universal_portal_health_report,
)

import pytest


def test_health_passes_when_core_bound_and_shell_accessible():
    reg = ApplicationRegistry(core_providers())
    report = universal_portal_health_report(reg, portal_accessibility_passed=True)
    assert isinstance(report, UniversalPortalHealth)
    assert report.passed is True
    names = {n for n, _ in report.checks}
    assert "core-dashboards-bound" in names
    assert report.report_id.startswith("UCOS-T8HLTH-")


def test_health_fails_when_core_unbound():
    report = universal_portal_health_report(ApplicationRegistry(), portal_accessibility_passed=True)
    assert report.passed is False
    checks = dict(report.checks)
    assert checks["core-dashboards-bound"] is False
    assert checks["catalog-complete"] is True


def test_health_fails_when_shell_inaccessible():
    reg = ApplicationRegistry(core_providers())
    report = universal_portal_health_report(reg, portal_accessibility_passed=False)
    assert report.passed is False
    assert dict(report.checks)["portal-shell-accessible"] is False


def test_health_is_deterministic():
    reg = ApplicationRegistry(core_providers())
    a = universal_portal_health_report(reg, portal_accessibility_passed=True)
    b = universal_portal_health_report(reg, portal_accessibility_passed=True)
    assert a.fingerprint() == b.fingerprint()


def test_missing_core_dashboard_fails_health():
    providers = core_providers()
    del providers[PortalApplication.CERTIFICATION_DASHBOARD]
    report = universal_portal_health_report(
        ApplicationRegistry(providers), portal_accessibility_passed=True
    )
    assert report.passed is False


def test_health_requires_registry():
    with pytest.raises(UniversalPortalServiceError):
        universal_portal_health_report(object(), portal_accessibility_passed=True)
