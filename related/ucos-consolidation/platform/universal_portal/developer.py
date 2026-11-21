"""UCOS-EPIC-008 / Terminal T8 — Developer Portal (API catalog).

The **developer experience** surface: a deterministic, content-addressed catalog of every
**published** API the Universal Portal exposes and consumes. It is a pure read model over
the published contract identities of the eight applications, the Universal Portal's own
published contracts, and — when a portal :class:`~platform.portal.discovery.ServiceDirectory`
is bound — the live platform service and capability directory. It invents no API: every
entry is a published contract reference (name@version) bound to the §3.2 capability group
and READ permission a developer needs to consume it.

It authorizes nothing itself (the :class:`~platform.universal_portal.service.UniversalPortalService`
gates the catalog on API-access READ); it holds no session state; it starts no server.
"""

from __future__ import annotations

from dataclasses import dataclass
from platform.foundation.contracts import content_hash
from platform.portal.discovery import ServiceDirectory
from platform.universal_portal.contracts import (
    UNIVERSAL_PORTAL_CONTRACTS,
    PortalApplication,
    all_portal_applications,
    application_group,
    application_section,
    consumed_contract_refs,
    required_permission,
)
from platform.universal_portal.errors import DeveloperPortalError
from typing import Any


@dataclass(frozen=True, slots=True)
class ApiEntry:
    """An immutable, content-addressed developer catalog entry for one published API."""

    entry_id: str
    application: str
    section: str
    contract_name: str
    contract_version: str
    group: str
    required_permission: str

    @classmethod
    def create(
        cls,
        *,
        application: str,
        section: str,
        contract_name: str,
        contract_version: str,
        group: str,
        required_permission: str,
    ) -> ApiEntry:
        core = {
            "application": application,
            "section": section,
            "contract_name": contract_name,
            "contract_version": contract_version,
            "group": group,
            "required_permission": required_permission,
        }
        return cls(
            entry_id=f"UCOS-T8API-{content_hash(core)[:16]}",
            application=application,
            section=section,
            contract_name=contract_name,
            contract_version=contract_version,
            group=group,
            required_permission=required_permission,
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "entry_id": self.entry_id,
            "application": self.application,
            "section": self.section,
            "contract_name": self.contract_name,
            "contract_version": self.contract_version,
            "group": self.group,
            "required_permission": self.required_permission,
        }


@dataclass(frozen=True, slots=True)
class DeveloperCatalog:
    """An immutable, content-addressed catalog of the published developer APIs."""

    entries: tuple[ApiEntry, ...]
    platform_contracts: tuple[str, ...]
    service_names: tuple[str, ...]
    capability_ids: tuple[str, ...]
    catalog_id: str = ""

    @classmethod
    def create(
        cls,
        *,
        entries: tuple[ApiEntry, ...],
        platform_contracts: tuple[str, ...],
        service_names: tuple[str, ...],
        capability_ids: tuple[str, ...],
    ) -> DeveloperCatalog:
        core = {
            "entries": [e.to_dict() for e in entries],
            "platform_contracts": list(platform_contracts),
            "service_names": list(service_names),
            "capability_ids": list(capability_ids),
        }
        return cls(
            entries=entries,
            platform_contracts=platform_contracts,
            service_names=service_names,
            capability_ids=capability_ids,
            catalog_id=f"UCOS-T8CAT-{content_hash(core)[:16]}",
        )

    @property
    def api_count(self) -> int:
        return len(self.entries)

    def to_dict(self) -> dict[str, Any]:
        return {
            "catalog_id": self.catalog_id,
            "api_count": self.api_count,
            "entries": [e.to_dict() for e in self.entries],
            "platform_contracts": list(self.platform_contracts),
            "service_count": len(self.service_names),
            "service_names": list(self.service_names),
            "capability_count": len(self.capability_ids),
            "capability_ids": list(self.capability_ids),
        }

    def fingerprint(self) -> str:
        return content_hash(self.to_dict())


class DeveloperPortal:
    """A deterministic read model over every published Universal Portal API."""

    __slots__ = ("_directory",)

    def __init__(self, directory: ServiceDirectory | None = None) -> None:
        if directory is not None and not isinstance(directory, ServiceDirectory):
            raise DeveloperPortalError("directory must be a ServiceDirectory when provided")
        self._directory = directory

    @property
    def bound_directory(self) -> bool:
        """True iff a platform service directory is bound (live service/capability API)."""
        return self._directory is not None

    def catalog(self) -> DeveloperCatalog:
        """Build the deterministic developer API catalog (pure, no authorization)."""
        entries: list[ApiEntry] = []
        for application in all_portal_applications():
            group = application_group(application).value
            permission = required_permission(application).value
            section = application_section(application).value
            for ref in consumed_contract_refs(application):
                entries.append(
                    ApiEntry.create(
                        application=application.value,
                        section=section,
                        contract_name=ref.name,
                        contract_version=str(ref.version),
                        group=group,
                        required_permission=permission,
                    )
                )
        ordered = tuple(sorted(entries, key=lambda e: (e.application, e.contract_name)))
        platform_contracts = tuple(
            f"{ref.name}@{ref.version}" for ref in UNIVERSAL_PORTAL_CONTRACTS
        )
        service_names: tuple[str, ...] = ()
        capability_ids: tuple[str, ...] = ()
        if self._directory is not None:
            service_names = tuple(self._directory.service_names)
            capability_ids = tuple(self._directory.capability_ids())
        return DeveloperCatalog.create(
            entries=ordered,
            platform_contracts=platform_contracts,
            service_names=service_names,
            capability_ids=capability_ids,
        )

    def entries_for(self, application: PortalApplication) -> tuple[ApiEntry, ...]:
        """The published API entries for a single application (fail-closed)."""
        if not isinstance(application, PortalApplication):
            raise DeveloperPortalError("application must be a PortalApplication")
        return tuple(e for e in self.catalog().entries if e.application == application.value)


__all__ = ["ApiEntry", "DeveloperCatalog", "DeveloperPortal"]
