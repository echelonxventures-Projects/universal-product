"""EC2-TASK-000077 — Portal workspace handoff tests.

Covers the authorization-gated portal-to-workspace handoff: an authorized principal
receives a content-addressed handoff descriptor to the workspace landing route; an
unauthorized or malformed selection never yields a usable handoff (fail-closed).
"""

from __future__ import annotations

from platform.foundation.identity import Principal, Role
from platform.identity.service import build_authorization_service
from platform.portal.access import PortalAccessGateway
from platform.portal.errors import WorkspaceHandoffError
from platform.portal.routing import Router
from platform.portal.workspace import WORKSPACE_GROUP, WorkspaceSelector

import pytest


def _selector() -> tuple[PortalAccessGateway, WorkspaceSelector]:
    gateway = PortalAccessGateway(build_authorization_service())
    return gateway, WorkspaceSelector(gateway, router=Router())


def _session(gateway: PortalAccessGateway, role: Role, tenant: str | None = None):
    principal = Principal.create("u@ucos", [role], tenant=tenant)
    return gateway.establish_session(principal, issued_at=0, ttl=100)


def test_selector_requires_valid_gateway():
    with pytest.raises(WorkspaceHandoffError):
        WorkspaceSelector("nope")  # type: ignore[arg-type]


def test_landing_path_matches_workspace_surface():
    _, selector = _selector()
    assert selector.landing_path == f"/{WORKSPACE_GROUP.value}"


def test_authorized_handoff_is_content_addressed():
    gateway, selector = _selector()
    session = _session(gateway, Role.DEVELOPER)
    handoff = selector.handoff(session.session_id, "ws-1", now=1)
    assert handoff.authorized is True
    assert handoff.handoff_id.startswith("UCOS-PWSH-")
    assert handoff.landing_path == selector.landing_path
    assert handoff.workspace_id == "ws-1"


def test_handoff_denied_for_role_without_grant():
    gateway, selector = _selector()
    # Integrator's workspace access is scoped; without a tenant the scope invariant denies.
    session = _session(gateway, Role.INTEGRATOR, tenant=None)
    handoff = selector.handoff(session.session_id, "ws-1", now=1)
    assert handoff.authorized is False
    with pytest.raises(WorkspaceHandoffError):
        selector.require_handoff(session.session_id, "ws-1", now=1)


def test_handoff_requires_workspace_id():
    gateway, selector = _selector()
    session = _session(gateway, Role.DEVELOPER)
    with pytest.raises(WorkspaceHandoffError):
        selector.handoff(session.session_id, "", now=1)


def test_require_handoff_returns_authorized():
    gateway, selector = _selector()
    session = _session(gateway, Role.PLATFORM_ADMINISTRATOR)
    handoff = selector.require_handoff(session.session_id, "ws-1", now=1)
    assert handoff.authorized is True
    assert handoff.to_dict()["authorized"] is True


def test_handoff_deterministic_for_same_inputs():
    gateway, selector = _selector()
    session = _session(gateway, Role.DEVELOPER)
    a = selector.handoff(session.session_id, "ws-9", now=1)
    b = selector.handoff(session.session_id, "ws-9", now=2)
    assert a.handoff_id == b.handoff_id  # id excludes the logical clock
