"""EPIC-RTE-002 — Execution Scheduler (Runtime Execution Platform).

Realises the **Execution Scheduler**: it turns the composition's already-recorded
:class:`~engine.runtime.planner.ExecutionPlan` into a deterministic
:class:`ExecutionSchedule` of :class:`ScheduledStep` entries, each carrying the
explicit readiness precondition (the dependencies that must be satisfied before the
step's universes may proceed).

The scheduler **reuses the recorded plan and graph verbatim** (Mandatory Rule 4):
it re-derives no ordering, no levels, and no coordination — it reads
``composition.plan.steps`` and ``composition.graph.dependencies_of`` and projects
them into an execution schedule. It is a *recorded structure only*: it dispatches
nothing and executes nothing (RUNTIME-013 ORL-15/ORL-23). Identical compositions
yield a byte-identical schedule (ORL-20).
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

from engine.foundation.obs.logging import get_logger
from engine.foundation.obs.telemetry import trace

if TYPE_CHECKING:  # pragma: no cover - typing only, avoids an import cycle
    from engine.runtime.composition import RuntimeComposition

_logger = get_logger("runtime.execution.scheduler")

#: The recorded schedule format.
EXECUTION_SCHEDULE_FORMAT = "ucos-execution-schedule/1.0.0"


@dataclass(frozen=True, slots=True)
class ScheduledStep:
    """One scheduled coordination step (a readiness unit, not a task).

    ``universe_ids`` are the universes scheduled at this stage (more than one only
    under ``concurrent`` coordination). ``ready_after`` are the universes whose
    prior completion is the precondition for this step to become ready.
    """

    stage: int
    universe_ids: tuple[str, ...]
    ready_after: tuple[str, ...] = field(default_factory=tuple)

    def to_dict(self) -> dict[str, Any]:
        return {
            "stage": self.stage,
            "universe_ids": list(self.universe_ids),
            "ready_after": list(self.ready_after),
        }


@dataclass(frozen=True, slots=True)
class ExecutionSchedule:
    """A deterministic, recorded execution schedule over a composition (ORL-20)."""

    schedule_id: str
    composition_id: str
    coordination: str
    order: tuple[str, ...]
    steps: tuple[ScheduledStep, ...]

    @property
    def stage_count(self) -> int:
        return len(self.steps)

    @property
    def parallelism(self) -> int:
        return max((len(step.universe_ids) for step in self.steps), default=0)

    def stage_of(self, universe_id: str) -> int:
        """The scheduled stage of ``universe_id`` (raises if not scheduled)."""
        for step in self.steps:
            if universe_id in step.universe_ids:
                return step.stage
        raise KeyError(universe_id)

    def stage_map(self) -> dict[str, int]:
        """A ``universe_id → stage`` map (deterministic)."""
        return {universe_id: step.stage for step in self.steps for universe_id in step.universe_ids}

    def to_dict(self) -> dict[str, Any]:
        return {
            "execution_schedule_format": EXECUTION_SCHEDULE_FORMAT,
            "schedule_id": self.schedule_id,
            "composition_id": self.composition_id,
            "coordination": self.coordination,
            "order": list(self.order),
            "stage_count": self.stage_count,
            "parallelism": self.parallelism,
            "steps": [step.to_dict() for step in self.steps],
        }


def schedule(composition: RuntimeComposition) -> ExecutionSchedule:
    """Produce a deterministic :class:`ExecutionSchedule` from ``composition``.

    Reuses the composition's recorded plan (order + steps) and graph (dependency
    readiness) verbatim; no re-planning occurs.
    """
    plan = composition.plan
    graph = composition.graph
    with trace(
        "runtime.execution.schedule",
        composition=composition.composition_id,
        coordination=plan.coordination,
    ):
        steps = tuple(
            ScheduledStep(
                stage=plan_step.stage,
                universe_ids=plan_step.universe_ids,
                ready_after=tuple(
                    sorted(
                        {
                            dependency
                            for universe_id in plan_step.universe_ids
                            for dependency in graph.dependencies_of(universe_id)
                        }
                    )
                ),
            )
            for plan_step in plan.steps
        )
        schedule_id = _schedule_id(composition.composition_id, plan.coordination, steps)
        result = ExecutionSchedule(
            schedule_id=schedule_id,
            composition_id=composition.composition_id,
            coordination=plan.coordination,
            order=plan.order,
            steps=steps,
        )
    _logger.info(
        "runtime.execution.scheduled",
        schedule_id=schedule_id,
        composition_id=composition.composition_id,
        stages=result.stage_count,
        parallelism=result.parallelism,
    )
    return result


def _schedule_id(composition_id: str, coordination: str, steps: tuple[ScheduledStep, ...]) -> str:
    step_part = "|".join(
        f"{s.stage}:{','.join(s.universe_ids)}:{','.join(s.ready_after)}" for s in steps
    )
    payload = f"{composition_id}||coordination={coordination}||steps={step_part}"
    digest = hashlib.sha256(payload.encode()).hexdigest()
    return f"UCOS-EXEC-SCHED-{digest[:16]}"


__all__ = [
    "EXECUTION_SCHEDULE_FORMAT",
    "ScheduledStep",
    "ExecutionSchedule",
    "schedule",
]
