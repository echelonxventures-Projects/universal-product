"""EC2-TASK-000065 — Role registry + §3.2 RBAC matrix tests."""

from __future__ import annotations

from platform.foundation.identity import Permission, Role
from platform.identity.contracts import CapabilityGroup
from platform.identity.errors import RoleRegistryError
from platform.identity.roles import (
    RoleDefinition,
    RoleGrant,
    RoleRegistry,
    default_role_definitions,
    default_role_registry,
)

import pytest

C, R, X, A = (
    Permission.CREATE,
    Permission.READ,
    Permission.EXECUTE,
    Permission.ADMINISTER,
)


def test_default_registry_has_nine_roles():
    reg = default_role_registry()
    assert len(reg) == 9
    assert reg.roles == tuple(Role)


def _grant(reg: RoleRegistry, role: Role, group: CapabilityGroup):
    return reg.get(role).grant_for(group)


def test_admin_is_administer_on_admin_groups():
    reg = default_role_registry()
    for group in (
        CapabilityGroup.USER_ROLE_QUOTA_ADMIN,
        CapabilityGroup.ADMINISTRATION_POLICY,
        CapabilityGroup.RUNTIME_OPERATIONS,
        CapabilityGroup.API_ACCESS,
    ):
        assert _grant(reg, Role.PLATFORM_ADMINISTRATOR, group).permissions == frozenset({A})
    # Admin has only READ on the pipeline explorers / certification ledger.
    ledger = _grant(reg, Role.PLATFORM_ADMINISTRATOR, CapabilityGroup.CERTIFICATION_LEDGER)
    assert ledger.permissions == frozenset({R})


def test_admin_has_no_grant_where_matrix_is_dash():
    reg = default_role_registry()
    # Non-admin roles have no user/role/quota admin grant.
    for role in Role:
        if role is Role.PLATFORM_ADMINISTRATOR:
            continue
        assert _grant(reg, role, CapabilityGroup.USER_ROLE_QUOTA_ADMIN) is None


def test_developer_generation_requests_crx():
    reg = default_role_registry()
    grant = _grant(reg, Role.DEVELOPER, CapabilityGroup.GENERATION_REQUESTS)
    assert grant.permissions == frozenset({C, R, X})
    assert grant.scoped is False


def test_developer_blueprint_catalog_read_only():
    reg = default_role_registry()
    grant = _grant(reg, Role.DEVELOPER, CapabilityGroup.BLUEPRINT_CATALOG)
    assert grant.permissions == frozenset({R})


def test_operator_runtime_execute_and_no_blueprint():
    reg = default_role_registry()
    ops_runtime = _grant(reg, Role.OPERATOR, CapabilityGroup.RUNTIME_OPERATIONS)
    assert ops_runtime.permissions == frozenset({X})
    assert _grant(reg, Role.OPERATOR, CapabilityGroup.BLUEPRINT_AUTHORING) is None
    assert _grant(reg, Role.OPERATOR, CapabilityGroup.GENERATION_REQUESTS) is None


def test_auditor_is_read_only_everywhere_it_has_access():
    reg = default_role_registry()
    definition = reg.get(Role.AUDITOR)
    for group in definition.groups:
        assert definition.grant_for(group).permissions == frozenset({R})


def test_certification_authority_attest_on_ledger():
    reg = default_role_registry()
    grant = _grant(reg, Role.CERTIFICATION_AUTHORITY, CapabilityGroup.CERTIFICATION_LEDGER)
    assert grant.attest is True
    assert R in grant.permissions


def test_business_user_artifact_explorer_is_scoped():
    reg = default_role_registry()
    grant = _grant(reg, Role.BUSINESS_USER, CapabilityGroup.ARTIFACT_EXPLORER)
    assert grant.scoped is True
    # But its execution dashboard access is not scoped.
    assert _grant(reg, Role.BUSINESS_USER, CapabilityGroup.EXECUTION_DASHBOARD).scoped is False


def test_partner_data_plane_scoped_but_portal_not():
    reg = default_role_registry()
    definition = reg.get(Role.PARTNER)
    # Per §3.2, the Partner's portal-navigation and identity-self grants are plain R
    # (not scoped); every other (data-plane) grant it holds is tenant-scoped.
    unscoped_groups = {
        CapabilityGroup.PORTAL_NAVIGATION,
        CapabilityGroup.IDENTITY_SESSIONS_SELF,
    }
    for group in definition.groups:
        grant = definition.grant_for(group)
        if group in unscoped_groups:
            assert grant.scoped is False, group
        else:
            assert grant.scoped is True, group


def test_integrator_has_no_portal_access():
    reg = default_role_registry()
    assert _grant(reg, Role.INTEGRATOR, CapabilityGroup.PORTAL_NAVIGATION) is None
    # Integrator identity/self session is read.
    self_grant = _grant(reg, Role.INTEGRATOR, CapabilityGroup.IDENTITY_SESSIONS_SELF)
    assert self_grant.permissions == frozenset({R})


def test_partner_generation_requests_crx_scoped():
    reg = default_role_registry()
    grant = _grant(reg, Role.PARTNER, CapabilityGroup.GENERATION_REQUESTS)
    assert grant.permissions == frozenset({C, R, X})
    assert grant.scoped is True


def test_registry_rejects_duplicate_role():
    reg = default_role_registry()
    with pytest.raises(RoleRegistryError):
        reg.register(RoleDefinition(role=Role.DEVELOPER, grants={}))


def test_registry_rejects_non_definition_and_absent():
    reg = RoleRegistry()
    with pytest.raises(RoleRegistryError):
        reg.register("not-a-definition")
    with pytest.raises(RoleRegistryError):
        reg.get(Role.DEVELOPER)


def test_grant_validation():
    with pytest.raises(RoleRegistryError):
        RoleGrant(group=CapabilityGroup.API_ACCESS, permissions=frozenset())
    with pytest.raises(RoleRegistryError):
        RoleGrant(group="nope", permissions=frozenset({R}))
    with pytest.raises(RoleRegistryError):
        RoleGrant(group=CapabilityGroup.API_ACCESS, permissions=frozenset({"x"}))


def test_role_definition_rejects_mismatched_group_key():
    good = RoleGrant(group=CapabilityGroup.API_ACCESS, permissions=frozenset({X}))
    with pytest.raises(RoleRegistryError):
        RoleDefinition(role=Role.DEVELOPER, grants={CapabilityGroup.PORTAL_NAVIGATION: good})


def test_role_definition_requires_role():
    with pytest.raises(RoleRegistryError):
        RoleDefinition(role="not-a-role", grants={})


def test_matrix_is_deterministic():
    a = default_role_registry()
    b = default_role_registry()
    assert a.fingerprint() == b.fingerprint()
    assert len(default_role_definitions()) == 9


def test_groups_returned_in_stable_order():
    definition = default_role_registry().get(Role.AUDITOR)
    groups = definition.groups
    assert list(groups) == sorted(groups, key=lambda g: list(CapabilityGroup).index(g))


def test_registry_contains_and_len():
    reg = default_role_registry()
    assert Role.DEVELOPER in reg
    assert Role.PARTNER in reg


def test_parse_grant_rejects_unknown_verb():
    from platform.identity.roles import _parse_grant

    with pytest.raises(RoleRegistryError):
        _parse_grant(CapabilityGroup.API_ACCESS, "Z")


def test_parse_grant_empty_is_none():
    from platform.identity.roles import _parse_grant

    assert _parse_grant(CapabilityGroup.API_ACCESS, "") is None
    assert _parse_grant(CapabilityGroup.API_ACCESS, "  ") is None
