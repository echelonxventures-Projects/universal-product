"""EPIC-007 (Terminal T7) — Runtime Platform Service (Universal Runtime Platform).

The single governed **composition point** of the Universal Runtime Platform — the
operational surface that ties the :class:`~platform.runtime_platform.core.RuntimeKernel`
(admission + scheduling + execution + registry + events + services) together with the
:class:`~platform.runtime_platform.workflow.WorkflowRunner` saga engine into one entry
point. It exposes the governed operations of the plane:

    * :meth:`RuntimePlatformService.submit_execution` / :meth:`submit_batch` — admit,
      schedule, model-run, and register governed executions.
    * :meth:`RuntimePlatformService.run_workflow` — resolve and run a workflow as a
      governed saga, registering every step (and any compensations) in the execution
      registry and emitting the workflow signals.
    * :meth:`RuntimePlatformService.get_execution` / :meth:`discover` / :meth:`lineage_of`
      / :meth:`ledger_entry` — pure reads over the append-only registry.
    * :meth:`RuntimePlatformService.evidence` — a deterministic, content-addressed record
      of the whole plane's state (reproducible; P5).

It is strictly additive and **govern/record-only**: it runs nothing live, starts no
server, admits only VALIDATED-and-CERTIFIED workloads (fail-closed), and never mutates a
recorded execution (the registry is append-only). Determinism holds: the same
attestations + the same ordered calls yield the same evidence fingerprint.
"""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
from platform.foundation.contracts import content_hash
from platform.runtime_platform.core import RuntimeKernel
from platform.runtime_platform.errors import RuntimePlatformServiceError
from platform.runtime_platform.events import (
    WORKFLOW_COMPENSATED,
    WORKFLOW_COMPLETED,
    WORKFLOW_RESOLVED,
    WORKFLOW_STEP_COMPLETED,
    RuntimeEventBus,
)
from platform.runtime_platform.execution import ExecutionRecord, ExecutionRequest
from platform.runtime_platform.registry import ExecutionLedgerEntry, ExecutionLineageView
from platform.runtime_platform.scheduling import ExecutionSchedule
from platform.runtime_platform.workflow import (
    WORKFLOW_COMPLETED as WORKFLOW_STATUS_COMPLETED,
)
from platform.runtime_platform.workflow import (
    WorkflowDefinition,
    WorkflowRunner,
    WorkflowRunRecord,
)
from typing import Any


@dataclass(frozen=True, slots=True)
class RuntimePlatformEvidence:
    """A deterministic, content-addressed record of Universal Runtime Platform state."""

    kernel_fingerprint: str
    registry_fingerprint: str
    execution_count: int
    admission_count: int
    workflow_run_count: int
    state_census: tuple[tuple[str, int], ...]
    registry_intact: bool
    event_count: int
    service_count: int
    evidence_id: str = ""

    @classmethod
    def create(
        cls,
        *,
        kernel_fingerprint: str,
        registry_fingerprint: str,
        execution_count: int,
        admission_count: int,
        workflow_run_count: int,
        state_census: tuple[tuple[str, int], ...],
        registry_intact: bool,
        event_count: int,
        service_count: int,
    ) -> RuntimePlatformEvidence:
        core = {
            "kernel_fingerprint": kernel_fingerprint,
            "registry_fingerprint": registry_fingerprint,
            "execution_count": execution_count,
            "admission_count": admission_count,
            "workflow_run_count": workflow_run_count,
            "state_census": [list(pair) for pair in state_census],
            "registry_intact": registry_intact,
            "event_count": event_count,
            "service_count": service_count,
        }
        return cls(
            kernel_fingerprint=kernel_fingerprint,
            registry_fingerprint=registry_fingerprint,
            execution_count=execution_count,
            admission_count=admission_count,
            workflow_run_count=workflow_run_count,
            state_census=state_census,
            registry_intact=registry_intact,
            event_count=event_count,
            service_count=service_count,
            evidence_id=f"UCOS-URPE-{content_hash(core)[:16]}",
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "evidence_id": self.evidence_id,
            "kernel_fingerprint": self.kernel_fingerprint,
            "registry_fingerprint": self.registry_fingerprint,
            "execution_count": self.execution_count,
            "admission_count": self.admission_count,
            "workflow_run_count": self.workflow_run_count,
            "state_census": {name: count for name, count in self.state_census},
            "registry_intact": self.registry_intact,
            "event_count": self.event_count,
            "service_count": self.service_count,
        }

    def fingerprint(self) -> str:
        return content_hash(self.to_dict())


class RuntimePlatformService:
    """The governed composition point for the UCOS Universal Runtime Platform."""

    __slots__ = ("_kernel", "_runner", "_workflow_runs")

    def __init__(self, *, kernel: RuntimeKernel, runner: WorkflowRunner) -> None:
        if not isinstance(kernel, RuntimeKernel):
            raise RuntimePlatformServiceError("service requires a RuntimeKernel")
        if not isinstance(runner, WorkflowRunner):
            raise RuntimePlatformServiceError("service requires a WorkflowRunner")
        self._kernel = kernel
        self._runner = runner
        self._workflow_runs = 0

    # -- component access -------------------------------------------------------

    @property
    def kernel(self) -> RuntimeKernel:
        return self._kernel

    @property
    def events(self) -> RuntimeEventBus:
        return self._kernel.events

    @property
    def workflow_run_count(self) -> int:
        return self._workflow_runs

    # -- governed execution -----------------------------------------------------

    def submit_execution(self, request: ExecutionRequest) -> ExecutionRecord:
        """Admit, model-run, and register a single governed execution (fail-closed)."""
        return self._kernel.submit(request)

    def submit_batch(self, requests: Iterable[ExecutionRequest]) -> tuple[ExecutionRecord, ...]:
        """Admit + schedule a batch, then model-run and register in scheduled order."""
        return self._kernel.submit_batch(requests)

    def schedule_batch(self, requests: Iterable[ExecutionRequest]) -> ExecutionSchedule:
        """Admit a batch and return its deterministic execution schedule (no run)."""
        return self._kernel.plan(requests)

    def compensate_execution(self, execution_id: str) -> ExecutionRecord:
        """Record a governed reversal of a settled execution (fail-closed)."""
        return self._kernel.compensate(execution_id)

    # -- governed workflow saga -------------------------------------------------

    def run_workflow(self, definition: WorkflowDefinition) -> WorkflowRunRecord:
        """Resolve and run a workflow as a governed saga, registering every execution.

        Each step's workload is admitted (VALIDATED ∧ CERTIFIED) before the saga runs; the
        run is executed by the runner over the kernel's engine, every produced execution
        (forward steps and any compensations) is enrolled in the append-only registry, and
        the workflow signals are emitted. Fail-closed on a non-admissible step.
        """
        if not isinstance(definition, WorkflowDefinition):
            raise RuntimePlatformServiceError("run_workflow requires a WorkflowDefinition")
        for step in definition.steps:
            self._kernel.admit(step.attestation)
        run_record = self._runner.run(definition)
        self._workflow_runs += 1
        self.events.publish(
            WORKFLOW_RESOLVED,
            subject=run_record.workflow_id,
            payload={"plan_id": run_record.plan.plan_id, "order": list(run_record.plan.order)},
        )
        for record in run_record.records:
            self._kernel.record(record)
        for record in run_record.step_records:
            self.events.publish(
                WORKFLOW_STEP_COMPLETED,
                subject=run_record.workflow_id,
                payload={
                    "workload_id": record.workload_id,
                    "final_state": record.final_state,
                    "execution_id": record.execution_id,
                },
            )
        self.events.publish(
            WORKFLOW_COMPLETED
            if run_record.status == WORKFLOW_STATUS_COMPLETED
            else WORKFLOW_COMPENSATED,
            subject=run_record.workflow_id,
            payload={"status": run_record.status, "failed_step": run_record.failed_step},
        )
        return run_record

    # -- pure reads over the append-only registry -------------------------------

    def get_execution(self, execution_id: str) -> ExecutionRecord:
        """Resolve a recorded execution by id (fail-closed on absent)."""
        return self._kernel.registry.get(execution_id)

    def discover(
        self,
        *,
        workflow_id: str | None = None,
        final_state: str | None = None,
    ) -> tuple[ExecutionRecord, ...]:
        """Discover recorded executions, optionally filtered by workflow or final state."""
        registry = self._kernel.registry
        if workflow_id is not None and final_state is not None:
            return tuple(
                record
                for record in registry.by_workflow(workflow_id)
                if record.final_state == final_state
            )
        if workflow_id is not None:
            return registry.by_workflow(workflow_id)
        if final_state is not None:
            return registry.by_state(final_state)
        return registry.records()

    def lineage_of(self, execution_id: str) -> ExecutionLineageView:
        """Render the deterministic lineage of a recorded execution (fail-closed)."""
        return self._kernel.registry.lineage(execution_id)

    def ledger_entry(self, execution_id: str) -> ExecutionLedgerEntry:
        """Resolve the hash-chained ledger entry for an execution (fail-closed)."""
        return self._kernel.registry.entry(execution_id)

    # -- evidence / health ------------------------------------------------------

    def evidence(self) -> RuntimePlatformEvidence:
        """Produce deterministic Universal Runtime Platform evidence over the plane state."""
        registry = self._kernel.registry
        census = registry.census()
        return RuntimePlatformEvidence.create(
            kernel_fingerprint=self._kernel.fingerprint(),
            registry_fingerprint=registry.fingerprint(),
            execution_count=census.get("total", 0),
            admission_count=self._kernel.admission_count,
            workflow_run_count=self._workflow_runs,
            state_census=tuple(sorted((k, v) for k, v in census.items() if k != "total")),
            registry_intact=registry.verify(),
            event_count=len(self.events),
            service_count=len(self._kernel.services),
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "kernel": self._kernel.to_dict(),
            "workflow_run_count": self._workflow_runs,
            "evidence": self.evidence().to_dict(),
        }


def build_runtime_platform_service(
    *,
    kernel: RuntimeKernel | None = None,
) -> RuntimePlatformService:
    """Default, registry-driven composition of the Universal Runtime Platform service.

    Wires a :class:`RuntimeKernel` (with its infrastructure, engine, execution registry,
    governed event bus, and runtime-service catalog) and a :class:`WorkflowRunner` bound to
    the kernel's engine so workflow executions share the same deterministic substrate.
    """
    runtime_kernel = kernel if kernel is not None else RuntimeKernel()
    if not isinstance(runtime_kernel, RuntimeKernel):
        raise RuntimePlatformServiceError("build requires a RuntimeKernel")
    runner = WorkflowRunner(engine=runtime_kernel.engine)
    return RuntimePlatformService(kernel=runtime_kernel, runner=runner)


__all__ = [
    "RuntimePlatformEvidence",
    "RuntimePlatformService",
    "build_runtime_platform_service",
]
