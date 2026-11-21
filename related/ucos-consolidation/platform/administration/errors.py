"""EC2-CAP-ADMIN-001 — Administration error taxonomy (Administration Runtime).

The UCOS Platform **Administration Runtime** — the operational administration surface
that governs platform, tenant, and workspace administration, operational
configuration, administrative lifecycle, and runtime management — reuses the EC-1 /
Platform Foundation error discipline additively; it does not fork or modify it. Every
administration error is rooted in :class:`~platform.foundation.errors.PlatformError`
(itself rooted in the certified EC-1
:class:`~engine.foundation.obs.errors.FoundationError`), carries a stable,
category-prefixed ``code`` (``EC2-ADMIN-*``) and structured, non-secret ``context`` so
failures are auditable (PL-02, IP-12) and machine-consumable by TRACK-001.

The Administration Runtime is **administrative only** — it is *not* governance, *not*
constitutional authority, *not* certification authority, and *not* execution
authorization. It is *additive* over EC-1, the Foundation (L4/L6), the Identity Layer
(L7), the Observability Layer (L8), and the Workspace Runtime (L3): it authorizes
**only** through the Identity Layer, observes **only** through the Observability Layer,
and reuses existing registries/contracts/identity/telemetry/error models — it
re-implements none of them, modifies none of them, and never writes to the certified
corpus (DP-03). Every administrative decision is **fail-closed**: on any doubt the
runtime denies rather than admits, and cross-tenant administration is refused.
"""

from __future__ import annotations

from platform.foundation.errors import PlatformError


class AdministrationError(PlatformError):
    """Base class for all EC-2 Administration Runtime errors."""

    code = "EC2-ADMIN-000"


class AdministrationContractError(AdministrationError):
    """An administrative contract, record, or vocabulary value is malformed (AR-03/PL-05)."""

    code = "EC2-ADMIN-CONTRACT-001"


class AdministrationContextError(AdministrationError):
    """An administrative runtime context is malformed (fail-closed)."""

    code = "EC2-ADMIN-CONTEXT-001"


class AdministrationConfigurationError(AdministrationError):
    """An administrative configuration/setting operation is malformed or inconsistent."""

    code = "EC2-ADMIN-CONFIG-001"


class AdministrationRoleError(AdministrationError):
    """An administrative role-view query is malformed."""

    code = "EC2-ADMIN-ROLE-001"


class AdministrationPermissionError(AdministrationError):
    """An administrative permission evaluation is malformed (fail-closed)."""

    code = "EC2-ADMIN-PERMISSION-001"


class AdministrationMembershipError(AdministrationError):
    """An administrative membership operation is malformed or inconsistent."""

    code = "EC2-ADMIN-MEMBERSHIP-001"


class AdministrationAuditError(AdministrationError):
    """An administrative audit/activity record is malformed."""

    code = "EC2-ADMIN-AUDIT-001"


class AdministrationSearchError(AdministrationError):
    """An administrative search request is malformed."""

    code = "EC2-ADMIN-SEARCH-001"


class AdministrationAccessError(AdministrationError):
    """An administrative access/authorization request is denied or malformed (fail-closed)."""

    code = "EC2-ADMIN-ACCESS-001"


class AdministrationServiceError(AdministrationError):
    """The administration service could not be composed or an operation is malformed."""

    code = "EC2-ADMIN-SERVICE-001"


__all__ = [
    "AdministrationError",
    "AdministrationContractError",
    "AdministrationContextError",
    "AdministrationConfigurationError",
    "AdministrationRoleError",
    "AdministrationPermissionError",
    "AdministrationMembershipError",
    "AdministrationAuditError",
    "AdministrationSearchError",
    "AdministrationAccessError",
    "AdministrationServiceError",
]
