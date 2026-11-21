"""EC2-TASK-000063 — Identity Contracts (EC2-EPIC-002).

The versioned contract surface for the UCOS Platform Identity Layer (L7 of the
Program architecture, §4). Every identity service — principal registry, role
registry, permission engine, policy engine, session model, authorization service —
is published as a documented, semantically versioned :class:`Contract`
(AR-03/PL-05), reusing the certified EC-1 contract machinery through the Platform
Foundation (:func:`~platform.foundation.contracts.platform_contract`,
:class:`~platform.foundation.contracts.ContractRef`).

This module also defines the immutable **core vocabulary** every identity service
speaks:

    * :class:`CapabilityGroup` — the sixteen capability-group rows of the §3.2 RBAC
      matrix; the unit access is granted and evaluated over.
    * :class:`Decision` — the fail-closed authorization effect (``PERMIT`` / ``DENY``).
    * :class:`AccessRequest` — an immutable, content-addressed "may *principal* perform
      *permission* on *capability group* (within *tenant*)?" question.
    * :class:`AccessDecision` — an immutable, content-addressed answer carrying the
      effect, a stable reason code, and the evaluated request.

All types are **immutable, typed, deterministic, and serializable** and hold no
runtime state and no secret material (SEC-04).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from platform.foundation.contracts import (
    Contract,
    ContractRef,
    content_hash,
    platform_contract,
)
from platform.foundation.errors import PlatformContractError
from platform.foundation.identity import Permission, Role
from platform.identity.errors import IdentityContractError
from typing import Any

#: The semantic version of the Identity Platform contract surface (AR-03/PL-05).
IDENTITY_CONTRACT_VERSION = "1.0.0"


class CapabilityGroup(str, Enum):
    """The sixteen capability-group rows of the §3.2 RBAC matrix.

    Access is granted to a :class:`~platform.foundation.identity.Role` and evaluated
    for a :class:`~platform.foundation.identity.Principal` over one of these groups —
    the coarse, auditable unit of authorization for the whole platform.
    """

    PORTAL_NAVIGATION = "portal-navigation"
    IDENTITY_SESSIONS_SELF = "identity-sessions-self"
    USER_ROLE_QUOTA_ADMIN = "user-role-quota-admin"
    WORKSPACE_PROJECT_LIFECYCLE = "workspace-project-lifecycle"
    BLUEPRINT_AUTHORING = "blueprint-authoring"
    BLUEPRINT_CATALOG = "blueprint-catalog"
    GENERATION_REQUESTS = "generation-requests"
    EXECUTION_DASHBOARD = "execution-dashboard"
    ARTIFACT_EXPLORER = "artifact-explorer"
    VALIDATION_EXPLORER = "validation-explorer"
    CERTIFICATION_LEDGER = "certification-ledger"
    RUNTIME_OPERATIONS = "runtime-operations"
    MONITORING_OBSERVABILITY = "monitoring-observability"
    ADMINISTRATION_POLICY = "administration-policy"
    AUDIT_TRACEABILITY = "audit-traceability"
    API_ACCESS = "api-access"


class Decision(str, Enum):
    """The fail-closed authorization effect."""

    PERMIT = "permit"
    DENY = "deny"


def all_capability_groups() -> tuple[CapabilityGroup, ...]:
    """Return every capability group in stable declaration order."""
    return tuple(CapabilityGroup)


@dataclass(frozen=True, slots=True)
class AccessRequest:
    """An immutable, content-addressed authorization question.

    "May principal ``principal_id`` (bearing ``roles``) perform ``permission`` on
    ``group`` — within ``tenant`` — over optional ``resource``?" The ``request_id``
    is content-addressed so an identical question always yields the same id.
    """

    principal_id: str
    roles: frozenset[Role]
    group: CapabilityGroup
    permission: Permission
    tenant: str | None = None
    resource: str | None = None
    request_id: str = ""

    @classmethod
    def create(
        cls,
        principal_id: str,
        roles: frozenset[Role],
        group: CapabilityGroup,
        permission: Permission,
        *,
        tenant: str | None = None,
        resource: str | None = None,
    ) -> AccessRequest:
        """Build a request with a deterministic, content-addressed ``request_id``."""
        if not isinstance(principal_id, str) or not principal_id:
            raise IdentityContractError("access request requires a principal_id")
        if not isinstance(group, CapabilityGroup):
            raise IdentityContractError(
                "access request group must be a CapabilityGroup",
                principal_id=principal_id,
            )
        if not isinstance(permission, Permission):
            raise IdentityContractError(
                "access request permission must be a Permission",
                principal_id=principal_id,
            )
        role_set = frozenset(roles)
        if not all(isinstance(r, Role) for r in role_set):
            raise IdentityContractError(
                "access request roles must be Role members", principal_id=principal_id
            )
        core = {
            "principal_id": principal_id,
            "roles": sorted(r.value for r in role_set),
            "group": group.value,
            "permission": permission.value,
            "tenant": tenant,
            "resource": resource,
        }
        return cls(
            principal_id=principal_id,
            roles=role_set,
            group=group,
            permission=permission,
            tenant=tenant,
            resource=resource,
            request_id=f"UCOS-AREQ-{content_hash(core)[:16]}",
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "request_id": self.request_id,
            "principal_id": self.principal_id,
            "roles": sorted(r.value for r in self.roles),
            "group": self.group.value,
            "permission": self.permission.value,
            "tenant": self.tenant,
            "resource": self.resource,
        }


@dataclass(frozen=True, slots=True)
class AccessDecision:
    """An immutable, content-addressed authorization answer (fail-closed).

    Carries the :class:`Decision` effect, a stable machine-readable ``reason`` code,
    and the evaluated :class:`AccessRequest`. The ``decision_id`` is content-addressed
    so an identical evaluation always yields the same id (deterministic evidence).
    """

    request: AccessRequest
    decision: Decision
    reason: str
    obligations: frozenset[str] = field(default_factory=frozenset)
    decision_id: str = ""

    @classmethod
    def create(
        cls,
        request: AccessRequest,
        decision: Decision,
        reason: str,
        *,
        obligations: frozenset[str] | None = None,
    ) -> AccessDecision:
        """Build a decision with a deterministic, content-addressed ``decision_id``."""
        if not isinstance(request, AccessRequest):
            raise IdentityContractError("a decision must reference an AccessRequest")
        if not isinstance(decision, Decision):
            raise IdentityContractError("decision effect must be a Decision")
        if not isinstance(reason, str) or not reason:
            raise IdentityContractError("decision requires a reason code")
        obs = frozenset(obligations or frozenset())
        core = {
            "request": request.to_dict(),
            "decision": decision.value,
            "reason": reason,
            "obligations": sorted(obs),
        }
        return cls(
            request=request,
            decision=decision,
            reason=reason,
            obligations=obs,
            decision_id=f"UCOS-ADEC-{content_hash(core)[:16]}",
        )

    @property
    def permitted(self) -> bool:
        return self.decision is Decision.PERMIT

    @property
    def denied(self) -> bool:
        return self.decision is Decision.DENY

    def to_dict(self) -> dict[str, Any]:
        return {
            "decision_id": self.decision_id,
            "request": self.request.to_dict(),
            "decision": self.decision.value,
            "reason": self.reason,
            "obligations": sorted(self.obligations),
        }


# --------------------------------------------------------------------------- #
# The published identity contract surface (L7).                               #
# --------------------------------------------------------------------------- #

#: The identity service contract identities the Identity Layer publishes. Each maps
#: to one EC2-EPIC-002 deliverable; consumers (portal, workspace, admin, …) bind to
#: these by reference (PL-05, versioned, backward-compatible).
_IDENTITY_CONTRACT_NAMES: tuple[tuple[str, str], ...] = (
    ("identity.principals.registry", "Principal registry — register/resolve principals."),
    ("identity.roles.registry", "Role registry — the §3.2 RBAC role definitions."),
    ("identity.permissions.resolve", "Permission engine — effective permission resolution."),
    ("identity.policy.evaluate", "Policy engine — fail-closed access policy evaluation."),
    ("identity.sessions.model", "Session model — establish/validate/revoke sessions."),
    ("identity.authorization.authorize", "Authorization service — the L7 access decision point."),
)

#: Immutable references to the six published identity contracts (name + version).
IDENTITY_CONTRACTS: tuple[ContractRef, ...] = tuple(
    ContractRef(name, IDENTITY_CONTRACT_VERSION) for name, _ in _IDENTITY_CONTRACT_NAMES
)


def identity_contract(name: str, description: str = "") -> Contract:
    """Build a versioned identity :class:`Contract` at the identity contract version."""
    if not isinstance(name, str) or not name:
        raise IdentityContractError("identity contract name is required")
    try:
        return platform_contract(name, IDENTITY_CONTRACT_VERSION, description)
    except PlatformContractError as exc:  # normalise into the identity taxonomy
        raise IdentityContractError(str(exc), name=name) from exc


def default_identity_contracts() -> tuple[Contract, ...]:
    """The six published identity contracts as concrete :class:`Contract` objects."""
    return tuple(
        identity_contract(name, description) for name, description in _IDENTITY_CONTRACT_NAMES
    )


__all__ = [
    "IDENTITY_CONTRACT_VERSION",
    "CapabilityGroup",
    "Decision",
    "all_capability_groups",
    "AccessRequest",
    "AccessDecision",
    "IDENTITY_CONTRACTS",
    "identity_contract",
    "default_identity_contracts",
]
