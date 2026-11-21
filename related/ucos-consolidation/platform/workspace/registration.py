"""EC2-TASK-000084 — Workspace Registry (EC2-EPIC-004).

The deterministic, append-only store of workspaces — the runtime home of workspace
**creation**, **registration**, **discovery**, and **resolution**. A workspace's
identity is its ``slug`` within its ``tenant`` (content-addressed ``workspace_id``), so
registration is idempotent-safe and fail-closed on genuine duplicates. Mutable facets
are applied immutably: a lifecycle transition or metadata update replaces the stored
:class:`~platform.workspace.contracts.Workspace` with a new immutable record (the id is
preserved) and records an ordered, append-only
:class:`~platform.workspace.lifecycle.WorkspaceEvent`, so the registry's history is
reproducible and auditable (OP-C3). The registry holds *records only* — it enforces no
authorization (that is the Identity Layer) and no isolation (that is the isolation
guard); it is the substrate the workspace service composes.
"""

from __future__ import annotations

from platform.foundation.contracts import content_hash
from platform.workspace.contracts import Workspace, WorkspaceStatus
from platform.workspace.errors import WorkspaceRegistryError
from platform.workspace.lifecycle import WorkspaceEvent, validate_transition
from platform.workspace.metadata import WorkspaceMetadata
from typing import Any


class WorkspaceRegistry:
    """A deterministic, append-only registry of workspaces (create/resolve/discover)."""

    __slots__ = ("_by_id", "_log")

    def __init__(self) -> None:
        self._by_id: dict[str, Workspace] = {}
        self._log: list[WorkspaceEvent] = []

    def register(self, workspace: Workspace) -> Workspace:
        """Register a workspace record (fail-closed on duplicate id)."""
        if not isinstance(workspace, Workspace):
            raise WorkspaceRegistryError("register requires a Workspace")
        if workspace.workspace_id in self._by_id:
            raise WorkspaceRegistryError(
                "workspace already registered",
                workspace_id=workspace.workspace_id,
                slug=workspace.slug,
            )
        self._by_id[workspace.workspace_id] = workspace
        return workspace

    def create(
        self,
        slug: str,
        name: str,
        owner_subject: str,
        *,
        tenant: str | None = None,
        metadata: WorkspaceMetadata | None = None,
    ) -> Workspace:
        """Build and register a new ACTIVE workspace (fail-closed on duplicate)."""
        workspace = Workspace.create(slug, name, owner_subject, tenant=tenant, metadata=metadata)
        return self.register(workspace)

    def __contains__(self, workspace_id: str) -> bool:
        return workspace_id in self._by_id

    def __len__(self) -> int:
        return len(self._by_id)

    def get(self, workspace_id: str) -> Workspace:
        """Resolve a workspace by id (fail-closed on absent)."""
        workspace = self._by_id.get(workspace_id)
        if workspace is None:
            raise WorkspaceRegistryError("no such workspace", workspace_id=workspace_id)
        return workspace

    def exists(self, slug: str, tenant: str | None = None) -> bool:
        """True iff a workspace with ``slug`` exists in ``tenant``."""
        probe = Workspace.create(slug, slug, "probe", tenant=tenant)
        return probe.workspace_id in self._by_id

    def resolve(self, slug: str, tenant: str | None = None) -> Workspace:
        """Resolve a workspace by its ``slug`` within ``tenant`` (fail-closed)."""
        probe = Workspace.create(slug, slug, "probe", tenant=tenant)
        workspace = self._by_id.get(probe.workspace_id)
        if workspace is None:
            raise WorkspaceRegistryError("no such workspace", slug=probe.slug, tenant=tenant)
        return workspace

    @property
    def ids(self) -> tuple[str, ...]:
        """Every registered workspace id in stable (sorted) order."""
        return tuple(sorted(self._by_id))

    def all(self) -> tuple[Workspace, ...]:
        """Every registered workspace in stable (id) order."""
        return tuple(self._by_id[wid] for wid in self.ids)

    def discover(self, tenant: str | None = None) -> tuple[Workspace, ...]:
        """Discover workspaces visible to ``tenant`` in stable order.

        ``tenant is None`` returns every workspace; a specified tenant returns that
        tenant's workspaces plus every untenanted (global) workspace. This is a pure
        read view — authorization and isolation are applied by the service.
        """
        if tenant is None:
            return self.all()
        return tuple(ws for ws in self.all() if ws.tenant == tenant or ws.tenant is None)

    def transition(self, workspace_id: str, target: WorkspaceStatus, *, tick: int) -> Workspace:
        """Apply a lifecycle transition (fail-closed) and record the event."""
        workspace = self.get(workspace_id)
        validate_transition(workspace.status, target)
        updated = workspace.with_status(target)
        self._by_id[workspace_id] = updated
        self._log.append(
            WorkspaceEvent(
                sequence=len(self._log),
                workspace_id=workspace_id,
                from_status=workspace.status,
                to_status=target,
                tick=tick,
            )
        )
        return updated

    def update_metadata(self, workspace_id: str, metadata: WorkspaceMetadata) -> Workspace:
        """Replace a workspace's metadata immutably (the id/status are preserved)."""
        workspace = self.get(workspace_id)
        updated = workspace.with_metadata(metadata)
        self._by_id[workspace_id] = updated
        return updated

    @property
    def events(self) -> tuple[WorkspaceEvent, ...]:
        """An immutable snapshot of the append-only lifecycle event log (in order)."""
        return tuple(self._log)

    def to_dict(self) -> dict[str, Any]:
        return {
            "workspace_count": len(self._by_id),
            "workspaces": [self._by_id[wid].to_dict() for wid in self.ids],
        }

    def fingerprint(self) -> str:
        return content_hash(self.to_dict())


__all__ = ["WorkspaceRegistry"]
