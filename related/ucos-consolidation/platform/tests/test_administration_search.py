"""EC2-CAP-ADMIN-001 — Administrative search tests.

Covers the authorization-scoped administrative search: fail-closed construction, an
empty/unauthorized response for an invalid session or an unauthorized (non-admin)
caller, ranked matching over settings and administrator assignments, empty-query
handling, and deterministic responses.
"""

from __future__ import annotations

from platform.administration.configuration import AdministrativeConfiguration
from platform.administration.contracts import AdministrativeScope
from platform.administration.errors import AdministrationSearchError
from platform.administration.membership import AdministrativeMembershipRegistry
from platform.administration.search import AdministrativeSearch
from platform.foundation.identity import Principal, Role
from platform.identity.service import build_authorization_service

import pytest


def _fixture(role=Role.PLATFORM_ADMINISTRATOR, subject="admin@x", tenant=None):
    auth = build_authorization_service()
    config = AdministrativeConfiguration()
    members = AdministrativeMembershipRegistry()
    config.set(AdministrativeScope.PLATFORM, "retention-policy", "long", tick=1)
    members.add(AdministrativeScope.TENANT, "acme", "UCOS-PRIN-a", "alice@x", tick=1, tenant="acme")
    search = AdministrativeSearch(config, members, auth)
    principal = Principal.create(subject, [role], tenant=tenant)
    session = auth.establish_session(principal, issued_at=0, ttl=1000)
    return search, session


def test_construction_validates_components():
    auth = build_authorization_service()
    config = AdministrativeConfiguration()
    members = AdministrativeMembershipRegistry()
    with pytest.raises(AdministrationSearchError):
        AdministrativeSearch("nope", members, auth)  # type: ignore[arg-type]
    with pytest.raises(AdministrationSearchError):
        AdministrativeSearch(config, "nope", auth)  # type: ignore[arg-type]
    with pytest.raises(AdministrationSearchError):
        AdministrativeSearch(config, members, "nope")  # type: ignore[arg-type]


def test_search_rejects_non_string_query():
    search, session = _fixture()
    with pytest.raises(AdministrationSearchError):
        search.search(session.session_id, 5, now=1)  # type: ignore[arg-type]


def test_invalid_session_is_unauthorized_empty():
    search, _ = _fixture()
    response = search.search("UCOS-SESS-missing", "retention", now=1)
    assert response.authorized is False
    assert response.results == ()


def test_unauthorized_role_is_empty():
    # Developer holds no READ on administration-policy → unauthorized.
    search, session = _fixture(role=Role.DEVELOPER, subject="dev@x")
    response = search.search(session.session_id, "retention", now=1)
    assert response.authorized is False


def test_auditor_may_search_read_only():
    search, session = _fixture(role=Role.AUDITOR, subject="aud@x")
    response = search.search(session.session_id, "retention", now=1)
    assert response.authorized is True
    assert any(h.kind == "setting" for h in response.results)


def test_empty_query_is_authorized_but_empty():
    search, session = _fixture()
    response = search.search(session.session_id, "   ", now=1)
    assert response.authorized is True
    assert response.results == ()


def test_search_matches_settings_and_members_ranked():
    search, session = _fixture()
    response = search.search(session.session_id, "retention acme", now=1)
    kinds = [h.kind for h in response.results]
    # deterministic ordering: 'member' sorts before 'setting'
    assert kinds == sorted(kinds)
    assert {"setting", "member"} <= set(kinds)
    assert response.response_id.startswith("UCOS-ASRS-")


def test_search_skips_non_matching_subjects():
    auth = build_authorization_service()
    config = AdministrativeConfiguration()
    members = AdministrativeMembershipRegistry()
    config.set(AdministrativeScope.PLATFORM, "retention-policy", "long", tick=1)
    config.set(AdministrativeScope.PLATFORM, "unrelated-flag", "off", tick=2)
    members.add(AdministrativeScope.TENANT, "acme", "UCOS-PRIN-a", "alice@x", tick=1, tenant="acme")
    members.add(AdministrativeScope.TENANT, "beta", "UCOS-PRIN-b", "bob@x", tick=2, tenant="beta")
    search = AdministrativeSearch(config, members, auth)
    principal = Principal.create("admin@x", [Role.PLATFORM_ADMINISTRATOR])
    session = auth.establish_session(principal, issued_at=0, ttl=1000)
    # Only the retention setting and the acme member match; the others are skipped.
    response = search.search(session.session_id, "retention acme", now=1)
    identifiers = {h.detail.get("key", h.detail.get("target")) for h in response.results}
    assert "retention-policy" in identifiers
    assert "unrelated-flag" not in identifiers
    assert "beta" not in identifiers


def test_response_is_deterministic_and_serializable():
    def run() -> str:
        search, session = _fixture()
        return search.search(session.session_id, "retention", now=1).fingerprint()

    assert run() == run()
    search, session = _fixture()
    data = search.search(session.session_id, "retention", now=1).to_dict()
    assert data["authorized"] is True
    assert data["result_count"] >= 1
