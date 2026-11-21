"""EPIC-RTE-002 — Execution Monitoring (Runtime Execution Platform).

Realises **Execution Monitoring**: a deterministic, read-only progress view over an
:class:`~engine.runtime.execution.coordinator.ExecutionRun`. Monitoring derives its
figures purely from the run's recorded states and audit log (no ambient state, no
wall-clock), so the same run always yields the same monitor (ORL-20). It observes;
it changes nothing (RUNTIME-013 ORL-15).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

from engine.runtime.execution.state import EXECUTION_STATES, TERMINAL_STATES

if TYPE_CHECKING:  # pragma: no cover - typing only, avoids an import cycle
    from engine.runtime.execution.coordinator import ExecutionRun

#: The recorded monitor format.
MONITOR_FORMAT = "ucos-execution-monitor/1.0.0"


@dataclass(frozen=True, slots=True)
class ExecutionMonitor:
    """A deterministic progress snapshot of a run (a read-only observation)."""

    run_id: str
    status: str
    total: int
    by_state: dict[str, int]
    transitions: int
    stage_count: int
    parallelism: int

    @property
    def terminal_count(self) -> int:
        return sum(self.by_state[state] for state in TERMINAL_STATES)

    @property
    def completed_fraction(self) -> float:
        """The fraction of universes in a terminal state (1.0 for an empty run)."""
        if self.total == 0:
            return 1.0
        return self.terminal_count / self.total

    @property
    def is_complete(self) -> bool:
        """True iff every universe has reached a terminal state."""
        return self.terminal_count == self.total

    def to_dict(self) -> dict[str, Any]:
        return {
            "monitor_format": MONITOR_FORMAT,
            "run_id": self.run_id,
            "status": self.status,
            "total": self.total,
            "by_state": dict(self.by_state),
            "transitions": self.transitions,
            "stage_count": self.stage_count,
            "parallelism": self.parallelism,
            "terminal_count": self.terminal_count,
            "completed_fraction": self.completed_fraction,
            "is_complete": self.is_complete,
        }


def monitor(run: ExecutionRun) -> ExecutionMonitor:
    """Produce a deterministic :class:`ExecutionMonitor` for ``run``."""
    by_state = {state: 0 for state in EXECUTION_STATES}
    for state in run.states:
        by_state[state.status] += 1
    return ExecutionMonitor(
        run_id=run.run_id,
        status=run.status,
        total=len(run.states),
        by_state=by_state,
        transitions=len(run.audit),
        stage_count=run.schedule.stage_count,
        parallelism=run.schedule.parallelism,
    )


__all__ = ["MONITOR_FORMAT", "ExecutionMonitor", "monitor"]
