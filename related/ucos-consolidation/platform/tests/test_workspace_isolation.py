"""EC2-TASK-000085 — Workspace isolation tests (P3).

Covers the deterministic tenant/workspace isolation guard: global workspaces visible
to all, unscoped principals not confined, tenant-match allowed, and cross-tenant
denied — the P3 invariant that cross-tenant access is refused in 100% of cases.
"""

from __future__ import annotations

from platform.foundation.identity import Principal, Role
from platform.workspace.contracts import Workspace
from platform.workspace.errors import WorkspaceIsolationError
from platform.workspace.isolation import IsolationGuard, tenants_isolated

import pytest


def _principal(tenant: str | None) -> Principal:
    return Principal.create("u@x", [Role.DEVELOPER], tenant=tenant)


def _workspace(tenant: str | None) -> Workspace:
    return Workspace.create("s", "n", "o", tenant=tenant)


def test_tenants_isolated_pure_predicate():
    assert tenants_isolated("a", "b") is True
    assert tenants_isolated("a", "a") is False
    assert tenants_isolated(None, "b") is False  # unscoped principal not confined
    assert tenants_isolated("a", None) is False  # global workspace


def test_global_workspace_visible_to_all():
    guard = IsolationGuard()
    decision = guard.evaluate(_principal("acme"), _workspace(None))
    assert decision.allowed and decision.reason == "global-workspace"


def test_unscoped_principal_not_confined():
    guard = IsolationGuard()
    decision = guard.evaluate(_principal(None), _workspace("acme"))
    assert decision.allowed and decision.reason == "unscoped-principal"


def test_tenant_match_allowed():
    guard = IsolationGuard()
    decision = guard.evaluate(_principal("acme"), _workspace("acme"))
    assert decision.allowed and decision.reason == "tenant-match"


def test_cross_tenant_denied():
    guard = IsolationGuard()
    decision = guard.evaluate(_principal("acme"), _workspace("beta"))
    assert decision.allowed is False
    assert decision.reason == "tenant-isolation-violation"
    assert not guard.permits(_principal("acme"), _workspace("beta"))
    assert decision.to_dict()["workspace_tenant"] == "beta"


def test_guard_rejects_bad_inputs():
    guard = IsolationGuard()
    with pytest.raises(WorkspaceIsolationError):
        guard.evaluate("nope", _workspace("a"))  # type: ignore[arg-type]
    with pytest.raises(WorkspaceIsolationError):
        guard.evaluate(_principal("a"), "nope")  # type: ignore[arg-type]
