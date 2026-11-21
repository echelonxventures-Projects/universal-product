"""EC2-TASK-000079 — Portal global search tests.

Covers deterministic ranking, tenant isolation, authorization-scoped kind filtering,
and the acceptance criterion that global search returns results across ≥4 entity
types. Fail-closed: a kind the caller cannot read is never searched.
"""

from __future__ import annotations

from platform.foundation.identity import Principal, Role
from platform.identity.service import build_authorization_service
from platform.portal.access import PortalAccessGateway
from platform.portal.contracts import EntityKind
from platform.portal.errors import PortalSearchError
from platform.portal.search import (
    GlobalSearch,
    SearchEntity,
    SearchIndex,
    default_search_index,
)

import pytest


def test_search_entity_is_content_addressed_and_validated():
    entity = SearchEntity.create(EntityKind.BLUEPRINT, "My Blueprint", keywords=("alpha",))
    assert entity.entity_id.startswith("UCOS-PSEN-")
    with pytest.raises(PortalSearchError):
        SearchEntity.create(EntityKind.BLUEPRINT, "")
    with pytest.raises(PortalSearchError):
        SearchEntity.create("nope", "x")  # type: ignore[arg-type]


def test_index_query_ranks_deterministically():
    index = SearchIndex(
        [
            SearchEntity.create(EntityKind.BLUEPRINT, "Runtime Blueprint", keywords=("runtime",)),
            SearchEntity.create(EntityKind.ARTIFACT, "Runtime Artifact", keywords=("runtime",)),
        ]
    )
    allowed = frozenset({EntityKind.BLUEPRINT, EntityKind.ARTIFACT})
    a = index.query("runtime", allowed_kinds=allowed)
    b = index.query("runtime", allowed_kinds=allowed)
    assert [r.entity.entity_id for r in a] == [r.entity.entity_id for r in b]
    assert len(a) == 2


def test_index_filters_by_allowed_kinds():
    index = default_search_index()
    only_blueprint = index.query("blueprint", allowed_kinds=frozenset({EntityKind.BLUEPRINT}))
    assert {r.entity.kind for r in only_blueprint} == {EntityKind.BLUEPRINT}


def test_empty_query_returns_nothing():
    index = default_search_index()
    assert index.query("   ", allowed_kinds=frozenset(EntityKind)) == ()


def test_tenant_isolation():
    index = SearchIndex(
        [
            SearchEntity.create(EntityKind.WORKSPACE, "Shared Workspace"),
            SearchEntity.create(EntityKind.WORKSPACE, "Tenant A Workspace", tenant="tenant-a"),
            SearchEntity.create(EntityKind.WORKSPACE, "Tenant B Workspace", tenant="tenant-b"),
        ]
    )
    allowed = frozenset({EntityKind.WORKSPACE})
    scoped = index.query("workspace", allowed_kinds=allowed, tenant="tenant-a")
    titles = {r.entity.title for r in scoped}
    assert "Tenant A Workspace" in titles
    assert "Tenant B Workspace" not in titles
    assert "Shared Workspace" in titles  # untenanted entities are visible to all
    # An unscoped caller sees everything.
    unscoped = index.query("workspace", allowed_kinds=allowed, tenant=None)
    assert len(unscoped) == 3


def _global_search(role: Role, tenant: str | None = None):
    gateway = PortalAccessGateway(build_authorization_service())
    principal = Principal.create("u@ucos", [role], tenant=tenant)
    session = gateway.establish_session(principal, issued_at=0, ttl=100)
    return GlobalSearch(default_search_index(), gateway), session


def test_global_search_spans_at_least_four_entity_types_for_admin():
    search, session = _global_search(Role.PLATFORM_ADMINISTRATOR)
    kinds = search.authorized_kinds(session.session_id, now=1)
    assert len(kinds) >= 4
    response = search.search(session.session_id, "workspace project blueprint artifact", now=1)
    assert len(response.kinds_present) >= 4
    assert response.response_id.startswith("UCOS-PSRS-")


def test_global_search_is_authorization_scoped():
    # The Integrator has no portal grant and scoped catalog access; without a tenant
    # its scoped kinds are denied, so it searches no kinds (fail-closed).
    search, session = _global_search(Role.INTEGRATOR, tenant=None)
    kinds = search.authorized_kinds(session.session_id, now=1)
    assert kinds == frozenset()
    response = search.search(session.session_id, "blueprint", now=1)
    assert response.results == ()


def test_global_search_response_is_deterministic():
    search, session = _global_search(Role.PLATFORM_ADMINISTRATOR)
    a = search.search(session.session_id, "runtime", now=1)
    b = search.search(session.session_id, "runtime", now=1)
    assert a.fingerprint() == b.fingerprint()


def test_global_search_rejects_non_string_query():
    search, session = _global_search(Role.PLATFORM_ADMINISTRATOR)
    with pytest.raises(PortalSearchError):
        search.search(session.session_id, 123, now=1)  # type: ignore[arg-type]


def test_index_add_requires_entity_and_constructors_validate():
    index = SearchIndex()
    with pytest.raises(PortalSearchError):
        index.add("nope")  # type: ignore[arg-type]
    with pytest.raises(PortalSearchError):
        GlobalSearch("nope", None)  # type: ignore[arg-type]


def test_global_search_requires_valid_gateway():
    with pytest.raises(PortalSearchError):
        GlobalSearch(default_search_index(), "nope")  # type: ignore[arg-type]


def test_index_kinds_property():
    index = default_search_index()
    assert EntityKind.BLUEPRINT in index.kinds
    assert len(index.kinds) == 7
