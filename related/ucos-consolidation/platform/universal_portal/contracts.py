"""UCOS-EPIC-008 / Terminal T8 — Universal Portal contracts & vocabulary.

The versioned contract surface for the **Universal Portal** (L1 presentation composition)
plus the immutable core vocabulary every Universal Portal component speaks. It reuses the
certified EC-1 contract machinery through the Platform Foundation
(:func:`~platform.foundation.contracts.platform_contract`,
:class:`~platform.foundation.contracts.ContractRef`) and the Identity Layer's
:class:`~platform.identity.contracts.CapabilityGroup` — the authoritative authorization
unit — so that **every T8 surface is authorization-derived, not invented**: each of the
eight portal applications binds to exactly one §3.2 capability group and the READ
permission that makes it visible/openable.

Vocabulary:
    * :class:`PortalApplication` — the eight Terminal-T8 surfaces (Administration Portal,
      Registry Explorer, Knowledge Graph Explorer, Measurement/Validation/Certification
      Dashboards, Developer Portal, Documentation Portal).
    * :class:`ApplicationSection` — the coarse grouping a surface appears under.
    * :class:`UniversalPortalSurface` — an immutable, content-addressed surface descriptor:
      an application, its title, its §3.2 capability group, its section, the required
      permission (READ), and the published contracts it consumes **by reference**.
    * :data:`UNIVERSAL_PORTAL_CONTRACTS` — the published Universal Portal service contracts
      consumers bind to by reference (PL-05, versioned).

All types are **immutable, typed, deterministic, and serializable**, hold no runtime state,
and hold no secret material (SEC-04). Each application consumes only **published** contract
identities of the underlying platform/engine services (never their internals).
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from platform.administration.contracts import ADMINISTRATION_CONTRACTS
from platform.certification.contracts import CERTIFICATION_CONSOLE_CONTRACTS
from platform.coverage.contracts import COVERAGE_CONTRACTS
from platform.foundation.contracts import (
    Contract,
    ContractRef,
    content_hash,
    platform_contract,
)
from platform.foundation.errors import PlatformContractError
from platform.foundation.identity import Permission
from platform.identity.contracts import CapabilityGroup
from platform.portal.contracts import PORTAL_CONTRACTS
from platform.universal_portal.errors import UniversalPortalContractError
from platform.validation.contracts import VALIDATION_CONSOLE_CONTRACTS
from typing import Any

#: The semantic version of the Universal Portal contract surface (AR-03/PL-05).
UNIVERSAL_PORTAL_CONTRACT_VERSION = "1.0.0"

#: The published contract identity of the certified EC-1 registry read adapter
#: (``engine.registry.REGISTRY_READ_CONTRACT``), referenced here by name+version so the
#: Registry Explorer consumes it purely by published reference (PL-05).
ENGINE_REGISTRY_CONTRACT = "registry.read"

#: The published contract identity of the certified EC-1 Universal Knowledge & Decision
#: Architecture (``engine.knowledge.UKDA_CONTRACT``), referenced by name+version.
ENGINE_KNOWLEDGE_CONTRACT = "knowledge.ukda"

_ENGINE_CONTRACT_VERSION = "1.0.0"


class ApplicationSection(str, Enum):
    """The coarse grouping a Universal Portal application appears under."""

    ADMINISTRATION = "administration"
    EXPLORATION = "exploration"
    DASHBOARDS = "dashboards"
    DEVELOPER = "developer"
    DOCUMENTATION = "documentation"


class PortalApplication(str, Enum):
    """The eight Terminal-T8 Universal Portal surfaces."""

    ADMINISTRATION_PORTAL = "administration-portal"
    REGISTRY_EXPLORER = "registry-explorer"
    KNOWLEDGE_GRAPH_EXPLORER = "knowledge-graph-explorer"
    MEASUREMENT_DASHBOARD = "measurement-dashboard"
    VALIDATION_DASHBOARD = "validation-dashboard"
    CERTIFICATION_DASHBOARD = "certification-dashboard"
    DEVELOPER_PORTAL = "developer-portal"
    DOCUMENTATION_PORTAL = "documentation-portal"


def all_portal_applications() -> tuple[PortalApplication, ...]:
    """Return every portal application in stable declaration order."""
    return tuple(PortalApplication)


#: title · authorizing §3.2 capability group · section — for each application. The portal
#: creates **no new authority**: every application reuses an existing capability group.
_APPLICATION_TABLE: dict[PortalApplication, tuple[str, CapabilityGroup, ApplicationSection]] = {
    PortalApplication.ADMINISTRATION_PORTAL: (
        "Administration Portal",
        CapabilityGroup.ADMINISTRATION_POLICY,
        ApplicationSection.ADMINISTRATION,
    ),
    PortalApplication.REGISTRY_EXPLORER: (
        "Registry Explorer",
        CapabilityGroup.API_ACCESS,
        ApplicationSection.EXPLORATION,
    ),
    PortalApplication.KNOWLEDGE_GRAPH_EXPLORER: (
        "Knowledge Graph Explorer",
        CapabilityGroup.AUDIT_TRACEABILITY,
        ApplicationSection.EXPLORATION,
    ),
    PortalApplication.MEASUREMENT_DASHBOARD: (
        "Measurement Dashboard",
        CapabilityGroup.MONITORING_OBSERVABILITY,
        ApplicationSection.DASHBOARDS,
    ),
    PortalApplication.VALIDATION_DASHBOARD: (
        "Validation Dashboard",
        CapabilityGroup.VALIDATION_EXPLORER,
        ApplicationSection.DASHBOARDS,
    ),
    PortalApplication.CERTIFICATION_DASHBOARD: (
        "Certification Dashboard",
        CapabilityGroup.CERTIFICATION_LEDGER,
        ApplicationSection.DASHBOARDS,
    ),
    PortalApplication.DEVELOPER_PORTAL: (
        "Developer Portal",
        CapabilityGroup.API_ACCESS,
        ApplicationSection.DEVELOPER,
    ),
    PortalApplication.DOCUMENTATION_PORTAL: (
        "Documentation Portal",
        CapabilityGroup.PORTAL_NAVIGATION,
        ApplicationSection.DOCUMENTATION,
    ),
}

#: The published Universal Portal contract each application publishes (its own view).
_APPLICATION_CONTRACT: dict[PortalApplication, str] = {
    PortalApplication.ADMINISTRATION_PORTAL: "universal-portal.administration.view",
    PortalApplication.REGISTRY_EXPLORER: "universal-portal.registry.explore",
    PortalApplication.KNOWLEDGE_GRAPH_EXPLORER: "universal-portal.knowledge.explore",
    PortalApplication.MEASUREMENT_DASHBOARD: "universal-portal.measurement.dashboard",
    PortalApplication.VALIDATION_DASHBOARD: "universal-portal.validation.dashboard",
    PortalApplication.CERTIFICATION_DASHBOARD: "universal-portal.certification.dashboard",
    PortalApplication.DEVELOPER_PORTAL: "universal-portal.developer.catalog",
    PortalApplication.DOCUMENTATION_PORTAL: "universal-portal.documentation.index",
}


def _self_ref(application: PortalApplication) -> ContractRef:
    """The Universal Portal contract reference this application publishes."""
    return ContractRef(_APPLICATION_CONTRACT[application], UNIVERSAL_PORTAL_CONTRACT_VERSION)


def _portal_discovery_ref() -> ContractRef:
    """The published portal service-discovery contract the Registry Explorer consumes."""
    for ref in PORTAL_CONTRACTS:
        if ref.name == "portal.discovery.services":
            return ref
    # Defensive: the portal shell always publishes discovery; fail-closed if it does not.
    raise UniversalPortalContractError(  # pragma: no cover - portal shell invariant
        "portal service-discovery contract is not published"
    )


#: The **published** contracts each application consumes (by reference only, PL-05).
def consumed_contract_refs(application: PortalApplication) -> tuple[ContractRef, ...]:
    """The published contract identities an application consumes (deterministic order)."""
    if not isinstance(application, PortalApplication):
        raise UniversalPortalContractError("application must be a PortalApplication")
    if application is PortalApplication.ADMINISTRATION_PORTAL:
        return tuple(ADMINISTRATION_CONTRACTS)
    if application is PortalApplication.REGISTRY_EXPLORER:
        return (
            _portal_discovery_ref(),
            ContractRef(ENGINE_REGISTRY_CONTRACT, _ENGINE_CONTRACT_VERSION),
        )
    if application is PortalApplication.KNOWLEDGE_GRAPH_EXPLORER:
        return (ContractRef(ENGINE_KNOWLEDGE_CONTRACT, _ENGINE_CONTRACT_VERSION),)
    if application is PortalApplication.MEASUREMENT_DASHBOARD:
        return tuple(COVERAGE_CONTRACTS)
    if application is PortalApplication.VALIDATION_DASHBOARD:
        return tuple(VALIDATION_CONSOLE_CONTRACTS)
    if application is PortalApplication.CERTIFICATION_DASHBOARD:
        return tuple(CERTIFICATION_CONSOLE_CONTRACTS)
    # Developer + Documentation portals publish (and thus "consume") their own view.
    return (_self_ref(application),)


def application_group(application: PortalApplication) -> CapabilityGroup:
    """The §3.2 capability group that authorizes an application (fail-closed)."""
    if not isinstance(application, PortalApplication):
        raise UniversalPortalContractError("application must be a PortalApplication")
    return _APPLICATION_TABLE[application][1]


def application_section(application: PortalApplication) -> ApplicationSection:
    """The section an application appears under (fail-closed)."""
    if not isinstance(application, PortalApplication):
        raise UniversalPortalContractError("application must be a PortalApplication")
    return _APPLICATION_TABLE[application][2]


def application_title(application: PortalApplication) -> str:
    """The human-readable title of an application (fail-closed)."""
    if not isinstance(application, PortalApplication):
        raise UniversalPortalContractError("application must be a PortalApplication")
    return _APPLICATION_TABLE[application][0]


def required_permission(application: PortalApplication) -> Permission:
    """The permission required to open an application (READ — read/inspection-only)."""
    if not isinstance(application, PortalApplication):
        raise UniversalPortalContractError("application must be a PortalApplication")
    return Permission.READ


@dataclass(frozen=True, slots=True)
class UniversalPortalSurface:
    """An immutable, content-addressed Universal Portal application surface descriptor."""

    surface_id: str
    application: PortalApplication
    title: str
    group: CapabilityGroup
    section: ApplicationSection
    required_permission: Permission
    consumed_contracts: tuple[str, ...]

    @classmethod
    def of(cls, application: PortalApplication) -> UniversalPortalSurface:
        """Build the surface descriptor for ``application`` (deterministic)."""
        if not isinstance(application, PortalApplication):
            raise UniversalPortalContractError("application must be a PortalApplication")
        title, group, section = _APPLICATION_TABLE[application]
        permission = required_permission(application)
        contracts = tuple(
            f"{ref.name}@{ref.version}" for ref in consumed_contract_refs(application)
        )
        core = {
            "application": application.value,
            "title": title,
            "group": group.value,
            "section": section.value,
            "required_permission": permission.value,
            "consumed_contracts": list(contracts),
        }
        return cls(
            surface_id=f"UCOS-T8SUR-{content_hash(core)[:16]}",
            application=application,
            title=title,
            group=group,
            section=section,
            required_permission=permission,
            consumed_contracts=contracts,
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "surface_id": self.surface_id,
            "application": self.application.value,
            "title": self.title,
            "group": self.group.value,
            "section": self.section.value,
            "required_permission": self.required_permission.value,
            "consumed_contracts": list(self.consumed_contracts),
        }


def default_universal_portal_surfaces() -> tuple[UniversalPortalSurface, ...]:
    """The eight Universal Portal surfaces in stable application-declaration order."""
    return tuple(UniversalPortalSurface.of(app) for app in all_portal_applications())


# --------------------------------------------------------------------------- #
# The published Universal Portal contract surface (L1, T8).                   #
# --------------------------------------------------------------------------- #

_UNIVERSAL_PORTAL_CONTRACT_NAMES: tuple[tuple[str, str], ...] = (
    ("universal-portal.shell.compose", "Universal Portal shell — composed T8 entry point."),
    ("universal-portal.administration.view", "Administration Portal over platform.administration."),
    ("universal-portal.registry.explore", "Registry Explorer over the platform service directory."),
    ("universal-portal.knowledge.explore", "Knowledge Graph Explorer over engine.knowledge."),
    ("universal-portal.measurement.dashboard", "Measurement Dashboard over platform.coverage."),
    ("universal-portal.validation.dashboard", "Validation Dashboard over platform.validation."),
    ("universal-portal.certification.dashboard", "Certification Dashboard over certification."),
    ("universal-portal.developer.catalog", "Developer Portal — the published API catalog."),
    ("universal-portal.documentation.index", "Documentation Portal — the documentation index."),
)

#: Immutable references to the published Universal Portal contracts (name + version).
UNIVERSAL_PORTAL_CONTRACTS: tuple[ContractRef, ...] = tuple(
    ContractRef(name, UNIVERSAL_PORTAL_CONTRACT_VERSION)
    for name, _ in _UNIVERSAL_PORTAL_CONTRACT_NAMES
)


def universal_portal_contract(name: str, description: str = "") -> Contract:
    """Build a versioned Universal Portal :class:`Contract` at the T8 contract version."""
    if not isinstance(name, str) or not name:
        raise UniversalPortalContractError("universal portal contract name is required")
    try:
        return platform_contract(name, UNIVERSAL_PORTAL_CONTRACT_VERSION, description)
    except PlatformContractError as exc:  # pragma: no cover - defensive normalisation
        raise UniversalPortalContractError(str(exc), name=name) from exc


def default_universal_portal_contracts() -> tuple[Contract, ...]:
    """The published Universal Portal contracts as concrete :class:`Contract` objects."""
    return tuple(
        universal_portal_contract(name, description)
        for name, description in _UNIVERSAL_PORTAL_CONTRACT_NAMES
    )


__all__ = [
    "UNIVERSAL_PORTAL_CONTRACT_VERSION",
    "ENGINE_REGISTRY_CONTRACT",
    "ENGINE_KNOWLEDGE_CONTRACT",
    "ApplicationSection",
    "PortalApplication",
    "all_portal_applications",
    "application_group",
    "application_section",
    "application_title",
    "required_permission",
    "consumed_contract_refs",
    "UniversalPortalSurface",
    "default_universal_portal_surfaces",
    "UNIVERSAL_PORTAL_CONTRACTS",
    "universal_portal_contract",
    "default_universal_portal_contracts",
]
