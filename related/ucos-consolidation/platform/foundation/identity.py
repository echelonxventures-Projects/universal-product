"""EC2-TASK-000057 — Platform Identity Model (EC2-EPIC-001).

The *model* (value types) for platform identity: roles, permissions, and
principals. This is the foundational vocabulary every future EC-2 epic reads to
reason about *who* may do *what*. It is **not** authentication or authorization
enforcement — those are EC2-EPIC-002 (Identity & Access) and EC2-EPIC-014
(Administration & Governance); this epic defines only the immutable, deterministic
model they build on.

The model encodes the nine EC-2 user categories (§3 of the Program) as
:class:`Role`, the coarse permission verbs (C/R/X/A) as :class:`Permission`, and an
immutable :class:`Principal` (identity + roles + optional tenant scope). Secrets and
credentials are never modeled here (SEC-04 — those are by reference in EPIC-002).
Principal identities are content-addressed and deterministic.
"""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from dataclasses import dataclass, field
from enum import Enum
from platform.foundation.contracts import content_hash
from platform.foundation.errors import PlatformIdentityError
from typing import Any


class Role(str, Enum):
    """The nine EC-2 platform user categories (§3 of the Program)."""

    PLATFORM_ADMINISTRATOR = "platform-administrator"
    ARCHITECT = "architect"
    DEVELOPER = "developer"
    OPERATOR = "operator"
    AUDITOR = "auditor"
    CERTIFICATION_AUTHORITY = "certification-authority"
    BUSINESS_USER = "business-user"
    PARTNER = "partner"
    INTEGRATOR = "integrator"


class Permission(str, Enum):
    """The coarse permission verbs used by the RBAC model (§3.2 of the Program)."""

    CREATE = "create"
    READ = "read"
    EXECUTE = "execute"
    ADMINISTER = "administer"


@dataclass(frozen=True, slots=True)
class Principal:
    """An immutable platform principal: an identity bearing roles and a scope.

    ``principal_id`` is content-addressed (deterministic) from the subject, roles,
    and tenant, so an identical principal definition always yields the same id.
    Holds **no** secret or credential material (SEC-04).
    """

    subject: str
    roles: frozenset[Role]
    tenant: str | None = None
    attributes: Mapping[str, Any] = field(default_factory=dict)
    principal_id: str = ""

    @classmethod
    def create(
        cls,
        subject: str,
        roles: Iterable[Role],
        *,
        tenant: str | None = None,
        attributes: Mapping[str, Any] | None = None,
    ) -> Principal:
        """Build a :class:`Principal` with a deterministic, content-addressed id."""
        if not isinstance(subject, str) or not subject.strip():
            raise PlatformIdentityError("principal subject is required")
        role_set = frozenset(roles)
        if not role_set:
            raise PlatformIdentityError("principal must hold at least one role", subject=subject)
        if not all(isinstance(r, Role) for r in role_set):
            raise PlatformIdentityError("principal roles must be Role members", subject=subject)
        attrs = dict(attributes or {})
        core = {
            "subject": subject,
            "roles": sorted(r.value for r in role_set),
            "tenant": tenant,
            "attributes": attrs,
        }
        digest = content_hash(core)
        return cls(
            subject=subject,
            roles=role_set,
            tenant=tenant,
            attributes=attrs,
            principal_id=f"UCOS-PRIN-{digest[:16]}",
        )

    def has_role(self, role: Role) -> bool:
        return role in self.roles

    def has_any_role(self, roles: Iterable[Role]) -> bool:
        return bool(self.roles.intersection(set(roles)))

    @property
    def is_scoped(self) -> bool:
        """True iff the principal is confined to a single tenant/workspace scope."""
        return self.tenant is not None

    def to_dict(self) -> dict[str, Any]:
        return {
            "principal_id": self.principal_id,
            "subject": self.subject,
            "roles": sorted(r.value for r in self.roles),
            "tenant": self.tenant,
            "attributes": dict(self.attributes),
        }


#: The roles whose access is always tenant/workspace-scoped and isolated (§3.2).
SCOPED_ROLES: frozenset[Role] = frozenset({Role.PARTNER, Role.INTEGRATOR})

#: The read-only roles that hold no mutation rights over pipeline artifacts (§3.2).
READ_ONLY_ROLES: frozenset[Role] = frozenset({Role.AUDITOR, Role.CERTIFICATION_AUTHORITY})


def all_roles() -> tuple[Role, ...]:
    """Return every defined role in stable declaration order."""
    return tuple(Role)


__all__ = [
    "Role",
    "Permission",
    "Principal",
    "SCOPED_ROLES",
    "READ_ONLY_ROLES",
    "all_roles",
]
