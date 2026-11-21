"""EC2-TASK-000133 — Artifact Explorer Service (EC2-EPIC-009).

The single, governed **artifact-explorer runtime composition point** (L3 Application of
the Program architecture) that composes the whole Artifact Explorer Runtime into one
entry point — the governed, **read-only** navigation surface for Program Surface #10
Artifact Explorer (PC-08 artifact discovery + PC-13 search + PC-16 audit):

    GenerationRequestRegistry · DispatchLedger · ProvenanceLedger (all consumed by
    reference) · ArtifactSearch · ExplorerHealth · (reused) AuthorizationService ·
    ObservabilityService

It is a strictly **additive**, **read/navigation-only** layer: it authorizes only through
the certified Identity Layer (L7) on the existing ``artifact-explorer`` capability group
— **no duplicate authorization or identity logic, no new authority, no new capability
group** — surfaces the EC2-EPIC-007 artifact/dispatch/provenance references **by
reference** (never re-deriving, never mutating), observes only through the Observability
Layer (L8), and exposes **no artifact generation, no artifact mutation, and no engine
execution** path. It re-implements none of them, modifies neither EC-1 nor any prior
layer, and writes nothing to the certified corpus (DP-03).

Every access is fail-closed and composes gates — **identity authorization** (RBAC §3.2,
READ) and **tenant/workspace isolation** (the reused rule, P3) — so cross-tenant access is
refused in 100% of cases. Owner and administrator standings are recognized and recorded.
Because every governed navigation is published onto the Foundation event bus, it is
captured as append-only audit (PC-16 / OP-C3).

The service is deterministic: the same identity registrations, the same consumed records,
and the same ordered sequence of calls yield the same
:class:`~platform.artifact_explorer.evidence.ExplorerEvidence` fingerprint (P5).
:func:`build_artifact_explorer_service` provides the default wiring;
:func:`~platform.artifact_explorer.bootstrap.bootstrap_artifact_explorer` composes it
onto a :class:`~platform.foundation.bootstrap.PlatformContext`.
"""

from __future__ import annotations

from dataclasses import dataclass
from platform.artifact_explorer.context import ArtifactContext
from platform.artifact_explorer.contracts import (
    ARTIFACT_EXPLORER_GROUP,
    ExplorerAction,
    permission_for,
)
from platform.artifact_explorer.errors import (
    ArtifactAccessError,
    ArtifactProvenanceError,
    ArtifactServiceError,
)
from platform.artifact_explorer.evidence import ExplorerEvidence
from platform.artifact_explorer.health import (
    ExplorerHealth,
    artifact_explorer_health_checks,
)
from platform.artifact_explorer.lineage import (
    ArtifactLineage,
    ArtifactProvenance,
    ArtifactTrace,
)
from platform.artifact_explorer.references import (
    ArtifactReference,
    ArtifactSummary,
    ArtifactView,
)
from platform.artifact_explorer.search import ArtifactSearch, ArtifactSearchResponse
from platform.blueprints.contracts import BlueprintFamily
from platform.foundation.contracts import content_hash
from platform.foundation.events import EventBus
from platform.foundation.identity import Permission
from platform.generation.contracts import GenerationRequest, RequestStatus
from platform.generation.dispatch import DispatchLedger, DispatchRecord
from platform.generation.provenance import ProvenanceLedger, RequestProvenance
from platform.generation.registry import GenerationRequestRegistry
from platform.generation.status import DerivedRequestStatus, derive_status
from platform.identity.contracts import AccessDecision
from platform.identity.errors import IdentityError
from platform.identity.service import AuthorizationService
from platform.observability.health import HealthRegistry
from platform.observability.service import ObservabilityService
from platform.workspace.isolation import tenants_isolated
from typing import Any

#: Governed events published onto the Foundation event bus (observed as append-only PC-16).
ARTIFACT_VIEWED_EVENT = "artifact.explorer.artifact.viewed"
ARTIFACT_DISCOVERED_EVENT = "artifact.explorer.artifacts.discovered"
ARTIFACT_LINEAGE_NAVIGATED_EVENT = "artifact.explorer.lineage.navigated"
ARTIFACT_PROVENANCE_NAVIGATED_EVENT = "artifact.explorer.provenance.navigated"
ARTIFACT_TRACE_NAVIGATED_EVENT = "artifact.explorer.trace.navigated"
ARTIFACT_SEARCHED_EVENT = "artifact.explorer.searched"
ARTIFACT_NAVIGATED_EVENT = "artifact.explorer.request.navigated"
ARTIFACT_HEALTH_CHANGED_EVENT = "artifact.explorer.health.changed"
ARTIFACT_ACCESS_EVENT = "artifact.explorer.access.evaluated"

#: The stable subject used for runtime-scoped (non-artifact) governed events.
_RUNTIME_SUBJECT = "platform.artifact_explorer.runtime"

# --------------------------------------------------------------------------- #
# Observability metric names (PC-12 monitoring; reproducible, no wall-clock).  #
# --------------------------------------------------------------------------- #
METRIC_LOOKUPS = "artifact.explorer.lookups"
METRIC_DISCOVERIES = "artifact.explorer.discoveries"
METRIC_SEARCHES = "artifact.explorer.searches"
METRIC_LINEAGE = "artifact.explorer.lineage_navigations"
METRIC_PROVENANCE = "artifact.explorer.provenance_navigations"
METRIC_TRACE = "artifact.explorer.trace_navigations"


@dataclass(frozen=True, slots=True)
class ArtifactAccess:
    """An immutable, content-addressed artifact-explorer access decision (fail-closed).

    Composes identity authorization (READ) and tenant/workspace isolation into a single
    verdict for one ``(principal, artifact, action)`` request. The explorer is read-only,
    so there is no owner/mutation gate; ``is_owner`` and ``is_administrator`` are carried
    for context (tenant / owner / administrator access standings).
    """

    request_ref: str
    principal_id: str
    action: ExplorerAction
    permission: Permission
    granted: bool
    reason: str
    is_owner: bool
    is_administrator: bool
    decision: AccessDecision
    access_id: str = ""

    @classmethod
    def create(
        cls,
        *,
        request_ref: str,
        action: ExplorerAction,
        permission: Permission,
        granted: bool,
        reason: str,
        decision: AccessDecision,
        is_owner: bool = False,
        is_administrator: bool = False,
    ) -> ArtifactAccess:
        principal_id = decision.request.principal_id
        core = {
            "request_ref": request_ref,
            "principal_id": principal_id,
            "action": action.value,
            "permission": permission.value,
            "granted": granted,
            "reason": reason,
            "is_owner": is_owner,
            "is_administrator": is_administrator,
        }
        return cls(
            request_ref=request_ref,
            principal_id=principal_id,
            action=action,
            permission=permission,
            granted=granted,
            reason=reason,
            is_owner=is_owner,
            is_administrator=is_administrator,
            decision=decision,
            access_id=f"UCOS-AXAC-{content_hash(core)[:16]}",
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "access_id": self.access_id,
            "request_ref": self.request_ref,
            "principal_id": self.principal_id,
            "action": self.action.value,
            "permission": self.permission.value,
            "granted": self.granted,
            "reason": self.reason,
            "is_owner": self.is_owner,
            "is_administrator": self.is_administrator,
            "decision": self.decision.to_dict(),
        }


class ArtifactExplorerService:
    """The governed L3 composition point for the UCOS Artifact Explorer Runtime (read-only)."""

    __slots__ = (
        "_registry",
        "_dispatch",
        "_provenance",
        "_authorization",
        "_search",
        "_health",
        "_health_registry",
        "_observability",
        "_events",
        "_access_evaluations",
        "_lookups",
        "_searches",
        "_lineage_navigations",
        "_provenance_navigations",
        "_trace_navigations",
        "_last_health_status",
    )

    def __init__(
        self,
        *,
        registry: GenerationRequestRegistry,
        dispatch: DispatchLedger,
        provenance: ProvenanceLedger,
        authorization: AuthorizationService,
        search: ArtifactSearch,
        health: ExplorerHealth,
        health_registry: HealthRegistry,
        observability: ObservabilityService | None = None,
        events: EventBus | None = None,
    ) -> None:
        if not isinstance(registry, GenerationRequestRegistry):
            raise ArtifactServiceError("a valid GenerationRequestRegistry is required")
        if not isinstance(dispatch, DispatchLedger):
            raise ArtifactServiceError("a valid DispatchLedger is required")
        if not isinstance(provenance, ProvenanceLedger):
            raise ArtifactServiceError("a valid ProvenanceLedger is required")
        if not isinstance(authorization, AuthorizationService):
            raise ArtifactServiceError("a valid AuthorizationService is required")
        if not isinstance(search, ArtifactSearch):
            raise ArtifactServiceError("a valid ArtifactSearch is required")
        if not isinstance(health, ExplorerHealth):
            raise ArtifactServiceError("a valid ExplorerHealth is required")
        if not isinstance(health_registry, HealthRegistry):
            raise ArtifactServiceError("a valid HealthRegistry is required")
        if observability is not None and not isinstance(observability, ObservabilityService):
            raise ArtifactServiceError(
                "observability must be an ObservabilityService when provided"
            )
        if events is not None and not isinstance(events, EventBus):
            raise ArtifactServiceError("events must be an EventBus when provided")
        self._registry = registry
        self._dispatch = dispatch
        self._provenance = provenance
        self._authorization = authorization
        self._search = search
        self._health = health
        self._health_registry = health_registry
        self._observability = observability
        self._events = events
        self._access_evaluations = 0
        self._lookups = 0
        self._searches = 0
        self._lineage_navigations = 0
        self._provenance_navigations = 0
        self._trace_navigations = 0
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
    def health(self) -> ExplorerHealth:
        return self._health

    @property
    def observability(self) -> ObservabilityService | None:
        return self._observability

    @property
    def access_evaluation_count(self) -> int:
        return self._access_evaluations

    # -- pure reads (no authorization; substrate projections) -------------------

    def reference_of(self, request_ref: str) -> ArtifactReference:
        """Project the artifact reference for a request (pure read; fail-closed on absent)."""
        request = self._registry.get(request_ref)
        return ArtifactReference.create(
            request,
            dispatch=self._dispatch_of(request_ref),
            provenance=self._provenance_of(request_ref),
        )

    def summary_of(self, request_ref: str) -> ArtifactSummary:
        """Project the artifact summary for a request (pure read; fail-closed on absent)."""
        request = self._registry.get(request_ref)
        return ArtifactSummary.from_request(
            request,
            has_dispatch=self._dispatch.has(request_ref),
            has_provenance=self._provenance.has(request_ref),
        )

    def view_of(self, request_ref: str) -> ArtifactView:
        """Project the full artifact view for a request (pure read; fail-closed on absent)."""
        request = self._registry.get(request_ref)
        return ArtifactView.from_request(
            request,
            dispatch=self._dispatch_of(request_ref),
            provenance=self._provenance_of(request_ref),
        )

    def status_of(self, request_ref: str) -> DerivedRequestStatus:
        """Derive a deterministic status for an artifact (pure read; fail-closed)."""
        request = self._registry.get(request_ref)
        return derive_status(
            request,
            has_dispatch=self._dispatch.has(request_ref),
            has_provenance=self._provenance.has(request_ref),
        )

    # -- artifact lookup (LOOKUP; audited) --------------------------------------

    def get_artifact(self, session_id: str, request_ref: str, *, now: int) -> ArtifactView:
        """Resolve the full read view of an artifact (requires LOOKUP; fail-closed)."""
        access = self._require_access(session_id, request_ref, ExplorerAction.LOOKUP, now=now)
        view = self.view_of(request_ref)
        self._lookups += 1
        self._emit(
            ARTIFACT_VIEWED_EVENT,
            subject=request_ref,
            payload={
                "principal_id": access.principal_id,
                "family": view.family.value,
                "posture": view.posture.value,
                "is_traceable": view.is_traceable,
            },
        )
        self._metric_counter(METRIC_LOOKUPS, family=view.family.value)
        return view

    # -- request-to-artifact navigation (NAVIGATE; audited) ---------------------

    def navigate_from_request(
        self, session_id: str, request_ref: str, *, now: int
    ) -> ArtifactContext:
        """Navigate from a request to its artifact context (requires NAVIGATE; fail-closed).

        The request-to-artifact navigation entry point: it resolves the artifact view and
        binds it to the authorized principal (recording the owner standing).
        """
        access = self._require_access(session_id, request_ref, ExplorerAction.NAVIGATE, now=now)
        view = self.view_of(request_ref)
        principal = self._authorization.principals.get(access.principal_id)
        context = ArtifactContext.create(view, principal, is_owner=access.is_owner)
        self._emit(
            ARTIFACT_NAVIGATED_EVENT,
            subject=request_ref,
            payload={"principal_id": access.principal_id, "context_id": context.context_id},
        )
        return context

    # -- discovery (DISCOVER; authorized READ + isolation) ----------------------

    def discover_artifacts(
        self,
        session_id: str,
        *,
        now: int,
        tenant: str | None = None,
        workspace_id: str | None = None,
        project_id: str | None = None,
        family: BlueprintFamily | None = None,
        status: RequestStatus | None = None,
    ) -> tuple[ArtifactSummary, ...]:
        """List/filter the artifacts a caller may see (authorized READ + isolation)."""
        principal = self._resolve_principal(session_id, now)
        if principal is None:
            return ()
        decision = self._authorization.authorize_principal(
            principal, ARTIFACT_EXPLORER_GROUP, Permission.READ, tenant=tenant
        )
        if not decision.permitted:
            return ()
        summaries = tuple(
            ArtifactSummary.from_request(
                request,
                has_dispatch=self._dispatch.has(request.request_id),
                has_provenance=self._provenance.has(request.request_id),
            )
            for request in self._registry.discover(
                workspace_id=workspace_id,
                project_id=project_id,
                tenant=tenant,
                family=family,
                status=status,
            )
            if not tenants_isolated(principal.tenant, request.tenant)
        )
        self._emit(
            ARTIFACT_DISCOVERED_EVENT,
            subject=_RUNTIME_SUBJECT,
            payload={"principal_id": principal.principal_id, "result_count": len(summaries)},
        )
        self._metric_counter(METRIC_DISCOVERIES)
        return summaries

    # -- lineage navigation (LINEAGE; audited) ----------------------------------

    def lineage(self, session_id: str, request_ref: str, *, now: int) -> ArtifactLineage:
        """Return the artifact lineage (requires LINEAGE; fail-closed)."""
        access = self._require_access(session_id, request_ref, ExplorerAction.LINEAGE, now=now)
        request = self._registry.get(request_ref)
        lineage = ArtifactLineage.from_request(request, provenance=self._provenance_of(request_ref))
        self._lineage_navigations += 1
        self._emit(
            ARTIFACT_LINEAGE_NAVIGATED_EVENT,
            subject=request_ref,
            payload={"principal_id": access.principal_id, "complete": lineage.is_complete},
        )
        self._metric_counter(METRIC_LINEAGE)
        return lineage

    # -- provenance navigation (PROVENANCE; audited) ----------------------------

    def artifact_provenance(
        self, session_id: str, request_ref: str, *, now: int
    ) -> ArtifactProvenance:
        """Return the artifact's link-4 provenance projection (requires PROVENANCE; fail-closed).

        Consumes the certified :class:`RequestProvenance` by reference. Fail-closed when
        no provenance is recorded for the artifact.
        """
        access = self._require_access(session_id, request_ref, ExplorerAction.PROVENANCE, now=now)
        record = self._provenance_of(request_ref)
        if record is None:
            raise ArtifactProvenanceError(
                "no provenance recorded for artifact", request_ref=request_ref
            )
        projection = ArtifactProvenance.from_provenance(record)
        self._provenance_navigations += 1
        self._emit(
            ARTIFACT_PROVENANCE_NAVIGATED_EVENT,
            subject=request_ref,
            payload={
                "principal_id": access.principal_id,
                "provenance_id": projection.provenance_id,
            },
        )
        self._metric_counter(METRIC_PROVENANCE)
        return projection

    # -- trace navigation (TRACE; audited) --------------------------------------

    def trace(self, session_id: str, request_ref: str, *, now: int) -> ArtifactTrace:
        """Return the artifact's full generation→execution trace (requires TRACE; fail-closed)."""
        access = self._require_access(session_id, request_ref, ExplorerAction.TRACE, now=now)
        request = self._registry.get(request_ref)
        trace = ArtifactTrace.from_parts(
            request,
            provenance=self._provenance_of(request_ref),
            dispatch=self._dispatch_of(request_ref),
        )
        self._trace_navigations += 1
        self._emit(
            ARTIFACT_TRACE_NAVIGATED_EVENT,
            subject=request_ref,
            payload={"principal_id": access.principal_id, "traceable": trace.is_traceable},
        )
        self._metric_counter(METRIC_TRACE)
        return trace

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
    ) -> ArtifactSearchResponse:
        """Run an authorization- and isolation-scoped artifact search (audited)."""
        response = self._search.search(
            session_id,
            query,
            now=now,
            tenant=tenant,
            workspace_id=workspace_id,
            project_id=project_id,
            family=family,
            status=status,
        )
        self._searches += 1
        self._emit(
            ARTIFACT_SEARCHED_EVENT,
            subject=_RUNTIME_SUBJECT,
            payload={
                "query": query,
                "authorized": response.authorized,
                "result_count": len(response.results),
            },
        )
        self._metric_counter(METRIC_SEARCHES)
        return response

    # -- access evaluation ------------------------------------------------------

    def evaluate_access(
        self,
        session_id: str,
        request_ref: str,
        action: ExplorerAction,
        *,
        now: int,
    ) -> ArtifactAccess:
        """Evaluate composed explorer access (identity READ ∧ isolation).

        Denials are returned as data (``granted == False``); a malformed action or an
        unknown artifact raises. Every evaluation is emitted as a governed
        ``artifact.explorer.access.evaluated`` event (PC-16).
        """
        if not isinstance(action, ExplorerAction):
            raise ArtifactServiceError("action must be an ExplorerAction")
        permission = permission_for(action)
        request = self._registry.get(request_ref)
        decision = self._authorization.authorize(
            session_id,
            ARTIFACT_EXPLORER_GROUP,
            permission,
            now=now,
            tenant=request.tenant,
            resource=request_ref,
        )
        access = self._compose_access(request, action, permission, decision)
        self._access_evaluations += 1
        self._emit(
            ARTIFACT_ACCESS_EVENT,
            subject=access.principal_id,
            payload={
                "request_ref": request_ref,
                "action": action.value,
                "granted": access.granted,
                "reason": access.reason,
            },
        )
        return access

    def _compose_access(
        self,
        request: GenerationRequest,
        action: ExplorerAction,
        permission: Permission,
        decision: AccessDecision,
    ) -> ArtifactAccess:
        if not decision.permitted:
            return ArtifactAccess.create(
                request_ref=request.request_id,
                action=action,
                permission=permission,
                granted=False,
                reason=decision.reason,
                decision=decision,
            )
        principal = self._authorization.principals.get(decision.request.principal_id)
        if tenants_isolated(principal.tenant, request.tenant):
            return ArtifactAccess.create(
                request_ref=request.request_id,
                action=action,
                permission=permission,
                granted=False,
                reason="tenant-isolation-violation",
                decision=decision,
            )
        is_owner = principal.subject == request.owner_subject
        is_administrator = self._authorization.permissions.has_permission(
            principal, ARTIFACT_EXPLORER_GROUP, Permission.ADMINISTER
        )
        return ArtifactAccess.create(
            request_ref=request.request_id,
            action=action,
            permission=permission,
            granted=True,
            reason="granted",
            decision=decision,
            is_owner=is_owner,
            is_administrator=is_administrator,
        )

    # -- health integration -----------------------------------------------------

    def health_report(self) -> dict[str, Any]:
        """The artifact-explorer runtime health endpoint (reuses the observability model)."""
        return self._health_registry.endpoint(self._health.probe())

    def refresh_health(self) -> str:
        """Re-probe the consumed-ledger integrity and emit ``health.changed`` on transition.

        A read-only integrity check (Phase 6): it re-derives the aggregate health verdict
        over the consumed EC2-EPIC-007 ledgers and, if it differs from the last observed
        verdict (e.g. a dangling provenance/dispatch reference appeared), publishes a
        governed ``artifact.explorer.health.changed`` event. It mutates nothing.
        """
        status = self._current_health_status()
        if status != self._last_health_status:
            self._last_health_status = status
            self._emit(
                ARTIFACT_HEALTH_CHANGED_EVENT,
                subject=_RUNTIME_SUBJECT,
                payload={"status": status},
            )
        return status

    # -- evidence ---------------------------------------------------------------

    def evidence(self) -> ExplorerEvidence:
        """Produce deterministic Explorer Evidence over the runtime state."""
        report = self._health_registry.report(self._health.probe())
        requests = self._registry.all()
        dispatched = sum(1 for r in requests if self._dispatch.has(r.request_id))
        provenance_count = len(self._provenance)
        traceable = sum(
            1
            for r in requests
            if self._dispatch.has(r.request_id) and self._provenance.has(r.request_id)
        )
        return ExplorerEvidence.create(
            registry_fingerprint=self._registry.fingerprint(),
            dispatch_fingerprint=self._dispatch.fingerprint(),
            provenance_fingerprint=self._provenance.fingerprint(),
            artifact_count=len(self._registry),
            dispatched_count=dispatched,
            provenance_count=provenance_count,
            traceable_count=traceable,
            lookup_count=self._lookups,
            search_count=self._searches,
            lineage_count=self._lineage_navigations,
            provenance_navigation_count=self._provenance_navigations,
            trace_count=self._trace_navigations,
            access_evaluation_count=self._access_evaluations,
            health_status=report.status.value,
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "artifact_count": len(self._registry),
            "dispatch_count": len(self._dispatch),
            "provenance_count": len(self._provenance),
            "access_evaluation_count": self._access_evaluations,
            "lookup_count": self._lookups,
            "search_count": self._searches,
            "observability_bound": self._observability is not None,
            "evidence": self.evidence().to_dict(),
        }

    # -- internals --------------------------------------------------------------

    def _dispatch_of(self, request_ref: str) -> DispatchRecord | None:
        return self._dispatch.get(request_ref) if self._dispatch.has(request_ref) else None

    def _provenance_of(self, request_ref: str) -> RequestProvenance | None:
        return self._provenance.get(request_ref) if self._provenance.has(request_ref) else None

    def _require_access(
        self,
        session_id: str,
        request_ref: str,
        action: ExplorerAction,
        *,
        now: int,
    ) -> ArtifactAccess:
        access = self.evaluate_access(session_id, request_ref, action, now=now)
        if not access.granted:
            raise ArtifactAccessError(
                "artifact explorer action denied",
                reason=access.reason,
                request_ref=request_ref,
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

    def _emit(self, event_type: str, *, subject: str, payload: dict[str, Any]) -> None:
        if self._events is not None:
            self._events.publish(
                event_type,
                source="platform.artifact_explorer.runtime",
                subject=subject,
                payload=payload,
            )

    def _metric_counter(self, name: str, **labels: str) -> None:
        if self._observability is not None:
            self._observability.metrics.counter(name, 1.0, **labels)


def build_artifact_explorer_service(
    *,
    authorization: AuthorizationService,
    registry: GenerationRequestRegistry | None = None,
    dispatch: DispatchLedger | None = None,
    provenance: ProvenanceLedger | None = None,
    observability: ObservabilityService | None = None,
    events: EventBus | None = None,
) -> ArtifactExplorerService:
    """Default, registry-driven composition of the Artifact Explorer Runtime.

    Wires the consumed generation request registry, dispatch + provenance ledgers (by
    reference), artifact search (over the supplied Identity ``authorization`` service),
    the explorer health probe and a health registry seeded with the explorer health
    checks, and — when supplied — the observability layer and event bus. The registry /
    dispatch / provenance are consumed by reference (typically the EC2-EPIC-007 runtime's
    own components); fresh empty ones are used only when not supplied.
    """
    if not isinstance(authorization, AuthorizationService):
        raise ArtifactServiceError(
            "build_artifact_explorer_service requires an AuthorizationService"
        )
    request_registry = registry if registry is not None else GenerationRequestRegistry()
    dispatch_ledger = dispatch if dispatch is not None else DispatchLedger()
    provenance_ledger = provenance if provenance is not None else ProvenanceLedger()
    search = ArtifactSearch(request_registry, dispatch_ledger, provenance_ledger, authorization)
    health = ExplorerHealth(request_registry, dispatch_ledger, provenance_ledger)
    health_registry = HealthRegistry()
    for check in artifact_explorer_health_checks():
        health_registry.register(check)
    return ArtifactExplorerService(
        registry=request_registry,
        dispatch=dispatch_ledger,
        provenance=provenance_ledger,
        authorization=authorization,
        search=search,
        health=health,
        health_registry=health_registry,
        observability=observability,
        events=events,
    )


__all__ = [
    "ARTIFACT_VIEWED_EVENT",
    "ARTIFACT_DISCOVERED_EVENT",
    "ARTIFACT_LINEAGE_NAVIGATED_EVENT",
    "ARTIFACT_PROVENANCE_NAVIGATED_EVENT",
    "ARTIFACT_TRACE_NAVIGATED_EVENT",
    "ARTIFACT_SEARCHED_EVENT",
    "ARTIFACT_NAVIGATED_EVENT",
    "ARTIFACT_HEALTH_CHANGED_EVENT",
    "ARTIFACT_ACCESS_EVENT",
    "METRIC_LOOKUPS",
    "METRIC_DISCOVERIES",
    "METRIC_SEARCHES",
    "METRIC_LINEAGE",
    "METRIC_PROVENANCE",
    "METRIC_TRACE",
    "ArtifactAccess",
    "ArtifactExplorerService",
    "build_artifact_explorer_service",
]
