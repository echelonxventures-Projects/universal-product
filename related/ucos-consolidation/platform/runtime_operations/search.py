"""EC2-TASK-000170 — Runtime Operations Search (EC2-EPIC-012).

The deterministic, authorization- and isolation-scoped **runtime-operation discovery**
entry point (Program §2.2 PC-13, PC-11). A caller sees an operation record in results only
when the Identity Layer authorizes READ on the ``runtime-operations`` group **and** the
reused tenant isolation rule permits it (P3) — so search can never leak a
cross-tenant/cross-workspace operation. Matching is a pure, case-insensitive token
function over runtime id, blueprint id, operation id, kind, environment, and labels, and
ranking is fully deterministic (score, then runtime, then id) so identical queries yield
identical results (P5). Results may be optionally scoped to a single runtime unit,
blueprint, certification, request, workspace, project, environment, and/or kind.

This mirrors the certified :mod:`platform.certification.search` topology exactly.
"""

from __future__ import annotations

from dataclasses import dataclass
from platform.foundation.contracts import content_hash
from platform.foundation.identity import Permission
from platform.identity.errors import IdentityError
from platform.identity.service import AuthorizationService
from platform.runtime_operations.contracts import (
    RUNTIME_OPERATIONS_GROUP,
    RuntimeOperationKind,
    RuntimeOperationRecord,
)
from platform.runtime_operations.errors import RuntimeOperationSearchError
from platform.runtime_operations.operations import RuntimeOperationRegistry
from platform.workspace.isolation import tenants_isolated
from typing import Any


def _tokens(text: str) -> tuple[str, ...]:
    return tuple(t for t in text.lower().split() if t)


def _score(record: RuntimeOperationRecord, query_tokens: tuple[str, ...]) -> int:
    haystack = (
        f"{record.runtime_id.lower()} {record.blueprint_id.lower()} "
        f"{record.operation_id.lower()} {record.kind.value} "
        f"{record.environment.lower()}"
    )
    labels = {label.lower() for label in record.metadata.labels}
    matched = 0
    for token in set(query_tokens):
        if token in haystack or any(token in label for label in labels):
            matched += 1
    return matched


@dataclass(frozen=True, slots=True)
class RuntimeOperationSearchResult:
    """An immutable ranked runtime-operation search hit."""

    record: RuntimeOperationRecord
    score: int

    def to_dict(self) -> dict[str, Any]:
        return {"record": self.record.to_dict(), "score": self.score}


@dataclass(frozen=True, slots=True)
class RuntimeOperationSearchResponse:
    """An immutable, content-addressed runtime-operation search response."""

    query: str
    authorized: bool
    results: tuple[RuntimeOperationSearchResult, ...]
    response_id: str = ""

    @classmethod
    def create(
        cls,
        query: str,
        authorized: bool,
        results: tuple[RuntimeOperationSearchResult, ...],
    ) -> RuntimeOperationSearchResponse:
        core = {
            "query": query,
            "authorized": authorized,
            "results": [r.to_dict() for r in results],
        }
        return cls(
            query=query,
            authorized=authorized,
            results=results,
            response_id=f"UCOS-ROSR-{content_hash(core)[:16]}",
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


class RuntimeOperationSearch:
    """The authorization- and isolation-scoped runtime-operation search (fail-closed)."""

    __slots__ = ("_registry", "_authorization")

    def __init__(
        self, registry: RuntimeOperationRegistry, authorization: AuthorizationService
    ) -> None:
        if not isinstance(registry, RuntimeOperationRegistry):
            raise RuntimeOperationSearchError("a valid RuntimeOperationRegistry is required")
        if not isinstance(authorization, AuthorizationService):
            raise RuntimeOperationSearchError("a valid AuthorizationService is required")
        self._registry = registry
        self._authorization = authorization

    def search(
        self,
        session_id: str,
        query: str,
        *,
        now: int,
        tenant: str | None = None,
        runtime_id: str | None = None,
        blueprint_id: str | None = None,
        certification_id: str | None = None,
        request_ref: str | None = None,
        workspace_id: str | None = None,
        project_id: str | None = None,
        environment: str | None = None,
        kind: RuntimeOperationKind | None = None,
    ) -> RuntimeOperationSearchResponse:
        """Run an authorization- and isolation-scoped runtime-operation search (fail-closed)."""
        if not isinstance(query, str):
            raise RuntimeOperationSearchError("search query must be a string")
        query_tokens = _tokens(query)

        principal = self._resolve_principal(session_id, now)
        if principal is None:
            return RuntimeOperationSearchResponse.create(query, False, ())

        decision = self._authorization.authorize_principal(
            principal, RUNTIME_OPERATIONS_GROUP, Permission.READ, tenant=tenant
        )
        if not decision.permitted:
            return RuntimeOperationSearchResponse.create(query, False, ())

        if not query_tokens:
            return RuntimeOperationSearchResponse.create(query, True, ())

        hits: list[RuntimeOperationSearchResult] = []
        for record in self._registry.discover(
            runtime_id=runtime_id,
            blueprint_id=blueprint_id,
            certification_id=certification_id,
            request_ref=request_ref,
            workspace_id=workspace_id,
            project_id=project_id,
            environment=environment,
            tenant=tenant,
            kind=kind,
        ):
            if tenants_isolated(principal.tenant, record.tenant):
                continue
            score = _score(record, query_tokens)
            if score > 0:
                hits.append(RuntimeOperationSearchResult(record=record, score=score))
        hits.sort(key=lambda h: (-h.score, h.record.runtime_id, h.record.operation_id))
        return RuntimeOperationSearchResponse.create(query, True, tuple(hits))

    def _resolve_principal(self, session_id: str, now: int):
        """Validate the session and resolve its principal (fail-closed → None)."""
        try:
            session = self._authorization.sessions.validate(session_id, now)
            return self._authorization.principals.get(session.principal_id)
        except IdentityError:
            return None


__all__ = [
    "RuntimeOperationSearchResult",
    "RuntimeOperationSearchResponse",
    "RuntimeOperationSearch",
]
