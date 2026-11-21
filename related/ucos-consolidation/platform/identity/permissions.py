"""EC2-TASK-000066 — Permission Engine (EC2-EPIC-002).

Resolves the **effective permissions** a principal holds on a capability group by
composing the grants of every role the principal bears (§3.2). It is a pure,
deterministic function of the :class:`~platform.identity.roles.RoleRegistry` and the
principal's roles — it enforces no invariants and makes no allow/deny decision
(that is the policy engine); it answers only *"what verbs does this principal hold
here, and under what scope?"*

Resolution rules (deterministic, least-privilege by construction):
    * The effective permission set is the **union** of the matching role grants —
      holding several roles never removes access, only adds it.
    * ``ADMINISTER`` is the top verb and **implies** ``CREATE``, ``READ`` and
      ``EXECUTE`` (an administrator of a group can do everything in it).
    * A group is **scoped** for a principal only if *every* contributing role grant
      is scoped; a single unscoped grant makes the effective access unscoped.
    * The **attest** obligation is carried if *any* contributing grant carries it.
    * A principal with no matching grant on a group resolves to the **empty** set
      (no access) — never an error.
"""

from __future__ import annotations

from dataclasses import dataclass
from platform.foundation.identity import Permission, Principal, Role
from platform.identity.contracts import CapabilityGroup
from platform.identity.errors import PermissionResolutionError, RoleRegistryError
from platform.identity.roles import RoleRegistry
from typing import Any

#: ``ADMINISTER`` implies the full verb set.
_ADMINISTER_IMPLIES: frozenset[Permission] = frozenset(
    {Permission.CREATE, Permission.READ, Permission.EXECUTE, Permission.ADMINISTER}
)


def expand_permissions(permissions: frozenset[Permission]) -> frozenset[Permission]:
    """Expand a permission set, honoring the ``ADMINISTER`` implication."""
    if Permission.ADMINISTER in permissions:
        return _ADMINISTER_IMPLIES
    return frozenset(permissions)


@dataclass(frozen=True, slots=True)
class EffectivePermissions:
    """The resolved, expanded permissions a principal holds on one capability group."""

    group: CapabilityGroup
    permissions: frozenset[Permission]
    scoped: bool
    attest: bool
    contributing_roles: frozenset[Role]

    @property
    def granted(self) -> bool:
        """True iff the principal holds any permission on the group."""
        return bool(self.permissions)

    def allows(self, permission: Permission) -> bool:
        return permission in self.permissions

    def to_dict(self) -> dict[str, Any]:
        return {
            "group": self.group.value,
            "permissions": sorted(p.value for p in self.permissions),
            "scoped": self.scoped,
            "attest": self.attest,
            "contributing_roles": sorted(r.value for r in self.contributing_roles),
        }


class PermissionEngine:
    """Deterministic resolver of a principal's effective permissions (§3.2)."""

    __slots__ = ("_roles",)

    def __init__(self, roles: RoleRegistry) -> None:
        if not isinstance(roles, RoleRegistry):
            raise PermissionResolutionError("a valid RoleRegistry is required")
        self._roles = roles

    @property
    def roles(self) -> RoleRegistry:
        return self._roles

    def resolve(self, principal: Principal, group: CapabilityGroup) -> EffectivePermissions:
        """Resolve a principal's effective permissions on ``group`` (deterministic)."""
        if not isinstance(principal, Principal):
            raise PermissionResolutionError("a valid Principal is required")
        if not isinstance(group, CapabilityGroup):
            raise PermissionResolutionError(
                "group must be a CapabilityGroup", principal_id=principal.principal_id
            )
        permissions: set[Permission] = set()
        contributing: set[Role] = set()
        scoped_flags: list[bool] = []
        attest = False
        for role in principal.roles:
            try:
                definition = self._roles.get(role)  # fail-closed on unknown role
            except RoleRegistryError as exc:
                raise PermissionResolutionError(
                    "principal bears a role absent from the role registry",
                    principal_id=principal.principal_id,
                    role=role.value,
                ) from exc
            grant = definition.grant_for(group)
            if grant is None:
                continue
            contributing.add(role)
            permissions |= expand_permissions(grant.permissions)
            scoped_flags.append(grant.scoped)
            attest = attest or grant.attest
        # Scoped only if every contributing grant is scoped; empty => not scoped.
        scoped = bool(scoped_flags) and all(scoped_flags)
        return EffectivePermissions(
            group=group,
            permissions=frozenset(permissions),
            scoped=scoped,
            attest=attest,
            contributing_roles=frozenset(contributing),
        )

    def has_permission(
        self, principal: Principal, group: CapabilityGroup, permission: Permission
    ) -> bool:
        """True iff the principal holds ``permission`` on ``group`` (grant-level only).

        This reflects the RBAC *grant*; it does **not** apply the policy invariants
        (scope match, read-only/append-only guards) — that is the policy engine.
        """
        if not isinstance(permission, Permission):
            raise PermissionResolutionError(
                "permission must be a Permission", principal_id=principal.principal_id
            )
        return self.resolve(principal, group).allows(permission)

    def resolve_all(self, principal: Principal) -> tuple[EffectivePermissions, ...]:
        """Resolve the principal's effective permissions on every capability group.

        Only groups where the principal holds some permission are returned, in stable
        capability-group order (deterministic).
        """
        from platform.identity.contracts import all_capability_groups

        resolved = (self.resolve(principal, g) for g in all_capability_groups())
        return tuple(ep for ep in resolved if ep.granted)


__all__ = [
    "expand_permissions",
    "EffectivePermissions",
    "PermissionEngine",
]
