"""EC2-CAP-ADMIN-001 — Administration contracts tests.

Covers the administrative vocabulary and the published contract surface: scopes,
domains, actions, operational states, the action→permission mapping (no new authority),
the content-addressed :class:`AdministrativeTarget`, and the versioned contract refs.
"""

from __future__ import annotations

from platform.administration.contracts import (
    ADMINISTRATION_CONTRACT_VERSION,
    ADMINISTRATION_CONTRACTS,
    ADMINISTRATION_GROUP,
    AdministrativeAction,
    AdministrativeDomain,
    AdministrativeScope,
    AdministrativeTarget,
    OperationalState,
    administration_contract,
    all_administrative_actions,
    all_administrative_scopes,
    all_operational_states,
    default_administration_contracts,
    required_permission,
)
from platform.administration.errors import AdministrationContractError
from platform.foundation.identity import Permission
from platform.identity.contracts import CapabilityGroup

import pytest


def test_administration_group_is_the_rbac_administration_row():
    assert ADMINISTRATION_GROUP is CapabilityGroup.ADMINISTRATION_POLICY


def test_enumerations_are_stable():
    assert all_administrative_scopes() == tuple(AdministrativeScope)
    assert all_administrative_actions() == tuple(AdministrativeAction)
    assert all_operational_states() == tuple(OperationalState)


@pytest.mark.parametrize(
    "action, permission",
    [
        (AdministrativeAction.INSPECT, Permission.READ),
        (AdministrativeAction.CONFIGURE, Permission.ADMINISTER),
        (AdministrativeAction.ASSIGN, Permission.ADMINISTER),
        (AdministrativeAction.REVOKE, Permission.ADMINISTER),
        (AdministrativeAction.SUSPEND, Permission.ADMINISTER),
        (AdministrativeAction.ACTIVATE, Permission.ADMINISTER),
    ],
)
def test_required_permission_maps_each_action(action, permission):
    assert required_permission(action) is permission


def test_required_permission_rejects_non_action():
    with pytest.raises(AdministrationContractError):
        required_permission("configure")  # type: ignore[arg-type]


def test_only_inspect_needs_read_every_other_action_needs_administer():
    for action in all_administrative_actions():
        if action is AdministrativeAction.INSPECT:
            assert required_permission(action) is Permission.READ
        else:
            assert required_permission(action) is Permission.ADMINISTER


def test_target_create_is_content_addressed_and_deterministic():
    a = AdministrativeTarget.create(
        AdministrativeScope.TENANT, AdministrativeDomain.CONFIGURATION, "acme", tenant="acme"
    )
    b = AdministrativeTarget.create(
        AdministrativeScope.TENANT, AdministrativeDomain.CONFIGURATION, "acme", tenant="acme"
    )
    assert a.target_id == b.target_id
    assert a.target_id.startswith("UCOS-ATGT-")
    assert a.fingerprint() == b.fingerprint()


def test_target_platform_helper():
    target = AdministrativeTarget.platform()
    assert target.scope is AdministrativeScope.PLATFORM
    assert target.identifier == "platform"
    assert target.tenant is None
    assert target.to_dict()["scope"] == "platform"


def test_target_rejects_bad_scope():
    with pytest.raises(AdministrationContractError):
        AdministrativeTarget.create("platform", AdministrativeDomain.PLATFORM, "x")  # type: ignore[arg-type]


def test_target_rejects_bad_domain():
    with pytest.raises(AdministrationContractError):
        AdministrativeTarget.create(AdministrativeScope.PLATFORM, "platform", "x")  # type: ignore[arg-type]


@pytest.mark.parametrize("identifier", ["", "   ", 5])
def test_target_rejects_bad_identifier(identifier):
    with pytest.raises(AdministrationContractError):
        AdministrativeTarget.create(
            AdministrativeScope.TENANT, AdministrativeDomain.TENANT, identifier, tenant="t"
        )  # type: ignore[arg-type]


def test_platform_scoped_target_must_not_carry_a_tenant():
    with pytest.raises(AdministrationContractError):
        AdministrativeTarget.create(
            AdministrativeScope.PLATFORM, AdministrativeDomain.PLATFORM, "platform", tenant="acme"
        )


def test_published_contracts_are_versioned_refs():
    assert len(ADMINISTRATION_CONTRACTS) == 8
    for ref in ADMINISTRATION_CONTRACTS:
        assert ref.version == ADMINISTRATION_CONTRACT_VERSION
        assert ref.name.startswith("administration.")


def test_default_contracts_materialize_every_ref():
    contracts = default_administration_contracts()
    assert {c.name for c in contracts} == {r.name for r in ADMINISTRATION_CONTRACTS}


def test_administration_contract_requires_a_name():
    with pytest.raises(AdministrationContractError):
        administration_contract("")


def test_administration_contract_builds_a_versioned_contract():
    contract = administration_contract("administration.runtime.service", "desc")
    assert contract.name == "administration.runtime.service"
    assert str(contract.version) == ADMINISTRATION_CONTRACT_VERSION
