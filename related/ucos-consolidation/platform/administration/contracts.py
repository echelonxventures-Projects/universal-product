"""EC2-CAP-ADMIN-001 — Administration Contracts (Administration Runtime).

The versioned contract surface for the UCOS Platform **Administration Runtime** plus
the immutable **core vocabulary** every administrative service speaks. It reuses the
certified EC-1 contract machinery through the Platform Foundation
(:func:`~platform.foundation.contracts.platform_contract`,
:class:`~platform.foundation.contracts.ContractRef`) and binds administrative
authorization to the single §3.2
:class:`~platform.identity.contracts.CapabilityGroup` ``administration-policy`` — so
**administrative access is authorization-derived, not invented**. The Administration
Runtime creates **no new authority**: on ``administration-policy`` the §3.2 matrix
grants ``ADMINISTER`` to the Platform Administrator and ``READ`` to the Auditor, and
no one else — the runtime enforces exactly that, adding nothing.

Vocabulary:
    * :class:`AdministrativeScope` — the boundary an administrative action addresses
      (``platform`` / ``tenant`` / ``workspace``).
    * :class:`AdministrativeDomain` — the administrative subject area of an action
      (configuration, membership, role, permission, lifecycle, …) — for audit
      categorization only; it confers nothing.
    * :class:`AdministrativeAction` — the operational administrative verb
      (``inspect`` / ``configure`` / ``assign`` / ``revoke`` / ``suspend`` /
      ``activate``); each maps to exactly one identity
      :class:`~platform.foundation.identity.Permission` on ``administration-policy``.
    * :class:`OperationalState` — the operational lifecycle state an administered
      resource occupies (``active`` / ``suspended`` / ``decommissioned``).
    * :class:`AdministrativeTarget` — an immutable, content-addressed description of
      *what* an action administers (scope + domain + identifier + tenant).
    * :data:`ADMINISTRATION_CONTRACTS` — the published administration service
      contracts consumers bind to by reference (PL-05, versioned).

All types are **immutable, typed, deterministic, and serializable**, hold no runtime
state, and hold no secret material (SEC-04).
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from platform.administration.errors import AdministrationContractError
from platform.foundation.contracts import (
    Contract,
    ContractRef,
    content_hash,
    platform_contract,
)
from platform.foundation.errors import PlatformContractError
from platform.foundation.identity import Permission
from platform.identity.contracts import CapabilityGroup
from typing import Any

#: The semantic version of the Administration Runtime contract surface (AR-03/PL-05).
ADMINISTRATION_CONTRACT_VERSION = "1.0.0"

#: The §3.2 capability group that authorizes every administrative action.
ADMINISTRATION_GROUP = CapabilityGroup.ADMINISTRATION_POLICY


class AdministrativeScope(str, Enum):
    """The boundary an administrative action addresses."""

    PLATFORM = "platform"
    TENANT = "tenant"
    WORKSPACE = "workspace"


class AdministrativeDomain(str, Enum):
    """The administrative subject area of an action (audit categorization only)."""

    CONTEXT = "context"
    CONFIGURATION = "configuration"
    MEMBERSHIP = "membership"
    ROLE = "role"
    PERMISSION = "permission"
    LIFECYCLE = "lifecycle"
    TENANT = "tenant"
    WORKSPACE = "workspace"
    PLATFORM = "platform"
    ACCESS = "access"
    SEARCH = "search"


class AdministrativeAction(str, Enum):
    """The operational administrative verbs (each maps to one identity permission)."""

    INSPECT = "inspect"
    CONFIGURE = "configure"
    ASSIGN = "assign"
    REVOKE = "revoke"
    SUSPEND = "suspend"
    ACTIVATE = "activate"


class OperationalState(str, Enum):
    """The operational lifecycle state an administered resource occupies.

    ``decommissioned`` is terminal. This models *operational administration* only —
    it is not a governance, constitutional, or certification state.
    """

    ACTIVE = "active"
    SUSPENDED = "suspended"
    DECOMMISSIONED = "decommissioned"


#: The identity permission each administrative action requires on ``administration-policy``.
#: ``INSPECT`` needs READ (Platform Administrator or Auditor); every mutating action
#: needs ADMINISTER (Platform Administrator only) — no new authority is created.
_ACTION_PERMISSION: dict[AdministrativeAction, Permission] = {
    AdministrativeAction.INSPECT: Permission.READ,
    AdministrativeAction.CONFIGURE: Permission.ADMINISTER,
    AdministrativeAction.ASSIGN: Permission.ADMINISTER,
    AdministrativeAction.REVOKE: Permission.ADMINISTER,
    AdministrativeAction.SUSPEND: Permission.ADMINISTER,
    AdministrativeAction.ACTIVATE: Permission.ADMINISTER,
}


def required_permission(action: AdministrativeAction) -> Permission:
    """Return the identity permission ``action`` requires on ``administration-policy``."""
    if not isinstance(action, AdministrativeAction):
        raise AdministrationContractError("action must be an AdministrativeAction")
    return _ACTION_PERMISSION[action]


def all_administrative_scopes() -> tuple[AdministrativeScope, ...]:
    """Return every administrative scope in stable declaration order."""
    return tuple(AdministrativeScope)


def all_administrative_actions() -> tuple[AdministrativeAction, ...]:
    """Return every administrative action in stable declaration order."""
    return tuple(AdministrativeAction)


def all_operational_states() -> tuple[OperationalState, ...]:
    """Return every operational state in stable declaration order."""
    return tuple(OperationalState)


def _require_identifier(identifier: str) -> str:
    if not isinstance(identifier, str) or not identifier:
        raise AdministrationContractError("administrative target identifier is required")
    normalized = identifier.strip()
    if not normalized:
        raise AdministrationContractError("administrative target identifier is required")
    return normalized


@dataclass(frozen=True, slots=True)
class AdministrativeTarget:
    """An immutable, content-addressed description of *what* an action administers."""

    target_id: str
    scope: AdministrativeScope
    domain: AdministrativeDomain
    identifier: str
    tenant: str | None

    @classmethod
    def create(
        cls,
        scope: AdministrativeScope,
        domain: AdministrativeDomain,
        identifier: str,
        *,
        tenant: str | None = None,
    ) -> AdministrativeTarget:
        """Build a target with a deterministic, content-addressed ``target_id``."""
        if not isinstance(scope, AdministrativeScope):
            raise AdministrationContractError("target scope must be an AdministrativeScope")
        if not isinstance(domain, AdministrativeDomain):
            raise AdministrationContractError("target domain must be an AdministrativeDomain")
        ident = _require_identifier(identifier)
        # A tenant/workspace-scoped target must name its tenant boundary (fail-closed).
        if scope is AdministrativeScope.PLATFORM and tenant is not None:
            raise AdministrationContractError("a platform-scoped target must not carry a tenant")
        core = {
            "scope": scope.value,
            "domain": domain.value,
            "identifier": ident,
            "tenant": tenant,
        }
        return cls(
            target_id=f"UCOS-ATGT-{content_hash(core)[:16]}",
            scope=scope,
            domain=domain,
            identifier=ident,
            tenant=tenant,
        )

    @classmethod
    def platform(
        cls, domain: AdministrativeDomain = AdministrativeDomain.PLATFORM
    ) -> AdministrativeTarget:
        """The canonical platform-wide administrative target."""
        return cls.create(AdministrativeScope.PLATFORM, domain, "platform")

    def to_dict(self) -> dict[str, Any]:
        return {
            "target_id": self.target_id,
            "scope": self.scope.value,
            "domain": self.domain.value,
            "identifier": self.identifier,
            "tenant": self.tenant,
        }

    def fingerprint(self) -> str:
        return content_hash(self.to_dict())


# --------------------------------------------------------------------------- #
# The published administration contract surface.                             #
# --------------------------------------------------------------------------- #

#: The administration service contract identities the Administration Runtime
#: publishes. Each maps to an EC2-CAP-ADMIN-001 deliverable; consumers bind to these
#: by reference (PL-05, versioned).
_ADMINISTRATION_CONTRACT_NAMES: tuple[tuple[str, str], ...] = (
    ("administration.context.enter", "Administrative context — enter an authorized admin scope."),
    ("administration.configuration.registry", "Configuration — operational settings + controls."),
    ("administration.membership.registry", "Membership administration — assign/revoke admins."),
    ("administration.roles.view", "Role administration — read-only §3.2 admin-grant projection."),
    ("administration.permissions.evaluate", "Permission administration — effective admin verbs."),
    ("administration.audit.trail", "Administrative audit + activity tracking (append-only)."),
    ("administration.search.query", "Administrative search — authorization-scoped discovery."),
    ("administration.runtime.service", "Administration runtime — the admin decision point."),
)

#: Immutable references to the published administration contracts (name + version).
ADMINISTRATION_CONTRACTS: tuple[ContractRef, ...] = tuple(
    ContractRef(name, ADMINISTRATION_CONTRACT_VERSION) for name, _ in _ADMINISTRATION_CONTRACT_NAMES
)


def administration_contract(name: str, description: str = "") -> Contract:
    """Build a versioned administration :class:`Contract` at the contract version."""
    if not isinstance(name, str) or not name:
        raise AdministrationContractError("administration contract name is required")
    try:
        return platform_contract(name, ADMINISTRATION_CONTRACT_VERSION, description)
    except PlatformContractError as exc:  # pragma: no cover - defensive normalisation
        raise AdministrationContractError(str(exc), name=name) from exc


def default_administration_contracts() -> tuple[Contract, ...]:
    """The published administration contracts as concrete :class:`Contract` objects."""
    return tuple(
        administration_contract(name, description)
        for name, description in _ADMINISTRATION_CONTRACT_NAMES
    )


__all__ = [
    "ADMINISTRATION_CONTRACT_VERSION",
    "ADMINISTRATION_GROUP",
    "AdministrativeScope",
    "AdministrativeDomain",
    "AdministrativeAction",
    "OperationalState",
    "AdministrativeTarget",
    "required_permission",
    "all_administrative_scopes",
    "all_administrative_actions",
    "all_operational_states",
    "ADMINISTRATION_CONTRACTS",
    "administration_contract",
    "default_administration_contracts",
]
