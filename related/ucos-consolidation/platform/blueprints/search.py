"""EC2-TASK-000105 — Blueprint Search (EC2-EPIC-006).

The deterministic, authorization- and isolation-scoped **blueprint discovery** entry
point (Program §2.2 PC-13, PC-05). A caller sees a blueprint in results only when the
Identity Layer authorizes READ on the ``blueprint-catalog`` group **and** the reused
tenant/workspace isolation rule permits it (P3) — so search can never leak a
cross-tenant/cross-workspace blueprint. Matching is a pure, case-insensitive token
function over slug, name, family, and labels, and ranking is fully deterministic
(score, then slug, then id) so identical queries yield identical results (P5). Results
may be optionally scoped to a single parent workspace and/or generation family.

This mirrors the certified :mod:`platform.projects.search` topology exactly.
"""

from __future__ import annotations

from dataclasses import dataclass
from platform.blueprints.contracts import BLUEPRINT_CATALOG_GROUP, Blueprint, BlueprintFamily
from platform.blueprints.errors import BlueprintSearchError
from platform.blueprints.registry import BlueprintRegistry
from platform.foundation.contracts import content_hash
from platform.foundation.identity import Permission
from platform.identity.errors import IdentityError
from platform.identity.service import AuthorizationService
from platform.workspace.isolation import tenants_isolated
from typing import Any


def _tokens(text: str) -> tuple[str, ...]:
    return tuple(t for t in text.lower().split() if t)


def _score(blueprint: Blueprint, query_tokens: tuple[str, ...]) -> int:
    haystack = f"{blueprint.slug} {blueprint.name.lower()} {blueprint.family.value}"
    labels = {label.lower() for label in blueprint.metadata.labels}
    matched = 0
    for token in set(query_tokens):
        if token in haystack or any(token in label for label in labels):
            matched += 1
    return matched


@dataclass(frozen=True, slots=True)
class BlueprintHit:
    """An immutable ranked blueprint search hit."""

    blueprint: Blueprint
    score: int

    def to_dict(self) -> dict[str, Any]:
        return {"blueprint": self.blueprint.to_dict(), "score": self.score}


@dataclass(frozen=True, slots=True)
class BlueprintSearchResponse:
    """An immutable, content-addressed blueprint search response."""

    query: str
    authorized: bool
    results: tuple[BlueprintHit, ...]
    response_id: str = ""

    @classmethod
    def create(
        cls, query: str, authorized: bool, results: tuple[BlueprintHit, ...]
    ) -> BlueprintSearchResponse:
        core = {
            "query": query,
            "authorized": authorized,
            "results": [r.to_dict() for r in results],
        }
        return cls(
            query=query,
            authorized=authorized,
            results=results,
            response_id=f"UCOS-BSRE-{content_hash(core)[:16]}",
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "response_id": self.response_id,
            "query": self.query,
            "authorized": self.authorized,
            "result_count": len(self.results),
            "results": [r.to_dict() for r in self.results],
        }

    def fingerprint(self) -> str:
        return content_hash(self.to_dict())


class BlueprintSearch:
    """The authorization- and isolation-scoped blueprint search (fail-closed)."""

    __slots__ = ("_registry", "_authorization")

    def __init__(self, registry: BlueprintRegistry, authorization: AuthorizationService) -> None:
        if not isinstance(registry, BlueprintRegistry):
            raise BlueprintSearchError("a valid BlueprintRegistry is required")
        if not isinstance(authorization, AuthorizationService):
            raise BlueprintSearchError("a valid AuthorizationService is required")
        self._registry = registry
        self._authorization = authorization

    def search(
        self,
        session_id: str,
        query: str,
        *,
        now: int,
        tenant: str | None = None,
        workspace_id: str | None = None,
        family: BlueprintFamily | None = None,
    ) -> BlueprintSearchResponse:
        """Run an authorization- and isolation-scoped blueprint search (fail-closed)."""
        if not isinstance(query, str):
            raise BlueprintSearchError("search query must be a string")
        query_tokens = _tokens(query)

        principal = self._resolve_principal(session_id, now)
        if principal is None:
            return BlueprintSearchResponse.create(query, False, ())

        decision = self._authorization.authorize_principal(
            principal, BLUEPRINT_CATALOG_GROUP, Permission.READ, tenant=tenant
        )
        if not decision.permitted:
            return BlueprintSearchResponse.create(query, False, ())

        if not query_tokens:
            return BlueprintSearchResponse.create(query, True, ())

        hits: list[BlueprintHit] = []
        for blueprint in self._registry.discover(
            workspace_id=workspace_id, tenant=tenant, family=family
        ):
            if tenants_isolated(principal.tenant, blueprint.tenant):
                continue
            score = _score(blueprint, query_tokens)
            if score > 0:
                hits.append(BlueprintHit(blueprint=blueprint, score=score))
        hits.sort(key=lambda h: (-h.score, h.blueprint.slug, h.blueprint.blueprint_id))
        return BlueprintSearchResponse.create(query, True, tuple(hits))

    def _resolve_principal(self, session_id: str, now: int):
        """Validate the session and resolve its principal (fail-closed → None)."""
        try:
            session = self._authorization.sessions.validate(session_id, now)
            return self._authorization.principals.get(session.principal_id)
        except IdentityError:
            return None


__all__ = ["BlueprintHit", "BlueprintSearchResponse", "BlueprintSearch"]
