"""TASK-000040 — Runtime Execution Planner (EPIC-006).

Realises the **execution planner** of the Universal Runtime Composition Engine: it
turns a resolved :class:`~engine.runtime.graph.RuntimeGraph` into a deterministic,
recorded :class:`ExecutionPlan` expressing one of the three coordination classes of
RUNTIME-013 §D9:

    * ``sequential``  — one universe per step, in dependency order (each universe's
      dependencies precede it);
    * ``concurrent``  — one step per dependency level; the members of a step are
      mutually independent and may be composed in parallel, with the previous
      levels recorded as the step's precondition;
    * ``conditional`` — one universe per step, in dependency order, each step
      recording the decidable condition (its direct dependencies) under which the
      universe participates.

The plan is a **recorded composition structure only** — it is not an engine, a
scheduler, or an executor, and it runs nothing (RUNTIME-013 ORL-15/ORL-23). It is
fully deterministic (derived from the graph's already-sorted order and levels), so
identical graphs yield byte-identical plans (ORL-20). Depends only on
:mod:`engine.runtime.graph` and the Foundation observability APIs.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from engine.foundation.obs.logging import get_logger
from engine.foundation.obs.telemetry import trace
from engine.runtime.errors import ExecutionPlanError
from engine.runtime.graph import RuntimeGraph

_logger = get_logger("runtime.planner")

#: The coordination classes recognised by the planner (RUNTIME-013 §D9).
COORDINATION_CLASSES: tuple[str, ...] = ("sequential", "concurrent", "conditional")

#: The default coordination class (strict dependency ordering).
DEFAULT_COORDINATION = "sequential"

#: The recorded plan format the planner emits.
EXECUTION_PLAN_FORMAT = "ucos-execution-plan/1.0.0"


@dataclass(frozen=True, slots=True)
class PlanStep:
    """One recorded step of a composition plan (a coordination unit, not a task).

    ``universe_ids`` are the universes composed at this step (more than one only
    under ``concurrent`` coordination). ``condition_on`` records the universes
    whose prior composition is the recorded precondition for this step.
    """

    stage: int
    universe_ids: tuple[str, ...]
    condition_on: tuple[str, ...] = field(default_factory=tuple)

    def to_dict(self) -> dict[str, object]:
        return {
            "stage": self.stage,
            "universe_ids": list(self.universe_ids),
            "condition_on": list(self.condition_on),
        }


@dataclass(frozen=True, slots=True)
class ExecutionPlan:
    """A deterministic, recorded coordination plan over a composition (RUNTIME-013 §D9).

    A composition *structure* only: it records the order and coordination of the
    composed universes and executes nothing (ORL-15).
    """

    coordination: str
    order: tuple[str, ...]
    steps: tuple[PlanStep, ...]

    @property
    def parallelism(self) -> int:
        """The widest step (1 for sequential/conditional; ≥1 for concurrent)."""
        return max((len(step.universe_ids) for step in self.steps), default=0)

    @property
    def stage_count(self) -> int:
        """The number of recorded steps."""
        return len(self.steps)

    def to_dict(self) -> dict[str, object]:
        return {
            "execution_plan_format": EXECUTION_PLAN_FORMAT,
            "coordination": self.coordination,
            "order": list(self.order),
            "stage_count": self.stage_count,
            "parallelism": self.parallelism,
            "steps": [step.to_dict() for step in self.steps],
        }


def plan_execution(
    graph: RuntimeGraph, *, coordination: str = DEFAULT_COORDINATION
) -> ExecutionPlan:
    """Produce a deterministic :class:`ExecutionPlan` for ``graph`` (RUNTIME-013 §D9).

    Args:
        graph: the resolved, acyclic composition dependency graph.
        coordination: one of :data:`COORDINATION_CLASSES`.

    Raises:
        ExecutionPlanError: if ``coordination`` is not a recognised class.
    """
    if coordination not in COORDINATION_CLASSES:
        raise ExecutionPlanError(
            "unknown coordination class",
            coordination=coordination,
            allowed=list(COORDINATION_CLASSES),
        )

    with trace("runtime.plan", coordination=coordination, universes=graph.count()):
        order = graph.order()
        if coordination == "sequential":
            steps = tuple(
                PlanStep(stage=index, universe_ids=(universe_id,))
                for index, universe_id in enumerate(order)
            )
        elif coordination == "concurrent":
            steps = tuple(
                PlanStep(
                    stage=index,
                    universe_ids=level,
                    condition_on=tuple(
                        sorted(
                            {
                                dependency
                                for universe_id in level
                                for dependency in graph.dependencies_of(universe_id)
                            }
                        )
                    ),
                )
                for index, level in enumerate(graph.levels())
            )
        else:  # conditional
            steps = tuple(
                PlanStep(
                    stage=index,
                    universe_ids=(universe_id,),
                    condition_on=graph.dependencies_of(universe_id),
                )
                for index, universe_id in enumerate(order)
            )

    plan = ExecutionPlan(coordination=coordination, order=order, steps=steps)
    _logger.info(
        "runtime.plan.built",
        coordination=coordination,
        stages=plan.stage_count,
        parallelism=plan.parallelism,
    )
    return plan


__all__ = [
    "COORDINATION_CLASSES",
    "DEFAULT_COORDINATION",
    "EXECUTION_PLAN_FORMAT",
    "PlanStep",
    "ExecutionPlan",
    "plan_execution",
]
