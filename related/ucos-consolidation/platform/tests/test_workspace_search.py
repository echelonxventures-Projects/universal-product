"""EC2-TASK-000087 — Workspace search tests.

Covers the deterministic, authorization- and isolation-scoped workspace discovery:
fail-closed construction, unauthenticated/denied searches return empty (never leak),
pure case-insensitive token matching + deterministic ranking, cross-tenant isolation
filtering (P3 — search can never surface a cross-tenant workspace), response/hit
serialization, and reproducibility (P5).
"""

from __future__ import annotations

from platform.foundation.identity import Principal, Role
from platform.identity.service import build_authorization_service
from platform.workspace.errors import WorkspaceSearchError
from platform.workspace.metadata import WorkspaceMetadata
from platform.workspace.registration import WorkspaceRegistry
from platform.workspace.search import WorkspaceHit, WorkspaceSearch, WorkspaceSearchResponse

import pytest


def _auth():
    return build_authorization_service()


def _session(auth, role: Role, subject: str = "u@x", tenant: str | None = None):
    principal = Principal.create(subject, [role], tenant=tenant)
    return auth.establish_session(principal, issued_at=0, ttl=1000)


def _seed_registry() -> WorkspaceRegistry:
    reg = WorkspaceRegistry()
    reg.create("acme-core", "Acme Core Platform", "o@x", tenant="acme")
    reg.create("acme-labs", "Acme Labs", "o@x", tenant="acme")
    reg.create(
        "beta-core",
        "Beta Core",
        "o@x",
        tenant="beta",
        metadata=WorkspaceMetadata.create(labels=["core"]),
    )
    reg.create("global-hub", "Global Hub", "o@x")  # untenanted / global
    return reg


def test_construction_is_fail_closed():
    auth = _auth()
    with pytest.raises(WorkspaceSearchError):
        WorkspaceSearch("nope", auth)  # type: ignore[arg-type]
    with pytest.raises(WorkspaceSearchError):
        WorkspaceSearch(WorkspaceRegistry(), "nope")  # type: ignore[arg-type]


def test_query_must_be_a_string():
    auth = _auth()
    session = _session(auth, Role.DEVELOPER)
    search = WorkspaceSearch(_seed_registry(), auth)
    with pytest.raises(WorkspaceSearchError):
        search.search(session.session_id, 123, now=1)  # type: ignore[arg-type]


def test_invalid_session_returns_unauthorized_empty():
    auth = _auth()
    search = WorkspaceSearch(_seed_registry(), auth)
    response = search.search("UCOS-SESS-missing", "acme", now=1)
    assert response.authorized is False
    assert response.results == ()
    assert response.response_id.startswith("UCOS-WSRS-")


def test_denied_authorization_returns_unauthorized_empty():
    # An Integrator holds only a *scoped* READ; a request without a matching tenant
    # is denied by the policy, so search returns unauthorized/empty (no leak).
    auth = _auth()
    session = _session(auth, Role.INTEGRATOR, tenant="acme")
    search = WorkspaceSearch(_seed_registry(), auth)
    response = search.search(session.session_id, "acme", now=1, tenant=None)
    assert response.authorized is False
    assert response.results == ()


def test_authorized_empty_query_returns_no_results():
    auth = _auth()
    session = _session(auth, Role.DEVELOPER)
    search = WorkspaceSearch(_seed_registry(), auth)
    response = search.search(session.session_id, "   ", now=1)
    assert response.authorized is True
    assert response.results == ()


def test_token_match_is_case_insensitive_over_slug_name_and_labels():
    auth = _auth()
    session = _session(auth, Role.DEVELOPER)
    search = WorkspaceSearch(_seed_registry(), auth)
    response = search.search(session.session_id, "ACME", now=1)
    assert response.authorized is True
    slugs = {hit.workspace.slug for hit in response.results}
    assert slugs == {"acme-core", "acme-labs"}
    # label-only match (the "core" label on beta-core, plus slug/name matches)
    by_label = search.search(session.session_id, "core", now=1)
    assert "beta-core" in {h.workspace.slug for h in by_label.results}


def test_ranking_is_deterministic_by_score_then_slug():
    auth = _auth()
    session = _session(auth, Role.DEVELOPER)
    search = WorkspaceSearch(_seed_registry(), auth)
    response = search.search(session.session_id, "acme core", now=1)
    # acme-core matches both tokens (score 2) and ranks ahead of acme-labs (score 1).
    assert response.results[0].workspace.slug == "acme-core"
    assert response.results[0].score == 2
    assert [h.workspace.slug for h in response.results][:2] == ["acme-core", "acme-labs"]


def test_search_filters_cross_tenant_workspaces():
    # A developer (unscoped READ) bound to tenant "acme" searching globally must never
    # see the "beta" workspace — the isolation guard removes it (P3).
    auth = _auth()
    session = _session(auth, Role.DEVELOPER, tenant="acme")
    search = WorkspaceSearch(_seed_registry(), auth)
    response = search.search(session.session_id, "core", now=1, tenant=None)
    slugs = {hit.workspace.slug for hit in response.results}
    assert "beta-core" not in slugs
    assert "acme-core" in slugs  # tenant match retained


def test_response_is_deterministic_and_serializable():
    def run() -> str:
        auth = _auth()
        session = _session(auth, Role.PLATFORM_ADMINISTRATOR)
        search = WorkspaceSearch(_seed_registry(), auth)
        return search.search(session.session_id, "acme core", now=1).fingerprint()

    assert run() == run()

    auth = _auth()
    session = _session(auth, Role.PLATFORM_ADMINISTRATOR)
    response = WorkspaceSearch(_seed_registry(), auth).search(session.session_id, "acme", now=1)
    d = response.to_dict()
    assert d["authorized"] is True
    assert d["result_count"] == len(response.results)
    assert d["results"][0]["score"] >= 1


def test_workspace_hit_serializes():
    reg = _seed_registry()
    ws = reg.resolve("acme-core", "acme")
    hit = WorkspaceHit(workspace=ws, score=3)
    assert hit.to_dict() == {"workspace": ws.to_dict(), "score": 3}


def test_empty_response_helper_is_content_addressed():
    response = WorkspaceSearchResponse.create("q", False, ())
    assert response.response_id.startswith("UCOS-WSRS-")
    assert response.to_dict()["result_count"] == 0
