"""EC2-TASK-000088 — Workspace Service (EC2-EPIC-004).

The single, governed **workspace runtime composition point** (L3 Application of the
Program architecture) that composes the whole Workspace Runtime into one entry point —
the scoped execution boundary for users, organizations, capabilities, and future
generated products:

    WorkspaceRegistry · MembershipRegistry · IsolationGuard · WorkspaceSearch ·
    WorkspaceHealth  ·  (reused) AuthorizationService · ObservabilityService

It is a strictly **additive** layer: it authorizes only through the certified Identity
Layer (L7) — **no duplicate authorization or identity logic** — observes only through
the Observability Layer (L8), and reuses the Foundation registries/events (L4/L6). It
re-implements none of them, modifies none of them, and writes nothing to the certified
corpus (DP-03). Every workspace access is fail-closed and composes three independent
gates — **identity authorization** (RBAC §3.2), **tenant/workspace isolation** (P3),
and **membership** — so cross-tenant access is refused in 100% of cases. Because every
governed action is published onto the Foundation event bus, it is captured by
observability as append-only audit (PC-16 / OP-C3).

The service is deterministic: the same identity registrations, workspaces, memberships,
and ordered sequence of calls yield the same :class:`WorkspaceEvidence` fingerprint
(P5). :func:`build_workspace_service` provides the default wiring;
:func:`~platform.workspace.bootstrap.bootstrap_workspace` composes it onto a
:class:`~platform.foundation.bootstrap.PlatformContext`.
"""

from __future__ import annotations

from dataclasses import dataclass
from platform.foundation.contracts import content_hash
from platform.foundation.events import EventBus
from platform.foundation.identity import Permission
from platform.identity.contracts import AccessDecision
from platform.identity.errors import IdentityError
from platform.identity.service import AuthorizationService
from platform.observability.health import HealthRegistry
from platform.observability.service import ObservabilityService
from platform.workspace.context import WorkspaceContext
from platform.workspace.contracts import (
    WORKSPACE_GROUP,
    MemberRole,
    Workspace,
    WorkspaceMember,
    WorkspaceStatus,
)
from platform.workspace.errors import WorkspaceAccessError, WorkspaceServiceError
from platform.workspace.health import WorkspaceHealth, workspace_health_checks
from platform.workspace.isolation import IsolationGuard, tenants_isolated
from platform.workspace.membership import MembershipRegistry
from platform.workspace.metadata import WorkspaceMetadata
from platform.workspace.registration import WorkspaceRegistry
from platform.workspace.search import WorkspaceSearch, WorkspaceSearchResponse
from typing import Any

#: Governed events published onto the Foundation event bus (observed as PC-16).
WORKSPACE_CREATED_EVENT = "workspace.created"
WORKSPACE_MEMBER_ADDED_EVENT = "workspace.member.added"
WORKSPACE_MEMBER_REMOVED_EVENT = "workspace.member.removed"
WORKSPACE_LIFECYCLE_EVENT = "workspace.lifecycle.transitioned"
WORKSPACE_ACCESS_EVENT = "workspace.access.evaluated"


@dataclass(frozen=True, slots=True)
class WorkspaceAccess:
    """An immutable, content-addressed workspace access decision (fail-closed).

    Composes identity authorization, tenant/workspace isolation, and membership into a
    single verdict for one ``(principal, workspace, permission)`` request.
    """

    workspace_id: str
    principal_id: str
    permission: Permission
    granted: bool
    reason: str
    member_role: MemberRole | None
    decision: AccessDecision
    access_id: str = ""

    @classmethod
    def create(
        cls,
        *,
        workspace_id: str,
        permission: Permission,
        granted: bool,
        reason: str,
        decision: AccessDecision,
        member_role: MemberRole | None = None,
    ) -> WorkspaceAccess:
        principal_id = decision.request.principal_id
        core = {
            "workspace_id": workspace_id,
            "principal_id": principal_id,
            "permission": permission.value,
            "granted": granted,
            "reason": reason,
            "member_role": member_role.value if member_role else None,
        }
        return cls(
            workspace_id=workspace_id,
            principal_id=principal_id,
            permission=permission,
            granted=granted,
            reason=reason,
            member_role=member_role,
            decision=decision,
            access_id=f"UCOS-WACC-{content_hash(core)[:16]}",
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "access_id": self.access_id,
            "workspace_id": self.workspace_id,
            "principal_id": self.principal_id,
            "permission": self.permission.value,
            "granted": self.granted,
            "reason": self.reason,
            "member_role": self.member_role.value if self.member_role else None,
            "decision": self.decision.to_dict(),
        }


@dataclass(frozen=True, slots=True)
class WorkspaceEvidence:
    """A deterministic, content-addressed record of workspace runtime state (evidence)."""

    registry_fingerprint: str
    membership_fingerprint: str
    workspace_count: int
    membership_count: int
    access_evaluation_count: int
    health_status: str
    evidence_id: str = ""

    @classmethod
    def create(
        cls,
        *,
        registry_fingerprint: str,
        membership_fingerprint: str,
        workspace_count: int,
        membership_count: int,
        access_evaluation_count: int,
        health_status: str,
    ) -> WorkspaceEvidence:
        core = {
            "registry_fingerprint": registry_fingerprint,
            "membership_fingerprint": membership_fingerprint,
            "workspace_count": workspace_count,
            "membership_count": membership_count,
            "access_evaluation_count": access_evaluation_count,
            "health_status": health_status,
        }
        return cls(
            registry_fingerprint=registry_fingerprint,
            membership_fingerprint=membership_fingerprint,
            workspace_count=workspace_count,
            membership_count=membership_count,
            access_evaluation_count=access_evaluation_count,
            health_status=health_status,
            evidence_id=f"UCOS-WSEV-{content_hash(core)[:16]}",
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "evidence_id": self.evidence_id,
            "registry_fingerprint": self.registry_fingerprint,
            "membership_fingerprint": self.membership_fingerprint,
            "workspace_count": self.workspace_count,
            "membership_count": self.membership_count,
            "access_evaluation_count": self.access_evaluation_count,
            "health_status": self.health_status,
        }

    def fingerprint(self) -> str:
        return content_hash(self.to_dict())


class WorkspaceService:
    """The governed L3 composition point for the UCOS Workspace Runtime."""

    __slots__ = (
        "_registry",
        "_membership",
        "_authorization",
        "_isolation",
        "_search",
        "_health",
        "_health_registry",
        "_observability",
        "_events",
        "_access_evaluations",
    )

    def __init__(
        self,
        *,
        registry: WorkspaceRegistry,
        membership: MembershipRegistry,
        authorization: AuthorizationService,
        search: WorkspaceSearch,
        health: WorkspaceHealth,
        health_registry: HealthRegistry,
        isolation: IsolationGuard | None = None,
        observability: ObservabilityService | None = None,
        events: EventBus | None = None,
    ) -> None:
        if not isinstance(registry, WorkspaceRegistry):
            raise WorkspaceServiceError("a valid WorkspaceRegistry is required")
        if not isinstance(membership, MembershipRegistry):
            raise WorkspaceServiceError("a valid MembershipRegistry is required")
        if not isinstance(authorization, AuthorizationService):
            raise WorkspaceServiceError("a valid AuthorizationService is required")
        if not isinstance(search, WorkspaceSearch):
            raise WorkspaceServiceError("a valid WorkspaceSearch is required")
        if not isinstance(health, WorkspaceHealth):
            raise WorkspaceServiceError("a valid WorkspaceHealth is required")
        if not isinstance(health_registry, HealthRegistry):
            raise WorkspaceServiceError("a valid HealthRegistry is required")
        if isolation is not None and not isinstance(isolation, IsolationGuard):
            raise WorkspaceServiceError("isolation must be an IsolationGuard when provided")
        if observability is not None and not isinstance(observability, ObservabilityService):
            raise WorkspaceServiceError(
                "observability must be an ObservabilityService when provided"
            )
        if events is not None and not isinstance(events, EventBus):
            raise WorkspaceServiceError("events must be an EventBus when provided")
        self._registry = registry
        self._membership = membership
        self._authorization = authorization
        self._search = search
        self._health = health
        self._health_registry = health_registry
        self._isolation = isolation if isolation is not None else IsolationGuard()
        self._observability = observability
        self._events = events
        self._access_evaluations = 0

    # -- component access -------------------------------------------------------

    @property
    def registry(self) -> WorkspaceRegistry:
        return self._registry

    @property
    def membership(self) -> MembershipRegistry:
        return self._membership

    @property
    def authorization(self) -> AuthorizationService:
        return self._authorization

    @property
    def isolation(self) -> IsolationGuard:
        return self._isolation

    @property
    def health(self) -> WorkspaceHealth:
        return self._health

    @property
    def observability(self) -> ObservabilityService | None:
        return self._observability

    @property
    def access_evaluation_count(self) -> int:
        return self._access_evaluations

    # -- creation ---------------------------------------------------------------

    def create_workspace(
        self,
        session_id: str,
        slug: str,
        name: str,
        *,
        now: int,
        tenant: str | None = None,
        metadata: WorkspaceMetadata | None = None,
    ) -> Workspace:
        """Create a workspace and enroll the creator as OWNER (fail-closed).

        Requires identity CREATE on ``workspace-project-lifecycle`` (with the target
        tenant) and cross-tenant isolation clearance. Raises
        :class:`WorkspaceAccessError` on any denial.
        """
        decision = self._authorization.authorize(
            session_id, WORKSPACE_GROUP, Permission.CREATE, now=now, tenant=tenant, resource=slug
        )
        if not decision.permitted:
            raise WorkspaceAccessError(
                "workspace creation denied", reason=decision.reason, slug=slug
            )
        principal = self._authorization.principals.get(decision.request.principal_id)
        if tenants_isolated(principal.tenant, tenant):
            raise WorkspaceAccessError(
                "cross-tenant workspace creation denied",
                reason="tenant-isolation-violation",
                slug=slug,
            )
        workspace = self._registry.create(
            slug, name, principal.subject, tenant=tenant, metadata=metadata
        )
        self._membership.add(
            workspace.workspace_id,
            principal.principal_id,
            principal.subject,
            MemberRole.OWNER,
            tick=now,
        )
        self._emit(
            WORKSPACE_CREATED_EVENT,
            subject=workspace.workspace_id,
            payload={"slug": workspace.slug, "tenant": workspace.tenant},
        )
        return workspace

    # -- resolution / discovery -------------------------------------------------

    def resolve(self, slug: str, tenant: str | None = None) -> Workspace:
        """Resolve a workspace by slug within a tenant (pure read; fail-closed)."""
        return self._registry.resolve(slug, tenant)

    def discover(
        self, session_id: str, *, now: int, tenant: str | None = None
    ) -> tuple[Workspace, ...]:
        """Discover the workspaces a caller may see (authorized READ + isolation)."""
        principal = self._resolve_principal(session_id, now)
        if principal is None:
            return ()
        decision = self._authorization.authorize_principal(
            principal, WORKSPACE_GROUP, Permission.READ, tenant=tenant
        )
        if not decision.permitted:
            return ()
        return tuple(
            ws for ws in self._registry.discover(tenant) if self._isolation.permits(principal, ws)
        )

    # -- selection / context ----------------------------------------------------

    def select_workspace(self, session_id: str, workspace_id: str, *, now: int) -> WorkspaceContext:
        """Select a workspace and return its runtime context (fail-closed).

        Requires READ access (identity + isolation + membership). Raises
        :class:`WorkspaceAccessError` when access is denied.
        """
        access = self.evaluate_access(session_id, workspace_id, Permission.READ, now=now)
        if not access.granted:
            raise WorkspaceAccessError(
                "workspace selection denied",
                reason=access.reason,
                workspace_id=workspace_id,
            )
        workspace = self._registry.get(workspace_id)
        principal = self._authorization.principals.get(access.principal_id)
        return WorkspaceContext.create(workspace, principal, member_role=access.member_role)

    # -- access evaluation ------------------------------------------------------

    def evaluate_access(
        self, session_id: str, workspace_id: str, permission: Permission, *, now: int
    ) -> WorkspaceAccess:
        """Evaluate composed workspace access (identity ∧ isolation ∧ membership).

        Denials are returned as data (``granted == False``); a malformed request or an
        unknown workspace raises. Every evaluation is emitted as a governed
        ``workspace.access.evaluated`` event (PC-16).
        """
        if not isinstance(permission, Permission):
            raise WorkspaceServiceError("permission must be a Permission")
        workspace = self._registry.get(workspace_id)
        decision = self._authorization.authorize(
            session_id,
            WORKSPACE_GROUP,
            permission,
            now=now,
            tenant=workspace.tenant,
            resource=workspace_id,
        )
        access = self._compose_access(workspace, permission, decision)
        self._access_evaluations += 1
        self._emit(
            WORKSPACE_ACCESS_EVENT,
            subject=access.principal_id,
            payload={
                "workspace_id": workspace_id,
                "permission": permission.value,
                "granted": access.granted,
                "reason": access.reason,
            },
        )
        return access

    def _compose_access(
        self, workspace: Workspace, permission: Permission, decision: AccessDecision
    ) -> WorkspaceAccess:
        if not decision.permitted:
            return WorkspaceAccess.create(
                workspace_id=workspace.workspace_id,
                permission=permission,
                granted=False,
                reason=decision.reason,
                decision=decision,
            )
        principal = self._authorization.principals.get(decision.request.principal_id)
        isolation = self._isolation.evaluate(principal, workspace)
        if not isolation.allowed:
            return WorkspaceAccess.create(
                workspace_id=workspace.workspace_id,
                permission=permission,
                granted=False,
                reason=isolation.reason,
                decision=decision,
            )
        if permission is not Permission.READ and not workspace.is_active:
            return WorkspaceAccess.create(
                workspace_id=workspace.workspace_id,
                permission=permission,
                granted=False,
                reason=f"workspace-{workspace.status.value}",
                decision=decision,
            )
        member = self._membership.member(workspace.workspace_id, principal.principal_id)
        is_admin = self._authorization.permissions.has_permission(
            principal, WORKSPACE_GROUP, Permission.ADMINISTER
        )
        if member is None and not is_admin:
            return WorkspaceAccess.create(
                workspace_id=workspace.workspace_id,
                permission=permission,
                granted=False,
                reason="not-a-member",
                decision=decision,
            )
        return WorkspaceAccess.create(
            workspace_id=workspace.workspace_id,
            permission=permission,
            granted=True,
            reason="granted",
            decision=decision,
            member_role=member.role if member is not None else None,
        )

    # -- membership management --------------------------------------------------

    def add_member(
        self,
        session_id: str,
        workspace_id: str,
        principal_id: str,
        subject: str,
        role: MemberRole,
        *,
        now: int,
    ) -> WorkspaceMember:
        """Add a member to a workspace (requires owner or platform administrator)."""
        workspace = self._registry.get(workspace_id)
        self._require_manager(session_id, workspace, now=now)
        member = self._membership.add(workspace_id, principal_id, subject, role, tick=now)
        self._emit(
            WORKSPACE_MEMBER_ADDED_EVENT,
            subject=workspace_id,
            payload={"principal_id": principal_id, "role": role.value},
        )
        return member

    def remove_member(
        self, session_id: str, workspace_id: str, principal_id: str, *, now: int
    ) -> WorkspaceMember:
        """Remove a member from a workspace (requires owner or platform administrator)."""
        workspace = self._registry.get(workspace_id)
        self._require_manager(session_id, workspace, now=now)
        member = self._membership.remove(workspace_id, principal_id, tick=now)
        self._emit(
            WORKSPACE_MEMBER_REMOVED_EVENT,
            subject=workspace_id,
            payload={"principal_id": principal_id},
        )
        return member

    # -- lifecycle --------------------------------------------------------------

    def transition(
        self, session_id: str, workspace_id: str, target: WorkspaceStatus, *, now: int
    ) -> Workspace:
        """Transition a workspace's lifecycle (requires owner or platform administrator)."""
        workspace = self._registry.get(workspace_id)
        self._require_manager(session_id, workspace, now=now)
        updated = self._registry.transition(workspace_id, target, tick=now)
        self._emit(
            WORKSPACE_LIFECYCLE_EVENT,
            subject=workspace_id,
            payload={"from": workspace.status.value, "to": target.value},
        )
        return updated

    # -- search -----------------------------------------------------------------

    def search(
        self, session_id: str, query: str, *, now: int, tenant: str | None = None
    ) -> WorkspaceSearchResponse:
        """Run an authorization- and isolation-scoped workspace search."""
        return self._search.search(session_id, query, now=now, tenant=tenant)

    # -- health integration -----------------------------------------------------

    def health_report(self) -> dict[str, Any]:
        """The workspace runtime health endpoint (reuses the observability model)."""
        return self._health_registry.endpoint(self._health.probe())

    # -- evidence ---------------------------------------------------------------

    def evidence(self) -> WorkspaceEvidence:
        """Produce deterministic Workspace Evidence over the runtime state."""
        report = self._health_registry.report(self._health.probe())
        return WorkspaceEvidence.create(
            registry_fingerprint=self._registry.fingerprint(),
            membership_fingerprint=self._membership.fingerprint(),
            workspace_count=len(self._registry),
            membership_count=len(self._membership),
            access_evaluation_count=self._access_evaluations,
            health_status=report.status.value,
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "workspace_count": len(self._registry),
            "membership_count": len(self._membership),
            "access_evaluation_count": self._access_evaluations,
            "observability_bound": self._observability is not None,
            "evidence": self.evidence().to_dict(),
        }

    # -- internals --------------------------------------------------------------

    def _require_manager(self, session_id: str, workspace: Workspace, *, now: int):
        """Require the caller be a workspace OWNER or a platform administrator."""
        access = self.evaluate_access(session_id, workspace.workspace_id, Permission.READ, now=now)
        if not access.granted:
            raise WorkspaceAccessError(
                "workspace management denied",
                reason=access.reason,
                workspace_id=workspace.workspace_id,
            )
        principal = self._authorization.principals.get(access.principal_id)
        is_admin = self._authorization.permissions.has_permission(
            principal, WORKSPACE_GROUP, Permission.ADMINISTER
        )
        is_owner = access.member_role is MemberRole.OWNER
        if not (is_admin or is_owner):
            raise WorkspaceAccessError(
                "workspace management requires owner or administrator",
                reason="not-a-manager",
                workspace_id=workspace.workspace_id,
            )
        return principal

    def _resolve_principal(self, session_id: str, now: int):
        try:
            session = self._authorization.sessions.validate(session_id, now)
            return self._authorization.principals.get(session.principal_id)
        except IdentityError:
            return None

    def _emit(self, event_type: str, *, subject: str, payload: dict[str, Any]) -> None:
        if self._events is not None:
            self._events.publish(
                event_type,
                source="platform.workspace.runtime",
                subject=subject,
                payload=payload,
            )


def build_workspace_service(
    *,
    authorization: AuthorizationService,
    observability: ObservabilityService | None = None,
    events: EventBus | None = None,
    registry: WorkspaceRegistry | None = None,
    membership: MembershipRegistry | None = None,
) -> WorkspaceService:
    """Default, registry-driven composition of the Workspace Runtime.

    Wires the workspace registry, membership registry, isolation guard, workspace
    search (over the supplied Identity ``authorization`` service), the workspace health
    probe and a health registry seeded with the workspace health checks, and — when
    supplied — the observability layer and event bus.
    """
    if not isinstance(authorization, AuthorizationService):
        raise WorkspaceServiceError("build_workspace_service requires an AuthorizationService")
    workspace_registry = registry if registry is not None else WorkspaceRegistry()
    membership_registry = membership if membership is not None else MembershipRegistry()
    isolation = IsolationGuard()
    search = WorkspaceSearch(workspace_registry, authorization, isolation=isolation)
    health = WorkspaceHealth(workspace_registry, membership_registry)
    health_registry = HealthRegistry()
    for check in workspace_health_checks():
        health_registry.register(check)
    return WorkspaceService(
        registry=workspace_registry,
        membership=membership_registry,
        authorization=authorization,
        search=search,
        health=health,
        health_registry=health_registry,
        isolation=isolation,
        observability=observability,
        events=events,
    )


__all__ = [
    "WORKSPACE_CREATED_EVENT",
    "WORKSPACE_MEMBER_ADDED_EVENT",
    "WORKSPACE_MEMBER_REMOVED_EVENT",
    "WORKSPACE_LIFECYCLE_EVENT",
    "WORKSPACE_ACCESS_EVENT",
    "WorkspaceAccess",
    "WorkspaceEvidence",
    "WorkspaceService",
    "build_workspace_service",
]
