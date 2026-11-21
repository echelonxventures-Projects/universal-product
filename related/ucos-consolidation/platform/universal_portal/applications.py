"""UCOS-EPIC-008 / Terminal T8 — Universal Portal application read model.

The deterministic, fail-closed read model over the eight Terminal-T8 applications. Each
application is bound (by reference) to a **published** backing service via an
:class:`ApplicationProvider` — a zero-argument callable returning the composed service
(or read model) that exposes a ``to_dict()`` deterministic snapshot. The Universal Portal
**never re-implements** a domain: it only reads the published snapshot of the service it
was handed.

    * :class:`ApplicationProvider` — the binding: ``Callable[[], object]`` returning a
      published service exposing ``to_dict()``.
    * :class:`ApplicationRegistry` — the deterministic registry of the eight applications
      and their (optional) provider bindings; a pure metadata + snapshot model.
    * :class:`ApplicationDescriptor` — the immutable, serializable description of one
      application (title, group, section, consumed contracts, bound?).
    * :class:`ApplicationView` — the immutable, content-addressed result of opening an
      application for one caller: whether the caller is authorized, whether the surface is
      bound/available, and the published snapshot when both hold (fail-closed otherwise).

The registry holds no session state and performs no authorization itself — the
:class:`~platform.universal_portal.service.UniversalPortalService` composes it with the
portal access gateway to render authorized views.
"""

from __future__ import annotations

from collections.abc import Callable, Mapping
from dataclasses import dataclass
from platform.foundation.contracts import content_hash
from platform.foundation.identity import Permission
from platform.identity.contracts import CapabilityGroup
from platform.universal_portal.contracts import (
    ApplicationSection,
    PortalApplication,
    UniversalPortalSurface,
    all_portal_applications,
    application_group,
    application_section,
    application_title,
    consumed_contract_refs,
    required_permission,
)
from platform.universal_portal.errors import ApplicationBindingError
from typing import Any

#: A binding to a published backing service: a zero-arg callable returning an object that
#: exposes a deterministic ``to_dict()`` snapshot (all EC-2 services do).
ApplicationProvider = Callable[[], Any]


@dataclass(frozen=True, slots=True)
class ApplicationDescriptor:
    """An immutable, serializable description of one Universal Portal application."""

    application: PortalApplication
    title: str
    group: CapabilityGroup
    section: ApplicationSection
    required_permission: Permission
    consumed_contracts: tuple[str, ...]
    bound: bool

    @classmethod
    def create(cls, application: PortalApplication, *, bound: bool) -> ApplicationDescriptor:
        surface = UniversalPortalSurface.of(application)
        return cls(
            application=application,
            title=surface.title,
            group=surface.group,
            section=surface.section,
            required_permission=surface.required_permission,
            consumed_contracts=surface.consumed_contracts,
            bound=bound,
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "application": self.application.value,
            "title": self.title,
            "group": self.group.value,
            "section": self.section.value,
            "required_permission": self.required_permission.value,
            "consumed_contracts": list(self.consumed_contracts),
            "bound": self.bound,
        }


@dataclass(frozen=True, slots=True)
class ApplicationView:
    """An immutable, content-addressed rendering of an opened application for one caller."""

    application: PortalApplication
    title: str
    group: CapabilityGroup
    section: ApplicationSection
    authorized: bool
    available: bool
    reason: str
    consumed_contracts: tuple[str, ...]
    snapshot: dict[str, Any] | None
    view_id: str = ""

    @classmethod
    def create(
        cls,
        application: PortalApplication,
        *,
        authorized: bool,
        available: bool,
        reason: str,
        snapshot: dict[str, Any] | None,
    ) -> ApplicationView:
        surface = UniversalPortalSurface.of(application)
        core = {
            "application": application.value,
            "authorized": authorized,
            "available": available,
            "reason": reason,
            "consumed_contracts": list(surface.consumed_contracts),
            "snapshot": snapshot,
        }
        return cls(
            application=application,
            title=surface.title,
            group=surface.group,
            section=surface.section,
            authorized=authorized,
            available=available,
            reason=reason,
            consumed_contracts=surface.consumed_contracts,
            snapshot=snapshot,
            view_id=f"UCOS-T8VEW-{content_hash(core)[:16]}",
        )

    @property
    def served(self) -> bool:
        """True iff the caller is authorized and the surface produced a snapshot."""
        return self.authorized and self.available and self.snapshot is not None

    def to_dict(self) -> dict[str, Any]:
        return {
            "view_id": self.view_id,
            "application": self.application.value,
            "title": self.title,
            "group": self.group.value,
            "section": self.section.value,
            "authorized": self.authorized,
            "available": self.available,
            "served": self.served,
            "reason": self.reason,
            "consumed_contracts": list(self.consumed_contracts),
            "snapshot": self.snapshot,
        }


class ApplicationRegistry:
    """A deterministic registry of the eight applications and their provider bindings."""

    __slots__ = ("_providers",)

    def __init__(self, providers: Mapping[PortalApplication, ApplicationProvider] | None = None):
        bindings: dict[PortalApplication, ApplicationProvider] = {}
        for application, provider in (providers or {}).items():
            if not isinstance(application, PortalApplication):
                raise ApplicationBindingError(
                    "provider keys must be PortalApplication members",
                    application=str(application),
                )
            if not callable(provider):
                raise ApplicationBindingError(
                    "an application provider must be callable",
                    application=application.value,
                )
            bindings[application] = provider
        self._providers = bindings

    # -- metadata ---------------------------------------------------------------

    @staticmethod
    def applications() -> tuple[PortalApplication, ...]:
        """Every application in stable declaration order."""
        return all_portal_applications()

    def is_bound(self, application: PortalApplication) -> bool:
        """True iff a backing provider is bound for ``application`` (fail-closed)."""
        if not isinstance(application, PortalApplication):
            raise ApplicationBindingError("application must be a PortalApplication")
        return application in self._providers

    @property
    def bound_count(self) -> int:
        return len(self._providers)

    def descriptor(self, application: PortalApplication) -> ApplicationDescriptor:
        """The immutable descriptor for ``application``."""
        if not isinstance(application, PortalApplication):
            raise ApplicationBindingError("application must be a PortalApplication")
        return ApplicationDescriptor.create(application, bound=self.is_bound(application))

    def descriptors(self) -> tuple[ApplicationDescriptor, ...]:
        """Every application descriptor in stable declaration order."""
        return tuple(self.descriptor(app) for app in self.applications())

    def surface(self, application: PortalApplication) -> UniversalPortalSurface:
        """The published surface descriptor for ``application``."""
        return UniversalPortalSurface.of(application)

    # -- snapshots (published read-only) ----------------------------------------

    def snapshot(self, application: PortalApplication) -> dict[str, Any] | None:
        """The published ``to_dict()`` snapshot of the bound service, or ``None``.

        Consumes only the published API of the bound service. A binding that is not a
        deterministic ``to_dict()`` provider fails loudly (fail-closed) so a malformed
        binding can never be silently served.
        """
        if not isinstance(application, PortalApplication):
            raise ApplicationBindingError("application must be a PortalApplication")
        provider = self._providers.get(application)
        if provider is None:
            return None
        obj = provider()
        to_dict = getattr(obj, "to_dict", None)
        if not callable(to_dict):
            raise ApplicationBindingError(
                "a bound application provider must expose a callable to_dict()",
                application=application.value,
            )
        result = to_dict()
        if not isinstance(result, dict):
            raise ApplicationBindingError(
                "a bound application to_dict() must return a mapping",
                application=application.value,
            )
        return result

    # -- helpers ----------------------------------------------------------------

    def group(self, application: PortalApplication) -> CapabilityGroup:
        return application_group(application)

    def section(self, application: PortalApplication) -> ApplicationSection:
        return application_section(application)

    def title(self, application: PortalApplication) -> str:
        return application_title(application)

    def permission(self, application: PortalApplication) -> Permission:
        return required_permission(application)

    def consumed_contracts(self, application: PortalApplication) -> tuple[str, ...]:
        return tuple(f"{ref.name}@{ref.version}" for ref in consumed_contract_refs(application))

    def to_dict(self) -> dict[str, Any]:
        return {
            "application_count": len(self.applications()),
            "bound_count": self.bound_count,
            "applications": [d.to_dict() for d in self.descriptors()],
        }

    def fingerprint(self) -> str:
        """A deterministic fingerprint over the application catalog + bindings."""
        return content_hash(self.to_dict())


__all__ = [
    "ApplicationProvider",
    "ApplicationDescriptor",
    "ApplicationView",
    "ApplicationRegistry",
]
