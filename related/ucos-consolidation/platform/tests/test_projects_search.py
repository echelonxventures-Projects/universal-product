"""EC2-TASK-000094 — Project search tests.

Covers the authorization- and isolation-scoped project discovery: fail-closed
construction, denial for an invalid session, denial when authorization refuses, empty
result for an empty query, deterministic token matching/ranking, workspace scoping, and
cross-tenant isolation (P3 — no leak).
"""

from __future__ import annotations

from platform.foundation.identity import Principal, Role
from platform.identity.service import build_authorization_service
from platform.projects.errors import ProjectSearchError
from platform.projects.registry import ProjectRegistry
from platform.projects.search import ProjectSearch

import pytest


def _fixture():
    auth = build_authorization_service()
    reg = ProjectRegistry()
    search = ProjectSearch(reg, auth)
    return auth, reg, search


def _session(auth, role: Role, subject="u@x", tenant=None):
    principal = Principal.create(subject, [role], tenant=tenant)
    return auth.establish_session(principal, issued_at=0, ttl=1000)


def test_construction_validation():
    auth = build_authorization_service()
    with pytest.raises(ProjectSearchError):
        ProjectSearch("nope", auth)  # type: ignore[arg-type]
    with pytest.raises(ProjectSearchError):
        ProjectSearch(ProjectRegistry(), "nope")  # type: ignore[arg-type]


def test_invalid_session_is_unauthorized():
    _, _, search = _fixture()
    response = search.search("UCOS-SESS-missing", "alpha", now=1)
    assert response.authorized is False
    assert response.results == ()


def test_authorization_refused_returns_unauthorized():
    auth, reg, search = _fixture()
    reg.create("alpha", "Alpha", "UCOS-WSPC-1", "dev@x")
    # Integrator's scoped READ is refused when the request tenant does not match.
    session = _session(auth, Role.INTEGRATOR, subject="i@x", tenant="acme")
    response = search.search(session.session_id, "alpha", now=1, tenant=None)
    assert response.authorized is False


def test_empty_query_authorized_but_empty():
    auth, reg, search = _fixture()
    reg.create("alpha", "Alpha", "UCOS-WSPC-1", "dev@x")
    session = _session(auth, Role.DEVELOPER, subject="dev@x")
    response = search.search(session.session_id, "   ", now=1)
    assert response.authorized is True
    assert response.results == ()


def test_query_must_be_string():
    auth, _, search = _fixture()
    session = _session(auth, Role.DEVELOPER, subject="dev@x")
    with pytest.raises(ProjectSearchError):
        search.search(session.session_id, 123, now=1)  # type: ignore[arg-type]


def test_token_matching_and_deterministic_ranking():
    auth, reg, search = _fixture()
    reg.create("alpha-core", "Alpha Core", "UCOS-WSPC-1", "dev@x")
    reg.create("beta", "Beta", "UCOS-WSPC-1", "dev@x")
    session = _session(auth, Role.DEVELOPER, subject="dev@x")
    response = search.search(session.session_id, "alpha", now=1)
    assert response.authorized is True
    assert {h.project.slug for h in response.results} == {"alpha-core"}
    assert response.response_id.startswith("UCOS-PSRE-")
    # deterministic response fingerprint
    again = search.search(session.session_id, "alpha", now=2)
    assert response.fingerprint() == again.fingerprint()


def test_workspace_scoped_search():
    auth, reg, search = _fixture()
    reg.create("alpha", "Alpha", "UCOS-WSPC-1", "dev@x")
    reg.create("alpha", "Alpha", "UCOS-WSPC-2", "dev@x")
    session = _session(auth, Role.DEVELOPER, subject="dev@x")
    response = search.search(session.session_id, "alpha", now=1, workspace_id="UCOS-WSPC-1")
    assert {h.project.workspace_id for h in response.results} == {"UCOS-WSPC-1"}


def test_cross_tenant_projects_are_not_leaked():
    auth, reg, search = _fixture()
    reg.create("alpha", "Alpha", "UCOS-WSPC-1", "dev@x", tenant="acme")
    reg.create("alpha", "Alpha Beta", "UCOS-WSPC-2", "dev@x", tenant="beta")
    # A tenant-acme developer searching unscoped (tenant=None) exercises the isolation
    # filter: discover returns both, but the beta project is filtered out (P3 — no leak).
    session = _session(auth, Role.DEVELOPER, subject="dev@x", tenant="acme")
    response = search.search(session.session_id, "alpha", now=1)
    tenants = {h.project.tenant for h in response.results}
    assert "beta" not in tenants
    assert tenants == {"acme"}
