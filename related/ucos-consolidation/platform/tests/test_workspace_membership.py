"""EC2-TASK-000083 — Workspace membership tests.

Covers the deterministic, append-only membership registry: add/remove, duplicate and
absent fail-closed handling, member/workspace queries, and the append-only event log.
"""

from __future__ import annotations

from platform.workspace.contracts import MemberRole
from platform.workspace.errors import MembershipError
from platform.workspace.membership import MembershipRegistry

import pytest

WS = "UCOS-WSPC-w"
P1 = "UCOS-PRIN-1"
P2 = "UCOS-PRIN-2"


def test_add_and_query_members():
    reg = MembershipRegistry()
    reg.add(WS, P1, "a@x", MemberRole.OWNER, tick=0)
    reg.add(WS, P2, "b@x", MemberRole.MEMBER, tick=1)
    assert reg.is_member(WS, P1)
    assert reg.member(WS, P2).role is MemberRole.MEMBER
    assert len(reg.members_of(WS)) == 2
    assert len(reg) == 2
    assert reg.workspace_ids == (WS,)
    assert reg.workspaces_of(P1) == (WS,)


def test_duplicate_add_is_fail_closed():
    reg = MembershipRegistry()
    reg.add(WS, P1, "a@x", MemberRole.OWNER, tick=0)
    with pytest.raises(MembershipError):
        reg.add(WS, P1, "a@x", MemberRole.MEMBER, tick=1)


def test_remove_member():
    reg = MembershipRegistry()
    reg.add(WS, P1, "a@x", MemberRole.OWNER, tick=0)
    removed = reg.remove(WS, P1, tick=1)
    assert removed.role is MemberRole.OWNER
    assert not reg.is_member(WS, P1)
    assert reg.workspace_ids == ()  # empty workspace no longer counted


def test_remove_absent_is_fail_closed():
    reg = MembershipRegistry()
    with pytest.raises(MembershipError):
        reg.remove(WS, P1, tick=0)


def test_member_absent_returns_none():
    reg = MembershipRegistry()
    assert reg.member(WS, P1) is None
    assert reg.members_of(WS) == ()


def test_event_log_is_append_only_and_ordered():
    reg = MembershipRegistry()
    reg.add(WS, P1, "a@x", MemberRole.OWNER, tick=0)
    reg.remove(WS, P1, tick=1)
    events = reg.events
    assert [e.action for e in events] == ["added", "removed"]
    assert [e.sequence for e in events] == [0, 1]
    assert events[0].to_dict()["role"] == "owner"


def test_fingerprint_is_deterministic():
    def build() -> str:
        reg = MembershipRegistry()
        reg.add(WS, P1, "a@x", MemberRole.OWNER, tick=0)
        reg.add(WS, P2, "b@x", MemberRole.MEMBER, tick=1)
        return reg.fingerprint()

    assert build() == build()
