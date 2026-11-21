"""EC2-TASK-000095 — Project Service (EC2-EPIC-005).

The single, governed **project runtime composition point** (L3 Application of the
Program architecture) that composes the whole Project Management Runtime into one
entry point — the project half of the "workspace & project lifecycle" surface:

    ProjectRegistry · AssociationRegistry · ProjectSearch · ProjectHealth ·
    (reused) AuthorizationService · WorkspaceRegistry · ObservabilityService

It is a strictly **additive** layer: it authorizes only through the certified Identity
Layer (L7) on the existing ``workspace-project-lifecycle`` capability group — **no
duplicate authorization or identity logic, no new authority, no new capability
group** — observes only through the Observability Layer (L8), reuses the Foundation
registries/events (L4/L6), and binds each project to a parent workspace through the
certified Workspace Runtime (L3) **by reference**. It re-implements none of them,
modifies none of them, resolves no downstream (blueprint/request/artifact) runtime,
and writes nothing to the certified corpus (DP-03).

Every project access is fail-closed and composes gates — **identity authorization**
(RBAC §3.2), **tenant/workspace isolation** (the reused rule, P3), and — for mutating
actions — **owner/administrator scoping** — so cross-tenant access is refused in 100%
of cases. Because every governed action is published onto the Foundation event bus,
it is captured by observability as append-only audit (PC-16 / OP-C3).

The service is deterministic: the same identity registrations, workspaces, projects,
associations, and ordered sequence of calls yield the same :class:`ProjectEvidence`
fingerprint (P5). :func:`build_project_service` provides the default wiring;
:func:`~platform.projects.bootstrap.bootstrap_projects` composes it onto a
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
from platform.projects.associations import AssociationRegistry
from platform.projects.context import ProjectContext
from platform.projects.contracts import (
    MUTATING_ACTIONS,
    PROJECT_GROUP,
    AssociationKind,
    Project,
    ProjectAction,
    ProjectAssociation,
    ProjectStatus,
    permission_for,
)
from platform.projects.errors import ProjectAccessError, ProjectServiceError
from platform.projects.health import ProjectHealth, project_health_checks
from platform.projects.metadata import ProjectMetadata
from platform.projects.registry import ProjectRegistry
from platform.projects.search import ProjectSearch, ProjectSearchResponse
from platform.projects.status import DerivedProjectStatus, derive_status
from platform.workspace.isolation import tenants_isolated
from platform.workspace.registration import WorkspaceRegistry
from typing import Any

#: Governed events published onto the Foundation event bus (observed as PC-16).
PROJECT_CREATED_EVENT = "project.created"
PROJECT_LIFECYCLE_EVENT = "project.lifecycle.transitioned"
PROJECT_ASSOCIATION_ADDED_EVENT = "project.association.added"
PROJECT_ASSOCIATION_REMOVED_EVENT = "project.association.removed"
PROJECT_ACCESS_EVENT = "project.access.evaluated"


@dataclass(frozen=True, slots=True)
class ProjectAccess:
    """An immutable, content-addressed project access decision (fail-closed).

    Composes identity authorization, tenant/workspace isolation, and (for mutating
    actions) owner/administrator scoping into a single verdict for one
    ``(principal, project, action)`` request.
    """

    project_id: str
    principal_id: str
    action: ProjectAction
    permission: Permission
    granted: bool
    reason: str
    is_owner: bool
    decision: AccessDecision
    access_id: str = ""

    @classmethod
    def create(
        cls,
        *,
        project_id: str,
        action: ProjectAction,
        permission: Permission,
        granted: bool,
        reason: str,
        decision: AccessDecision,
        is_owner: bool = False,
    ) -> ProjectAccess:
        principal_id = decision.request.principal_id
        core = {
            "project_id": project_id,
            "principal_id": principal_id,
            "action": action.value,
            "permission": permission.value,
            "granted": granted,
            "reason": reason,
            "is_owner": is_owner,
        }
        return cls(
            project_id=project_id,
            principal_id=principal_id,
            action=action,
            permission=permission,
            granted=granted,
            reason=reason,
            is_owner=is_owner,
            decision=decision,
            access_id=f"UCOS-PACC-{content_hash(core)[:16]}",
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "access_id": self.access_id,
            "project_id": self.project_id,
            "principal_id": self.principal_id,
            "action": self.action.value,
            "permission": self.permission.value,
            "granted": self.granted,
            "reason": self.reason,
            "is_owner": self.is_owner,
            "decision": self.decision.to_dict(),
        }


@dataclass(frozen=True, slots=True)
class ProjectEvidence:
    """A deterministic, content-addressed record of project runtime state (evidence)."""

    registry_fingerprint: str
    associations_fingerprint: str
    project_count: int
    association_count: int
    access_evaluation_count: int
    health_status: str
    evidence_id: str = ""

    @classmethod
    def create(
        cls,
        *,
        registry_fingerprint: str,
        associations_fingerprint: str,
        project_count: int,
        association_count: int,
        access_evaluation_count: int,
        health_status: str,
    ) -> ProjectEvidence:
        core = {
            "registry_fingerprint": registry_fingerprint,
            "associations_fingerprint": associations_fingerprint,
            "project_count": project_count,
            "association_count": association_count,
            "access_evaluation_count": access_evaluation_count,
            "health_status": health_status,
        }
        return cls(
            registry_fingerprint=registry_fingerprint,
            associations_fingerprint=associations_fingerprint,
            project_count=project_count,
            association_count=association_count,
            access_evaluation_count=access_evaluation_count,
            health_status=health_status,
            evidence_id=f"UCOS-PEVT-{content_hash(core)[:16]}",
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "evidence_id": self.evidence_id,
            "registry_fingerprint": self.registry_fingerprint,
            "associations_fingerprint": self.associations_fingerprint,
            "project_count": self.project_count,
            "association_count": self.association_count,
            "access_evaluation_count": self.access_evaluation_count,
            "health_status": self.health_status,
        }

    def fingerprint(self) -> str:
        return content_hash(self.to_dict())


class ProjectService:
    """The governed L3 composition point for the UCOS Project Management Runtime."""

    __slots__ = (
        "_registry",
        "_associations",
        "_authorization",
        "_workspaces",
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
        registry: ProjectRegistry,
        associations: AssociationRegistry,
        authorization: AuthorizationService,
        workspaces: WorkspaceRegistry,
        search: ProjectSearch,
        health: ProjectHealth,
        health_registry: HealthRegistry,
        observability: ObservabilityService | None = None,
        events: EventBus | None = None,
    ) -> None:
        if not isinstance(registry, ProjectRegistry):
            raise ProjectServiceError("a valid ProjectRegistry is required")
        if not isinstance(associations, AssociationRegistry):
            raise ProjectServiceError("a valid AssociationRegistry is required")
        if not isinstance(authorization, AuthorizationService):
            raise ProjectServiceError("a valid AuthorizationService is required")
        if not isinstance(workspaces, WorkspaceRegistry):
            raise ProjectServiceError("a valid WorkspaceRegistry is required")
        if not isinstance(search, ProjectSearch):
            raise ProjectServiceError("a valid ProjectSearch is required")
        if not isinstance(health, ProjectHealth):
            raise ProjectServiceError("a valid ProjectHealth is required")
        if not isinstance(health_registry, HealthRegistry):
            raise ProjectServiceError("a valid HealthRegistry is required")
        if observability is not None and not isinstance(observability, ObservabilityService):
            raise ProjectServiceError("observability must be an ObservabilityService when provided")
        if events is not None and not isinstance(events, EventBus):
            raise ProjectServiceError("events must be an EventBus when provided")
        self._registry = registry
        self._associations = associations
        self._authorization = authorization
        self._workspaces = workspaces
        self._search = search
        self._health = health
        self._health_registry = health_registry
        self._observability = observability
        self._events = events
        self._access_evaluations = 0

    # -- component access -------------------------------------------------------

    @property
    def registry(self) -> ProjectRegistry:
        return self._registry

    @property
    def associations(self) -> AssociationRegistry:
        return self._associations

    @property
    def authorization(self) -> AuthorizationService:
        return self._authorization

    @property
    def workspaces(self) -> WorkspaceRegistry:
        return self._workspaces

    @property
    def health(self) -> ProjectHealth:
        return self._health

    @property
    def observability(self) -> ObservabilityService | None:
        return self._observability

    @property
    def access_evaluation_count(self) -> int:
        return self._access_evaluations

    # -- creation ---------------------------------------------------------------

    def create_project(
        self,
        session_id: str,
        slug: str,
        name: str,
        workspace_id: str,
        *,
        now: int,
        metadata: ProjectMetadata | None = None,
    ) -> Project:
        """Create a project scoped to a workspace and record the creator as owner.

        Requires identity CREATE on ``workspace-project-lifecycle`` (with the parent
        workspace's tenant), an ACTIVE parent workspace, and cross-tenant isolation
        clearance. Raises :class:`ProjectAccessError` on any denial.
        """
        workspace = self._workspaces.get(workspace_id)
        if not workspace.is_active:
            raise ProjectAccessError(
                "parent workspace is not active",
                reason=f"workspace-{workspace.status.value}",
                workspace_id=workspace_id,
            )
        decision = self._authorization.authorize(
            session_id,
            PROJECT_GROUP,
            Permission.CREATE,
            now=now,
            tenant=workspace.tenant,
            resource=slug,
        )
        if not decision.permitted:
            raise ProjectAccessError("project creation denied", reason=decision.reason, slug=slug)
        principal = self._authorization.principals.get(decision.request.principal_id)
        if tenants_isolated(principal.tenant, workspace.tenant):
            raise ProjectAccessError(
                "cross-tenant project creation denied",
                reason="tenant-isolation-violation",
                slug=slug,
            )
        project = self._registry.create(
            slug,
            name,
            workspace_id,
            principal.subject,
            tenant=workspace.tenant,
            metadata=metadata,
        )
        self._emit(
            PROJECT_CREATED_EVENT,
            subject=project.project_id,
            payload={
                "slug": project.slug,
                "workspace_id": workspace_id,
                "tenant": project.tenant,
            },
        )
        return project

    # -- resolution / discovery -------------------------------------------------

    def resolve(self, slug: str, workspace_id: str) -> Project:
        """Resolve a project by slug within a workspace (pure read; fail-closed)."""
        return self._registry.resolve(slug, workspace_id)

    def discover(
        self,
        session_id: str,
        *,
        now: int,
        tenant: str | None = None,
        workspace_id: str | None = None,
    ) -> tuple[Project, ...]:
        """Discover the projects a caller may see (authorized READ + isolation)."""
        principal = self._resolve_principal(session_id, now)
        if principal is None:
            return ()
        decision = self._authorization.authorize_principal(
            principal, PROJECT_GROUP, Permission.READ, tenant=tenant
        )
        if not decision.permitted:
            return ()
        return tuple(
            project
            for project in self._registry.discover(workspace_id=workspace_id, tenant=tenant)
            if not tenants_isolated(principal.tenant, project.tenant)
        )

    # -- selection / context ----------------------------------------------------

    def select_project(self, session_id: str, project_id: str, *, now: int) -> ProjectContext:
        """Select a project and return its runtime context (fail-closed).

        Requires INSPECT (READ) access (identity + isolation). Raises
        :class:`ProjectAccessError` when access is denied.
        """
        access = self.evaluate_access(session_id, project_id, ProjectAction.INSPECT, now=now)
        if not access.granted:
            raise ProjectAccessError(
                "project selection denied",
                reason=access.reason,
                project_id=project_id,
            )
        project = self._registry.get(project_id)
        principal = self._authorization.principals.get(access.principal_id)
        return ProjectContext.create(project, principal, is_owner=access.is_owner)

    # -- access evaluation ------------------------------------------------------

    def evaluate_access(
        self, session_id: str, project_id: str, action: ProjectAction, *, now: int
    ) -> ProjectAccess:
        """Evaluate composed project access (identity ∧ isolation ∧ owner-scoping).

        Denials are returned as data (``granted == False``); a malformed request or an
        unknown project raises. Every evaluation is emitted as a governed
        ``project.access.evaluated`` event (PC-16).
        """
        if not isinstance(action, ProjectAction):
            raise ProjectServiceError("action must be a ProjectAction")
        permission = permission_for(action)
        project = self._registry.get(project_id)
        decision = self._authorization.authorize(
            session_id,
            PROJECT_GROUP,
            permission,
            now=now,
            tenant=project.tenant,
            resource=project_id,
        )
        access = self._compose_access(project, action, permission, decision)
        self._access_evaluations += 1
        self._emit(
            PROJECT_ACCESS_EVENT,
            subject=access.principal_id,
            payload={
                "project_id": project_id,
                "action": action.value,
                "granted": access.granted,
                "reason": access.reason,
            },
        )
        return access

    def _compose_access(
        self,
        project: Project,
        action: ProjectAction,
        permission: Permission,
        decision: AccessDecision,
    ) -> ProjectAccess:
        if not decision.permitted:
            return ProjectAccess.create(
                project_id=project.project_id,
                action=action,
                permission=permission,
                granted=False,
                reason=decision.reason,
                decision=decision,
            )
        principal = self._authorization.principals.get(decision.request.principal_id)
        if tenants_isolated(principal.tenant, project.tenant):
            return ProjectAccess.create(
                project_id=project.project_id,
                action=action,
                permission=permission,
                granted=False,
                reason="tenant-isolation-violation",
                decision=decision,
            )
        is_owner = principal.subject == project.owner_subject
        if action in MUTATING_ACTIONS:
            if project.is_terminal:
                return ProjectAccess.create(
                    project_id=project.project_id,
                    action=action,
                    permission=permission,
                    granted=False,
                    reason="project-archived",
                    decision=decision,
                    is_owner=is_owner,
                )
            is_admin = self._authorization.permissions.has_permission(
                principal, PROJECT_GROUP, Permission.ADMINISTER
            )
            if not (is_owner or is_admin):
                return ProjectAccess.create(
                    project_id=project.project_id,
                    action=action,
                    permission=permission,
                    granted=False,
                    reason="not-an-owner",
                    decision=decision,
                    is_owner=is_owner,
                )
        return ProjectAccess.create(
            project_id=project.project_id,
            action=action,
            permission=permission,
            granted=True,
            reason="granted",
            decision=decision,
            is_owner=is_owner,
        )

    # -- lifecycle --------------------------------------------------------------

    def transition(
        self, session_id: str, project_id: str, target: ProjectStatus, *, now: int
    ) -> Project:
        """Transition a project's lifecycle (requires owner or platform administrator)."""
        access = self.evaluate_access(
            session_id, project_id, ProjectAction.TRANSITION_LIFECYCLE, now=now
        )
        if not access.granted:
            raise ProjectAccessError(
                "project lifecycle transition denied",
                reason=access.reason,
                project_id=project_id,
            )
        previous = self._registry.get(project_id)
        updated = self._registry.transition(project_id, target, tick=now)
        self._emit(
            PROJECT_LIFECYCLE_EVENT,
            subject=project_id,
            payload={"from": previous.status.value, "to": target.value},
        )
        return updated

    # -- associations -----------------------------------------------------------

    def add_association(
        self,
        session_id: str,
        project_id: str,
        kind: AssociationKind,
        ref_id: str,
        *,
        now: int,
    ) -> ProjectAssociation:
        """Bind a typed reference to a project (requires owner or administrator)."""
        access = self.evaluate_access(
            session_id, project_id, ProjectAction.ADD_ASSOCIATION, now=now
        )
        if not access.granted:
            raise ProjectAccessError(
                "project association denied",
                reason=access.reason,
                project_id=project_id,
            )
        association = self._associations.add(project_id, kind, ref_id, tick=now)
        self._emit(
            PROJECT_ASSOCIATION_ADDED_EVENT,
            subject=project_id,
            payload={"kind": kind.value, "ref_id": ref_id},
        )
        return association

    def remove_association(
        self,
        session_id: str,
        project_id: str,
        kind: AssociationKind,
        ref_id: str,
        *,
        now: int,
    ) -> ProjectAssociation:
        """Unbind a typed reference from a project (requires owner or administrator)."""
        access = self.evaluate_access(
            session_id, project_id, ProjectAction.REMOVE_ASSOCIATION, now=now
        )
        if not access.granted:
            raise ProjectAccessError(
                "project association removal denied",
                reason=access.reason,
                project_id=project_id,
            )
        association = self._associations.remove(project_id, kind, ref_id, tick=now)
        self._emit(
            PROJECT_ASSOCIATION_REMOVED_EVENT,
            subject=project_id,
            payload={"kind": kind.value, "ref_id": ref_id},
        )
        return association

    # -- status derivation ------------------------------------------------------

    def status_of(self, project_id: str) -> DerivedProjectStatus:
        """Derive a deterministic status for a project (pure read; fail-closed)."""
        project = self._registry.get(project_id)
        return derive_status(project, self._associations.associations_of(project_id))

    # -- search -----------------------------------------------------------------

    def search(
        self,
        session_id: str,
        query: str,
        *,
        now: int,
        tenant: str | None = None,
        workspace_id: str | None = None,
    ) -> ProjectSearchResponse:
        """Run an authorization- and isolation-scoped project search."""
        return self._search.search(
            session_id, query, now=now, tenant=tenant, workspace_id=workspace_id
        )

    # -- health integration -----------------------------------------------------

    def health_report(self) -> dict[str, Any]:
        """The project runtime health endpoint (reuses the observability model)."""
        return self._health_registry.endpoint(self._health.probe())

    # -- evidence ---------------------------------------------------------------

    def evidence(self) -> ProjectEvidence:
        """Produce deterministic Project Evidence over the runtime state."""
        report = self._health_registry.report(self._health.probe())
        return ProjectEvidence.create(
            registry_fingerprint=self._registry.fingerprint(),
            associations_fingerprint=self._associations.fingerprint(),
            project_count=len(self._registry),
            association_count=len(self._associations),
            access_evaluation_count=self._access_evaluations,
            health_status=report.status.value,
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "project_count": len(self._registry),
            "association_count": len(self._associations),
            "access_evaluation_count": self._access_evaluations,
            "observability_bound": self._observability is not None,
            "evidence": self.evidence().to_dict(),
        }

    # -- internals --------------------------------------------------------------

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
                source="platform.projects.runtime",
                subject=subject,
                payload=payload,
            )


def build_project_service(
    *,
    authorization: AuthorizationService,
    workspaces: WorkspaceRegistry,
    observability: ObservabilityService | None = None,
    events: EventBus | None = None,
    registry: ProjectRegistry | None = None,
    associations: AssociationRegistry | None = None,
) -> ProjectService:
    """Default, registry-driven composition of the Project Management Runtime.

    Wires the project registry, association registry, project search (over the supplied
    Identity ``authorization`` service), the project health probe and a health registry
    seeded with the project health checks, the reused workspace registry (parent-scope
    binding + isolation), and — when supplied — the observability layer and event bus.
    """
    if not isinstance(authorization, AuthorizationService):
        raise ProjectServiceError("build_project_service requires an AuthorizationService")
    if not isinstance(workspaces, WorkspaceRegistry):
        raise ProjectServiceError("build_project_service requires a WorkspaceRegistry")
    project_registry = registry if registry is not None else ProjectRegistry()
    association_registry = associations if associations is not None else AssociationRegistry()
    search = ProjectSearch(project_registry, authorization)
    health = ProjectHealth(project_registry, association_registry)
    health_registry = HealthRegistry()
    for check in project_health_checks():
        health_registry.register(check)
    return ProjectService(
        registry=project_registry,
        associations=association_registry,
        authorization=authorization,
        workspaces=workspaces,
        search=search,
        health=health,
        health_registry=health_registry,
        observability=observability,
        events=events,
    )


__all__ = [
    "PROJECT_CREATED_EVENT",
    "PROJECT_LIFECYCLE_EVENT",
    "PROJECT_ASSOCIATION_ADDED_EVENT",
    "PROJECT_ASSOCIATION_REMOVED_EVENT",
    "PROJECT_ACCESS_EVENT",
    "ProjectAccess",
    "ProjectEvidence",
    "ProjectService",
    "build_project_service",
]
