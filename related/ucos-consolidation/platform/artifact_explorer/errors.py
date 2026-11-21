"""EC2-TASK-000127 — Artifact Explorer error taxonomy (EC2-EPIC-009).

The UCOS Platform **Artifact Explorer Runtime** — the L3 realization of the Program
"Artifact Explorer" surface (Program §2.1 #10, PC-08 artifact discovery + PC-13 search +
PC-16 audit, §4 L3/L4) — reuses the EC-1 / Platform Foundation error discipline
additively; it does not fork or modify it. Every artifact-explorer error is rooted in
:class:`~platform.foundation.errors.PlatformError` (itself rooted in the certified EC-1
:class:`~engine.foundation.obs.errors.FoundationError`), carries a stable,
category-prefixed ``code`` (``EC2-AX-*``) and structured, non-secret ``context`` so
failures are auditable (PL-02, IP-12) and machine-consumable by TRACK-001.

The Artifact Explorer Runtime is *additive* over EC-1, the Foundation (L4/L6), the
Identity Layer (L7), the Observability Layer (L8), and the Generation Request Runtime
(EC2-EPIC-007, L3): it consumes them only through published contracts / composition
roots, never modifies them, and never writes to the certified corpus (DP-03). It
**consumes the EC-2 generation artifacts, dispatch, and provenance references by
reference** — resolving :class:`~platform.generation.contracts.GenerationRequest`,
:class:`~platform.generation.dispatch.DispatchRecord`, and
:class:`~platform.generation.provenance.RequestProvenance` read-only to project artifact
views, lineage, provenance, and trace navigation — and **generates no artifact, mutates
no artifact, and executes no engine** (the explorer is strictly read-only). Every access
decision is **fail-closed**: on any doubt the runtime denies rather than admits, and
cross-tenant/cross-workspace access is refused (P3).
"""

from __future__ import annotations

from platform.foundation.errors import PlatformError


class ArtifactExplorerError(PlatformError):
    """Base class for all EC-2 Artifact Explorer Runtime errors."""

    code = "EC2-AX-000"


class ArtifactContractError(ArtifactExplorerError):
    """An explorer contract, view, or vocabulary declaration is malformed (AR-03/PL-05)."""

    code = "EC2-AX-CONTRACT-001"


class ArtifactReferenceError(ArtifactExplorerError):
    """An artifact reference/view projection is malformed (by reference; fail-closed)."""

    code = "EC2-AX-REFERENCE-001"


class ArtifactLineageError(ArtifactExplorerError):
    """An artifact lineage projection is malformed or incomplete (fail-closed)."""

    code = "EC2-AX-LINEAGE-001"


class ArtifactProvenanceError(ArtifactExplorerError):
    """An artifact provenance projection is malformed (link-4 by reference; fail-closed)."""

    code = "EC2-AX-PROVENANCE-001"


class ArtifactTraceError(ArtifactExplorerError):
    """An artifact trace (navigation edge) is malformed or incomplete (fail-closed)."""

    code = "EC2-AX-TRACE-001"


class ArtifactSearchError(ArtifactExplorerError):
    """An artifact-explorer search request is malformed."""

    code = "EC2-AX-SEARCH-001"


class ArtifactAccessError(ArtifactExplorerError):
    """An artifact-explorer access/authorization request is denied or malformed (fail-closed)."""

    code = "EC2-AX-ACCESS-001"


class ArtifactServiceError(ArtifactExplorerError):
    """The artifact-explorer service could not be composed or an operation is malformed."""

    code = "EC2-AX-SERVICE-001"


__all__ = [
    "ArtifactExplorerError",
    "ArtifactContractError",
    "ArtifactReferenceError",
    "ArtifactLineageError",
    "ArtifactProvenanceError",
    "ArtifactTraceError",
    "ArtifactSearchError",
    "ArtifactAccessError",
    "ArtifactServiceError",
]
