"""EC2-TASK-000109 — Generation Request error taxonomy (EC2-EPIC-007).

The UCOS Platform **Generation Request Runtime** — the L3 realization of the Program
"Generation Requests" surface (Program §2.1 #8, PC-06 generation submission +
PC-07 execution dispatch, §4 L3/L4) — reuses the EC-1 / Platform Foundation error
discipline additively; it does not fork or modify it. Every generation-request error
is rooted in :class:`~platform.foundation.errors.PlatformError` (itself rooted in the
certified EC-1 :class:`~engine.foundation.obs.errors.FoundationError`), carries a
stable, category-prefixed ``code`` (``EC2-GR-*``) and structured, non-secret
``context`` so failures are auditable (PL-02, IP-12) and machine-consumable by
TRACK-001.

The Generation Request Runtime is *additive* over EC-1, the Foundation (L4/L6), the
Identity Layer (L7), the Observability Layer (L8), the Workspace Runtime (L3), the
Project Management Runtime (L3), and the Blueprint Catalog & Management Runtime (L3/L6):
it consumes them only through published contracts / composition roots, never modifies
them, and never writes to the certified corpus (DP-03). A malformed request contract,
metadata, provenance, dispatch, lifecycle transition, registration, status, context,
search, or access decision fails loudly with a specific error. Every access decision
is **fail-closed**: on any doubt the runtime denies rather than admits, and
cross-tenant/cross-workspace access is refused (P3). A request may reach the Execution
Runtime **only** through the governed dispatch boundary — there is no runtime bypass
path (§7 dispatch integration).
"""

from __future__ import annotations

from platform.foundation.errors import PlatformError


class GenerationRequestError(PlatformError):
    """Base class for all EC-2 Generation Request Runtime errors."""

    code = "EC2-GR-000"


class RequestContractError(GenerationRequestError):
    """A request contract, record, or vocabulary declaration is malformed (AR-03/PL-05)."""

    code = "EC2-GR-CONTRACT-001"


class RequestMetadataError(GenerationRequestError):
    """Generation request metadata is malformed."""

    code = "EC2-GR-METADATA-001"


class RequestLifecycleError(GenerationRequestError):
    """An illegal or malformed generation-request lifecycle transition (fail-closed)."""

    code = "EC2-GR-LIFECYCLE-001"


class RequestRegistryError(GenerationRequestError):
    """A request could not be registered or resolved (duplicate/absent/malformed)."""

    code = "EC2-GR-REGISTRY-001"


class RequestDispatchError(GenerationRequestError):
    """A dispatch handoff to the Execution Runtime is malformed or inadmissible (fail-closed)."""

    code = "EC2-GR-DISPATCH-001"


class RequestProvenanceError(GenerationRequestError):
    """Request provenance-by-reference is malformed or incomplete (link-4, fail-closed)."""

    code = "EC2-GR-PROVENANCE-001"


class RequestStatusError(GenerationRequestError):
    """A generation-request derived-status computation is malformed."""

    code = "EC2-GR-STATUS-001"


class RequestSearchError(GenerationRequestError):
    """A generation-request search request is malformed."""

    code = "EC2-GR-SEARCH-001"


class RequestAccessError(GenerationRequestError):
    """A generation-request access/authorization request is denied or malformed (fail-closed)."""

    code = "EC2-GR-ACCESS-001"


class RequestServiceError(GenerationRequestError):
    """The generation-request service could not be composed or an operation is malformed."""

    code = "EC2-GR-SERVICE-001"


__all__ = [
    "GenerationRequestError",
    "RequestContractError",
    "RequestMetadataError",
    "RequestLifecycleError",
    "RequestRegistryError",
    "RequestDispatchError",
    "RequestProvenanceError",
    "RequestStatusError",
    "RequestSearchError",
    "RequestAccessError",
    "RequestServiceError",
]
