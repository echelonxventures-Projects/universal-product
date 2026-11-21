"""UCOS EC-2 Platform Portal & Navigation (EC2-EPIC-003) — the platform entry point.

The Portal Layer (L1 Presentation of the Program architecture, §4) is the primary
authenticated entry point into the UCOS Platform. It is a strictly **additive** layer
over the certified EC-1 engine and the EC-2 Foundation (EC2-EPIC-001), Identity
(EC2-EPIC-002), and Observability (EC2-EPIC-013) layers: it authenticates/authorizes
only through the Identity Layer, observes only through the Observability Layer, and
discovers only through the Foundation registries — it re-implements none of them,
modifies neither EC-1 nor any prior layer, never writes to the certified corpus
(DP-03), remains deterministic, and preserves every EC-1 certification.

Deliverables (EC2-TASK-000073…000080):
    * **errors** (TASK-000073) — the ``EC2-PORTAL-*`` error taxonomy over ``PlatformError``.
    * **contracts** (TASK-000073) — the versioned portal contract surface + vocabulary:
      ``PortalSection``, ``PortalSurface`` (the sixteen §3.2 surfaces), ``EntityKind``.
    * **access** (TASK-000074) — ``PortalAccessGateway`` integrating the Identity Layer
      (authentication/authorization; no duplicate identity).
    * **navigation** (TASK-000075) — ``NavigationModel`` (authorized surfaces by section)
      + the ``AccessibilityReport``.
    * **routing** (TASK-000076) — the deterministic, fail-closed ``Router``.
    * **workspace** (TASK-000077) — the portal-to-workspace ``WorkspaceSelector`` /
      ``WorkspaceHandoff`` model.
    * **discovery** (TASK-000078) — ``ServiceDirectory`` (service discovery + capability
      access) and ``ObservabilityView`` (health/runtime/monitoring visibility).
    * **search** (TASK-000079) — ``GlobalSearch`` across ≥4 entity kinds (PC-13).
    * **service** (TASK-000080) — the ``PortalService`` composition root (shell),
      ``PortalEvidence``, ``build_portal_service`` and ``bootstrap_portal``.

This epic carries no constitutional authority; the external gates (EC-1…EC-6) remain
open. It starts no server and opens no socket — it is the deterministic presentation
*model*, the reusable substrate the work-surface epics (Workspace, Projects, …) build on.
"""

from __future__ import annotations

from platform.portal.access import PortalAccessGateway, PortalAdmission
from platform.portal.contracts import (
    PORTAL_CONTRACT_VERSION,
    PORTAL_CONTRACTS,
    PORTAL_HOME_PATH,
    EntityKind,
    PortalSection,
    PortalSurface,
    all_entity_kinds,
    all_portal_sections,
    default_portal_contracts,
    default_portal_surfaces,
    entity_kind_group,
    portal_contract,
)
from platform.portal.discovery import (
    OBSERVABILITY_GROUP,
    ObservabilityView,
    ServiceDirectory,
)
from platform.portal.errors import (
    NavigationError,
    PortalAccessError,
    PortalContractError,
    PortalError,
    PortalSearchError,
    PortalServiceError,
    RoutingError,
    ServiceDiscoveryError,
    WorkspaceHandoffError,
)
from platform.portal.navigation import (
    AccessibilityReport,
    Navigation,
    NavigationItem,
    NavigationModel,
    NavigationSection,
    SurfacePredicate,
)
from platform.portal.routing import Route, Router, normalize_path
from platform.portal.search import (
    GlobalSearch,
    SearchEntity,
    SearchIndex,
    SearchResponse,
    SearchResult,
    default_search_index,
)
from platform.portal.service import (
    PORTAL_BOOTSTRAP_EVENT,
    PORTAL_ENTERED_EVENT,
    NavigationResult,
    PortalEvidence,
    PortalService,
    PortalView,
    bootstrap_portal,
    build_portal_service,
)
from platform.portal.workspace import (
    WORKSPACE_GROUP,
    WorkspaceHandoff,
    WorkspaceSelector,
)

__all__ = [
    # contracts (TASK-000073)
    "PORTAL_CONTRACT_VERSION",
    "PORTAL_CONTRACTS",
    "PORTAL_HOME_PATH",
    "PortalSection",
    "all_portal_sections",
    "PortalSurface",
    "default_portal_surfaces",
    "EntityKind",
    "all_entity_kinds",
    "entity_kind_group",
    "portal_contract",
    "default_portal_contracts",
    # access (TASK-000074)
    "PortalAccessGateway",
    "PortalAdmission",
    # navigation (TASK-000075)
    "SurfacePredicate",
    "NavigationItem",
    "NavigationSection",
    "Navigation",
    "AccessibilityReport",
    "NavigationModel",
    # routing (TASK-000076)
    "Route",
    "normalize_path",
    "Router",
    # workspace (TASK-000077)
    "WORKSPACE_GROUP",
    "WorkspaceHandoff",
    "WorkspaceSelector",
    # discovery (TASK-000078)
    "OBSERVABILITY_GROUP",
    "ServiceDirectory",
    "ObservabilityView",
    # search (TASK-000079)
    "SearchEntity",
    "SearchResult",
    "SearchResponse",
    "SearchIndex",
    "GlobalSearch",
    "default_search_index",
    # service (TASK-000080)
    "PORTAL_BOOTSTRAP_EVENT",
    "PORTAL_ENTERED_EVENT",
    "PortalView",
    "NavigationResult",
    "PortalEvidence",
    "PortalService",
    "build_portal_service",
    "bootstrap_portal",
    # errors (TASK-000073)
    "PortalError",
    "PortalContractError",
    "NavigationError",
    "RoutingError",
    "PortalAccessError",
    "WorkspaceHandoffError",
    "ServiceDiscoveryError",
    "PortalSearchError",
    "PortalServiceError",
]
