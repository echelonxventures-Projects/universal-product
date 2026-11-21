"""EC2-TASK-000128 — Execution Dashboard Domain Model (EC2-EPIC-008).

The immutable, content-addressed **read-only view value types** the Execution Dashboard
Runtime surfaces (Program §2.1 #8/#10, PC-08 execution visibility). Every view is a
**pure projection** of already-recorded Generation Request state (EPIC-007) — a
:class:`~platform.generation.contracts.GenerationRequest`, its derived
:class:`~platform.generation.status.DerivedRequestStatus`, and the append-only
:class:`~platform.generation.lifecycle.RequestEvent` log — computed with **no wall-clock
and no ambient state**, so an identical source state yields byte-identical views and
fingerprints (P5). The dashboard **records no lifecycle, execution, or generation state of
its own** and **re-derives no status** (P10): it reuses the frozen
:class:`~platform.generation.contracts.RequestStatus` /
:class:`~platform.generation.contracts.ExecutionState` /
:class:`~platform.generation.status.RequestPosture` vocabulary and the
:data:`~platform.generation.contracts.TERMINAL_STATUSES` set verbatim.

Domain:
    * :class:`ExecutionSnapshot` — a per-request operational snapshot (identity, binding,
      lifecycle + execution + posture, terminality) surfaced by reference.
    * :class:`QueueSummary` — the deterministic queue-depth census (waiting / queued /
      dispatched / running / active / terminal + full status census).
    * :class:`RequestMetrics` — the aggregate request census (status / execution-state /
      family counts, terminal/active, throughput outcomes, success rate).
    * :class:`RequestTrend` — a deterministic lifecycle-transition trend over the event
      log (by target/source status, terminal transitions, logical tick range).
    * :class:`HealthSnapshot` — a projection of the dashboard health endpoint plus the
      surfaced upstream generation-runtime health.
    * :class:`DashboardSummary` — the top-level aggregate (metrics + queue + health).
    * :class:`DashboardView` — the full navigation surface (summary + snapshots + trend),
      scoped to the viewing principal / tenant.
"""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from platform.execution_dashboard.errors import DashboardViewError
from platform.foundation.contracts import content_hash
from platform.generation.contracts import (
    TERMINAL_STATUSES,
    ExecutionState,
    GenerationRequest,
    RequestStatus,
)
from platform.generation.lifecycle import RequestEvent
from platform.generation.status import DerivedRequestStatus
from typing import Any

#: The lifecycle statuses whose execution posture is "waiting" (pre-queue admission).
_WAITING_STATUSES: frozenset[RequestStatus] = frozenset(
    {RequestStatus.SUBMITTED, RequestStatus.VALIDATING, RequestStatus.APPROVED}
)


@dataclass(frozen=True, slots=True)
class ExecutionSnapshot:
    """An immutable, content-addressed per-request operational snapshot (by reference)."""

    snapshot_id: str
    request_id: str
    slug: str
    blueprint_ref: str
    workspace_id: str
    project_id: str | None
    tenant: str | None
    owner_subject: str
    family: str
    status: str
    execution_state: str
    posture: str
    is_dispatched: bool
    is_terminal: bool
    is_traceable: bool
    submitted_tick: int

    @classmethod
    def from_request(
        cls, request: GenerationRequest, derived: DerivedRequestStatus
    ) -> ExecutionSnapshot:
        """Project a snapshot from a request and its certified derived status (pure)."""
        if not isinstance(request, GenerationRequest):
            raise DashboardViewError("ExecutionSnapshot requires a GenerationRequest")
        if not isinstance(derived, DerivedRequestStatus):
            raise DashboardViewError("ExecutionSnapshot requires a DerivedRequestStatus")
        if derived.request_id != request.request_id:
            raise DashboardViewError(
                "snapshot request/derived-status mismatch",
                request_id=request.request_id,
                derived_id=derived.request_id,
            )
        core = {
            "request_id": request.request_id,
            "slug": request.slug,
            "blueprint_ref": request.blueprint_ref,
            "workspace_id": request.workspace_id,
            "project_id": request.project_id,
            "tenant": request.tenant,
            "owner_subject": request.owner_subject,
            "family": request.family.value,
            "status": request.status.value,
            "execution_state": derived.execution_state.value,
            "posture": derived.posture.value,
            "is_dispatched": derived.is_dispatched,
            "is_terminal": derived.is_terminal,
            "is_traceable": derived.is_traceable,
            "submitted_tick": request.submitted_tick,
        }
        return cls(
            snapshot_id=f"UCOS-EDSN-{content_hash(core)[:16]}",
            request_id=request.request_id,
            slug=request.slug,
            blueprint_ref=request.blueprint_ref,
            workspace_id=request.workspace_id,
            project_id=request.project_id,
            tenant=request.tenant,
            owner_subject=request.owner_subject,
            family=request.family.value,
            status=request.status.value,
            execution_state=derived.execution_state.value,
            posture=derived.posture.value,
            is_dispatched=derived.is_dispatched,
            is_terminal=derived.is_terminal,
            is_traceable=derived.is_traceable,
            submitted_tick=request.submitted_tick,
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "snapshot_id": self.snapshot_id,
            "request_id": self.request_id,
            "slug": self.slug,
            "blueprint_ref": self.blueprint_ref,
            "workspace_id": self.workspace_id,
            "project_id": self.project_id,
            "tenant": self.tenant,
            "owner_subject": self.owner_subject,
            "family": self.family,
            "status": self.status,
            "execution_state": self.execution_state,
            "posture": self.posture,
            "is_dispatched": self.is_dispatched,
            "is_terminal": self.is_terminal,
            "is_traceable": self.is_traceable,
            "submitted_tick": self.submitted_tick,
        }

    def fingerprint(self) -> str:
        return content_hash(self.to_dict())


def _status_census(requests: tuple[GenerationRequest, ...]) -> dict[str, int]:
    """A deterministic per-status census (every status present, stable order)."""
    tally = {status.value: 0 for status in RequestStatus}
    for request in requests:
        tally[request.status.value] += 1
    return tally


@dataclass(frozen=True, slots=True)
class QueueSummary:
    """An immutable, content-addressed queue-depth census (deterministic)."""

    summary_id: str
    total: int
    waiting: int
    queue_depth: int
    dispatched: int
    running: int
    active: int
    terminal: int
    status_census: tuple[tuple[str, int], ...]

    @classmethod
    def from_requests(cls, requests: Iterable[GenerationRequest]) -> QueueSummary:
        """Project the queue census from the requests in scope (pure)."""
        items = tuple(requests)
        for request in items:
            if not isinstance(request, GenerationRequest):
                raise DashboardViewError("QueueSummary requires GenerationRequest items")
        census = _status_census(items)
        waiting = sum(census[s.value] for s in _WAITING_STATUSES)
        queue_depth = census[RequestStatus.QUEUED.value]
        dispatched = census[RequestStatus.DISPATCHED.value]
        running = census[RequestStatus.RUNNING.value]
        terminal = sum(census[s.value] for s in TERMINAL_STATUSES)
        active = len(items) - terminal
        census_pairs = tuple(sorted(census.items()))
        core = {
            "total": len(items),
            "waiting": waiting,
            "queue_depth": queue_depth,
            "dispatched": dispatched,
            "running": running,
            "active": active,
            "terminal": terminal,
            "status_census": [list(pair) for pair in census_pairs],
        }
        return cls(
            summary_id=f"UCOS-EDQS-{content_hash(core)[:16]}",
            total=len(items),
            waiting=waiting,
            queue_depth=queue_depth,
            dispatched=dispatched,
            running=running,
            active=active,
            terminal=terminal,
            status_census=census_pairs,
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "summary_id": self.summary_id,
            "total": self.total,
            "waiting": self.waiting,
            "queue_depth": self.queue_depth,
            "dispatched": self.dispatched,
            "running": self.running,
            "active": self.active,
            "terminal": self.terminal,
            "status_census": {name: count for name, count in self.status_census},
        }

    def fingerprint(self) -> str:
        return content_hash(self.to_dict())


@dataclass(frozen=True, slots=True)
class RequestMetrics:
    """An immutable, content-addressed aggregate request census (status aggregation)."""

    metrics_id: str
    total: int
    active: int
    terminal: int
    dispatched: int
    completed: int
    failed: int
    cancelled: int
    success_rate: float
    status_census: tuple[tuple[str, int], ...]
    execution_census: tuple[tuple[str, int], ...]
    family_census: tuple[tuple[str, int], ...]

    @classmethod
    def from_requests(cls, requests: Iterable[GenerationRequest]) -> RequestMetrics:
        """Project the aggregate census from the requests in scope (pure)."""
        items = tuple(requests)
        for request in items:
            if not isinstance(request, GenerationRequest):
                raise DashboardViewError("RequestMetrics requires GenerationRequest items")
        status_census = _status_census(items)
        execution_census = {state.value: 0 for state in ExecutionState}
        family_census: dict[str, int] = {}
        for request in items:
            execution_census[request.execution_state.value] += 1
            family_census[request.family.value] = family_census.get(request.family.value, 0) + 1
        terminal = sum(status_census[s.value] for s in TERMINAL_STATUSES)
        active = len(items) - terminal
        dispatched = sum(1 for r in items if r.is_dispatched)
        completed = status_census[RequestStatus.COMPLETED.value]
        failed = status_census[RequestStatus.FAILED.value]
        cancelled = status_census[RequestStatus.CANCELLED.value]
        # Success rate = completed / terminal (0.0 when nothing has terminated). Pure.
        success_rate = round(completed / terminal, 6) if terminal else 0.0
        status_pairs = tuple(sorted(status_census.items()))
        execution_pairs = tuple(sorted(execution_census.items()))
        family_pairs = tuple(sorted(family_census.items()))
        core = {
            "total": len(items),
            "active": active,
            "terminal": terminal,
            "dispatched": dispatched,
            "completed": completed,
            "failed": failed,
            "cancelled": cancelled,
            "success_rate": success_rate,
            "status_census": [list(p) for p in status_pairs],
            "execution_census": [list(p) for p in execution_pairs],
            "family_census": [list(p) for p in family_pairs],
        }
        return cls(
            metrics_id=f"UCOS-EDMT-{content_hash(core)[:16]}",
            total=len(items),
            active=active,
            terminal=terminal,
            dispatched=dispatched,
            completed=completed,
            failed=failed,
            cancelled=cancelled,
            success_rate=success_rate,
            status_census=status_pairs,
            execution_census=execution_pairs,
            family_census=family_pairs,
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "metrics_id": self.metrics_id,
            "total": self.total,
            "active": self.active,
            "terminal": self.terminal,
            "dispatched": self.dispatched,
            "completed": self.completed,
            "failed": self.failed,
            "cancelled": self.cancelled,
            "success_rate": self.success_rate,
            "status_census": {name: count for name, count in self.status_census},
            "execution_census": {name: count for name, count in self.execution_census},
            "family_census": {name: count for name, count in self.family_census},
        }

    def fingerprint(self) -> str:
        return content_hash(self.to_dict())


@dataclass(frozen=True, slots=True)
class RequestTrend:
    """An immutable, content-addressed lifecycle-transition trend (deterministic)."""

    trend_id: str
    total_transitions: int
    terminal_transitions: int
    first_tick: int
    last_tick: int
    by_target: tuple[tuple[str, int], ...]
    by_source: tuple[tuple[str, int], ...]

    @classmethod
    def from_events(cls, events: Iterable[RequestEvent]) -> RequestTrend:
        """Project a deterministic transition trend from the lifecycle event log (pure)."""
        items = tuple(events)
        for event in items:
            if not isinstance(event, RequestEvent):
                raise DashboardViewError("RequestTrend requires RequestEvent items")
        by_target: dict[str, int] = {}
        by_source: dict[str, int] = {}
        terminal_transitions = 0
        ticks: list[int] = []
        for event in items:
            by_target[event.to_status.value] = by_target.get(event.to_status.value, 0) + 1
            by_source[event.from_status.value] = by_source.get(event.from_status.value, 0) + 1
            if event.to_status in TERMINAL_STATUSES:
                terminal_transitions += 1
            ticks.append(event.tick)
        first_tick = min(ticks) if ticks else 0
        last_tick = max(ticks) if ticks else 0
        target_pairs = tuple(sorted(by_target.items()))
        source_pairs = tuple(sorted(by_source.items()))
        core = {
            "total_transitions": len(items),
            "terminal_transitions": terminal_transitions,
            "first_tick": first_tick,
            "last_tick": last_tick,
            "by_target": [list(p) for p in target_pairs],
            "by_source": [list(p) for p in source_pairs],
        }
        return cls(
            trend_id=f"UCOS-EDTR-{content_hash(core)[:16]}",
            total_transitions=len(items),
            terminal_transitions=terminal_transitions,
            first_tick=first_tick,
            last_tick=last_tick,
            by_target=target_pairs,
            by_source=source_pairs,
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "trend_id": self.trend_id,
            "total_transitions": self.total_transitions,
            "terminal_transitions": self.terminal_transitions,
            "first_tick": self.first_tick,
            "last_tick": self.last_tick,
            "by_target": {name: count for name, count in self.by_target},
            "by_source": {name: count for name, count in self.by_source},
        }

    def fingerprint(self) -> str:
        return content_hash(self.to_dict())


@dataclass(frozen=True, slots=True)
class HealthSnapshot:
    """An immutable, content-addressed projection of the dashboard health endpoint."""

    snapshot_id: str
    status: str
    healthy: bool
    checks: tuple[tuple[str, str, str], ...]
    source_status: str | None

    @classmethod
    def from_endpoint(
        cls, endpoint: Mapping[str, Any], *, source_status: str | None = None
    ) -> HealthSnapshot:
        """Project a health snapshot from a health-registry endpoint view (pure)."""
        if not isinstance(endpoint, Mapping):
            raise DashboardViewError("HealthSnapshot requires an endpoint mapping")
        try:
            status = str(endpoint["status"])
            healthy = bool(endpoint["healthy"])
            raw_checks = endpoint["checks"]
        except (KeyError, TypeError) as exc:
            raise DashboardViewError("malformed health endpoint view") from exc
        checks = tuple(
            (str(c["name"]), str(c["status"]), str(c.get("detail", ""))) for c in raw_checks
        )
        core = {
            "status": status,
            "healthy": healthy,
            "checks": [list(c) for c in checks],
            "source_status": source_status,
        }
        return cls(
            snapshot_id=f"UCOS-EDHS-{content_hash(core)[:16]}",
            status=status,
            healthy=healthy,
            checks=checks,
            source_status=source_status,
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "snapshot_id": self.snapshot_id,
            "status": self.status,
            "healthy": self.healthy,
            "checks": [
                {"name": name, "status": status, "detail": detail}
                for name, status, detail in self.checks
            ],
            "source_status": self.source_status,
        }

    def fingerprint(self) -> str:
        return content_hash(self.to_dict())


@dataclass(frozen=True, slots=True)
class DashboardSummary:
    """An immutable, content-addressed top-level dashboard aggregate (metrics+queue+health)."""

    summary_id: str
    metrics: RequestMetrics
    queue: QueueSummary
    health: HealthSnapshot

    @classmethod
    def create(
        cls,
        *,
        metrics: RequestMetrics,
        queue: QueueSummary,
        health: HealthSnapshot,
    ) -> DashboardSummary:
        """Aggregate the census, queue, and health views into one summary (pure)."""
        if not isinstance(metrics, RequestMetrics):
            raise DashboardViewError("DashboardSummary requires a RequestMetrics")
        if not isinstance(queue, QueueSummary):
            raise DashboardViewError("DashboardSummary requires a QueueSummary")
        if not isinstance(health, HealthSnapshot):
            raise DashboardViewError("DashboardSummary requires a HealthSnapshot")
        core = {
            "metrics": metrics.fingerprint(),
            "queue": queue.fingerprint(),
            "health": health.fingerprint(),
        }
        return cls(
            summary_id=f"UCOS-EDSM-{content_hash(core)[:16]}",
            metrics=metrics,
            queue=queue,
            health=health,
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "summary_id": self.summary_id,
            "metrics": self.metrics.to_dict(),
            "queue": self.queue.to_dict(),
            "health": self.health.to_dict(),
        }

    def fingerprint(self) -> str:
        return content_hash(self.to_dict())


@dataclass(frozen=True, slots=True)
class DashboardView:
    """An immutable, content-addressed full navigation surface, scoped to a principal."""

    view_id: str
    principal_id: str
    tenant: str | None
    summary: DashboardSummary
    snapshots: tuple[ExecutionSnapshot, ...]
    trend: RequestTrend

    @classmethod
    def create(
        cls,
        *,
        principal_id: str,
        tenant: str | None,
        summary: DashboardSummary,
        snapshots: tuple[ExecutionSnapshot, ...],
        trend: RequestTrend,
    ) -> DashboardView:
        """Compose the full dashboard view for a viewing principal (pure)."""
        if not isinstance(principal_id, str) or not principal_id:
            raise DashboardViewError("DashboardView requires a principal_id")
        if not isinstance(summary, DashboardSummary):
            raise DashboardViewError("DashboardView requires a DashboardSummary")
        if not isinstance(trend, RequestTrend):
            raise DashboardViewError("DashboardView requires a RequestTrend")
        snaps = tuple(snapshots)
        for snapshot in snaps:
            if not isinstance(snapshot, ExecutionSnapshot):
                raise DashboardViewError("DashboardView snapshots must be ExecutionSnapshots")
        core = {
            "principal_id": principal_id,
            "tenant": tenant,
            "summary": summary.fingerprint(),
            "snapshots": [s.snapshot_id for s in snaps],
            "trend": trend.fingerprint(),
        }
        return cls(
            view_id=f"UCOS-EDVW-{content_hash(core)[:16]}",
            principal_id=principal_id,
            tenant=tenant,
            summary=summary,
            snapshots=snaps,
            trend=trend,
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "view_id": self.view_id,
            "principal_id": self.principal_id,
            "tenant": self.tenant,
            "summary": self.summary.to_dict(),
            "snapshots": [s.to_dict() for s in self.snapshots],
            "trend": self.trend.to_dict(),
        }

    def fingerprint(self) -> str:
        return content_hash(self.to_dict())


__all__ = [
    "ExecutionSnapshot",
    "QueueSummary",
    "RequestMetrics",
    "RequestTrend",
    "HealthSnapshot",
    "DashboardSummary",
    "DashboardView",
]
