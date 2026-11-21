"""EC2-TASK-000057 — Platform identity model tests."""

from __future__ import annotations

from platform.foundation.errors import PlatformIdentityError
from platform.foundation.identity import (
    READ_ONLY_ROLES,
    SCOPED_ROLES,
    Permission,
    Principal,
    Role,
    all_roles,
)

import pytest


def test_nine_roles_defined():
    assert len(all_roles()) == 9
    assert Role.PLATFORM_ADMINISTRATOR in all_roles()
    assert Role.CERTIFICATION_AUTHORITY in all_roles()


def test_permissions_are_crud_x_a():
    assert {p.value for p in Permission} == {"create", "read", "execute", "administer"}


def test_principal_is_content_addressed_and_deterministic():
    a = Principal.create("alice", [Role.DEVELOPER])
    b = Principal.create("alice", [Role.DEVELOPER])
    assert a.principal_id == b.principal_id
    assert a.principal_id.startswith("UCOS-PRIN-")
    assert a.has_role(Role.DEVELOPER)
    assert a.has_any_role([Role.ARCHITECT, Role.DEVELOPER])
    assert a.is_scoped is False


def test_principal_scope_and_attributes():
    p = Principal.create("partner-1", [Role.PARTNER], tenant="ws-1", attributes={"org": "acme"})
    assert p.is_scoped is True
    assert p.tenant == "ws-1"
    assert p.to_dict()["attributes"] == {"org": "acme"}


def test_distinct_roles_yield_distinct_ids():
    a = Principal.create("bob", [Role.DEVELOPER])
    b = Principal.create("bob", [Role.OPERATOR])
    assert a.principal_id != b.principal_id


def test_principal_requires_subject():
    with pytest.raises(PlatformIdentityError):
        Principal.create("   ", [Role.DEVELOPER])


def test_principal_requires_role():
    with pytest.raises(PlatformIdentityError):
        Principal.create("x", [])


def test_principal_rejects_non_role():
    with pytest.raises(PlatformIdentityError):
        Principal.create("x", ["not-a-role"])


def test_role_classification_sets():
    assert SCOPED_ROLES == frozenset({Role.PARTNER, Role.INTEGRATOR})
    assert READ_ONLY_ROLES == frozenset({Role.AUDITOR, Role.CERTIFICATION_AUTHORITY})
