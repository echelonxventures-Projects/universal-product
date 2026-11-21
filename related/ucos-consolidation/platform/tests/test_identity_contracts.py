"""EC2-TASK-000063 — Identity contracts + core vocabulary tests."""

from __future__ import annotations

from platform.foundation.identity import Permission, Role
from platform.identity.contracts import (
    IDENTITY_CONTRACT_VERSION,
    IDENTITY_CONTRACTS,
    AccessDecision,
    AccessRequest,
    CapabilityGroup,
    Decision,
    all_capability_groups,
    default_identity_contracts,
    identity_contract,
)
from platform.identity.errors import IdentityContractError

import pytest


def test_sixteen_capability_groups():
    assert len(all_capability_groups()) == 16
    assert CapabilityGroup.CERTIFICATION_LEDGER in all_capability_groups()
    assert CapabilityGroup.API_ACCESS in all_capability_groups()


def test_decision_effects():
    assert {d.value for d in Decision} == {"permit", "deny"}


def test_six_identity_contracts_published():
    assert len(IDENTITY_CONTRACTS) == 6
    names = {ref.name for ref in IDENTITY_CONTRACTS}
    assert "identity.authorization.authorize" in names
    assert "identity.roles.registry" in names
    for ref in IDENTITY_CONTRACTS:
        assert ref.version == IDENTITY_CONTRACT_VERSION


def test_default_identity_contracts_build():
    contracts = default_identity_contracts()
    assert len(contracts) == 6
    assert all(str(c.version) == IDENTITY_CONTRACT_VERSION for c in contracts)


def test_identity_contract_requires_name():
    with pytest.raises(IdentityContractError):
        identity_contract("")


def test_access_request_is_content_addressed_and_deterministic():
    a = AccessRequest.create(
        "UCOS-PRIN-x",
        frozenset({Role.DEVELOPER}),
        CapabilityGroup.GENERATION_REQUESTS,
        Permission.EXECUTE,
    )
    b = AccessRequest.create(
        "UCOS-PRIN-x",
        frozenset({Role.DEVELOPER}),
        CapabilityGroup.GENERATION_REQUESTS,
        Permission.EXECUTE,
    )
    assert a.request_id == b.request_id
    assert a.request_id.startswith("UCOS-AREQ-")


def test_access_request_distinct_permission_yields_distinct_id():
    a = AccessRequest.create(
        "p", frozenset({Role.DEVELOPER}), CapabilityGroup.GENERATION_REQUESTS, Permission.READ
    )
    b = AccessRequest.create(
        "p", frozenset({Role.DEVELOPER}), CapabilityGroup.GENERATION_REQUESTS, Permission.EXECUTE
    )
    assert a.request_id != b.request_id


def test_access_request_validation():
    dev = frozenset({Role.DEVELOPER})
    with pytest.raises(IdentityContractError):
        AccessRequest.create("", dev, CapabilityGroup.API_ACCESS, Permission.READ)
    with pytest.raises(IdentityContractError):
        AccessRequest.create("p", dev, "not-a-group", Permission.READ)
    with pytest.raises(IdentityContractError):
        AccessRequest.create("p", dev, CapabilityGroup.API_ACCESS, "nope")
    with pytest.raises(IdentityContractError):
        AccessRequest.create(
            "p", frozenset({"not-a-role"}), CapabilityGroup.API_ACCESS, Permission.READ
        )


def test_access_decision_content_addressed_and_flags():
    req = AccessRequest.create(
        "p", frozenset({Role.DEVELOPER}), CapabilityGroup.PORTAL_NAVIGATION, Permission.READ
    )
    permit = AccessDecision.create(req, Decision.PERMIT, "rbac-grant")
    deny = AccessDecision.create(req, Decision.DENY, "no-grant")
    assert permit.permitted and not permit.denied
    assert deny.denied and not deny.permitted
    assert permit.decision_id.startswith("UCOS-ADEC-")
    assert permit.decision_id != deny.decision_id


def test_access_decision_validation():
    req = AccessRequest.create(
        "p", frozenset({Role.DEVELOPER}), CapabilityGroup.PORTAL_NAVIGATION, Permission.READ
    )
    with pytest.raises(IdentityContractError):
        AccessDecision.create("not-a-request", Decision.PERMIT, "r")
    with pytest.raises(IdentityContractError):
        AccessDecision.create(req, "nope", "r")
    with pytest.raises(IdentityContractError):
        AccessDecision.create(req, Decision.PERMIT, "")


def test_access_decision_to_dict_roundtrip_fields():
    req = AccessRequest.create(
        "p",
        frozenset({Role.PARTNER}),
        CapabilityGroup.API_ACCESS,
        Permission.EXECUTE,
        tenant="ws-1",
        resource="res-1",
    )
    dec = AccessDecision.create(
        req, Decision.PERMIT, "rbac-grant", obligations=frozenset({"tenant-scoped"})
    )
    d = dec.to_dict()
    assert d["decision"] == "permit"
    assert d["obligations"] == ["tenant-scoped"]
    assert d["request"]["tenant"] == "ws-1"
    assert d["request"]["resource"] == "res-1"


def test_identity_contract_normalises_platform_error(monkeypatch):
    import platform.identity.contracts as contracts_mod
    from platform.foundation.errors import PlatformContractError

    def _boom(name, version, description=""):
        raise PlatformContractError("bad contract")

    monkeypatch.setattr(contracts_mod, "platform_contract", _boom)
    with pytest.raises(IdentityContractError):
        contracts_mod.identity_contract("identity.x")
