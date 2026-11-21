"""Shared test helpers for the UCOS-EPIC-008 / Terminal T8 Universal Portal tests.

Not a test module (no ``test_`` prefix, not collected); lives under ``platform/tests`` so
it is excluded from coverage. Provides deterministic fixtures: a fake published-service
provider, a Universal Portal built with all core surfaces bound, and session helpers over
the certified Identity Layer (§3.2 RBAC).
"""

from __future__ import annotations

from dataclasses import dataclass
from platform.foundation.identity import Principal, Role
from platform.identity.service import AuthorizationService, build_authorization_service
from platform.universal_portal.applications import ApplicationProvider
from platform.universal_portal.contracts import PortalApplication
from platform.universal_portal.service import (
    UniversalPortalService,
    build_universal_portal_service,
)
from typing import Any


@dataclass(frozen=True, slots=True)
class FakeService:
    """A minimal published-service stand-in exposing a deterministic ``to_dict()``."""

    name: str
    value: int = 1

    def to_dict(self) -> dict[str, Any]:
        return {"service": self.name, "value": self.value}


def core_providers() -> dict[PortalApplication, ApplicationProvider]:
    """Bind the four core operational dashboards to deterministic fake services."""
    return {
        PortalApplication.ADMINISTRATION_PORTAL: lambda: FakeService("administration"),
        PortalApplication.MEASUREMENT_DASHBOARD: lambda: FakeService("measurement"),
        PortalApplication.VALIDATION_DASHBOARD: lambda: FakeService("validation"),
        PortalApplication.CERTIFICATION_DASHBOARD: lambda: FakeService("certification"),
    }


def all_providers() -> dict[PortalApplication, ApplicationProvider]:
    """Bind all six domain surfaces (core + the two explorers) to fake services."""
    providers = core_providers()
    providers[PortalApplication.REGISTRY_EXPLORER] = lambda: FakeService("registry")
    providers[PortalApplication.KNOWLEDGE_GRAPH_EXPLORER] = lambda: FakeService("knowledge")
    return providers


def build_service(
    *,
    providers: dict[PortalApplication, ApplicationProvider] | None = None,
    events: Any | None = None,
    authorization: AuthorizationService | None = None,
) -> tuple[AuthorizationService, UniversalPortalService]:
    """Build a Universal Portal over a default authorization service (core surfaces bound)."""
    auth = authorization or build_authorization_service(events=events)
    service = build_universal_portal_service(
        authorization=auth,
        events=events,
        providers=core_providers() if providers is None else providers,
    )
    return auth, service


def session(
    auth: AuthorizationService,
    *,
    role: Role = Role.PLATFORM_ADMINISTRATOR,
    subject: str = "admin@x",
    tenant: str | None = None,
) -> str:
    """Establish a session for a principal bearing ``role`` and return its session id."""
    established = auth.establish_session(
        Principal.create(subject, [role], tenant=tenant), issued_at=0, ttl=1000
    )
    return established.session_id


__all__ = [
    "FakeService",
    "core_providers",
    "all_providers",
    "build_service",
    "session",
]
