"""EPIC-RTE-002 — Execution Rollback (Runtime Execution Platform).

Realises **Execution Rollback**: the reversible reversal of a modelled execution.
Every completed universe is reversed in **reverse dependency order** (dependents
before their dependencies — a leaf-first teardown), reusing the composition graph's
recorded topological order verbatim (:meth:`RuntimeGraph.order`, EPIC-006) and the
lifecycle's ``completed → rolled_back`` transition. This mirrors the reversible,
checkpoint-based rollback discipline of EPIC-005 (IP-08). Rollback produces a new,
deterministic :class:`~engine.runtime.execution.coordinator.ExecutionRun` and a
recorded :class:`RollbackPlan`; it reverses records, not live effects (RUNTIME-013
ORL-15).
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass
from typing import Any

from engine.foundation.obs.logging import get_logger
from engine.foundation.obs.telemetry import trace
from engine.runtime.execution.auditing import ROLLBACK, AuditLog
from engine.runtime.execution.coordinator import ExecutionRun, build_run_descriptor
from engine.runtime.execution.errors import RollbackError
from engine.runtime.execution.lifecycle import require_transition
from engine.runtime.execution.state import (
    COMPLETED,
    ROLLED_BACK,
    derive_run_status,
)

_logger = get_logger("runtime.execution.rollback")

#: The recorded rollback-plan format.
ROLLBACK_PLAN_FORMAT = "ucos-execution-rollback/1.0.0"


@dataclass(frozen=True, slots=True)
class RollbackPlan:
    """A deterministic, recorded reverse-order rollback plan over a run (IP-08)."""

    plan_id: str
    run_id: str
    composition_id: str
    order: tuple[str, ...]

    @property
    def is_empty(self) -> bool:
        return not self.order

    def to_dict(self) -> dict[str, Any]:
        return {
            "rollback_plan_format": ROLLBACK_PLAN_FORMAT,
            "plan_id": self.plan_id,
            "run_id": self.run_id,
            "composition_id": self.composition_id,
            "order": list(self.order),
        }


def rollback_plan(run: ExecutionRun) -> RollbackPlan:
    """Produce the reverse-order rollback plan for the completed universes of ``run``."""
    completed = {s.universe_id for s in run.states if s.status == COMPLETED}
    order = tuple(
        universe_id
        for universe_id in reversed(run.composition.graph.order())
        if universe_id in completed
    )
    return RollbackPlan(
        plan_id=_plan_id(run.run_id, order),
        run_id=run.run_id,
        composition_id=run.composition_id,
        order=order,
    )


def rollback(run: ExecutionRun) -> ExecutionRun:
    """Reverse ``run`` into a new, deterministic rolled-back :class:`ExecutionRun`.

    Raises:
        RollbackError: if the run has no completed universe to reverse.
    """
    plan = rollback_plan(run)
    if plan.is_empty:
        raise RollbackError("run has no completed universe to roll back", run_id=run.run_id)

    with trace("runtime.execution.rollback", run=run.run_id):
        states = run.state_map()
        audit = AuditLog()
        for universe_id in plan.order:
            current = states[universe_id]
            require_transition(COMPLETED, ROLLED_BACK)
            audit = audit.append(
                event=ROLLBACK,
                universe_id=universe_id,
                stage=current.stage,
                source_state=COMPLETED,
                target_state=ROLLED_BACK,
                detail="reverse-order-rollback",
            )
            states[universe_id] = current.with_status(ROLLED_BACK, outcome="rolled-back")

        final_states = tuple(sorted(states.values(), key=lambda s: s.universe_id))
        status = derive_run_status(final_states)
        rolled_run_id = _rollback_run_id(run.run_id)
        descriptor = build_run_descriptor(
            run_id=rolled_run_id,
            composition=run.composition,
            authorization_id=run.authorization_id,
            execution_schedule=run.schedule,
            states=final_states,
            audit=audit,
            status=status,
        )
        rolled = ExecutionRun(
            run_id=rolled_run_id,
            composition=run.composition,
            coordination=run.coordination,
            authorization_id=run.authorization_id,
            schedule=run.schedule,
            states=final_states,
            audit=audit,
            status=status,
            disclosure=run.disclosure,
            descriptor=descriptor,
        )
    _logger.info(
        "runtime.execution.rolled_back",
        run=run.run_id,
        rolled_run_id=rolled_run_id,
        reversed_count=len(plan.order),
    )
    return rolled


def _plan_id(run_id: str, order: tuple[str, ...]) -> str:
    payload = f"{run_id}||rollback={','.join(order)}"
    digest = hashlib.sha256(payload.encode()).hexdigest()
    return f"UCOS-EXEC-RBACK-{digest[:16]}"


def _rollback_run_id(run_id: str) -> str:
    digest = hashlib.sha256(f"{run_id}::rollback".encode()).hexdigest()
    return f"UCOS-EXEC-RUN-{digest[:16]}"


__all__ = ["ROLLBACK_PLAN_FORMAT", "RollbackPlan", "rollback_plan", "rollback"]
