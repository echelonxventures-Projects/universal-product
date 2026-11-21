"""EC2-CAP-ADMIN-001 — Administrative Context (Administration Runtime).

The immutable, content-addressed **runtime context** produced when a principal
successfully enters an administrative scope: the binding of *who* (principal +
subject) to *where* (administrative scope + tenant) and *what administrative actions*
that principal is granted there. It is derived only from an already-authorized,
isolation-cleared entry — it grants nothing on its own (the granted actions are the
verbs the Identity Layer already resolved for the principal) and holds no secret
material (SEC-04).

The administrative context is *not* an authentication session and *not* a new session
model: sessions are the certified Identity Layer's responsibility
(:class:`~platform.identity.sessions.Session`). This context is a derived, downstream
value a runtime-management surface carries to operate **within** an administrative
boundary. It is deterministic: identical bindings yield an identical ``context_id``.
"""

from __future__ import annotations

from dataclasses import dataclass
from platform.administration.contracts import AdministrativeAction, AdministrativeScope
from platform.administration.errors import AdministrationContextError
from platform.foundation.contracts import content_hash
from platform.foundation.identity import Principal
from typing import Any


@dataclass(frozen=True, slots=True)
class AdministrativeContext:
    """An immutable, content-addressed administrative runtime context binding."""

    context_id: str
    principal_id: str
    subject: str
    scope: AdministrativeScope
    tenant: str | None
    actions: frozenset[AdministrativeAction]

    @classmethod
    def create(
        cls,
        principal: Principal,
        scope: AdministrativeScope,
        actions: frozenset[AdministrativeAction],
        *,
        tenant: str | None = None,
    ) -> AdministrativeContext:
        """Build the deterministic runtime context for an authorized admin entry."""
        if not isinstance(principal, Principal):
            raise AdministrationContextError("administrative context requires a Principal")
        if not isinstance(scope, AdministrativeScope):
            raise AdministrationContextError("administrative context requires a scope")
        action_set = frozenset(actions)
        if not all(isinstance(a, AdministrativeAction) for a in action_set):
            raise AdministrationContextError(
                "administrative context actions must be AdministrativeAction members"
            )
        core = {
            "principal_id": principal.principal_id,
            "scope": scope.value,
            "tenant": tenant,
            "actions": sorted(a.value for a in action_set),
        }
        return cls(
            context_id=f"UCOS-ACTX-{content_hash(core)[:16]}",
            principal_id=principal.principal_id,
            subject=principal.subject,
            scope=scope,
            tenant=tenant,
            actions=action_set,
        )

    def permits(self, action: AdministrativeAction) -> bool:
        """True iff the entered context is granted ``action``."""
        if not isinstance(action, AdministrativeAction):
            raise AdministrationContextError("action must be an AdministrativeAction")
        return action in self.actions

    @property
    def can_administer(self) -> bool:
        """True iff the context holds any mutating administrative action."""
        return bool(self.actions - {AdministrativeAction.INSPECT})

    def to_dict(self) -> dict[str, Any]:
        return {
            "context_id": self.context_id,
            "principal_id": self.principal_id,
            "subject": self.subject,
            "scope": self.scope.value,
            "tenant": self.tenant,
            "actions": sorted(a.value for a in self.actions),
        }

    def fingerprint(self) -> str:
        return content_hash(self.to_dict())


__all__ = ["AdministrativeContext"]
