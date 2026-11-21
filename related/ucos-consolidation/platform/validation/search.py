"""EC2-TASK-000149 — Validation Console Search (EC2-EPIC-010).

The deterministic, authorization- and isolation-scoped **validation discovery** entry
point (Program §2.2 PC-13, PC-09). A caller sees a validation record in results only when
the Identity Layer authorizes READ on the ``validation-explorer`` group **and** the
reused tenant isolation rule permits it (P3) — so search can never leak a
cross-tenant/cross-workspace validation. Matching is a pure, case-insensitive token
function over target id, blueprint id, verdict, and labels, and ranking is fully
deterministic (score, then target, then id) so identical queries yield identical results
(P5). Results may be optionally scoped to a single target, blueprint, request, workspace,
project, and/or acceptance outcome.

This mirrors the certified :mod:`platform.generation.search` topology exactly.
"""

from __future__ import annotations

from dataclasses import dataclass
from platform.foundation.contracts import content_hash
from platform.foundation.identity import Permission
from platform.identity.errors import IdentityError
from platform.identity.service import AuthorizationService
from platform.validation.contracts import VALIDATION_CONSOLE_GROUP, ValidationRecord
from platform.validation.errors import ValidationSearchError
from platform.validation.registry import ValidationRecordRegistry
from platform.workspace.isolation import tenants_isolated
from typing import Any


def _tokens(text: str) -> tuple[str, ...]:
    return tuple(t for t in text.lower().split() if t)


def _score(record: ValidationRecord, query_tokens: tuple[str, ...]) -> int:
    haystack = (
        f"{record.target_id.lower()} {record.blueprint_id.lower()} {record.report.verdict.value}"
    )
    labels = {label.lower() for label in record.metadata.labels}
    matched = 0
    for token in set(query_tokens):
        if token in haystack or any(token in label for label in labels):
            matched += 1
    return matched


@dataclass(frozen=True, slots=True)
class ValidationSearchResult:
    """An immutable ranked validation-record search hit."""

    record: ValidationRecord
    score: int

    def to_dict(self) -> dict[str, Any]:
        return {"record": self.record.to_dict(), "score": self.score}


@dataclass(frozen=True, slots=True)
class ValidationSearchResponse:
    """An immutable, content-addressed validation-record search response."""

    query: str
    authorized: bool
    results: tuple[ValidationSearchResult, ...]
    response_id: str = ""

    @classmethod
    def create(
        cls, query: str, authorized: bool, results: tuple[ValidationSearchResult, ...]
    ) -> ValidationSearchResponse:
        core = {
            "query": query,
            "authorized": authorized,
            "results": [r.to_dict() for r in results],
        }
        return cls(
            query=query,
            authorized=authorized,
            results=results,
            response_id=f"UCOS-VSRE-{content_hash(core)[:16]}",
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


class ValidationSearch:
    """The authorization- and isolation-scoped validation-record search (fail-closed)."""

    __slots__ = ("_registry", "_authorization")

    def __init__(
        self, registry: ValidationRecordRegistry, authorization: AuthorizationService
    ) -> None:
        if not isinstance(registry, ValidationRecordRegistry):
            raise ValidationSearchError("a valid ValidationRecordRegistry is required")
        if not isinstance(authorization, AuthorizationService):
            raise ValidationSearchError("a valid AuthorizationService is required")
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
        request_ref: str | None = None,
        workspace_id: str | None = None,
        project_id: str | None = None,
        accepted: bool | None = None,
    ) -> ValidationSearchResponse:
        """Run an authorization- and isolation-scoped validation search (fail-closed)."""
        if not isinstance(query, str):
            raise ValidationSearchError("search query must be a string")
        query_tokens = _tokens(query)

        principal = self._resolve_principal(session_id, now)
        if principal is None:
            return ValidationSearchResponse.create(query, False, ())

        decision = self._authorization.authorize_principal(
            principal, VALIDATION_CONSOLE_GROUP, Permission.READ, tenant=tenant
        )
        if not decision.permitted:
            return ValidationSearchResponse.create(query, False, ())

        if not query_tokens:
            return ValidationSearchResponse.create(query, True, ())

        hits: list[ValidationSearchResult] = []
        for record in self._registry.discover(
            target_id=target_id,
            blueprint_id=blueprint_id,
            request_ref=request_ref,
            workspace_id=workspace_id,
            project_id=project_id,
            tenant=tenant,
            accepted=accepted,
        ):
            if tenants_isolated(principal.tenant, record.tenant):
                continue
            score = _score(record, query_tokens)
            if score > 0:
                hits.append(ValidationSearchResult(record=record, score=score))
        hits.sort(key=lambda h: (-h.score, h.record.target_id, h.record.record_id))
        return ValidationSearchResponse.create(query, True, tuple(hits))

    def _resolve_principal(self, session_id: str, now: int):
        """Validate the session and resolve its principal (fail-closed → None)."""
        try:
            session = self._authorization.sessions.validate(session_id, now)
            return self._authorization.principals.get(session.principal_id)
        except IdentityError:
            return None


__all__ = ["ValidationSearchResult", "ValidationSearchResponse", "ValidationSearch"]
