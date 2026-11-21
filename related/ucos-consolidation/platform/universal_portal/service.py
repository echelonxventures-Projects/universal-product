"""UCOS-EPIC-008 / Terminal T8 — Universal Portal Service (composition root).

The single, governed **Universal Portal composition point** (L1) that unifies the eight
Terminal-T8 surfaces into one deterministic entry point over the certified EC-2 Portal
shell (EC2-EPIC-003). It is strictly **additive**: it authorizes only through the portal
access gateway (Identity L7), reads only the **published** ``to_dict()`` snapshot of each
bound backing service, re-implements no domain, mutates nothing, starts no server, opens no
socket, and never writes to the certified corpus (DP-03). Every surface is **fail-closed**:
an unauthorized caller, or an unbound surface, is denied (denial is returned as data on
:class:`~platform.universal_portal.applications.ApplicationView`, never a leaked snapshot).

It is deterministic: the same identity registrations, bound providers, and ordered calls
yield the same :class:`UniversalPortalEvidence` fingerprint. This module also provides
:func:`build_universal_portal_service` (default wiring over an
:class:`~platform.identity.service.AuthorizationService`) and
:func:`bootstrap_universal_portal` (composes identity + observability + portal + the
Administration/Validation/Certification/Measurement backing services and the
service-directory/knowledge explorers onto a
:class:`~platform.foundation.bootstrap.PlatformContext`, publishes the Universal Portal
contracts, and emits a composition event).
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from platform.foundation.contracts import content_hash
from platform.foundation.events import EventBus
from platform.identity.contracts import Decision
from platform.identity.service import AuthorizationService, bootstrap_identity
from platform.observability.service import ObservabilityService, bootstrap_observability
from platform.portal.access import PortalAccessGateway
from platform.portal.discovery import ServiceDirectory
from platform.portal.service import PortalService, PortalView, build_portal_service
from platform.universal_portal.applications import (
    ApplicationProvider,
    ApplicationRegistry,
    ApplicationView,
)
from platform.universal_portal.contracts import (
    UNIVERSAL_PORTAL_CONTRACTS,
    PortalApplication,
    default_universal_portal_contracts,
)
from platform.universal_portal.developer import DeveloperPortal
from platform.universal_portal.documentation import DocumentationPortal
from platform.universal_portal.errors import UniversalPortalServiceError
from platform.universal_portal.health import (
    UniversalPortalHealth,
    universal_portal_health_report,
)
from typing import Any

#: The event emitted when the Universal Portal is composed onto a context.
UNIVERSAL_PORTAL_BOOTSTRAP_EVENT = "universal_portal.bootstrap.completed"

#: The governed event emitted when an authorized caller opens a T8 application (PC-16).
UNIVERSAL_PORTAL_OPENED_EVENT = "universal_portal.application.opened"


@dataclass(frozen=True, slots=True)
class _Snapshot:
    """A minimal deterministic snapshot holder exposing a published ``to_dict()``."""

    payload: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return dict(self.payload)


@dataclass(frozen=True, slots=True)
class UniversalPortalEvidence:
    """A deterministic, content-addressed record of Universal Portal state (evidence)."""

    applications_fingerprint: str
    developer_catalog_fingerprint: str
    documentation_fingerprint: str
    portal_evidence_fingerprint: str
    health_passed: bool
    application_count: int
    bound_count: int
    contract_count: int
    open_count: int
    evidence_id: str = ""

    @classmethod
    def create(
        cls,
        *,
        applications_fingerprint: str,
        developer_catalog_fingerprint: str,
        documentation_fingerprint: str,
        portal_evidence_fingerprint: str,
        health_passed: bool,
        application_count: int,
        bound_count: int,
        contract_count: int,
        open_count: int,
    ) -> UniversalPortalEvidence:
        core = {
            "applications_fingerprint": applications_fingerprint,
            "developer_catalog_fingerprint": developer_catalog_fingerprint,
            "documentation_fingerprint": documentation_fingerprint,
            "portal_evidence_fingerprint": portal_evidence_fingerprint,
            "health_passed": health_passed,
            "application_count": application_count,
            "bound_count": bound_count,
            "contract_count": contract_count,
            "open_count": open_count,
        }
        return cls(
            applications_fingerprint=applications_fingerprint,
            developer_catalog_fingerprint=developer_catalog_fingerprint,
            documentation_fingerprint=documentation_fingerprint,
            portal_evidence_fingerprint=portal_evidence_fingerprint,
            health_passed=health_passed,
            application_count=application_count,
            bound_count=bound_count,
            contract_count=contract_count,
            open_count=open_count,
            evidence_id=f"UCOS-T8EV-{content_hash(core)[:16]}",
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "evidence_id": self.evidence_id,
            "applications_fingerprint": self.applications_fingerprint,
            "developer_catalog_fingerprint": self.developer_catalog_fingerprint,
            "documentation_fingerprint": self.documentation_fingerprint,
            "portal_evidence_fingerprint": self.portal_evidence_fingerprint,
            "health_passed": self.health_passed,
            "application_count": self.application_count,
            "bound_count": self.bound_count,
            "contract_count": self.contract_count,
            "open_count": self.open_count,
        }

    def fingerprint(self) -> str:
        return content_hash(self.to_dict())


class UniversalPortalService:
    """The governed L1 composition point for the UCOS Ω∞ Universal Portal (T8)."""

    __slots__ = (
        "_portal",
        "_registry",
        "_developer",
        "_documentation",
        "_events",
        "_opens",
    )

    def __init__(
        self,
        *,
        portal: PortalService,
        registry: ApplicationRegistry,
        developer: DeveloperPortal,
        documentation: DocumentationPortal,
        events: EventBus | None = None,
    ) -> None:
        if not isinstance(portal, PortalService):
            raise UniversalPortalServiceError("a valid PortalService is required")
        if not isinstance(registry, ApplicationRegistry):
            raise UniversalPortalServiceError("a valid ApplicationRegistry is required")
        if not isinstance(developer, DeveloperPortal):
            raise UniversalPortalServiceError("a valid DeveloperPortal is required")
        if not isinstance(documentation, DocumentationPortal):
            raise UniversalPortalServiceError("a valid DocumentationPortal is required")
        if events is not None and not isinstance(events, EventBus):
            raise UniversalPortalServiceError("events must be an EventBus when provided")
        self._portal = portal
        self._registry = registry
        self._developer = developer
        self._documentation = documentation
        self._events = events
        self._opens = 0

    # -- component access -------------------------------------------------------

    @property
    def portal(self) -> PortalService:
        return self._portal

    @property
    def gateway(self) -> PortalAccessGateway:
        return self._portal.gateway

    @property
    def applications_registry(self) -> ApplicationRegistry:
        return self._registry

    @property
    def developer_portal(self) -> DeveloperPortal:
        return self._developer

    @property
    def documentation_portal(self) -> DocumentationPortal:
        return self._documentation

    @property
    def open_count(self) -> int:
        return self._opens

    # -- shell entry (delegates to the certified portal shell) -----------------

    def enter(self, session_id: str, *, now: int, tenant: str | None = None) -> PortalView:
        """Admit a session into the portal and render its authorized shell view."""
        return self._portal.enter(session_id, now=now, tenant=tenant)

    # -- application catalog ----------------------------------------------------

    def applications(self):
        """Every application descriptor in stable declaration order."""
        return self._registry.descriptors()

    def open(
        self,
        session_id: str,
        application: PortalApplication,
        *,
        now: int,
        tenant: str | None = None,
    ) -> ApplicationView:
        """Open a T8 application for a caller (fail-closed authorization-gated).

        Authorizes the caller for the application's §3.2 capability group + READ through
        the portal access gateway. On PERMIT and a bound surface, returns the published
        ``to_dict()`` snapshot; otherwise returns a fail-closed view with no snapshot.
        """
        if not isinstance(application, PortalApplication):
            raise UniversalPortalServiceError("application must be a PortalApplication")
        group = self._registry.group(application)
        permission = self._registry.permission(application)
        decision = self._portal.gateway.authorize(
            session_id, group, permission, now=now, tenant=tenant
        )
        authorized = decision.decision is Decision.PERMIT
        available = self._registry.is_bound(application)
        snapshot = self._registry.snapshot(application) if authorized and available else None
        if authorized:
            self._opens += 1
            self._emit_opened(application, decision.request.principal_id, session_id)
        return ApplicationView.create(
            application=application,
            authorized=authorized,
            available=available,
            reason=decision.reason,
            snapshot=snapshot,
        )

    # -- convenience surface accessors ------------------------------------------

    def administration(self, session_id: str, *, now: int, tenant: str | None = None):
        app = PortalApplication.ADMINISTRATION_PORTAL
        return self.open(session_id, app, now=now, tenant=tenant)

    def registry_explorer(self, session_id: str, *, now: int, tenant: str | None = None):
        return self.open(session_id, PortalApplication.REGISTRY_EXPLORER, now=now, tenant=tenant)

    def knowledge_graph(self, session_id: str, *, now: int, tenant: str | None = None):
        return self.open(
            session_id, PortalApplication.KNOWLEDGE_GRAPH_EXPLORER, now=now, tenant=tenant
        )

    def measurement(self, session_id: str, *, now: int, tenant: str | None = None):
        app = PortalApplication.MEASUREMENT_DASHBOARD
        return self.open(session_id, app, now=now, tenant=tenant)

    def validation(self, session_id: str, *, now: int, tenant: str | None = None):
        return self.open(session_id, PortalApplication.VALIDATION_DASHBOARD, now=now, tenant=tenant)

    def certification(self, session_id: str, *, now: int, tenant: str | None = None):
        return self.open(
            session_id, PortalApplication.CERTIFICATION_DASHBOARD, now=now, tenant=tenant
        )

    def developer(self, session_id: str, *, now: int, tenant: str | None = None):
        return self.open(session_id, PortalApplication.DEVELOPER_PORTAL, now=now, tenant=tenant)

    def documentation(self, session_id: str, *, now: int, tenant: str | None = None):
        return self.open(session_id, PortalApplication.DOCUMENTATION_PORTAL, now=now, tenant=tenant)

    # -- portal shell delegation ------------------------------------------------

    def navigate(self, session_id: str, path: str, *, now: int, tenant: str | None = None):
        """Resolve + authorize a portal shell path (delegated to the shell)."""
        return self._portal.navigate(session_id, path, now=now, tenant=tenant)

    def search(self, session_id: str, query: str, *, now: int, tenant: str | None = None):
        """Run an authorization-scoped global search (delegated to the shell)."""
        return self._portal.search(session_id, query, now=now, tenant=tenant)

    def discover_services(self) -> ServiceDirectory:
        """The platform service-discovery model (delegated to the shell)."""
        return self._portal.discover_services()

    # -- health + evidence ------------------------------------------------------

    def health(self) -> UniversalPortalHealth:
        """The deterministic Universal Portal health report."""
        accessibility = self._portal.navigation.accessibility_report()
        return universal_portal_health_report(
            self._registry, portal_accessibility_passed=accessibility.passed
        )

    def evidence(self) -> UniversalPortalEvidence:
        """Produce deterministic Universal Portal evidence over the composed model."""
        return UniversalPortalEvidence.create(
            applications_fingerprint=self._registry.fingerprint(),
            developer_catalog_fingerprint=self._developer.catalog().fingerprint(),
            documentation_fingerprint=self._documentation.index().fingerprint(),
            portal_evidence_fingerprint=self._portal.evidence().fingerprint(),
            health_passed=self.health().passed,
            application_count=len(self._registry.applications()),
            bound_count=self._registry.bound_count,
            contract_count=len(UNIVERSAL_PORTAL_CONTRACTS),
            open_count=self._opens,
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "applications": self._registry.to_dict(),
            "developer_catalog": self._developer.catalog().to_dict(),
            "documentation_index": self._documentation.index().to_dict(),
            "health": self.health().to_dict(),
            "open_count": self._opens,
            "contract_count": len(UNIVERSAL_PORTAL_CONTRACTS),
            "evidence": self.evidence().to_dict(),
        }

    # -- internals --------------------------------------------------------------

    def _emit_opened(self, application: PortalApplication, principal_id: str, session_id: str):
        if self._events is not None:
            self._events.publish(
                UNIVERSAL_PORTAL_OPENED_EVENT,
                source="platform.universal_portal.service",
                subject=principal_id,
                payload={"application": application.value, "session_id": session_id},
            )


def build_universal_portal_service(
    *,
    authorization: AuthorizationService,
    observability: ObservabilityService | None = None,
    events: EventBus | None = None,
    services: Any | None = None,
    capabilities: Any | None = None,
    providers: Mapping[PortalApplication, ApplicationProvider] | None = None,
) -> UniversalPortalService:
    """Default composition of the Universal Portal over an Identity authorization service.

    Builds the certified EC-2 portal shell, the developer + documentation read models, and
    the application registry (binding the supplied domain ``providers`` plus the self-backed
    developer and documentation surfaces). The developer catalog is enriched with the live
    service directory when ``services`` + ``capabilities`` are supplied.
    """
    if not isinstance(authorization, AuthorizationService):
        raise UniversalPortalServiceError("build_universal_portal_service requires authorization")
    portal = build_portal_service(
        authorization=authorization,
        observability=observability,
        events=events,
        services=services,
        capabilities=capabilities,
    )
    directory: ServiceDirectory | None
    try:
        directory = portal.discover_services()
    except Exception:  # noqa: BLE001 — no directory bound is a valid (degraded) composition
        directory = None
    developer = DeveloperPortal(directory)
    documentation = DocumentationPortal()

    bindings: dict[PortalApplication, ApplicationProvider] = dict(providers or {})
    bindings.setdefault(PortalApplication.DEVELOPER_PORTAL, developer.catalog)
    bindings.setdefault(PortalApplication.DOCUMENTATION_PORTAL, documentation.index)
    registry = ApplicationRegistry(bindings)

    return UniversalPortalService(
        portal=portal,
        registry=registry,
        developer=developer,
        documentation=documentation,
        events=events,
    )


def _knowledge_snapshot_provider() -> ApplicationProvider:
    """Bind the Knowledge Graph Explorer to a deterministic knowledge-graph snapshot.

    Consumes the certified EC-1 Knowledge Layer (``engine.knowledge``) only through its
    published API (``build_seed_base`` → ``derive_edges`` → ``KnowledgeGraph``), read-only.
    """
    from engine.knowledge import build_seed_base

    base = build_seed_base()
    graph = base.graph()
    payload: dict[str, Any] = {
        "source": "engine.knowledge",
        "contract": "knowledge.ukda@1.0.0",
        "object_count": len(base.object_ids()),
        "node_count": len(graph.nodes()),
        "edge_count": len(graph),
        "relationship_types": [t.value for t in graph.types()],
        "nodes": list(graph.nodes()),
    }
    snapshot = _Snapshot(payload)
    return lambda: snapshot


def bootstrap_universal_portal(
    context: Any,
    *,
    authorization: AuthorizationService | None = None,
    observability: ObservabilityService | None = None,
) -> UniversalPortalService:
    """Compose the Universal Portal onto a :class:`PlatformContext` (registry-driven).

    Composes the platform end to end: Identity (L7) and Observability (L8) are bootstrapped
    onto the context if not supplied, then the Administration, Validation, Certification,
    and Measurement (coverage) backing services are composed and bound, the Registry
    Explorer is bound to the live platform service directory, and the Knowledge Graph
    Explorer is bound to the certified knowledge graph. Publishes the Universal Portal
    contracts into the foundation service registry (PL-05) and emits a deterministic
    ``universal_portal.bootstrap.completed`` event. Typed loosely to avoid an import cycle.
    """
    from platform.administration.bootstrap import bootstrap_administration
    from platform.certification.bootstrap import bootstrap_certification_console
    from platform.coverage.evidence import InMemoryEvidenceSource
    from platform.coverage.service import build_coverage_service
    from platform.foundation.services import ServiceDescriptor
    from platform.validation.bootstrap import bootstrap_validation_console

    auth = authorization if authorization is not None else bootstrap_identity(context)
    obs = observability if observability is not None else bootstrap_observability(context)

    administration = bootstrap_administration(context, authorization=auth, observability=obs)
    validation = bootstrap_validation_console(context, authorization=auth, observability=obs)
    certification = bootstrap_certification_console(context, authorization=auth, observability=obs)
    # A hermetic, deterministic coverage instrument (real deployments may rebind to a
    # RepositoryEvidenceSource); the Measurement Dashboard reads its published snapshot.
    coverage = build_coverage_service(InMemoryEvidenceSource([], []))
    directory = ServiceDirectory(context.services, context.capabilities)

    providers: dict[PortalApplication, ApplicationProvider] = {
        PortalApplication.ADMINISTRATION_PORTAL: lambda: administration,
        PortalApplication.VALIDATION_DASHBOARD: lambda: validation,
        PortalApplication.CERTIFICATION_DASHBOARD: lambda: certification,
        PortalApplication.MEASUREMENT_DASHBOARD: lambda: coverage,
        PortalApplication.REGISTRY_EXPLORER: lambda: directory,
        PortalApplication.KNOWLEDGE_GRAPH_EXPLORER: _knowledge_snapshot_provider(),
    }

    service = build_universal_portal_service(
        authorization=auth,
        observability=obs,
        events=context.events,
        services=context.services,
        capabilities=context.capabilities,
        providers=providers,
    )

    contracts = {c.name: c for c in default_universal_portal_contracts()}
    for ref in UNIVERSAL_PORTAL_CONTRACTS:
        if ref.name in context.services:
            continue
        if "developer" in ref.name or "registry" in ref.name:
            caps = ("PC-01", "PC-13")
        elif "documentation" in ref.name:
            caps = ("PC-01",)
        else:
            caps = ("PC-01", "PC-13")
        context.services.register(
            ServiceDescriptor(
                name=ref.name,
                contract=contracts[ref.name],
                capabilities=caps,
                description=f"Universal Portal service: {ref.name}.",
            ),
            provider=lambda svc=service: svc,
        )

    context.events.publish(
        UNIVERSAL_PORTAL_BOOTSTRAP_EVENT,
        source="platform.universal_portal.bootstrap",
        subject=context.program_id,
        payload={
            "universal_portal_contracts": [ref.name for ref in UNIVERSAL_PORTAL_CONTRACTS],
            "applications": len(service.applications()),
            "bound": service.applications_registry.bound_count,
        },
    )
    return service


__all__ = [
    "UNIVERSAL_PORTAL_BOOTSTRAP_EVENT",
    "UNIVERSAL_PORTAL_OPENED_EVENT",
    "UniversalPortalEvidence",
    "UniversalPortalService",
    "build_universal_portal_service",
    "bootstrap_universal_portal",
]
