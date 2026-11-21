"""EC2-CAP-ADMIN-001 — Administrative Membership (Administration Runtime).

The deterministic, append-only registry binding principals to **administrative
scopes** — *who is an administrator of what* (the platform, a tenant, or a workspace).
This is the substrate for tenant administration, workspace administration, and
membership administration. An administrative membership is an *operational
administration fact* — it records an administrative assignment and never a substitute
for platform authorization (which the Identity Layer resolves; a principal must hold
``administration-policy`` grants to be assigned an administrator by the service).

Membership identity is the ``(scope, target, principal)`` triple (content-addressed
``member_id``). The registry is fail-closed (duplicate add, or removal/lookup of an
absent member, raise) and records every change as an ordered, append-only
:class:`AdministrativeMembershipEvent` (no wall-clock; a caller-supplied logical
``tick``) so administrative history is reproducible and auditable (OP-C3).

``add`` validates only value shape — it deliberately does **not** enforce the
scope↔tenant cross-field invariant; that consistency is asserted by
:class:`~platform.administration.health.AdministrationHealth` so an induced
inconsistency (a fault) drives health ``UNHEALTHY`` (OP-C1), exactly as the Workspace
Runtime surfaces orphaned memberships.
"""

from __future__ import annotations

from dataclasses import dataclass
from platform.administration.contracts import AdministrativeScope
from platform.administration.errors import AdministrationMembershipError
from platform.foundation.contracts import content_hash
from typing import Any


def _require_str(value: str, what: str) -> str:
    if not isinstance(value, str) or not value:
        raise AdministrationMembershipError(f"administrative membership requires a {what}")
    return value


@dataclass(frozen=True, slots=True)
class AdministrativeMember:
    """An immutable, content-addressed binding of a principal to an admin scope."""

    member_id: str
    scope: AdministrativeScope
    target: str
    principal_id: str
    subject: str
    tenant: str | None

    @classmethod
    def create(
        cls,
        scope: AdministrativeScope,
        target: str,
        principal_id: str,
        subject: str,
        *,
        tenant: str | None = None,
    ) -> AdministrativeMember:
        """Build a member with a deterministic id (keyed by scope + target + principal)."""
        if not isinstance(scope, AdministrativeScope):
            raise AdministrationMembershipError("member scope must be an AdministrativeScope")
        target_v = _require_str(target, "target")
        principal_v = _require_str(principal_id, "principal_id")
        subject_v = _require_str(subject, "subject")
        key = {"scope": scope.value, "target": target_v, "principal_id": principal_v}
        return cls(
            member_id=f"UCOS-AMEM-{content_hash(key)[:16]}",
            scope=scope,
            target=target_v,
            principal_id=principal_v,
            subject=subject_v,
            tenant=tenant,
        )

    @property
    def requires_tenant(self) -> bool:
        """True iff this member's scope should name a tenant boundary (tenant/workspace)."""
        return self.scope in (AdministrativeScope.TENANT, AdministrativeScope.WORKSPACE)

    @property
    def is_consistent(self) -> bool:
        """True iff a tenant/workspace-scoped member names a tenant boundary."""
        return not self.requires_tenant or self.tenant is not None

    def to_dict(self) -> dict[str, Any]:
        return {
            "member_id": self.member_id,
            "scope": self.scope.value,
            "target": self.target,
            "principal_id": self.principal_id,
            "subject": self.subject,
            "tenant": self.tenant,
        }


@dataclass(frozen=True, slots=True)
class AdministrativeMembershipEvent:
    """An immutable, ordered record of an administrative membership change."""

    sequence: int
    member_id: str
    scope: AdministrativeScope
    target: str
    principal_id: str
    action: str
    tick: int

    def to_dict(self) -> dict[str, Any]:
        return {
            "sequence": self.sequence,
            "member_id": self.member_id,
            "scope": self.scope.value,
            "target": self.target,
            "principal_id": self.principal_id,
            "action": self.action,
            "tick": self.tick,
        }


class AdministrativeMembershipRegistry:
    """A deterministic, append-only registry of administrative memberships."""

    __slots__ = ("_by_id", "_log")

    def __init__(self) -> None:
        self._by_id: dict[str, AdministrativeMember] = {}
        self._log: list[AdministrativeMembershipEvent] = []

    def add(
        self,
        scope: AdministrativeScope,
        target: str,
        principal_id: str,
        subject: str,
        *,
        tick: int,
        tenant: str | None = None,
    ) -> AdministrativeMember:
        """Assign a principal as administrator of a scope target (fail-closed on duplicate)."""
        member = AdministrativeMember.create(scope, target, principal_id, subject, tenant=tenant)
        if member.member_id in self._by_id:
            raise AdministrationMembershipError(
                "principal is already an administrator of this target",
                scope=scope.value,
                target=member.target,
                principal_id=member.principal_id,
            )
        self._ingest(member)
        self._record(member, "assigned", tick)
        return member

    def remove(
        self,
        scope: AdministrativeScope,
        target: str,
        principal_id: str,
        *,
        tick: int,
    ) -> AdministrativeMember:
        """Revoke an administrator assignment (fail-closed on absent)."""
        probe = AdministrativeMember.create(scope, target, principal_id, "probe")
        member = self._by_id.get(probe.member_id)
        if member is None:
            raise AdministrationMembershipError(
                "principal is not an administrator of this target",
                scope=scope.value,
                target=probe.target,
                principal_id=probe.principal_id,
            )
        del self._by_id[member.member_id]
        self._record(member, "revoked", tick)
        return member

    def _ingest(self, member: AdministrativeMember) -> None:
        """Store a pre-built member (used by ``add`` and by fault-injection tests)."""
        if not isinstance(member, AdministrativeMember):
            raise AdministrationMembershipError("a valid AdministrativeMember is required")
        self._by_id[member.member_id] = member

    def is_administrator(self, scope: AdministrativeScope, target: str, principal_id: str) -> bool:
        """True iff ``principal_id`` is an administrator of ``(scope, target)``."""
        probe = AdministrativeMember.create(scope, target, principal_id, "probe")
        return probe.member_id in self._by_id

    def members_of(
        self, scope: AdministrativeScope, target: str
    ) -> tuple[AdministrativeMember, ...]:
        """Every administrator of ``(scope, target)`` in stable (member-id) order."""
        if not isinstance(scope, AdministrativeScope):
            raise AdministrationMembershipError("scope must be an AdministrativeScope")
        selected = [m for m in self._by_id.values() if m.scope is scope and m.target == target]
        return tuple(sorted(selected, key=lambda m: m.member_id))

    def scopes_of(self, principal_id: str) -> tuple[AdministrativeMember, ...]:
        """Every administrative membership held by ``principal_id`` (stable order)."""
        selected = [m for m in self._by_id.values() if m.principal_id == principal_id]
        return tuple(sorted(selected, key=lambda m: m.member_id))

    def all(self) -> tuple[AdministrativeMember, ...]:
        """Every current administrative membership in stable (member-id) order."""
        return tuple(self._by_id[mid] for mid in sorted(self._by_id))

    @property
    def events(self) -> tuple[AdministrativeMembershipEvent, ...]:
        """An immutable snapshot of the append-only membership event log (in order)."""
        return tuple(self._log)

    def __len__(self) -> int:
        return len(self._by_id)

    def to_dict(self) -> dict[str, Any]:
        return {
            "member_count": len(self._by_id),
            "members": [m.to_dict() for m in self.all()],
        }

    def fingerprint(self) -> str:
        return content_hash(self.to_dict())

    def _record(self, member: AdministrativeMember, action: str, tick: int) -> None:
        self._log.append(
            AdministrativeMembershipEvent(
                sequence=len(self._log),
                member_id=member.member_id,
                scope=member.scope,
                target=member.target,
                principal_id=member.principal_id,
                action=action,
                tick=tick,
            )
        )


__all__ = [
    "AdministrativeMember",
    "AdministrativeMembershipEvent",
    "AdministrativeMembershipRegistry",
]
