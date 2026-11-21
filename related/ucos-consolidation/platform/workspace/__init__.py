"""UCOS EC-2 Platform Workspace Runtime (EC2-EPIC-004) — the scoped execution boundary.

The Workspace Runtime (L3 Application of the Program architecture, §4) is the primary
execution boundary for users, organizations, capabilities, services, runtime assets,
and future generated products. It is a strictly **additive** layer over the certified
EC-1 engine and the EC-2 Foundation (EC2-EPIC-001), Identity (EC2-EPIC-002), and
Observability (EC2-EPIC-013) layers: it authorizes only through the Identity Layer
(no duplicate identity/authorization logic), observes only through the Observability
Layer, and reuses the Foundation registries/events — it re-implements none of them,
modifies neither EC-1 nor any prior layer, never writes to the certified corpus
(DP-03), remains deterministic, and preserves every EC-1 certification.

Deliverables (EC2-TASK-000081…000088):
    * **errors** — the ``EC2-WORKSPACE-*`` error taxonomy over ``PlatformError``.
    * **metadata** — the immutable ``WorkspaceMetadata`` value type.
    * **contracts** — the versioned contract surface + vocabulary: ``WorkspaceStatus``,
      ``MemberRole``, ``Workspace``, ``WorkspaceMember``, ``WORKSPACE_CONTRACTS``.
    * **lifecycle** — the deterministic workspace state machine + ``WorkspaceEvent``.
    * **membership** — the append-only ``MembershipRegistry``.
    * **registration** — the ``WorkspaceRegistry`` (create/register/resolve/discover).
    * **isolation** — the tenant/workspace ``IsolationGuard`` (P3).
    * **context** — the resolved ``WorkspaceContext`` runtime binding.
    * **search** — authorization- and isolation-scoped ``WorkspaceSearch``.
    * **health** — workspace health checks + ``WorkspaceHealth`` (reuses L8 model).
    * **service** — the ``WorkspaceService`` composition root + ``WorkspaceEvidence``.
    * **bootstrap** — ``bootstrap_workspace`` (composes identity + observability + workspace).

This epic carries no constitutional authority; the external gates (EC-1…EC-6) remain
open. It starts no server and opens no socket — it is the deterministic runtime model,
the reusable substrate later work-surface epics (Projects, …) build on.
"""

from __future__ import annotations

from platform.workspace.bootstrap import WORKSPACE_BOOTSTRAP_EVENT, bootstrap_workspace
from platform.workspace.context import WorkspaceContext
from platform.workspace.contracts import (
    WORKSPACE_CONTRACT_VERSION,
    WORKSPACE_CONTRACTS,
    WORKSPACE_GROUP,
    MemberRole,
    Workspace,
    WorkspaceMember,
    WorkspaceStatus,
    all_member_roles,
    all_workspace_statuses,
    default_workspace_contracts,
    workspace_contract,
)
from platform.workspace.errors import (
    MembershipError,
    WorkspaceAccessError,
    WorkspaceContractError,
    WorkspaceError,
    WorkspaceIsolationError,
    WorkspaceLifecycleError,
    WorkspaceMetadataError,
    WorkspaceRegistryError,
    WorkspaceSearchError,
    WorkspaceServiceError,
)
from platform.workspace.health import (
    INTEGRITY_CHECK,
    REGISTRY_CHECK,
    WorkspaceHealth,
    workspace_health_checks,
)
from platform.workspace.isolation import IsolationDecision, IsolationGuard, tenants_isolated
from platform.workspace.lifecycle import (
    WorkspaceEvent,
    allowed_transitions,
    can_transition,
    validate_transition,
)
from platform.workspace.membership import MembershipEvent, MembershipRegistry
from platform.workspace.metadata import EMPTY_METADATA, WorkspaceMetadata
from platform.workspace.registration import WorkspaceRegistry
from platform.workspace.search import WorkspaceHit, WorkspaceSearch, WorkspaceSearchResponse
from platform.workspace.service import (
    WORKSPACE_ACCESS_EVENT,
    WORKSPACE_CREATED_EVENT,
    WORKSPACE_LIFECYCLE_EVENT,
    WORKSPACE_MEMBER_ADDED_EVENT,
    WORKSPACE_MEMBER_REMOVED_EVENT,
    WorkspaceAccess,
    WorkspaceEvidence,
    WorkspaceService,
    build_workspace_service,
)

__all__ = [
    # contracts
    "WORKSPACE_CONTRACT_VERSION",
    "WORKSPACE_CONTRACTS",
    "WORKSPACE_GROUP",
    "WorkspaceStatus",
    "MemberRole",
    "Workspace",
    "WorkspaceMember",
    "all_workspace_statuses",
    "all_member_roles",
    "workspace_contract",
    "default_workspace_contracts",
    # metadata
    "WorkspaceMetadata",
    "EMPTY_METADATA",
    # lifecycle
    "WorkspaceEvent",
    "allowed_transitions",
    "can_transition",
    "validate_transition",
    # membership
    "MembershipEvent",
    "MembershipRegistry",
    # registration
    "WorkspaceRegistry",
    # isolation
    "IsolationDecision",
    "IsolationGuard",
    "tenants_isolated",
    # context
    "WorkspaceContext",
    # search
    "WorkspaceHit",
    "WorkspaceSearchResponse",
    "WorkspaceSearch",
    # health
    "REGISTRY_CHECK",
    "INTEGRITY_CHECK",
    "workspace_health_checks",
    "WorkspaceHealth",
    # service
    "WORKSPACE_CREATED_EVENT",
    "WORKSPACE_MEMBER_ADDED_EVENT",
    "WORKSPACE_MEMBER_REMOVED_EVENT",
    "WORKSPACE_LIFECYCLE_EVENT",
    "WORKSPACE_ACCESS_EVENT",
    "WorkspaceAccess",
    "WorkspaceEvidence",
    "WorkspaceService",
    "build_workspace_service",
    # bootstrap
    "WORKSPACE_BOOTSTRAP_EVENT",
    "bootstrap_workspace",
    # errors
    "WorkspaceError",
    "WorkspaceContractError",
    "WorkspaceMetadataError",
    "WorkspaceLifecycleError",
    "MembershipError",
    "WorkspaceRegistryError",
    "WorkspaceIsolationError",
    "WorkspaceSearchError",
    "WorkspaceAccessError",
    "WorkspaceServiceError",
]
