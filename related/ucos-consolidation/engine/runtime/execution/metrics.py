"""EPIC-RTE-002 — Execution Metrics (Runtime Execution Platform).

Realises **Execution Metrics**: a deterministic, derived set of counters over an
:class:`~engine.runtime.execution.coordinator.ExecutionRun`, plus optional emission
into the Foundation in-memory metric registry (:mod:`engine.foundation.obs.telemetry`,
reused verbatim — no duplicate metric machinery). The derived record is a pure
function of the run (no wall-clock), so identical runs yield identical metrics
(ORL-20). Metrics observe; they change nothing (RUNTIME-013 ORL-15).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

from engine.foundation.obs.telemetry import metric_counter, metric_gauge
from engine.runtime.execution.state import COMPLETED, EXECUTION_STATES, FAILED, SKIPPED

if TYPE_CHECKING:  # pragma: no cover - typing only, avoids an import cycle
    from engine.runtime.execution.coordinator import ExecutionRun

#: The recorded metrics format.
METRICS_FORMAT = "ucos-execution-metrics/1.0.0"


@dataclass(frozen=True, slots=True)
class ExecutionMetrics:
    """Deterministic, derived execution counters (a pure observation)."""

    run_id: str
    status: str
    total: int
    completed: int
    failed: int
    skipped: int
    transitions: int
    stage_count: int
    parallelism: int
    by_state: dict[str, int]
    by_context: dict[str, int]

    @property
    def success_ratio(self) -> float:
        """The completed fraction of the run (1.0 for an empty run)."""
        return 1.0 if self.total == 0 else self.completed / self.total

    def to_dict(self) -> dict[str, Any]:
        return {
            "metrics_format": METRICS_FORMAT,
            "run_id": self.run_id,
            "status": self.status,
            "total": self.total,
            "completed": self.completed,
            "failed": self.failed,
            "skipped": self.skipped,
            "transitions": self.transitions,
            "stage_count": self.stage_count,
            "parallelism": self.parallelism,
            "success_ratio": self.success_ratio,
            "by_state": dict(self.by_state),
            "by_context": dict(self.by_context),
        }


def execution_metrics(run: ExecutionRun, *, emit: bool = False) -> ExecutionMetrics:
    """Derive :class:`ExecutionMetrics` from ``run``.

    Args:
        run: the execution run to measure.
        emit: when true, also record the counters into the Foundation metric
            registry (a side channel; the returned record remains pure).
    """
    by_state = {state: 0 for state in EXECUTION_STATES}
    by_context: dict[str, int] = {}
    for state in run.states:
        by_state[state.status] += 1
        by_context[state.context_id] = by_context.get(state.context_id, 0) + 1

    metrics = ExecutionMetrics(
        run_id=run.run_id,
        status=run.status,
        total=len(run.states),
        completed=by_state[COMPLETED],
        failed=by_state[FAILED],
        skipped=by_state[SKIPPED],
        transitions=len(run.audit),
        stage_count=run.schedule.stage_count,
        parallelism=run.schedule.parallelism,
        by_state=by_state,
        by_context={cid: by_context[cid] for cid in sorted(by_context)},
    )
    if emit:
        metric_gauge("execution.universes", metrics.total, run=run.run_id)
        metric_counter("execution.transitions", metrics.transitions, run=run.run_id)
        for status, count in metrics.by_state.items():
            metric_gauge("execution.by_state", count, run=run.run_id, state=status)
    return metrics


__all__ = ["METRICS_FORMAT", "ExecutionMetrics", "execution_metrics"]
