"""EC2-TASK-000132 — Execution Dashboard Service (EC2-EPIC-008).

The single, governed **execution-dashboard runtime composition point** (L3 Application of
the Program architecture) that composes the whole Execution Dashboard Runtime into one
entry point — the governed observability & navigation surface for Program Surface #8
Execution Dashboard (PC-08 execution visibility + PC-13 search + PC-16 audit + PC-12
monitoring):

    (consumed by reference) GenerationRequestService · GenerationRequestRegistry ·
    DashboardSearch · DashboardHealth · (reused) AuthorizationService · ObservabilityService

It is a strictly **additive**, **read/observability-only** layer. It authorizes only
through the certified Identity Layer (L7) on the existing ``execution-dashboard`` capability
group — **no duplicate authorization or identity logic, no new authority, no new capability
group** — surfaces the certified EPIC-007 Generation Request state **by reference**
(read-only projections, never re-derived — P10), observes only through the Observability
Layer (L8), and exposes **no execution, generation, engine, lifecycle, or registry logic**.
It re-implements none of them, modifies neither EC-1 nor any prior layer, and writes nothing
to the certified corpus (DP-03).

Crucially, the dashboard gates on its **own** ``execution-dashboard`` capability group, not
``generation-requests`` — so a role that holds dashboard READ but no generation grant (e.g.
Operator, §3.2) can observe the dashboard, while every read still composes **identity
authorization** (RBAC §3.2, READ) with **tenant/workspace isolation** (the reused rule, P3),
so cross-tenant visibility is refused in 100% of cases. Because every governed action is
published onto the Foundation event bus, it is captured as append-only audit (PC-16 / OP-C3)
and metered (PC-12).

The service is deterministic: the same identity registrations, the same consumed request
state, and the same ordered sequence of calls yield the same
:class:`~platform.execution_dashboard.evidence.DashboardEvidence` fingerprint (P5).
:func:`build_execution_dashboard_service` provides the default wiring;
:func:`~platform.execution_dashboard.bootstrap.bootstrap_execution_dashboard` composes it
onto a :class:`~platform.foundation.bootstrap.PlatformContext`.
"""

from __future__ import annotations

from dataclasses import dataclass
from platform.execution_dashboard.contracts import (
    EXECUTION_DASHBOARD_GROUP,
    OBSERVED_GENERATION_EVENTS,
    OBSERVED_GENERATION_METRICS,
    DashboardAction,
    permission_for,
)
from platform.execution_dashboard.errors import (
    DashboardAccessError,
    DashboardServiceError,
)
from platform.execution_dashboard.evidence import DashboardEvidence
from platform.execution_dashboard.health import (
    DashboardHealth,
    execution_dashboard_health_checks,
)
from platform.execution_dashboard.search import DashboardSearch
from platform.execution_dashboard.views import (
    DashboardSummary,
    DashboardView,
    ExecutionSnapshot,
    HealthSnapshot,
    QueueSummary,
    RequestMetrics,
    RequestTrend,
)
from platform.foundation.contracts import content_hash
from platform.foundation.events import EventBus
from platform.foundation.identity import Permission, Principal
from platform.generation.contracts import GenerationRequest, RequestStatus
from platform.generation.lifecycle import RequestEvent
from platform.generation.search import RequestSearchResponse
from platform.generation.service import GenerationRequestService
from platform.identity.contracts import AccessDecision
from platform.identity.errors import IdentityError
from platform.identity.service import AuthorizationService
from platform.observability.health import HealthRegistry
from platform.observability.service import ObservabilityService
from platform.workspace.isolation import tenants_isolated
from typing import Any

#: Governed events published onto the Foundation event bus (observed as PC-16 audit).
DASHBOARD_VIEWED_EVENT = "dashboard.view.rendered"
DASHBOARD_SUMMARY_EVENT = "dashboard.summary.viewed"
DASHBOARD_QUEUE_EVENT = "dashboard.queue.inspected"
DASHBOARD_CENSUS_EVENT = "dashboard.census.viewed"
DASHBOARD_TREND_EVENT = "dashboard.trend.viewed"
DASHBOARD_HEALTH_EVENT = "dashboard.health.inspected"
DASHBOARD_SNAPSHOT_EVENT = "dashboard.request.inspected"
DASHBOARD_SEARCH_EVENT = "dashboard.search.performed"
DASHBOARD_HEALTH_CHANGED_EVENT = "dashboard.health.changed"
DASHBOARD_ACCESS_EVENT = "dashboard.access.evaluated"

#: The stable subject used for surface-scoped (non-request) governed events.
_RUNTIME_SUBJECT = "platform.execution_dashboard.runtime"

# --------------------------------------------------------------------------- #
# Observability metric names (PC-12 monitoring; reproducible, no wall-clock).  #
# --------------------------------------------------------------------------- #
METRIC_VIEWS = "dashboard.views"
METRIC_SUMMARIES = "dashboard.summaries"
METRIC_QUEUE_INSPECTIONS = "dashboard.queue_inspections"
METRIC_CENSUS_VIEWS = "dashboard.census_views"
METRIC_TREND_VIEWS = "dashboard.trend_views"
METRIC_HEALTH_INSPECTIONS = "dashboard.health_inspections"
METRIC_SEARCHES = "dashboard.searches"


@dataclass(frozen=True, slots=True)
class DashboardAccess:
    """An immutable, content-addressed execution-dashboard access decision (fail-closed).

    Composes identity authorization (READ) and the requested tenant scope into a single
    verdict for one ``(principal, action, tenant)`` surface request. The dashboard is
    read-only, so there is no owner/mutation gate; per-request tenant isolation is applied
    when projecting the data.
    """

    principal_id: str
    action: DashboardAction
    permission: Permission
    granted: bool
    reason: str
    tenant: str | None
    access_id: str = ""

    @classmethod
    def create(
        cls,
        *,
        action: DashboardAction,
        permission: Permission,
        granted: bool,
        reason: str,
        decision: AccessDecision,
        tenant: str | None,
    ) -> DashboardAccess:
        principal_id = decision.request.principal_id
        core = {
            "principal_id": principal_id,
            "action": action.value,
            "permission": permission.value,
            "granted": granted,
            "reason": reason,
            "tenant": tenant,
        }
        return cls(
            principal_id=principal_id,
            action=action,
            permission=permission,
            granted=granted,
            reason=reason,
            tenant=tenant,
            access_id=f"UCOS-EDAC-{content_hash(core)[:16]}",
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "access_id": self.access_id,
            "principal_id": self.principal_id,
            "action": self.action.value,
            "permission": self.permission.value,
            "granted": self.granted,
            "reason": self.reason,
            "tenant": self.tenant,
        }


class ExecutionDashboardService:
    """The governed L3 composition point for the UCOS Execution Dashboard Runtime."""

    __slots__ = (
        "_generation",
        "_authorization",
        "_search",
        "_health",
        "_health_registry",
        "_observability",
        "_events",
        "_access_evaluations",
        "_view_count",
        "_search_count",
        "_last_health_status",
    )

    def __init__(
        self,
        *,
        generation: GenerationRequestService,
        authorization: AuthorizationService,
        search: DashboardSearch,
        health: DashboardHealth,
        health_registry: HealthRegistry,
        observability: ObservabilityService | None = None,
        events: EventBus | None = None,
    ) -> None:
        if not isinstance(generation, GenerationRequestService):
            raise DashboardServiceError("a valid GenerationRequestService is required")
        if not isinstance(authorization, AuthorizationService):
            raise DashboardServiceError("a valid AuthorizationService is required")
        if not isinstance(search, DashboardSearch):
            raise DashboardServiceError("a valid DashboardSearch is required")
        if not isinstance(health, DashboardHealth):
            raise DashboardServiceError("a valid DashboardHealth is required")
        if not isinstance(health_registry, HealthRegistry):
            raise DashboardServiceError("a valid HealthRegistry is required")
        if observability is not None and not isinstance(observability, ObservabilityService):
            raise DashboardServiceError(
                "observability must be an ObservabilityService when provided"
            )
        if events is not None and not isinstance(events, EventBus):
            raise DashboardServiceError("events must be an EventBus when provided")
        self._generation = generation
        self._authorization = authorization
        self._search = search
        self._health = health
        self._health_registry = health_registry
        self._observability = observability
        self._events = events
        self._access_evaluations = 0
        self._view_count = 0
        self._search_count = 0
        self._last_health_status = self._current_health_status()

    # -- component access -------------------------------------------------------

    @property
    def generation(self) -> GenerationRequestService:
        return self._generation

    @property
    def registry(self):  # -> GenerationRequestRegistry
        """The consumed generation request registry (read source, by reference)."""
        return self._generation.registry

    @property
    def authorization(self) -> AuthorizationService:
        return self._authorization

    @property
    def health(self) -> DashboardHealth:
        return self._health

    @property
    def observability(self) -> ObservabilityService | None:
        return self._observability

    @property
    def access_evaluation_count(self) -> int:
        return self._access_evaluations

    @property
    def view_count(self) -> int:
        return self._view_count

    @property
    def search_count(self) -> int:
        return self._search_count

    @property
    def observed_generation_events(self) -> tuple[str, ...]:
        """The EPIC-007 governed events this dashboard surfaces (by reference)."""
        return OBSERVED_GENERATION_EVENTS

    @property
    def observed_generation_metrics(self) -> tuple[str, ...]:
        """The EPIC-007 observability metrics this dashboard surfaces (by reference)."""
        return OBSERVED_GENERATION_METRICS

    # -- the full navigation view (Program Surface #8) --------------------------

    def view(
        self,
        session_id: str,
        *,
        now: int,
        tenant: str | None = None,
        workspace_id: str | None = None,
        project_id: str | None = None,
        status: RequestStatus | None = None,
    ) -> DashboardView:
        """Render the full dashboard navigation view (requires VIEW/READ; fail-closed)."""
        access = self._require_access(session_id, DashboardAction.VIEW, now=now, tenant=tenant)
        principal = self._authorization.principals.get(access.principal_id)
        requests = self._scoped_requests(principal, tenant, workspace_id, project_id, status)
        snapshots = self._snapshots(requests)
        summary = self._compose_summary(requests)
        trend = RequestTrend.from_events(self._scoped_events(requests))
        dashboard_view = DashboardView.create(
            principal_id=principal.principal_id,
            tenant=tenant,
            summary=summary,
            snapshots=snapshots,
            trend=trend,
        )
        self._view_count += 1
        self._metric_counter(METRIC_VIEWS)
        self._emit(
            DASHBOARD_VIEWED_EVENT,
            subject=principal.principal_id,
            payload={
                "view_id": dashboard_view.view_id,
                "tenant": tenant,
                "request_count": summary.metrics.total,
                "queue_depth": summary.queue.queue_depth,
            },
        )
        self._emit_health_change()
        return dashboard_view

    # -- summary / queue / census / trend / health -----------------------------

    def summary(
        self,
        session_id: str,
        *,
        now: int,
        tenant: str | None = None,
        workspace_id: str | None = None,
        project_id: str | None = None,
        status: RequestStatus | None = None,
    ) -> DashboardSummary:
        """Compose the dashboard summary (metrics+queue+health) (requires SUMMARIZE)."""
        access = self._require_access(session_id, DashboardAction.SUMMARIZE, now=now, tenant=tenant)
        principal = self._authorization.principals.get(access.principal_id)
        requests = self._scoped_requests(principal, tenant, workspace_id, project_id, status)
        summary = self._compose_summary(requests)
        self._metric_counter(METRIC_SUMMARIES)
        self._emit(
            DASHBOARD_SUMMARY_EVENT,
            subject=principal.principal_id,
            payload={"summary_id": summary.summary_id, "tenant": tenant},
        )
        self._emit_health_change()
        return summary

    def queue(
        self,
        session_id: str,
        *,
        now: int,
        tenant: str | None = None,
        workspace_id: str | None = None,
        project_id: str | None = None,
    ) -> QueueSummary:
        """Return the deterministic queue-depth census (requires INSPECT_QUEUE)."""
        access = self._require_access(
            session_id, DashboardAction.INSPECT_QUEUE, now=now, tenant=tenant
        )
        principal = self._authorization.principals.get(access.principal_id)
        requests = self._scoped_requests(principal, tenant, workspace_id, project_id, None)
        queue = QueueSummary.from_requests(requests)
        self._metric_counter(METRIC_QUEUE_INSPECTIONS)
        self._emit(
            DASHBOARD_QUEUE_EVENT,
            subject=principal.principal_id,
            payload={"summary_id": queue.summary_id, "queue_depth": queue.queue_depth},
        )
        return queue

    def census(
        self,
        session_id: str,
        *,
        now: int,
        tenant: str | None = None,
        workspace_id: str | None = None,
        project_id: str | None = None,
    ) -> RequestMetrics:
        """Return the aggregate request census / status aggregation (requires CENSUS)."""
        access = self._require_access(session_id, DashboardAction.CENSUS, now=now, tenant=tenant)
        principal = self._authorization.principals.get(access.principal_id)
        requests = self._scoped_requests(principal, tenant, workspace_id, project_id, None)
        metrics = RequestMetrics.from_requests(requests)
        self._metric_counter(METRIC_CENSUS_VIEWS)
        self._emit(
            DASHBOARD_CENSUS_EVENT,
            subject=principal.principal_id,
            payload={"metrics_id": metrics.metrics_id, "total": metrics.total},
        )
        return metrics

    def trends(
        self,
        session_id: str,
        *,
        now: int,
        tenant: str | None = None,
        workspace_id: str | None = None,
        project_id: str | None = None,
    ) -> RequestTrend:
        """Generate the deterministic lifecycle-transition trend (requires TREND)."""
        access = self._require_access(session_id, DashboardAction.TREND, now=now, tenant=tenant)
        principal = self._authorization.principals.get(access.principal_id)
        requests = self._scoped_requests(principal, tenant, workspace_id, project_id, None)
        trend = RequestTrend.from_events(self._scoped_events(requests))
        self._metric_counter(METRIC_TREND_VIEWS)
        self._emit(
            DASHBOARD_TREND_EVENT,
            subject=principal.principal_id,
            payload={"trend_id": trend.trend_id, "transitions": trend.total_transitions},
        )
        return trend

    def health_view(self, session_id: str, *, now: int) -> HealthSnapshot:
        """Return the dashboard health snapshot + surfaced source health (INSPECT_HEALTH)."""
        self._require_access(session_id, DashboardAction.INSPECT_HEALTH, now=now)
        snapshot = self._health_snapshot()
        self._metric_counter(METRIC_HEALTH_INSPECTIONS)
        self._emit(
            DASHBOARD_HEALTH_EVENT,
            subject=_RUNTIME_SUBJECT,
            payload={"snapshot_id": snapshot.snapshot_id, "status": snapshot.status},
        )
        self._emit_health_change()
        return snapshot

    # -- request visibility -----------------------------------------------------

    def list_snapshots(
        self,
        session_id: str,
        *,
        now: int,
        tenant: str | None = None,
        workspace_id: str | None = None,
        project_id: str | None = None,
        status: RequestStatus | None = None,
    ) -> tuple[ExecutionSnapshot, ...]:
        """List the per-request execution snapshots a caller may see (requires DISCOVER)."""
        principal = self._resolve_principal(session_id, now)
        if principal is None:
            return ()
        decision = self._authorization.authorize_principal(
            principal, EXECUTION_DASHBOARD_GROUP, Permission.READ, tenant=tenant
        )
        if not decision.permitted:
            return ()
        requests = self._scoped_requests(principal, tenant, workspace_id, project_id, status)
        return self._snapshots(requests)

    def snapshot_of(self, session_id: str, request_id: str, *, now: int) -> ExecutionSnapshot:
        """Return a single per-request execution snapshot (requires INSPECT; fail-closed)."""
        request = self._generation.registry.get(request_id)
        access = self._require_access(
            session_id, DashboardAction.INSPECT, now=now, tenant=request.tenant
        )
        principal = self._authorization.principals.get(access.principal_id)
        if tenants_isolated(principal.tenant, request.tenant):
            raise DashboardAccessError(
                "cross-tenant request inspection denied",
                reason="tenant-isolation-violation",
                request_id=request_id,
            )
        snapshot = self._snapshot(request)
        self._emit(
            DASHBOARD_SNAPSHOT_EVENT,
            subject=principal.principal_id,
            payload={"request_id": request_id, "snapshot_id": snapshot.snapshot_id},
        )
        return snapshot

    # -- search -----------------------------------------------------------------

    def search(
        self,
        session_id: str,
        query: str,
        *,
        now: int,
        tenant: str | None = None,
        workspace_id: str | None = None,
        project_id: str | None = None,
        status: RequestStatus | None = None,
    ) -> RequestSearchResponse:
        """Run an authorization- and isolation-scoped dashboard request search."""
        response = self._search.search(
            session_id,
            query,
            now=now,
            tenant=tenant,
            workspace_id=workspace_id,
            project_id=project_id,
            status=status,
        )
        self._search_count += 1
        self._metric_counter(METRIC_SEARCHES)
        self._emit(
            DASHBOARD_SEARCH_EVENT,
            subject=_RUNTIME_SUBJECT,
            payload={
                "query": query,
                "authorized": response.authorized,
                "result_count": len(response.results),
            },
        )
        return response

    # -- access evaluation ------------------------------------------------------

    def evaluate_access(
        self,
        session_id: str,
        action: DashboardAction,
        *,
        now: int,
        tenant: str | None = None,
    ) -> DashboardAccess:
        """Evaluate composed dashboard access (identity READ on ``execution-dashboard``).

        Denials are returned as data (``granted == False``); a malformed action raises.
        Every evaluation is emitted as a governed ``dashboard.access.evaluated`` event
        (PC-16). Per-request tenant isolation is applied separately during projection.
        """
        if not isinstance(action, DashboardAction):
            raise DashboardServiceError("action must be a DashboardAction")
        permission = permission_for(action)
        decision = self._authorization.authorize(
            session_id,
            EXECUTION_DASHBOARD_GROUP,
            permission,
            now=now,
            tenant=tenant,
            resource=_RUNTIME_SUBJECT,
        )
        access = DashboardAccess.create(
            action=action,
            permission=permission,
            granted=decision.permitted,
            reason="granted" if decision.permitted else decision.reason,
            decision=decision,
            tenant=tenant,
        )
        self._access_evaluations += 1
        self._emit(
            DASHBOARD_ACCESS_EVENT,
            subject=access.principal_id,
            payload={
                "action": action.value,
                "granted": access.granted,
                "reason": access.reason,
                "tenant": tenant,
            },
        )
        return access

    # -- health integration -----------------------------------------------------

    def health_report(self) -> dict[str, Any]:
        """The execution-dashboard runtime health endpoint (reuses the observability model)."""
        return self._health_registry.endpoint(self._health.probe())

    # -- evidence ---------------------------------------------------------------

    def evidence(self) -> DashboardEvidence:
        """Produce deterministic Dashboard Evidence over the runtime state."""
        report = self._health_registry.report(self._health.probe())
        requests = self._generation.registry.all()
        metrics = RequestMetrics.from_requests(requests)
        queue = QueueSummary.from_requests(requests)
        return DashboardEvidence.create(
            registry_fingerprint=self._generation.registry.fingerprint(),
            request_count=metrics.total,
            active_count=metrics.active,
            terminal_count=metrics.terminal,
            queue_depth=queue.queue_depth,
            view_count=self._view_count,
            search_count=self._search_count,
            access_evaluation_count=self._access_evaluations,
            status_census=metrics.status_census,
            health_status=report.status.value,
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "request_count": len(self._generation.registry),
            "view_count": self._view_count,
            "search_count": self._search_count,
            "access_evaluation_count": self._access_evaluations,
            "observability_bound": self._observability is not None,
            "evidence": self.evidence().to_dict(),
        }

    # -- internals --------------------------------------------------------------

    def _require_access(
        self,
        session_id: str,
        action: DashboardAction,
        *,
        now: int,
        tenant: str | None = None,
    ) -> DashboardAccess:
        access = self.evaluate_access(session_id, action, now=now, tenant=tenant)
        if not access.granted:
            raise DashboardAccessError(
                "execution dashboard action denied",
                reason=access.reason,
                action=action.value,
            )
        return access

    def _resolve_principal(self, session_id: str, now: int) -> Principal | None:
        try:
            session = self._authorization.sessions.validate(session_id, now)
            return self._authorization.principals.get(session.principal_id)
        except IdentityError:
            return None

    def _scoped_requests(
        self,
        principal: Principal,
        tenant: str | None,
        workspace_id: str | None,
        project_id: str | None,
        status: RequestStatus | None,
    ) -> tuple[GenerationRequest, ...]:
        """The requests a principal may see (discover + tenant/workspace isolation)."""
        return tuple(
            request
            for request in self._generation.registry.discover(
                workspace_id=workspace_id,
                project_id=project_id,
                tenant=tenant,
                status=status,
            )
            if not tenants_isolated(principal.tenant, request.tenant)
        )

    def _scoped_events(self, requests: tuple[GenerationRequest, ...]) -> tuple[RequestEvent, ...]:
        """The lifecycle events belonging to the in-scope requests (ordered)."""
        visible = {request.request_id for request in requests}
        return tuple(e for e in self._generation.registry.events if e.request_id in visible)

    def _snapshot(self, request: GenerationRequest) -> ExecutionSnapshot:
        derived = self._generation.status_of(request.request_id)
        return ExecutionSnapshot.from_request(request, derived)

    def _snapshots(self, requests: tuple[GenerationRequest, ...]) -> tuple[ExecutionSnapshot, ...]:
        return tuple(self._snapshot(request) for request in requests)

    def _compose_summary(self, requests: tuple[GenerationRequest, ...]) -> DashboardSummary:
        metrics = RequestMetrics.from_requests(requests)
        queue = QueueSummary.from_requests(requests)
        health = self._health_snapshot()
        return DashboardSummary.create(metrics=metrics, queue=queue, health=health)

    def _health_snapshot(self) -> HealthSnapshot:
        endpoint = self._health_registry.endpoint(self._health.probe())
        source_status = self._generation.health_report().get("status")
        return HealthSnapshot.from_endpoint(endpoint, source_status=source_status)

    def _current_health_status(self) -> str:
        return self._health_registry.report(self._health.probe()).status.value

    def _emit_health_change(self) -> None:
        status = self._current_health_status()
        if status != self._last_health_status:
            self._last_health_status = status
            self._emit(
                DASHBOARD_HEALTH_CHANGED_EVENT,
                subject=_RUNTIME_SUBJECT,
                payload={"status": status},
            )

    def _emit(self, event_type: str, *, subject: str, payload: dict[str, Any]) -> None:
        if self._events is not None:
            self._events.publish(
                event_type,
                source="platform.execution_dashboard.runtime",
                subject=subject,
                payload=payload,
            )

    def _metric_counter(self, name: str, **labels: str) -> None:
        if self._observability is not None:
            self._observability.metrics.counter(name, 1.0, **labels)


def build_execution_dashboard_service(
    *,
    generation: GenerationRequestService,
    authorization: AuthorizationService,
    observability: ObservabilityService | None = None,
    events: EventBus | None = None,
) -> ExecutionDashboardService:
    """Default, registry-driven composition of the Execution Dashboard Runtime.

    Wires the dashboard search (over the consumed generation registry and the supplied
    Identity ``authorization`` service, gated on ``execution-dashboard``), the dashboard
    health probe and a health registry seeded with the dashboard health checks, and — when
    supplied — the observability layer and event bus. The Generation Request Runtime
    (EPIC-007) is consumed **by reference** as the read source; it is never modified.
    """
    if not isinstance(generation, GenerationRequestService):
        raise DashboardServiceError(
            "build_execution_dashboard_service requires a GenerationRequestService"
        )
    if not isinstance(authorization, AuthorizationService):
        raise DashboardServiceError(
            "build_execution_dashboard_service requires an AuthorizationService"
        )
    search = DashboardSearch(generation.registry, authorization)
    health = DashboardHealth(generation.registry)
    health_registry = HealthRegistry()
    for check in execution_dashboard_health_checks():
        health_registry.register(check)
    return ExecutionDashboardService(
        generation=generation,
        authorization=authorization,
        search=search,
        health=health,
        health_registry=health_registry,
        observability=observability,
        events=events,
    )


__all__ = [
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
]
