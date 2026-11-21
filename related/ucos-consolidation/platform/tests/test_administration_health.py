"""EC2-CAP-ADMIN-001 — Administrative health tests.

Covers the administration runtime health integration (reusing the L8 health model):
the two critical checks, a healthy baseline, and the inducible scope↔tenant integrity
fault that drives the integrity check to UNHEALTHY (OP-C1).
"""

from __future__ import annotations

from platform.administration.configuration import AdministrativeConfiguration
from platform.administration.contracts import AdministrativeScope
from platform.administration.health import (
    CONFIGURATION_CHECK,
    INTEGRITY_CHECK,
    AdministrationHealth,
    administration_health_checks,
)
from platform.administration.membership import AdministrativeMembershipRegistry
from platform.observability.contracts import HealthStatus

import pytest


def test_two_critical_checks_declared():
    checks = administration_health_checks()
    assert {c.name for c in checks} == {CONFIGURATION_CHECK, INTEGRITY_CHECK}
    assert all(c.critical for c in checks)


def test_construction_validates_components():
    config = AdministrativeConfiguration()
    members = AdministrativeMembershipRegistry()
    with pytest.raises(TypeError):
        AdministrationHealth("nope", members)  # type: ignore[arg-type]
    with pytest.raises(TypeError):
        AdministrationHealth(config, "nope")  # type: ignore[arg-type]


def test_healthy_when_all_memberships_consistent():
    config = AdministrativeConfiguration()
    members = AdministrativeMembershipRegistry()
    members.add(AdministrativeScope.PLATFORM, "platform", "UCOS-PRIN-a", "a@x", tick=1)
    members.add(AdministrativeScope.TENANT, "acme", "UCOS-PRIN-b", "b@x", tick=2, tenant="acme")
    health = AdministrationHealth(config, members)
    assert health.healthy is True
    assert health.probe()[INTEGRITY_CHECK] is HealthStatus.HEALTHY
    assert health.inconsistent_members() == ()


def test_inconsistent_membership_drives_unhealthy():
    config = AdministrativeConfiguration()
    members = AdministrativeMembershipRegistry()
    # A tenant-scoped administrator with no tenant boundary is an induced fault (OP-C1).
    members.add(AdministrativeScope.TENANT, "acme", "UCOS-PRIN-a", "a@x", tick=1, tenant=None)
    health = AdministrationHealth(config, members)
    assert health.healthy is False
    assert health.probe()[INTEGRITY_CHECK] is HealthStatus.UNHEALTHY
    assert len(health.inconsistent_members()) == 1
    assert health.probe()[CONFIGURATION_CHECK] is HealthStatus.HEALTHY
