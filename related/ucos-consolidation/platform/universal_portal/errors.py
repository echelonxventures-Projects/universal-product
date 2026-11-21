"""UCOS-EPIC-008 / Terminal T8 — Universal Portal error taxonomy.

The Universal Portal (L1 presentation composition) reuses the EC-1 / Platform Foundation
error discipline additively — it does not fork or modify it. Every Universal Portal error
is rooted in :class:`~platform.foundation.errors.PlatformError` (itself rooted in the
certified EC-1 :class:`~engine.foundation.obs.errors.FoundationError`), carries a stable,
category-prefixed ``code`` (``T8-UPORTAL-*``) and structured, non-secret ``context`` so
failures are auditable (PL-02, IP-12) and machine-consumable by TRACK-001.

The portal consumes the certified EC-2 Portal shell, Identity (L7), Observability (L8),
and each domain runtime only through their published contracts / composition roots — it
never modifies them and never writes to the certified corpus (DP-03). A malformed
application binding, contract, access request, developer-catalog request, or documentation
request fails loudly with a specific error. Every access failure is **fail-closed**: on any
doubt the portal denies rather than exposes a surface.
"""

from __future__ import annotations

from platform.foundation.errors import PlatformError


class UniversalPortalError(PlatformError):
    """Base class for all UCOS-EPIC-008 Universal Portal errors."""

    code = "T8-UPORTAL-000"


class UniversalPortalContractError(UniversalPortalError):
    """A Universal Portal contract, application, or surface declaration is malformed."""

    code = "T8-UPORTAL-CONTRACT-001"


class ApplicationBindingError(UniversalPortalError):
    """A portal application provider binding is malformed or duplicated (fail-closed)."""

    code = "T8-UPORTAL-BINDING-001"


class UniversalPortalAccessError(UniversalPortalError):
    """A Universal Portal access request is denied or malformed (fail-closed).

    Raised when the portal cannot admit a caller or a required surface authorization is
    denied where the caller demanded enforcement rather than data.
    """

    code = "T8-UPORTAL-ACCESS-001"


class DeveloperPortalError(UniversalPortalError):
    """A developer-portal API-catalog request is malformed."""

    code = "T8-UPORTAL-DEVELOPER-001"


class DocumentationPortalError(UniversalPortalError):
    """A documentation-portal index or page request is malformed."""

    code = "T8-UPORTAL-DOC-001"


class UniversalPortalServiceError(UniversalPortalError):
    """The Universal Portal service could not be composed or an operation is malformed."""

    code = "T8-UPORTAL-SERVICE-001"


__all__ = [
    "UniversalPortalError",
    "UniversalPortalContractError",
    "ApplicationBindingError",
    "UniversalPortalAccessError",
    "DeveloperPortalError",
    "DocumentationPortalError",
    "UniversalPortalServiceError",
]
