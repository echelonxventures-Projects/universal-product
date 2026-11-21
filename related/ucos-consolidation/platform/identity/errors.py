"""EC2-TASK-000063 — Platform Identity error taxonomy (EC2-EPIC-002).

The Identity Platform **reuses** the EC-2 Platform Foundation error discipline
(EC2-TASK-000055) additively — every identity error is rooted in
:class:`~platform.foundation.errors.PlatformError` (itself rooted in the certified
EC-1 :class:`~engine.foundation.obs.errors.FoundationError`), carries a stable,
category-prefixed ``code`` (``EC2-IDENTITY-*``) and structured, **non-secret**
``context`` so every denial and failure is auditable (PL-02, IP-12, PC-16) and
machine-consumable by TRACK-001.

The Identity Platform is *additive over EC-1 and over the Platform Foundation*: it
consumes both only through published contracts, modifies neither, and never writes
to the certified corpus (DP-03). A malformed identity contract, a duplicate/absent
principal or role registration, a permission-resolution fault, a policy fault, a
session fault, or an authorization fault fails loudly and fail-closed with a
specific error. Secrets and credentials are never modeled (SEC-04) — credentials
are held by reference only.
"""

from __future__ import annotations

from platform.foundation.errors import PlatformError


class IdentityError(PlatformError):
    """Base class for all EC-2 Identity Platform errors."""

    code = "EC2-IDENTITY-100"


class IdentityContractError(IdentityError):
    """An identity contract is malformed or violates versioning discipline (AR-03/PL-05)."""

    code = "EC2-IDENTITY-CONTRACT-001"


class PrincipalRegistryError(IdentityError):
    """A principal could not be registered or resolved (duplicate, absent, malformed)."""

    code = "EC2-IDENTITY-PRINCIPAL-001"


class RoleRegistryError(IdentityError):
    """A role definition could not be registered or resolved (duplicate, absent, malformed)."""

    code = "EC2-IDENTITY-ROLE-001"


class PermissionResolutionError(IdentityError):
    """A permission set could not be resolved (unknown capability group or role)."""

    code = "EC2-IDENTITY-PERMISSION-001"


class PolicyEvaluationError(IdentityError):
    """An access policy could not be evaluated (malformed rule or request)."""

    code = "EC2-IDENTITY-POLICY-001"


class SessionError(IdentityError):
    """A session is malformed, absent, expired, or revoked (fail-closed)."""

    code = "EC2-IDENTITY-SESSION-001"


class AuthorizationError(IdentityError):
    """An authorization operation could not be completed (fail-closed)."""

    code = "EC2-IDENTITY-AUTHZ-001"


__all__ = [
    "IdentityError",
    "IdentityContractError",
    "PrincipalRegistryError",
    "RoleRegistryError",
    "PermissionResolutionError",
    "PolicyEvaluationError",
    "SessionError",
    "AuthorizationError",
]
