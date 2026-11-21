"""EPIC-007 (Terminal T7) — Workflow Orchestration (Universal Runtime Platform).

The **Workflow** engine — realizing ``PRS-026`` Workflow Resolution and ``PRS-027``
Workflow Execution with ``PRS-029``-style saga compensation. A :class:`WorkflowDefinition`
is *metadata, not code*: an ordered set of :class:`WorkflowStep` records with declared
dependencies. Resolution (:meth:`WorkflowDefinition.resolve`) turns the definition into a
deterministic, dependency-ordered :class:`WorkflowPlan`; execution
(:class:`WorkflowRunner`) drives each step through the
:class:`~platform.runtime_platform.execution.ExecutionEngine` in resolved order and
records the outcome.

Execution is a **governed saga**: if any step fails, the runner compensates every
already-succeeded step in strict reverse order (a governed reversal per
:mod:`~platform.runtime_platform.lifecycle`) and settles the run as ``compensated``;
otherwise the run settles ``completed``. Everything is a recorded structure — nothing
runs live — and identical definitions yield byte-identical run records.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from platform.foundation.contracts import content_hash
from platform.runtime_platform.contracts import WorkloadAttestation
from platform.runtime_platform.errors import WorkflowError
from platform.runtime_platform.execution import ExecutionEngine, ExecutionRecord, ExecutionRequest
from typing import Any

#: The recorded workflow formats.
WORKFLOW_PLAN_FORMAT = "ucos-runtime-workflow-plan/1.0.0"
WORKFLOW_RUN_FORMAT = "ucos-runtime-workflow-run/1.0.0"

#: The settled workflow run statuses.
WORKFLOW_COMPLETED = "completed"
WORKFLOW_COMPENSATED = "compensated"


@dataclass(frozen=True, slots=True)
class WorkflowStep:
    """An immutable workflow step (a governed, attested workload with declared dependencies)."""

    step_id: str
    attestation: WorkloadAttestation
    depends_on: tuple[str, ...] = field(default_factory=tuple)
    inject_failure: bool = False

    def __post_init__(self) -> None:
        if not isinstance(self.step_id, str) or not self.step_id:
            raise WorkflowError("workflow step_id is required")
        if not isinstance(self.attestation, WorkloadAttestation):
            raise WorkflowError(
                "workflow step requires a WorkloadAttestation", step_id=self.step_id
            )
        for dependency in self.depends_on:
            if not isinstance(dependency, str) or not dependency:
                raise WorkflowError(
                    "workflow step dependencies must be non-empty", step_id=self.step_id
                )
        if self.step_id in self.depends_on:
            raise WorkflowError("a workflow step may not depend on itself", step_id=self.step_id)
        object.__setattr__(self, "depends_on", tuple(self.depends_on))

    @property
    def workload_id(self) -> str:
        return self.attestation.workload_id

    def to_dict(self) -> dict[str, Any]:
        return {
            "step_id": self.step_id,
            "workload_id": self.workload_id,
            "attestation": self.attestation.attestation_id,
            "depends_on": list(self.depends_on),
            "inject_failure": self.inject_failure,
        }


@dataclass(frozen=True, slots=True)
class WorkflowPlan:
    """A deterministic, dependency-ordered resolution of a workflow definition."""

    workflow_id: str
    order: tuple[str, ...]
    stages: tuple[tuple[str, ...], ...]
    plan_id: str = ""

    @classmethod
    def create(
        cls, *, workflow_id: str, order: tuple[str, ...], stages: tuple[tuple[str, ...], ...]
    ) -> WorkflowPlan:
        core = {
            "workflow_id": workflow_id,
            "order": list(order),
            "stages": [list(s) for s in stages],
        }
        return cls(
            workflow_id=workflow_id,
            order=order,
            stages=stages,
            plan_id=f"UCOS-URPW-{content_hash(core)[:16]}",
        )

    @property
    def stage_count(self) -> int:
        return len(self.stages)

    def to_dict(self) -> dict[str, Any]:
        return {
            "workflow_plan_format": WORKFLOW_PLAN_FORMAT,
            "plan_id": self.plan_id,
            "workflow_id": self.workflow_id,
            "order": list(self.order),
            "stage_count": self.stage_count,
            "stages": [list(stage) for stage in self.stages],
        }

    def fingerprint(self) -> str:
        return content_hash(self.to_dict())


@dataclass(frozen=True, slots=True)
class WorkflowDefinition:
    """An immutable, metadata-driven workflow definition (steps + dependencies)."""

    workflow_id: str
    name: str
    steps: tuple[WorkflowStep, ...]

    def __post_init__(self) -> None:
        if not isinstance(self.workflow_id, str) or not self.workflow_id:
            raise WorkflowError("workflow_id is required")
        if not self.steps:
            raise WorkflowError("workflow requires at least one step", workflow_id=self.workflow_id)
        object.__setattr__(self, "steps", tuple(self.steps))
        ids = [step.step_id for step in self.steps]
        if len(set(ids)) != len(ids):
            raise WorkflowError("workflow step ids must be unique", workflow_id=self.workflow_id)
        known = set(ids)
        for step in self.steps:
            for dependency in step.depends_on:
                if dependency not in known:
                    raise WorkflowError(
                        "workflow step depends on an unknown step",
                        workflow_id=self.workflow_id,
                        step_id=step.step_id,
                        missing=dependency,
                    )

    def step(self, step_id: str) -> WorkflowStep:
        for step in self.steps:
            if step.step_id == step_id:
                return step
        raise WorkflowError("no such workflow step", workflow_id=self.workflow_id, step_id=step_id)

    def resolve(self) -> WorkflowPlan:
        """Resolve the definition into a deterministic dependency-ordered plan (fail-closed)."""
        deps = {step.step_id: set(step.depends_on) for step in self.steps}
        placed: set[str] = set()
        stages: list[tuple[str, ...]] = []
        remaining = set(deps)
        while remaining:
            ready = sorted(sid for sid in remaining if deps[sid] <= placed)
            if not ready:
                raise WorkflowError(
                    "workflow dependency cycle detected",
                    workflow_id=self.workflow_id,
                    unresolved=sorted(remaining),
                )
            stages.append(tuple(ready))
            placed.update(ready)
            remaining.difference_update(ready)
        order = tuple(sid for stage in stages for sid in stage)
        return WorkflowPlan.create(workflow_id=self.workflow_id, order=order, stages=tuple(stages))

    def to_dict(self) -> dict[str, Any]:
        return {
            "workflow_id": self.workflow_id,
            "name": self.name,
            "steps": [step.to_dict() for step in self.steps],
        }

    def fingerprint(self) -> str:
        return content_hash(self.to_dict())


@dataclass(frozen=True, slots=True)
class WorkflowRunRecord:
    """An immutable, content-addressed record of a workflow run outcome."""

    workflow_id: str
    plan: WorkflowPlan
    status: str
    step_records: tuple[ExecutionRecord, ...]
    compensations: tuple[ExecutionRecord, ...]
    failed_step: str | None = None
    run_id: str = ""

    @classmethod
    def create(
        cls,
        *,
        workflow_id: str,
        plan: WorkflowPlan,
        status: str,
        step_records: tuple[ExecutionRecord, ...],
        compensations: tuple[ExecutionRecord, ...],
        failed_step: str | None,
    ) -> WorkflowRunRecord:
        core = {
            "workflow_id": workflow_id,
            "plan_id": plan.plan_id,
            "status": status,
            "step_records": [record.execution_id for record in step_records],
            "compensations": [record.execution_id for record in compensations],
            "failed_step": failed_step,
        }
        return cls(
            workflow_id=workflow_id,
            plan=plan,
            status=status,
            step_records=step_records,
            compensations=compensations,
            failed_step=failed_step,
            run_id=f"UCOS-URPWR-{content_hash(core)[:16]}",
        )

    @property
    def completed(self) -> bool:
        return self.status == WORKFLOW_COMPLETED

    @property
    def records(self) -> tuple[ExecutionRecord, ...]:
        """Every recorded execution (forward steps followed by compensations)."""
        return (*self.step_records, *self.compensations)

    def to_dict(self) -> dict[str, Any]:
        return {
            "workflow_run_format": WORKFLOW_RUN_FORMAT,
            "run_id": self.run_id,
            "workflow_id": self.workflow_id,
            "status": self.status,
            "failed_step": self.failed_step,
            "plan": self.plan.to_dict(),
            "step_records": [record.to_dict() for record in self.step_records],
            "compensations": [record.to_dict() for record in self.compensations],
        }

    def fingerprint(self) -> str:
        return content_hash(self.to_dict())


class WorkflowRunner:
    """The deterministic saga runner over a :class:`WorkflowDefinition`."""

    __slots__ = ("_engine",)

    def __init__(self, engine: ExecutionEngine | None = None) -> None:
        if engine is not None and not isinstance(engine, ExecutionEngine):
            raise WorkflowError("WorkflowRunner requires an ExecutionEngine")
        self._engine = engine if engine is not None else ExecutionEngine()

    @property
    def engine(self) -> ExecutionEngine:
        return self._engine

    def run(self, definition: WorkflowDefinition) -> WorkflowRunRecord:
        """Resolve and run a workflow as a governed saga (compensate-on-failure).

        Steps run in resolved order. On the first failing step, every already-succeeded
        step is compensated in strict reverse order and the run settles ``compensated``;
        with no failure the run settles ``completed``. Recorded structures only.
        """
        if not isinstance(definition, WorkflowDefinition):
            raise WorkflowError("run requires a WorkflowDefinition")
        plan = definition.resolve()
        step_records: list[ExecutionRecord] = []
        failed_step: str | None = None
        for step_id in plan.order:
            step = definition.step(step_id)
            request = ExecutionRequest(
                workload_id=step.workload_id,
                attestation=step.attestation,
                inject_failure=step.inject_failure,
            )
            record = self._engine.run(request, workflow_id=definition.workflow_id)
            step_records.append(record)
            if not record.succeeded:
                failed_step = step_id
                break
        if failed_step is None:
            return WorkflowRunRecord.create(
                workflow_id=definition.workflow_id,
                plan=plan,
                status=WORKFLOW_COMPLETED,
                step_records=tuple(step_records),
                compensations=(),
                failed_step=None,
            )
        # Saga compensation: reverse every succeeded step (skip the failed one).
        compensations: list[ExecutionRecord] = [
            self._engine.compensate(record) for record in reversed(step_records) if record.succeeded
        ]
        return WorkflowRunRecord.create(
            workflow_id=definition.workflow_id,
            plan=plan,
            status=WORKFLOW_COMPENSATED,
            step_records=tuple(step_records),
            compensations=tuple(compensations),
            failed_step=failed_step,
        )


__all__ = [
    "WORKFLOW_PLAN_FORMAT",
    "WORKFLOW_RUN_FORMAT",
    "WORKFLOW_COMPLETED",
    "WORKFLOW_COMPENSATED",
    "WorkflowStep",
    "WorkflowPlan",
    "WorkflowDefinition",
    "WorkflowRunRecord",
    "WorkflowRunner",
]
