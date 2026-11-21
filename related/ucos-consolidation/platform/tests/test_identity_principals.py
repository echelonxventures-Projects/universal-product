"""EC2-TASK-000064 — Principal registry tests."""

from __future__ import annotations

from platform.foundation.identity import Principal, Role
from platform.identity.errors import PrincipalRegistryError
from platform.identity.principals import PrincipalRegistry

import pytest


def test_register_and_resolve():
    reg = PrincipalRegistry()
    p = Principal.create("alice", [Role.DEVELOPER])
    reg.register(p)
    assert p.principal_id in reg
    assert reg.get(p.principal_id) is p
    assert len(reg) == 1


def test_register_subject_helper():
    reg = PrincipalRegistry()
    p = reg.register_subject("bob", [Role.OPERATOR], tenant="ws-1", attributes={"k": "v"})
    assert p.tenant == "ws-1"
    assert reg.in_tenant("ws-1") == (p,)


def test_registration_is_idempotent_for_identical_principal():
    reg = PrincipalRegistry()
    p = Principal.create("alice", [Role.DEVELOPER])
    reg.register(p)
    again = reg.register(Principal.create("alice", [Role.DEVELOPER]))
    assert again is p
    assert len(reg) == 1


def test_register_all_and_deterministic_order():
    reg = PrincipalRegistry()
    a = Principal.create("alice", [Role.DEVELOPER])
    b = Principal.create("bob", [Role.OPERATOR])
    reg.register_all([b, a])
    # Deterministic: sorted by principal_id regardless of insertion order.
    assert reg.ids == tuple(sorted([a.principal_id, b.principal_id]))
    assert reg.principals() == tuple(reg.get(pid) for pid in reg.ids)


def test_by_subject_and_with_role():
    reg = PrincipalRegistry()
    dev = reg.register_subject("carol", [Role.DEVELOPER])
    ops = reg.register_subject("carol", [Role.OPERATOR])
    subjects = {p.principal_id for p in reg.by_subject("carol")}
    assert subjects == {dev.principal_id, ops.principal_id}
    assert reg.with_role(Role.OPERATOR) == (ops,)
    assert reg.with_role(Role.DEVELOPER) == (dev,)


def test_get_absent_raises():
    reg = PrincipalRegistry()
    with pytest.raises(PrincipalRegistryError):
        reg.get("UCOS-PRIN-missing")


def test_register_rejects_non_principal():
    reg = PrincipalRegistry()
    with pytest.raises(PrincipalRegistryError):
        reg.register("not-a-principal")


def test_register_rejects_missing_id():
    reg = PrincipalRegistry()
    # A Principal built directly (not via create) has an empty principal_id.
    bare = Principal(subject="x", roles=frozenset({Role.DEVELOPER}))
    with pytest.raises(PrincipalRegistryError):
        reg.register(bare)


def test_conflicting_definition_under_same_id_rejected(monkeypatch):
    reg = PrincipalRegistry()
    p = Principal.create("alice", [Role.DEVELOPER])
    reg.register(p)
    # Forge a different-body principal that collides on id.
    forged = Principal(
        subject="mallory", roles=frozenset({Role.OPERATOR}), principal_id=p.principal_id
    )
    with pytest.raises(PrincipalRegistryError):
        reg.register(forged)


def test_fingerprint_is_deterministic():
    a = PrincipalRegistry()
    b = PrincipalRegistry()
    a.register_subject("alice", [Role.DEVELOPER])
    b.register_subject("alice", [Role.DEVELOPER])
    assert a.fingerprint() == b.fingerprint()
    assert a.to_dict()["principal_count"] == 1
