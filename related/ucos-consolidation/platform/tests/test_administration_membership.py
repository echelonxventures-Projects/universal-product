"""EC2-CAP-ADMIN-001 — Administrative membership tests.

Covers the append-only administrative membership registry: content-addressed members,
fail-closed assign/revoke, scope/target lookups, per-principal scopes, the append-only
event log, the scope↔tenant consistency flag (surfaced by health), validation, and
determinism.
"""

from __future__ import annotations

from platform.administration.contracts import AdministrativeScope
from platform.administration.errors import AdministrationMembershipError
from platform.administration.membership import (
    AdministrativeMember,
    AdministrativeMembershipRegistry,
)

import pytest


def test_member_is_content_addressed_by_scope_target_principal():
    a = AdministrativeMember.create(
        AdministrativeScope.TENANT, "acme", "UCOS-PRIN-a", "a@x", tenant="acme"
    )
    b = AdministrativeMember.create(
        AdministrativeScope.TENANT, "acme", "UCOS-PRIN-a", "a@x", tenant="acme"
    )
    assert a.member_id == b.member_id
    assert a.member_id.startswith("UCOS-AMEM-")


@pytest.mark.parametrize(
    "kwargs",
    [
        {"scope": "tenant", "target": "acme", "principal_id": "p", "subject": "s"},
        {"scope": AdministrativeScope.TENANT, "target": "", "principal_id": "p", "subject": "s"},
        {"scope": AdministrativeScope.TENANT, "target": "t", "principal_id": "", "subject": "s"},
        {"scope": AdministrativeScope.TENANT, "target": "t", "principal_id": "p", "subject": ""},
    ],
)
def test_member_create_validates_shape(kwargs):
    with pytest.raises(AdministrationMembershipError):
        AdministrativeMember.create(
            kwargs["scope"], kwargs["target"], kwargs["principal_id"], kwargs["subject"]
        )  # type: ignore[arg-type]


def test_add_is_fail_closed_on_duplicate():
    reg = AdministrativeMembershipRegistry()
    reg.add(AdministrativeScope.PLATFORM, "platform", "UCOS-PRIN-a", "a@x", tick=1)
    with pytest.raises(AdministrationMembershipError):
        reg.add(AdministrativeScope.PLATFORM, "platform", "UCOS-PRIN-a", "a@x", tick=2)


def test_remove_is_fail_closed_on_absent():
    reg = AdministrativeMembershipRegistry()
    with pytest.raises(AdministrationMembershipError):
        reg.remove(AdministrativeScope.PLATFORM, "platform", "UCOS-PRIN-a", tick=1)


def test_add_remove_records_ordered_events():
    reg = AdministrativeMembershipRegistry()
    reg.add(AdministrativeScope.TENANT, "acme", "UCOS-PRIN-a", "a@x", tick=1, tenant="acme")
    reg.remove(AdministrativeScope.TENANT, "acme", "UCOS-PRIN-a", tick=2)
    actions = [e.action for e in reg.events]
    assert actions == ["assigned", "revoked"]
    assert reg.events[0].to_dict()["action"] == "assigned"


def test_is_administrator_and_members_of_and_scopes_of():
    reg = AdministrativeMembershipRegistry()
    reg.add(AdministrativeScope.TENANT, "acme", "UCOS-PRIN-a", "a@x", tick=1, tenant="acme")
    reg.add(AdministrativeScope.TENANT, "acme", "UCOS-PRIN-b", "b@x", tick=2, tenant="acme")
    reg.add(AdministrativeScope.WORKSPACE, "ws-1", "UCOS-PRIN-a", "a@x", tick=3, tenant="acme")
    assert reg.is_administrator(AdministrativeScope.TENANT, "acme", "UCOS-PRIN-a")
    assert not reg.is_administrator(AdministrativeScope.TENANT, "acme", "UCOS-PRIN-z")
    assert len(reg.members_of(AdministrativeScope.TENANT, "acme")) == 2
    assert len(reg.scopes_of("UCOS-PRIN-a")) == 2
    assert len(reg) == 3


def test_members_of_rejects_bad_scope():
    reg = AdministrativeMembershipRegistry()
    with pytest.raises(AdministrationMembershipError):
        reg.members_of("tenant", "acme")  # type: ignore[arg-type]


def test_scope_tenant_consistency_flag():
    consistent = AdministrativeMember.create(
        AdministrativeScope.TENANT, "acme", "UCOS-PRIN-a", "a@x", tenant="acme"
    )
    inconsistent = AdministrativeMember.create(
        AdministrativeScope.TENANT, "acme", "UCOS-PRIN-a", "a@x"
    )
    platform_member = AdministrativeMember.create(
        AdministrativeScope.PLATFORM, "platform", "UCOS-PRIN-a", "a@x"
    )
    assert consistent.is_consistent is True
    assert consistent.requires_tenant is True
    assert inconsistent.is_consistent is False
    assert platform_member.requires_tenant is False
    assert platform_member.is_consistent is True


def test_ingest_rejects_non_member():
    reg = AdministrativeMembershipRegistry()
    with pytest.raises(AdministrationMembershipError):
        reg._ingest("nope")  # type: ignore[arg-type]


def test_to_dict_and_fingerprint_deterministic():
    def build() -> AdministrativeMembershipRegistry:
        reg = AdministrativeMembershipRegistry()
        reg.add(AdministrativeScope.PLATFORM, "platform", "UCOS-PRIN-a", "a@x", tick=1)
        reg.add(AdministrativeScope.TENANT, "acme", "UCOS-PRIN-b", "b@x", tick=2, tenant="acme")
        return reg

    one, two = build(), build()
    assert one.fingerprint() == two.fingerprint()
    assert one.to_dict()["member_count"] == 2
    assert [m.member_id for m in one.all()] == [m.member_id for m in two.all()]
