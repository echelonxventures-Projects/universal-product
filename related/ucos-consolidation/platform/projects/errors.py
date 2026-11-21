"""EC2-TASK-000089 — Project error taxonomy (EC2-EPIC-005).

The UCOS Platform **Project Management Runtime** — the project half of the L3
Application "workspace & project lifecycle" surface (Program §2.1 surface 4, PC-03,
§4 L3) — reuses the EC-1 / Platform Foundation error discipline additively; it does
not fork or modify it. Every project error is rooted in
:class:`~platform.foundation.errors.PlatformError` (itself rooted in the certified
EC-1 :class:`~engine.foundation.obs.errors.FoundationError`), carries a stable,
category-prefixed ``code`` (``EC2-PROJ-*``) and structured, non-secret ``context`` so
failures are auditable (PL-02, IP-12) and machine-consumable by TRACK-001.

The Project Management Runtime is *additive* over EC-1, the Foundation (L4/L6), the
Identity Layer (L7), the Observability Layer (L8), and the Workspace Runtime (L3): it
consumes them only through published contracts / composition roots, never modifies
them, and never writes to the certified corpus (DP-03). A malformed project contract,
lifecycle transition, association, metadata, registration, search, context, or access
decision fails loudly with a specific error. Every access decision is **fail-closed**:
on any doubt the runtime denies rather than admits, and cross-tenant/cross-workspace
access is refused (P3).
"""

from __future__ import annotations

from platform.foundation.errors import PlatformError


class ProjectError(PlatformError):
    """Base class for all EC-2 Project Management Runtime errors."""

    code = "EC2-PROJ-000"


class ProjectContractError(ProjectError):
    """A project contract, record, or association declaration is malformed (AR-03/PL-05)."""

    code = "EC2-PROJ-CONTRACT-001"


class ProjectMetadataError(ProjectError):
    """Project metadata is malformed."""

    code = "EC2-PROJ-METADATA-001"


class ProjectLifecycleError(ProjectError):
    """An illegal or malformed project lifecycle transition (fail-closed)."""

    code = "EC2-PROJ-LIFECYCLE-001"


class ProjectRegistryError(ProjectError):
    """A project could not be registered or resolved (duplicate/absent/malformed)."""

    code = "EC2-PROJ-REGISTRY-001"


class ProjectAssociationError(ProjectError):
    """A project association is malformed or violates referential integrity (fail-closed)."""

    code = "EC2-PROJ-ASSOCIATION-001"


class ProjectStatusError(ProjectError):
    """A project derived-status computation is malformed."""

    code = "EC2-PROJ-STATUS-001"


class ProjectSearchError(ProjectError):
    """A project search request is malformed."""

    code = "EC2-PROJ-SEARCH-001"


class ProjectAccessError(ProjectError):
    """A project access/authorization request is denied or malformed (fail-closed)."""

    code = "EC2-PROJ-ACCESS-001"


class ProjectServiceError(ProjectError):
    """The project service could not be composed or an operation is malformed."""

    code = "EC2-PROJ-SERVICE-001"


__all__ = [
    "ProjectError",
    "ProjectContractError",
    "ProjectMetadataError",
    "ProjectLifecycleError",
    "ProjectRegistryError",
    "ProjectAssociationError",
    "ProjectStatusError",
    "ProjectSearchError",
    "ProjectAccessError",
    "ProjectServiceError",
]
