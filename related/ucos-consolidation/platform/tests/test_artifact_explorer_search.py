"""EC2-TASK-000130 — Artifact Explorer search tests (EC2-EPIC-009).

Covers the authorization- and isolation-scoped artifact search: fail-closed construction,
unauthorized/invalid-session paths, empty-query handling, deterministic scoring/ranking,
cross-tenant isolation exclusion, and the consumption of an EC2-EPIC-007
``RequestSearchResponse`` (of ``RequestHit``) via ``from_request_search_response``.
"""

from __future__ import annotations

from platform.artifact_explorer.errors import ArtifactSearchError
from platform.artifact_explorer.search import (
    ArtifactSearch,
    ArtifactSearchResponse,
    ArtifactSearchResult,
)
from platform.foundation.identity import Role
from platform.generation.dispatch import DispatchLedger
from platform.generation.provenance import ProvenanceLedger
from platform.generation.registry import GenerationRequestRegistry
from platform.generation.search import RequestHit, RequestSearchResponse
from platform.identity.service import build_authorization_service
from platform.tests.artifact_explorer_helpers import (
    dispatch_for,
    make_request,
    no_grant_auth,
    provenance_for,
    session,
)

import pytest


def _search(*, authorization=None):
    auth = authorization or build_authorization_service()
    registry = GenerationRequestRegistry()
    dispatch = DispatchLedger()
    provenance = ProvenanceLedger()
    return (
        auth,
        registry,
        dispatch,
        provenance,
        ArtifactSearch(registry, dispatch, provenance, auth),
    )


def test_search_rejects_invalid_components():
    auth = build_authorization_service()
    reg = GenerationRequestRegistry()
    disp = DispatchLedger()
    prov = ProvenanceLedger()
    with pytest.raises(ArtifactSearchError):
        ArtifactSearch("nope", disp, prov, auth)  # type: ignore[arg-type]
    with pytest.raises(ArtifactSearchError):
        ArtifactSearch(reg, "nope", prov, auth)  # type: ignore[arg-type]
    with pytest.raises(ArtifactSearchError):
        ArtifactSearch(reg, disp, "nope", auth)  # type: ignore[arg-type]
    with pytest.raises(ArtifactSearchError):
        ArtifactSearch(reg, disp, prov, "nope")  # type: ignore[arg-type]


def test_search_rejects_non_string_query():
    _, _, _, _, search = _search()
    with pytest.raises(ArtifactSearchError):
        search.search("UCOS-SESS-x", 123, now=1)  # type: ignore[arg-type]


def test_search_unauthorized_for_invalid_session():
    _, _, _, _, search = _search()
    resp = search.search("UCOS-SESS-missing", "artifact", now=1)
    assert resp.authorized is False
    assert resp.results == ()


def test_search_unauthorized_without_grant():
    auth = no_grant_auth()
    _, registry, _, _, search = _search(authorization=auth)
    make_request(registry)
    sess = session(auth, role=Role.OPERATOR, subject="op@x")
    resp = search.search(sess.session_id, "artifact", now=1)
    assert resp.authorized is False


def test_search_empty_query_returns_authorized_empty():
    auth, registry, _, _, search = _search()
    make_request(registry)
    sess = session(auth)
    resp = search.search(sess.session_id, "   ", now=1)
    assert resp.authorized is True
    assert resp.results == ()


def test_search_ranks_and_carries_presence_flags():
    auth, registry, dispatch, provenance, search = _search()
    req = make_request(registry, slug="alpha-data")
    dispatch_for(dispatch, req)
    provenance_for(provenance, req)
    make_request(registry, slug="beta-data")
    sess = session(auth)
    resp = search.search(sess.session_id, "alpha data", now=1)
    assert resp.authorized is True
    assert resp.response_id.startswith("UCOS-AXSR-")
    top = resp.results[0]
    assert top.summary.slug == "alpha-data"
    assert top.summary.has_dispatch is True
    assert top.summary.has_provenance is True
    assert top.score >= resp.results[-1].score
    assert resp.to_dict()["result_count"] == len(resp.results)
    assert resp.fingerprint() == search.search(sess.session_id, "alpha data", now=1).fingerprint()


def test_search_excludes_zero_score_requests():
    auth, registry, dispatch, provenance, search = _search()
    make_request(registry, slug="alpha-data")
    make_request(registry, slug="zeta-widget")  # scores 0 for the query below
    sess = session(auth)
    resp = search.search(sess.session_id, "alpha", now=1)
    assert resp.authorized is True
    slugs = {r.summary.slug for r in resp.results}
    assert slugs == {"alpha-data"}


def test_search_excludes_cross_tenant_artifacts():
    auth, registry, _, _, search = _search()
    make_request(registry, slug="secret-data", tenant="beta")
    intruder = session(auth, subject="x@x", tenant="acme")
    resp = search.search(intruder.session_id, "secret", now=1)
    assert resp.authorized is True
    assert resp.results == ()


# --------------------------------------------------------------------------- #
# Consumption of the EC2-EPIC-007 RequestSearchResponse / RequestHit           #
# --------------------------------------------------------------------------- #


def test_from_request_search_response_projects_hits():
    registry = GenerationRequestRegistry()
    dispatch = DispatchLedger()
    provenance = ProvenanceLedger()
    req = make_request(registry, slug="alpha-data")
    dispatch_for(dispatch, req)
    provenance_for(provenance, req)
    request_response = RequestSearchResponse.create(
        "alpha", True, (RequestHit(request=req, score=3),)
    )
    projected = ArtifactSearchResponse.from_request_search_response(
        request_response, dispatch=dispatch, provenance=provenance
    )
    assert projected.authorized is True
    assert len(projected.results) == 1
    result = projected.results[0]
    assert isinstance(result, ArtifactSearchResult)
    assert result.summary.request_ref == req.request_id
    assert result.summary.has_dispatch is True
    assert result.summary.has_provenance is True
    assert result.score == 3


def test_from_request_search_response_rejects_bad_inputs():
    dispatch = DispatchLedger()
    provenance = ProvenanceLedger()
    good = RequestSearchResponse.create("q", True, ())
    with pytest.raises(ArtifactSearchError):
        ArtifactSearchResponse.from_request_search_response(
            "nope",
            dispatch=dispatch,
            provenance=provenance,  # type: ignore[arg-type]
        )
    with pytest.raises(ArtifactSearchError):
        ArtifactSearchResponse.from_request_search_response(
            good,
            dispatch="nope",
            provenance=provenance,  # type: ignore[arg-type]
        )
    with pytest.raises(ArtifactSearchError):
        ArtifactSearchResponse.from_request_search_response(
            good,
            dispatch=dispatch,
            provenance="nope",  # type: ignore[arg-type]
        )
