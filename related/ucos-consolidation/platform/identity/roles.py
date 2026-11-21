"""EC2-TASK-000065 — Role Registry (EC2-EPIC-002).

The authoritative, registry-driven encoding of the **§3.2 RBAC matrix** of the
Program. Each of the nine platform :class:`~platform.foundation.identity.Role`
categories is defined as a :class:`RoleDefinition` — a mapping from every
:class:`~platform.identity.contracts.CapabilityGroup` it may touch to a
:class:`RoleGrant` (the permission verbs it holds there, whether that access is
tenant-scoped, and whether it carries the certification *attest* obligation).

This module is a pure, deterministic *value model*: it enforces nothing (the
permission engine resolves and the policy engine enforces) — it is the single source
of truth those engines read. :func:`default_role_registry` seeds the exact matrix
transcribed verbatim from §3.2; ``C`` = create, ``R`` = read, ``X`` = execute,
``A`` = administer, ``(s)`` = tenant/workspace-scoped, ``+attest`` = attestation
obligation.
"""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from dataclasses import dataclass, field
from platform.foundation.contracts import content_hash
from platform.foundation.identity import Permission, Role
from platform.identity.contracts import CapabilityGroup, all_capability_groups
from platform.identity.errors import RoleRegistryError
from typing import Any

_PERMISSION_TOKENS: dict[str, Permission] = {
    "C": Permission.CREATE,
    "R": Permission.READ,
    "X": Permission.EXECUTE,
    "A": Permission.ADMINISTER,
}


@dataclass(frozen=True, slots=True)
class RoleGrant:
    """An immutable grant: what a role may do on one capability group.

    ``scoped`` marks a grant that is always confined to the principal's tenant/
    workspace (§3.2 Partner/Integrator isolation invariant). ``attest`` marks the
    Certification Authority's attestation obligation on the certification ledger
    (record-only; confers no constitutional authority).
    """

    group: CapabilityGroup
    permissions: frozenset[Permission]
    scoped: bool = False
    attest: bool = False

    def __post_init__(self) -> None:
        if not isinstance(self.group, CapabilityGroup):
            raise RoleRegistryError("grant group must be a CapabilityGroup")
        perms = frozenset(self.permissions)
        if not perms:
            raise RoleRegistryError(
                "a role grant must hold at least one permission", group=self.group.value
            )
        if not all(isinstance(p, Permission) for p in perms):
            raise RoleRegistryError(
                "grant permissions must be Permission members", group=self.group.value
            )
        object.__setattr__(self, "permissions", perms)

    def to_dict(self) -> dict[str, Any]:
        return {
            "group": self.group.value,
            "permissions": sorted(p.value for p in self.permissions),
            "scoped": self.scoped,
            "attest": self.attest,
        }


@dataclass(frozen=True, slots=True)
class RoleDefinition:
    """An immutable role definition: a role and its per-capability-group grants."""

    role: Role
    grants: Mapping[CapabilityGroup, RoleGrant] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not isinstance(self.role, Role):
            raise RoleRegistryError("role definition requires a Role")
        for group, grant in self.grants.items():
            if not isinstance(grant, RoleGrant) or grant.group is not group:
                raise RoleRegistryError(
                    "role grant is malformed or keyed under the wrong group",
                    role=self.role.value,
                )
        # Freeze the mapping into an immutable dict.
        object.__setattr__(self, "grants", dict(self.grants))

    def grant_for(self, group: CapabilityGroup) -> RoleGrant | None:
        """Return this role's grant for ``group``, or ``None`` if it has none."""
        return self.grants.get(group)

    @property
    def groups(self) -> tuple[CapabilityGroup, ...]:
        """The capability groups this role holds any grant on (stable order)."""
        return tuple(g for g in all_capability_groups() if g in self.grants)

    def to_dict(self) -> dict[str, Any]:
        return {
            "role": self.role.value,
            "grants": [self.grants[g].to_dict() for g in self.groups],
        }


class RoleRegistry:
    """A deterministic, registry-driven store of role definitions (§3.2)."""

    __slots__ = ("_by_role",)

    def __init__(self) -> None:
        self._by_role: dict[Role, RoleDefinition] = {}

    def register(self, definition: RoleDefinition) -> RoleDefinition:
        """Register a role definition (fail-closed on duplicates)."""
        if not isinstance(definition, RoleDefinition):
            raise RoleRegistryError("a valid RoleDefinition is required")
        if definition.role in self._by_role:
            raise RoleRegistryError("role already registered", role=definition.role.value)
        self._by_role[definition.role] = definition
        return definition

    def register_all(self, definitions: Iterable[RoleDefinition]) -> None:
        for definition in definitions:
            self.register(definition)

    def __contains__(self, role: Role) -> bool:
        return role in self._by_role

    def __len__(self) -> int:
        return len(self._by_role)

    def get(self, role: Role) -> RoleDefinition:
        """Resolve a role definition (raises if absent)."""
        definition = self._by_role.get(role)
        if definition is None:
            raise RoleRegistryError("no such role", role=getattr(role, "value", role))
        return definition

    @property
    def roles(self) -> tuple[Role, ...]:
        """Every registered role in stable declaration order."""
        return tuple(r for r in Role if r in self._by_role)

    def definitions(self) -> tuple[RoleDefinition, ...]:
        """Every role definition in stable declaration order."""
        return tuple(self._by_role[r] for r in self.roles)

    def to_dict(self) -> dict[str, Any]:
        return {
            "role_count": len(self._by_role),
            "roles": [d.to_dict() for d in self.definitions()],
        }

    def fingerprint(self) -> str:
        """A deterministic content hash of the whole matrix (reproducible)."""
        return content_hash(self.to_dict())


# --------------------------------------------------------------------------- #
# The §3.2 RBAC matrix, transcribed verbatim. Each role maps to a 16-token     #
# tuple, one token per capability group in :func:`all_capability_groups` order:#
#   0 portal-navigation        4 blueprint-authoring   8 artifact-explorer     #
#   1 identity-sessions-self    5 blueprint-catalog     9 validation-explorer   #
#   2 user-role-quota-admin     6 generation-requests  10 certification-ledger  #
#   3 workspace-project         7 execution-dashboard  11 runtime-operations    #
#  12 monitoring-observability 13 administration-policy 14 audit-traceability   #
#  15 api-access                                                                #
# Token grammar: "" = no grant (—); "C/R/X/A" = verbs; suffix "(s)" = scoped;   #
# suffix "+attest" = attestation obligation (implies R).                       #
# --------------------------------------------------------------------------- #
_MATRIX: dict[Role, tuple[str, ...]] = {
    Role.PLATFORM_ADMINISTRATOR: (
        "R",
        "A",
        "A",
        "A",
        "R",
        "R",
        "R",
        "R",
        "R",
        "R",
        "R",
        "A",
        "A",
        "A",
        "A",
        "A",
    ),
    Role.ARCHITECT: (
        "R",
        "R",
        "",
        "C/R",
        "C/R",
        "C/R",
        "C/R/X",
        "R",
        "R",
        "R",
        "R",
        "",
        "R",
        "",
        "R",
        "X",
    ),
    Role.DEVELOPER: (
        "R",
        "R",
        "",
        "C/R",
        "C/R",
        "R",
        "C/R/X",
        "R",
        "R",
        "R",
        "R",
        "",
        "R",
        "",
        "R",
        "X",
    ),
    Role.OPERATOR: (
        "R",
        "R",
        "",
        "R",
        "",
        "",
        "",
        "R",
        "R",
        "R",
        "R",
        "X",
        "R",
        "",
        "R",
        "X",
    ),
    Role.AUDITOR: (
        "R",
        "R",
        "",
        "R",
        "R",
        "R",
        "R",
        "R",
        "R",
        "R",
        "R",
        "R",
        "R",
        "R",
        "R",
        "R",
    ),
    Role.CERTIFICATION_AUTHORITY: (
        "R",
        "R",
        "",
        "R",
        "R",
        "R",
        "R",
        "R",
        "R",
        "R",
        "R+attest",
        "R",
        "R",
        "",
        "R",
        "R",
    ),
    Role.BUSINESS_USER: (
        "R",
        "R",
        "",
        "C/R",
        "",
        "R",
        "C/R/X",
        "R",
        "R(s)",
        "R",
        "R",
        "",
        "R",
        "",
        "R",
        "X",
    ),
    Role.PARTNER: (
        "R",
        "R",
        "",
        "R(s)",
        "C/R(s)",
        "R(s)",
        "C/R/X(s)",
        "R(s)",
        "R(s)",
        "R(s)",
        "R(s)",
        "",
        "R(s)",
        "",
        "R(s)",
        "X(s)",
    ),
    Role.INTEGRATOR: (
        "",
        "R",
        "",
        "R(s)",
        "C/R(s)",
        "R(s)",
        "C/R/X(s)",
        "R(s)",
        "R(s)",
        "R(s)",
        "R(s)",
        "",
        "R(s)",
        "",
        "R(s)",
        "X(s)",
    ),
}


def _parse_grant(group: CapabilityGroup, token: str) -> RoleGrant | None:
    """Parse a single §3.2 matrix cell token into a :class:`RoleGrant` (or None)."""
    token = token.strip()
    if not token:
        return None
    scoped = token.endswith("(s)")
    if scoped:
        token = token[:-3]
    attest = token.endswith("+attest")
    if attest:
        token = token[: -len("+attest")]
    verbs = [v for v in token.split("/") if v]
    permissions = set()
    for verb in verbs:
        permission = _PERMISSION_TOKENS.get(verb)
        if permission is None:
            raise RoleRegistryError(
                "unknown permission verb in RBAC matrix", group=group.value, verb=verb
            )
        permissions.add(permission)
    if attest:
        # Attestation is a read-plus obligation; ensure READ is present.
        permissions.add(Permission.READ)
    return RoleGrant(
        group=group,
        permissions=frozenset(permissions),
        scoped=scoped,
        attest=attest,
    )


def default_role_definitions() -> tuple[RoleDefinition, ...]:
    """The nine role definitions transcribed from the §3.2 RBAC matrix."""
    groups = all_capability_groups()
    definitions: list[RoleDefinition] = []
    for role in Role:
        tokens = _MATRIX[role]
        if len(tokens) != len(groups):
            raise RoleRegistryError(  # pragma: no cover - guards transcription errors
                "RBAC matrix row width mismatch", role=role.value
            )
        grants: dict[CapabilityGroup, RoleGrant] = {}
        for group, token in zip(groups, tokens, strict=True):
            grant = _parse_grant(group, token)
            if grant is not None:
                grants[group] = grant
        definitions.append(RoleDefinition(role=role, grants=grants))
    return tuple(definitions)


def default_role_registry() -> RoleRegistry:
    """A role registry seeded with the complete §3.2 RBAC matrix (all nine roles)."""
    registry = RoleRegistry()
    registry.register_all(default_role_definitions())
    return registry


__all__ = [
    "RoleGrant",
    "RoleDefinition",
    "RoleRegistry",
    "default_role_definitions",
    "default_role_registry",
]
