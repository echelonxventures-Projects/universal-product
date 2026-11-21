"""EC2-TASK-000069 — Authorization service + identity evidence tests (end-to-end)."""

from __future__ import annotations

from platform.foundation.bootstrap import bootstrap_platform
from platform.foundation.config import load_platform_config
from platform.foundation.events import EventBus
from platform.foundation.identity import Permission, Principal, Role
from platform.identity.contracts import IDENTITY_CONTRACTS, CapabilityGroup, Decision
from platform.identity.errors import AuthorizationError
from platform.identity.permissions import PermissionEngine
from platform.identity.policy import PolicyEngine
from platform.identity.principals import PrincipalRegistry
from platform.identity.roles import default_role_registry
from platform.identity.service import (
    ACCESS_EVENT,
    IDENTITY_BOOTSTRAP_EVENT,
    AuthorizationService,
    IdentityEvidence,
    bootstrap_identity,
    build_authorization_service,
)
from platform.identity.sessions import SessionRegistry

import pytest

C, R, X, A = (
    Permission.CREATE,
    Permission.READ,
    Permission.EXECUTE,
    Permission.ADMINISTER,
)


def test_build_default_service_seeds_matrix():
    svc = build_authorization_service()
    assert len(svc.roles) == 9
    assert len(svc.principals) == 0


def test_service_exposes_components():
    svc = build_authorization_service()
    assert isinstance(svc.permissions, PermissionEngine)
    assert isinstance(svc.policy, PolicyEngine)
    assert isinstance(svc.sessions, SessionRegistry)
    assert svc.decisions == ()


def test_register_principal_directly():
    svc = build_authorization_service()
    dev = Principal.create("dev", [Role.DEVELOPER])
    assert svc.register_principal(dev) is dev
    assert dev.principal_id in svc.principals


def test_authorize_principal_permit_and_log():
    svc = build_authorization_service()
    dev = Principal.create("dev", [Role.DEVELOPER])
    dec = svc.authorize_principal(dev, CapabilityGroup.GENERATION_REQUESTS, X)
    assert dec.decision is Decision.PERMIT
    assert len(svc.decisions) == 1


def test_end_to_end_session_authorize():
    events = EventBus()
    svc = build_authorization_service(events=events)
    dev = Principal.create("dev", [Role.DEVELOPER])
    session = svc.establish_session(dev, issued_at=0, ttl=100)
    dec = svc.authorize(session.session_id, CapabilityGroup.GENERATION_REQUESTS, X, now=1)
    assert dec.decision is Decision.PERMIT
    # Audit event emitted.
    access_events = events.events_of(ACCESS_EVENT)
    assert len(access_events) == 1
    assert access_events[0].subject == dev.principal_id


def test_authorize_expired_session_denies():
    svc = build_authorization_service()
    dev = Principal.create("dev", [Role.DEVELOPER])
    session = svc.establish_session(dev, issued_at=0, ttl=10)
    dec = svc.authorize(session.session_id, CapabilityGroup.GENERATION_REQUESTS, X, now=10)
    assert dec.decision is Decision.DENY
    assert dec.reason == "session-expired"


def test_authorize_revoked_session_denies():
    svc = build_authorization_service()
    dev = Principal.create("dev", [Role.DEVELOPER])
    session = svc.establish_session(dev, issued_at=0, ttl=100)
    svc.revoke_session(session.session_id, tick=5)
    dec = svc.authorize(session.session_id, CapabilityGroup.GENERATION_REQUESTS, X, now=6)
    assert dec.decision is Decision.DENY
    assert dec.reason == "session-revoked"


def test_authorize_absent_session_denies():
    svc = build_authorization_service()
    dec = svc.authorize("UCOS-SESS-missing", CapabilityGroup.PORTAL_NAVIGATION, R, now=0)
    assert dec.decision is Decision.DENY
    assert dec.reason == "session-absent"
    assert dec.request.principal_id == "anonymous"


def test_authorize_unregistered_principal_denies():
    # Establish a session directly on the shared session registry, bypassing the
    # service's principal registration, to exercise the fail-closed path.
    principals = PrincipalRegistry()
    roles = default_role_registry()
    sessions = SessionRegistry()
    svc = AuthorizationService(
        principals=principals,
        roles=roles,
        permissions=PermissionEngine(roles),
        policy=PolicyEngine(PermissionEngine(roles)),
        sessions=sessions,
    )
    dev = Principal.create("ghost", [Role.DEVELOPER])
    session = sessions.establish(dev, issued_at=0, ttl=100)  # not registered as principal
    dec = svc.authorize(session.session_id, CapabilityGroup.GENERATION_REQUESTS, X, now=1)
    assert dec.decision is Decision.DENY
    assert dec.reason == "principal-unregistered"


def test_negative_access_matrix_sample():
    """A representative sweep of denied combinations (least-privilege enforced)."""
    svc = build_authorization_service()
    cases = [
        (Role.DEVELOPER, CapabilityGroup.USER_ROLE_QUOTA_ADMIN, A, None),
        (Role.OPERATOR, CapabilityGroup.BLUEPRINT_AUTHORING, C, None),
        (Role.BUSINESS_USER, CapabilityGroup.RUNTIME_OPERATIONS, X, None),
        (Role.AUDITOR, CapabilityGroup.GENERATION_REQUESTS, X, None),
        (Role.ARCHITECT, CapabilityGroup.RUNTIME_OPERATIONS, X, None),
    ]
    for role, group, perm, tenant in cases:
        p = Principal.create(f"u-{role.value}", [role], tenant=tenant)
        dec = svc.authorize_principal(p, group, perm, tenant=tenant)
        assert dec.decision is Decision.DENY, (role, group, perm)


def test_service_input_validation():
    roles = default_role_registry()
    pe = PermissionEngine(roles)
    ok = dict(
        principals=PrincipalRegistry(),
        roles=roles,
        permissions=pe,
        policy=PolicyEngine(pe),
        sessions=SessionRegistry(),
    )
    with pytest.raises(AuthorizationError):
        AuthorizationService(**{**ok, "principals": "x"})
    with pytest.raises(AuthorizationError):
        AuthorizationService(**{**ok, "roles": "x"})
    with pytest.raises(AuthorizationError):
        AuthorizationService(**{**ok, "permissions": "x"})
    with pytest.raises(AuthorizationError):
        AuthorizationService(**{**ok, "policy": "x"})
    with pytest.raises(AuthorizationError):
        AuthorizationService(**{**ok, "sessions": "x"})
    with pytest.raises(AuthorizationError):
        AuthorizationService(**{**ok, "events": "x"})


def test_identity_evidence_deterministic():
    def _run():
        svc = build_authorization_service()
        dev = Principal.create("dev", [Role.DEVELOPER])
        svc.authorize_principal(dev, CapabilityGroup.GENERATION_REQUESTS, X)
        svc.authorize_principal(dev, CapabilityGroup.USER_ROLE_QUOTA_ADMIN, A)
        return svc.evidence()

    a = _run()
    b = _run()
    assert isinstance(a, IdentityEvidence)
    assert a.fingerprint() == b.fingerprint()
    assert a.evidence_id == b.evidence_id
    assert a.decision_count == 2
    assert a.permit_count == 1
    assert a.deny_count == 1


def test_service_to_dict_has_evidence():
    svc = build_authorization_service()
    dev = Principal.create("dev", [Role.DEVELOPER])
    svc.establish_session(dev, issued_at=0, ttl=10)
    svc.authorize_principal(dev, CapabilityGroup.PORTAL_NAVIGATION, R)
    d = svc.to_dict()
    assert d["decision_count"] == 1
    assert "evidence" in d
    assert d["principals"]["principal_count"] == 1


def test_bootstrap_identity_registers_contracts_and_emits_event():
    ctx = bootstrap_platform(load_platform_config(environ={}))
    svc = bootstrap_identity(ctx)
    assert isinstance(svc, AuthorizationService)
    # All six identity contracts registered as services (registry-driven).
    for ref in IDENTITY_CONTRACTS:
        assert ref.name in ctx.services
        assert ctx.services.resolve(ref.name) is svc
    boot_events = ctx.events.events_of(IDENTITY_BOOTSTRAP_EVENT)
    assert len(boot_events) == 1
    assert boot_events[0].payload["roles"] == 9


def test_bootstrap_identity_is_idempotent_on_contract_names():
    ctx = bootstrap_platform(load_platform_config(environ={}))
    bootstrap_identity(ctx)
    # A second composition must not raise on already-registered contract names.
    svc2 = bootstrap_identity(ctx)
    assert isinstance(svc2, AuthorizationService)


def test_end_to_end_deterministic_decision_ids():
    def _decide():
        svc = build_authorization_service()
        dev = Principal.create("dev", [Role.DEVELOPER])
        s = svc.establish_session(dev, issued_at=0, ttl=100)
        return svc.authorize(s.session_id, CapabilityGroup.GENERATION_REQUESTS, X, now=1)

    assert _decide().decision_id == _decide().decision_id
