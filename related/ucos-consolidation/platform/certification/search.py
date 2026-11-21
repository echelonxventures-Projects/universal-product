"""EC2-TASK-000158 — Certification Console Search (EC2-EPIC-011).

The deterministic, authorization- and isolation-scoped **certification discovery** entry
point (Program §2.2 PC-13, PC-10). A caller sees a certification record in results only
when the Identity Layer authorizes READ on the ``certification-ledger`` group **and** the
reused tenant isolation rule permits it (P3) — so search can never leak a
cross-tenant/cross-workspace certification. Matching is a pure, case-insensitive token
function over target id, blueprint id, certification id, status, version, and labels, and
ranking is fully deterministic (score, then target, then id) so identical queries yield
identical results (P5). Results may be optionally scoped to a single target, blueprint,
certification, request, workspace, project, and/or certified outcome.

This mirrors the certified :mod:`platform.validation.search` topology exactly.
"""

from __future__ import annotations

from dataclasses import dataclass
from platform.certification.contracts import (
    CERTIFICATION_CONSOLE_GROUP,
    CertificationConsoleRecord,
)
from platform.certification.errors import CertificationSearchError
from platform.certification.registry import CertificationRegistry
from platform.foundation.contracts import content_hash
from platform.foundation.identity import Permission
from platform.identity.errors import IdentityError
from platform.identity.service import AuthorizationService
from platform.workspace.isolation import tenants_isolated
from typing import Any


def _tokens(text: str) -> tuple[str, ...]:
    return tuple(t for t in text.lower().split() if t)


def _score(record: CertificationConsoleRecord, query_tokens: tuple[str, ...]) -> int:
    haystack = (
        f"{record.target_id.lower()} {record.blueprint_id.lower()} "
        f"{record.certification_id.lower()} {record.record.status.value} "
        f"{record.version.lower()}"
    )
    labels = {label.lower() for label in record.metadata.labels}
    matched = 0
    for token in set(query_tokens):
        if token in haystack or any(token in label for label in labels):
            matched += 1
    return matched


@dataclass(frozen=True, slots=True)
class CertificationSearchResult:
    """An immutable ranked certification-record search hit."""

    record: CertificationConsoleRecord
    score: int

    def to_dict(self) -> dict[str, Any]:
        return {"record": self.record.to_dict(), "score": self.score}


@dataclass(frozen=True, slots=True)
class CertificationSearchResponse:
    """An immutable, content-addressed certification-record search response."""

    query: str
    authorized: bool
    results: tuple[CertificationSearchResult, ...]
    response_id: str = ""

    @classmethod
    def create(
        cls, query: str, authorized: bool, results: tuple[CertificationSearchResult, ...]
    ) -> CertificationSearchResponse:
        core = {
            "query": query,
            "authorized": authorized,
            "results": [r.to_dict() for r in results],
        }
        return cls(
            query=query,
            authorized=authorized,
            results=results,
            response_id=f"UCOS-CSRE-{content_hash(core)[:16]}",
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


class CertificationSearch:
    """The authorization- and isolation-scoped certification-record search (fail-closed)."""

    __slots__ = ("_registry", "_authorization")

    def __init__(
        self, registry: CertificationRegistry, authorization: AuthorizationService
    ) -> None:
        if not isinstance(registry, CertificationRegistry):
            raise CertificationSearchError("a valid CertificationRegistry is required")
        if not isinstance(authorization, AuthorizationService):
            raise CertificationSearchError("a valid AuthorizationService is required")
        self._registry = registry
        self._authorization = authorization

    def search(
        self,
        session_id: str,
        query: str,
        *,
        now: int,
        tenant: str | None = None,
        target_id: str | None = None,
        blueprint_id: str | None = None,
        certification_id: str | None = None,
        request_ref: str | None = None,
        workspace_id: str | None = None,
        project_id: str | None = None,
        certified: bool | None = None,
    ) -> CertificationSearchResponse:
        """Run an authorization- and isolation-scoped certification search (fail-closed)."""
        if not isinstance(query, str):
            raise CertificationSearchError("search query must be a string")
        query_tokens = _tokens(query)

        principal = self._resolve_principal(session_id, now)
        if principal is None:
            return CertificationSearchResponse.create(query, False, ())

        decision = self._authorization.authorize_principal(
            principal, CERTIFICATION_CONSOLE_GROUP, Permission.READ, tenant=tenant
        )
        if not decision.permitted:
            return CertificationSearchResponse.create(query, False, ())

        if not query_tokens:
            return CertificationSearchResponse.create(query, True, ())

        hits: list[CertificationSearchResult] = []
        for record in self._registry.discover(
            target_id=target_id,
            blueprint_id=blueprint_id,
            certification_id=certification_id,
            request_ref=request_ref,
            workspace_id=workspace_id,
            project_id=project_id,
            tenant=tenant,
            certified=certified,
        ):
            if tenants_isolated(principal.tenant, record.tenant):
                continue
            score = _score(record, query_tokens)
            if score > 0:
                hits.append(CertificationSearchResult(record=record, score=score))
        hits.sort(key=lambda h: (-h.score, h.record.target_id, h.record.record_id))
        return CertificationSearchResponse.create(query, True, tuple(hits))

    def _resolve_principal(self, session_id: str, now: int):
        """Validate the session and resolve its principal (fail-closed → None)."""
        try:
            session = self._authorization.sessions.validate(session_id, now)
            return self._authorization.principals.get(session.principal_id)
        except IdentityError:
            return None


__all__ = [
    "CertificationSearchResult",
    "CertificationSearchResponse",
    "CertificationSearch",
]
