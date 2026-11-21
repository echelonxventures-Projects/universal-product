"""EC2-CAP-ADMIN-001 — Administrative Role View (Administration Runtime).

**Role administration** as a strictly **read-only projection** over the certified
Identity Layer's §3.2 RBAC matrix (:class:`~platform.identity.roles.RoleRegistry`).
This module introduces **no new role scheme, no new allocator, and no new authority**:
it only *reads* which platform :class:`~platform.foundation.identity.Role` categories
hold a grant on the ``administration-policy`` capability group and *what verbs* they
hold there. Administering roles, in an operational-administration runtime that is not
governance, means **inspecting** the authoritative matrix — never mutating it (the
matrix is the Identity Layer's canon).

The projection is a pure, deterministic function of the reused role registry — it
holds no state of its own and reproduces the same fingerprint for the same matrix.
"""

from __future__ import annotations

from platform.administration.contracts import ADMINISTRATION_GROUP
from platform.administration.errors import AdministrationRoleError
from platform.foundation.contracts import content_hash
from platform.foundation.identity import Permission, Role
from platform.identity.roles import RoleGrant, RoleRegistry
from typing import Any


class AdministrativeRoleView:
    """A deterministic, read-only view of administrative grants in the §3.2 matrix."""

    __slots__ = ("_roles",)

    def __init__(self, roles: RoleRegistry) -> None:
        if not isinstance(roles, RoleRegistry):
            raise AdministrationRoleError("a valid RoleRegistry is required")
        self._roles = roles

    @property
    def roles(self) -> RoleRegistry:
        return self._roles

    def grant_for(self, role: Role) -> RoleGrant | None:
        """Return ``role``'s grant on the administration group, or ``None``."""
        if not isinstance(role, Role):
            raise AdministrationRoleError("role must be a Role")
        return self._roles.get(role).grant_for(ADMINISTRATION_GROUP)

    def administrative_roles(self) -> tuple[Role, ...]:
        """Every registered role that holds any grant on ``administration-policy``."""
        return tuple(r for r in self._roles.roles if self.grant_for(r) is not None)

    def administering_roles(self) -> tuple[Role, ...]:
        """Every registered role that holds ADMINISTER on ``administration-policy``."""
        return tuple(
            r
            for r in self._roles.roles
            if (grant := self.grant_for(r)) is not None
            and Permission.ADMINISTER in grant.permissions
        )

    def can_administer(self, role: Role) -> bool:
        """True iff ``role`` holds ADMINISTER on the administration group."""
        grant = self.grant_for(role)
        return grant is not None and Permission.ADMINISTER in grant.permissions

    def permissions_of(self, role: Role) -> frozenset[Permission]:
        """The permission verbs ``role`` holds on the administration group (may be empty)."""
        grant = self.grant_for(role)
        return grant.permissions if grant is not None else frozenset()

    def to_dict(self) -> dict[str, Any]:
        return {
            "group": ADMINISTRATION_GROUP.value,
            "administrative_roles": [
                {
                    "role": role.value,
                    "permissions": sorted(p.value for p in self.permissions_of(role)),
                    "can_administer": self.can_administer(role),
                }
                for role in self.administrative_roles()
            ],
        }

    def fingerprint(self) -> str:
        return content_hash(self.to_dict())


__all__ = ["AdministrativeRoleView"]
