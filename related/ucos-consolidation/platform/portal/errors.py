"""EC2-TASK-000073 — Portal error taxonomy (EC2-EPIC-003).

The UCOS Platform **Portal & Navigation** layer (L1 Presentation of the Program
architecture, §4) reuses the EC-1 / Platform Foundation error discipline additively —
it does not fork or modify it. Every portal error is rooted in
:class:`~platform.foundation.errors.PlatformError` (itself rooted in the certified
EC-1 :class:`~engine.foundation.obs.errors.FoundationError`), carries a stable,
category-prefixed ``code`` (``EC2-PORTAL-*``) and structured, non-secret ``context``
so failures are auditable (PL-02, IP-12) and machine-consumable by TRACK-001.

The Portal is *additive over EC-1 and the platform*: it consumes the certified EC-1
engine and the EC-2 Identity (L7) and Observability (L8) layers only through their
published contracts / composition roots, never modifies them, and never writes to the
certified corpus (DP-03). A malformed portal contract, navigation model, route,
access request, workspace handoff, service-discovery request, or search fails loudly
with a specific error. Every access failure is **fail-closed**: on any doubt the
portal denies rather than exposes a surface.
"""

from __future__ import annotations

from platform.foundation.errors import PlatformError


class PortalError(PlatformError):
    """Base class for all EC-2 Platform Portal errors."""

    code = "EC2-PORTAL-000"


class PortalContractError(PortalError):
    """A portal contract or surface declaration is malformed (AR-03/PL-05)."""

    code = "EC2-PORTAL-CONTRACT-001"


class NavigationError(PortalError):
    """A navigation model or navigation item is malformed or inconsistent."""

    code = "EC2-PORTAL-NAV-001"


class RoutingError(PortalError):
    """A route is malformed, duplicated, or cannot be resolved (fail-closed)."""

    code = "EC2-PORTAL-ROUTE-001"


class PortalAccessError(PortalError):
    """A portal access/authentication-integration request is denied or malformed.

    Raised when the portal cannot admit a caller — an absent/expired/revoked session,
    an unauthorized surface, or a malformed access request. Fail-closed by design.
    """

    code = "EC2-PORTAL-ACCESS-001"


class WorkspaceHandoffError(PortalError):
    """A portal-to-workspace handoff is malformed or unauthorized."""

    code = "EC2-PORTAL-WORKSPACE-001"


class ServiceDiscoveryError(PortalError):
    """A platform-services discovery / capability-access request is malformed."""

    code = "EC2-PORTAL-DISCOVERY-001"


class PortalSearchError(PortalError):
    """A global-search request or search entity is malformed."""

    code = "EC2-PORTAL-SEARCH-001"


class PortalServiceError(PortalError):
    """The portal service could not be composed or a portal operation is malformed."""

    code = "EC2-PORTAL-SERVICE-001"


__all__ = [
    "PortalError",
    "PortalContractError",
    "NavigationError",
    "RoutingError",
    "PortalAccessError",
    "WorkspaceHandoffError",
    "ServiceDiscoveryError",
    "PortalSearchError",
    "PortalServiceError",
]
