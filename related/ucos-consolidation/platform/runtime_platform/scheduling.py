"""EPIC-007 (Terminal T7) — Execution Scheduling (Universal Runtime Platform).

The **Execution Scheduler** — realizing ``PRS-001`` Execution Scheduling. It turns a set
of governed :class:`~platform.runtime_platform.execution.ExecutionRequest` records into a
deterministic :class:`ExecutionSchedule` of dependency-ordered stages, each carrying the
explicit readiness precondition (the in-batch dependencies that must complete before a
stage's workloads may proceed).

The schedule is a *recorded structure only*: it dispatches nothing and runs nothing
(the engine does the modelled run). Ordering is total and deterministic — within a stage,
workloads are ordered by descending governed ``priority`` then ascending ``workload_id``
— so identical request sets yield a byte-identical schedule. A missing dependency or a
dependency cycle fails closed.
"""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
from platform.foundation.contracts import content_hash
from platform.runtime_platform.errors import ExecutionScheduleError
from platform.runtime_platform.execution import ExecutionRequest
from typing import Any

#: The recorded schedule format.
EXECUTION_SCHEDULE_FORMAT = "ucos-runtime-execution-schedule/1.0.0"


@dataclass(frozen=True, slots=True)
class ScheduledStep:
    """One deterministic scheduling stage (a readiness unit, not a dispatch)."""

    stage: int
    workload_ids: tuple[str, ...]
    ready_after: tuple[str, ...]

    def to_dict(self) -> dict[str, Any]:
        return {
            "stage": self.stage,
            "workload_ids": list(self.workload_ids),
            "ready_after": list(self.ready_after),
        }


@dataclass(frozen=True, slots=True)
class ExecutionSchedule:
    """A deterministic, recorded execution schedule over a batch of requests."""

    schedule_id: str
    order: tuple[str, ...]
    steps: tuple[ScheduledStep, ...]

    @property
    def stage_count(self) -> int:
        return len(self.steps)

    @property
    def parallelism(self) -> int:
        return max((len(step.workload_ids) for step in self.steps), default=0)

    def stage_of(self, workload_id: str) -> int:
        """The scheduled stage of ``workload_id`` (raises if not scheduled)."""
        for step in self.steps:
            if workload_id in step.workload_ids:
                return step.stage
        raise ExecutionScheduleError("workload not scheduled", workload_id=workload_id)

    def to_dict(self) -> dict[str, Any]:
        return {
            "execution_schedule_format": EXECUTION_SCHEDULE_FORMAT,
            "schedule_id": self.schedule_id,
            "order": list(self.order),
            "stage_count": self.stage_count,
            "parallelism": self.parallelism,
            "steps": [step.to_dict() for step in self.steps],
        }

    def fingerprint(self) -> str:
        return content_hash(self.to_dict())


def schedule(requests: Iterable[ExecutionRequest]) -> ExecutionSchedule:
    """Produce a deterministic dependency-ordered :class:`ExecutionSchedule`.

    Workloads are placed in the earliest stage whose dependencies are all satisfied in
    strictly earlier stages. Within a stage, order is ``(-priority, workload_id)``. A
    dependency on an unknown workload, or a dependency cycle, fails closed.
    """
    by_id: dict[str, ExecutionRequest] = {}
    for request in requests:
        if not isinstance(request, ExecutionRequest):
            raise ExecutionScheduleError("schedule requires ExecutionRequest records")
        if request.workload_id in by_id:
            raise ExecutionScheduleError(
                "duplicate workload in schedule batch", workload_id=request.workload_id
            )
        by_id[request.workload_id] = request

    for workload_id, request in by_id.items():
        for dependency in request.dependencies:
            if dependency not in by_id:
                raise ExecutionScheduleError(
                    "execution depends on an unknown workload",
                    workload_id=workload_id,
                    missing=dependency,
                )

    placed: dict[str, int] = {}
    steps: list[ScheduledStep] = []
    remaining = set(by_id)
    stage = 0
    while remaining:
        ready = [
            workload_id
            for workload_id in remaining
            if all(dep in placed for dep in by_id[workload_id].dependencies)
        ]
        if not ready:
            raise ExecutionScheduleError(
                "dependency cycle detected in schedule batch",
                unresolved=sorted(remaining),
            )
        ready.sort(key=lambda wid: (-by_id[wid].priority, wid))
        ready_after = sorted({dep for wid in ready for dep in by_id[wid].dependencies})
        steps.append(
            ScheduledStep(stage=stage, workload_ids=tuple(ready), ready_after=tuple(ready_after))
        )
        for workload_id in ready:
            placed[workload_id] = stage
        remaining.difference_update(ready)
        stage += 1

    order = tuple(workload_id for step in steps for workload_id in step.workload_ids)
    schedule_id = _schedule_id(steps)
    return ExecutionSchedule(schedule_id=schedule_id, order=order, steps=tuple(steps))


def _schedule_id(steps: list[ScheduledStep]) -> str:
    payload = "|".join(
        f"{s.stage}:{','.join(s.workload_ids)}:{','.join(s.ready_after)}" for s in steps
    )
    return f"UCOS-URPS-{content_hash({'steps': payload})[:16]}"


__all__ = [
    "EXECUTION_SCHEDULE_FORMAT",
    "ScheduledStep",
    "ExecutionSchedule",
    "schedule",
]
