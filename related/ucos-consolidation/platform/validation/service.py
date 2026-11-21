"""EC2-TASK-000151 — Validation Console Service (EC2-EPIC-010).

The single, governed **validation-console runtime composition point** (L3 Application of
the Program architecture) that composes the whole Validation Console Runtime into one
entry point — the governed inspection surface for Program Surface #9 Validation Explorer
(PC-09 validation inspection + PC-13 search + PC-16 audit):

    ValidationRecordRegistry · ValidationFacade (engine.validation by reference) ·
    ValidationSearch · ValidationHealth · (reused) AuthorizationService ·
    ObservabilityService

It is a strictly **additive**, **read/inspection-only** layer: it authorizes only
through the certified Identity Layer (L7) on the existing ``validation-explorer``
capability group — **no duplicate authorization or identity logic, no new authority, no
new capability group** — surfaces the certified EC-1 validation output **by reference**
(reproduced read-only by the L4 façade, never re-derived — TP-01), observes only through
the Observability Layer (L8), and exposes **no mutation path** to any surfaced report,
evidence, or acceptance decision. It re-implements none of them, modifies neither EC-1
nor any prior layer, and writes nothing to the certified corpus (DP-03).

Every access is fail-closed and composes gates — **identity authorization** (RBAC §3.2,
READ) and **tenant/workspace isolation** (the reused rule, P3) — so cross-tenant access
is refused in 100% of cases. Because every governed action is published onto the
Foundation event bus and appended to the registry's inspection log, it is captured as
append-only audit (PC-16 / OP-C3).

The service is deterministic: the same identity registrations, the same surfaced
validations, and the same ordered sequence of calls yield the same
:class:`~platform.validation.evidence.ValidationConsoleEvidence` fingerprint (P5).
:func:`build_validation_console_service` provides the default wiring;
:func:`~platform.validation.bootstrap.bootstrap_validation_console` composes it onto a
:class:`~platform.foundation.bootstrap.PlatformContext`.
"""

from __future__ import annotations

from dataclasses import dataclass
from platform.foundation.contracts import content_hash
from platform.foundation.events import EventBus
from platform.foundation.identity import Permission
from platform.identity.contracts import AccessDecision
from platform.identity.errors import IdentityError
from platform.identity.service import AuthorizationService
from platform.observability.health import HealthRegistry
from platform.observability.service import ObservabilityService
from platform.validation.context import ValidationContext
from platform.validation.contracts import (
    VALIDATION_CONSOLE_GROUP,
    ValidationAction,
    ValidationDecisionView,
    ValidationEvidenceReference,
    ValidationRecord,
    ValidationSummary,
    ValidationTrace,
    permission_for,
)
from platform.validation.errors import (
    ValidationAccessError,
    ValidationServiceError,
)
from platform.validation.evidence import ValidationConsoleEvidence
from platform.validation.facade import SurfacedValidation, ValidationFacade
from platform.validation.health import ValidationHealth, validation_console_health_checks
from platform.validation.metadata import ValidationRecordMetadata
from platform.validation.registry import ValidationRecordRegistry
from platform.validation.search import ValidationSearch, ValidationSearchResponse
from platform.validation.status import DerivedValidationStatus, derive_status
from platform.workspace.isolation import tenants_isolated
from typing import Any

from engine.validation.contracts import ValidationReport, ValidationSubject

#: Governed events published onto the Foundation event bus (observed as PC-16).
VALIDATION_SURFACED_EVENT = "validation.report.surfaced"
VALIDATION_INSPECTED_EVENT = "validation.report.inspected"
VALIDATION_EVIDENCE_RENDERED_EVENT = "validation.report.evidence.rendered"
VALIDATION_DECISION_RENDERED_EVENT = "validation.report.decision.rendered"
VALIDATION_SEARCHED_EVENT = "validation.report.searched"
VALIDATION_TRACED_EVENT = "validation.report.traced"
VALIDATION_ACCEPTED_EVENT = "validation.report.accepted"
VALIDATION_REJECTED_EVENT = "validation.report.rejected"
VALIDATION_HEALTH_CHANGED_EVENT = "validation.console.health.changed"
VALIDATION_ACCESS_EVENT = "validation.report.access.evaluated"

#: The stable subject used for runtime-scoped (non-record) governed events.
_RUNTIME_SUBJECT = "platform.validation.runtime"

# --------------------------------------------------------------------------- #
# Observability metric names (PC-12 monitoring; reproducible, no wall-clock).  #
# --------------------------------------------------------------------------- #
METRIC_SURFACED = "validation.reports.surfaced"
METRIC_ACCEPTED = "validation.reports.accepted"
METRIC_REJECTED = "validation.reports.rejected"
METRIC_ADVISORY = "validation.reports.advisory"
METRIC_INSPECTIONS = "validation.reports.inspections"
METRIC_BLOCKING_FAILURES = "validation.reports.blocking_failures"


@dataclass(frozen=True, slots=True)
class ValidationAccess:
    """An immutable, content-addressed validation-console access decision (fail-closed).

    Composes identity authorization (READ) and tenant/workspace isolation into a single
    verdict for one ``(principal, record, action)`` request. The console is read-only, so
    there is no owner/mutation gate; ``is_owner`` is carried for context only.
    """

    record_id: str
    principal_id: str
    action: ValidationAction
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
        record_id: str,
        action: ValidationAction,
        permission: Permission,
        granted: bool,
        reason: str,
        decision: AccessDecision,
        is_owner: bool = False,
    ) -> ValidationAccess:
        principal_id = decision.request.principal_id
        core = {
            "record_id": record_id,
            "principal_id": principal_id,
            "action": action.value,
            "permission": permission.value,
            "granted": granted,
            "reason": reason,
            "is_owner": is_owner,
        }
        return cls(
            record_id=record_id,
            principal_id=principal_id,
            action=action,
            permission=permission,
            granted=granted,
            reason=reason,
            is_owner=is_owner,
            decision=decision,
            access_id=f"UCOS-VACC-{content_hash(core)[:16]}",
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "access_id": self.access_id,
            "record_id": self.record_id,
            "principal_id": self.principal_id,
            "action": self.action.value,
            "permission": self.permission.value,
            "granted": self.granted,
            "reason": self.reason,
            "is_owner": self.is_owner,
            "decision": self.decision.to_dict(),
        }


class ValidationConsoleService:
    """The governed L3 composition point for the UCOS Validation Console Runtime."""

    __slots__ = (
        "_registry",
        "_facade",
        "_authorization",
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
        registry: ValidationRecordRegistry,
        facade: ValidationFacade,
        authorization: AuthorizationService,
        search: ValidationSearch,
        health: ValidationHealth,
        health_registry: HealthRegistry,
        observability: ObservabilityService | None = None,
        events: EventBus | None = None,
    ) -> None:
        if not isinstance(registry, ValidationRecordRegistry):
            raise ValidationServiceError("a valid ValidationRecordRegistry is required")
        if not isinstance(facade, ValidationFacade):
            raise ValidationServiceError("a valid ValidationFacade is required")
        if not isinstance(authorization, AuthorizationService):
            raise ValidationServiceError("a valid AuthorizationService is required")
        if not isinstance(search, ValidationSearch):
            raise ValidationServiceError("a valid ValidationSearch is required")
        if not isinstance(health, ValidationHealth):
            raise ValidationServiceError("a valid ValidationHealth is required")
        if not isinstance(health_registry, HealthRegistry):
            raise ValidationServiceError("a valid HealthRegistry is required")
        if observability is not None and not isinstance(observability, ObservabilityService):
            raise ValidationServiceError(
                "observability must be an ObservabilityService when provided"
            )
        if events is not None and not isinstance(events, EventBus):
            raise ValidationServiceError("events must be an EventBus when provided")
        self._registry = registry
        self._facade = facade
        self._authorization = authorization
        self._search = search
        self._health = health
        self._health_registry = health_registry
        self._observability = observability
        self._events = events
        self._access_evaluations = 0
        self._last_health_status = self._current_health_status()

    # -- component access -------------------------------------------------------

    @property
    def registry(self) -> ValidationRecordRegistry:
        return self._registry

    @property
    def facade(self) -> ValidationFacade:
        return self._facade

    @property
    def authorization(self) -> AuthorizationService:
        return self._authorization

    @property
    def health(self) -> ValidationHealth:
        return self._health

    @property
    def observability(self) -> ObservabilityService | None:
        return self._observability

    @property
    def access_evaluation_count(self) -> int:
        return self._access_evaluations

    # -- surfacing (reproduce + record a validation, read-only over EC-1) -------

    def surface_validation(
        self,
        session_id: str,
        subject: ValidationSubject,
        *,
        now: int,
        request_ref: str | None = None,
        workspace_id: str | None = None,
        project_id: str | None = None,
        tenant: str | None = None,
        metadata: ValidationRecordMetadata | None = None,
    ) -> ValidationRecord:
        """Reproduce (read-only) and record the certified validation of ``subject``.

        Requires identity READ on ``validation-explorer`` (with the target's tenant) and
        cross-tenant isolation clearance. The certified :class:`ValidationReport` +
        evidence + decision are reproduced by the L4 façade (never re-derived); the record
        is content-addressed and idempotent. Raises :class:`ValidationAccessError` on any
        denial. This is a read operation over EC-1 truth — it exposes no mutation of any
        validation datum.
        """
        if not isinstance(subject, ValidationSubject):
            raise ValidationServiceError("surface_validation requires a ValidationSubject")
        decision = self._authorization.authorize(
            session_id,
            VALIDATION_CONSOLE_GROUP,
            Permission.READ,
            now=now,
            tenant=tenant,
            resource=subject.target_id,
        )
        if not decision.permitted:
            raise ValidationAccessError(
                "validation surfacing denied", reason=decision.reason, target=subject.target_id
            )
        principal = self._authorization.principals.get(decision.request.principal_id)
        if tenants_isolated(principal.tenant, tenant):
            raise ValidationAccessError(
                "cross-tenant validation surfacing denied",
                reason="tenant-isolation-violation",
                target=subject.target_id,
            )
        surfaced: SurfacedValidation = self._facade.surface(subject)
        record = ValidationRecord.create(
            report=surfaced.report,
            evidence=surfaced.evidence,
            decision=surfaced.decision,
            subject=surfaced.subject,
            owner_subject=principal.subject,
            request_ref=request_ref,
            workspace_id=workspace_id,
            project_id=project_id,
            tenant=tenant,
            metadata=metadata,
        )
        record = self._registry.record(record)
        self._emit(
            VALIDATION_SURFACED_EVENT,
            subject=record.record_id,
            payload={
                "target_id": record.target_id,
                "blueprint_id": record.blueprint_id,
                "verdict": record.report.verdict.value,
                "accepted": record.accepted,
                "engine_contract": surfaced.engine_contract,
                "request_ref": request_ref,
                "tenant": tenant,
            },
        )
        self._emit(
            VALIDATION_ACCEPTED_EVENT if record.accepted else VALIDATION_REJECTED_EVENT,
            subject=record.record_id,
            payload={"target_id": record.target_id, "verdict": record.report.verdict.value},
        )
        self._metric_counter(METRIC_SURFACED)
        self._metric_counter(METRIC_ACCEPTED if record.accepted else METRIC_REJECTED)
        if record.report.advisory_failures:
            self._metric_counter(METRIC_ADVISORY)
        self._metric_histogram(
            METRIC_BLOCKING_FAILURES, float(len(record.report.blocking_failures))
        )
        self._emit_health_change()
        return record

    # -- retrieval / resolution -------------------------------------------------

    def get_validation(self, record_id: str) -> ValidationRecord:
        """Retrieve a record by id (pure read; fail-closed on absent)."""
        return self._registry.get(record_id)

    def summary_of(self, record_id: str) -> ValidationSummary:
        """Return the report summary for a record (pure read; fail-closed on absent)."""
        return self._registry.get(record_id).summary()

    def report_of(self, record_id: str) -> ValidationReport:
        """Return the certified report for a record (pure read; fail-closed on absent)."""
        return self._registry.get(record_id).report

    def list_validations(
        self,
        session_id: str,
        *,
        now: int,
        tenant: str | None = None,
        target_id: str | None = None,
        blueprint_id: str | None = None,
        request_ref: str | None = None,
        workspace_id: str | None = None,
        project_id: str | None = None,
        accepted: bool | None = None,
    ) -> tuple[ValidationRecord, ...]:
        """List/filter the records a caller may see (authorized READ + isolation)."""
        principal = self._resolve_principal(session_id, now)
        if principal is None:
            return ()
        decision = self._authorization.authorize_principal(
            principal, VALIDATION_CONSOLE_GROUP, Permission.READ, tenant=tenant
        )
        if not decision.permitted:
            return ()
        return tuple(
            record
            for record in self._registry.discover(
                target_id=target_id,
                blueprint_id=blueprint_id,
                request_ref=request_ref,
                workspace_id=workspace_id,
                project_id=project_id,
                tenant=tenant,
                accepted=accepted,
            )
            if not tenants_isolated(principal.tenant, record.tenant)
        )

    # -- selection / inspection (record-scoped, audited) ------------------------

    def select_validation(self, session_id: str, record_id: str, *, now: int) -> ValidationContext:
        """Select a record and return its runtime context (requires INSPECT; fail-closed)."""
        access = self._require_access(session_id, record_id, ValidationAction.INSPECT, now=now)
        record = self._registry.get(record_id)
        principal = self._authorization.principals.get(access.principal_id)
        self._registry.record_inspection(
            record_id, ValidationAction.INSPECT.value, access.principal_id, tick=now
        )
        self._emit(
            VALIDATION_INSPECTED_EVENT,
            subject=record_id,
            payload={"target_id": record.target_id, "principal_id": access.principal_id},
        )
        self._metric_counter(METRIC_INSPECTIONS)
        return ValidationContext.create(record, principal, is_owner=access.is_owner)

    def view_evidence(
        self, session_id: str, record_id: str, *, now: int
    ) -> ValidationEvidenceReference:
        """Render the evidence reference for a record (requires VIEW_EVIDENCE; fail-closed)."""
        access = self._require_access(
            session_id, record_id, ValidationAction.VIEW_EVIDENCE, now=now
        )
        record = self._registry.get(record_id)
        self._registry.record_inspection(
            record_id, ValidationAction.VIEW_EVIDENCE.value, access.principal_id, tick=now
        )
        reference = record.evidence_reference()
        self._emit(
            VALIDATION_EVIDENCE_RENDERED_EVENT,
            subject=record_id,
            payload={
                "target_id": record.target_id,
                "evidence_fingerprint": reference.evidence_fingerprint,
            },
        )
        return reference

    def view_decision(self, session_id: str, record_id: str, *, now: int) -> ValidationDecisionView:
        """Render the acceptance-decision view (requires VIEW_DECISION; fail-closed)."""
        access = self._require_access(
            session_id, record_id, ValidationAction.VIEW_DECISION, now=now
        )
        record = self._registry.get(record_id)
        self._registry.record_inspection(
            record_id, ValidationAction.VIEW_DECISION.value, access.principal_id, tick=now
        )
        view = record.decision_view()
        self._emit(
            VALIDATION_DECISION_RENDERED_EVENT,
            subject=record_id,
            payload={"target_id": record.target_id, "accepted": view.accepted},
        )
        return view

    # -- status tracking --------------------------------------------------------

    def status_of(self, record_id: str) -> DerivedValidationStatus:
        """Derive a deterministic status for a record (pure read; fail-closed)."""
        return derive_status(self._registry.get(record_id).report)

    def track_validation(
        self, session_id: str, record_id: str, *, now: int
    ) -> DerivedValidationStatus:
        """Track a record's derived status (requires TRACK/READ access; fail-closed)."""
        access = self._require_access(session_id, record_id, ValidationAction.TRACK, now=now)
        self._registry.record_inspection(
            record_id, ValidationAction.TRACK.value, access.principal_id, tick=now
        )
        return self.status_of(record_id)

    # -- traceability -----------------------------------------------------------

    def trace(self, session_id: str, record_id: str, *, now: int) -> ValidationTrace:
        """Return the validation trace edge for a record (requires TRACE; fail-closed)."""
        access = self._require_access(session_id, record_id, ValidationAction.TRACE, now=now)
        record = self._registry.get(record_id)
        self._registry.record_inspection(
            record_id, ValidationAction.TRACE.value, access.principal_id, tick=now
        )
        trace = record.trace()
        self._emit(
            VALIDATION_TRACED_EVENT,
            subject=record_id,
            payload=trace.edge(),
        )
        return trace

    # -- fidelity (machine-checkable, P6) ---------------------------------------

    def verify_fidelity(self, record_id: str) -> bool:
        """True iff the record's stored report reproduces the certified engine output (P6)."""
        record = self._registry.get(record_id)
        return self._facade.verify_fidelity(record.report, record.subject)

    # -- search -----------------------------------------------------------------

    def search(
        self,
        session_id: str,
        query: str,
        *,
        now: int,
        tenant: str | None = None,
        target_id: str | None = None,
        blueprint_id: str | None = None,
        request_ref: str | None = None,
        workspace_id: str | None = None,
        project_id: str | None = None,
        accepted: bool | None = None,
    ) -> ValidationSearchResponse:
        """Run an authorization- and isolation-scoped validation search."""
        response = self._search.search(
            session_id,
            query,
            now=now,
            tenant=tenant,
            target_id=target_id,
            blueprint_id=blueprint_id,
            request_ref=request_ref,
            workspace_id=workspace_id,
            project_id=project_id,
            accepted=accepted,
        )
        self._emit(
            VALIDATION_SEARCHED_EVENT,
            subject=_RUNTIME_SUBJECT,
            payload={
                "query": query,
                "authorized": response.authorized,
                "result_count": len(response.results),
            },
        )
        return response

    # -- metadata ---------------------------------------------------------------

    def annotate(
        self, session_id: str, record_id: str, metadata: ValidationRecordMetadata, *, now: int
    ) -> ValidationRecord:
        """Attach descriptive console metadata to a record (requires INSPECT/READ).

        This mutates only the console's own descriptive annotation — never any surfaced
        validation datum (report/evidence/decision are immutable). Fail-closed.
        """
        self._require_access(session_id, record_id, ValidationAction.INSPECT, now=now)
        if not isinstance(metadata, ValidationRecordMetadata):
            raise ValidationServiceError("annotate requires a ValidationRecordMetadata")
        return self._registry.update_metadata(record_id, metadata)

    # -- access evaluation ------------------------------------------------------

    def evaluate_access(
        self,
        session_id: str,
        record_id: str,
        action: ValidationAction,
        *,
        now: int,
    ) -> ValidationAccess:
        """Evaluate composed console access (identity READ ∧ isolation).

        Denials are returned as data (``granted == False``); a malformed action or an
        unknown record raises. Every evaluation is emitted as a governed
        ``validation.report.access.evaluated`` event (PC-16).
        """
        if not isinstance(action, ValidationAction):
            raise ValidationServiceError("action must be a ValidationAction")
        permission = permission_for(action)
        record = self._registry.get(record_id)
        decision = self._authorization.authorize(
            session_id,
            VALIDATION_CONSOLE_GROUP,
            permission,
            now=now,
            tenant=record.tenant,
            resource=record_id,
        )
        access = self._compose_access(record, action, permission, decision)
        self._access_evaluations += 1
        self._emit(
            VALIDATION_ACCESS_EVENT,
            subject=access.principal_id,
            payload={
                "record_id": record_id,
                "action": action.value,
                "granted": access.granted,
                "reason": access.reason,
            },
        )
        return access

    def _compose_access(
        self,
        record: ValidationRecord,
        action: ValidationAction,
        permission: Permission,
        decision: AccessDecision,
    ) -> ValidationAccess:
        if not decision.permitted:
            return ValidationAccess.create(
                record_id=record.record_id,
                action=action,
                permission=permission,
                granted=False,
                reason=decision.reason,
                decision=decision,
            )
        principal = self._authorization.principals.get(decision.request.principal_id)
        if tenants_isolated(principal.tenant, record.tenant):
            return ValidationAccess.create(
                record_id=record.record_id,
                action=action,
                permission=permission,
                granted=False,
                reason="tenant-isolation-violation",
                decision=decision,
            )
        is_owner = principal.subject == record.owner_subject
        return ValidationAccess.create(
            record_id=record.record_id,
            action=action,
            permission=permission,
            granted=True,
            reason="granted",
            decision=decision,
            is_owner=is_owner,
        )

    # -- health integration -----------------------------------------------------

    def health_report(self) -> dict[str, Any]:
        """The validation-console runtime health endpoint (reuses the observability model)."""
        return self._health_registry.endpoint(self._health.probe())

    # -- evidence ---------------------------------------------------------------

    def evidence(self) -> ValidationConsoleEvidence:
        """Produce deterministic Validation Console Evidence over the runtime state."""
        report = self._health_registry.report(self._health.probe())
        census = self._registry.count_by_verdict()
        return ValidationConsoleEvidence.create(
            registry_fingerprint=self._registry.fingerprint(),
            record_count=census["total"],
            accepted_count=census["accepted"],
            rejected_count=census["rejected"],
            inspection_count=len(self._registry.inspections),
            access_evaluation_count=self._access_evaluations,
            verdict_census=tuple(sorted(census.items())),
            health_status=report.status.value,
        )

    def to_dict(self) -> dict[str, Any]:
        census = self._registry.count_by_verdict()
        return {
            "record_count": census["total"],
            "accepted_count": census["accepted"],
            "rejected_count": census["rejected"],
            "inspection_count": len(self._registry.inspections),
            "access_evaluation_count": self._access_evaluations,
            "observability_bound": self._observability is not None,
            "evidence": self.evidence().to_dict(),
        }

    # -- internals --------------------------------------------------------------

    def _require_access(
        self,
        session_id: str,
        record_id: str,
        action: ValidationAction,
        *,
        now: int,
    ) -> ValidationAccess:
        access = self.evaluate_access(session_id, record_id, action, now=now)
        if not access.granted:
            raise ValidationAccessError(
                "validation console action denied",
                reason=access.reason,
                record_id=record_id,
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
                VALIDATION_HEALTH_CHANGED_EVENT,
                subject=_RUNTIME_SUBJECT,
                payload={"status": status},
            )

    def _emit(self, event_type: str, *, subject: str, payload: dict[str, Any]) -> None:
        if self._events is not None:
            self._events.publish(
                event_type,
                source="platform.validation.runtime",
                subject=subject,
                payload=payload,
            )

    def _metric_counter(self, name: str, **labels: str) -> None:
        if self._observability is not None:
            self._observability.metrics.counter(name, 1.0, **labels)

    def _metric_histogram(self, name: str, value: float, **labels: str) -> None:
        if self._observability is not None:
            self._observability.metrics.histogram(name, value, **labels)


def build_validation_console_service(
    *,
    authorization: AuthorizationService,
    observability: ObservabilityService | None = None,
    events: EventBus | None = None,
    registry: ValidationRecordRegistry | None = None,
    facade: ValidationFacade | None = None,
) -> ValidationConsoleService:
    """Default, registry-driven composition of the Validation Console Runtime.

    Wires the record registry, the read-only EC-1 validation façade (consumes
    ``engine.validation`` by reference), validation search (over the supplied Identity
    ``authorization`` service), the console health probe and a health registry seeded with
    the console health checks, and — when supplied — the observability layer and event bus.
    """
    if not isinstance(authorization, AuthorizationService):
        raise ValidationServiceError(
            "build_validation_console_service requires an AuthorizationService"
        )
    record_registry = registry if registry is not None else ValidationRecordRegistry()
    validation_facade = facade if facade is not None else ValidationFacade()
    search = ValidationSearch(record_registry, authorization)
    health = ValidationHealth(record_registry, validation_facade)
    health_registry = HealthRegistry()
    for check in validation_console_health_checks():
        health_registry.register(check)
    return ValidationConsoleService(
        registry=record_registry,
        facade=validation_facade,
        authorization=authorization,
        search=search,
        health=health,
        health_registry=health_registry,
        observability=observability,
        events=events,
    )


__all__ = [
    "VALIDATION_SURFACED_EVENT",
    "VALIDATION_INSPECTED_EVENT",
    "VALIDATION_EVIDENCE_RENDERED_EVENT",
    "VALIDATION_DECISION_RENDERED_EVENT",
    "VALIDATION_SEARCHED_EVENT",
    "VALIDATION_TRACED_EVENT",
    "VALIDATION_ACCEPTED_EVENT",
    "VALIDATION_REJECTED_EVENT",
    "VALIDATION_HEALTH_CHANGED_EVENT",
    "VALIDATION_ACCESS_EVENT",
    "METRIC_SURFACED",
    "METRIC_ACCEPTED",
    "METRIC_REJECTED",
    "METRIC_ADVISORY",
    "METRIC_INSPECTIONS",
    "METRIC_BLOCKING_FAILURES",
    "ValidationAccess",
    "ValidationConsoleService",
    "build_validation_console_service",
]
