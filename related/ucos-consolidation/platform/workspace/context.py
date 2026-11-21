"""EC2-TASK-000086 — Workspace Context (EC2-EPIC-004).

The immutable, content-addressed **runtime context** produced when a principal
successfully selects/resolves a workspace: the binding of *who* (principal + subject)
to *where* (workspace + tenant) and *in what collaboration role* (member role). It is
the value a downstream runtime surface (projects, generation requests, …) carries to
operate **within** a workspace's isolation boundary. The context is derived only from
an already-authorized, isolation-cleared selection — it grants nothing on its own and
holds no secret material (SEC-04). It is deterministic: identical bindings yield an
identical ``context_id``.
"""

from __future__ import annotations

from dataclasses import dataclass
from platform.foundation.contracts import content_hash
from platform.foundation.identity import Principal
from platform.workspace.contracts import MemberRole, Workspace, WorkspaceStatus
from platform.workspace.errors import WorkspaceServiceError
from typing import Any


@dataclass(frozen=True, slots=True)
class WorkspaceContext:
    """An immutable, content-addressed workspace runtime context binding."""

    context_id: str
    workspace_id: str
    workspace_slug: str
    workspace_status: WorkspaceStatus
    principal_id: str
    subject: str
    tenant: str | None
    member_role: MemberRole | None

    @classmethod
    def create(
        cls,
        workspace: Workspace,
        principal: Principal,
        *,
        member_role: MemberRole | None = None,
    ) -> WorkspaceContext:
        """Build the deterministic runtime context for a resolved selection."""
        if not isinstance(workspace, Workspace):
            raise WorkspaceServiceError("workspace context requires a Workspace")
        if not isinstance(principal, Principal):
            raise WorkspaceServiceError("workspace context requires a Principal")
        if member_role is not None and not isinstance(member_role, MemberRole):
            raise WorkspaceServiceError("member_role must be a MemberRole when provided")
        core = {
            "workspace_id": workspace.workspace_id,
            "workspace_status": workspace.status.value,
            "principal_id": principal.principal_id,
            "tenant": workspace.tenant,
            "member_role": member_role.value if member_role else None,
        }
        return cls(
            context_id=f"UCOS-WCTX-{content_hash(core)[:16]}",
            workspace_id=workspace.workspace_id,
            workspace_slug=workspace.slug,
            workspace_status=workspace.status,
            principal_id=principal.principal_id,
            subject=principal.subject,
            tenant=workspace.tenant,
            member_role=member_role,
        )

    @property
    def is_active(self) -> bool:
        """True iff the bound workspace is ACTIVE."""
        return self.workspace_status is WorkspaceStatus.ACTIVE

    def to_dict(self) -> dict[str, Any]:
        return {
            "context_id": self.context_id,
            "workspace_id": self.workspace_id,
            "workspace_slug": self.workspace_slug,
            "workspace_status": self.workspace_status.value,
            "principal_id": self.principal_id,
            "subject": self.subject,
            "tenant": self.tenant,
            "member_role": self.member_role.value if self.member_role else None,
        }

    def fingerprint(self) -> str:
        return content_hash(self.to_dict())


__all__ = ["WorkspaceContext"]
