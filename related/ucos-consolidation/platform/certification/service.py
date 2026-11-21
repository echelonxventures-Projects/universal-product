"""EC2-TASK-000160 — Certification Console Service (EC2-EPIC-011).

The single, governed **certification-console runtime composition point** (L3 Application
of the Program architecture) that composes the whole Certification Console & Ledger
Runtime into one entry point — the governed inspection surface for Program Surface #10
*Certification Ledger* (PC-10 certification inspection & ledger + PC-13 search + PC-16
audit):

    CertificationRegistry · CertificationFacade (engine.certification by reference) ·
    CertificationConsoleLedger · CertificationSearch · CertificationHealth ·
    (reused) AuthorizationService · ObservabilityService

It is a strictly **additive**, **read/inspection-only** layer: it authorizes only through
the certified Identity Layer (L7) on the existing ``certification-ledger`` capability
group — **no duplicate authorization or identity logic, no new authority, no new
capability group** — surfaces the certified EC-1 certification output **by reference**
(reproduced read-only by the L4 façade, never re-derived — TP-01), observes only through
the Observability Layer (L8), and exposes **no mutation path** to any surfaced record,
evidence, or ledger entry (the ledger is append-only by construction). It re-implements
none of them, modifies neither EC-1 nor any prior layer, and writes nothing to the
certified corpus (DP-03).

Every access is fail-closed and composes gates — **identity authorization** (RBAC §3.2,
READ) and **tenant/workspace isolation** (the reused rule, P3) — so cross-tenant access
is refused in 100% of cases. Because every governed action is published onto the
Foundation event bus and appended to the registry's inspection log, it is captured as
append-only audit (PC-16 / OP-C3).

The service is deterministic: the same identity registrations, the same surfaced
certifications, and the same ordered sequence of calls yield the same
:class:`~platform.certification.evidence.CertificationConsoleEvidence` fingerprint (P5).
:func:`build_certification_console_service` provides the default wiring;
:func:`~platform.certification.bootstrap.bootstrap_certification_console` composes it onto
a :class:`~platform.foundation.bootstrap.PlatformContext`.
"""

from __future__ import annotations

from dataclasses import dataclass
from platform.certification.context import CertificationContext
from platform.certification.contracts import (
    CERTIFICATION_CONSOLE_GROUP,
    CertificationAction,
    CertificationConsoleRecord,
    CertificationEvidenceReference,
    CertificationRecordMetadata,
    CertificationSummary,
    CertificationTrace,
    permission_for,
)
from platform.certification.errors import (
    CertificationAccessError,
    CertificationServiceError,
)
from platform.certification.evidence import CertificationConsoleEvidence
from platform.certification.facade import CertificationFacade, SurfacedCertification
from platform.certification.health import (
    CertificationHealth,
    certification_console_health_checks,
)
from platform.certification.ledger import (
    CertificationConsoleLedger,
    CertificationLedgerView,
    CertificationLineageView,
)
from platform.certification.registry import CertificationRegistry
from platform.certification.search import CertificationSearch, CertificationSearchResponse
from platform.certification.status import (
    CertificationReadiness,
    DerivedCertificationStatus,
    GovernanceAssessment,
    derive_status,
    evaluate_readiness,
    validate_governance,
)
from platform.foundation.contracts import content_hash
from platform.foundation.events import EventBus
from platform.foundation.identity import Permission
from platform.identity.contracts import AccessDecision
from platform.identity.errors import IdentityError
from platform.identity.service import AuthorizationService
from platform.observability.health import HealthRegistry
from platform.observability.service import ObservabilityService
from platform.workspace.isolation import tenants_isolated
from typing import Any

from engine.certification.contracts import CertificationClass
from engine.certification.engine import CertificationDecision
from engine.validation.contracts import ValidationReport
from engine.validation.evidence import ValidationEvidence

#: Governed events published onto the Foundation event bus (observed as PC-16).
CERTIFICATION_SURFACED_EVENT = "certification.record.surfaced"
CERTIFICATION_INSPECTED_EVENT = "certification.record.inspected"
CERTIFICATION_EVIDENCE_RENDERED_EVENT = "certification.record.evidence.rendered"
CERTIFICATION_LEDGER_VIEWED_EVENT = "certification.record.ledger.viewed"
CERTIFICATION_LINEAGE_RENDERED_EVENT = "certification.record.lineage.rendered"
CERTIFICATION_SEARCHED_EVENT = "certification.record.searched"
CERTIFICATION_TRACED_EVENT = "certification.record.traced"
CERTIFICATION_CERTIFIED_EVENT = "certification.record.certified"
CERTIFICATION_NOT_CERTIFIED_EVENT = "certification.record.not_certified"
CERTIFICATION_READINESS_EVALUATED_EVENT = "certification.record.readiness.evaluated"
CERTIFICATION_GOVERNANCE_VALIDATED_EVENT = "certification.record.governance.validated"
CERTIFICATION_LEDGER_APPENDED_EVENT = "certification.ledger.appended"
CERTIFICATION_HEALTH_CHANGED_EVENT = "certification.console.health.changed"
CERTIFICATION_ACCESS_EVENT = "certification.record.access.evaluated"

#: The stable subject used for runtime-scoped (non-record) governed events.
_RUNTIME_SUBJECT = "platform.certification.runtime"

# --------------------------------------------------------------------------- #
# Observability metric names (PC-12 monitoring; reproducible, no wall-clock).  #
# --------------------------------------------------------------------------- #
METRIC_SURFACED = "certification.records.surfaced"
METRIC_CERTIFIED = "certification.records.certified"
METRIC_NOT_CERTIFIED = "certification.records.not_certified"
METRIC_ADVISORY = "certification.records.advisory"
METRIC_INSPECTIONS = "certification.records.inspections"
METRIC_LEDGER_APPENDS = "certification.ledger.appends"
METRIC_BLOCKING_FAILURES = "certification.records.blocking_failures"


@dataclass(frozen=True, slots=True)
class CertificationAccess:
    """An immutable, content-addressed certification-console access decision (fail-closed).

    Composes identity authorization (READ) and tenant/workspace isolation into a single
    verdict for one ``(principal, record, action)`` request. The console is read-only, so
    there is no owner/mutation gate; ``is_owner`` is carried for context only.
    """

    record_id: str
    principal_id: str
    action: CertificationAction
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
        action: CertificationAction,
        permission: Permission,
        granted: bool,
        reason: str,
        decision: AccessDecision,
        is_owner: bool = False,
    ) -> CertificationAccess:
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
            access_id=f"UCOS-CACC-{content_hash(core)[:16]}",
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


class CertificationConsoleService:
    """The governed L3 composition point for the UCOS Certification Console & Ledger Runtime."""

    __slots__ = (
        "_registry",
        "_facade",
        "_ledger",
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
        registry: CertificationRegistry,
        facade: CertificationFacade,
        ledger: CertificationConsoleLedger,
        authorization: AuthorizationService,
        search: CertificationSearch,
        health: CertificationHealth,
        health_registry: HealthRegistry,
        observability: ObservabilityService | None = None,
        events: EventBus | None = None,
    ) -> None:
        if not isinstance(registry, CertificationRegistry):
            raise CertificationServiceError("a valid CertificationRegistry is required")
        if not isinstance(facade, CertificationFacade):
            raise CertificationServiceError("a valid CertificationFacade is required")
        if not isinstance(ledger, CertificationConsoleLedger):
            raise CertificationServiceError("a valid CertificationConsoleLedger is required")
        if not isinstance(authorization, AuthorizationService):
            raise CertificationServiceError("a valid AuthorizationService is required")
        if not isinstance(search, CertificationSearch):
            raise CertificationServiceError("a valid CertificationSearch is required")
        if not isinstance(health, CertificationHealth):
            raise CertificationServiceError("a valid CertificationHealth is required")
        if not isinstance(health_registry, HealthRegistry):
            raise CertificationServiceError("a valid HealthRegistry is required")
        if observability is not None and not isinstance(observability, ObservabilityService):
            raise CertificationServiceError(
                "observability must be an ObservabilityService when provided"
            )
        if events is not None and not isinstance(events, EventBus):
            raise CertificationServiceError("events must be an EventBus when provided")
        self._registry = registry
        self._facade = facade
        self._ledger = ledger
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
    def registry(self) -> CertificationRegistry:
        return self._registry

    @property
    def facade(self) -> CertificationFacade:
        return self._facade

    @property
    def ledger(self) -> CertificationConsoleLedger:
        return self._ledger

    @property
    def authorization(self) -> AuthorizationService:
        return self._authorization

    @property
    def health(self) -> CertificationHealth:
        return self._health

    @property
    def observability(self) -> ObservabilityService | None:
        return self._observability

    @property
    def access_evaluation_count(self) -> int:
        return self._access_evaluations

    # -- surfacing (reproduce + record + ledger a certification, read-only over EC-1) --

    def surface_certification(
        self,
        session_id: str,
        report: ValidationReport,
        validation_evidence: ValidationEvidence,
        *,
        now: int,
        version: str,
        certification_class: CertificationClass = CertificationClass.ENGINEERING_READINESS,
        request_ref: str | None = None,
        workspace_id: str | None = None,
        project_id: str | None = None,
        tenant: str | None = None,
        metadata: CertificationRecordMetadata | None = None,
    ) -> CertificationConsoleRecord:
        """Reproduce (read-only) and record + ledger the certified certification.

        Requires identity READ on ``certification-ledger`` (with the target's tenant) and
        cross-tenant isolation clearance. The certified :class:`CertificationDecision` +
        record + evidence are reproduced by the L4 façade over the supplied validation
        output (never re-derived); the console record is content-addressed and idempotent,
        and the immutable certified record is appended to the append-only ledger. Raises
        :class:`CertificationAccessError` on any denial.
        """
        if not isinstance(report, ValidationReport):
            raise CertificationServiceError("surface_certification requires a ValidationReport")
        if not isinstance(validation_evidence, ValidationEvidence):
            raise CertificationServiceError("surface_certification requires a ValidationEvidence")
        decision = self._authorization.authorize(
            session_id,
            CERTIFICATION_CONSOLE_GROUP,
            Permission.READ,
            now=now,
            tenant=tenant,
            resource=report.target_id,
        )
        if not decision.permitted:
            raise CertificationAccessError(
                "certification surfacing denied",
                reason=decision.reason,
                target=report.target_id,
            )
        principal = self._authorization.principals.get(decision.request.principal_id)
        if tenants_isolated(principal.tenant, tenant):
            raise CertificationAccessError(
                "cross-tenant certification surfacing denied",
                reason="tenant-isolation-violation",
                target=report.target_id,
            )
        surfaced: SurfacedCertification = self._facade.surface(
            report, validation_evidence, version=version, certification_class=certification_class
        )
        record = CertificationConsoleRecord.create(
            report=surfaced.report,
            validation_evidence=surfaced.validation_evidence,
            decision=surfaced.decision,
            certification_evidence=surfaced.certification_evidence,
            owner_subject=principal.subject,
            request_ref=request_ref,
            workspace_id=workspace_id,
            project_id=project_id,
            tenant=tenant,
            metadata=metadata,
        )
        record = self._registry.record(record)
        newly_appended = record.certification_id not in self._ledger
        entry = self._ledger.append(record.record)
        self._emit(
            CERTIFICATION_SURFACED_EVENT,
            subject=record.record_id,
            payload={
                "certification_id": record.certification_id,
                "target_id": record.target_id,
                "blueprint_id": record.blueprint_id,
                "status": record.record.status.value,
                "certified": record.certified,
                "engine_contract": surfaced.engine_contract,
                "request_ref": request_ref,
                "tenant": tenant,
            },
        )
        certified_event = (
            CERTIFICATION_CERTIFIED_EVENT if record.certified else CERTIFICATION_NOT_CERTIFIED_EVENT
        )
        self._emit(
            certified_event,
            subject=record.record_id,
            payload={"target_id": record.target_id, "status": record.record.status.value},
        )
        if newly_appended:
            self._emit(
                CERTIFICATION_LEDGER_APPENDED_EVENT,
                subject=record.record_id,
                payload={
                    "sequence": entry.sequence,
                    "certification_id": entry.certification_id,
                    "entry_hash": entry.entry_hash,
                },
            )
            self._metric_counter(METRIC_LEDGER_APPENDS)
        self._metric_counter(METRIC_SURFACED)
        self._metric_counter(METRIC_CERTIFIED if record.certified else METRIC_NOT_CERTIFIED)
        if record.decision.advisory_failures:
            self._metric_counter(METRIC_ADVISORY)
        self._metric_histogram(
            METRIC_BLOCKING_FAILURES, float(len(record.decision.blocking_failures))
        )
        self._emit_health_change()
        return record

    # -- retrieval / resolution -------------------------------------------------

    def get_certification(self, record_id: str) -> CertificationConsoleRecord:
        """Retrieve a record by id (pure read; fail-closed on absent)."""
        return self._registry.get(record_id)

    def summary_of(self, record_id: str) -> CertificationSummary:
        """Return the certification summary for a record (pure read; fail-closed on absent)."""
        return self._registry.get(record_id).summary()

    def decision_of(self, record_id: str) -> CertificationDecision:
        """Return the certified decision for a record (pure read; fail-closed on absent)."""
        return self._registry.get(record_id).decision

    def list_certifications(
        self,
        session_id: str,
        *,
        now: int,
        tenant: str | None = None,
        target_id: str | None = None,
        blueprint_id: str | None = None,
        certification_id: str | None = None,
        request_ref: str | None = None,
        workspace_id: str | None = None,
        project_id: str | None = None,
        certified: bool | None = None,
    ) -> tuple[CertificationConsoleRecord, ...]:
        """List/filter the records a caller may see (authorized READ + isolation)."""
        principal = self._resolve_principal(session_id, now)
        if principal is None:
            return ()
        decision = self._authorization.authorize_principal(
            principal, CERTIFICATION_CONSOLE_GROUP, Permission.READ, tenant=tenant
        )
        if not decision.permitted:
            return ()
        return tuple(
            record
            for record in self._registry.discover(
                target_id=target_id,
                blueprint_id=blueprint_id,
                certification_id=certification_id,
                request_ref=request_ref,
                workspace_id=workspace_id,
                project_id=project_id,
                tenant=tenant,
                certified=certified,
            )
            if not tenants_isolated(principal.tenant, record.tenant)
        )

    # -- selection / inspection (record-scoped, audited) ------------------------

    def select_certification(
        self, session_id: str, record_id: str, *, now: int
    ) -> CertificationContext:
        """Select a record and return its runtime context (requires INSPECT; fail-closed)."""
        access = self._require_access(session_id, record_id, CertificationAction.INSPECT, now=now)
        record = self._registry.get(record_id)
        principal = self._authorization.principals.get(access.principal_id)
        self._registry.record_inspection(
            record_id, CertificationAction.INSPECT.value, access.principal_id, tick=now
        )
        self._emit(
            CERTIFICATION_INSPECTED_EVENT,
            subject=record_id,
            payload={"target_id": record.target_id, "principal_id": access.principal_id},
        )
        self._metric_counter(METRIC_INSPECTIONS)
        return CertificationContext.create(record, principal, is_owner=access.is_owner)

    def view_evidence(
        self, session_id: str, record_id: str, *, now: int
    ) -> CertificationEvidenceReference:
        """Render the evidence reference for a record (requires VIEW_EVIDENCE; fail-closed)."""
        access = self._require_access(
            session_id, record_id, CertificationAction.VIEW_EVIDENCE, now=now
        )
        record = self._registry.get(record_id)
        self._registry.record_inspection(
            record_id, CertificationAction.VIEW_EVIDENCE.value, access.principal_id, tick=now
        )
        reference = record.evidence_reference()
        self._emit(
            CERTIFICATION_EVIDENCE_RENDERED_EVENT,
            subject=record_id,
            payload={
                "target_id": record.target_id,
                "evidence_fingerprint": reference.evidence_fingerprint,
            },
        )
        return reference

    # -- ledger navigation / lineage --------------------------------------------

    def view_ledger_entry(
        self, session_id: str, record_id: str, *, now: int
    ) -> CertificationLedgerView:
        """Render the ledger entry for a record (requires VIEW_LEDGER; fail-closed)."""
        access = self._require_access(
            session_id, record_id, CertificationAction.VIEW_LEDGER, now=now
        )
        record = self._registry.get(record_id)
        self._registry.record_inspection(
            record_id, CertificationAction.VIEW_LEDGER.value, access.principal_id, tick=now
        )
        view = self._ledger.view(record.certification_id)
        self._emit(
            CERTIFICATION_LEDGER_VIEWED_EVENT,
            subject=record_id,
            payload={
                "certification_id": view.certification_id,
                "sequence": view.sequence,
                "entry_hash": view.entry_hash,
            },
        )
        return view

    def lineage_of(self, session_id: str, record_id: str, *, now: int) -> CertificationLineageView:
        """Render the ledger lineage for a record (requires VIEW_LINEAGE; fail-closed)."""
        access = self._require_access(
            session_id, record_id, CertificationAction.VIEW_LINEAGE, now=now
        )
        record = self._registry.get(record_id)
        self._registry.record_inspection(
            record_id, CertificationAction.VIEW_LINEAGE.value, access.principal_id, tick=now
        )
        lineage = self._ledger.lineage(record.certification_id)
        self._emit(
            CERTIFICATION_LINEAGE_RENDERED_EVENT,
            subject=record_id,
            payload={
                "certification_id": lineage.certification_id,
                "depth": lineage.depth,
                "parent": lineage.parent,
            },
        )
        return lineage

    # -- status tracking --------------------------------------------------------

    def status_of(self, record_id: str) -> DerivedCertificationStatus:
        """Derive a deterministic status for a record (pure read; fail-closed)."""
        return derive_status(self._registry.get(record_id).decision)

    def track_certification(
        self, session_id: str, record_id: str, *, now: int
    ) -> DerivedCertificationStatus:
        """Track a record's derived status (requires TRACK/READ access; fail-closed)."""
        access = self._require_access(session_id, record_id, CertificationAction.TRACK, now=now)
        self._registry.record_inspection(
            record_id, CertificationAction.TRACK.value, access.principal_id, tick=now
        )
        return self.status_of(record_id)

    # -- readiness --------------------------------------------------------------

    def readiness_of(self, record_id: str) -> CertificationReadiness:
        """Evaluate deterministic readiness for a record (pure read; fail-closed)."""
        return evaluate_readiness(self._registry.get(record_id).decision)

    def assess_readiness(
        self, session_id: str, record_id: str, *, now: int
    ) -> CertificationReadiness:
        """Evaluate readiness (requires EVALUATE_READINESS access; fail-closed)."""
        access = self._require_access(
            session_id, record_id, CertificationAction.EVALUATE_READINESS, now=now
        )
        self._registry.record_inspection(
            record_id, CertificationAction.EVALUATE_READINESS.value, access.principal_id, tick=now
        )
        readiness = self.readiness_of(record_id)
        self._emit(
            CERTIFICATION_READINESS_EVALUATED_EVENT,
            subject=record_id,
            payload={"target_id": readiness.target_id, "ready": readiness.ready},
        )
        return readiness

    # -- governance validation --------------------------------------------------

    def governance_of(self, record_id: str) -> GovernanceAssessment:
        """Evaluate certification governance for a record (pure read; fail-closed)."""
        return validate_governance(self._registry.get(record_id).decision)

    def assess_governance(
        self, session_id: str, record_id: str, *, now: int
    ) -> GovernanceAssessment:
        """Validate governance (requires VALIDATE_GOVERNANCE access; fail-closed)."""
        access = self._require_access(
            session_id, record_id, CertificationAction.VALIDATE_GOVERNANCE, now=now
        )
        self._registry.record_inspection(
            record_id, CertificationAction.VALIDATE_GOVERNANCE.value, access.principal_id, tick=now
        )
        assessment = self.governance_of(record_id)
        self._emit(
            CERTIFICATION_GOVERNANCE_VALIDATED_EVENT,
            subject=record_id,
            payload={
                "target_id": assessment.target_id,
                "compliant": assessment.compliant,
                "violations": [v.rule for v in assessment.violations],
            },
        )
        return assessment

    # -- traceability -----------------------------------------------------------

    def trace(self, session_id: str, record_id: str, *, now: int) -> CertificationTrace:
        """Return the certification trace edge for a record (requires TRACE; fail-closed)."""
        access = self._require_access(session_id, record_id, CertificationAction.TRACE, now=now)
        record = self._registry.get(record_id)
        self._registry.record_inspection(
            record_id, CertificationAction.TRACE.value, access.principal_id, tick=now
        )
        trace = record.trace()
        self._emit(CERTIFICATION_TRACED_EVENT, subject=record_id, payload=trace.edge())
        return trace

    # -- fidelity (machine-checkable, P6) ---------------------------------------

    def verify_fidelity(self, record_id: str) -> bool:
        """True iff the record's stored certification reproduces the certified output (P6)."""
        record = self._registry.get(record_id)
        return self._facade.verify_fidelity(
            record.record,
            record.report,
            record.validation_evidence,
            version=record.version,
            certification_class=record.decision.certification_class,
        )

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
        certification_id: str | None = None,
        request_ref: str | None = None,
        workspace_id: str | None = None,
        project_id: str | None = None,
        certified: bool | None = None,
    ) -> CertificationSearchResponse:
        """Run an authorization- and isolation-scoped certification search."""
        response = self._search.search(
            session_id,
            query,
            now=now,
            tenant=tenant,
            target_id=target_id,
            blueprint_id=blueprint_id,
            certification_id=certification_id,
            request_ref=request_ref,
            workspace_id=workspace_id,
            project_id=project_id,
            certified=certified,
        )
        self._emit(
            CERTIFICATION_SEARCHED_EVENT,
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
        self,
        session_id: str,
        record_id: str,
        metadata: CertificationRecordMetadata,
        *,
        now: int,
    ) -> CertificationConsoleRecord:
        """Attach descriptive console metadata to a record (requires INSPECT/READ).

        This mutates only the console's own descriptive annotation — never any surfaced
        certification datum (decision/record/evidence are immutable). Fail-closed.
        """
        self._require_access(session_id, record_id, CertificationAction.INSPECT, now=now)
        if not isinstance(metadata, CertificationRecordMetadata):
            raise CertificationServiceError("annotate requires a CertificationRecordMetadata")
        return self._registry.update_metadata(record_id, metadata)

    # -- access evaluation ------------------------------------------------------

    def evaluate_access(
        self,
        session_id: str,
        record_id: str,
        action: CertificationAction,
        *,
        now: int,
    ) -> CertificationAccess:
        """Evaluate composed console access (identity READ ∧ isolation).

        Denials are returned as data (``granted == False``); a malformed action or an
        unknown record raises. Every evaluation is emitted as a governed
        ``certification.record.access.evaluated`` event (PC-16).
        """
        if not isinstance(action, CertificationAction):
            raise CertificationServiceError("action must be a CertificationAction")
        permission = permission_for(action)
        record = self._registry.get(record_id)
        decision = self._authorization.authorize(
            session_id,
            CERTIFICATION_CONSOLE_GROUP,
            permission,
            now=now,
            tenant=record.tenant,
            resource=record_id,
        )
        access = self._compose_access(record, action, permission, decision)
        self._access_evaluations += 1
        self._emit(
            CERTIFICATION_ACCESS_EVENT,
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
        record: CertificationConsoleRecord,
        action: CertificationAction,
        permission: Permission,
        decision: AccessDecision,
    ) -> CertificationAccess:
        if not decision.permitted:
            return CertificationAccess.create(
                record_id=record.record_id,
                action=action,
                permission=permission,
                granted=False,
                reason=decision.reason,
                decision=decision,
            )
        principal = self._authorization.principals.get(decision.request.principal_id)
        if tenants_isolated(principal.tenant, record.tenant):
            return CertificationAccess.create(
                record_id=record.record_id,
                action=action,
                permission=permission,
                granted=False,
                reason="tenant-isolation-violation",
                decision=decision,
            )
        is_owner = principal.subject == record.owner_subject
        return CertificationAccess.create(
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
        """The certification-console runtime health endpoint (reuses the observability model)."""
        return self._health_registry.endpoint(self._health.probe())

    # -- evidence ---------------------------------------------------------------

    def evidence(self) -> CertificationConsoleEvidence:
        """Produce deterministic Certification Console Evidence over the runtime state."""
        report = self._health_registry.report(self._health.probe())
        census = self._registry.count_by_status()
        return CertificationConsoleEvidence.create(
            registry_fingerprint=self._registry.fingerprint(),
            ledger_fingerprint=self._ledger.fingerprint(),
            record_count=census["total"],
            certified_count=census["certified"],
            not_certified_count=census["not_certified"],
            ledger_entry_count=len(self._ledger),
            ledger_intact=self._ledger.verify(),
            inspection_count=len(self._registry.inspections),
            access_evaluation_count=self._access_evaluations,
            status_census=tuple(sorted(census.items())),
            health_status=report.status.value,
        )

    def to_dict(self) -> dict[str, Any]:
        census = self._registry.count_by_status()
        return {
            "record_count": census["total"],
            "certified_count": census["certified"],
            "not_certified_count": census["not_certified"],
            "ledger_entry_count": len(self._ledger),
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
        action: CertificationAction,
        *,
        now: int,
    ) -> CertificationAccess:
        access = self.evaluate_access(session_id, record_id, action, now=now)
        if not access.granted:
            raise CertificationAccessError(
                "certification console action denied",
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
                CERTIFICATION_HEALTH_CHANGED_EVENT,
                subject=_RUNTIME_SUBJECT,
                payload={"status": status},
            )

    def _emit(self, event_type: str, *, subject: str, payload: dict[str, Any]) -> None:
        if self._events is not None:
            self._events.publish(
                event_type,
                source="platform.certification.runtime",
                subject=subject,
                payload=payload,
            )

    def _metric_counter(self, name: str, **labels: str) -> None:
        if self._observability is not None:
            self._observability.metrics.counter(name, 1.0, **labels)

    def _metric_histogram(self, name: str, value: float, **labels: str) -> None:
        if self._observability is not None:
            self._observability.metrics.histogram(name, value, **labels)


def build_certification_console_service(
    *,
    authorization: AuthorizationService,
    observability: ObservabilityService | None = None,
    events: EventBus | None = None,
    registry: CertificationRegistry | None = None,
    facade: CertificationFacade | None = None,
    ledger: CertificationConsoleLedger | None = None,
) -> CertificationConsoleService:
    """Default, registry-driven composition of the Certification Console & Ledger Runtime.

    Wires the record registry, the read-only EC-1 certification façade (consumes
    ``engine.certification`` by reference), the append-only console ledger, certification
    search (over the supplied Identity ``authorization`` service), the console health
    probe and a health registry seeded with the console health checks, and — when
    supplied — the observability layer and event bus.
    """
    if not isinstance(authorization, AuthorizationService):
        raise CertificationServiceError(
            "build_certification_console_service requires an AuthorizationService"
        )
    record_registry = registry if registry is not None else CertificationRegistry()
    certification_facade = facade if facade is not None else CertificationFacade()
    console_ledger = ledger if ledger is not None else CertificationConsoleLedger()
    search = CertificationSearch(record_registry, authorization)
    health = CertificationHealth(record_registry, console_ledger, certification_facade)
    health_registry = HealthRegistry()
    for check in certification_console_health_checks():
        health_registry.register(check)
    return CertificationConsoleService(
        registry=record_registry,
        facade=certification_facade,
        ledger=console_ledger,
        authorization=authorization,
        search=search,
        health=health,
        health_registry=health_registry,
        observability=observability,
        events=events,
    )


__all__ = [
    "CERTIFICATION_SURFACED_EVENT",
    "CERTIFICATION_INSPECTED_EVENT",
    "CERTIFICATION_EVIDENCE_RENDERED_EVENT",
    "CERTIFICATION_LEDGER_VIEWED_EVENT",
    "CERTIFICATION_LINEAGE_RENDERED_EVENT",
    "CERTIFICATION_SEARCHED_EVENT",
    "CERTIFICATION_TRACED_EVENT",
    "CERTIFICATION_CERTIFIED_EVENT",
    "CERTIFICATION_NOT_CERTIFIED_EVENT",
    "CERTIFICATION_READINESS_EVALUATED_EVENT",
    "CERTIFICATION_GOVERNANCE_VALIDATED_EVENT",
    "CERTIFICATION_LEDGER_APPENDED_EVENT",
    "CERTIFICATION_HEALTH_CHANGED_EVENT",
    "CERTIFICATION_ACCESS_EVENT",
    "METRIC_SURFACED",
    "METRIC_CERTIFIED",
    "METRIC_NOT_CERTIFIED",
    "METRIC_ADVISORY",
    "METRIC_INSPECTIONS",
    "METRIC_LEDGER_APPENDS",
    "METRIC_BLOCKING_FAILURES",
    "CertificationAccess",
    "CertificationConsoleService",
    "build_certification_console_service",
]
