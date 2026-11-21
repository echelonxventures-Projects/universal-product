"""EC2-TASK-000088 — Workspace health tests.

Covers the workspace runtime health integration, which reuses the certified L8
Observability health model (no new health machinery): the two critical checks, the
deterministic probe over the workspace + membership registries, orphaned-membership
detection (an induced integrity fault → UNHEALTHY, OP-C1), and fail-closed
construction.
"""

from __future__ import annotations

from platform.observability.contracts import HealthStatus
from platform.observability.health import HealthCheck
from platform.workspace.contracts import MemberRole
from platform.workspace.health import (
    INTEGRITY_CHECK,
    REGISTRY_CHECK,
    WorkspaceHealth,
    workspace_health_checks,
)
from platform.workspace.membership import MembershipRegistry
from platform.workspace.registration import WorkspaceRegistry

import pytest


def test_health_checks_are_two_critical_checks_in_stable_order():
    checks = workspace_health_checks()
    assert all(isinstance(c, HealthCheck) for c in checks)
    assert [c.name for c in checks] == [REGISTRY_CHECK, INTEGRITY_CHECK]
    assert all(c.critical for c in checks)


def test_construction_is_fail_closed():
    with pytest.raises(TypeError):
        WorkspaceHealth("nope", MembershipRegistry())  # type: ignore[arg-type]
    with pytest.raises(TypeError):
        WorkspaceHealth(WorkspaceRegistry(), "nope")  # type: ignore[arg-type]


def test_probe_is_healthy_when_every_membership_references_a_workspace():
    reg = WorkspaceRegistry()
    membership = MembershipRegistry()
    ws = reg.create("s", "n", "o")
    membership.add(ws.workspace_id, "UCOS-PRIN-1", "a@x", MemberRole.OWNER, tick=0)
    health = WorkspaceHealth(reg, membership)
    assert health.orphaned_membership_workspaces() == ()
    probe = health.probe()
    assert probe[REGISTRY_CHECK] is HealthStatus.HEALTHY
    assert probe[INTEGRITY_CHECK] is HealthStatus.HEALTHY
    assert health.healthy is True


def test_orphaned_membership_drives_integrity_unhealthy():
    reg = WorkspaceRegistry()
    membership = MembershipRegistry()
    # A membership referencing an unregistered workspace is an integrity fault (OP-C1).
    membership.add("UCOS-WSPC-orphan", "UCOS-PRIN-1", "a@x", MemberRole.OWNER, tick=0)
    health = WorkspaceHealth(reg, membership)
    assert health.orphaned_membership_workspaces() == ("UCOS-WSPC-orphan",)
    probe = health.probe()
    assert probe[REGISTRY_CHECK] is HealthStatus.HEALTHY
    assert probe[INTEGRITY_CHECK] is HealthStatus.UNHEALTHY
    assert health.healthy is False


def test_empty_registries_are_healthy():
    health = WorkspaceHealth(WorkspaceRegistry(), MembershipRegistry())
    assert health.healthy is True
