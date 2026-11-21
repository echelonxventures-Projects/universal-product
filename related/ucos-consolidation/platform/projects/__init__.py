"""UCOS EC-2 Platform Project Management Runtime (EC2-EPIC-005).

The Project Management Runtime (L3 Application of the Program architecture, §4) realizes
the **project** half of PC-03 ("workspace & project lifecycle"): a scoped organizational
container, subordinate to a workspace, that lets authorized principals create and
organize **projects**, associate work references (blueprints, requests, artifacts) to
them **by reference**, drive each project through a deterministic lifecycle, and expose
a deterministically-derivable project status — with authorization- and isolation-scoped
discovery/search, cross-runtime health, append-only audit, and reproducible evidence.

Authoritative basis: ``06-IMPLEMENTATION/UCOS-EC-2-PLATFORM-REALIZATION-PROGRAM.md``
(§2.1 surface #4 Project Management, PC-03, §3.2 ``workspace-project-lifecycle``, §4 L3
Application, §5 EC2-EPIC-005 acceptance, P3 Workspace & Project Integrity), as determined
by ``platform/project-management/EC2-EPIC-005-DETERMINATION.md``.

It is a strictly **additive** layer over the certified EC-1 engine and the EC-2
Foundation (EC2-EPIC-001), Identity (EC2-EPIC-002), Observability (EC2-EPIC-013), and
Workspace (EC2-EPIC-004) layers: it authorizes only through the Identity Layer on the
existing ``workspace-project-lifecycle`` capability group (no new authority, no new
capability group), observes only through the Observability Layer, reuses the Foundation
registries/events, and binds projects to workspaces by reference. It introduces no
downstream (blueprint/request/artifact) runtime dependency (associations are record-only
references), modifies neither EC-1 nor any prior layer, never writes to the certified
corpus (DP-03), remains deterministic, starts no server, and opens no socket.

Deliverables (EC2-TASK-000089…000096):
    * **errors** — the ``EC2-PROJ-*`` error taxonomy over ``PlatformError``.
    * **metadata** — the immutable ``ProjectMetadata`` value type.
    * **contracts** — the versioned contract surface + vocabulary: ``ProjectStatus``,
      ``AssociationKind``, ``ProjectAction``, ``Project``, ``ProjectAssociation``,
      ``PROJECT_CONTRACTS``, verb→permission map.
    * **lifecycle** — the deterministic project state machine + ``ProjectEvent``.
    * **registry** — the ``ProjectRegistry`` (create/register/resolve/discover).
    * **associations** — the append-only ``AssociationRegistry`` (by reference).
    * **status** — the deterministic derived-status computation.
    * **context** — the resolved ``ProjectContext`` runtime binding.
    * **search** — authorization- and isolation-scoped ``ProjectSearch``.
    * **health** — project health checks + ``ProjectHealth`` (reuses L8 model).
    * **service** — the ``ProjectService`` composition root + ``ProjectEvidence``.
    * **bootstrap** — ``bootstrap_projects`` (composes identity + observability +
      workspace + projects).
"""

from __future__ import annotations

from platform.projects.associations import AssociationEvent, AssociationRegistry
from platform.projects.bootstrap import PROJECT_BOOTSTRAP_EVENT, bootstrap_projects
from platform.projects.context import ProjectContext
from platform.projects.contracts import (
    MUTATING_ACTIONS,
    PROJECT_CONTRACT_VERSION,
    PROJECT_CONTRACTS,
    PROJECT_GROUP,
    AssociationKind,
    Project,
    ProjectAction,
    ProjectAssociation,
    ProjectStatus,
    all_association_kinds,
    all_project_actions,
    all_project_statuses,
    default_project_contracts,
    permission_for,
    project_contract,
)
from platform.projects.errors import (
    ProjectAccessError,
    ProjectAssociationError,
    ProjectContractError,
    ProjectError,
    ProjectLifecycleError,
    ProjectMetadataError,
    ProjectRegistryError,
    ProjectSearchError,
    ProjectServiceError,
    ProjectStatusError,
)
from platform.projects.health import (
    INTEGRITY_CHECK,
    REGISTRY_CHECK,
    ProjectHealth,
    project_health_checks,
)
from platform.projects.lifecycle import (
    ProjectEvent,
    allowed_transitions,
    can_transition,
    validate_transition,
)
from platform.projects.metadata import EMPTY_METADATA, ProjectMetadata
from platform.projects.registry import ProjectRegistry
from platform.projects.search import ProjectHit, ProjectSearch, ProjectSearchResponse
from platform.projects.service import (
    PROJECT_ACCESS_EVENT,
    PROJECT_ASSOCIATION_ADDED_EVENT,
    PROJECT_ASSOCIATION_REMOVED_EVENT,
    PROJECT_CREATED_EVENT,
    PROJECT_LIFECYCLE_EVENT,
    ProjectAccess,
    ProjectEvidence,
    ProjectService,
    build_project_service,
)
from platform.projects.status import (
    DerivedProjectStatus,
    ProjectPosture,
    derive_status,
)

__all__ = [
    # contracts
    "PROJECT_CONTRACT_VERSION",
    "PROJECT_CONTRACTS",
    "PROJECT_GROUP",
    "ProjectStatus",
    "AssociationKind",
    "ProjectAction",
    "MUTATING_ACTIONS",
    "Project",
    "ProjectAssociation",
    "permission_for",
    "all_project_statuses",
    "all_association_kinds",
    "all_project_actions",
    "project_contract",
    "default_project_contracts",
    # metadata
    "ProjectMetadata",
    "EMPTY_METADATA",
    # lifecycle
    "ProjectEvent",
    "allowed_transitions",
    "can_transition",
    "validate_transition",
    # registry
    "ProjectRegistry",
    # associations
    "AssociationEvent",
    "AssociationRegistry",
    # status
    "ProjectPosture",
    "DerivedProjectStatus",
    "derive_status",
    # context
    "ProjectContext",
    # search
    "ProjectHit",
    "ProjectSearchResponse",
    "ProjectSearch",
    # health
    "REGISTRY_CHECK",
    "INTEGRITY_CHECK",
    "project_health_checks",
    "ProjectHealth",
    # service
    "PROJECT_CREATED_EVENT",
    "PROJECT_LIFECYCLE_EVENT",
    "PROJECT_ASSOCIATION_ADDED_EVENT",
    "PROJECT_ASSOCIATION_REMOVED_EVENT",
    "PROJECT_ACCESS_EVENT",
    "ProjectAccess",
    "ProjectEvidence",
    "ProjectService",
    "build_project_service",
    # bootstrap
    "PROJECT_BOOTSTRAP_EVENT",
    "bootstrap_projects",
    # errors
    "ProjectError",
    "ProjectContractError",
    "ProjectMetadataError",
    "ProjectLifecycleError",
    "ProjectRegistryError",
    "ProjectAssociationError",
    "ProjectStatusError",
    "ProjectSearchError",
    "ProjectAccessError",
    "ProjectServiceError",
]
