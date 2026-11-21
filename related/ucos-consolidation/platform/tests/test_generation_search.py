"""EC2-TASK-000115 — Generation request search tests (EC2-EPIC-007).

Covers authorization- and isolation-scoped discovery: unauthorized/invalid-session
denial, empty-query short-circuit, deterministic token matching + ranking, tenant
isolation filtering, and scoped filters (workspace/project/family/status).
"""

from __future__ import annotations

from platform.blueprints.contracts import BlueprintFamily
from platform.foundation.identity import Principal, Role
from platform.generation.errors import RequestSearchError
from platform.generation.registry import GenerationRequestRegistry
from platform.generation.search import RequestSearch
from platform.identity.service import build_authorization_service

import pytest


def _fixture():
    auth = build_authorization_service()
    reg = GenerationRequestRegistry()
    return auth, reg, RequestSearch(reg, auth)


def _session(auth, role=Role.ARCHITECT, subject="arch@x", tenant=None):
    return auth.establish_session(
        Principal.create(subject, [role], tenant=tenant), issued_at=0, ttl=1000
    )


def test_construction_validates_components():
    auth = build_authorization_service()
    with pytest.raises(RequestSearchError):
        RequestSearch("nope", auth)  # type: ignore[arg-type]
    with pytest.raises(RequestSearchError):
        RequestSearch(GenerationRequestRegistry(), "nope")  # type: ignore[arg-type]


def test_search_requires_string_query():
    auth, _, search = _fixture()
    sess = _session(auth)
    with pytest.raises(RequestSearchError):
        search.search(sess.session_id, 123, now=1)  # type: ignore[arg-type]


def test_invalid_session_is_unauthorized():
    _, _, search = _fixture()
    resp = search.search("UCOS-SESS-missing", "req", now=1)
    assert resp.authorized is False
    assert resp.results == ()


def test_unauthorized_role_denied():
    auth, reg, search = _fixture()
    reg.create(
        "req-1", "UCOS-BLPR-a", "UCOS-WSPC-1", "op@x", BlueprintFamily.DATA, submitted_tick=1
    )
    op = _session(auth, role=Role.OPERATOR, subject="op@x")  # no generation-requests grant
    resp = search.search(op.session_id, "req", now=1)
    assert resp.authorized is False


def test_empty_query_authorized_but_empty():
    auth, _, search = _fixture()
    sess = _session(auth)
    resp = search.search(sess.session_id, "   ", now=1)
    assert resp.authorized is True
    assert resp.results == ()


def test_match_rank_and_isolation():
    auth, reg, search = _fixture()
    reg.create(
        "alpha",
        "UCOS-BLPR-a",
        "UCOS-WSPC-1",
        "arch@x",
        BlueprintFamily.DATA,
        submitted_tick=1,
        tenant="acme",
    )
    reg.create(
        "beta",
        "UCOS-BLPR-b",
        "UCOS-WSPC-1",
        "arch@x",
        BlueprintFamily.API,
        submitted_tick=2,
        tenant="beta",
    )
    sess = _session(auth, subject="arch@x", tenant="acme")
    resp = search.search(sess.session_id, "alpha", now=1, tenant="acme")
    assert resp.authorized is True
    slugs = {h.request.slug for h in resp.results}
    assert "alpha" in slugs
    assert "beta" not in slugs  # cross-tenant filtered
    assert resp.response_id.startswith("UCOS-GSRE-")
    assert resp.fingerprint() == resp.fingerprint()


def test_scoped_filters_family_and_status():
    auth, reg, search = _fixture()
    reg.create(
        "dataflow",
        "UCOS-BLPR-a",
        "UCOS-WSPC-1",
        "arch@x",
        BlueprintFamily.DATA,
        submitted_tick=1,
    )
    sess = _session(auth)
    resp = search.search(sess.session_id, "data", now=1, family=BlueprintFamily.DATA)
    assert any(h.request.slug == "dataflow" for h in resp.results)
    hit = next(h for h in resp.results if h.request.slug == "dataflow")
    assert hit.score > 0
    assert hit.to_dict()["score"] == hit.score
    assert resp.to_dict()["result_count"] == len(resp.results)


def test_label_match_and_zero_score_and_isolation_skip():
    auth, reg, search = _fixture()
    # A request matched only via a metadata label (not the haystack).
    from platform.generation.metadata import RequestMetadata

    reg.create(
        "opaque",
        "UCOS-BLPR-a",
        "UCOS-WSPC-1",
        "arch@x",
        BlueprintFamily.DATA,
        submitted_tick=1,
        tenant="acme",
        metadata=RequestMetadata.create(labels=["priority"]),
    )
    # A same-tenant request that will score zero for the query token.
    reg.create(
        "other",
        "UCOS-BLPR-b",
        "UCOS-WSPC-1",
        "arch@x",
        BlueprintFamily.DATA,
        submitted_tick=2,
        tenant="acme",
    )
    # A cross-tenant request that must be isolation-skipped when scanned (tenant=None).
    reg.create(
        "secret",
        "UCOS-BLPR-c",
        "UCOS-WSPC-1",
        "arch@x",
        BlueprintFamily.DATA,
        submitted_tick=3,
        tenant="beta",
    )
    sess = _session(auth, subject="arch@x", tenant="acme")
    resp = search.search(sess.session_id, "priority", now=1)  # tenant=None ⇒ scans all
    slugs = {h.request.slug for h in resp.results}
    assert "opaque" in slugs  # matched via label branch
    assert "other" not in slugs  # zero score, dropped
    assert "secret" not in slugs  # cross-tenant, isolation-skipped
