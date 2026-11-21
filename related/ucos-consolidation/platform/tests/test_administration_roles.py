"""EC2-CAP-ADMIN-001 — Administrative role-view tests.

Covers role administration as a read-only projection over the §3.2 RBAC matrix: which
roles hold administrative grants, which can administer, the verb sets, and the fact
that the runtime creates no new authority (only Platform Administrator administers;
Auditor reads; nobody else has any administration-policy grant).
"""

from __future__ import annotations

from platform.administration.errors import AdministrationRoleError
from platform.administration.roles import AdministrativeRoleView
from platform.foundation.identity import Permission, Role
from platform.identity.roles import default_role_registry

import pytest


def _view() -> AdministrativeRoleView:
    return AdministrativeRoleView(default_role_registry())


def test_requires_a_role_registry():
    with pytest.raises(AdministrationRoleError):
        AdministrativeRoleView("nope")  # type: ignore[arg-type]


def test_roles_property_exposes_the_reused_registry():
    registry = default_role_registry()
    assert AdministrativeRoleView(registry).roles is registry


def test_administrative_roles_are_exactly_admin_and_auditor():
    view = _view()
    assert set(view.administrative_roles()) == {
        Role.PLATFORM_ADMINISTRATOR,
        Role.AUDITOR,
    }


def test_only_platform_administrator_can_administer():
    view = _view()
    assert view.administering_roles() == (Role.PLATFORM_ADMINISTRATOR,)
    assert view.can_administer(Role.PLATFORM_ADMINISTRATOR) is True
    assert view.can_administer(Role.AUDITOR) is False
    assert view.can_administer(Role.DEVELOPER) is False


def test_permissions_of_reflects_the_matrix():
    view = _view()
    assert Permission.ADMINISTER in view.permissions_of(Role.PLATFORM_ADMINISTRATOR)
    assert view.permissions_of(Role.AUDITOR) == frozenset({Permission.READ})
    assert view.permissions_of(Role.DEVELOPER) == frozenset()


def test_grant_for_returns_none_when_no_grant():
    view = _view()
    assert view.grant_for(Role.DEVELOPER) is None
    assert view.grant_for(Role.PLATFORM_ADMINISTRATOR) is not None


def test_grant_for_rejects_non_role():
    with pytest.raises(AdministrationRoleError):
        _view().grant_for("developer")  # type: ignore[arg-type]


def test_to_dict_and_fingerprint_are_deterministic():
    assert _view().fingerprint() == _view().fingerprint()
    data = _view().to_dict()
    assert data["group"] == "administration-policy"
    roles = {r["role"] for r in data["administrative_roles"]}
    assert roles == {"platform-administrator", "auditor"}
