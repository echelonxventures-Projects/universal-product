"""EC2-TASK-000105 — Blueprint search tests (EC2-EPIC-006, PC-13, P3)."""

from __future__ import annotations

from platform.blueprints.contracts import BlueprintFamily
from platform.blueprints.errors import BlueprintSearchError
from platform.blueprints.registry import BlueprintRegistry
from platform.blueprints.search import BlueprintSearch
from platform.foundation.identity import Principal, Role
from platform.identity.service import build_authorization_service

import pytest


def _fixture():
    auth = build_authorization_service()
    reg = BlueprintRegistry()
    reg.create("payments-data", "Payments Data", "ws1", "o", BlueprintFamily.DATA, tenant="acme")
    reg.create("orders-event", "Orders Event", "ws1", "o", BlueprintFamily.EVENT, tenant="beta")
    reg.create("global-api", "Global API", "ws1", "o", BlueprintFamily.API)
    return auth, reg, BlueprintSearch(reg, auth)


def _session(auth, role, subject="u@x", tenant=None):
    return auth.establish_session(
        Principal.create(subject, [role], tenant=tenant), issued_at=0, ttl=1000
    )


def test_search_requires_valid_components():
    auth = build_authorization_service()
    with pytest.raises(BlueprintSearchError):
        BlueprintSearch("nope", auth)  # type: ignore[arg-type]
    with pytest.raises(BlueprintSearchError):
        BlueprintSearch(BlueprintRegistry(), "nope")  # type: ignore[arg-type]


def test_search_matches_by_slug_name_and_family():
    auth, _, search = _fixture()
    session = _session(auth, Role.ARCHITECT)
    resp = search.search(session.session_id, "data", now=1)
    assert resp.authorized is True
    assert {h.blueprint.slug for h in resp.results} == {"payments-data"}
    assert resp.response_id.startswith("UCOS-BSRE-")
    # family token matches
    assert {
        h.blueprint.slug for h in search.search(session.session_id, "event", now=1).results
    } == {"orders-event"}


def test_search_is_isolation_scoped():
    auth, _, search = _fixture()
    acme = _session(auth, Role.ARCHITECT, subject="a@x", tenant="acme")
    resp = search.search(acme.session_id, "data event api", now=1)
    slugs = {h.blueprint.slug for h in resp.results}
    assert "payments-data" in slugs
    assert "global-api" in slugs  # untenanted visible
    assert "orders-event" not in slugs  # cross-tenant filtered


def test_search_unauthorized_returns_unauthorized_empty():
    auth, _, search = _fixture()
    op = _session(auth, Role.OPERATOR)  # no READ on blueprint-catalog
    resp = search.search(op.session_id, "data", now=1)
    assert resp.authorized is False
    assert resp.results == ()


def test_search_invalid_session_and_empty_query():
    auth, _, search = _fixture()
    assert search.search("UCOS-SESS-missing", "data", now=1).authorized is False
    session = _session(auth, Role.ARCHITECT)
    empty = search.search(session.session_id, "   ", now=1)
    assert empty.authorized is True
    assert empty.results == ()


def test_search_rejects_non_string_query():
    auth, _, search = _fixture()
    session = _session(auth, Role.ARCHITECT)
    with pytest.raises(BlueprintSearchError):
        search.search(session.session_id, 5, now=1)  # type: ignore[arg-type]


def test_search_ranking_is_deterministic():
    auth, _, search = _fixture()
    session = _session(auth, Role.ARCHITECT)
    a = search.search(session.session_id, "data event api", now=1)
    b = search.search(session.session_id, "data event api", now=1)
    assert a.fingerprint() == b.fingerprint()
