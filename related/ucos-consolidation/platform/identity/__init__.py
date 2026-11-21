"""UCOS EC-2 Platform Identity Layer (EC2-EPIC-002) — identity services only.

The Identity Platform (L7 of the Program architecture, §4). It authenticates,
authorizes, and isolates access to every platform capability, as a strictly
**additive** layer over the certified EC-1 engine and the EC-2 Platform Foundation
(EC2-EPIC-001): it consumes both only through published contracts, modifies neither,
never writes to the certified corpus (DP-03), remains deterministic, is
registry-driven, and preserves every EC-1 certification.

Deliverables (EC2-TASK-000063…000070):
    * **contracts** (TASK-000063) — the versioned identity contract surface plus the
      core vocabulary: ``CapabilityGroup``, ``Decision``, ``AccessRequest``,
      ``AccessDecision``.
    * **principals** (TASK-000064) — the deterministic, append-only ``PrincipalRegistry``.
    * **roles** (TASK-000065) — ``RoleRegistry`` seeded with the §3.2 RBAC matrix.
    * **permissions** (TASK-000066) — the ``PermissionEngine`` (effective permission
      resolution).
    * **policy** (TASK-000067) — the fail-closed ``PolicyEngine`` (§3.2 invariants).
    * **sessions** (TASK-000068) — the ``Session`` model + deterministic ``SessionRegistry``.
    * **service** (TASK-000069) — the ``AuthorizationService`` composition root and
      ``IdentityEvidence``.

This epic is **identity services only**: no UI, portal, dashboard, or runtime
operation is implemented here. It carries no constitutional authority; the external
gates (EC-1…EC-6) remain open.
"""

from __future__ import annotations

from platform.identity.contracts import (
    IDENTITY_CONTRACT_VERSION,
    IDENTITY_CONTRACTS,
    AccessDecision,
    AccessRequest,
    CapabilityGroup,
    Decision,
    all_capability_groups,
    default_identity_contracts,
    identity_contract,
)
from platform.identity.errors import (
    AuthorizationError,
    IdentityContractError,
    IdentityError,
    PermissionResolutionError,
    PolicyEvaluationError,
    PrincipalRegistryError,
    RoleRegistryError,
    SessionError,
)
from platform.identity.permissions import (
    EffectivePermissions,
    PermissionEngine,
    expand_permissions,
)
from platform.identity.policy import (
    FROZEN_CORPUS_PREFIXES,
    WRITE_PERMISSIONS,
    NamedPolicyRule,
    PolicyEngine,
    PolicyRule,
)
from platform.identity.principals import PrincipalRegistry
from platform.identity.roles import (
    RoleDefinition,
    RoleGrant,
    RoleRegistry,
    default_role_definitions,
    default_role_registry,
)
from platform.identity.service import (
    ACCESS_EVENT,
    IDENTITY_BOOTSTRAP_EVENT,
    AuthorizationService,
    IdentityEvidence,
    bootstrap_identity,
    build_authorization_service,
)
from platform.identity.sessions import (
    Session,
    SessionEvent,
    SessionRegistry,
    SessionStatus,
)

__all__ = [
    # contracts (TASK-000063)
    "IDENTITY_CONTRACT_VERSION",
    "IDENTITY_CONTRACTS",
    "CapabilityGroup",
    "Decision",
    "AccessRequest",
    "AccessDecision",
    "all_capability_groups",
    "identity_contract",
    "default_identity_contracts",
    # principals (TASK-000064)
    "PrincipalRegistry",
    # roles (TASK-000065)
    "RoleGrant",
    "RoleDefinition",
    "RoleRegistry",
    "default_role_definitions",
    "default_role_registry",
    # permissions (TASK-000066)
    "expand_permissions",
    "EffectivePermissions",
    "PermissionEngine",
    # policy (TASK-000067)
    "FROZEN_CORPUS_PREFIXES",
    "WRITE_PERMISSIONS",
    "PolicyRule",
    "NamedPolicyRule",
    "PolicyEngine",
    # sessions (TASK-000068)
    "SessionStatus",
    "Session",
    "SessionEvent",
    "SessionRegistry",
    # service (TASK-000069)
    "ACCESS_EVENT",
    "IDENTITY_BOOTSTRAP_EVENT",
    "IdentityEvidence",
    "AuthorizationService",
    "build_authorization_service",
    "bootstrap_identity",
    # errors (TASK-000063)
    "IdentityError",
    "IdentityContractError",
    "PrincipalRegistryError",
    "RoleRegistryError",
    "PermissionResolutionError",
    "PolicyEvaluationError",
    "SessionError",
    "AuthorizationError",
]
