"""EC2-TASK-000130 — Artifact Explorer Search (EC2-EPIC-009).

The deterministic, authorization- and isolation-scoped **artifact discovery** entry
point (Program §2.2 PC-13, PC-08). A caller sees an artifact in results only when the
Identity Layer authorizes READ on the ``artifact-explorer`` group **and** the reused
tenant/workspace isolation rule permits it (P3) — so search can never leak a
cross-tenant/cross-workspace artifact. Matching is a pure, case-insensitive token
function over slug, blueprint ref, family, lifecycle status, and labels, and ranking is
fully deterministic (score, then slug, then request id) so identical queries yield
identical results (P5). Results may be optionally scoped to a single workspace, project,
generation family, and/or lifecycle status.

This mirrors the certified :mod:`platform.generation.search` topology exactly. It also
**consumes** the EC2-EPIC-007 :class:`~platform.generation.search.RequestSearchResponse`
(of :class:`~platform.generation.search.RequestHit`) — the explorer can project an
already-authorized generation-request search response into artifact search results by
reference (:meth:`ArtifactSearchResponse.from_request_search_response`).
"""

from __future__ import annotations

from dataclasses import dataclass
from platform.artifact_explorer.errors import ArtifactSearchError
from platform.artifact_explorer.references import ArtifactSummary
from platform.blueprints.contracts import BlueprintFamily
from platform.foundation.contracts import content_hash
from platform.foundation.identity import Permission
from platform.generation.contracts import GenerationRequest, RequestStatus
from platform.generation.dispatch import DispatchLedger
from platform.generation.provenance import ProvenanceLedger
from platform.generation.registry import GenerationRequestRegistry
from platform.generation.search import RequestSearchResponse
from platform.identity.contracts import CapabilityGroup
from platform.identity.errors import IdentityError
from platform.identity.service import AuthorizationService
from platform.workspace.isolation import tenants_isolated
from typing import Any

#: The §3.2 capability group authorizing artifact-explorer search (reused; no new group).
ARTIFACT_EXPLORER_GROUP = CapabilityGroup.ARTIFACT_EXPLORER


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
class ArtifactSearchResult:
    """An immutable ranked artifact search hit (a summary projection + score)."""

    summary: ArtifactSummary
    score: int

    def to_dict(self) -> dict[str, Any]:
        return {"summary": self.summary.to_dict(), "score": self.score}


@dataclass(frozen=True, slots=True)
class ArtifactSearchResponse:
    """An immutable, content-addressed artifact search response."""

    query: str
    authorized: bool
    results: tuple[ArtifactSearchResult, ...]
    response_id: str = ""

    @classmethod
    def create(
        cls, query: str, authorized: bool, results: tuple[ArtifactSearchResult, ...]
    ) -> ArtifactSearchResponse:
        core = {
            "query": query,
            "authorized": authorized,
            "results": [r.to_dict() for r in results],
        }
        return cls(
            query=query,
            authorized=authorized,
            results=results,
            response_id=f"UCOS-AXSR-{content_hash(core)[:16]}",
        )

    @classmethod
    def from_request_search_response(
        cls,
        response: RequestSearchResponse,
        *,
        dispatch: DispatchLedger,
        provenance: ProvenanceLedger,
    ) -> ArtifactSearchResponse:
        """Project an EC2-EPIC-007 request-search response into artifact results (by reference).

        Consumes the already-authorized, isolation-scoped
        :class:`RequestSearchResponse` (of :class:`RequestHit`) and maps each hit to an
        :class:`ArtifactSummary`, carrying the dispatch/provenance presence flags from the
        supplied ledgers. Re-derives nothing and re-authorizes nothing — it is a faithful
        projection of an existing response.
        """
        if not isinstance(response, RequestSearchResponse):
            raise ArtifactSearchError(
                "from_request_search_response requires a RequestSearchResponse"
            )
        if not isinstance(dispatch, DispatchLedger):
            raise ArtifactSearchError("a valid DispatchLedger is required")
        if not isinstance(provenance, ProvenanceLedger):
            raise ArtifactSearchError("a valid ProvenanceLedger is required")
        results = tuple(
            ArtifactSearchResult(
                summary=ArtifactSummary.from_request(
                    hit.request,
                    has_dispatch=dispatch.has(hit.request.request_id),
                    has_provenance=provenance.has(hit.request.request_id),
                ),
                score=hit.score,
            )
            for hit in response.results
        )
        return cls.create(response.query, response.authorized, results)

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


class ArtifactSearch:
    """The authorization- and isolation-scoped artifact search (fail-closed, read-only)."""

    __slots__ = ("_registry", "_dispatch", "_provenance", "_authorization")

    def __init__(
        self,
        registry: GenerationRequestRegistry,
        dispatch: DispatchLedger,
        provenance: ProvenanceLedger,
        authorization: AuthorizationService,
    ) -> None:
        if not isinstance(registry, GenerationRequestRegistry):
            raise ArtifactSearchError("a valid GenerationRequestRegistry is required")
        if not isinstance(dispatch, DispatchLedger):
            raise ArtifactSearchError("a valid DispatchLedger is required")
        if not isinstance(provenance, ProvenanceLedger):
            raise ArtifactSearchError("a valid ProvenanceLedger is required")
        if not isinstance(authorization, AuthorizationService):
            raise ArtifactSearchError("a valid AuthorizationService is required")
        self._registry = registry
        self._dispatch = dispatch
        self._provenance = provenance
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
    ) -> ArtifactSearchResponse:
        """Run an authorization- and isolation-scoped artifact search (fail-closed)."""
        if not isinstance(query, str):
            raise ArtifactSearchError("search query must be a string")
        query_tokens = _tokens(query)

        principal = self._resolve_principal(session_id, now)
        if principal is None:
            return ArtifactSearchResponse.create(query, False, ())

        decision = self._authorization.authorize_principal(
            principal, ARTIFACT_EXPLORER_GROUP, Permission.READ, tenant=tenant
        )
        if not decision.permitted:
            return ArtifactSearchResponse.create(query, False, ())

        if not query_tokens:
            return ArtifactSearchResponse.create(query, True, ())

        hits: list[ArtifactSearchResult] = []
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
                summary = ArtifactSummary.from_request(
                    request,
                    has_dispatch=self._dispatch.has(request.request_id),
                    has_provenance=self._provenance.has(request.request_id),
                )
                hits.append(ArtifactSearchResult(summary=summary, score=score))
        hits.sort(key=lambda h: (-h.score, h.summary.slug, h.summary.request_ref))
        return ArtifactSearchResponse.create(query, True, tuple(hits))

    def _resolve_principal(self, session_id: str, now: int):
        """Validate the session and resolve its principal (fail-closed → None)."""
        try:
            session = self._authorization.sessions.validate(session_id, now)
            return self._authorization.principals.get(session.principal_id)
        except IdentityError:
            return None


__all__ = ["ArtifactSearchResult", "ArtifactSearchResponse", "ArtifactSearch"]
