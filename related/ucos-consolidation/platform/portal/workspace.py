"""EC2-TASK-000077 — Portal Workspace Handoff Model (EC2-EPIC-003).

The **portal-to-workspace handoff** model. Workspace lifecycle itself is owned by
EC2-EPIC-004 (Workspace & Collaboration) — not yet built — so the portal implements
only the *handoff*: the governed transition from the portal shell into a scoped
workspace context. A handoff is a deterministic, content-addressed descriptor naming
the target workspace, the (optional) tenant scope, and the landing route, produced
**only** after the Identity Layer authorizes READ on the ``workspace-project-lifecycle``
capability group (§3.2 row 3) — including the tenant-isolation invariant for scoped
roles (Partner/Integrator).

The model invents no workspace semantics and holds no workspace state; it is the
authorization-gated seam a future workspace layer consumes. It is fail-closed: an
unauthorized or malformed selection never yields a usable handoff.
"""

from __future__ import annotations

from dataclasses import dataclass
from platform.foundation.contracts import content_hash
from platform.foundation.identity import Permission
from platform.identity.contracts import AccessDecision, CapabilityGroup, Decision
from platform.portal.access import PortalAccessGateway
from platform.portal.errors import WorkspaceHandoffError
from platform.portal.routing import Router
from typing import Any

#: The capability group a caller must hold READ on to enter a workspace context.
WORKSPACE_GROUP = CapabilityGroup.WORKSPACE_PROJECT_LIFECYCLE


@dataclass(frozen=True, slots=True)
class WorkspaceHandoff:
    """An immutable, content-addressed portal-to-workspace handoff descriptor."""

    session_id: str
    principal_id: str
    workspace_id: str
    tenant: str | None
    landing_path: str
    authorized: bool
    decision: AccessDecision
    handoff_id: str = ""

    @classmethod
    def create(
        cls,
        *,
        session_id: str,
        principal_id: str,
        workspace_id: str,
        tenant: str | None,
        landing_path: str,
        authorized: bool,
        decision: AccessDecision,
    ) -> WorkspaceHandoff:
        core = {
            "principal_id": principal_id,
            "workspace_id": workspace_id,
            "tenant": tenant,
            "landing_path": landing_path,
            "authorized": authorized,
        }
        return cls(
            session_id=session_id,
            principal_id=principal_id,
            workspace_id=workspace_id,
            tenant=tenant,
            landing_path=landing_path,
            authorized=authorized,
            decision=decision,
            handoff_id=f"UCOS-PWSH-{content_hash(core)[:16]}",
        )

    @property
    def reason(self) -> str:
        return self.decision.reason

    def to_dict(self) -> dict[str, Any]:
        return {
            "handoff_id": self.handoff_id,
            "session_id": self.session_id,
            "principal_id": self.principal_id,
            "workspace_id": self.workspace_id,
            "tenant": self.tenant,
            "landing_path": self.landing_path,
            "authorized": self.authorized,
            "decision": self.decision.to_dict(),
        }


class WorkspaceSelector:
    """Produces authorization-gated portal-to-workspace handoffs (fail-closed)."""

    __slots__ = ("_gateway", "_landing_path")

    def __init__(self, gateway: PortalAccessGateway, *, router: Router | None = None) -> None:
        if not isinstance(gateway, PortalAccessGateway):
            raise WorkspaceHandoffError("a valid PortalAccessGateway is required")
        self._gateway = gateway
        # The workspace landing route is resolved from the router when available so
        # the handoff target stays consistent with the routing model.
        if router is not None:
            self._landing_path = router.resolve(f"/{WORKSPACE_GROUP.value}").path
        else:
            self._landing_path = f"/{WORKSPACE_GROUP.value}"

    @property
    def landing_path(self) -> str:
        return self._landing_path

    def handoff(
        self,
        session_id: str,
        workspace_id: str,
        *,
        now: int,
        tenant: str | None = None,
    ) -> WorkspaceHandoff:
        """Build a handoff for ``workspace_id`` (authorized READ on the group).

        Returns an unauthorized handoff (``authorized == False``) when the identity
        decision denies — denials are data, not exceptions — but a malformed request
        raises :class:`WorkspaceHandoffError`.
        """
        if not isinstance(workspace_id, str) or not workspace_id:
            raise WorkspaceHandoffError("handoff requires a workspace_id")
        decision = self._gateway.authorize(
            session_id,
            WORKSPACE_GROUP,
            Permission.READ,
            now=now,
            tenant=tenant,
            resource=workspace_id,
        )
        authorized = decision.decision is Decision.PERMIT
        return WorkspaceHandoff.create(
            session_id=session_id,
            principal_id=decision.request.principal_id,
            workspace_id=workspace_id,
            tenant=tenant,
            landing_path=self._landing_path,
            authorized=authorized,
            decision=decision,
        )

    def require_handoff(
        self,
        session_id: str,
        workspace_id: str,
        *,
        now: int,
        tenant: str | None = None,
    ) -> WorkspaceHandoff:
        """Produce a handoff or raise :class:`WorkspaceHandoffError` (fail-closed)."""
        handoff = self.handoff(session_id, workspace_id, now=now, tenant=tenant)
        if not handoff.authorized:
            raise WorkspaceHandoffError(
                "workspace handoff denied",
                session_id=session_id,
                workspace_id=workspace_id,
                reason=handoff.reason,
            )
        return handoff


__all__ = ["WORKSPACE_GROUP", "WorkspaceHandoff", "WorkspaceSelector"]
