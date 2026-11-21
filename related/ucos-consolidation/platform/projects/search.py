"""EC2-TASK-000094 — Project Search (EC2-EPIC-005).

The deterministic, authorization- and isolation-scoped **project discovery** entry
point (Program §2.2 PC-13). A caller sees a project in results only when the Identity
Layer authorizes READ on the ``workspace-project-lifecycle`` group **and** the reused
tenant/workspace isolation rule permits it (P3) — so search can never leak a
cross-tenant/cross-workspace project. Matching is a pure, case-insensitive token
function over slug, name, and labels, and ranking is fully deterministic (score, then
slug, then id) so identical queries yield identical results (P5). Results may be
optionally scoped to a single parent workspace.
"""

from __future__ import annotations

from dataclasses import dataclass
from platform.foundation.contracts import content_hash
from platform.foundation.identity import Permission
from platform.identity.errors import IdentityError
from platform.identity.service import AuthorizationService
from platform.projects.contracts import PROJECT_GROUP, Project
from platform.projects.errors import ProjectSearchError
from platform.projects.registry import ProjectRegistry
from platform.workspace.isolation import tenants_isolated
from typing import Any


def _tokens(text: str) -> tuple[str, ...]:
    return tuple(t for t in text.lower().split() if t)


def _score(project: Project, query_tokens: tuple[str, ...]) -> int:
    haystack = f"{project.slug} {project.name.lower()}"
    labels = {label.lower() for label in project.metadata.labels}
    matched = 0
    for token in set(query_tokens):
        if token in haystack or any(token in label for label in labels):
            matched += 1
    return matched


@dataclass(frozen=True, slots=True)
class ProjectHit:
    """An immutable ranked project search hit."""

    project: Project
    score: int

    def to_dict(self) -> dict[str, Any]:
        return {"project": self.project.to_dict(), "score": self.score}


@dataclass(frozen=True, slots=True)
class ProjectSearchResponse:
    """An immutable, content-addressed project search response."""

    query: str
    authorized: bool
    results: tuple[ProjectHit, ...]
    response_id: str = ""

    @classmethod
    def create(
        cls, query: str, authorized: bool, results: tuple[ProjectHit, ...]
    ) -> ProjectSearchResponse:
        core = {
            "query": query,
            "authorized": authorized,
            "results": [r.to_dict() for r in results],
        }
        return cls(
            query=query,
            authorized=authorized,
            results=results,
            response_id=f"UCOS-PSRE-{content_hash(core)[:16]}",
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


class ProjectSearch:
    """The authorization- and isolation-scoped project search (fail-closed)."""

    __slots__ = ("_registry", "_authorization")

    def __init__(self, registry: ProjectRegistry, authorization: AuthorizationService) -> None:
        if not isinstance(registry, ProjectRegistry):
            raise ProjectSearchError("a valid ProjectRegistry is required")
        if not isinstance(authorization, AuthorizationService):
            raise ProjectSearchError("a valid AuthorizationService is required")
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
    ) -> ProjectSearchResponse:
        """Run an authorization- and isolation-scoped project search (fail-closed)."""
        if not isinstance(query, str):
            raise ProjectSearchError("search query must be a string")
        query_tokens = _tokens(query)

        principal = self._resolve_principal(session_id, now)
        if principal is None:
            return ProjectSearchResponse.create(query, False, ())

        decision = self._authorization.authorize_principal(
            principal, PROJECT_GROUP, Permission.READ, tenant=tenant
        )
        if not decision.permitted:
            return ProjectSearchResponse.create(query, False, ())

        if not query_tokens:
            return ProjectSearchResponse.create(query, True, ())

        hits: list[ProjectHit] = []
        for project in self._registry.discover(workspace_id=workspace_id, tenant=tenant):
            if tenants_isolated(principal.tenant, project.tenant):
                continue
            score = _score(project, query_tokens)
            if score > 0:
                hits.append(ProjectHit(project=project, score=score))
        hits.sort(key=lambda h: (-h.score, h.project.slug, h.project.project_id))
        return ProjectSearchResponse.create(query, True, tuple(hits))

    def _resolve_principal(self, session_id: str, now: int):
        """Validate the session and resolve its principal (fail-closed → None)."""
        try:
            session = self._authorization.sessions.validate(session_id, now)
            return self._authorization.principals.get(session.principal_id)
        except IdentityError:
            return None


__all__ = ["ProjectHit", "ProjectSearchResponse", "ProjectSearch"]
