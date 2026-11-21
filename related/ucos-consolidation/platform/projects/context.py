"""EC2-TASK-000093 — Project Context (EC2-EPIC-005).

The immutable, content-addressed **runtime context** produced when a principal
successfully selects/resolves a project: the binding of *who* (principal + subject)
to *where* (project + parent workspace + tenant) and *in what standing* (project
owner or not). It is the value a downstream runtime surface (blueprint catalog,
generation requests, …) carries to operate **within** a project's scope. The context
is derived only from an already-authorized, isolation-cleared selection — it grants
nothing on its own and holds no secret material (SEC-04). It is deterministic:
identical bindings yield an identical ``context_id``.
"""

from __future__ import annotations

from dataclasses import dataclass
from platform.foundation.contracts import content_hash
from platform.foundation.identity import Principal
from platform.projects.contracts import Project, ProjectStatus
from platform.projects.errors import ProjectServiceError
from typing import Any


@dataclass(frozen=True, slots=True)
class ProjectContext:
    """An immutable, content-addressed project runtime context binding."""

    context_id: str
    project_id: str
    project_slug: str
    project_status: ProjectStatus
    workspace_id: str
    principal_id: str
    subject: str
    tenant: str | None
    is_owner: bool

    @classmethod
    def create(
        cls,
        project: Project,
        principal: Principal,
        *,
        is_owner: bool = False,
    ) -> ProjectContext:
        """Build the deterministic runtime context for a resolved selection."""
        if not isinstance(project, Project):
            raise ProjectServiceError("project context requires a Project")
        if not isinstance(principal, Principal):
            raise ProjectServiceError("project context requires a Principal")
        if not isinstance(is_owner, bool):
            raise ProjectServiceError("is_owner must be a bool")
        core = {
            "project_id": project.project_id,
            "project_status": project.status.value,
            "workspace_id": project.workspace_id,
            "principal_id": principal.principal_id,
            "tenant": project.tenant,
            "is_owner": is_owner,
        }
        return cls(
            context_id=f"UCOS-PCTX-{content_hash(core)[:16]}",
            project_id=project.project_id,
            project_slug=project.slug,
            project_status=project.status,
            workspace_id=project.workspace_id,
            principal_id=principal.principal_id,
            subject=principal.subject,
            tenant=project.tenant,
            is_owner=is_owner,
        )

    @property
    def is_active(self) -> bool:
        """True iff the bound project is ACTIVE."""
        return self.project_status is ProjectStatus.ACTIVE

    def to_dict(self) -> dict[str, Any]:
        return {
            "context_id": self.context_id,
            "project_id": self.project_id,
            "project_slug": self.project_slug,
            "project_status": self.project_status.value,
            "workspace_id": self.workspace_id,
            "principal_id": self.principal_id,
            "subject": self.subject,
            "tenant": self.tenant,
            "is_owner": self.is_owner,
        }

    def fingerprint(self) -> str:
        return content_hash(self.to_dict())


__all__ = ["ProjectContext"]
