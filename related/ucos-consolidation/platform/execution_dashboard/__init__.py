"""UCOS EC-2 Platform Execution Dashboard Runtime (EC2-EPIC-008).

The Execution Dashboard Runtime (L3 Application of the Program architecture, §4) realizes
Program **Surface #8/#10 Execution Dashboard** (PC-08 execution visibility + PC-13 search +
PC-16 audit + PC-12 monitoring): it provides authorized principals **operational visibility
and navigation** over the Generation Requests managed by the certified EC2-EPIC-007
Generation Request Runtime. It surfaces — read-only, by reference — the request census, the
queue depth, per-request execution snapshots, lifecycle-transition trends, and runtime health,
and lets principals discover/search requests under authorization and tenant isolation, with
append-only audit and reproducible evidence.

**The dashboard is an observability and navigation surface only.** It implements **no
execution logic, no generation logic, and no engine implementation**; it consumes the
Generation Request Runtime **by reference** and re-derives no lifecycle, execution, or
generation state (P10). It authorizes on the pre-existing ``execution-dashboard`` capability
group — never ``generation-requests`` — so a role that holds dashboard READ but no generation
grant (e.g. Operator, §3.2) can observe the dashboard, while every read still composes RBAC
authorization with tenant/workspace isolation (P3, fail-closed).

Authoritative basis: ``06-IMPLEMENTATION/UCOS-EC-2-PLATFORM-REALIZATION-PROGRAM.md`` (§2.1
surface #8 Execution Dashboard, PC-08/PC-12/PC-13/PC-16, §3.2 RBAC row ``execution-dashboard``
— R for all nine users, scoped for Partner/Integrator, §4 L3). It is strictly **additive**
over the certified EC-1 engine and the EC-2 Foundation (EC2-EPIC-001), Identity
(EC2-EPIC-002), Observability (EC2-EPIC-013), and Generation Request (EC2-EPIC-007) layers:
it modifies neither EC-1 nor any prior layer, never writes to the certified corpus (DP-03),
remains deterministic, starts no server, and opens no socket.

Deliverables (EC2-TASK-000127…000133):
    * **errors** — the ``EC2-ED-*`` error taxonomy over ``PlatformError``.
    * **contracts** — the READ-only ``DashboardAction`` vocabulary, the verb→permission map
      binding the ``execution-dashboard`` group, the surfaced EPIC-007 vocabulary and observed
      observability surface, and ``EXECUTION_DASHBOARD_CONTRACTS``.
    * **views** — the immutable domain model: ``ExecutionSnapshot``, ``QueueSummary``,
      ``RequestMetrics``, ``RequestTrend``, ``HealthSnapshot``, ``DashboardSummary``,
      ``DashboardView``.
    * **search** — authorization- and isolation-scoped ``DashboardSearch`` (surfaces the
      EPIC-007 ``RequestSearchResponse`` / ``RequestHit`` contracts).
    * **health** — dashboard health checks + ``DashboardHealth`` (reuses the L8 model).
    * **evidence** — the deterministic ``DashboardEvidence`` runtime record.
    * **service** — the ``ExecutionDashboardService`` composition root + ``DashboardAccess``.
    * **bootstrap** — ``bootstrap_execution_dashboard`` (composes identity + observability +
      the generation runtime by reference + the dashboard runtime).
"""

from __future__ import annotations

from platform.execution_dashboard.bootstrap import (
    EXECUTION_DASHBOARD_BOOTSTRAP_EVENT,
    bootstrap_execution_dashboard,
)
from platform.execution_dashboard.contracts import (
    DASHBOARD_TERMINAL_STATUSES,
    EXECUTION_DASHBOARD_CONTRACT_VERSION,
    EXECUTION_DASHBOARD_CONTRACTS,
    EXECUTION_DASHBOARD_GROUP,
    OBSERVED_GENERATION_EVENTS,
    OBSERVED_GENERATION_METRICS,
    DashboardAction,
    DashboardDerivedStatus,
    DashboardExecutionState,
    DashboardRequestPosture,
    DashboardRequestStatus,
    all_dashboard_actions,
    default_execution_dashboard_contracts,
    execution_dashboard_contract,
    permission_for,
)
from platform.execution_dashboard.errors import (
    DashboardAccessError,
    DashboardContractError,
    DashboardHealthError,
    DashboardSearchError,
    DashboardServiceError,
    DashboardViewError,
    ExecutionDashboardError,
)
from platform.execution_dashboard.evidence import DashboardEvidence
from platform.execution_dashboard.health import (
    CENSUS_CHECK,
    QUEUE_CHECK,
    REGISTRY_CHECK,
    DashboardHealth,
    execution_dashboard_health_checks,
)
from platform.execution_dashboard.search import DashboardSearch
from platform.execution_dashboard.service import (
    DASHBOARD_ACCESS_EVENT,
    DASHBOARD_CENSUS_EVENT,
    DASHBOARD_HEALTH_CHANGED_EVENT,
    DASHBOARD_HEALTH_EVENT,
    DASHBOARD_QUEUE_EVENT,
    DASHBOARD_SEARCH_EVENT,
    DASHBOARD_SNAPSHOT_EVENT,
    DASHBOARD_SUMMARY_EVENT,
    DASHBOARD_TREND_EVENT,
    DASHBOARD_VIEWED_EVENT,
    METRIC_CENSUS_VIEWS,
    METRIC_HEALTH_INSPECTIONS,
    METRIC_QUEUE_INSPECTIONS,
    METRIC_SEARCHES,
    METRIC_SUMMARIES,
    METRIC_TREND_VIEWS,
    METRIC_VIEWS,
    DashboardAccess,
    ExecutionDashboardService,
    build_execution_dashboard_service,
)
from platform.execution_dashboard.views import (
    DashboardSummary,
    DashboardView,
    ExecutionSnapshot,
    HealthSnapshot,
    QueueSummary,
    RequestMetrics,
    RequestTrend,
)

__all__ = [
    # contracts
    "EXECUTION_DASHBOARD_CONTRACT_VERSION",
    "EXECUTION_DASHBOARD_CONTRACTS",
    "EXECUTION_DASHBOARD_GROUP",
    "DASHBOARD_TERMINAL_STATUSES",
    "OBSERVED_GENERATION_EVENTS",
    "OBSERVED_GENERATION_METRICS",
    "DashboardAction",
    "DashboardRequestStatus",
    "DashboardExecutionState",
    "DashboardRequestPosture",
    "DashboardDerivedStatus",
    "permission_for",
    "all_dashboard_actions",
    "execution_dashboard_contract",
    "default_execution_dashboard_contracts",
    # views
    "ExecutionSnapshot",
    "QueueSummary",
    "RequestMetrics",
    "RequestTrend",
    "HealthSnapshot",
    "DashboardSummary",
    "DashboardView",
    # search
    "DashboardSearch",
    # health
    "REGISTRY_CHECK",
    "CENSUS_CHECK",
    "QUEUE_CHECK",
    "execution_dashboard_health_checks",
    "DashboardHealth",
    # evidence
    "DashboardEvidence",
    # service
    "DASHBOARD_VIEWED_EVENT",
    "DASHBOARD_SUMMARY_EVENT",
    "DASHBOARD_QUEUE_EVENT",
    "DASHBOARD_CENSUS_EVENT",
    "DASHBOARD_TREND_EVENT",
    "DASHBOARD_HEALTH_EVENT",
    "DASHBOARD_SNAPSHOT_EVENT",
    "DASHBOARD_SEARCH_EVENT",
    "DASHBOARD_HEALTH_CHANGED_EVENT",
    "DASHBOARD_ACCESS_EVENT",
    "METRIC_VIEWS",
    "METRIC_SUMMARIES",
    "METRIC_QUEUE_INSPECTIONS",
    "METRIC_CENSUS_VIEWS",
    "METRIC_TREND_VIEWS",
    "METRIC_HEALTH_INSPECTIONS",
    "METRIC_SEARCHES",
    "DashboardAccess",
    "ExecutionDashboardService",
    "build_execution_dashboard_service",
    # bootstrap
    "EXECUTION_DASHBOARD_BOOTSTRAP_EVENT",
    "bootstrap_execution_dashboard",
    # errors
    "ExecutionDashboardError",
    "DashboardContractError",
    "DashboardViewError",
    "DashboardSearchError",
    "DashboardHealthError",
    "DashboardAccessError",
    "DashboardServiceError",
]
