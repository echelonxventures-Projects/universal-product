"""EC2-TASK-000166 — Runtime Operation Orchestration & Registry (EC2-EPIC-012).

The **record-only orchestration** of governed runtime operations plus the deterministic,
append-only store of the operation records it produces. This is the runtime home of
Program Surface #11 *Runtime Operations* (PC-11): it composes the CERTIFIED-only
admission gate (:mod:`~platform.runtime_operations.guard`) with the read-only EC-1
descriptor façade (:mod:`~platform.runtime_operations.facade`) to *plan* a deploy or
rollback of a certified runtime unit — **generating the EC-1 descriptor by reference and
recording the governed operation**, implementing **no deployment logic of its own** (the
actual runtime execution stays inside EC-1 / the downstream runtime platform).

    * :class:`RuntimeOperationPlan` — the immutable, content-addressed outcome of planning
      one operation: the admitted operation record, its admission decision, and (for a
      rollback) its reversibility proof.
    * :class:`RuntimeOperationPlanner` — the pure orchestration engine. It is fail-closed:
      a non-CERTIFIED (or otherwise inadmissible) unit raises
      :class:`~platform.runtime_operations.errors.RuntimeAdmissionError` and **no
      descriptor is generated and no operation is recorded**.
    * :class:`InspectionEvent` / :class:`RuntimeOperationRegistry` — the append-only
      operation-record store and ordered inspection log (PC-16 audit / reconstruction).

The planner and registry consult no wall-clock and no external state; identical inputs
yield identical plans and identical record ids (P5). Nothing here writes to the certified
corpus (DP-03), and the registry exposes no update or delete of a record (append-only;
descriptive metadata is replaced immutably, preserving the content-addressed id).
"""

from __future__ import annotations

from dataclasses import dataclass
from platform.certification.contracts import CertificationConsoleRecord
from platform.foundation.contracts import content_hash
from platform.runtime_operations.contracts import (
    RuntimeOperationKind,
    RuntimeOperationMetadata,
    RuntimeOperationRecord,
)
from platform.runtime_operations.errors import (
    RuntimeAdmissionError,
    RuntimeOperationRecordError,
)
from platform.runtime_operations.facade import RuntimeFacade
from platform.runtime_operations.guard import AdmissionDecision, RuntimeAdmissionGuard
from platform.runtime_operations.reversibility import ReversibilityProof, prove_reversibility
from typing import Any

from engine.runtime.assembly import RuntimeUnit


@dataclass(frozen=True, slots=True)
class RuntimeOperationPlan:
    """An immutable, content-addressed outcome of planning one governed runtime operation."""

    plan_id: str
    kind: RuntimeOperationKind
    record: RuntimeOperationRecord
    admission: AdmissionDecision
    reversibility: ReversibilityProof | None

    @classmethod
    def create(
        cls,
        *,
        record: RuntimeOperationRecord,
        admission: AdmissionDecision,
        reversibility: ReversibilityProof | None,
    ) -> RuntimeOperationPlan:
        core = {
            "operation_id": record.operation_id,
            "kind": record.kind.value,
            "admission_id": admission.admission_id,
            "reversibility_id": reversibility.proof_id if reversibility is not None else None,
        }
        return cls(
            plan_id=f"UCOS-ROOP-{content_hash(core)[:16]}",
            kind=record.kind,
            record=record,
            admission=admission,
            reversibility=reversibility,
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "plan_id": self.plan_id,
            "kind": self.kind.value,
            "record": self.record.to_dict(),
            "admission": self.admission.to_dict(),
            "reversibility": (
                self.reversibility.to_dict() if self.reversibility is not None else None
            ),
        }

    def fingerprint(self) -> str:
        return content_hash(self.to_dict())


class RuntimeOperationPlanner:
    """The pure, fail-closed orchestration engine for governed runtime operations."""

    __slots__ = ("_facade", "_guard")

    def __init__(
        self,
        facade: RuntimeFacade | None = None,
        guard: RuntimeAdmissionGuard | None = None,
    ) -> None:
        if facade is not None and not isinstance(facade, RuntimeFacade):
            raise RuntimeOperationRecordError("planner requires a RuntimeFacade")
        if guard is not None and not isinstance(guard, RuntimeAdmissionGuard):
            raise RuntimeOperationRecordError("planner requires a RuntimeAdmissionGuard")
        self._facade = facade if facade is not None else RuntimeFacade()
        self._guard = guard if guard is not None else RuntimeAdmissionGuard()

    @property
    def facade(self) -> RuntimeFacade:
        return self._facade

    @property
    def guard(self) -> RuntimeAdmissionGuard:
        return self._guard

    def _admit(
        self,
        unit: RuntimeUnit,
        certification: CertificationConsoleRecord,
        kind: RuntimeOperationKind,
    ) -> AdmissionDecision:
        admission = self._guard.evaluate(unit, certification, kind)
        if not admission.admitted:
            raise RuntimeAdmissionError(
                "runtime operation admission denied (only CERTIFIED units are deployable)",
                reason=admission.reason,
                runtime_id=unit.runtime_id,
                kind=kind.value,
                blockers=list(admission.blockers),
            )
        return admission

    def plan_deploy(
        self,
        unit: RuntimeUnit,
        certification: CertificationConsoleRecord,
        *,
        owner_subject: str,
        environment: str | None = None,
        request_ref: str | None = None,
        workspace_id: str | None = None,
        project_id: str | None = None,
        tenant: str | None = None,
        metadata: RuntimeOperationMetadata | None = None,
    ) -> RuntimeOperationPlan:
        """Plan a governed deploy of a CERTIFIED unit (admit → generate descriptor → record)."""
        admission = self._admit(unit, certification, RuntimeOperationKind.DEPLOY)
        env = environment if environment is not None else unit.environment
        deployment = self._facade.deployment_descriptor(unit, environment=env)
        record = RuntimeOperationRecord.create(
            kind=RuntimeOperationKind.DEPLOY,
            unit=unit,
            certification=certification,
            deployment=deployment,
            owner_subject=owner_subject,
            environment=env,
            request_ref=request_ref,
            workspace_id=workspace_id,
            project_id=project_id,
            tenant=tenant,
            metadata=metadata,
        )
        return RuntimeOperationPlan.create(record=record, admission=admission, reversibility=None)

    def plan_rollback(
        self,
        unit: RuntimeUnit,
        certification: CertificationConsoleRecord,
        *,
        owner_subject: str,
        previous: RuntimeUnit | None = None,
        environment: str | None = None,
        request_ref: str | None = None,
        workspace_id: str | None = None,
        project_id: str | None = None,
        tenant: str | None = None,
        metadata: RuntimeOperationMetadata | None = None,
    ) -> RuntimeOperationPlan:
        """Plan a governed, reversible rollback of a CERTIFIED unit (IP-08)."""
        admission = self._admit(unit, certification, RuntimeOperationKind.ROLLBACK)
        env = environment if environment is not None else unit.environment
        rollback_descriptor = self._facade.rollback_descriptor(
            unit, previous=previous, environment=env
        )
        record = RuntimeOperationRecord.create(
            kind=RuntimeOperationKind.ROLLBACK,
            unit=unit,
            certification=certification,
            rollback=rollback_descriptor,
            owner_subject=owner_subject,
            environment=env,
            previous_unit=previous,
            request_ref=request_ref,
            workspace_id=workspace_id,
            project_id=project_id,
            tenant=tenant,
            metadata=metadata,
        )
        reversibility = prove_reversibility(rollback_descriptor)
        return RuntimeOperationPlan.create(
            record=record, admission=admission, reversibility=reversibility
        )


# --------------------------------------------------------------------------- #
# Append-only operation-record registry + inspection log.                     #
# --------------------------------------------------------------------------- #


@dataclass(frozen=True, slots=True)
class InspectionEvent:
    """An immutable, ordered record of a governed inspection over an operation record."""

    sequence: int
    operation_id: str
    action: str
    principal_id: str
    tick: int

    def to_dict(self) -> dict[str, Any]:
        return {
            "sequence": self.sequence,
            "operation_id": self.operation_id,
            "action": self.action,
            "principal_id": self.principal_id,
            "tick": self.tick,
        }


class RuntimeOperationRegistry:
    """A deterministic, append-only registry of runtime-operation records (record/discover)."""

    __slots__ = ("_by_id", "_log")

    def __init__(self) -> None:
        self._by_id: dict[str, RuntimeOperationRecord] = {}
        self._log: list[InspectionEvent] = []

    def record(self, record: RuntimeOperationRecord) -> RuntimeOperationRecord:
        """Register an operation record (idempotent by id; fail-closed on a conflict)."""
        if not isinstance(record, RuntimeOperationRecord):
            raise RuntimeOperationRecordError("record requires a RuntimeOperationRecord")
        existing = self._by_id.get(record.operation_id)
        if existing is not None:
            if existing.fingerprint() == record.fingerprint():
                return existing
            raise RuntimeOperationRecordError(
                "a distinct operation record already exists for this id",
                operation_id=record.operation_id,
            )
        self._by_id[record.operation_id] = record
        return record

    def __contains__(self, operation_id: str) -> bool:
        return operation_id in self._by_id

    def __len__(self) -> int:
        return len(self._by_id)

    def get(self, operation_id: str) -> RuntimeOperationRecord:
        """Resolve a record by id (fail-closed on absent)."""
        record = self._by_id.get(operation_id)
        if record is None:
            raise RuntimeOperationRecordError("no such operation record", operation_id=operation_id)
        return record

    @property
    def ids(self) -> tuple[str, ...]:
        """Every registered operation id in stable (sorted) order."""
        return tuple(sorted(self._by_id))

    def all(self) -> tuple[RuntimeOperationRecord, ...]:
        """Every registered record in stable (id) order."""
        return tuple(self._by_id[oid] for oid in self.ids)

    def by_runtime(self, runtime_id: str) -> tuple[RuntimeOperationRecord, ...]:
        """Every operation for a given runtime unit, in stable order."""
        return tuple(r for r in self.all() if r.runtime_id == runtime_id)

    def by_kind(self, kind: RuntimeOperationKind) -> tuple[RuntimeOperationRecord, ...]:
        """Every operation of a given kind, in stable order."""
        return tuple(r for r in self.all() if r.kind is kind)

    def discover(
        self,
        *,
        runtime_id: str | None = None,
        blueprint_id: str | None = None,
        certification_id: str | None = None,
        request_ref: str | None = None,
        workspace_id: str | None = None,
        project_id: str | None = None,
        tenant: str | None = None,
        environment: str | None = None,
        kind: RuntimeOperationKind | None = None,
    ) -> tuple[RuntimeOperationRecord, ...]:
        """Discover records, optionally scoped (stable order; pure read view).

        Authorization and isolation are applied by the service. ``tenant`` (when set)
        returns that tenant's records plus every untenanted (global) record.
        """
        records = self.all()
        if runtime_id is not None:
            records = tuple(r for r in records if r.runtime_id == runtime_id)
        if blueprint_id is not None:
            records = tuple(r for r in records if r.blueprint_id == blueprint_id)
        if certification_id is not None:
            records = tuple(
                r for r in records if r.certification.certification_id == certification_id
            )
        if request_ref is not None:
            records = tuple(r for r in records if r.request_ref == request_ref)
        if workspace_id is not None:
            records = tuple(r for r in records if r.workspace_id == workspace_id)
        if project_id is not None:
            records = tuple(r for r in records if r.project_id == project_id)
        if environment is not None:
            records = tuple(r for r in records if r.environment == environment)
        if kind is not None:
            records = tuple(r for r in records if r.kind is kind)
        if tenant is not None:
            records = tuple(r for r in records if r.tenant == tenant or r.tenant is None)
        return records

    def update_metadata(
        self, operation_id: str, metadata: RuntimeOperationMetadata
    ) -> RuntimeOperationRecord:
        """Replace a record's descriptive metadata immutably (the id is preserved)."""
        record = self.get(operation_id)
        updated = record.with_metadata(metadata)
        self._by_id[operation_id] = updated
        return updated

    def record_inspection(
        self, operation_id: str, action: str, principal_id: str, *, tick: int
    ) -> InspectionEvent:
        """Append an ordered inspection event to the append-only audit log (PC-16)."""
        if operation_id not in self._by_id:
            raise RuntimeOperationRecordError(
                "cannot record inspection for an unknown operation", operation_id=operation_id
            )
        event = InspectionEvent(
            sequence=len(self._log),
            operation_id=operation_id,
            action=action,
            principal_id=principal_id,
            tick=tick,
        )
        self._log.append(event)
        return event

    def inspections_of(self, operation_id: str) -> tuple[InspectionEvent, ...]:
        """Every recorded inspection for an operation, in order (reconstruction, PC-16)."""
        return tuple(e for e in self._log if e.operation_id == operation_id)

    @property
    def inspections(self) -> tuple[InspectionEvent, ...]:
        """An immutable snapshot of the append-only inspection log (in order)."""
        return tuple(self._log)

    def count_by_kind(self) -> dict[str, int]:
        """A deterministic deploy/rollback census over the registered records."""
        deploys = sum(1 for r in self._by_id.values() if r.kind is RuntimeOperationKind.DEPLOY)
        return {
            "total": len(self._by_id),
            "deploy": deploys,
            "rollback": len(self._by_id) - deploys,
        }

    def to_dict(self) -> dict[str, Any]:
        return {
            "operation_count": len(self._by_id),
            "operations": [self._by_id[oid].to_dict() for oid in self.ids],
            "kind_census": self.count_by_kind(),
        }

    def fingerprint(self) -> str:
        return content_hash(self.to_dict())


__all__ = [
    "RuntimeOperationPlan",
    "RuntimeOperationPlanner",
    "InspectionEvent",
    "RuntimeOperationRegistry",
]
