"""EC2-TASK-000066 — Permission engine tests."""

from __future__ import annotations

from platform.foundation.identity import Permission, Principal, Role
from platform.identity.contracts import CapabilityGroup
from platform.identity.errors import PermissionResolutionError
from platform.identity.permissions import PermissionEngine, expand_permissions
from platform.identity.roles import default_role_registry

import pytest

C, R, X, A = (
    Permission.CREATE,
    Permission.READ,
    Permission.EXECUTE,
    Permission.ADMINISTER,
)


def _engine() -> PermissionEngine:
    return PermissionEngine(default_role_registry())


def test_administer_expands_to_full_verb_set():
    assert expand_permissions(frozenset({A})) == frozenset({C, R, X, A})
    assert expand_permissions(frozenset({R})) == frozenset({R})


def test_admin_resolves_full_set_on_admin_group():
    eng = _engine()
    admin = Principal.create("root", [Role.PLATFORM_ADMINISTRATOR])
    eff = eng.resolve(admin, CapabilityGroup.USER_ROLE_QUOTA_ADMIN)
    assert eff.permissions == frozenset({C, R, X, A})
    assert eff.granted is True
    assert eng.has_permission(admin, CapabilityGroup.USER_ROLE_QUOTA_ADMIN, C)


def test_developer_generation_requests():
    eng = _engine()
    dev = Principal.create("dev", [Role.DEVELOPER])
    eff = eng.resolve(dev, CapabilityGroup.GENERATION_REQUESTS)
    assert eff.permissions == frozenset({C, R, X})
    assert eff.scoped is False


def test_no_grant_is_empty_not_error():
    eng = _engine()
    dev = Principal.create("dev", [Role.DEVELOPER])
    eff = eng.resolve(dev, CapabilityGroup.USER_ROLE_QUOTA_ADMIN)
    assert eff.granted is False
    assert eff.permissions == frozenset()
    assert eng.has_permission(dev, CapabilityGroup.USER_ROLE_QUOTA_ADMIN, R) is False


def test_union_of_multiple_roles_widens_access():
    eng = _engine()
    multi = Principal.create("multi", [Role.OPERATOR, Role.DEVELOPER])
    # Developer has C/R/X on generation; Operator has none there -> union = C/R/X.
    eff = eng.resolve(multi, CapabilityGroup.GENERATION_REQUESTS)
    assert eff.permissions == frozenset({C, R, X})
    assert eff.contributing_roles == frozenset({Role.DEVELOPER})


def test_scoped_only_when_all_contributors_scoped():
    eng = _engine()
    # Partner (scoped) + Developer (unscoped) on generation -> unscoped effective.
    mixed = Principal.create("mix", [Role.PARTNER, Role.DEVELOPER], tenant="ws-1")
    eff = eng.resolve(mixed, CapabilityGroup.GENERATION_REQUESTS)
    assert eff.scoped is False
    # Partner alone -> scoped.
    partner = Principal.create("prt", [Role.PARTNER], tenant="ws-1")
    assert eng.resolve(partner, CapabilityGroup.GENERATION_REQUESTS).scoped is True


def test_attest_carried_from_cert_authority():
    eng = _engine()
    ca = Principal.create("ca", [Role.CERTIFICATION_AUTHORITY])
    eff = eng.resolve(ca, CapabilityGroup.CERTIFICATION_LEDGER)
    assert eff.attest is True


def test_resolve_all_returns_only_granted_groups_in_order():
    eng = _engine()
    dev = Principal.create("dev", [Role.DEVELOPER])
    resolved = eng.resolve_all(dev)
    groups = [ep.group for ep in resolved]
    assert CapabilityGroup.USER_ROLE_QUOTA_ADMIN not in groups
    assert CapabilityGroup.GENERATION_REQUESTS in groups
    assert groups == sorted(groups, key=lambda g: list(CapabilityGroup).index(g))


def test_effective_permissions_to_dict():
    eng = _engine()
    dev = Principal.create("dev", [Role.DEVELOPER])
    d = eng.resolve(dev, CapabilityGroup.GENERATION_REQUESTS).to_dict()
    assert d["group"] == CapabilityGroup.GENERATION_REQUESTS.value
    assert set(d["permissions"]) == {"create", "read", "execute"}


def test_engine_input_validation():
    with pytest.raises(PermissionResolutionError):
        PermissionEngine("not-a-registry")
    eng = _engine()
    dev = Principal.create("dev", [Role.DEVELOPER])
    with pytest.raises(PermissionResolutionError):
        eng.resolve("not-a-principal", CapabilityGroup.API_ACCESS)
    with pytest.raises(PermissionResolutionError):
        eng.resolve(dev, "not-a-group")
    with pytest.raises(PermissionResolutionError):
        eng.has_permission(dev, CapabilityGroup.API_ACCESS, "not-a-permission")


def test_unknown_role_fails_closed():
    # A role registry missing a role the principal bears -> fail-closed.
    from platform.identity.roles import RoleRegistry, default_role_definitions

    partial = RoleRegistry()
    for definition in default_role_definitions():
        if definition.role is not Role.OPERATOR:
            partial.register(definition)
    eng = PermissionEngine(partial)
    ops = Principal.create("ops", [Role.OPERATOR])
    with pytest.raises(PermissionResolutionError):
        eng.resolve(ops, CapabilityGroup.RUNTIME_OPERATIONS)


def test_engine_exposes_role_registry():
    reg = default_role_registry()
    eng = PermissionEngine(reg)
    assert eng.roles is reg
