"""EC2-TASK-000064 — Principal Registry (EC2-EPIC-002).

The deterministic, append-only registry of platform principals. A
:class:`~platform.foundation.identity.Principal` (defined in the Platform Foundation,
EC2-TASK-000057) is *who* acts on the platform; this registry is the authoritative,
registry-driven store of *which* principals exist and the seam every identity
service resolves them through.

Guarantees (IMP-007 §5 determinism; PL-04 least-privilege; SEC-04 secrets by ref):
    * **Deterministic** — principals list and resolve in a stable order (sorted by
      ``principal_id``); registration order does not affect observable behavior.
    * **Content-addressed identity** — a principal is keyed by its content-addressed
      ``principal_id``; registering the *same* principal definition twice is idempotent,
      registering a *different* principal under a colliding subject is allowed (each is
      a distinct content-addressed identity), and re-registering a conflicting body
      under an existing id is rejected.
    * **Append-only & fail-closed** — the registry never mutates or removes a
      principal; unknown resolution raises.
    * **No secrets** — principals hold no credential material (SEC-04); credentials
      are referenced elsewhere by reference only.

This module stores *principal declarations only*; it authenticates nothing and
authorizes nothing (those are the session model and the authorization service).
"""

from __future__ import annotations

from collections.abc import Iterable
from platform.foundation.identity import Principal, Role
from platform.identity.errors import PrincipalRegistryError
from typing import Any


class PrincipalRegistry:
    """A deterministic, append-only registry of platform principals."""

    __slots__ = ("_by_id",)

    def __init__(self) -> None:
        self._by_id: dict[str, Principal] = {}

    def register(self, principal: Principal) -> Principal:
        """Register a principal (idempotent for an identical definition; fail-closed).

        Registering the exact same content-addressed principal again is a no-op.
        Registering a *different* principal body under an existing ``principal_id``
        (which content-addressing makes practically impossible, but is guarded
        defensively) is rejected.
        """
        if not isinstance(principal, Principal):
            raise PrincipalRegistryError("a valid Principal is required")
        if not principal.principal_id:
            raise PrincipalRegistryError(
                "principal must carry a content-addressed principal_id",
                subject=principal.subject,
            )
        existing = self._by_id.get(principal.principal_id)
        if existing is not None:
            if existing.to_dict() != principal.to_dict():
                raise PrincipalRegistryError(
                    "principal_id already registered with a different definition",
                    principal_id=principal.principal_id,
                )
            return existing
        self._by_id[principal.principal_id] = principal
        return principal

    def register_subject(
        self,
        subject: str,
        roles: Iterable[Role],
        *,
        tenant: str | None = None,
        attributes: dict[str, Any] | None = None,
    ) -> Principal:
        """Create (content-addressed) and register a principal in one step."""
        principal = Principal.create(subject, roles, tenant=tenant, attributes=attributes)
        return self.register(principal)

    def register_all(self, principals: Iterable[Principal]) -> None:
        for principal in principals:
            self.register(principal)

    def __contains__(self, principal_id: str) -> bool:
        return principal_id in self._by_id

    def __len__(self) -> int:
        return len(self._by_id)

    def get(self, principal_id: str) -> Principal:
        """Resolve a principal by its content-addressed id (raises if absent)."""
        principal = self._by_id.get(principal_id)
        if principal is None:
            raise PrincipalRegistryError("no such principal", principal_id=principal_id)
        return principal

    @property
    def ids(self) -> tuple[str, ...]:
        """Every registered principal id in deterministic order."""
        return tuple(sorted(self._by_id))

    def principals(self) -> tuple[Principal, ...]:
        """Every registered principal in deterministic (id) order."""
        return tuple(self._by_id[pid] for pid in self.ids)

    def by_subject(self, subject: str) -> tuple[Principal, ...]:
        """Every principal for ``subject`` in deterministic (id) order.

        A subject may hold more than one content-addressed identity (e.g. differing
        role sets or tenant scopes); all are returned.
        """
        return tuple(p for p in self.principals() if p.subject == subject)

    def with_role(self, role: Role) -> tuple[Principal, ...]:
        """Every registered principal bearing ``role`` (deterministic order)."""
        return tuple(p for p in self.principals() if p.has_role(role))

    def in_tenant(self, tenant: str) -> tuple[Principal, ...]:
        """Every registered principal scoped to ``tenant`` (deterministic order)."""
        return tuple(p for p in self.principals() if p.tenant == tenant)

    def to_dict(self) -> dict[str, Any]:
        return {
            "principal_count": len(self._by_id),
            "principals": [p.to_dict() for p in self.principals()],
        }

    def fingerprint(self) -> str:
        """A deterministic content hash of the whole registry (reproducible)."""
        from platform.foundation.contracts import content_hash

        return content_hash(self.to_dict())


__all__ = ["PrincipalRegistry"]
