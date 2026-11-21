"""EC2-TASK-000081 — Workspace Contracts (EC2-EPIC-004).

The versioned contract surface for the UCOS Platform **Workspace Runtime** (L3
Application of the Program architecture, §4) plus the immutable **core vocabulary**
every workspace service speaks. It reuses the certified EC-1 contract machinery
through the Platform Foundation
(:func:`~platform.foundation.contracts.platform_contract`,
:class:`~platform.foundation.contracts.ContractRef`) and binds workspace authorization
to the single §3.2 :class:`~platform.identity.contracts.CapabilityGroup`
``workspace-project-lifecycle`` — so **workspace access is authorization-derived, not
invented**.

Vocabulary:
    * :class:`WorkspaceStatus` — the lifecycle states a workspace occupies
      (``active`` / ``suspended`` / ``archived``); ``archived`` is terminal.
    * :class:`MemberRole` — the workspace-local collaboration role of a principal
      (``owner`` / ``member`` / ``viewer``); distinct from, and never a substitute for,
      the platform RBAC :class:`~platform.foundation.identity.Role`.
    * :class:`Workspace` — an immutable, content-addressed scoped container: a stable
      ``slug`` (its identity within a tenant), a display name, an optional ``tenant``
      (the isolation boundary), an owner subject, a status, and metadata.
    * :class:`WorkspaceMember` — an immutable, content-addressed binding of a principal
      to a workspace with a :class:`MemberRole`.
    * :data:`WORKSPACE_CONTRACTS` — the published workspace service contracts consumers
      bind to by reference (PL-05, versioned).

All types are **immutable, typed, deterministic, and serializable**, hold no runtime
state, and hold no secret material (SEC-04).
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from platform.foundation.contracts import (
    Contract,
    ContractRef,
    content_hash,
    platform_contract,
)
from platform.foundation.errors import PlatformContractError
from platform.identity.contracts import CapabilityGroup
from platform.workspace.errors import WorkspaceContractError
from platform.workspace.metadata import EMPTY_METADATA, WorkspaceMetadata
from typing import Any

#: The semantic version of the Workspace Runtime contract surface (AR-03/PL-05).
WORKSPACE_CONTRACT_VERSION = "1.0.0"

#: The §3.2 capability group that authorizes every workspace action.
WORKSPACE_GROUP = CapabilityGroup.WORKSPACE_PROJECT_LIFECYCLE


class WorkspaceStatus(str, Enum):
    """The lifecycle states a workspace occupies (``archived`` is terminal)."""

    ACTIVE = "active"
    SUSPENDED = "suspended"
    ARCHIVED = "archived"


class MemberRole(str, Enum):
    """The workspace-local collaboration role of a principal.

    Distinct from the platform RBAC :class:`~platform.foundation.identity.Role`: it
    scopes collaboration *within* a workspace and never grants platform authority
    (which is always resolved by the Identity Layer).
    """

    OWNER = "owner"
    MEMBER = "member"
    VIEWER = "viewer"


def all_workspace_statuses() -> tuple[WorkspaceStatus, ...]:
    """Return every workspace status in stable declaration order."""
    return tuple(WorkspaceStatus)


def all_member_roles() -> tuple[MemberRole, ...]:
    """Return every workspace member role in stable declaration order."""
    return tuple(MemberRole)


def _require_slug(slug: str) -> str:
    if not isinstance(slug, str) or not slug:
        raise WorkspaceContractError("workspace slug is required")
    normalized = slug.strip().lower()
    if not normalized or any(c.isspace() for c in normalized):
        raise WorkspaceContractError("workspace slug must be non-empty and whitespace-free")
    return normalized


@dataclass(frozen=True, slots=True)
class Workspace:
    """An immutable, content-addressed scoped workspace container.

    A workspace's identity is its ``slug`` within its ``tenant`` — the ``workspace_id``
    is content-addressed from exactly those two fields so registration is idempotent
    and reproducible; mutable facets (status, metadata) never change the id.
    """

    workspace_id: str
    slug: str
    name: str
    tenant: str | None
    owner_subject: str
    status: WorkspaceStatus
    metadata: WorkspaceMetadata

    @classmethod
    def create(
        cls,
        slug: str,
        name: str,
        owner_subject: str,
        *,
        tenant: str | None = None,
        status: WorkspaceStatus = WorkspaceStatus.ACTIVE,
        metadata: WorkspaceMetadata | None = None,
    ) -> Workspace:
        """Build a workspace with a deterministic, content-addressed ``workspace_id``."""
        normalized_slug = _require_slug(slug)
        if not isinstance(name, str) or not name:
            raise WorkspaceContractError("workspace name is required", slug=normalized_slug)
        if not isinstance(owner_subject, str) or not owner_subject:
            raise WorkspaceContractError(
                "workspace owner_subject is required", slug=normalized_slug
            )
        if not isinstance(status, WorkspaceStatus):
            raise WorkspaceContractError("workspace status must be a WorkspaceStatus")
        md = metadata if metadata is not None else EMPTY_METADATA
        if not isinstance(md, WorkspaceMetadata):
            raise WorkspaceContractError("workspace metadata must be a WorkspaceMetadata")
        identity = {"slug": normalized_slug, "tenant": tenant}
        return cls(
            workspace_id=f"UCOS-WSPC-{content_hash(identity)[:16]}",
            slug=normalized_slug,
            name=name,
            tenant=tenant,
            owner_subject=owner_subject,
            status=status,
            metadata=md,
        )

    def with_status(self, status: WorkspaceStatus) -> Workspace:
        """Return an immutable copy in ``status`` (the id is preserved)."""
        if not isinstance(status, WorkspaceStatus):
            raise WorkspaceContractError("workspace status must be a WorkspaceStatus")
        return Workspace(
            workspace_id=self.workspace_id,
            slug=self.slug,
            name=self.name,
            tenant=self.tenant,
            owner_subject=self.owner_subject,
            status=status,
            metadata=self.metadata,
        )

    def with_metadata(self, metadata: WorkspaceMetadata) -> Workspace:
        """Return an immutable copy carrying ``metadata`` (the id is preserved)."""
        if not isinstance(metadata, WorkspaceMetadata):
            raise WorkspaceContractError("workspace metadata must be a WorkspaceMetadata")
        return Workspace(
            workspace_id=self.workspace_id,
            slug=self.slug,
            name=self.name,
            tenant=self.tenant,
            owner_subject=self.owner_subject,
            status=self.status,
            metadata=metadata,
        )

    @property
    def is_active(self) -> bool:
        return self.status is WorkspaceStatus.ACTIVE

    @property
    def is_global(self) -> bool:
        """True iff the workspace is untenanted (visible across tenants)."""
        return self.tenant is None

    def to_dict(self) -> dict[str, Any]:
        return {
            "workspace_id": self.workspace_id,
            "slug": self.slug,
            "name": self.name,
            "tenant": self.tenant,
            "owner_subject": self.owner_subject,
            "status": self.status.value,
            "metadata": self.metadata.to_dict(),
        }

    def fingerprint(self) -> str:
        return content_hash(self.to_dict())


@dataclass(frozen=True, slots=True)
class WorkspaceMember:
    """An immutable, content-addressed binding of a principal to a workspace."""

    member_id: str
    workspace_id: str
    principal_id: str
    subject: str
    role: MemberRole

    @classmethod
    def create(
        cls,
        workspace_id: str,
        principal_id: str,
        subject: str,
        role: MemberRole,
    ) -> WorkspaceMember:
        """Build a member with a deterministic id (keyed by workspace + principal)."""
        if not isinstance(workspace_id, str) or not workspace_id:
            raise WorkspaceContractError("member requires a workspace_id")
        if not isinstance(principal_id, str) or not principal_id:
            raise WorkspaceContractError("member requires a principal_id")
        if not isinstance(subject, str) or not subject:
            raise WorkspaceContractError("member requires a subject")
        if not isinstance(role, MemberRole):
            raise WorkspaceContractError("member role must be a MemberRole")
        key = {"workspace_id": workspace_id, "principal_id": principal_id}
        return cls(
            member_id=f"UCOS-WMEM-{content_hash(key)[:16]}",
            workspace_id=workspace_id,
            principal_id=principal_id,
            subject=subject,
            role=role,
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "member_id": self.member_id,
            "workspace_id": self.workspace_id,
            "principal_id": self.principal_id,
            "subject": self.subject,
            "role": self.role.value,
        }


# --------------------------------------------------------------------------- #
# The published workspace contract surface (L3).                              #
# --------------------------------------------------------------------------- #

#: The workspace service contract identities the Workspace Runtime publishes. Each
#: maps to an EC2-EPIC-004 deliverable; consumers bind to these by reference (PL-05).
_WORKSPACE_CONTRACT_NAMES: tuple[tuple[str, str], ...] = (
    ("workspace.registry.registry", "Workspace registry — create/register/resolve/discover."),
    ("workspace.membership.registry", "Membership registry — bind principals to workspaces."),
    ("workspace.lifecycle.transition", "Lifecycle — deterministic workspace state machine."),
    ("workspace.isolation.evaluate", "Isolation — tenant/workspace boundary evaluation (P3)."),
    ("workspace.search.query", "Workspace search — authorization + isolation scoped discovery."),
    ("workspace.runtime.service", "Workspace runtime — the L3 access + context decision point."),
)

#: Immutable references to the published workspace contracts (name + version).
WORKSPACE_CONTRACTS: tuple[ContractRef, ...] = tuple(
    ContractRef(name, WORKSPACE_CONTRACT_VERSION) for name, _ in _WORKSPACE_CONTRACT_NAMES
)


def workspace_contract(name: str, description: str = "") -> Contract:
    """Build a versioned workspace :class:`Contract` at the workspace contract version."""
    if not isinstance(name, str) or not name:
        raise WorkspaceContractError("workspace contract name is required")
    try:
        return platform_contract(name, WORKSPACE_CONTRACT_VERSION, description)
    except PlatformContractError as exc:  # pragma: no cover - defensive normalisation
        raise WorkspaceContractError(str(exc), name=name) from exc


def default_workspace_contracts() -> tuple[Contract, ...]:
    """The published workspace contracts as concrete :class:`Contract` objects."""
    return tuple(
        workspace_contract(name, description) for name, description in _WORKSPACE_CONTRACT_NAMES
    )


__all__ = [
    "WORKSPACE_CONTRACT_VERSION",
    "WORKSPACE_GROUP",
    "WorkspaceStatus",
    "MemberRole",
    "all_workspace_statuses",
    "all_member_roles",
    "Workspace",
    "WorkspaceMember",
    "WORKSPACE_CONTRACTS",
    "workspace_contract",
    "default_workspace_contracts",
]
