"""EC2-CAP-ADMIN-001 — Administrative permission-evaluation tests.

Covers permission administration as an evaluation view over the reused Identity
PermissionEngine: the effective administration-policy resolution, the derived
administrative action set, per-action checks, and the ``is_administrator`` derivation —
all authorization-derived (no new authority).
"""

from __future__ import annotations

from platform.administration.contracts import AdministrativeAction
from platform.administration.errors import AdministrationPermissionError
from platform.administration.permissions import AdministrativePermissions
from platform.foundation.identity import Principal, Role
from platform.identity.permissions import PermissionEngine
from platform.identity.roles import default_role_registry

import pytest


def _engine() -> PermissionEngine:
    return PermissionEngine(default_role_registry())


def _admin(tenant=None):
    return Principal.create("admin@x", [Role.PLATFORM_ADMINISTRATOR], tenant=tenant)


def _auditor():
    return Principal.create("aud@x", [Role.AUDITOR])


def _developer():
    return Principal.create("dev@x", [Role.DEVELOPER])


def test_requires_a_permission_engine():
    with pytest.raises(AdministrationPermissionError):
        AdministrativePermissions("nope")  # type: ignore[arg-type]


def test_administrator_is_granted_every_action():
    perms = AdministrativePermissions(_engine())
    actions = perms.actions_for(_admin())
    assert actions == frozenset(AdministrativeAction)
    assert perms.is_administrator(_admin()) is True


def test_auditor_holds_only_inspect():
    perms = AdministrativePermissions(_engine())
    actions = perms.actions_for(_auditor())
    assert actions == frozenset({AdministrativeAction.INSPECT})
    assert perms.can(_auditor(), AdministrativeAction.INSPECT) is True
    assert perms.can(_auditor(), AdministrativeAction.CONFIGURE) is False
    assert perms.is_administrator(_auditor()) is False


def test_developer_holds_no_administrative_action():
    perms = AdministrativePermissions(_engine())
    assert perms.actions_for(_developer()) == frozenset()
    assert perms.is_administrator(_developer()) is False


def test_resolve_returns_effective_permissions_on_the_admin_group():
    perms = AdministrativePermissions(_engine())
    effective = perms.resolve(_admin())
    assert effective.granted is True


def test_permissions_property_exposes_the_reused_engine():
    engine = _engine()
    assert AdministrativePermissions(engine).permissions is engine


def test_resolve_rejects_non_principal():
    with pytest.raises(AdministrationPermissionError):
        AdministrativePermissions(_engine()).resolve("nope")  # type: ignore[arg-type]


def test_can_rejects_non_action():
    with pytest.raises(AdministrationPermissionError):
        AdministrativePermissions(_engine()).can(_admin(), "configure")  # type: ignore[arg-type]
