"""EC2-TASK-000131 — Execution dashboard search tests (EC2-EPIC-008).

Covers the authorization- and isolation-scoped dashboard request search: construction
guards, authorized ranked matching, fail-closed denials (invalid session, no dashboard
grant, scoped cross-tenant), tenant isolation filtering, empty-query short-circuit, and
scoping filters — all gated on the ``execution-dashboard`` group (never generation-requests).
"""

from __future__ import annotations

from platform.blueprints.contracts import BlueprintFamily
from platform.execution_dashboard.errors import DashboardSearchError
from platform.execution_dashboard.search import DashboardSearch
from platform.foundation.identity import Principal, Role
from platform.generation.contracts import RequestStatus
from platform.generation.registry import GenerationRequestRegistry
from platform.identity.roles import RoleDefinition, RoleRegistry, default_role_definitions
from platform.identity.service import build_authorization_service

import pytest


def _registry():
    reg = GenerationRequestRegistry()
    reg.create(
        "alpha",
        "UCOS-BLPR-1",
        "UCOS-WSPC-1",
        "arch@x",
        BlueprintFamily.DATA,
        submitted_tick=1,
        tenant="acme",
    )
    reg.create(
        "beta",
        "UCOS-BLPR-2",
        "UCOS-WSPC-1",
        "arch@x",
        BlueprintFamily.EVENT,
        submitted_tick=2,
        tenant="acme",
    )
    reg.create(
        "gamma",
        "UCOS-BLPR-3",
        "UCOS-WSPC-2",
        "arch@x",
        BlueprintFamily.DATA,
        submitted_tick=3,
        tenant="beta",
    )
    return reg


def _session(auth, role=Role.OPERATOR, subject="op@x", tenant=None):
    return auth.establish_session(
        Principal.create(subject, [role], tenant=tenant), issued_at=0, ttl=1000
    )


def test_construction_validates_components():
    auth = build_authorization_service()
    with pytest.raises(DashboardSearchError):
        DashboardSearch("nope", auth)  # type: ignore[arg-type]
    with pytest.raises(DashboardSearchError):
        DashboardSearch(GenerationRequestRegistry(), "nope")  # type: ignore[arg-type]


def test_authorized_search_ranks_matches():
    auth = build_authorization_service()
    search = DashboardSearch(_registry(), auth)
    session = _session(auth, tenant="acme")
    resp = search.search(session.session_id, "alpha", now=1, tenant="acme")
    assert resp.authorized is True
    assert len(resp.results) == 1
    assert resp.results[0].request.slug == "alpha"


def test_search_rejects_non_string_query():
    auth = build_authorization_service()
    search = DashboardSearch(_registry(), auth)
    session = _session(auth)
    with pytest.raises(DashboardSearchError):
        search.search(session.session_id, 123, now=1)  # type: ignore[arg-type]


def test_search_unauthorized_for_invalid_session():
    auth = build_authorization_service()
    search = DashboardSearch(_registry(), auth)
    resp = search.search("UCOS-SESS-missing", "alpha", now=1)
    assert resp.authorized is False
    assert resp.results == ()


def test_search_denied_without_dashboard_grant():
    defs = [d for d in default_role_definitions() if d.role is not Role.OPERATOR]
    defs.append(RoleDefinition(role=Role.OPERATOR, grants={}))
    roles = RoleRegistry()
    roles.register_all(defs)
    auth = build_authorization_service(roles=roles)
    search = DashboardSearch(_registry(), auth)
    session = _session(auth)
    resp = search.search(session.session_id, "alpha", now=1)
    assert resp.authorized is False


def test_search_denied_scoped_cross_tenant():
    auth = build_authorization_service()
    search = DashboardSearch(_registry(), auth)
    partner = _session(auth, role=Role.PARTNER, subject="p@x", tenant="acme")
    resp = search.search(partner.session_id, "gamma", now=1, tenant="beta")
    assert resp.authorized is False


def test_search_empty_query_short_circuits():
    auth = build_authorization_service()
    search = DashboardSearch(_registry(), auth)
    session = _session(auth)
    resp = search.search(session.session_id, "   ", now=1)
    assert resp.authorized is True
    assert resp.results == ()


def test_search_isolation_filters_cross_tenant_requests():
    auth = build_authorization_service()
    search = DashboardSearch(_registry(), auth)
    # Tenant-bound operator in acme searching everything must never see beta's request.
    session = _session(auth, tenant="acme")
    resp = search.search(session.session_id, "gamma", now=1)
    assert resp.authorized is True
    assert all(hit.request.tenant != "beta" for hit in resp.results)


def test_search_scoped_by_status():
    reg = _registry()
    auth = build_authorization_service()
    search = DashboardSearch(reg, auth)
    session = _session(auth, tenant="acme")
    resp = search.search(
        session.session_id, "alpha", now=1, tenant="acme", status=RequestStatus.SUBMITTED
    )
    assert {h.request.slug for h in resp.results} == {"alpha"}
    resp2 = search.search(
        session.session_id, "alpha", now=1, tenant="acme", status=RequestStatus.QUEUED
    )
    assert resp2.results == ()
