"""EPIC-RTE-002 — Execution Health (Runtime Execution Platform).

Realises **Execution Health**: a deterministic, three-valued health assessment of
an :class:`~engine.runtime.execution.coordinator.ExecutionRun`, derived purely from
its recorded states (no ambient state, ORL-20). Health observes; it changes nothing
(RUNTIME-013 ORL-15).

    HEALTHY  — every universe completed successfully.
    DEGRADED — no failure, but at least one universe was skipped (or rolled back).
    FAILED   — at least one universe failed.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

from engine.runtime.execution.state import (
    COMPLETED,
    FAILED,
    ROLLED_BACK,
    SKIPPED,
)

if TYPE_CHECKING:  # pragma: no cover - typing only, avoids an import cycle
    from engine.runtime.execution.coordinator import ExecutionRun

#: Health values.
HEALTHY = "healthy"
DEGRADED = "degraded"
UNHEALTHY = "failed"

#: The closed, sorted set of health values.
HEALTH_STATES: tuple[str, ...] = (DEGRADED, HEALTHY, UNHEALTHY)

#: The recorded health format.
HEALTH_FORMAT = "ucos-execution-health/1.0.0"


@dataclass(frozen=True, slots=True)
class ExecutionHealth:
    """A deterministic health assessment of a run (a pure observation)."""

    run_id: str
    health: str
    completed: int
    failed: int
    skipped: int
    rolled_back: int
    total: int

    @property
    def healthy(self) -> bool:
        return self.health == HEALTHY

    def to_dict(self) -> dict[str, Any]:
        return {
            "health_format": HEALTH_FORMAT,
            "run_id": self.run_id,
            "health": self.health,
            "healthy": self.healthy,
            "completed": self.completed,
            "failed": self.failed,
            "skipped": self.skipped,
            "rolled_back": self.rolled_back,
            "total": self.total,
        }


def health(run: ExecutionRun) -> ExecutionHealth:
    """Assess the deterministic health of ``run``."""
    counts = {COMPLETED: 0, FAILED: 0, SKIPPED: 0, ROLLED_BACK: 0}
    for state in run.states:
        if state.status in counts:
            counts[state.status] += 1

    if counts[FAILED] > 0:
        verdict = UNHEALTHY
    elif counts[SKIPPED] > 0 or counts[ROLLED_BACK] > 0:
        verdict = DEGRADED
    else:
        verdict = HEALTHY

    return ExecutionHealth(
        run_id=run.run_id,
        health=verdict,
        completed=counts[COMPLETED],
        failed=counts[FAILED],
        skipped=counts[SKIPPED],
        rolled_back=counts[ROLLED_BACK],
        total=len(run.states),
    )


__all__ = [
    "HEALTHY",
    "DEGRADED",
    "UNHEALTHY",
    "HEALTH_STATES",
    "HEALTH_FORMAT",
    "ExecutionHealth",
    "health",
]
