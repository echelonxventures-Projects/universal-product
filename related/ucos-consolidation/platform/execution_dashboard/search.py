"""EC2-TASK-000131 — Execution Dashboard Search (EC2-EPIC-008).

The deterministic, authorization- and isolation-scoped **request navigation** entry point
for the dashboard (Program §2.2 PC-13, PC-08). It **surfaces the certified EPIC-007 search
contracts** — :class:`~platform.generation.search.RequestSearchResponse` and
:class:`~platform.generation.search.RequestHit` (re-used, never redefined) — but gates on
the dashboard's **own** capability group ``execution-dashboard`` rather than
``generation-requests``: a principal sees a request in results iff the Identity Layer
authorizes READ on ``execution-dashboard`` **and** the reused tenant isolation rule permits
it (P3). This is the decisive difference from EPIC-007's own search — an Operator (who holds
``execution-dashboard`` READ but *no* ``generation-requests`` grant, §3.2) can navigate the
dashboard, yet can never leak a cross-tenant request.

Matching is a pure, case-insensitive token function over slug, blueprint ref, family, and
status, and ranking is fully deterministic (score, then slug, then id) so identical queries
yield identical results (P5). The dashboard consumes the certified
:class:`~platform.generation.registry.GenerationRequestRegistry` **by reference**, read-only
— it re-implements no registry and mutates nothing.

This mirrors the certified :mod:`platform.generation.search` topology exactly.
"""

from __future__ import annotations

from platform.execution_dashboard.contracts import EXECUTION_DASHBOARD_GROUP
from platform.execution_dashboard.errors import DashboardSearchError
from platform.foundation.identity import Permission
from platform.generation.contracts import GenerationRequest, RequestStatus
from platform.generation.registry import GenerationRequestRegistry
from platform.generation.search import RequestHit, RequestSearchResponse
from platform.identity.errors import IdentityError
from platform.identity.service import AuthorizationService
from platform.workspace.isolation import tenants_isolated


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


class DashboardSearch:
    """The authorization- and isolation-scoped dashboard request search (fail-closed)."""

    __slots__ = ("_registry", "_authorization")

    def __init__(
        self, registry: GenerationRequestRegistry, authorization: AuthorizationService
    ) -> None:
        if not isinstance(registry, GenerationRequestRegistry):
            raise DashboardSearchError("a valid GenerationRequestRegistry is required")
        if not isinstance(authorization, AuthorizationService):
            raise DashboardSearchError("a valid AuthorizationService is required")
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
        status: RequestStatus | None = None,
    ) -> RequestSearchResponse:
        """Run an authorization- and isolation-scoped request search (fail-closed)."""
        if not isinstance(query, str):
            raise DashboardSearchError("search query must be a string")
        query_tokens = _tokens(query)

        principal = self._resolve_principal(session_id, now)
        if principal is None:
            return RequestSearchResponse.create(query, False, ())

        decision = self._authorization.authorize_principal(
            principal, EXECUTION_DASHBOARD_GROUP, Permission.READ, tenant=tenant
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


__all__ = ["DashboardSearch"]
