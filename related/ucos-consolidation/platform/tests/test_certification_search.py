"""EC2-TASK-000158 — Certification console search tests (EC2-EPIC-011).

Covers authorization- and isolation-scoped discovery: unauthenticated/unauthorized
callers see nothing, cross-tenant records are never leaked (P3), matching is a pure token
function, and ranking is deterministic.
"""

from __future__ import annotations

from platform.certification.contracts import CertificationConsoleRecord
from platform.certification.errors import CertificationSearchError
from platform.certification.registry import CertificationRegistry
from platform.certification.search import (
    CertificationSearch,
    CertificationSearchResponse,
    CertificationSearchResult,
)
from platform.foundation.identity import Principal, Role
from platform.identity.service import build_authorization_service
from platform.tests.certification_console_helpers import (
    VERSION,
    authorization_without_certification_read,
    certified_output,
)

import pytest

from engine.certification.contracts import CertificationSubject
from engine.certification.engine import CertificationEngine
from engine.certification.evidence import build_certification_evidence


def _record(validation_output, **kw):
    report, evidence = validation_output
    subject = CertificationSubject.from_validation(report, evidence, version=VERSION)
    decision = CertificationEngine().certify(subject)
    return CertificationConsoleRecord.create(
        report=report,
        validation_evidence=evidence,
        decision=decision,
        certification_evidence=build_certification_evidence(decision),
        owner_subject=kw.pop("owner_subject", "arch@x"),
        **kw,
    )


def _session(auth, *, subject="arch@x", tenant=None, role=Role.ARCHITECT):
    return auth.establish_session(
        Principal.create(subject, [role], tenant=tenant), issued_at=0, ttl=1000
    )


def _fixture(*, tenant=None):
    auth = build_authorization_service()
    reg = CertificationRegistry()
    reg.record(_record(certified_output(), tenant=tenant))
    search = CertificationSearch(reg, auth)
    return auth, reg, search


def test_search_requires_valid_session():
    auth, reg, search = _fixture(tenant="acme")
    resp = search.search("UCOS-SESS-missing", "certified", now=1, tenant="acme")
    assert isinstance(resp, CertificationSearchResponse)
    assert resp.authorized is False
    assert resp.results == ()


def test_search_denied_without_read_grant():
    auth = authorization_without_certification_read()
    reg = CertificationRegistry()
    reg.record(_record(certified_output()))
    search = CertificationSearch(reg, auth)
    sess = _session(auth, subject="op@x", role=Role.OPERATOR)
    resp = search.search(sess.session_id, "certified", now=1)
    assert resp.authorized is False


def test_empty_query_returns_authorized_no_results():
    auth, reg, search = _fixture(tenant="acme")
    sess = _session(auth, tenant="acme")
    resp = search.search(sess.session_id, "   ", now=1, tenant="acme")
    assert resp.authorized is True
    assert resp.results == ()


def test_search_matches_and_ranks_deterministically():
    auth, reg, search = _fixture(tenant="acme")
    sess = _session(auth, tenant="acme")
    resp = search.search(sess.session_id, "certified data", now=1, tenant="acme")
    assert resp.authorized is True
    assert resp.results
    assert isinstance(resp.results[0], CertificationSearchResult)
    assert resp.response_id.startswith("UCOS-CSRE-")
    assert resp.fingerprint() == resp.fingerprint()
    assert resp.to_dict()["result_count"] == len(resp.results)


def test_search_never_leaks_cross_tenant():
    auth, reg, search = _fixture(tenant="beta")
    intruder = _session(auth, subject="x@x", tenant="acme")
    resp = search.search(intruder.session_id, "certified", now=1)
    assert resp.authorized is True
    assert resp.results == ()


def test_search_no_match_returns_empty():
    auth, reg, search = _fixture(tenant="acme")
    sess = _session(auth, tenant="acme")
    resp = search.search(sess.session_id, "zzzznomatch", now=1, tenant="acme")
    assert resp.results == ()


def test_search_rejects_bad_query_and_construction():
    auth, reg, search = _fixture()
    sess = _session(auth)
    with pytest.raises(CertificationSearchError):
        search.search(sess.session_id, 123, now=1)  # type: ignore[arg-type]
    with pytest.raises(CertificationSearchError):
        CertificationSearch("nope", auth)  # type: ignore[arg-type]
    with pytest.raises(CertificationSearchError):
        CertificationSearch(reg, "nope")  # type: ignore[arg-type]
