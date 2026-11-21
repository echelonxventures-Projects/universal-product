"""EC2-TASK-000068 — Session model + registry tests (deterministic, no wall-clock)."""

from __future__ import annotations

from platform.foundation.identity import Principal, Role
from platform.identity.errors import SessionError
from platform.identity.sessions import Session, SessionRegistry, SessionStatus

import pytest


def _principal(subject="dev", tenant=None):
    return Principal.create(subject, [Role.DEVELOPER], tenant=tenant)


def test_establish_is_content_addressed_and_deterministic():
    p = _principal()
    a = Session.establish(p, issued_at=0, ttl=100)
    b = Session.establish(p, issued_at=0, ttl=100)
    assert a.session_id == b.session_id
    assert a.session_id.startswith("UCOS-SESS-")
    assert a.expires_at == 100


def test_effective_status_lifecycle():
    p = _principal()
    s = Session.establish(p, issued_at=10, ttl=5)  # expires at 15
    assert s.effective_status(10) is SessionStatus.ACTIVE
    assert s.is_valid(14) is True
    assert s.effective_status(15) is SessionStatus.EXPIRED
    assert s.is_valid(15) is False
    revoked = s.revoked()
    assert revoked.effective_status(10) is SessionStatus.REVOKED


def test_establish_validation():
    p = _principal()
    with pytest.raises(SessionError):
        Session.establish("not-a-principal", issued_at=0, ttl=1)
    with pytest.raises(SessionError):
        Session.establish(p, issued_at=-1, ttl=1)
    with pytest.raises(SessionError):
        Session.establish(p, issued_at=0, ttl=0)
    with pytest.raises(SessionError):
        Session.establish(p, issued_at=0, ttl=1, credential_ref="")
    # Booleans must not sneak through as ints.
    with pytest.raises(SessionError):
        Session.establish(p, issued_at=True, ttl=1)
    with pytest.raises(SessionError):
        Session.establish(p, issued_at=0, ttl=True)


def test_credential_ref_is_by_reference_only():
    p = _principal()
    s = Session.establish(p, issued_at=0, ttl=10, credential_ref="vault://token-1")
    assert s.credential_ref == "vault://token-1"
    assert s.to_dict()["credential_ref"] == "vault://token-1"


def test_registry_establish_and_validate():
    reg = SessionRegistry()
    p = _principal()
    s = reg.establish(p, issued_at=0, ttl=10)
    assert s.session_id in reg
    assert reg.validate(s.session_id, 5).session_id == s.session_id
    assert len(reg.events) == 1
    assert reg.events[0].status is SessionStatus.ACTIVE


def test_registry_establish_idempotent():
    reg = SessionRegistry()
    p = _principal()
    a = reg.establish(p, issued_at=0, ttl=10)
    b = reg.establish(p, issued_at=0, ttl=10)
    assert a is b
    assert len(reg) == 1
    assert len(reg.events) == 1


def test_validate_expired_fails_closed():
    reg = SessionRegistry()
    p = _principal()
    s = reg.establish(p, issued_at=0, ttl=10)
    with pytest.raises(SessionError):
        reg.validate(s.session_id, 10)


def test_validate_absent_fails_closed():
    reg = SessionRegistry()
    with pytest.raises(SessionError):
        reg.validate("UCOS-SESS-missing", 0)


def test_validate_rejects_bad_now():
    reg = SessionRegistry()
    p = _principal()
    s = reg.establish(p, issued_at=0, ttl=10)
    with pytest.raises(SessionError):
        reg.validate(s.session_id, -1)


def test_revoke_is_idempotent_and_logged():
    reg = SessionRegistry()
    p = _principal()
    s = reg.establish(p, issued_at=0, ttl=100)
    revoked = reg.revoke(s.session_id, tick=5)
    assert revoked.lifecycle is SessionStatus.REVOKED
    # Revoked session no longer validates even before expiry.
    with pytest.raises(SessionError):
        reg.validate(s.session_id, 6)
    # Idempotent revoke does not add another event.
    reg.revoke(s.session_id, tick=7)
    revoke_events = [e for e in reg.events if e.status is SessionStatus.REVOKED]
    assert len(revoke_events) == 1


def test_registry_queries_deterministic():
    reg = SessionRegistry()
    p1 = _principal("alice")
    p2 = _principal("bob")
    s1 = reg.establish(p1, issued_at=0, ttl=10)
    s2 = reg.establish(p2, issued_at=1, ttl=10)
    assert reg.ids == tuple(sorted([s1.session_id, s2.session_id]))
    assert reg.for_principal(p1.principal_id) == (s1,)
    assert set(reg.active_sessions(2)) == {s1, s2}
    assert set(reg.active_sessions(10)) == {s2}  # s1 expired at 10


def test_registry_to_dict():
    reg = SessionRegistry()
    reg.establish(_principal(), issued_at=0, ttl=10)
    d = reg.to_dict()
    assert d["session_count"] == 1
    assert len(d["sessions"]) == 1
    assert len(d["events"]) == 1


def test_session_event_to_dict():
    reg = SessionRegistry()
    s = reg.establish(_principal(), issued_at=0, ttl=10)
    event = reg.events[0]
    assert event.to_dict() == {
        "sequence": 0,
        "session_id": s.session_id,
        "status": "active",
        "tick": 0,
    }
