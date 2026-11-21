"""EC2-TASK-000149 — Validation console search tests (EC2-EPIC-010).

Covers authorization- and isolation-scoped discovery: unauthenticated/unauthorized
callers see nothing, cross-tenant records are never leaked (P3), matching is a pure token
function, and ranking is deterministic.
"""

from __future__ import annotations

from platform.foundation.identity import Principal, Role
from platform.identity.service import build_authorization_service
from platform.tests.validation_console_helpers import (
    accepted_subject,
    authorization_without_validation_read,
)
from platform.validation.contracts import ValidationRecord
from platform.validation.errors import ValidationSearchError
from platform.validation.registry import ValidationRecordRegistry
from platform.validation.search import (
    ValidationSearch,
    ValidationSearchResponse,
    ValidationSearchResult,
)

import pytest

from engine.validation.evidence import build_validation_evidence
from engine.validation.executor import ValidationEngine
from engine.validation.gates import enforce_acceptance


def _record(subject, **kw):
    report = ValidationEngine().validate(subject)
    return ValidationRecord.create(
        report=report,
        evidence=build_validation_evidence(report),
        decision=enforce_acceptance(report),
        subject=subject,
        owner_subject=kw.pop("owner_subject", "arch@x"),
        **kw,
    )


def _session(auth, *, subject="arch@x", tenant=None, role=Role.ARCHITECT):
    return auth.establish_session(
        Principal.create(subject, [role], tenant=tenant), issued_at=0, ttl=1000
    )


def _fixture(*, tenant=None):
    auth = build_authorization_service()
    reg = ValidationRecordRegistry()
    reg.record(_record(accepted_subject(), tenant=tenant))
    search = ValidationSearch(reg, auth)
    return auth, reg, search


def test_search_requires_valid_session():
    auth, reg, search = _fixture(tenant="acme")
    resp = search.search("UCOS-SESS-missing", "data", now=1, tenant="acme")
    assert isinstance(resp, ValidationSearchResponse)
    assert resp.authorized is False
    assert resp.results == ()


def test_search_denied_without_read_grant():
    auth = authorization_without_validation_read()
    reg = ValidationRecordRegistry()
    reg.record(_record(accepted_subject()))
    search = ValidationSearch(reg, auth)
    session = _session(auth, subject="op@x", role=Role.OPERATOR)
    resp = search.search(session.session_id, "data", now=1)
    assert resp.authorized is False


def test_empty_query_returns_authorized_no_results():
    auth, reg, search = _fixture(tenant="acme")
    session = _session(auth, tenant="acme")
    resp = search.search(session.session_id, "   ", now=1, tenant="acme")
    assert resp.authorized is True
    assert resp.results == ()


def test_search_matches_and_ranks_deterministically():
    auth, reg, search = _fixture(tenant="acme")
    session = _session(auth, tenant="acme")
    resp = search.search(session.session_id, "data pass", now=1, tenant="acme")
    assert resp.authorized is True
    assert resp.results
    assert isinstance(resp.results[0], ValidationSearchResult)
    assert resp.response_id.startswith("UCOS-VSRE-")
    assert resp.fingerprint() == resp.fingerprint()
    assert resp.to_dict()["result_count"] == len(resp.results)


def test_search_never_leaks_cross_tenant():
    auth, reg, search = _fixture(tenant="beta")
    intruder = _session(auth, subject="x@x", tenant="acme")
    resp = search.search(intruder.session_id, "data", now=1)
    assert resp.authorized is True
    assert resp.results == ()


def test_search_no_match_returns_empty():
    auth, reg, search = _fixture(tenant="acme")
    session = _session(auth, tenant="acme")
    resp = search.search(session.session_id, "zzzznomatch", now=1, tenant="acme")
    assert resp.results == ()


def test_search_rejects_bad_query_and_construction():
    auth, reg, search = _fixture()
    session = _session(auth)
    with pytest.raises(ValidationSearchError):
        search.search(session.session_id, 123, now=1)  # type: ignore[arg-type]
    with pytest.raises(ValidationSearchError):
        ValidationSearch("nope", auth)  # type: ignore[arg-type]
    with pytest.raises(ValidationSearchError):
        ValidationSearch(reg, "nope")  # type: ignore[arg-type]
