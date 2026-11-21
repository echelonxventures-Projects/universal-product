"""EC2-TASK-000172 — Runtime Operations Service (EC2-EPIC-012).

The single, governed **runtime-operations runtime composition point** (L8 Operations of
the Program architecture) that composes the whole Runtime Operations Runtime into one
entry point — the governed operate + inspection surface for Program Surface #11 *Runtime
Operations* (PC-11 runtime deploy/rollback operations + PC-13 search + PC-16 audit):

    RuntimeOperationRegistry · RuntimeOperationPlanner (RuntimeFacade over engine.runtime
    by reference + RuntimeAdmissionGuard) · DescriptorCatalog · RuntimeOperationLedger ·
    RuntimeOperationSearch · RuntimeOperationsHealth · (reused) AuthorizationService ·
    ObservabilityService

It is a strictly **additive**, **govern/record-only** layer: it authorizes only through
the certified Identity Layer (L7) on the existing ``runtime-operations`` capability group
— **no duplicate authorization or identity logic, no new authority, no new capability
group** — governs deploy/rollback **only from EC-1 descriptors** (produced read-only by
the L4 façade, never re-implemented — TP-01), admits **only CERTIFIED units** (consuming
certification status from the certified Certification Console by reference), observes only
through the Observability Layer (L8), and exposes **no mutation path** to any surfaced
descriptor, certification record, or ledger entry (the operation ledger is append-only by
construction). The actual runtime execution remains inside EC-1; this runtime governs and
records only. It re-implements none of the layers it composes, modifies neither EC-1 nor
any prior layer, and writes nothing to the certified corpus (DP-03).

Every operate/read is fail-closed and composes gates — **identity authorization** (RBAC
§3.2: ``EXECUTE`` for deploy/rollback, ``READ`` for inspection) and **tenant/workspace
isolation** (the reused rule, P3) — so cross-tenant access is refused in 100% of cases.
Because every governed action is published onto the Foundation event bus and appended to
the registry's inspection log, it is captured as append-only audit (PC-16 / OP-C3).

The service is deterministic: the same identity registrations, the same runtime units +
certifications, and the same ordered sequence of calls yield the same
:class:`RuntimeOperationEvidence` fingerprint (P5).
:func:`build_runtime_operations_service` provides the default wiring;
:func:`~platform.runtime_operations.bootstrap.bootstrap_runtime_operations` composes it
onto a :class:`~platform.foundation.bootstrap.PlatformContext`.
"""

from __future__ import annotations

from dataclasses import dataclass
from platform.certification.contracts import CertificationConsoleRecord
from platform.foundation.contracts import content_hash
from platform.foundation.events import EventBus
from platform.foundation.identity import Permission
from platform.identity.contracts import AccessDecision
from platform.identity.errors import IdentityError
from platform.identity.service import AuthorizationService
from platform.observability.health import HealthRegistry
from platform.observability.service import ObservabilityService
from platform.runtime_operations.context import RuntimeOperationContext
from platform.runtime_operations.contracts import (
    RUNTIME_OPERATIONS_GROUP,
    DeploymentDescriptorView,
    RollbackDescriptorView,
    RuntimeOperationAction,
    RuntimeOperationKind,
    RuntimeOperationMetadata,
    RuntimeOperationRecord,
    permission_for,
)
from platform.runtime_operations.descriptors import DescriptorCatalog
from platform.runtime_operations.errors import (
    RuntimeOperationAccessError,
    RuntimeOperationServiceError,
    RuntimeReversibilityError,
)
from platform.runtime_operations.health import (
    RuntimeOperationsHealth,
    runtime_operations_health_checks,
)
from platform.runtime_operations.ledger import (
    RuntimeOperationLedger,
    RuntimeOperationLedgerView,
    RuntimeOperationLineageView,
)
from platform.runtime_operations.operations import (
    RuntimeOperationPlanner,
    RuntimeOperationRegistry,
)
from platform.runtime_operations.reversibility import ReversibilityProof, prove_reversibility
from platform.runtime_operations.search import (
    RuntimeOperationSearch,
    RuntimeOperationSearchResponse,
)
from platform.runtime_operations.status import (
    DerivedRuntimeOperationStatus,
    GovernanceAssessment,
    derive_status,
    validate_governance,
)
from platform.workspace.isolation import tenants_isolated
from typing import Any

from engine.runtime.assembly import RuntimeUnit

#: Governed events published onto the Foundation event bus (observed as PC-16).
RUNTIME_DEPLOY_APPLIED_EVENT = "runtime.operation.deploy.applied"
RUNTIME_ROLLBACK_APPLIED_EVENT = "runtime.operation.rollback.applied"
RUNTIME_OPERATION_RECORDED_EVENT = "runtime.operation.recorded"
RUNTIME_LEDGER_APPENDED_EVENT = "runtime.operation.ledger.appended"
RUNTIME_OPERATION_INSPECTED_EVENT = "runtime.operation.inspected"
RUNTIME_DESCRIPTOR_INSPECTED_EVENT = "runtime.operation.descriptor.inspected"
RUNTIME_LEDGER_VIEWED_EVENT = "runtime.operation.ledger.viewed"
RUNTIME_LINEAGE_RENDERED_EVENT = "runtime.operation.lineage.rendered"
RUNTIME_OPERATION_SEARCHED_EVENT = "runtime.operation.searched"
RUNTIME_OPERATION_TRACKED_EVENT = "runtime.operation.tracked"
RUNTIME_REVERSIBILITY_VERIFIED_EVENT = "runtime.operation.reversibility.verified"
RUNTIME_GOVERNANCE_VALIDATED_EVENT = "runtime.operation.governance.validated"
RUNTIME_HEALTH_CHANGED_EVENT = "runtime.operations.health.changed"
RUNTIME_OPERATION_ACCESS_EVENT = "runtime.operation.access.evaluated"

#: The stable subject used for runtime-scoped (non-record) governed events.
_RUNTIME_SUBJECT = "platform.runtime_operations.runtime"

# --------------------------------------------------------------------------- #
# Observability metric names (PC-12 monitoring; reproducible, no wall-clock).  #
# --------------------------------------------------------------------------- #
METRIC_OPERATIONS = "runtime.operations.total"
METRIC_DEPLOYS = "runtime.operations.deploys"
METRIC_ROLLBACKS = "runtime.operations.rollbacks"
METRIC_LEDGER_APPENDS = "runtime.operations.ledger_appends"
METRIC_INSPECTIONS = "runtime.operations.inspections"
METRIC_CLOSURE_SIZE = "runtime.operations.closure_size"


@dataclass(frozen=True, slots=True)
class RuntimeOperationAccess:
    """An immutable, content-addressed runtime-operations access decision (fail-closed).

    Composes identity authorization (the verb's permission) and tenant/workspace isolation
    into a single verdict for one ``(principal, operation, action)`` request. ``is_owner``
    is carried for context.
    """

    operation_id: str
    principal_id: str
    action: RuntimeOperationAction
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
        operation_id: str,
        action: RuntimeOperationAction,
        permission: Permission,
        granted: bool,
        reason: str,
        decision: AccessDecision,
        is_owner: bool = False,
    ) -> RuntimeOperationAccess:
        principal_id = decision.request.principal_id
        core = {
            "operation_id": operation_id,
            "principal_id": principal_id,
            "action": action.value,
            "permission": permission.value,
            "granted": granted,
            "reason": reason,
            "is_owner": is_owner,
        }
        return cls(
            operation_id=operation_id,
            principal_id=principal_id,
            action=action,
            permission=permission,
            granted=granted,
            reason=reason,
            is_owner=is_owner,
            decision=decision,
            access_id=f"UCOS-ROAC-{content_hash(core)[:16]}",
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "access_id": self.access_id,
            "operation_id": self.operation_id,
            "principal_id": self.principal_id,
            "action": self.action.value,
            "permission": self.permission.value,
            "granted": self.granted,
            "reason": self.reason,
            "is_owner": self.is_owner,
            "decision": self.decision.to_dict(),
        }


@dataclass(frozen=True, slots=True)
class RuntimeOperationEvidence:
    """A deterministic, content-addressed record of runtime-operations runtime state."""

    registry_fingerprint: str
    ledger_fingerprint: str
    operation_count: int
    deploy_count: int
    rollback_count: int
    ledger_entry_count: int
    ledger_intact: bool
    inspection_count: int
    access_evaluation_count: int
    kind_census: tuple[tuple[str, int], ...]
    health_status: str
    evidence_id: str = ""

    @classmethod
    def create(
        cls,
        *,
        registry_fingerprint: str,
        ledger_fingerprint: str,
        operation_count: int,
        deploy_count: int,
        rollback_count: int,
        ledger_entry_count: int,
        ledger_intact: bool,
        inspection_count: int,
        access_evaluation_count: int,
        kind_census: tuple[tuple[str, int], ...],
        health_status: str,
    ) -> RuntimeOperationEvidence:
        core = {
            "registry_fingerprint": registry_fingerprint,
            "ledger_fingerprint": ledger_fingerprint,
            "operation_count": operation_count,
            "deploy_count": deploy_count,
            "rollback_count": rollback_count,
            "ledger_entry_count": ledger_entry_count,
            "ledger_intact": ledger_intact,
            "inspection_count": inspection_count,
            "access_evaluation_count": access_evaluation_count,
            "kind_census": [list(pair) for pair in kind_census],
            "health_status": health_status,
        }
        return cls(
            registry_fingerprint=registry_fingerprint,
            ledger_fingerprint=ledger_fingerprint,
            operation_count=operation_count,
            deploy_count=deploy_count,
            rollback_count=rollback_count,
            ledger_entry_count=ledger_entry_count,
            ledger_intact=ledger_intact,
            inspection_count=inspection_count,
            access_evaluation_count=access_evaluation_count,
            kind_census=kind_census,
            health_status=health_status,
            evidence_id=f"UCOS-ROEV-{content_hash(core)[:16]}",
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "evidence_id": self.evidence_id,
            "registry_fingerprint": self.registry_fingerprint,
            "ledger_fingerprint": self.ledger_fingerprint,
            "operation_count": self.operation_count,
            "deploy_count": self.deploy_count,
            "rollback_count": self.rollback_count,
            "ledger_entry_count": self.ledger_entry_count,
            "ledger_intact": self.ledger_intact,
            "inspection_count": self.inspection_count,
            "access_evaluation_count": self.access_evaluation_count,
            "kind_census": {name: count for name, count in self.kind_census},
            "health_status": self.health_status,
        }

    def fingerprint(self) -> str:
        return content_hash(self.to_dict())


class RuntimeOperationsService:
    """The governed L8 composition point for the UCOS Runtime Operations Runtime."""

    __slots__ = (
        "_registry",
        "_planner",
        "_descriptors",
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
        registry: RuntimeOperationRegistry,
        planner: RuntimeOperationPlanner,
        descriptors: DescriptorCatalog,
        ledger: RuntimeOperationLedger,
        authorization: AuthorizationService,
        search: RuntimeOperationSearch,
        health: RuntimeOperationsHealth,
        health_registry: HealthRegistry,
        observability: ObservabilityService | None = None,
        events: EventBus | None = None,
    ) -> None:
        if not isinstance(registry, RuntimeOperationRegistry):
            raise RuntimeOperationServiceError("a valid RuntimeOperationRegistry is required")
        if not isinstance(planner, RuntimeOperationPlanner):
            raise RuntimeOperationServiceError("a valid RuntimeOperationPlanner is required")
        if not isinstance(descriptors, DescriptorCatalog):
            raise RuntimeOperationServiceError("a valid DescriptorCatalog is required")
        if not isinstance(ledger, RuntimeOperationLedger):
            raise RuntimeOperationServiceError("a valid RuntimeOperationLedger is required")
        if not isinstance(authorization, AuthorizationService):
            raise RuntimeOperationServiceError("a valid AuthorizationService is required")
        if not isinstance(search, RuntimeOperationSearch):
            raise RuntimeOperationServiceError("a valid RuntimeOperationSearch is required")
        if not isinstance(health, RuntimeOperationsHealth):
            raise RuntimeOperationServiceError("a valid RuntimeOperationsHealth is required")
        if not isinstance(health_registry, HealthRegistry):
            raise RuntimeOperationServiceError("a valid HealthRegistry is required")
        if observability is not None and not isinstance(observability, ObservabilityService):
            raise RuntimeOperationServiceError(
                "observability must be an ObservabilityService when provided"
            )
        if events is not None and not isinstance(events, EventBus):
            raise RuntimeOperationServiceError("events must be an EventBus when provided")
        self._registry = registry
        self._planner = planner
        self._descriptors = descriptors
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
    def registry(self) -> RuntimeOperationRegistry:
        return self._registry

    @property
    def planner(self) -> RuntimeOperationPlanner:
        return self._planner

    @property
    def descriptors(self) -> DescriptorCatalog:
        return self._descriptors

    @property
    def ledger(self) -> RuntimeOperationLedger:
        return self._ledger

    @property
    def authorization(self) -> AuthorizationService:
        return self._authorization

    @property
    def health(self) -> RuntimeOperationsHealth:
        return self._health

    @property
    def observability(self) -> ObservabilityService | None:
        return self._observability

    @property
    def access_evaluation_count(self) -> int:
        return self._access_evaluations

    # -- governed operate (deploy / rollback; require EXECUTE + CERTIFIED) ------

    def deploy(
        self,
        session_id: str,
        unit: RuntimeUnit,
        certification: CertificationConsoleRecord,
        *,
        now: int,
        environment: str | None = None,
        request_ref: str | None = None,
        workspace_id: str | None = None,
        project_id: str | None = None,
        tenant: str | None = None,
        metadata: RuntimeOperationMetadata | None = None,
    ) -> RuntimeOperationRecord:
        """Govern a deploy of a CERTIFIED unit from the EC-1 deployment descriptor.

        Requires identity EXECUTE on ``runtime-operations`` (with the unit's tenant) and
        cross-tenant isolation clearance, then CERTIFIED-only admission. The deployment
        descriptor is reproduced read-only by the L4 façade (never re-implemented); the
        operation record is content-addressed and idempotent, and appended to the
        append-only ledger. Raises :class:`RuntimeOperationAccessError` on any access
        denial and :class:`~platform.runtime_operations.errors.RuntimeAdmissionError` on a
        non-CERTIFIED / inadmissible unit (fail-closed).
        """
        principal = self._authorize_operate(
            session_id, unit, RuntimeOperationAction.DEPLOY, now=now, tenant=tenant
        )
        plan = self._planner.plan_deploy(
            unit,
            certification,
            owner_subject=principal.subject,
            environment=environment,
            request_ref=request_ref,
            workspace_id=workspace_id,
            project_id=project_id,
            tenant=tenant,
            metadata=metadata,
        )
        return self._record_operation(plan, RUNTIME_DEPLOY_APPLIED_EVENT, tenant=tenant)

    def rollback(
        self,
        session_id: str,
        unit: RuntimeUnit,
        certification: CertificationConsoleRecord,
        *,
        now: int,
        previous: RuntimeUnit | None = None,
        environment: str | None = None,
        request_ref: str | None = None,
        workspace_id: str | None = None,
        project_id: str | None = None,
        tenant: str | None = None,
        metadata: RuntimeOperationMetadata | None = None,
    ) -> RuntimeOperationRecord:
        """Govern a reversible rollback of a CERTIFIED unit from the EC-1 rollback descriptor.

        Requires identity EXECUTE + isolation + CERTIFIED-only admission; the reversible
        rollback descriptor (IP-08) is reproduced read-only by the L4 façade. Fail-closed.
        """
        principal = self._authorize_operate(
            session_id, unit, RuntimeOperationAction.ROLLBACK, now=now, tenant=tenant
        )
        plan = self._planner.plan_rollback(
            unit,
            certification,
            owner_subject=principal.subject,
            previous=previous,
            environment=environment,
            request_ref=request_ref,
            workspace_id=workspace_id,
            project_id=project_id,
            tenant=tenant,
            metadata=metadata,
        )
        return self._record_operation(plan, RUNTIME_ROLLBACK_APPLIED_EVENT, tenant=tenant)

    def _authorize_operate(
        self,
        session_id: str,
        unit: RuntimeUnit,
        action: RuntimeOperationAction,
        *,
        now: int,
        tenant: str | None,
    ):
        if not isinstance(unit, RuntimeUnit):
            raise RuntimeOperationServiceError("operate requires a RuntimeUnit")
        decision = self._authorization.authorize(
            session_id,
            RUNTIME_OPERATIONS_GROUP,
            permission_for(action),
            now=now,
            tenant=tenant,
            resource=unit.runtime_id,
        )
        if not decision.permitted:
            raise RuntimeOperationAccessError(
                "runtime operation denied",
                reason=decision.reason,
                runtime_id=unit.runtime_id,
                action=action.value,
            )
        principal = self._authorization.principals.get(decision.request.principal_id)
        if tenants_isolated(principal.tenant, tenant):
            raise RuntimeOperationAccessError(
                "cross-tenant runtime operation denied",
                reason="tenant-isolation-violation",
                runtime_id=unit.runtime_id,
                action=action.value,
            )
        return principal

    def _record_operation(
        self, plan, applied_event: str, *, tenant: str | None
    ) -> RuntimeOperationRecord:
        record = self._registry.record(plan.record)
        newly_appended = record.operation_id not in self._ledger
        entry = self._ledger.append(record)
        self._emit(
            applied_event,
            subject=record.operation_id,
            payload={
                "runtime_id": record.runtime_id,
                "blueprint_id": record.blueprint_id,
                "environment": record.environment,
                "certification_id": record.certification.certification_id,
                "certified": record.certified,
                "reversible": record.reversible,
                "descriptor_fingerprint": record.descriptor_fingerprint(),
                "tenant": tenant,
            },
        )
        self._emit(
            RUNTIME_OPERATION_RECORDED_EVENT,
            subject=record.operation_id,
            payload={"runtime_id": record.runtime_id, "kind": record.kind.value},
        )
        if newly_appended:
            self._emit(
                RUNTIME_LEDGER_APPENDED_EVENT,
                subject=record.operation_id,
                payload={
                    "sequence": entry.sequence,
                    "operation_id": entry.operation_id,
                    "entry_hash": entry.entry_hash,
                },
            )
            self._metric_counter(METRIC_LEDGER_APPENDS)
        self._metric_counter(METRIC_OPERATIONS)
        self._metric_counter(
            METRIC_DEPLOYS if record.kind is RuntimeOperationKind.DEPLOY else METRIC_ROLLBACKS
        )
        self._metric_histogram(METRIC_CLOSURE_SIZE, float(len(record.unit.dependency_closure)))
        self._emit_health_change()
        return record

    # -- retrieval / resolution -------------------------------------------------

    def get_operation(self, operation_id: str) -> RuntimeOperationRecord:
        """Retrieve a record by id (pure read; fail-closed on absent)."""
        return self._registry.get(operation_id)

    def status_of(self, operation_id: str) -> DerivedRuntimeOperationStatus:
        """Derive a deterministic status for a record (pure read; fail-closed)."""
        return derive_status(self._registry.get(operation_id))

    def governance_of(self, operation_id: str) -> GovernanceAssessment:
        """Evaluate operation governance for a record (pure read; fail-closed)."""
        return validate_governance(self._registry.get(operation_id))

    def reversibility_of(self, operation_id: str) -> ReversibilityProof:
        """Prove reversibility for a rollback record (pure read; fail-closed)."""
        record = self._registry.get(operation_id)
        if record.kind is not RuntimeOperationKind.ROLLBACK or record.rollback is None:
            raise RuntimeReversibilityError(
                "only rollback operations are reversibility-provable",
                operation_id=operation_id,
            )
        return prove_reversibility(record.rollback)

    def discover_operations(
        self,
        session_id: str,
        *,
        now: int,
        tenant: str | None = None,
        runtime_id: str | None = None,
        blueprint_id: str | None = None,
        certification_id: str | None = None,
        request_ref: str | None = None,
        workspace_id: str | None = None,
        project_id: str | None = None,
        environment: str | None = None,
        kind: RuntimeOperationKind | None = None,
    ) -> tuple[RuntimeOperationRecord, ...]:
        """Discover/filter the operations a caller may see (authorized READ + isolation)."""
        principal = self._resolve_principal(session_id, now)
        if principal is None:
            return ()
        decision = self._authorization.authorize_principal(
            principal, RUNTIME_OPERATIONS_GROUP, Permission.READ, tenant=tenant
        )
        if not decision.permitted:
            return ()
        return tuple(
            record
            for record in self._registry.discover(
                runtime_id=runtime_id,
                blueprint_id=blueprint_id,
                certification_id=certification_id,
                request_ref=request_ref,
                workspace_id=workspace_id,
                project_id=project_id,
                environment=environment,
                tenant=tenant,
                kind=kind,
            )
            if not tenants_isolated(principal.tenant, record.tenant)
        )

    # -- selection / inspection (record-scoped, audited) ------------------------

    def select_operation(
        self, session_id: str, operation_id: str, *, now: int
    ) -> RuntimeOperationContext:
        """Select a record and return its runtime context (requires INSPECT; fail-closed)."""
        access = self._require_access(
            session_id, operation_id, RuntimeOperationAction.INSPECT, now=now
        )
        record = self._registry.get(operation_id)
        principal = self._authorization.principals.get(access.principal_id)
        self._registry.record_inspection(
            operation_id, RuntimeOperationAction.INSPECT.value, access.principal_id, tick=now
        )
        self._emit(
            RUNTIME_OPERATION_INSPECTED_EVENT,
            subject=operation_id,
            payload={"runtime_id": record.runtime_id, "principal_id": access.principal_id},
        )
        self._metric_counter(METRIC_INSPECTIONS)
        return RuntimeOperationContext.create(record, principal, is_owner=access.is_owner)

    def inspect_descriptor(
        self, session_id: str, operation_id: str, *, now: int
    ) -> DeploymentDescriptorView | RollbackDescriptorView:
        """Inspect an operation's governing EC-1 descriptor (requires INSPECT; fail-closed)."""
        access = self._require_access(
            session_id, operation_id, RuntimeOperationAction.INSPECT, now=now
        )
        self._registry.record_inspection(
            operation_id, RuntimeOperationAction.INSPECT.value, access.principal_id, tick=now
        )
        view = self._descriptors.inspect(operation_id)
        self._emit(
            RUNTIME_DESCRIPTOR_INSPECTED_EVENT,
            subject=operation_id,
            payload={
                "runtime_id": view.runtime_id,
                "descriptor_fingerprint": view.descriptor_fingerprint,
            },
        )
        return view

    # -- ledger navigation / lineage --------------------------------------------

    def view_ledger_entry(
        self, session_id: str, operation_id: str, *, now: int
    ) -> RuntimeOperationLedgerView:
        """Render the ledger entry for an operation (requires VIEW_LEDGER; fail-closed)."""
        access = self._require_access(
            session_id, operation_id, RuntimeOperationAction.VIEW_LEDGER, now=now
        )
        self._registry.record_inspection(
            operation_id, RuntimeOperationAction.VIEW_LEDGER.value, access.principal_id, tick=now
        )
        view = self._ledger.view(operation_id)
        self._emit(
            RUNTIME_LEDGER_VIEWED_EVENT,
            subject=operation_id,
            payload={
                "operation_id": view.operation_id,
                "sequence": view.sequence,
                "entry_hash": view.entry_hash,
            },
        )
        return view

    def lineage_of(
        self, session_id: str, operation_id: str, *, now: int
    ) -> RuntimeOperationLineageView:
        """Render the ledger lineage for an operation (requires VIEW_LINEAGE; fail-closed)."""
        access = self._require_access(
            session_id, operation_id, RuntimeOperationAction.VIEW_LINEAGE, now=now
        )
        self._registry.record_inspection(
            operation_id, RuntimeOperationAction.VIEW_LINEAGE.value, access.principal_id, tick=now
        )
        lineage = self._ledger.lineage(operation_id)
        self._emit(
            RUNTIME_LINEAGE_RENDERED_EVENT,
            subject=operation_id,
            payload={
                "operation_id": lineage.operation_id,
                "depth": lineage.depth,
                "parent": lineage.parent,
            },
        )
        return lineage

    # -- status tracking --------------------------------------------------------

    def track_operation(
        self, session_id: str, operation_id: str, *, now: int
    ) -> DerivedRuntimeOperationStatus:
        """Track a record's derived status (requires TRACK/READ access; fail-closed)."""
        access = self._require_access(
            session_id, operation_id, RuntimeOperationAction.TRACK, now=now
        )
        self._registry.record_inspection(
            operation_id, RuntimeOperationAction.TRACK.value, access.principal_id, tick=now
        )
        status = self.status_of(operation_id)
        self._emit(
            RUNTIME_OPERATION_TRACKED_EVENT,
            subject=operation_id,
            payload={"runtime_id": status.runtime_id, "posture": status.posture.value},
        )
        return status

    # -- reversibility (IP-08) --------------------------------------------------

    def verify_reversibility(
        self, session_id: str, operation_id: str, *, now: int
    ) -> ReversibilityProof:
        """Verify rollback reversibility (requires VERIFY_REVERSIBILITY access; fail-closed)."""
        access = self._require_access(
            session_id, operation_id, RuntimeOperationAction.VERIFY_REVERSIBILITY, now=now
        )
        self._registry.record_inspection(
            operation_id,
            RuntimeOperationAction.VERIFY_REVERSIBILITY.value,
            access.principal_id,
            tick=now,
        )
        proof = self.reversibility_of(operation_id)
        self._emit(
            RUNTIME_REVERSIBILITY_VERIFIED_EVENT,
            subject=operation_id,
            payload={"runtime_id": proof.runtime_id, "reversible": proof.reversible},
        )
        return proof

    # -- governance validation --------------------------------------------------

    def assess_governance(
        self, session_id: str, operation_id: str, *, now: int
    ) -> GovernanceAssessment:
        """Validate governance (requires VALIDATE_GOVERNANCE access; fail-closed)."""
        access = self._require_access(
            session_id, operation_id, RuntimeOperationAction.VALIDATE_GOVERNANCE, now=now
        )
        self._registry.record_inspection(
            operation_id,
            RuntimeOperationAction.VALIDATE_GOVERNANCE.value,
            access.principal_id,
            tick=now,
        )
        assessment = self.governance_of(operation_id)
        self._emit(
            RUNTIME_GOVERNANCE_VALIDATED_EVENT,
            subject=operation_id,
            payload={
                "runtime_id": assessment.runtime_id,
                "compliant": assessment.compliant,
                "violations": [v.rule for v in assessment.violations],
            },
        )
        return assessment

    # -- fidelity (machine-checkable, P6) ---------------------------------------

    def verify_fidelity(self, operation_id: str) -> bool:
        """True iff the operation's stored descriptor reproduces the EC-1 output (P6)."""
        record = self._registry.get(operation_id)
        if record.kind is RuntimeOperationKind.DEPLOY:
            return self._planner.facade.verify_deployment_fidelity(
                record.deployment, record.unit, environment=record.environment
            )
        return self._planner.facade.verify_rollback_fidelity(
            record.rollback,
            record.unit,
            previous=record.previous_unit,
            environment=record.environment,
        )

    # -- search -----------------------------------------------------------------

    def search(
        self,
        session_id: str,
        query: str,
        *,
        now: int,
        tenant: str | None = None,
        runtime_id: str | None = None,
        blueprint_id: str | None = None,
        certification_id: str | None = None,
        request_ref: str | None = None,
        workspace_id: str | None = None,
        project_id: str | None = None,
        environment: str | None = None,
        kind: RuntimeOperationKind | None = None,
    ) -> RuntimeOperationSearchResponse:
        """Run an authorization- and isolation-scoped runtime-operation search."""
        response = self._search.search(
            session_id,
            query,
            now=now,
            tenant=tenant,
            runtime_id=runtime_id,
            blueprint_id=blueprint_id,
            certification_id=certification_id,
            request_ref=request_ref,
            workspace_id=workspace_id,
            project_id=project_id,
            environment=environment,
            kind=kind,
        )
        self._emit(
            RUNTIME_OPERATION_SEARCHED_EVENT,
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
        operation_id: str,
        metadata: RuntimeOperationMetadata,
        *,
        now: int,
    ) -> RuntimeOperationRecord:
        """Attach descriptive console metadata to a record (requires INSPECT/READ).

        This mutates only the runtime's own descriptive annotation — never any surfaced
        descriptor or certification datum (all immutable). Fail-closed.
        """
        self._require_access(session_id, operation_id, RuntimeOperationAction.INSPECT, now=now)
        if not isinstance(metadata, RuntimeOperationMetadata):
            raise RuntimeOperationServiceError("annotate requires a RuntimeOperationMetadata")
        return self._registry.update_metadata(operation_id, metadata)

    # -- access evaluation ------------------------------------------------------

    def evaluate_access(
        self,
        session_id: str,
        operation_id: str,
        action: RuntimeOperationAction,
        *,
        now: int,
    ) -> RuntimeOperationAccess:
        """Evaluate composed runtime-operations access (identity permission ∧ isolation).

        Denials are returned as data (``granted == False``); a malformed action or an
        unknown record raises. Every evaluation is emitted as a governed
        ``runtime.operation.access.evaluated`` event (PC-16).
        """
        if not isinstance(action, RuntimeOperationAction):
            raise RuntimeOperationServiceError("action must be a RuntimeOperationAction")
        permission = permission_for(action)
        record = self._registry.get(operation_id)
        decision = self._authorization.authorize(
            session_id,
            RUNTIME_OPERATIONS_GROUP,
            permission,
            now=now,
            tenant=record.tenant,
            resource=operation_id,
        )
        access = self._compose_access(record, action, permission, decision)
        self._access_evaluations += 1
        self._emit(
            RUNTIME_OPERATION_ACCESS_EVENT,
            subject=access.principal_id,
            payload={
                "operation_id": operation_id,
                "action": action.value,
                "granted": access.granted,
                "reason": access.reason,
            },
        )
        return access

    def _compose_access(
        self,
        record: RuntimeOperationRecord,
        action: RuntimeOperationAction,
        permission: Permission,
        decision: AccessDecision,
    ) -> RuntimeOperationAccess:
        if not decision.permitted:
            return RuntimeOperationAccess.create(
                operation_id=record.operation_id,
                action=action,
                permission=permission,
                granted=False,
                reason=decision.reason,
                decision=decision,
            )
        principal = self._authorization.principals.get(decision.request.principal_id)
        if tenants_isolated(principal.tenant, record.tenant):
            return RuntimeOperationAccess.create(
                operation_id=record.operation_id,
                action=action,
                permission=permission,
                granted=False,
                reason="tenant-isolation-violation",
                decision=decision,
            )
        is_owner = principal.subject == record.owner_subject
        return RuntimeOperationAccess.create(
            operation_id=record.operation_id,
            action=action,
            permission=permission,
            granted=True,
            reason="granted",
            decision=decision,
            is_owner=is_owner,
        )

    # -- health integration -----------------------------------------------------

    def health_report(self) -> dict[str, Any]:
        """The runtime-operations runtime health endpoint (reuses the observability model)."""
        return self._health_registry.endpoint(self._health.probe())

    # -- evidence ---------------------------------------------------------------

    def evidence(self) -> RuntimeOperationEvidence:
        """Produce deterministic Runtime Operation Evidence over the runtime state."""
        report = self._health_registry.report(self._health.probe())
        census = self._registry.count_by_kind()
        return RuntimeOperationEvidence.create(
            registry_fingerprint=self._registry.fingerprint(),
            ledger_fingerprint=self._ledger.fingerprint(),
            operation_count=census["total"],
            deploy_count=census["deploy"],
            rollback_count=census["rollback"],
            ledger_entry_count=len(self._ledger),
            ledger_intact=self._ledger.verify(),
            inspection_count=len(self._registry.inspections),
            access_evaluation_count=self._access_evaluations,
            kind_census=tuple(sorted(census.items())),
            health_status=report.status.value,
        )

    def to_dict(self) -> dict[str, Any]:
        census = self._registry.count_by_kind()
        return {
            "operation_count": census["total"],
            "deploy_count": census["deploy"],
            "rollback_count": census["rollback"],
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
        operation_id: str,
        action: RuntimeOperationAction,
        *,
        now: int,
    ) -> RuntimeOperationAccess:
        access = self.evaluate_access(session_id, operation_id, action, now=now)
        if not access.granted:
            raise RuntimeOperationAccessError(
                "runtime operations action denied",
                reason=access.reason,
                operation_id=operation_id,
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
                RUNTIME_HEALTH_CHANGED_EVENT,
                subject=_RUNTIME_SUBJECT,
                payload={"status": status},
            )

    def _emit(self, event_type: str, *, subject: str, payload: dict[str, Any]) -> None:
        if self._events is not None:
            self._events.publish(
                event_type,
                source="platform.runtime_operations.runtime",
                subject=subject,
                payload=payload,
            )

    def _metric_counter(self, name: str, **labels: str) -> None:
        if self._observability is not None:
            self._observability.metrics.counter(name, 1.0, **labels)

    def _metric_histogram(self, name: str, value: float, **labels: str) -> None:
        if self._observability is not None:
            self._observability.metrics.histogram(name, value, **labels)


def build_runtime_operations_service(
    *,
    authorization: AuthorizationService,
    observability: ObservabilityService | None = None,
    events: EventBus | None = None,
    registry: RuntimeOperationRegistry | None = None,
    planner: RuntimeOperationPlanner | None = None,
    ledger: RuntimeOperationLedger | None = None,
) -> RuntimeOperationsService:
    """Default, registry-driven composition of the Runtime Operations Runtime.

    Wires the operation registry, the record-only orchestration planner (which holds the
    read-only EC-1 runtime façade + the CERTIFIED-only admission guard), the descriptor
    discovery/inspection catalog, the append-only hash-chained operation ledger, operation
    search (over the supplied Identity ``authorization`` service), the runtime health probe
    and a health registry seeded with the runtime health checks, and — when supplied — the
    observability layer and event bus.
    """
    if not isinstance(authorization, AuthorizationService):
        raise RuntimeOperationServiceError(
            "build_runtime_operations_service requires an AuthorizationService"
        )
    operation_registry = registry if registry is not None else RuntimeOperationRegistry()
    operation_planner = planner if planner is not None else RuntimeOperationPlanner()
    operation_ledger = ledger if ledger is not None else RuntimeOperationLedger()
    descriptors = DescriptorCatalog(operation_registry)
    search = RuntimeOperationSearch(operation_registry, authorization)
    health = RuntimeOperationsHealth(operation_registry, operation_ledger, operation_planner.facade)
    health_registry = HealthRegistry()
    for check in runtime_operations_health_checks():
        health_registry.register(check)
    return RuntimeOperationsService(
        registry=operation_registry,
        planner=operation_planner,
        descriptors=descriptors,
        ledger=operation_ledger,
        authorization=authorization,
        search=search,
        health=health,
        health_registry=health_registry,
        observability=observability,
        events=events,
    )


__all__ = [
    "RUNTIME_DEPLOY_APPLIED_EVENT",
    "RUNTIME_ROLLBACK_APPLIED_EVENT",
    "RUNTIME_OPERATION_RECORDED_EVENT",
    "RUNTIME_LEDGER_APPENDED_EVENT",
    "RUNTIME_OPERATION_INSPECTED_EVENT",
    "RUNTIME_DESCRIPTOR_INSPECTED_EVENT",
    "RUNTIME_LEDGER_VIEWED_EVENT",
    "RUNTIME_LINEAGE_RENDERED_EVENT",
    "RUNTIME_OPERATION_SEARCHED_EVENT",
    "RUNTIME_OPERATION_TRACKED_EVENT",
    "RUNTIME_REVERSIBILITY_VERIFIED_EVENT",
    "RUNTIME_GOVERNANCE_VALIDATED_EVENT",
    "RUNTIME_HEALTH_CHANGED_EVENT",
    "RUNTIME_OPERATION_ACCESS_EVENT",
    "METRIC_OPERATIONS",
    "METRIC_DEPLOYS",
    "METRIC_ROLLBACKS",
    "METRIC_LEDGER_APPENDS",
    "METRIC_INSPECTIONS",
    "METRIC_CLOSURE_SIZE",
    "RuntimeOperationAccess",
    "RuntimeOperationEvidence",
    "RuntimeOperationsService",
    "build_runtime_operations_service",
]
