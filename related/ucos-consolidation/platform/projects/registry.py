"""EC2-TASK-000091 — Project Registry (EC2-EPIC-005).

The deterministic, append-only store of projects — the runtime home of project
**creation**, **registration**, **discovery**, and **resolution**. A project's
identity is its ``slug`` within its parent ``workspace_id`` (content-addressed
``project_id``), so registration is idempotent-safe and fail-closed on genuine
duplicates. Mutable facets are applied immutably: a lifecycle transition or metadata
update replaces the stored :class:`~platform.projects.contracts.Project` with a new
immutable record (the id is preserved) and records an ordered, append-only
:class:`~platform.projects.lifecycle.ProjectEvent`, so the registry's history is
reproducible and auditable (OP-C3). The registry holds *records only* — it enforces
no authorization (that is the Identity Layer), no isolation (the reused workspace
isolation rule), and it does not resolve the parent workspace (the service binds it);
it is the substrate the project service composes.
"""

from __future__ import annotations

from platform.foundation.contracts import content_hash
from platform.projects.contracts import Project, ProjectStatus
from platform.projects.errors import ProjectRegistryError
from platform.projects.lifecycle import ProjectEvent, validate_transition
from platform.projects.metadata import ProjectMetadata
from typing import Any


class ProjectRegistry:
    """A deterministic, append-only registry of projects (create/resolve/discover)."""

    __slots__ = ("_by_id", "_log")

    def __init__(self) -> None:
        self._by_id: dict[str, Project] = {}
        self._log: list[ProjectEvent] = []

    def register(self, project: Project) -> Project:
        """Register a project record (fail-closed on duplicate id)."""
        if not isinstance(project, Project):
            raise ProjectRegistryError("register requires a Project")
        if project.project_id in self._by_id:
            raise ProjectRegistryError(
                "project already registered",
                project_id=project.project_id,
                slug=project.slug,
            )
        self._by_id[project.project_id] = project
        return project

    def create(
        self,
        slug: str,
        name: str,
        workspace_id: str,
        owner_subject: str,
        *,
        tenant: str | None = None,
        metadata: ProjectMetadata | None = None,
    ) -> Project:
        """Build and register a new ACTIVE project (fail-closed on duplicate)."""
        project = Project.create(
            slug, name, workspace_id, owner_subject, tenant=tenant, metadata=metadata
        )
        return self.register(project)

    def __contains__(self, project_id: str) -> bool:
        return project_id in self._by_id

    def __len__(self) -> int:
        return len(self._by_id)

    def get(self, project_id: str) -> Project:
        """Resolve a project by id (fail-closed on absent)."""
        project = self._by_id.get(project_id)
        if project is None:
            raise ProjectRegistryError("no such project", project_id=project_id)
        return project

    def exists(self, slug: str, workspace_id: str) -> bool:
        """True iff a project with ``slug`` exists in ``workspace_id``."""
        probe = Project.create(slug, slug, workspace_id, "probe")
        return probe.project_id in self._by_id

    def resolve(self, slug: str, workspace_id: str) -> Project:
        """Resolve a project by its ``slug`` within ``workspace_id`` (fail-closed)."""
        probe = Project.create(slug, slug, workspace_id, "probe")
        project = self._by_id.get(probe.project_id)
        if project is None:
            raise ProjectRegistryError(
                "no such project", slug=probe.slug, workspace_id=workspace_id
            )
        return project

    @property
    def ids(self) -> tuple[str, ...]:
        """Every registered project id in stable (sorted) order."""
        return tuple(sorted(self._by_id))

    def all(self) -> tuple[Project, ...]:
        """Every registered project in stable (id) order."""
        return tuple(self._by_id[pid] for pid in self.ids)

    def discover(
        self, *, workspace_id: str | None = None, tenant: str | None = None
    ) -> tuple[Project, ...]:
        """Discover projects, optionally scoped by workspace and/or tenant (stable order).

        This is a pure read view — authorization and isolation are applied by the
        service. ``workspace_id`` restricts to a single parent workspace; ``tenant``
        (when set) returns that tenant's projects plus every untenanted (global)
        project (mirrors the workspace discovery semantics).
        """
        projects = self.all()
        if workspace_id is not None:
            projects = tuple(p for p in projects if p.workspace_id == workspace_id)
        if tenant is not None:
            projects = tuple(p for p in projects if p.tenant == tenant or p.tenant is None)
        return projects

    def transition(self, project_id: str, target: ProjectStatus, *, tick: int) -> Project:
        """Apply a lifecycle transition (fail-closed) and record the event."""
        project = self.get(project_id)
        validate_transition(project.status, target)
        updated = project.with_status(target)
        self._by_id[project_id] = updated
        self._log.append(
            ProjectEvent(
                sequence=len(self._log),
                project_id=project_id,
                from_status=project.status,
                to_status=target,
                tick=tick,
            )
        )
        return updated

    def update_metadata(self, project_id: str, metadata: ProjectMetadata) -> Project:
        """Replace a project's metadata immutably (the id/status are preserved)."""
        project = self.get(project_id)
        updated = project.with_metadata(metadata)
        self._by_id[project_id] = updated
        return updated

    @property
    def events(self) -> tuple[ProjectEvent, ...]:
        """An immutable snapshot of the append-only lifecycle event log (in order)."""
        return tuple(self._log)

    def to_dict(self) -> dict[str, Any]:
        return {
            "project_count": len(self._by_id),
            "projects": [self._by_id[pid].to_dict() for pid in self.ids],
        }

    def fingerprint(self) -> str:
        return content_hash(self.to_dict())


__all__ = ["ProjectRegistry"]
