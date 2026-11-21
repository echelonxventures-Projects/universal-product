"""EC2-CAP-ADMIN-001 — Administrative Permissions (Administration Runtime).

**Permission administration** as a deterministic *evaluation view* over the certified
Identity Layer's :class:`~platform.identity.permissions.PermissionEngine`. It
introduces **no new authorization logic**: it reuses the engine to resolve a
principal's effective permissions on the ``administration-policy`` capability group
(§3.2) and maps them onto the operational
:class:`~platform.administration.contracts.AdministrativeAction` verbs the
Administration Runtime speaks.

Because every administrative action is bound to exactly one identity
:class:`~platform.foundation.identity.Permission`
(:func:`~platform.administration.contracts.required_permission`), the granted action
set is fully derived from the reused RBAC resolution — it can neither add nor widen
authority. It is a pure function of the principal and the reused engine.
"""

from __future__ import annotations

from platform.administration.contracts import (
    ADMINISTRATION_GROUP,
    AdministrativeAction,
    all_administrative_actions,
    required_permission,
)
from platform.administration.errors import AdministrationPermissionError
from platform.foundation.identity import Principal
from platform.identity.permissions import EffectivePermissions, PermissionEngine


class AdministrativePermissions:
    """Deterministic evaluator of a principal's effective administrative verbs."""

    __slots__ = ("_permissions",)

    def __init__(self, permissions: PermissionEngine) -> None:
        if not isinstance(permissions, PermissionEngine):
            raise AdministrationPermissionError("a valid PermissionEngine is required")
        self._permissions = permissions

    @property
    def permissions(self) -> PermissionEngine:
        return self._permissions

    def resolve(self, principal: Principal) -> EffectivePermissions:
        """Resolve the principal's effective permissions on ``administration-policy``."""
        if not isinstance(principal, Principal):
            raise AdministrationPermissionError("a valid Principal is required")
        return self._permissions.resolve(principal, ADMINISTRATION_GROUP)

    def can(self, principal: Principal, action: AdministrativeAction) -> bool:
        """True iff ``principal`` holds the identity permission ``action`` requires."""
        if not isinstance(action, AdministrativeAction):
            raise AdministrationPermissionError("action must be an AdministrativeAction")
        effective = self.resolve(principal)
        return effective.allows(required_permission(action))

    def actions_for(self, principal: Principal) -> frozenset[AdministrativeAction]:
        """The set of administrative actions ``principal`` is granted (may be empty)."""
        effective = self.resolve(principal)
        return frozenset(
            action
            for action in all_administrative_actions()
            if effective.allows(required_permission(action))
        )

    def is_administrator(self, principal: Principal) -> bool:
        """True iff ``principal`` holds any mutating administrative action."""
        return bool(self.actions_for(principal) - {AdministrativeAction.INSPECT})


__all__ = ["AdministrativePermissions"]
