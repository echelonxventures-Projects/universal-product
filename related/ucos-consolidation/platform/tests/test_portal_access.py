"""EC2-TASK-000074 — Portal access gateway tests.

Covers the authentication/authorization integration: the gateway delegates session
lifecycle and authorization to the certified Identity Layer (no duplicate identity),
admits only principals holding READ on ``portal-navigation`` (fail-closed), and denies
absent/expired/revoked sessions and ungranted roles (the Integrator).
"""

from __future__ import annotations

from platform.foundation.identity import Permission, Principal, Role
from platform.identity.contracts import CapabilityGroup, Decision
from platform.identity.service import build_authorization_service
from platform.portal.access import PortalAccessGateway
from platform.portal.errors import PortalAccessError

import pytest


def _gateway() -> PortalAccessGateway:
    return PortalAccessGateway(build_authorization_service())


def _principal(role: Role, subject: str = "u@ucos", tenant: str | None = None) -> Principal:
    return Principal.create(subject, [role], tenant=tenant)


def test_gateway_requires_authorization_service():
    with pytest.raises(PortalAccessError):
        PortalAccessGateway("not-a-service")  # type: ignore[arg-type]


def test_admin_is_admitted():
    gw = _gateway()
    session = gw.establish_session(_principal(Role.PLATFORM_ADMINISTRATOR), issued_at=0, ttl=100)
    admission = gw.admit(session.session_id, now=1)
    assert admission.admitted is True
    assert admission.decision.decision is Decision.PERMIT
    assert admission.principal_id.startswith("UCOS-PRIN-")


def test_integrator_is_denied_admission_no_grant():
    gw = _gateway()
    session = gw.establish_session(_principal(Role.INTEGRATOR), issued_at=0, ttl=100)
    admission = gw.admit(session.session_id, now=1)
    assert admission.admitted is False
    assert admission.reason == "no-grant"


def test_require_admission_raises_when_denied():
    gw = _gateway()
    session = gw.establish_session(_principal(Role.INTEGRATOR), issued_at=0, ttl=100)
    with pytest.raises(PortalAccessError):
        gw.require_admission(session.session_id, now=1)


def test_absent_session_is_denied():
    gw = _gateway()
    admission = gw.admit("UCOS-SESS-does-not-exist", now=1)
    assert admission.admitted is False
    assert admission.reason == "session-absent"


def test_expired_session_is_denied():
    gw = _gateway()
    session = gw.establish_session(_principal(Role.PLATFORM_ADMINISTRATOR), issued_at=0, ttl=10)
    admission = gw.admit(session.session_id, now=10)  # now >= expires_at => expired
    assert admission.admitted is False
    assert admission.reason == "session-expired"


def test_revoked_session_is_denied():
    gw = _gateway()
    session = gw.establish_session(_principal(Role.PLATFORM_ADMINISTRATOR), issued_at=0, ttl=100)
    gw.revoke_session(session.session_id, tick=1)
    admission = gw.admit(session.session_id, now=2)
    assert admission.admitted is False
    assert admission.reason == "session-revoked"


def test_is_permitted_reflects_matrix():
    gw = _gateway()
    dev = gw.establish_session(_principal(Role.DEVELOPER), issued_at=0, ttl=100)
    # Developer holds create/read/execute on generation requests, but not admin.
    assert gw.is_permitted(
        dev.session_id, CapabilityGroup.GENERATION_REQUESTS, Permission.READ, now=1
    )
    assert not gw.is_permitted(
        dev.session_id, CapabilityGroup.USER_ROLE_QUOTA_ADMIN, Permission.ADMINISTER, now=1
    )


def test_authorize_validates_arguments():
    gw = _gateway()
    session = gw.establish_session(_principal(Role.PLATFORM_ADMINISTRATOR), issued_at=0, ttl=100)
    with pytest.raises(PortalAccessError):
        gw.authorize("", CapabilityGroup.PORTAL_NAVIGATION, Permission.READ, now=1)
    with pytest.raises(PortalAccessError):
        gw.authorize(session.session_id, "grp", Permission.READ, now=1)  # type: ignore[arg-type]
    with pytest.raises(PortalAccessError):
        gw.authorize(session.session_id, CapabilityGroup.PORTAL_NAVIGATION, "R", now=1)  # type: ignore[arg-type]


def test_establish_session_requires_principal():
    gw = _gateway()
    with pytest.raises(PortalAccessError):
        gw.establish_session("nope", issued_at=0, ttl=10)  # type: ignore[arg-type]


def test_admission_serializes():
    gw = _gateway()
    session = gw.establish_session(_principal(Role.PLATFORM_ADMINISTRATOR), issued_at=0, ttl=100)
    admission = gw.admit(session.session_id, now=1)
    payload = admission.to_dict()
    assert payload["admitted"] is True
    assert payload["decision"]["decision"] == "permit"


def test_gateway_exposes_authorization_service():
    from platform.identity.service import AuthorizationService

    gw = _gateway()
    assert isinstance(gw.authorization, AuthorizationService)
