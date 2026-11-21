"""EC2-TASK-000117 — Generation Request Service (EC2-EPIC-007).

The single, governed **generation-request runtime composition point** (L3 Application
of the Program architecture) that composes the whole Generation Request Runtime into
one entry point — the canonical governed entry point for ALL generation activity in
EC-2 (Program Surface #8, PC-06 submission + PC-07 dispatch):

    GenerationRequestRegistry · DispatchLedger · ProvenanceLedger · RequestSearch ·
    RequestHealth  ·  (reused) AuthorizationService · WorkspaceRegistry ·
    ObservabilityService

It is a strictly **additive** layer: it authorizes only through the certified Identity
Layer (L7) on the existing ``generation-requests`` capability group — **no duplicate
authorization or identity logic, no new authority, no new capability group** — records
the recorded EC-1 classification (via the referenced blueprint) read-only, observes only
through the Observability Layer (L8), reuses the Foundation registries/events (L4/L6),
and binds each request to a parent workspace/project and a catalog blueprint **by
reference**. It re-implements none of them, modifies neither EC-1 nor any prior layer,
and writes nothing to the certified corpus (DP-03).

Every request access is fail-closed and composes gates — **identity authorization**
(RBAC §3.2), **tenant/workspace isolation** (the reused rule, P3), and — for mutating
actions — **owner/administrator scoping** — so cross-tenant access is refused in 100%
of cases. Because every governed action is published onto the Foundation event bus, it
is captured by observability as append-only audit (PC-16 / OP-C3). The runtime is the
**authoritative execution-dispatch boundary**: a request reaches the EC-1 Execution
Runtime only through :meth:`GenerationRequestService.dispatch_request`, which records an
immutable :class:`~platform.generation.dispatch.DispatchRecord` bound to the certified
engine contracts by reference — there is no runtime bypass path (§7).

The service is deterministic: the same identity registrations, workspaces, requests,
dispatches, provenance, and ordered sequence of calls yield the same
:class:`RequestEvidence` fingerprint (P5). :func:`build_generation_request_service`
provides the default wiring;
:func:`~platform.generation.bootstrap.bootstrap_generation_requests` composes it onto a
:class:`~platform.foundation.bootstrap.PlatformContext`.
"""

from __future__ import annotations

from dataclasses import dataclass
from platform.blueprints.contracts import BlueprintFamily
from platform.foundation.contracts import content_hash
from platform.foundation.events import EventBus
from platform.foundation.identity import Permission
from platform.generation.context import RequestContext
from platform.generation.contracts import (
    GENERATION_REQUEST_GROUP,
    MUTATING_ACTIONS,
    GenerationRequest,
    RequestAction,
    RequestStatus,
    permission_for,
)
from platform.generation.dispatch import (
    DEFAULT_EXECUTION_TARGET,
    DispatchLedger,
    DispatchRecord,
)
from platform.generation.errors import (
    RequestAccessError,
    RequestDispatchError,
    RequestServiceError,
)
from platform.generation.health import RequestHealth, generation_request_health_checks
from platform.generation.metadata import RequestMetadata
from platform.generation.provenance import ProvenanceLedger, RequestProvenance
from platform.generation.registry import GenerationRequestRegistry
from platform.generation.search import RequestSearch, RequestSearchResponse
from platform.generation.status import DerivedRequestStatus, derive_status
from platform.identity.contracts import AccessDecision
from platform.identity.errors import IdentityError
from platform.identity.service import AuthorizationService
from platform.observability.health import HealthRegistry
from platform.observability.service import ObservabilityService
from platform.workspace.isolation import tenants_isolated
from platform.workspace.registration import WorkspaceRegistry
from typing import Any

#: Governed events published onto the Foundation event bus (observed as PC-16).
REQUEST_SUBMITTED_EVENT = "generation.request.submitted"
REQUEST_VALIDATING_EVENT = "generation.request.validating"
REQUEST_APPROVED_EVENT = "generation.request.approved"
REQUEST_QUEUED_EVENT = "generation.request.queued"
REQUEST_DISPATCHED_EVENT = "generation.request.dispatched"
REQUEST_RUNNING_EVENT = "generation.request.running"
REQUEST_COMPLETED_EVENT = "generation.request.completed"
REQUEST_FAILED_EVENT = "generation.request.failed"
REQUEST_CANCELLED_EVENT = "generation.request.cancelled"
REQUEST_METADATA_UPDATED_EVENT = "generation.request.metadata.updated"
REQUEST_PROVENANCE_LINKED_EVENT = "generation.request.provenance.linked"
REQUEST_HEALTH_CHANGED_EVENT = "generation.request.health.changed"
REQUEST_ACCESS_EVENT = "generation.request.access.evaluated"

#: The stable subject used for runtime-scoped (non-request) governed events.
_RUNTIME_SUBJECT = "platform.generation.runtime"

# --------------------------------------------------------------------------- #
# Observability metric names (PC-12 monitoring; reproducible, no wall-clock).  #
# --------------------------------------------------------------------------- #
METRIC_SUBMITTED = "generation.requests.submitted"
METRIC_DISPATCHED = "generation.requests.dispatched"
METRIC_COMPLETED = "generation.requests.completed"
METRIC_FAILED = "generation.requests.failed"
METRIC_CANCELLED = "generation.requests.cancelled"
METRIC_QUEUE_DEPTH = "generation.requests.queue_depth"
METRIC_LIFECYCLE_LATENCY = "generation.requests.lifecycle_latency"

#: The lifecycle events that terminate a request (for latency/throughput metrics).
_TERMINAL_TRANSITIONS: dict[RequestStatus, str] = {
    RequestStatus.COMPLETED: METRIC_COMPLETED,
    RequestStatus.FAILED: METRIC_FAILED,
    RequestStatus.CANCELLED: METRIC_CANCELLED,
}


@dataclass(frozen=True, slots=True)
class RequestAccess:
    """An immutable, content-addressed generation-request access decision (fail-closed).

    Composes identity authorization, tenant/workspace isolation, and (for mutating
    actions) owner/administrator scoping into a single verdict for one
    ``(principal, request, action)`` request.
    """

    request_id: str
    principal_id: str
    action: RequestAction
    permission: Permission
    granted: bool
    reason: str
    is_owner: bool
    decision: AccessDecision
    access_id: str = ""

    @classmethod
    def create(
        cls,
        *,
        request_id: str,
        action: RequestAction,
        permission: Permission,
        granted: bool,
        reason: str,
        decision: AccessDecision,
        is_owner: bool = False,
    ) -> RequestAccess:
        principal_id = decision.request.principal_id
        core = {
            "request_id": request_id,
            "principal_id": principal_id,
            "action": action.value,
            "permission": permission.value,
            "granted": granted,
            "reason": reason,
            "is_owner": is_owner,
        }
        return cls(
            request_id=request_id,
            principal_id=principal_id,
            action=action,
            permission=permission,
            granted=granted,
            reason=reason,
            is_owner=is_owner,
            decision=decision,
            access_id=f"UCOS-GACC-{content_hash(core)[:16]}",
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "access_id": self.access_id,
            "request_id": self.request_id,
            "principal_id": self.principal_id,
            "action": self.action.value,
            "permission": self.permission.value,
            "granted": self.granted,
            "reason": self.reason,
            "is_owner": self.is_owner,
            "decision": self.decision.to_dict(),
        }


@dataclass(frozen=True, slots=True)
class RequestEvidence:
    """A deterministic, content-addressed record of request runtime state (evidence)."""

    registry_fingerprint: str
    dispatch_fingerprint: str
    provenance_fingerprint: str
    request_count: int
    dispatched_count: int
    provenance_count: int
    terminal_count: int
    access_evaluation_count: int
    status_census: tuple[tuple[str, int], ...]
    health_status: str
    evidence_id: str = ""

    @classmethod
    def create(
        cls,
        *,
        registry_fingerprint: str,
        dispatch_fingerprint: str,
        provenance_fingerprint: str,
        request_count: int,
        dispatched_count: int,
        provenance_count: int,
        terminal_count: int,
        access_evaluation_count: int,
        status_census: tuple[tuple[str, int], ...],
        health_status: str,
    ) -> RequestEvidence:
        core = {
            "registry_fingerprint": registry_fingerprint,
            "dispatch_fingerprint": dispatch_fingerprint,
            "provenance_fingerprint": provenance_fingerprint,
            "request_count": request_count,
            "dispatched_count": dispatched_count,
            "provenance_count": provenance_count,
            "terminal_count": terminal_count,
            "access_evaluation_count": access_evaluation_count,
            "status_census": [list(pair) for pair in status_census],
            "health_status": health_status,
        }
        return cls(
            registry_fingerprint=registry_fingerprint,
            dispatch_fingerprint=dispatch_fingerprint,
            provenance_fingerprint=provenance_fingerprint,
            request_count=request_count,
            dispatched_count=dispatched_count,
            provenance_count=provenance_count,
            terminal_count=terminal_count,
            access_evaluation_count=access_evaluation_count,
            status_census=status_census,
            health_status=health_status,
            evidence_id=f"UCOS-GEVT-{content_hash(core)[:16]}",
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "evidence_id": self.evidence_id,
            "registry_fingerprint": self.registry_fingerprint,
            "dispatch_fingerprint": self.dispatch_fingerprint,
            "provenance_fingerprint": self.provenance_fingerprint,
            "request_count": self.request_count,
            "dispatched_count": self.dispatched_count,
            "provenance_count": self.provenance_count,
            "terminal_count": self.terminal_count,
            "access_evaluation_count": self.access_evaluation_count,
            "status_census": {name: count for name, count in self.status_census},
            "health_status": self.health_status,
        }

    def fingerprint(self) -> str:
        return content_hash(self.to_dict())


class GenerationRequestService:
    """The governed L3 composition point for the UCOS Generation Request Runtime."""

    __slots__ = (
        "_registry",
        "_dispatch",
        "_provenance",
        "_authorization",
        "_workspaces",
        "_search",
        "_health",
        "_health_registry",
        "_observability",
        "_events",
        "_access_evaluations",
        "_last_health_status",
    )

    def __init__(
        self,
        *,
        registry: GenerationRequestRegistry,
        dispatch: DispatchLedger,
        provenance: ProvenanceLedger,
        authorization: AuthorizationService,
        workspaces: WorkspaceRegistry,
        search: RequestSearch,
        health: RequestHealth,
        health_registry: HealthRegistry,
        observability: ObservabilityService | None = None,
        events: EventBus | None = None,
    ) -> None:
        if not isinstance(registry, GenerationRequestRegistry):
            raise RequestServiceError("a valid GenerationRequestRegistry is required")
        if not isinstance(dispatch, DispatchLedger):
            raise RequestServiceError("a valid DispatchLedger is required")
        if not isinstance(provenance, ProvenanceLedger):
            raise RequestServiceError("a valid ProvenanceLedger is required")
        if not isinstance(authorization, AuthorizationService):
            raise RequestServiceError("a valid AuthorizationService is required")
        if not isinstance(workspaces, WorkspaceRegistry):
            raise RequestServiceError("a valid WorkspaceRegistry is required")
        if not isinstance(search, RequestSearch):
            raise RequestServiceError("a valid RequestSearch is required")
        if not isinstance(health, RequestHealth):
            raise RequestServiceError("a valid RequestHealth is required")
        if not isinstance(health_registry, HealthRegistry):
            raise RequestServiceError("a valid HealthRegistry is required")
        if observability is not None and not isinstance(observability, ObservabilityService):
            raise RequestServiceError("observability must be an ObservabilityService when provided")
        if events is not None and not isinstance(events, EventBus):
            raise RequestServiceError("events must be an EventBus when provided")
        self._registry = registry
        self._dispatch = dispatch
        self._provenance = provenance
        self._authorization = authorization
        self._workspaces = workspaces
        self._search = search
        self._health = health
        self._health_registry = health_registry
        self._observability = observability
        self._events = events
        self._access_evaluations = 0
        self._last_health_status = self._current_health_status()

    # -- component access -------------------------------------------------------

    @property
    def registry(self) -> GenerationRequestRegistry:
        return self._registry

    @property
    def dispatch(self) -> DispatchLedger:
        return self._dispatch

    @property
    def provenance(self) -> ProvenanceLedger:
        return self._provenance

    @property
    def authorization(self) -> AuthorizationService:
        return self._authorization

    @property
    def workspaces(self) -> WorkspaceRegistry:
        return self._workspaces

    @property
    def health(self) -> RequestHealth:
        return self._health

    @property
    def observability(self) -> ObservabilityService | None:
        return self._observability

    @property
    def access_evaluation_count(self) -> int:
        return self._access_evaluations

    # -- submission (create request) -------------------------------------------

    def submit_request(
        self,
        session_id: str,
        slug: str,
        blueprint_ref: str,
        workspace_id: str,
        family: BlueprintFamily,
        *,
        now: int,
        project_id: str | None = None,
        metadata: RequestMetadata | None = None,
    ) -> GenerationRequest:
        """Submit (create) a generation request scoped to a workspace; record the owner.

        The canonical governed entry point for generation activity. Requires identity
        CREATE on ``generation-requests`` (with the parent workspace's tenant), an ACTIVE
        parent workspace, and cross-tenant isolation clearance. Raises
        :class:`RequestAccessError` on any denial. The request enters in SUBMITTED.
        """
        workspace = self._workspaces.get(workspace_id)
        if not workspace.is_active:
            raise RequestAccessError(
                "parent workspace is not active",
                reason=f"workspace-{workspace.status.value}",
                workspace_id=workspace_id,
            )
        decision = self._authorization.authorize(
            session_id,
            GENERATION_REQUEST_GROUP,
            Permission.CREATE,
            now=now,
            tenant=workspace.tenant,
            resource=slug,
        )
        if not decision.permitted:
            raise RequestAccessError(
                "generation request submission denied", reason=decision.reason, slug=slug
            )
        principal = self._authorization.principals.get(decision.request.principal_id)
        if tenants_isolated(principal.tenant, workspace.tenant):
            raise RequestAccessError(
                "cross-tenant generation request submission denied",
                reason="tenant-isolation-violation",
                slug=slug,
            )
        request = self._registry.create(
            slug,
            blueprint_ref,
            workspace_id,
            principal.subject,
            family,
            submitted_tick=now,
            project_id=project_id,
            tenant=workspace.tenant,
            metadata=metadata,
        )
        self._emit(
            REQUEST_SUBMITTED_EVENT,
            subject=request.request_id,
            payload={
                "slug": request.slug,
                "blueprint_ref": blueprint_ref,
                "workspace_id": workspace_id,
                "project_id": project_id,
                "family": family.value,
                "tenant": request.tenant,
            },
        )
        self._metric_counter(METRIC_SUBMITTED, family=family.value)
        return request

    # -- lifecycle transitions --------------------------------------------------

    def start_validation(self, session_id: str, request_id: str, *, now: int) -> GenerationRequest:
        """SUBMITTED → VALIDATING (governance/structural pre-checks). Requires VALIDATE."""
        return self._transition(
            session_id,
            request_id,
            RequestAction.VALIDATE,
            RequestStatus.VALIDATING,
            REQUEST_VALIDATING_EVENT,
            now=now,
        )

    def approve(self, session_id: str, request_id: str, *, now: int) -> GenerationRequest:
        """VALIDATING → APPROVED (admitted for execution). Requires APPROVE."""
        return self._transition(
            session_id,
            request_id,
            RequestAction.APPROVE,
            RequestStatus.APPROVED,
            REQUEST_APPROVED_EVENT,
            now=now,
        )

    def enqueue(self, session_id: str, request_id: str, *, now: int) -> GenerationRequest:
        """APPROVED → QUEUED (awaiting dispatch). Requires QUEUE."""
        updated = self._transition(
            session_id,
            request_id,
            RequestAction.QUEUE,
            RequestStatus.QUEUED,
            REQUEST_QUEUED_EVENT,
            now=now,
        )
        self._update_queue_depth()
        return updated

    def mark_running(self, session_id: str, request_id: str, *, now: int) -> GenerationRequest:
        """DISPATCHED → RUNNING (execution began on the runtime). Requires RUN."""
        return self._transition(
            session_id,
            request_id,
            RequestAction.RUN,
            RequestStatus.RUNNING,
            REQUEST_RUNNING_EVENT,
            now=now,
        )

    def complete(self, session_id: str, request_id: str, *, now: int) -> GenerationRequest:
        """RUNNING → COMPLETED (execution succeeded). Requires COMPLETE."""
        return self._transition(
            session_id,
            request_id,
            RequestAction.COMPLETE,
            RequestStatus.COMPLETED,
            REQUEST_COMPLETED_EVENT,
            now=now,
        )

    def fail(self, session_id: str, request_id: str, *, now: int) -> GenerationRequest:
        """→ FAILED (execution or validation error). Requires FAIL."""
        return self._transition(
            session_id,
            request_id,
            RequestAction.FAIL,
            RequestStatus.FAILED,
            REQUEST_FAILED_EVENT,
            now=now,
        )

    def cancel_request(self, session_id: str, request_id: str, *, now: int) -> GenerationRequest:
        """→ CANCELLED (withdrawn by owner/administrator). Requires CANCEL."""
        updated = self._transition(
            session_id,
            request_id,
            RequestAction.CANCEL,
            RequestStatus.CANCELLED,
            REQUEST_CANCELLED_EVENT,
            now=now,
        )
        self._update_queue_depth()
        return updated

    # -- dispatch integration (the governed execution boundary, §7) -------------

    def dispatch_request(
        self,
        session_id: str,
        request_id: str,
        *,
        now: int,
        content_hash: str,
        execution_target: str = DEFAULT_EXECUTION_TARGET,
        parameters: dict[str, str] | None = None,
    ) -> DispatchRecord:
        """Hand a QUEUED request off to the EC-1 Execution Runtime (the authoritative boundary).

        Composes: **dispatch authorization** (EXECUTE on ``generation-requests`` + owner/
        admin scoping), **dispatch preparation** (a content-addressed
        :class:`DispatchRecord` bound to the certified engine contracts by reference),
        **dispatch validation** (the request must be QUEUED; the target must be a
        certified EC-1 execution contract), **dispatch tracking** (recorded in the
        append-only :class:`DispatchLedger`, transition QUEUED → DISPATCHED), and
        **dispatch auditing** (governed ``generation.request.dispatched`` event with the
        handoff edge). A request reaches the runtime **only** through this method.
        """
        access = self._require_access(session_id, request_id, RequestAction.DISPATCH, now=now)
        request = self._registry.get(request_id)
        if request.status is not RequestStatus.QUEUED:
            raise RequestDispatchError(
                "only a QUEUED request may be dispatched",
                request_id=request_id,
                status=request.status.value,
            )
        record = DispatchRecord.create(
            request_ref=request_id,
            blueprint_ref=request.blueprint_ref,
            family=request.family,
            content_hash=content_hash,
            tick=now,
            execution_target=execution_target,
            parameters=parameters,
        )
        self._dispatch.record(record)
        self._registry.transition(request_id, RequestStatus.DISPATCHED, tick=now)
        self._emit(
            REQUEST_DISPATCHED_EVENT,
            subject=request_id,
            payload=record.handoff_edge(),
        )
        self._metric_counter(METRIC_DISPATCHED, family=request.family.value)
        self._update_queue_depth()
        self._emit_health_change()
        # bind is_owner into the access log (already emitted in evaluate_access)
        _ = access
        return record

    # -- provenance (link-4 continuation) ---------------------------------------

    def record_provenance(
        self, session_id: str, request_id: str, provenance: RequestProvenance, *, now: int
    ) -> RequestProvenance:
        """Record the request's link-4 provenance edge (requires owner; fail-closed).

        Materializes the ``Generation → Blueprint → Request → Implementation`` trace
        continuation. Requires a mutating grant (VALIDATE) + owner/admin scoping, and is
        permitted at any lifecycle state (completion/failure evidence is recorded post
        hoc). The provenance ``request_ref`` must match the request.
        """
        self._require_access(
            session_id, request_id, RequestAction.VALIDATE, now=now, allow_terminal=True
        )
        if not isinstance(provenance, RequestProvenance):
            raise RequestServiceError("record_provenance requires a RequestProvenance")
        if provenance.request_ref != request_id:
            raise RequestServiceError(
                "provenance request_ref does not match the request",
                extra={"request_ref": provenance.request_ref, "request_id": request_id},
            )
        recorded = self._provenance.record(provenance)
        self._emit(
            REQUEST_PROVENANCE_LINKED_EVENT,
            subject=request_id,
            payload=recorded.trace_edge(),
        )
        return recorded

    # -- resolution / retrieval / discovery -------------------------------------

    def get_request(self, request_id: str) -> GenerationRequest:
        """Retrieve a request by id (pure read; fail-closed on absent)."""
        return self._registry.get(request_id)

    def list_requests(
        self,
        session_id: str,
        *,
        now: int,
        tenant: str | None = None,
        workspace_id: str | None = None,
        project_id: str | None = None,
        family: BlueprintFamily | None = None,
        status: RequestStatus | None = None,
    ) -> tuple[GenerationRequest, ...]:
        """List/filter the requests a caller may see (authorized READ + isolation)."""
        principal = self._resolve_principal(session_id, now)
        if principal is None:
            return ()
        decision = self._authorization.authorize_principal(
            principal, GENERATION_REQUEST_GROUP, Permission.READ, tenant=tenant
        )
        if not decision.permitted:
            return ()
        return tuple(
            request
            for request in self._registry.discover(
                workspace_id=workspace_id,
                project_id=project_id,
                tenant=tenant,
                family=family,
                status=status,
            )
            if not tenants_isolated(principal.tenant, request.tenant)
        )

    # -- selection / context ----------------------------------------------------

    def select_request(self, session_id: str, request_id: str, *, now: int) -> RequestContext:
        """Select a request and return its runtime context (fail-closed).

        Requires INSPECT (READ) access (identity + isolation). Raises
        :class:`RequestAccessError` when access is denied.
        """
        access = self.evaluate_access(session_id, request_id, RequestAction.INSPECT, now=now)
        if not access.granted:
            raise RequestAccessError(
                "generation request selection denied",
                reason=access.reason,
                request_id=request_id,
            )
        request = self._registry.get(request_id)
        principal = self._authorization.principals.get(access.principal_id)
        return RequestContext.create(request, principal, is_owner=access.is_owner)

    # -- status tracking --------------------------------------------------------

    def status_of(self, request_id: str) -> DerivedRequestStatus:
        """Derive a deterministic status for a request (pure read; fail-closed)."""
        request = self._registry.get(request_id)
        return derive_status(
            request,
            has_dispatch=self._dispatch.has(request_id),
            has_provenance=self._provenance.has(request_id),
        )

    def track_request(self, session_id: str, request_id: str, *, now: int) -> DerivedRequestStatus:
        """Track a request's derived status (requires TRACK/READ access; fail-closed)."""
        access = self.evaluate_access(session_id, request_id, RequestAction.TRACK, now=now)
        if not access.granted:
            raise RequestAccessError(
                "generation request tracking denied",
                reason=access.reason,
                request_id=request_id,
            )
        return self.status_of(request_id)

    # -- traceability (link-4 evidence) -----------------------------------------

    def trace(self, session_id: str, request_id: str, *, now: int) -> dict[str, Any]:
        """Return the link-4 trace edge for a request (requires TRACE; fail-closed)."""
        access = self.evaluate_access(session_id, request_id, RequestAction.TRACE, now=now)
        if not access.granted:
            raise RequestAccessError(
                "generation request trace denied",
                reason=access.reason,
                request_id=request_id,
            )
        return self._provenance.trace(request_id)

    # -- metadata ---------------------------------------------------------------

    def update_metadata(
        self, session_id: str, request_id: str, metadata: RequestMetadata, *, now: int
    ) -> GenerationRequest:
        """Replace a request's metadata immutably (requires owner; SUBMIT authority)."""
        self._require_access(session_id, request_id, RequestAction.SUBMIT, now=now)
        if not isinstance(metadata, RequestMetadata):
            raise RequestServiceError("update_metadata requires a RequestMetadata")
        updated = self._registry.update_metadata(request_id, metadata)
        self._emit(
            REQUEST_METADATA_UPDATED_EVENT,
            subject=request_id,
            payload={"metadata_fingerprint": metadata.fingerprint()},
        )
        return updated

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
        family: BlueprintFamily | None = None,
        status: RequestStatus | None = None,
    ) -> RequestSearchResponse:
        """Run an authorization- and isolation-scoped generation-request search."""
        return self._search.search(
            session_id,
            query,
            now=now,
            tenant=tenant,
            workspace_id=workspace_id,
            project_id=project_id,
            family=family,
            status=status,
        )

    # -- access evaluation ------------------------------------------------------

    def evaluate_access(
        self,
        session_id: str,
        request_id: str,
        action: RequestAction,
        *,
        now: int,
        allow_terminal: bool = False,
    ) -> RequestAccess:
        """Evaluate composed request access (identity ∧ isolation ∧ owner-scoping).

        Denials are returned as data (``granted == False``); a malformed request or an
        unknown request raises. Every evaluation is emitted as a governed
        ``generation.request.access.evaluated`` event (PC-16). ``allow_terminal`` relaxes
        the terminal-state block for evidence-recording actions (e.g. provenance), which
        are legitimately recorded after a request reaches a terminal state.
        """
        if not isinstance(action, RequestAction):
            raise RequestServiceError("action must be a RequestAction")
        permission = permission_for(action)
        request = self._registry.get(request_id)
        decision = self._authorization.authorize(
            session_id,
            GENERATION_REQUEST_GROUP,
            permission,
            now=now,
            tenant=request.tenant,
            resource=request_id,
        )
        access = self._compose_access(
            request, action, permission, decision, allow_terminal=allow_terminal
        )
        self._access_evaluations += 1
        self._emit(
            REQUEST_ACCESS_EVENT,
            subject=access.principal_id,
            payload={
                "request_id": request_id,
                "action": action.value,
                "granted": access.granted,
                "reason": access.reason,
            },
        )
        return access

    def _compose_access(
        self,
        request: GenerationRequest,
        action: RequestAction,
        permission: Permission,
        decision: AccessDecision,
        *,
        allow_terminal: bool = False,
    ) -> RequestAccess:
        if not decision.permitted:
            return RequestAccess.create(
                request_id=request.request_id,
                action=action,
                permission=permission,
                granted=False,
                reason=decision.reason,
                decision=decision,
            )
        principal = self._authorization.principals.get(decision.request.principal_id)
        if tenants_isolated(principal.tenant, request.tenant):
            return RequestAccess.create(
                request_id=request.request_id,
                action=action,
                permission=permission,
                granted=False,
                reason="tenant-isolation-violation",
                decision=decision,
            )
        is_owner = principal.subject == request.owner_subject
        if action in MUTATING_ACTIONS:
            if request.is_terminal and not allow_terminal:
                return RequestAccess.create(
                    request_id=request.request_id,
                    action=action,
                    permission=permission,
                    granted=False,
                    reason="request-terminal",
                    decision=decision,
                    is_owner=is_owner,
                )
            is_admin = self._authorization.permissions.has_permission(
                principal, GENERATION_REQUEST_GROUP, Permission.ADMINISTER
            )
            if not (is_owner or is_admin):
                return RequestAccess.create(
                    request_id=request.request_id,
                    action=action,
                    permission=permission,
                    granted=False,
                    reason="not-an-owner",
                    decision=decision,
                    is_owner=is_owner,
                )
        return RequestAccess.create(
            request_id=request.request_id,
            action=action,
            permission=permission,
            granted=True,
            reason="granted",
            decision=decision,
            is_owner=is_owner,
        )

    # -- health integration -----------------------------------------------------

    def health_report(self) -> dict[str, Any]:
        """The generation-request runtime health endpoint (reuses the observability model)."""
        return self._health_registry.endpoint(self._health.probe())

    # -- evidence ---------------------------------------------------------------

    def evidence(self) -> RequestEvidence:
        """Produce deterministic Request Evidence over the runtime state."""
        report = self._health_registry.report(self._health.probe())
        requests = self._registry.all()
        dispatched = sum(1 for r in requests if r.is_dispatched)
        terminal = sum(1 for r in requests if r.is_terminal)
        census = tuple(sorted(self._registry.count_by_status().items()))
        return RequestEvidence.create(
            registry_fingerprint=self._registry.fingerprint(),
            dispatch_fingerprint=self._dispatch.fingerprint(),
            provenance_fingerprint=self._provenance.fingerprint(),
            request_count=len(self._registry),
            dispatched_count=dispatched,
            provenance_count=len(self._provenance),
            terminal_count=terminal,
            access_evaluation_count=self._access_evaluations,
            status_census=census,
            health_status=report.status.value,
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "request_count": len(self._registry),
            "dispatch_count": len(self._dispatch),
            "provenance_count": len(self._provenance),
            "access_evaluation_count": self._access_evaluations,
            "observability_bound": self._observability is not None,
            "evidence": self.evidence().to_dict(),
        }

    # -- internals --------------------------------------------------------------

    def _transition(
        self,
        session_id: str,
        request_id: str,
        action: RequestAction,
        target: RequestStatus,
        event_type: str,
        *,
        now: int,
    ) -> GenerationRequest:
        """Authorize + apply a governed lifecycle transition and emit its event."""
        self._require_access(session_id, request_id, action, now=now)
        previous = self._registry.get(request_id)
        updated = self._registry.transition(request_id, target, tick=now)
        self._emit(
            event_type,
            subject=request_id,
            payload={"from": previous.status.value, "to": target.value},
        )
        if target in _TERMINAL_TRANSITIONS:
            self._metric_counter(_TERMINAL_TRANSITIONS[target], family=updated.family.value)
            self._metric_latency(updated, now)
            self._emit_health_change()
        return updated

    def _require_access(
        self,
        session_id: str,
        request_id: str,
        action: RequestAction,
        *,
        now: int,
        allow_terminal: bool = False,
    ) -> RequestAccess:
        access = self.evaluate_access(
            session_id, request_id, action, now=now, allow_terminal=allow_terminal
        )
        if not access.granted:
            raise RequestAccessError(
                "generation request action denied",
                reason=access.reason,
                request_id=request_id,
                action=action.value,
            )
        return access

    def _resolve_principal(self, session_id: str, now: int):
        try:
            session = self._authorization.sessions.validate(session_id, now)
            return self._authorization.principals.get(session.principal_id)
        except IdentityError:
            return None

    def _current_health_status(self) -> str:
        return self._health_registry.report(self._health.probe()).status.value

    def _emit_health_change(self) -> None:
        status = self._current_health_status()
        if status != self._last_health_status:
            self._last_health_status = status
            self._emit(
                REQUEST_HEALTH_CHANGED_EVENT,
                subject=_RUNTIME_SUBJECT,
                payload={"status": status},
            )

    def _emit(self, event_type: str, *, subject: str, payload: dict[str, Any]) -> None:
        if self._events is not None:
            self._events.publish(
                event_type,
                source="platform.generation.runtime",
                subject=subject,
                payload=payload,
            )

    # -- observability metrics (PC-12; reproducible, no wall-clock) -------------

    def _metric_counter(self, name: str, **labels: str) -> None:
        if self._observability is not None:
            self._observability.metrics.counter(name, 1.0, **labels)

    def _metric_latency(self, request: GenerationRequest, now: int) -> None:
        if self._observability is not None:
            latency = max(0, now - request.submitted_tick)
            self._observability.metrics.histogram(
                METRIC_LIFECYCLE_LATENCY, float(latency), status=request.status.value
            )

    def _update_queue_depth(self) -> None:
        if self._observability is not None:
            depth = self._registry.count_by_status().get(RequestStatus.QUEUED.value, 0)
            self._observability.metrics.gauge(METRIC_QUEUE_DEPTH, float(depth))


def build_generation_request_service(
    *,
    authorization: AuthorizationService,
    workspaces: WorkspaceRegistry,
    observability: ObservabilityService | None = None,
    events: EventBus | None = None,
    registry: GenerationRequestRegistry | None = None,
    dispatch: DispatchLedger | None = None,
    provenance: ProvenanceLedger | None = None,
) -> GenerationRequestService:
    """Default, registry-driven composition of the Generation Request Runtime.

    Wires the request registry, dispatch + provenance ledgers, request search (over the
    supplied Identity ``authorization`` service), the request health probe and a health
    registry seeded with the request health checks, the reused workspace registry
    (parent-scope binding + isolation), and — when supplied — the observability layer and
    event bus.
    """
    if not isinstance(authorization, AuthorizationService):
        raise RequestServiceError(
            "build_generation_request_service requires an AuthorizationService"
        )
    if not isinstance(workspaces, WorkspaceRegistry):
        raise RequestServiceError("build_generation_request_service requires a WorkspaceRegistry")
    request_registry = registry if registry is not None else GenerationRequestRegistry()
    dispatch_ledger = dispatch if dispatch is not None else DispatchLedger()
    provenance_ledger = provenance if provenance is not None else ProvenanceLedger()
    search = RequestSearch(request_registry, authorization)
    health = RequestHealth(request_registry, dispatch_ledger)
    health_registry = HealthRegistry()
    for check in generation_request_health_checks():
        health_registry.register(check)
    return GenerationRequestService(
        registry=request_registry,
        dispatch=dispatch_ledger,
        provenance=provenance_ledger,
        authorization=authorization,
        workspaces=workspaces,
        search=search,
        health=health,
        health_registry=health_registry,
        observability=observability,
        events=events,
    )


__all__ = [
    "REQUEST_SUBMITTED_EVENT",
    "REQUEST_VALIDATING_EVENT",
    "REQUEST_APPROVED_EVENT",
    "REQUEST_QUEUED_EVENT",
    "REQUEST_DISPATCHED_EVENT",
    "REQUEST_RUNNING_EVENT",
    "REQUEST_COMPLETED_EVENT",
    "REQUEST_FAILED_EVENT",
    "REQUEST_CANCELLED_EVENT",
    "REQUEST_METADATA_UPDATED_EVENT",
    "REQUEST_PROVENANCE_LINKED_EVENT",
    "REQUEST_HEALTH_CHANGED_EVENT",
    "REQUEST_ACCESS_EVENT",
    "METRIC_SUBMITTED",
    "METRIC_DISPATCHED",
    "METRIC_COMPLETED",
    "METRIC_FAILED",
    "METRIC_CANCELLED",
    "METRIC_QUEUE_DEPTH",
    "METRIC_LIFECYCLE_LATENCY",
    "RequestAccess",
    "RequestEvidence",
    "GenerationRequestService",
    "build_generation_request_service",
]
