"""EC2-TASK-000074 — Portal Access Gateway (EC2-EPIC-003).

The portal's **authentication & authorization integration** point. It does **not**
implement identity — it composes the certified EC-2 Identity Layer (L7,
EC2-EPIC-002) by holding a reference to its
:class:`~platform.identity.service.AuthorizationService` and routing every portal
access decision through it. There is **no duplicate identity implementation**: the
gateway establishes/validates sessions, resolves principals, and authorizes surface
access strictly via the L7 decision point (session → principal → policy → decision),
inheriting its fail-closed guarantees, append-only decision log, and audit events
(PC-16).

Admission is fail-closed: a caller may **enter** the portal only with a valid session
whose principal holds READ on the ``portal-navigation`` capability group (§3.2 row 0).
An absent/expired/revoked session, an unregistered principal, or a role without that
grant (e.g. the Integrator, whose §3.2 portal-navigation cell is empty) is denied.
"""

from __future__ import annotations

from dataclasses import dataclass
from platform.foundation.identity import Permission, Principal
from platform.identity.contracts import AccessDecision, CapabilityGroup, Decision
from platform.identity.service import AuthorizationService
from platform.identity.sessions import Session
from platform.portal.errors import PortalAccessError
from typing import Any


@dataclass(frozen=True, slots=True)
class PortalAdmission:
    """An immutable record of a portal admission decision (fail-closed).

    Produced by :meth:`PortalAccessGateway.admit`; ``admitted`` is ``True`` only when
    the session's principal holds READ on ``portal-navigation``. Carries the
    identity-layer :class:`AccessDecision` so the admission is fully traceable.
    """

    session_id: str
    principal_id: str
    admitted: bool
    decision: AccessDecision

    @property
    def reason(self) -> str:
        return self.decision.reason

    def to_dict(self) -> dict[str, Any]:
        return {
            "session_id": self.session_id,
            "principal_id": self.principal_id,
            "admitted": self.admitted,
            "decision": self.decision.to_dict(),
        }


class PortalAccessGateway:
    """Integrates the Identity Layer as the portal's single access decision seam."""

    __slots__ = ("_authorization",)

    def __init__(self, authorization: AuthorizationService) -> None:
        if not isinstance(authorization, AuthorizationService):
            raise PortalAccessError("a valid AuthorizationService is required")
        self._authorization = authorization

    @property
    def authorization(self) -> AuthorizationService:
        """The composed L7 authorization service (identity integration point)."""
        return self._authorization

    # -- session lifecycle (delegated to identity) ------------------------------

    def establish_session(
        self,
        principal: Principal,
        *,
        issued_at: int,
        ttl: int,
        credential_ref: str | None = None,
    ) -> Session:
        """Establish an authenticated session via the Identity Layer (no duplication)."""
        if not isinstance(principal, Principal):
            raise PortalAccessError("establish_session requires a Principal")
        return self._authorization.establish_session(
            principal, issued_at=issued_at, ttl=ttl, credential_ref=credential_ref
        )

    def revoke_session(self, session_id: str, *, tick: int) -> Session:
        """Revoke a session via the Identity Layer (idempotent, append-only)."""
        return self._authorization.revoke_session(session_id, tick=tick)

    # -- authorization (delegated to identity) ----------------------------------

    def authorize(
        self,
        session_id: str,
        group: CapabilityGroup,
        permission: Permission,
        *,
        now: int,
        tenant: str | None = None,
        resource: str | None = None,
    ) -> AccessDecision:
        """Authorize a session-bearing request through the L7 decision point."""
        if not isinstance(session_id, str) or not session_id:
            raise PortalAccessError("authorize requires a session_id")
        if not isinstance(group, CapabilityGroup):
            raise PortalAccessError("group must be a CapabilityGroup")
        if not isinstance(permission, Permission):
            raise PortalAccessError("permission must be a Permission")
        return self._authorization.authorize(
            session_id, group, permission, now=now, tenant=tenant, resource=resource
        )

    def is_permitted(
        self,
        session_id: str,
        group: CapabilityGroup,
        permission: Permission,
        *,
        now: int,
        tenant: str | None = None,
        resource: str | None = None,
    ) -> bool:
        """True iff the session-bearing request is PERMITTED (fail-closed)."""
        decision = self.authorize(
            session_id, group, permission, now=now, tenant=tenant, resource=resource
        )
        return decision.decision is Decision.PERMIT

    # -- admission --------------------------------------------------------------

    def admit(self, session_id: str, *, now: int, tenant: str | None = None) -> PortalAdmission:
        """Decide whether ``session_id`` may enter the portal (fail-closed).

        Admission requires READ on the ``portal-navigation`` capability group. The
        returned :class:`PortalAdmission` carries the underlying identity decision;
        it never raises for an ordinary denial (denials are data, not exceptions),
        but a malformed request raises :class:`PortalAccessError`.
        """
        decision = self.authorize(
            session_id,
            CapabilityGroup.PORTAL_NAVIGATION,
            Permission.READ,
            now=now,
            tenant=tenant,
        )
        return PortalAdmission(
            session_id=session_id,
            principal_id=decision.request.principal_id,
            admitted=decision.decision is Decision.PERMIT,
            decision=decision,
        )

    def require_admission(
        self, session_id: str, *, now: int, tenant: str | None = None
    ) -> PortalAdmission:
        """Admit or raise :class:`PortalAccessError` (fail-closed enforcement)."""
        admission = self.admit(session_id, now=now, tenant=tenant)
        if not admission.admitted:
            raise PortalAccessError(
                "portal admission denied",
                session_id=session_id,
                reason=admission.reason,
            )
        return admission


__all__ = ["PortalAdmission", "PortalAccessGateway"]
