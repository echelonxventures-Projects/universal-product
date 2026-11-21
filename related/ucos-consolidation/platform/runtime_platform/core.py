"""EPIC-007 (Terminal T7) — Runtime Core / Kernel (Universal Runtime Platform).

The **Runtime Core** — the minimal deterministic kernel that wires the runtime plane's
substrate together and owns the single **admission gate**. It composes (never
re-implements):

    * the technology-neutral
      :class:`~platform.runtime_platform.infrastructure.RuntimeInfrastructure`
      (placement + capacity posture);
    * the model-only :class:`~platform.runtime_platform.execution.ExecutionEngine`;
    * the deterministic :func:`~platform.runtime_platform.scheduling.schedule` scheduler;
    * the append-only :class:`~platform.runtime_platform.registry.ExecutionRegistry`;
    * the governed :class:`~platform.runtime_platform.events.RuntimeEventBus`;
    * the :class:`~platform.runtime_platform.services.RuntimeServiceCatalog`.

It owns the **fail-closed admission gate** (:meth:`RuntimeKernel.admit`): only a workload
whose upstream :class:`~platform.runtime_platform.contracts.WorkloadAttestation` is both
VALIDATED and CERTIFIED may be admitted — the concrete realization of *consuming*
Validation and Certification (Registry/Knowledge/Measurement references are recorded as
lineage). :meth:`RuntimeKernel.submit` and :meth:`RuntimeKernel.submit_batch` drive the
admit → schedule → model-run → register → emit path deterministically; the kernel starts
no server and runs nothing live.
"""

from __future__ import annotations

from collections.abc import Iterable
from platform.foundation.contracts import content_hash
from platform.runtime_platform.contracts import CONSUMED_CONTRACTS, WorkloadAttestation
from platform.runtime_platform.errors import RuntimeAdmissionError, RuntimeKernelError
from platform.runtime_platform.events import (
    CAPACITY_CHANGED,
    EXECUTION_COMPENSATED,
    EXECUTION_FAILED,
    EXECUTION_REGISTERED,
    EXECUTION_SCHEDULED,
    EXECUTION_STARTED,
    EXECUTION_SUCCEEDED,
    WORKLOAD_PLACED,
    RuntimeEventBus,
)
from platform.runtime_platform.execution import ExecutionEngine, ExecutionRecord, ExecutionRequest
from platform.runtime_platform.infrastructure import RuntimeInfrastructure
from platform.runtime_platform.lifecycle import COMPENSATED, FAILED, SUCCEEDED
from platform.runtime_platform.registry import ExecutionRegistry
from platform.runtime_platform.scheduling import ExecutionSchedule, schedule
from platform.runtime_platform.services import RuntimeServiceCatalog
from typing import Any

#: The recorded kernel format.
RUNTIME_KERNEL_FORMAT = "ucos-runtime-kernel/1.0.0"

#: Maps a settled final state to its governed terminal event category.
_TERMINAL_EVENT: dict[str, str] = {
    SUCCEEDED: EXECUTION_SUCCEEDED,
    FAILED: EXECUTION_FAILED,
    COMPENSATED: EXECUTION_COMPENSATED,
}


class RuntimeKernel:
    """The deterministic Universal Runtime Platform kernel + fail-closed admission gate."""

    __slots__ = (
        "_infrastructure",
        "_engine",
        "_registry",
        "_events",
        "_services",
        "_admissions",
    )

    def __init__(
        self,
        *,
        infrastructure: RuntimeInfrastructure | None = None,
        engine: ExecutionEngine | None = None,
        registry: ExecutionRegistry | None = None,
        events: RuntimeEventBus | None = None,
        services: RuntimeServiceCatalog | None = None,
    ) -> None:
        self._infrastructure = (
            infrastructure if infrastructure is not None else RuntimeInfrastructure()
        )
        if not isinstance(self._infrastructure, RuntimeInfrastructure):
            raise RuntimeKernelError("kernel requires a RuntimeInfrastructure")
        self._engine = engine if engine is not None else ExecutionEngine(self._infrastructure)
        if not isinstance(self._engine, ExecutionEngine):
            raise RuntimeKernelError("kernel requires an ExecutionEngine")
        self._registry = registry if registry is not None else ExecutionRegistry()
        if not isinstance(self._registry, ExecutionRegistry):
            raise RuntimeKernelError("kernel requires an ExecutionRegistry")
        self._events = events if events is not None else RuntimeEventBus()
        if not isinstance(self._events, RuntimeEventBus):
            raise RuntimeKernelError("kernel requires a RuntimeEventBus")
        self._services = services if services is not None else RuntimeServiceCatalog()
        if not isinstance(self._services, RuntimeServiceCatalog):
            raise RuntimeKernelError("kernel requires a RuntimeServiceCatalog")
        self._admissions = 0

    # -- component access -------------------------------------------------------

    @property
    def infrastructure(self) -> RuntimeInfrastructure:
        return self._infrastructure

    @property
    def engine(self) -> ExecutionEngine:
        return self._engine

    @property
    def registry(self) -> ExecutionRegistry:
        return self._registry

    @property
    def events(self) -> RuntimeEventBus:
        return self._events

    @property
    def services(self) -> RuntimeServiceCatalog:
        return self._services

    @property
    def admission_count(self) -> int:
        return self._admissions

    @property
    def consumed_contracts(self) -> tuple[str, ...]:
        """The certified upstream capability contracts this kernel consumes (by reference)."""
        return tuple(ref.name for ref in CONSUMED_CONTRACTS)

    # -- admission gate ---------------------------------------------------------

    def admit(self, attestation: WorkloadAttestation) -> WorkloadAttestation:
        """Admit a workload iff it is VALIDATED and CERTIFIED upstream (fail-closed).

        This is the single realization of consuming Validation + Certification: a
        workload that is not both validated and certified is refused
        (:class:`RuntimeAdmissionError`). Registry/Knowledge/Measurement references on the
        attestation are recorded as lineage but the hard gate is validation ∧
        certification.
        """
        if not isinstance(attestation, WorkloadAttestation):
            raise RuntimeKernelError("admit requires a WorkloadAttestation")
        if not attestation.admissible:
            raise RuntimeAdmissionError(
                "workload refused admission: not both validated and certified",
                workload_id=attestation.workload_id,
                validated=attestation.validated,
                certified=attestation.certified,
            )
        self._admissions += 1
        return attestation

    # -- scheduling -------------------------------------------------------------

    def plan(self, requests: Iterable[ExecutionRequest]) -> ExecutionSchedule:
        """Admit every request then produce a deterministic execution schedule."""
        materialized = tuple(requests)
        for request in materialized:
            self.admit(request.attestation)
        result = schedule(materialized)
        for step in result.steps:
            self._events.publish(
                EXECUTION_SCHEDULED,
                subject=result.schedule_id,
                payload={"stage": step.stage, "workload_ids": list(step.workload_ids)},
            )
        return result

    # -- submit (admit → run → register → emit) ---------------------------------

    def submit(
        self, request: ExecutionRequest, *, workflow_id: str | None = None
    ) -> ExecutionRecord:
        """Admit, model-run, register, and emit a single governed execution (fail-closed)."""
        if not isinstance(request, ExecutionRequest):
            raise RuntimeKernelError("submit requires an ExecutionRequest")
        self.admit(request.attestation)
        record = self._engine.run(request, workflow_id=workflow_id)
        return self._register(record)

    def submit_batch(self, requests: Iterable[ExecutionRequest]) -> tuple[ExecutionRecord, ...]:
        """Admit + schedule a batch, then model-run and register in scheduled order."""
        materialized = {request.workload_id: request for request in requests}
        scheduled = self.plan(materialized.values())
        return tuple(self.submit(materialized[workload_id]) for workload_id in scheduled.order)

    def compensate(self, execution_id: str) -> ExecutionRecord:
        """Record a governed reversal of a settled execution and register it (fail-closed)."""
        original = self._registry.get(execution_id)
        compensated = self._engine.compensate(original)
        return self._register(compensated)

    def record(self, record: ExecutionRecord) -> ExecutionRecord:
        """Register an already-modelled execution record and emit its signals (idempotent).

        Used to enrol records produced elsewhere in the plane (e.g. a workflow saga run)
        into the append-only registry with the standard governed event emissions.
        """
        if not isinstance(record, ExecutionRecord):
            raise RuntimeKernelError("record requires an ExecutionRecord")
        return self._register(record)

    def _register(self, record: ExecutionRecord) -> ExecutionRecord:
        newly = record.execution_id not in self._registry
        self._events.publish(
            WORKLOAD_PLACED,
            subject=record.execution_id,
            payload={"workload_id": record.workload_id, "partition": record.placement.partition},
        )
        self._events.publish(
            EXECUTION_STARTED,
            subject=record.execution_id,
            payload={"workload_id": record.workload_id},
        )
        self._events.publish(
            _TERMINAL_EVENT.get(record.final_state, EXECUTION_FAILED),
            subject=record.execution_id,
            payload={"workload_id": record.workload_id, "final_state": record.final_state},
        )
        self._registry.register(record)
        if newly:
            self._events.publish(
                EXECUTION_REGISTERED,
                subject=record.execution_id,
                payload={
                    "workload_id": record.workload_id,
                    "final_state": record.final_state,
                    "record_fingerprint": record.fingerprint(),
                },
            )
        return record

    # -- capacity governance ----------------------------------------------------

    def announce_capacity(self) -> None:
        """Emit the current governed capacity posture as a capacity-changed signal."""
        self._events.publish(
            CAPACITY_CHANGED,
            subject="platform.runtime_platform.capacity",
            payload=self._infrastructure.posture.to_dict(),
        )

    # -- evidence ---------------------------------------------------------------

    def to_dict(self) -> dict[str, Any]:
        return {
            "runtime_kernel_format": RUNTIME_KERNEL_FORMAT,
            "consumed_contracts": list(self.consumed_contracts),
            "services": self._services.to_dict(),
            "infrastructure": self._infrastructure.summary(),
            "admission_count": self._admissions,
            "execution_count": len(self._registry),
            "registry_intact": self._registry.verify(),
            "event_count": len(self._events),
        }

    def fingerprint(self) -> str:
        """A deterministic content hash over the kernel's recorded state."""
        return content_hash(
            {
                "consumed_contracts": list(self.consumed_contracts),
                "services": self._services.to_dict(),
                "infrastructure": self._infrastructure.fingerprint(),
                "registry": self._registry.fingerprint(),
            }
        )


__all__ = ["RUNTIME_KERNEL_FORMAT", "RuntimeKernel"]
