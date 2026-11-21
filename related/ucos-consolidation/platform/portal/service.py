"""EC2-TASK-000080 — Portal Service (EC2-EPIC-003).

The single, governed **portal composition point** (L1 Presentation of the Program
architecture) that composes the whole portal into one entry point — the *primary
entry point into the UCOS platform*:

    PortalAccessGateway · NavigationModel · Router · WorkspaceSelector ·
    ServiceDirectory · ObservabilityView · GlobalSearch

It is a strictly **additive** layer: it authenticates/authorizes only through the
certified EC-2 Identity Layer (L7), observes only through the EC-2 Observability Layer
(L8), discovers only through the EC-2 Foundation registries (L4/L6 metadata) — it
re-implements none of them, modifies none of them, writes nothing to the certified
corpus (DP-03), and starts no server or socket (this is the deterministic presentation
*model*, not a running web tier). Every portal action is fail-closed and, because it
publishes onto the Platform Foundation event bus, is captured by observability as a
governed action (PC-16).

The service is deterministic: the same identity registrations, surfaces, search index,
and ordered sequence of calls yield the same :class:`PortalEvidence` fingerprint. This
module also provides :func:`build_portal_service` (default wiring) and
:func:`bootstrap_portal` (composes identity + observability + portal onto a
:class:`~platform.foundation.bootstrap.PlatformContext`, publishes the portal
contracts, and emits a composition event).
"""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from platform.foundation.capabilities import CapabilityCatalog
from platform.foundation.contracts import content_hash
from platform.foundation.events import EventBus
from platform.foundation.services import ServiceRegistry
from platform.identity.contracts import AccessDecision, Decision
from platform.identity.service import AuthorizationService, bootstrap_identity
from platform.observability.contracts import HealthStatus
from platform.observability.service import ObservabilityService, bootstrap_observability
from platform.portal.access import PortalAccessGateway, PortalAdmission
from platform.portal.contracts import (
    PORTAL_CONTRACTS,
    PortalSurface,
    default_portal_contracts,
    default_portal_surfaces,
)
from platform.portal.discovery import ObservabilityView, ServiceDirectory
from platform.portal.errors import PortalServiceError
from platform.portal.navigation import AccessibilityReport, Navigation, NavigationModel
from platform.portal.routing import Route, Router
from platform.portal.search import GlobalSearch, SearchIndex, SearchResponse, default_search_index
from platform.portal.workspace import WorkspaceHandoff, WorkspaceSelector
from typing import Any

#: The event emitted when the Portal Layer is composed onto a context.
PORTAL_BOOTSTRAP_EVENT = "portal.bootstrap.completed"

#: The governed event emitted when a session enters the portal (observed as PC-16).
PORTAL_ENTERED_EVENT = "portal.session.entered"


@dataclass(frozen=True, slots=True)
class PortalView:
    """An immutable, content-addressed rendering of the portal for one caller."""

    session_id: str
    principal_id: str
    navigation: Navigation
    landing_path: str
    accessibility: AccessibilityReport
    view_id: str = ""

    @classmethod
    def create(
        cls,
        *,
        session_id: str,
        principal_id: str,
        navigation: Navigation,
        landing_path: str,
        accessibility: AccessibilityReport,
    ) -> PortalView:
        core = {
            "principal_id": principal_id,
            "navigation": navigation.to_dict(),
            "landing_path": landing_path,
            "accessibility": accessibility.to_dict(),
        }
        return cls(
            session_id=session_id,
            principal_id=principal_id,
            navigation=navigation,
            landing_path=landing_path,
            accessibility=accessibility,
            view_id=f"UCOS-PVEW-{content_hash(core)[:16]}",
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "view_id": self.view_id,
            "session_id": self.session_id,
            "principal_id": self.principal_id,
            "landing_path": self.landing_path,
            "navigation": self.navigation.to_dict(),
            "accessibility": self.accessibility.to_dict(),
        }


@dataclass(frozen=True, slots=True)
class NavigationResult:
    """An immutable result of resolving + authorizing a navigation to a path."""

    path: str
    authorized: bool
    route: Route
    decision: AccessDecision

    @property
    def reason(self) -> str:
        return self.decision.reason

    def to_dict(self) -> dict[str, Any]:
        return {
            "path": self.path,
            "authorized": self.authorized,
            "route": self.route.to_dict(),
            "decision": self.decision.to_dict(),
        }


@dataclass(frozen=True, slots=True)
class PortalEvidence:
    """A deterministic, content-addressed record of portal state (evidence)."""

    surfaces_fingerprint: str
    routes_fingerprint: str
    search_index_fingerprint: str
    accessibility_passed: bool
    surface_count: int
    contract_count: int
    entry_count: int
    evidence_id: str = ""

    @classmethod
    def create(
        cls,
        *,
        surfaces_fingerprint: str,
        routes_fingerprint: str,
        search_index_fingerprint: str,
        accessibility_passed: bool,
        surface_count: int,
        contract_count: int,
        entry_count: int,
    ) -> PortalEvidence:
        core = {
            "surfaces_fingerprint": surfaces_fingerprint,
            "routes_fingerprint": routes_fingerprint,
            "search_index_fingerprint": search_index_fingerprint,
            "accessibility_passed": accessibility_passed,
            "surface_count": surface_count,
            "contract_count": contract_count,
            "entry_count": entry_count,
        }
        return cls(
            surfaces_fingerprint=surfaces_fingerprint,
            routes_fingerprint=routes_fingerprint,
            search_index_fingerprint=search_index_fingerprint,
            accessibility_passed=accessibility_passed,
            surface_count=surface_count,
            contract_count=contract_count,
            entry_count=entry_count,
            evidence_id=f"UCOS-PTEV-{content_hash(core)[:16]}",
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "evidence_id": self.evidence_id,
            "surfaces_fingerprint": self.surfaces_fingerprint,
            "routes_fingerprint": self.routes_fingerprint,
            "search_index_fingerprint": self.search_index_fingerprint,
            "accessibility_passed": self.accessibility_passed,
            "surface_count": self.surface_count,
            "contract_count": self.contract_count,
            "entry_count": self.entry_count,
        }

    def fingerprint(self) -> str:
        return content_hash(self.to_dict())


class PortalService:
    """The governed L1 composition point for the UCOS Platform Portal."""

    __slots__ = (
        "_gateway",
        "_navigation",
        "_router",
        "_workspace",
        "_directory",
        "_observability_view",
        "_search",
        "_events",
        "_entries",
    )

    def __init__(
        self,
        *,
        gateway: PortalAccessGateway,
        navigation: NavigationModel,
        router: Router,
        workspace: WorkspaceSelector,
        search: GlobalSearch,
        directory: ServiceDirectory | None = None,
        observability_view: ObservabilityView | None = None,
        events: EventBus | None = None,
    ) -> None:
        if not isinstance(gateway, PortalAccessGateway):
            raise PortalServiceError("a valid PortalAccessGateway is required")
        if not isinstance(navigation, NavigationModel):
            raise PortalServiceError("a valid NavigationModel is required")
        if not isinstance(router, Router):
            raise PortalServiceError("a valid Router is required")
        if not isinstance(workspace, WorkspaceSelector):
            raise PortalServiceError("a valid WorkspaceSelector is required")
        if not isinstance(search, GlobalSearch):
            raise PortalServiceError("a valid GlobalSearch is required")
        if directory is not None and not isinstance(directory, ServiceDirectory):
            raise PortalServiceError("directory must be a ServiceDirectory when provided")
        if observability_view is not None and not isinstance(observability_view, ObservabilityView):
            raise PortalServiceError(
                "observability_view must be an ObservabilityView when provided"
            )
        if events is not None and not isinstance(events, EventBus):
            raise PortalServiceError("events must be an EventBus when provided")
        self._gateway = gateway
        self._navigation = navigation
        self._router = router
        self._workspace = workspace
        self._search = search
        self._directory = directory
        self._observability_view = observability_view
        self._events = events
        self._entries = 0

    # -- component access -------------------------------------------------------

    @property
    def gateway(self) -> PortalAccessGateway:
        return self._gateway

    @property
    def navigation(self) -> NavigationModel:
        return self._navigation

    @property
    def router(self) -> Router:
        return self._router

    @property
    def workspace(self) -> WorkspaceSelector:
        return self._workspace

    @property
    def search_engine(self) -> GlobalSearch:
        return self._search

    @property
    def observability(self) -> ObservabilityView | None:
        return self._observability_view

    @property
    def entry_count(self) -> int:
        return self._entries

    # -- shell entry (authenticated portal reachable) --------------------------

    def enter(self, session_id: str, *, now: int, tenant: str | None = None) -> PortalView:
        """Admit a session and render its authorized portal view (fail-closed).

        Raises :class:`~platform.portal.errors.PortalAccessError` when admission is
        denied (no READ on ``portal-navigation``). On success emits a governed
        ``portal.session.entered`` event (observed as PC-16) and returns the
        authorized navigation tree, the landing route, and the accessibility report.
        """
        admission = self._gateway.require_admission(session_id, now=now, tenant=tenant)
        navigation = self._navigation.build(self._visibility(session_id, now=now, tenant=tenant))
        accessibility = self._navigation.accessibility_report()
        self._entries += 1
        self._emit_entered(admission)
        return PortalView.create(
            session_id=session_id,
            principal_id=admission.principal_id,
            navigation=navigation,
            landing_path=self._router.resolve("/").path,
            accessibility=accessibility,
        )

    # -- routing (navigation to authorized surfaces) ---------------------------

    def navigate(
        self, session_id: str, path: str, *, now: int, tenant: str | None = None
    ) -> NavigationResult:
        """Resolve ``path`` and authorize its surface (fail-closed, never guesses).

        Resolution raises :class:`~platform.portal.errors.RoutingError` for an unknown
        path; authorization denial is returned as data (``authorized == False``).
        """
        route = self._router.resolve(path)
        decision = self._gateway.authorize(
            session_id,
            route.group,
            route.required_permission,
            now=now,
            tenant=tenant,
        )
        return NavigationResult(
            path=route.path,
            authorized=decision.decision is Decision.PERMIT,
            route=route,
            decision=decision,
        )

    # -- workspace handoff ------------------------------------------------------

    def select_workspace(
        self,
        session_id: str,
        workspace_id: str,
        *,
        now: int,
        tenant: str | None = None,
    ) -> WorkspaceHandoff:
        """Produce a portal-to-workspace handoff (authorization-gated)."""
        return self._workspace.handoff(session_id, workspace_id, now=now, tenant=tenant)

    # -- global search ----------------------------------------------------------

    def search(
        self, session_id: str, query: str, *, now: int, tenant: str | None = None
    ) -> SearchResponse:
        """Run an authorization-scoped global search (PC-13)."""
        return self._search.search(session_id, query, now=now, tenant=tenant)

    # -- platform services access ----------------------------------------------

    def discover_services(self) -> ServiceDirectory:
        """The platform service-discovery / capability-access model (fail-closed)."""
        if self._directory is None:
            raise PortalServiceError("no service directory bound to the portal")
        return self._directory

    # -- observability integration ---------------------------------------------

    def health(
        self,
        session_id: str,
        results: Mapping[str, HealthStatus],
        *,
        now: int,
        tenant: str | None = None,
    ) -> dict[str, Any]:
        """Health visibility (G1), gated on observability READ."""
        return self._require_observability().health(session_id, results, now=now, tenant=tenant)

    def runtime(self, session_id: str, *, now: int, tenant: str | None = None) -> dict[str, Any]:
        """Runtime visibility (governed-action evidence), gated on observability READ."""
        return self._require_observability().runtime(session_id, now=now, tenant=tenant)

    def monitoring(self, session_id: str, *, now: int, tenant: str | None = None) -> dict[str, Any]:
        """Monitoring visibility (metric snapshot), gated on observability READ."""
        return self._require_observability().monitoring(session_id, now=now, tenant=tenant)

    # -- evidence ---------------------------------------------------------------

    def evidence(self) -> PortalEvidence:
        """Produce deterministic Portal Evidence over the composed model."""
        surfaces_fingerprint = content_hash([s.to_dict() for s in self._navigation.surfaces])
        return PortalEvidence.create(
            surfaces_fingerprint=surfaces_fingerprint,
            routes_fingerprint=self._router.fingerprint(),
            search_index_fingerprint=self._search.index.fingerprint(),
            accessibility_passed=self._navigation.accessibility_report().passed,
            surface_count=len(self._navigation.surfaces),
            contract_count=len(PORTAL_CONTRACTS),
            entry_count=self._entries,
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "surface_count": len(self._navigation.surfaces),
            "route_count": len(self._router),
            "search_entity_count": len(self._search.index),
            "entry_count": self._entries,
            "observability_bound": self._observability_view is not None
            and self._observability_view.bound,
            "evidence": self.evidence().to_dict(),
        }

    # -- internals --------------------------------------------------------------

    def _visibility(self, session_id: str, *, now: int, tenant: str | None):
        """Build the surface-visibility predicate for one caller (fail-closed)."""

        def is_visible(surface: PortalSurface) -> bool:
            return self._gateway.is_permitted(
                session_id,
                surface.group,
                surface.required_permission,
                now=now,
                tenant=tenant,
            )

        return is_visible

    def _require_observability(self) -> ObservabilityView:
        if self._observability_view is None:
            raise PortalServiceError("no observability view bound to the portal")
        return self._observability_view

    def _emit_entered(self, admission: PortalAdmission) -> None:
        if self._events is not None:
            self._events.publish(
                PORTAL_ENTERED_EVENT,
                source="platform.portal.shell",
                subject=admission.principal_id,
                payload={"session_id": admission.session_id},
            )


def build_portal_service(
    *,
    authorization: AuthorizationService,
    observability: ObservabilityService | None = None,
    events: EventBus | None = None,
    services: ServiceRegistry | None = None,
    capabilities: CapabilityCatalog | None = None,
    surfaces: Iterable[PortalSurface] | None = None,
    search_index: SearchIndex | None = None,
) -> PortalService:
    """Default, registry-driven composition of the Portal Layer.

    Wires the access gateway (over the supplied Identity ``authorization`` service),
    the navigation model and router (over the same surface catalog), the workspace
    selector, the global search (over ``search_index`` or a default demonstration
    index), and — when supplied — the service directory (over ``services`` +
    ``capabilities``) and the observability view (over ``observability``).
    """
    if not isinstance(authorization, AuthorizationService):
        raise PortalServiceError("build_portal_service requires an AuthorizationService")
    catalog = tuple(surfaces) if surfaces is not None else default_portal_surfaces()
    gateway = PortalAccessGateway(authorization)
    navigation = NavigationModel(catalog)
    router = Router(catalog)
    workspace = WorkspaceSelector(gateway, router=router)
    index = search_index if search_index is not None else default_search_index()
    search = GlobalSearch(index, gateway)
    directory = (
        ServiceDirectory(services, capabilities)
        if services is not None and capabilities is not None
        else None
    )
    observability_view = ObservabilityView(gateway, observability)
    return PortalService(
        gateway=gateway,
        navigation=navigation,
        router=router,
        workspace=workspace,
        search=search,
        directory=directory,
        observability_view=observability_view,
        events=events,
    )


def bootstrap_portal(
    context: Any,
    *,
    authorization: AuthorizationService | None = None,
    observability: ObservabilityService | None = None,
) -> PortalService:
    """Compose the Portal Layer onto a :class:`PlatformContext` (registry-driven).

    Composes the platform end to end: the Identity Layer (L7) and Observability Layer
    (L8) are bootstrapped onto the context if not supplied, then the Portal (L1) is
    built over them. Publishes the portal contracts into the foundation service
    registry (EC2-EPIC-001), binds the portal to the context event bus (so entries are
    observed as governed actions), and emits a deterministic
    ``portal.bootstrap.completed`` event. The parameter is typed loosely to avoid a
    hard import cycle on the foundation bootstrap module.
    """
    from platform.foundation.services import ServiceDescriptor

    auth = authorization if authorization is not None else bootstrap_identity(context)
    obs = observability if observability is not None else bootstrap_observability(context)

    service = build_portal_service(
        authorization=auth,
        observability=obs,
        events=context.events,
        services=context.services,
        capabilities=context.capabilities,
    )

    contracts = {c.name: c for c in default_portal_contracts()}
    for ref in PORTAL_CONTRACTS:
        if ref.name in context.services:
            continue
        if "search" in ref.name:
            caps = ("PC-13",)
        elif "access" in ref.name or "shell" in ref.name:
            caps = ("PC-01", "PC-02")
        else:
            caps = ("PC-01",)
        context.services.register(
            ServiceDescriptor(
                name=ref.name,
                contract=contracts[ref.name],
                capabilities=caps,
                description=f"Portal Platform service: {ref.name}.",
            ),
            provider=lambda svc=service: svc,
        )

    context.events.publish(
        PORTAL_BOOTSTRAP_EVENT,
        source="platform.portal.bootstrap",
        subject=context.program_id,
        payload={
            "portal_contracts": [ref.name for ref in PORTAL_CONTRACTS],
            "surfaces": len(service.navigation.surfaces),
            "routes": len(service.router),
        },
    )
    return service


__all__ = [
    "PORTAL_BOOTSTRAP_EVENT",
    "PORTAL_ENTERED_EVENT",
    "PortalView",
    "NavigationResult",
    "PortalEvidence",
    "PortalService",
    "build_portal_service",
    "bootstrap_portal",
]
