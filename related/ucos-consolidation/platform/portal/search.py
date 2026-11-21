"""EC2-TASK-000079 — Portal Global Search (EC2-EPIC-003).

The portal's **global search & discovery** capability (PC-13). It answers the
acceptance criterion *"global search returns results across ≥4 entity types"* while
honoring platform authorization and tenant isolation:

    * :class:`SearchEntity` — an immutable, content-addressed searchable record of one
      of the seven :class:`~platform.portal.contracts.EntityKind` s (workspaces,
      projects, blueprints, generation requests, artifacts, validation reports,
      certifications), optionally tenant-scoped.
    * :class:`SearchIndex` — a deterministic in-memory index; matching is a pure,
      case-insensitive token function and ranking is fully deterministic
      (score, then title, then id) so identical queries yield identical results.
    * :class:`GlobalSearch` — the portal entry point. It computes the set of entity
      kinds the caller is authorized to see (READ on each kind's §3.2 capability
      group, via the Identity Layer), applies tenant isolation, and returns only
      authorized hits. Fail-closed: a kind the caller cannot read is never searched.
"""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
from platform.foundation.contracts import content_hash
from platform.foundation.identity import Permission
from platform.portal.access import PortalAccessGateway
from platform.portal.contracts import EntityKind, all_entity_kinds, entity_kind_group
from platform.portal.errors import PortalSearchError
from typing import Any


def _tokens(text: str) -> tuple[str, ...]:
    """Deterministic lowercase whitespace tokenization."""
    return tuple(t for t in text.lower().split() if t)


@dataclass(frozen=True, slots=True)
class SearchEntity:
    """An immutable, content-addressed searchable platform entity."""

    kind: EntityKind
    title: str
    keywords: frozenset[str]
    tenant: str | None = None
    entity_id: str = ""

    @classmethod
    def create(
        cls,
        kind: EntityKind,
        title: str,
        *,
        keywords: Iterable[str] | None = None,
        tenant: str | None = None,
    ) -> SearchEntity:
        if not isinstance(kind, EntityKind):
            raise PortalSearchError("search entity kind must be an EntityKind")
        if not isinstance(title, str) or not title:
            raise PortalSearchError("search entity requires a title")
        kw = frozenset(k.lower() for k in (keywords or ()) if k)
        core = {
            "kind": kind.value,
            "title": title,
            "keywords": sorted(kw),
            "tenant": tenant,
        }
        return cls(
            kind=kind,
            title=title,
            keywords=kw,
            tenant=tenant,
            entity_id=f"UCOS-PSEN-{content_hash(core)[:16]}",
        )

    def score(self, query_tokens: tuple[str, ...]) -> int:
        """Deterministic match score: number of query tokens found in this entity."""
        haystack = self.title.lower()
        matched = 0
        for token in set(query_tokens):
            if token in haystack or any(token in kw for kw in self.keywords):
                matched += 1
        return matched

    def to_dict(self) -> dict[str, Any]:
        return {
            "entity_id": self.entity_id,
            "kind": self.kind.value,
            "title": self.title,
            "keywords": sorted(self.keywords),
            "tenant": self.tenant,
        }


@dataclass(frozen=True, slots=True)
class SearchResult:
    """An immutable ranked search hit."""

    entity: SearchEntity
    score: int

    def to_dict(self) -> dict[str, Any]:
        return {"entity": self.entity.to_dict(), "score": self.score}


@dataclass(frozen=True, slots=True)
class SearchResponse:
    """An immutable, content-addressed search response over authorized kinds."""

    query: str
    kinds_searched: tuple[EntityKind, ...]
    results: tuple[SearchResult, ...]
    response_id: str = ""

    @classmethod
    def create(
        cls,
        query: str,
        kinds_searched: tuple[EntityKind, ...],
        results: tuple[SearchResult, ...],
    ) -> SearchResponse:
        core = {
            "query": query,
            "kinds_searched": [k.value for k in kinds_searched],
            "results": [r.to_dict() for r in results],
        }
        return cls(
            query=query,
            kinds_searched=kinds_searched,
            results=results,
            response_id=f"UCOS-PSRS-{content_hash(core)[:16]}",
        )

    @property
    def kinds_present(self) -> frozenset[EntityKind]:
        """The distinct entity kinds actually represented in the results."""
        return frozenset(r.entity.kind for r in self.results)

    def to_dict(self) -> dict[str, Any]:
        return {
            "response_id": self.response_id,
            "query": self.query,
            "kinds_searched": [k.value for k in self.kinds_searched],
            "result_count": len(self.results),
            "results": [r.to_dict() for r in self.results],
        }

    def fingerprint(self) -> str:
        return content_hash(self.to_dict())


class SearchIndex:
    """A deterministic in-memory search index over platform entities."""

    __slots__ = ("_entities",)

    def __init__(self, entities: Iterable[SearchEntity] | None = None) -> None:
        self._entities: dict[str, SearchEntity] = {}
        if entities is not None:
            self.add_all(entities)

    def add(self, entity: SearchEntity) -> SearchEntity:
        """Add an entity (idempotent by content-addressed id)."""
        if not isinstance(entity, SearchEntity):
            raise PortalSearchError("index add requires a SearchEntity")
        self._entities[entity.entity_id] = entity
        return entity

    def add_all(self, entities: Iterable[SearchEntity]) -> None:
        for entity in entities:
            self.add(entity)

    def __len__(self) -> int:
        return len(self._entities)

    @property
    def kinds(self) -> frozenset[EntityKind]:
        """The distinct entity kinds present in the index."""
        return frozenset(e.kind for e in self._entities.values())

    def query(
        self,
        text: str,
        *,
        allowed_kinds: frozenset[EntityKind],
        tenant: str | None = None,
    ) -> tuple[SearchResult, ...]:
        """Return deterministically ranked hits within ``allowed_kinds``.

        Tenant isolation: a tenant-scoped entity is visible only to a caller in the
        same tenant; an unscoped caller (``tenant is None``) sees all. Ranking is by
        descending score, then title, then entity id (fully deterministic).
        """
        query_tokens = _tokens(text)
        if not query_tokens:
            return ()
        hits: list[SearchResult] = []
        for entity in self._entities.values():
            if entity.kind not in allowed_kinds:
                continue
            if not self._tenant_visible(entity.tenant, tenant):
                continue
            score = entity.score(query_tokens)
            if score > 0:
                hits.append(SearchResult(entity=entity, score=score))
        hits.sort(key=lambda r: (-r.score, r.entity.title, r.entity.entity_id))
        return tuple(hits)

    @staticmethod
    def _tenant_visible(entity_tenant: str | None, caller_tenant: str | None) -> bool:
        """Tenant isolation predicate (fail-closed for scoped callers)."""
        if entity_tenant is None:
            return True
        if caller_tenant is None:
            return True  # unscoped caller (e.g. administrator) sees all tenants
        return entity_tenant == caller_tenant

    def to_dict(self) -> dict[str, Any]:
        return {
            "entity_count": len(self._entities),
            "entities": [self._entities[eid].to_dict() for eid in sorted(self._entities)],
        }

    def fingerprint(self) -> str:
        return content_hash(self.to_dict())


class GlobalSearch:
    """The portal's authorization-scoped global search entry point (PC-13)."""

    __slots__ = ("_index", "_gateway")

    def __init__(self, index: SearchIndex, gateway: PortalAccessGateway) -> None:
        if not isinstance(index, SearchIndex):
            raise PortalSearchError("a valid SearchIndex is required")
        if not isinstance(gateway, PortalAccessGateway):
            raise PortalSearchError("a valid PortalAccessGateway is required")
        self._index = index
        self._gateway = gateway

    @property
    def index(self) -> SearchIndex:
        return self._index

    def authorized_kinds(
        self, session_id: str, *, now: int, tenant: str | None = None
    ) -> frozenset[EntityKind]:
        """The entity kinds this caller may see (READ on each kind's group)."""
        allowed: set[EntityKind] = set()
        for kind in all_entity_kinds():
            group = entity_kind_group(kind)
            if self._gateway.is_permitted(
                session_id, group, Permission.READ, now=now, tenant=tenant
            ):
                allowed.add(kind)
        return frozenset(allowed)

    def search(
        self, session_id: str, query: str, *, now: int, tenant: str | None = None
    ) -> SearchResponse:
        """Run an authorization-scoped global search (fail-closed by kind)."""
        if not isinstance(query, str):
            raise PortalSearchError("search query must be a string")
        allowed = self.authorized_kinds(session_id, now=now, tenant=tenant)
        kinds_searched = tuple(k for k in all_entity_kinds() if k in allowed)
        results = self._index.query(query, allowed_kinds=allowed, tenant=tenant)
        return SearchResponse.create(query, kinds_searched, results)


def default_search_index() -> SearchIndex:
    """A small deterministic demonstration index spanning all seven entity kinds.

    Used by the portal shell so global search is populated out of the box and the
    "≥4 entity types" acceptance criterion is demonstrable without external data.
    """
    return SearchIndex(
        [
            SearchEntity.create(
                EntityKind.WORKSPACE, "Platform Core Workspace", keywords=("core", "platform")
            ),
            SearchEntity.create(
                EntityKind.PROJECT, "Realization Engine Project", keywords=("engine", "realization")
            ),
            SearchEntity.create(
                EntityKind.BLUEPRINT, "Service Blueprint", keywords=("service", "blueprint")
            ),
            SearchEntity.create(
                EntityKind.GENERATION_REQUEST,
                "Nightly Generation Request",
                keywords=("generation", "nightly"),
            ),
            SearchEntity.create(
                EntityKind.ARTIFACT,
                "Signed Runtime Artifact",
                keywords=("artifact", "runtime", "signed"),
            ),
            SearchEntity.create(
                EntityKind.VALIDATION_REPORT,
                "Acceptance Validation Report",
                keywords=("validation", "acceptance"),
            ),
            SearchEntity.create(
                EntityKind.CERTIFICATION,
                "Program Certification Record",
                keywords=("certification", "program"),
            ),
        ]
    )


__all__ = [
    "SearchEntity",
    "SearchResult",
    "SearchResponse",
    "SearchIndex",
    "GlobalSearch",
    "default_search_index",
]
