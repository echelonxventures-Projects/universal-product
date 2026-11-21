"""EC2-CAP-ADMIN-001 — Administrative Search (Administration Runtime).

The deterministic, authorization-scoped **administrative discovery** entry point. A
caller sees administrative subjects — operational settings and administrator
assignments — only when the Identity Layer authorizes READ on the
``administration-policy`` group (the ``INSPECT`` action). Search never invents
visibility: an unauthenticated or unauthorized caller receives an empty, unauthorized
response (fail-closed). Matching is a pure, case-insensitive token function over the
subject's stable fields, and ranking is fully deterministic (kind, then score, then
identifier) so identical queries yield identical results (P5).
"""

from __future__ import annotations

from dataclasses import dataclass
from platform.administration.configuration import AdministrativeConfiguration
from platform.administration.contracts import ADMINISTRATION_GROUP
from platform.administration.errors import AdministrationSearchError
from platform.administration.membership import AdministrativeMembershipRegistry
from platform.foundation.contracts import content_hash
from platform.foundation.identity import Permission
from platform.identity.errors import IdentityError
from platform.identity.service import AuthorizationService
from typing import Any


def _tokens(text: str) -> tuple[str, ...]:
    return tuple(t for t in text.lower().split() if t)


def _score(haystack: str, query_tokens: tuple[str, ...]) -> int:
    matched = 0
    for token in set(query_tokens):
        if token in haystack:
            matched += 1
    return matched


@dataclass(frozen=True, slots=True)
class AdministrativeHit:
    """An immutable ranked administrative search hit."""

    kind: str
    identifier: str
    score: int
    detail: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return {
            "kind": self.kind,
            "identifier": self.identifier,
            "score": self.score,
            "detail": self.detail,
        }


@dataclass(frozen=True, slots=True)
class AdministrativeSearchResponse:
    """An immutable, content-addressed administrative search response."""

    query: str
    authorized: bool
    results: tuple[AdministrativeHit, ...]
    response_id: str = ""

    @classmethod
    def create(
        cls, query: str, authorized: bool, results: tuple[AdministrativeHit, ...]
    ) -> AdministrativeSearchResponse:
        core = {
            "query": query,
            "authorized": authorized,
            "results": [r.to_dict() for r in results],
        }
        return cls(
            query=query,
            authorized=authorized,
            results=results,
            response_id=f"UCOS-ASRS-{content_hash(core)[:16]}",
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


class AdministrativeSearch:
    """The authorization-scoped administrative search (fail-closed)."""

    __slots__ = ("_configuration", "_membership", "_authorization")

    def __init__(
        self,
        configuration: AdministrativeConfiguration,
        membership: AdministrativeMembershipRegistry,
        authorization: AuthorizationService,
    ) -> None:
        if not isinstance(configuration, AdministrativeConfiguration):
            raise AdministrationSearchError("a valid AdministrativeConfiguration is required")
        if not isinstance(membership, AdministrativeMembershipRegistry):
            raise AdministrationSearchError("a valid AdministrativeMembershipRegistry is required")
        if not isinstance(authorization, AuthorizationService):
            raise AdministrationSearchError("a valid AuthorizationService is required")
        self._configuration = configuration
        self._membership = membership
        self._authorization = authorization

    def search(
        self, session_id: str, query: str, *, now: int, tenant: str | None = None
    ) -> AdministrativeSearchResponse:
        """Run an authorization-scoped administrative search (fail-closed)."""
        if not isinstance(query, str):
            raise AdministrationSearchError("search query must be a string")
        query_tokens = _tokens(query)

        principal = self._resolve_principal(session_id, now)
        if principal is None:
            return AdministrativeSearchResponse.create(query, False, ())

        decision = self._authorization.authorize_principal(
            principal, ADMINISTRATION_GROUP, Permission.READ, tenant=tenant
        )
        if not decision.permitted:
            return AdministrativeSearchResponse.create(query, False, ())

        if not query_tokens:
            return AdministrativeSearchResponse.create(query, True, ())

        hits: list[AdministrativeHit] = []
        for setting in self._configuration.all():
            haystack = f"{setting.key} {setting.value} {setting.scope.value}".lower()
            score = _score(haystack, query_tokens)
            if score > 0:
                hits.append(
                    AdministrativeHit(
                        kind="setting",
                        identifier=setting.setting_id,
                        score=score,
                        detail=setting.to_dict(),
                    )
                )
        for member in self._membership.all():
            haystack = f"{member.subject} {member.target} {member.scope.value}".lower()
            score = _score(haystack, query_tokens)
            if score > 0:
                hits.append(
                    AdministrativeHit(
                        kind="member",
                        identifier=member.member_id,
                        score=score,
                        detail=member.to_dict(),
                    )
                )
        hits.sort(key=lambda h: (h.kind, -h.score, h.identifier))
        return AdministrativeSearchResponse.create(query, True, tuple(hits))

    def _resolve_principal(self, session_id: str, now: int):
        try:
            session = self._authorization.sessions.validate(session_id, now)
            return self._authorization.principals.get(session.principal_id)
        except IdentityError:
            return None


__all__ = [
    "AdministrativeHit",
    "AdministrativeSearchResponse",
    "AdministrativeSearch",
]
