"""EC2-TASK-000087 — Workspace Search (EC2-EPIC-004).

The deterministic, authorization- and isolation-scoped **workspace discovery** entry
point. A caller sees a workspace in results only when the Identity Layer authorizes
READ on the ``workspace-project-lifecycle`` group **and** the tenant/workspace
isolation guard permits it (P3) — so search can never leak a cross-tenant workspace.
Matching is a pure, case-insensitive token function over slug, name, and labels, and
ranking is fully deterministic (score, then slug, then id) so identical queries yield
identical results (P5).
"""

from __future__ import annotations

from dataclasses import dataclass
from platform.foundation.contracts import content_hash
from platform.foundation.identity import Permission
from platform.identity.errors import IdentityError
from platform.identity.service import AuthorizationService
from platform.workspace.contracts import WORKSPACE_GROUP, Workspace
from platform.workspace.errors import WorkspaceSearchError
from platform.workspace.isolation import IsolationGuard
from platform.workspace.registration import WorkspaceRegistry
from typing import Any


def _tokens(text: str) -> tuple[str, ...]:
    return tuple(t for t in text.lower().split() if t)


def _score(workspace: Workspace, query_tokens: tuple[str, ...]) -> int:
    haystack = f"{workspace.slug} {workspace.name.lower()}"
    labels = {label.lower() for label in workspace.metadata.labels}
    matched = 0
    for token in set(query_tokens):
        if token in haystack or any(token in label for label in labels):
            matched += 1
    return matched


@dataclass(frozen=True, slots=True)
class WorkspaceHit:
    """An immutable ranked workspace search hit."""

    workspace: Workspace
    score: int

    def to_dict(self) -> dict[str, Any]:
        return {"workspace": self.workspace.to_dict(), "score": self.score}


@dataclass(frozen=True, slots=True)
class WorkspaceSearchResponse:
    """An immutable, content-addressed workspace search response."""

    query: str
    authorized: bool
    results: tuple[WorkspaceHit, ...]
    response_id: str = ""

    @classmethod
    def create(
        cls, query: str, authorized: bool, results: tuple[WorkspaceHit, ...]
    ) -> WorkspaceSearchResponse:
        core = {
            "query": query,
            "authorized": authorized,
            "results": [r.to_dict() for r in results],
        }
        return cls(
            query=query,
            authorized=authorized,
            results=results,
            response_id=f"UCOS-WSRS-{content_hash(core)[:16]}",
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


class WorkspaceSearch:
    """The authorization- and isolation-scoped workspace search (fail-closed)."""

    __slots__ = ("_registry", "_authorization", "_isolation")

    def __init__(
        self,
        registry: WorkspaceRegistry,
        authorization: AuthorizationService,
        *,
        isolation: IsolationGuard | None = None,
    ) -> None:
        if not isinstance(registry, WorkspaceRegistry):
            raise WorkspaceSearchError("a valid WorkspaceRegistry is required")
        if not isinstance(authorization, AuthorizationService):
            raise WorkspaceSearchError("a valid AuthorizationService is required")
        self._registry = registry
        self._authorization = authorization
        self._isolation = isolation if isolation is not None else IsolationGuard()

    def search(
        self, session_id: str, query: str, *, now: int, tenant: str | None = None
    ) -> WorkspaceSearchResponse:
        """Run an authorization- and isolation-scoped workspace search (fail-closed)."""
        if not isinstance(query, str):
            raise WorkspaceSearchError("search query must be a string")
        query_tokens = _tokens(query)

        principal = self._resolve_principal(session_id, now)
        if principal is None:
            return WorkspaceSearchResponse.create(query, False, ())

        decision = self._authorization.authorize_principal(
            principal, WORKSPACE_GROUP, Permission.READ, tenant=tenant
        )
        if not decision.permitted:
            return WorkspaceSearchResponse.create(query, False, ())

        if not query_tokens:
            return WorkspaceSearchResponse.create(query, True, ())

        hits: list[WorkspaceHit] = []
        for workspace in self._registry.discover(tenant):
            if not self._isolation.permits(principal, workspace):
                continue
            score = _score(workspace, query_tokens)
            if score > 0:
                hits.append(WorkspaceHit(workspace=workspace, score=score))
        hits.sort(key=lambda h: (-h.score, h.workspace.slug, h.workspace.workspace_id))
        return WorkspaceSearchResponse.create(query, True, tuple(hits))

    def _resolve_principal(self, session_id: str, now: int):
        """Validate the session and resolve its principal (fail-closed → None)."""
        try:
            session = self._authorization.sessions.validate(session_id, now)
            return self._authorization.principals.get(session.principal_id)
        except IdentityError:
            return None


__all__ = ["WorkspaceHit", "WorkspaceSearchResponse", "WorkspaceSearch"]
