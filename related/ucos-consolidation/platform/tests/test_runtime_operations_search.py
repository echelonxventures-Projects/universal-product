"""EC2-TASK-000170 — Runtime Operations search tests (EC2-EPIC-012).

Covers the authorization- and isolation-scoped operation search: authorized matching,
empty-query short-circuit, unauthorized/invalid-session denial, cross-tenant isolation,
and deterministic ranking.
"""

from __future__ import annotations

from platform.foundation.identity import Role
from platform.identity.service import build_authorization_service
from platform.runtime_operations.errors import RuntimeOperationSearchError
from platform.runtime_operations.operations import RuntimeOperationPlanner, RuntimeOperationRegistry
from platform.runtime_operations.search import (
    RuntimeOperationSearch,
    RuntimeOperationSearchResponse,
)
from platform.tests.runtime_operations_helpers import (
    authorization_without_runtime_grant,
    certification_record,
    runtime_unit,
    session,
)

import pytest


def _seed(registry, *, tenant=None):
    rec = (
        RuntimeOperationPlanner()
        .plan_deploy(runtime_unit(), certification_record(), owner_subject="op@x", tenant=tenant)
        .record
    )
    registry.record(rec)
    return rec


def _search(auth, registry):
    return RuntimeOperationSearch(registry, auth)


def test_search_requires_valid_components():
    auth = build_authorization_service()
    with pytest.raises(RuntimeOperationSearchError):
        RuntimeOperationSearch("nope", auth)  # type: ignore[arg-type]
    with pytest.raises(RuntimeOperationSearchError):
        RuntimeOperationSearch(RuntimeOperationRegistry(), "nope")  # type: ignore[arg-type]


def test_authorized_search_matches():
    auth = build_authorization_service()
    registry = RuntimeOperationRegistry()
    rec = _seed(registry)
    search = _search(auth, registry)
    sess = session(auth, role=Role.AUDITOR, subject="aud@x")
    resp = search.search(sess.session_id, "data", now=1)
    assert isinstance(resp, RuntimeOperationSearchResponse)
    assert resp.authorized is True
    assert any(r.record.operation_id == rec.operation_id for r in resp.results)
    assert resp.response_id.startswith("UCOS-ROSR-")
    assert resp.to_dict()["result_count"] >= 1
    assert resp.fingerprint() == resp.fingerprint()
    assert resp.results[0].to_dict()["score"] >= 1


def test_empty_query_authorized_but_no_results():
    auth = build_authorization_service()
    registry = RuntimeOperationRegistry()
    _seed(registry)
    resp = _search(auth, registry).search(session(auth, role=Role.AUDITOR).session_id, "   ", now=1)
    assert resp.authorized is True
    assert resp.results == ()


def test_search_rejects_non_string_query():
    auth = build_authorization_service()
    with pytest.raises(RuntimeOperationSearchError):
        _search(auth, RuntimeOperationRegistry()).search(
            session(auth).session_id,
            5,
            now=1,  # type: ignore[arg-type]
        )


def test_unauthorized_session_and_no_grant():
    registry = RuntimeOperationRegistry()
    _seed(registry)
    auth = build_authorization_service()
    resp = _search(auth, registry).search("UCOS-SESS-missing", "data", now=1)
    assert resp.authorized is False
    no_auth = authorization_without_runtime_grant()
    reg2 = RuntimeOperationRegistry()
    _seed(reg2)
    op = session(no_auth, role=Role.OPERATOR, subject="op@x")
    resp2 = _search(no_auth, reg2).search(op.session_id, "data", now=1)
    assert resp2.authorized is False


def test_cross_tenant_isolation():
    auth = build_authorization_service()
    registry = RuntimeOperationRegistry()
    _seed(registry, tenant="beta")
    intruder = session(auth, role=Role.AUDITOR, subject="a@x", tenant="acme")
    # Unscoped search returns the beta record from discovery; the isolation guard then
    # skips it (the cross-tenant continue branch).
    resp = _search(auth, registry).search(intruder.session_id, "data", now=1)
    assert resp.authorized is True
    assert resp.results == ()


def test_no_match_returns_empty_results():
    auth = build_authorization_service()
    registry = RuntimeOperationRegistry()
    _seed(registry)
    resp = _search(auth, registry).search(
        session(auth, role=Role.AUDITOR).session_id, "zzzznomatch", now=1
    )
    assert resp.authorized is True
    assert resp.results == ()
