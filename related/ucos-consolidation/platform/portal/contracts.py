"""EC2-TASK-000073 — Portal Contracts (EC2-EPIC-003).

The versioned contract surface for the UCOS Platform **Portal & Navigation** layer
(L1 Presentation of the Program architecture, §4) plus the immutable **core
vocabulary** every portal service speaks. It reuses the certified EC-1 contract
machinery through the Platform Foundation
(:func:`~platform.foundation.contracts.platform_contract`,
:class:`~platform.foundation.contracts.ContractRef`) and the Identity Layer's
:class:`~platform.identity.contracts.CapabilityGroup` — the authoritative
authorization unit — so that **navigation and routing are authorization-derived, not
invented**: every navigable surface binds to exactly one §3.2 capability group and
the READ permission that makes it visible.

Vocabulary:
    * :class:`PortalSection` — the coarse grouping a surface appears under in the
      shell (main work surfaces, the account area, administration, governance, and
      observability). Directly satisfies the mission's *Administration Entry*,
      *Governance Entry*, and *Observability Integration* navigation categories.
    * :class:`PortalSurface` — an immutable, content-addressed navigable surface: a
      title, its §3.2 :class:`CapabilityGroup`, its section, a deterministic route
      ``path``, and the :class:`~platform.foundation.identity.Permission` required to
      see it (READ). The sixteen surfaces are transcribed from the §3.2 matrix rows.
    * :class:`EntityKind` — the platform entity types global search spans (≥4;
      acceptance criterion), each bound to the capability group that authorizes it.
    * :data:`PORTAL_CONTRACTS` — the published portal service contracts consumers
      bind to by reference (PL-05, versioned).

All types are **immutable, typed, deterministic, and serializable**, hold no runtime
state, and hold no secret material (SEC-04).
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from platform.foundation.contracts import (
    Contract,
    ContractRef,
    content_hash,
    platform_contract,
)
from platform.foundation.errors import PlatformContractError
from platform.foundation.identity import Permission
from platform.identity.contracts import CapabilityGroup, all_capability_groups
from platform.portal.errors import PortalContractError, PortalSearchError
from typing import Any

#: The semantic version of the Portal contract surface (AR-03/PL-05).
PORTAL_CONTRACT_VERSION = "1.0.0"

#: The route path of the portal home / shell root.
PORTAL_HOME_PATH = "/"


class PortalSection(str, Enum):
    """The coarse grouping a navigable surface appears under in the portal shell.

    The sections encode the mission's distinct navigation categories: the primary
    work surfaces (:attr:`MAIN`), the self-service account area
    (:attr:`ACCOUNT`), the *Administration Entry* (:attr:`ADMINISTRATION`), the
    *Governance Entry* (:attr:`GOVERNANCE`), and the *Observability Integration*
    (:attr:`OBSERVABILITY`).
    """

    MAIN = "main"
    ACCOUNT = "account"
    ADMINISTRATION = "administration"
    GOVERNANCE = "governance"
    OBSERVABILITY = "observability"


def all_portal_sections() -> tuple[PortalSection, ...]:
    """Return every portal section in stable declaration order."""
    return tuple(PortalSection)


#: The presentation metadata for each §3.2 capability group, transcribed from the
#: Program (§2.1 surfaces / §3.2 matrix rows): a human-readable title and the shell
#: section it belongs to. Navigation is derived from this table — never invented.
_SURFACE_TABLE: dict[CapabilityGroup, tuple[str, PortalSection]] = {
    CapabilityGroup.PORTAL_NAVIGATION: ("Portal Home", PortalSection.MAIN),
    CapabilityGroup.IDENTITY_SESSIONS_SELF: ("Account & Sessions", PortalSection.ACCOUNT),
    CapabilityGroup.USER_ROLE_QUOTA_ADMIN: ("Users, Roles & Quotas", PortalSection.ADMINISTRATION),
    CapabilityGroup.WORKSPACE_PROJECT_LIFECYCLE: ("Workspaces & Projects", PortalSection.MAIN),
    CapabilityGroup.BLUEPRINT_AUTHORING: ("Blueprint Authoring", PortalSection.MAIN),
    CapabilityGroup.BLUEPRINT_CATALOG: ("Blueprint Catalog", PortalSection.MAIN),
    CapabilityGroup.GENERATION_REQUESTS: ("Generation Requests", PortalSection.MAIN),
    CapabilityGroup.EXECUTION_DASHBOARD: ("Execution Dashboard", PortalSection.MAIN),
    CapabilityGroup.ARTIFACT_EXPLORER: ("Artifact Explorer", PortalSection.MAIN),
    CapabilityGroup.VALIDATION_EXPLORER: ("Validation Explorer", PortalSection.MAIN),
    CapabilityGroup.CERTIFICATION_LEDGER: ("Certification & Ledger", PortalSection.GOVERNANCE),
    CapabilityGroup.RUNTIME_OPERATIONS: ("Runtime Operations", PortalSection.MAIN),
    CapabilityGroup.MONITORING_OBSERVABILITY: ("Monitoring & Health", PortalSection.OBSERVABILITY),
    CapabilityGroup.ADMINISTRATION_POLICY: (
        "Administration & Policy",
        PortalSection.ADMINISTRATION,
    ),
    CapabilityGroup.AUDIT_TRACEABILITY: ("Audit & Traceability", PortalSection.GOVERNANCE),
    CapabilityGroup.API_ACCESS: ("API Access", PortalSection.MAIN),
}


def _surface_path(group: CapabilityGroup) -> str:
    """Deterministic route path for a surface (the home group maps to ``/``)."""
    if group is CapabilityGroup.PORTAL_NAVIGATION:
        return PORTAL_HOME_PATH
    return f"/{group.value}"


@dataclass(frozen=True, slots=True)
class PortalSurface:
    """An immutable, content-addressed navigable portal surface.

    Each surface corresponds to exactly one §3.2 :class:`CapabilityGroup`; visibility
    in the navigation requires the ``required_permission`` (READ) on that group, so
    the surface set a principal sees is a pure function of the RBAC matrix.
    """

    surface_id: str
    title: str
    group: CapabilityGroup
    section: PortalSection
    path: str
    required_permission: Permission = Permission.READ

    @classmethod
    def create(
        cls,
        title: str,
        group: CapabilityGroup,
        section: PortalSection,
        path: str,
        *,
        required_permission: Permission = Permission.READ,
    ) -> PortalSurface:
        """Build a surface with a deterministic, content-addressed ``surface_id``."""
        if not isinstance(title, str) or not title:
            raise PortalContractError("portal surface requires a title")
        if not isinstance(group, CapabilityGroup):
            raise PortalContractError("portal surface group must be a CapabilityGroup")
        if not isinstance(section, PortalSection):
            raise PortalContractError(
                "portal surface section must be a PortalSection", group=group.value
            )
        if not isinstance(path, str) or not path.startswith("/"):
            raise PortalContractError(
                "portal surface path must be an absolute route", group=group.value
            )
        if not isinstance(required_permission, Permission):
            raise PortalContractError("required_permission must be a Permission", group=group.value)
        core = {
            "title": title,
            "group": group.value,
            "section": section.value,
            "path": path,
            "required_permission": required_permission.value,
        }
        return cls(
            surface_id=f"UCOS-PSUR-{content_hash(core)[:16]}",
            title=title,
            group=group,
            section=section,
            path=path,
            required_permission=required_permission,
        )

    @property
    def is_home(self) -> bool:
        """True iff this is the portal home / shell root surface."""
        return self.group is CapabilityGroup.PORTAL_NAVIGATION

    def to_dict(self) -> dict[str, Any]:
        return {
            "surface_id": self.surface_id,
            "title": self.title,
            "group": self.group.value,
            "section": self.section.value,
            "path": self.path,
            "required_permission": self.required_permission.value,
        }


def default_portal_surfaces() -> tuple[PortalSurface, ...]:
    """The sixteen portal surfaces transcribed from the §3.2 capability groups.

    Ordered by :func:`all_capability_groups` declaration order (deterministic). The
    portal home surface (``portal-navigation``) is first and routes to ``/``.
    """
    surfaces: list[PortalSurface] = []
    for group in all_capability_groups():
        title, section = _SURFACE_TABLE[group]
        surfaces.append(PortalSurface.create(title, group, section, _surface_path(group)))
    return tuple(surfaces)


class EntityKind(str, Enum):
    """The platform entity types global search spans (acceptance: ≥4 kinds).

    Each kind is authorized by exactly one §3.2 capability group (see
    :func:`entity_kind_group`): a principal sees search hits of a kind only when it
    holds READ on that kind's capability group.
    """

    WORKSPACE = "workspace"
    PROJECT = "project"
    BLUEPRINT = "blueprint"
    GENERATION_REQUEST = "generation-request"
    ARTIFACT = "artifact"
    VALIDATION_REPORT = "validation-report"
    CERTIFICATION = "certification"


#: The capability group that authorizes visibility of each search entity kind.
_ENTITY_GROUP: dict[EntityKind, CapabilityGroup] = {
    EntityKind.WORKSPACE: CapabilityGroup.WORKSPACE_PROJECT_LIFECYCLE,
    EntityKind.PROJECT: CapabilityGroup.WORKSPACE_PROJECT_LIFECYCLE,
    EntityKind.BLUEPRINT: CapabilityGroup.BLUEPRINT_CATALOG,
    EntityKind.GENERATION_REQUEST: CapabilityGroup.GENERATION_REQUESTS,
    EntityKind.ARTIFACT: CapabilityGroup.ARTIFACT_EXPLORER,
    EntityKind.VALIDATION_REPORT: CapabilityGroup.VALIDATION_EXPLORER,
    EntityKind.CERTIFICATION: CapabilityGroup.CERTIFICATION_LEDGER,
}


def all_entity_kinds() -> tuple[EntityKind, ...]:
    """Return every search entity kind in stable declaration order."""
    return tuple(EntityKind)


def entity_kind_group(kind: EntityKind) -> CapabilityGroup:
    """Return the capability group that authorizes visibility of ``kind``."""
    if not isinstance(kind, EntityKind):
        raise PortalSearchError("entity kind must be an EntityKind")
    return _ENTITY_GROUP[kind]


# --------------------------------------------------------------------------- #
# The published portal contract surface (L1).                                 #
# --------------------------------------------------------------------------- #

#: The portal service contract identities the Portal Layer publishes. Each maps to an
#: EC2-EPIC-003 deliverable; consumers bind to these by reference (PL-05, versioned).
_PORTAL_CONTRACT_NAMES: tuple[tuple[str, str], ...] = (
    ("portal.shell.entry", "Portal shell — authenticated entry point + landing view."),
    ("portal.navigation.model", "Navigation model — authorized surfaces by section."),
    ("portal.routing.resolve", "Routing model — resolve a path to an authorized surface."),
    ("portal.access.gateway", "Access gateway — identity-integrated portal admission."),
    ("portal.workspace.handoff", "Workspace handoff — portal-to-workspace selection."),
    ("portal.discovery.services", "Service discovery — platform capability access model."),
    ("portal.search.query", "Global search — cross-entity discovery (PC-13)."),
)

#: Immutable references to the published portal contracts (name + version).
PORTAL_CONTRACTS: tuple[ContractRef, ...] = tuple(
    ContractRef(name, PORTAL_CONTRACT_VERSION) for name, _ in _PORTAL_CONTRACT_NAMES
)


def portal_contract(name: str, description: str = "") -> Contract:
    """Build a versioned portal :class:`Contract` at the portal contract version."""
    if not isinstance(name, str) or not name:
        raise PortalContractError("portal contract name is required")
    try:
        return platform_contract(name, PORTAL_CONTRACT_VERSION, description)
    except PlatformContractError as exc:  # pragma: no cover - defensive normalisation
        raise PortalContractError(str(exc), name=name) from exc


def default_portal_contracts() -> tuple[Contract, ...]:
    """The published portal contracts as concrete :class:`Contract` objects."""
    return tuple(portal_contract(name, description) for name, description in _PORTAL_CONTRACT_NAMES)


__all__ = [
    "PORTAL_CONTRACT_VERSION",
    "PORTAL_HOME_PATH",
    "PortalSection",
    "all_portal_sections",
    "PortalSurface",
    "default_portal_surfaces",
    "EntityKind",
    "all_entity_kinds",
    "entity_kind_group",
    "PORTAL_CONTRACTS",
    "portal_contract",
    "default_portal_contracts",
]
