"""EC2-TASK-000115 — Generation Request Search (EC2-EPIC-007).

The deterministic, authorization- and isolation-scoped **request discovery** entry
point (Program §2.2 PC-13, PC-06). A caller sees a request in results only when the
Identity Layer authorizes READ on the ``generation-requests`` group **and** the reused
tenant/workspace isolation rule permits it (P3) — so search can never leak a
cross-tenant/cross-workspace request. Matching is a pure, case-insensitive token
function over slug, blueprint ref, family, status, and labels, and ranking is fully
deterministic (score, then slug, then id) so identical queries yield identical results
(P5). Results may be optionally scoped to a single parent workspace, project, generation
family, and/or lifecycle status.

This mirrors the certified :mod:`platform.blueprints.search` topology exactly.
"""

from __future__ import annotations

from dataclasses import dataclass
from platform.blueprints.contracts import BlueprintFamily
from platform.foundation.contracts import content_hash
from platform.foundation.identity import Permission
from platform.generation.contracts import (
    GENERATION_REQUEST_GROUP,
    GenerationRequest,
    RequestStatus,
)
from platform.generation.errors import RequestSearchError
from platform.generation.registry import GenerationRequestRegistry
from platform.identity.errors import IdentityError
from platform.identity.service import AuthorizationService
from platform.workspace.isolation import tenants_isolated
from typing import Any


def _tokens(text: str) -> tuple[str, ...]:
    return tuple(t for t in text.lower().split() if t)


def _score(request: GenerationRequest, query_tokens: tuple[str, ...]) -> int:
    haystack = (
        f"{request.slug} {request.blueprint_ref.lower()} "
        f"{request.family.value} {request.status.value}"
    )
    labels = {label.lower() for label in request.metadata.labels}
    matched = 0
    for token in set(query_tokens):
        if token in haystack or any(token in label for label in labels):
            matched += 1
    return matched


@dataclass(frozen=True, slots=True)
class RequestHit:
    """An immutable ranked generation-request search hit."""

    request: GenerationRequest
    score: int

    def to_dict(self) -> dict[str, Any]:
        return {"request": self.request.to_dict(), "score": self.score}


@dataclass(frozen=True, slots=True)
class RequestSearchResponse:
    """An immutable, content-addressed generation-request search response."""

    query: str
    authorized: bool
    results: tuple[RequestHit, ...]
    response_id: str = ""

    @classmethod
    def create(
        cls, query: str, authorized: bool, results: tuple[RequestHit, ...]
    ) -> RequestSearchResponse:
        core = {
            "query": query,
            "authorized": authorized,
            "results": [r.to_dict() for r in results],
        }
        return cls(
            query=query,
            authorized=authorized,
            results=results,
            response_id=f"UCOS-GSRE-{content_hash(core)[:16]}",
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


class RequestSearch:
    """The authorization- and isolation-scoped generation-request search (fail-closed)."""

    __slots__ = ("_registry", "_authorization")

    def __init__(
        self, registry: GenerationRequestRegistry, authorization: AuthorizationService
    ) -> None:
        if not isinstance(registry, GenerationRequestRegistry):
            raise RequestSearchError("a valid GenerationRequestRegistry is required")
        if not isinstance(authorization, AuthorizationService):
            raise RequestSearchError("a valid AuthorizationService is required")
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
        project_id: str | None = None,
        family: BlueprintFamily | None = None,
        status: RequestStatus | None = None,
    ) -> RequestSearchResponse:
        """Run an authorization- and isolation-scoped request search (fail-closed)."""
        if not isinstance(query, str):
            raise RequestSearchError("search query must be a string")
        query_tokens = _tokens(query)

        principal = self._resolve_principal(session_id, now)
        if principal is None:
            return RequestSearchResponse.create(query, False, ())

        decision = self._authorization.authorize_principal(
            principal, GENERATION_REQUEST_GROUP, Permission.READ, tenant=tenant
        )
        if not decision.permitted:
            return RequestSearchResponse.create(query, False, ())

        if not query_tokens:
            return RequestSearchResponse.create(query, True, ())

        hits: list[RequestHit] = []
        for request in self._registry.discover(
            workspace_id=workspace_id,
            project_id=project_id,
            tenant=tenant,
            family=family,
            status=status,
        ):
            if tenants_isolated(principal.tenant, request.tenant):
                continue
            score = _score(request, query_tokens)
            if score > 0:
                hits.append(RequestHit(request=request, score=score))
        hits.sort(key=lambda h: (-h.score, h.request.slug, h.request.request_id))
        return RequestSearchResponse.create(query, True, tuple(hits))

    def _resolve_principal(self, session_id: str, now: int):
        """Validate the session and resolve its principal (fail-closed → None)."""
        try:
            session = self._authorization.sessions.validate(session_id, now)
            return self._authorization.principals.get(session.principal_id)
        except IdentityError:
            return None


__all__ = ["RequestHit", "RequestSearchResponse", "RequestSearch"]
