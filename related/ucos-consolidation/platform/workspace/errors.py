"""EC2-TASK-000081 — Workspace error taxonomy (EC2-EPIC-004).

The UCOS Platform **Workspace Runtime** — the scoped execution boundary of the L3
Application layer (Program §2.1 surface 2, §4 L3) — reuses the EC-1 / Platform
Foundation error discipline additively; it does not fork or modify it. Every workspace
error is rooted in :class:`~platform.foundation.errors.PlatformError` (itself rooted in
the certified EC-1 :class:`~engine.foundation.obs.errors.FoundationError`), carries a
stable, category-prefixed ``code`` (``EC2-WORKSPACE-*``) and structured, non-secret
``context`` so failures are auditable (PL-02, IP-12) and machine-consumable by
TRACK-001.

The Workspace Runtime is *additive* over EC-1, the Foundation (L4/L6), the Identity
Layer (L7), and the Observability Layer (L8): it consumes them only through published
contracts / composition roots, never modifies them, and never writes to the certified
corpus (DP-03). A malformed workspace contract, membership, lifecycle transition,
metadata, registration, search, context, or isolation decision fails loudly with a
specific error. Every access decision is **fail-closed**: on any doubt the runtime
denies rather than admits, and cross-tenant access is refused (P3).
"""

from __future__ import annotations

from platform.foundation.errors import PlatformError


class WorkspaceError(PlatformError):
    """Base class for all EC-2 Workspace Runtime errors."""

    code = "EC2-WORKSPACE-000"


class WorkspaceContractError(WorkspaceError):
    """A workspace contract, record, or member declaration is malformed (AR-03/PL-05)."""

    code = "EC2-WORKSPACE-CONTRACT-001"


class WorkspaceMetadataError(WorkspaceError):
    """Workspace metadata is malformed."""

    code = "EC2-WORKSPACE-METADATA-001"


class WorkspaceLifecycleError(WorkspaceError):
    """An illegal or malformed workspace lifecycle transition (fail-closed)."""

    code = "EC2-WORKSPACE-LIFECYCLE-001"


class MembershipError(WorkspaceError):
    """A workspace membership operation is malformed or inconsistent."""

    code = "EC2-WORKSPACE-MEMBERSHIP-001"


class WorkspaceRegistryError(WorkspaceError):
    """A workspace could not be registered or resolved (duplicate/absent/malformed)."""

    code = "EC2-WORKSPACE-REGISTRY-001"


class WorkspaceIsolationError(WorkspaceError):
    """A workspace isolation evaluation is malformed (fail-closed)."""

    code = "EC2-WORKSPACE-ISOLATION-001"


class WorkspaceSearchError(WorkspaceError):
    """A workspace search request is malformed."""

    code = "EC2-WORKSPACE-SEARCH-001"


class WorkspaceAccessError(WorkspaceError):
    """A workspace access/authorization request is denied or malformed (fail-closed)."""

    code = "EC2-WORKSPACE-ACCESS-001"


class WorkspaceServiceError(WorkspaceError):
    """The workspace service could not be composed or an operation is malformed."""

    code = "EC2-WORKSPACE-SERVICE-001"


__all__ = [
    "WorkspaceError",
    "WorkspaceContractError",
    "WorkspaceMetadataError",
    "WorkspaceLifecycleError",
    "MembershipError",
    "WorkspaceRegistryError",
    "WorkspaceIsolationError",
    "WorkspaceSearchError",
    "WorkspaceAccessError",
    "WorkspaceServiceError",
]
