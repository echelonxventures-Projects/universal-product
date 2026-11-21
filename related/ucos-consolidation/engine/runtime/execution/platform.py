"""EPIC-RTE-002 — Universal Runtime Execution Platform (facade).

The single, cohesive entry point that composes the twenty execution capabilities of
EPIC-RTE-002 into a complete **Runtime Execution Platform**, extending the EPIC-006
Universal Runtime Composition Engine. It is a thin coordinator: every method
delegates to the capability module that owns the logic (scheduler, coordinator,
lifecycle, monitoring, recovery, continuation, checkpointing, replay, rollback,
isolation, federation, authorization, auditing, metrics, health, diagnostics,
state, snapshot, persistence, replay validation) — the platform **reuses every
existing runtime capability and duplicates none**.

Everything the platform produces is a deterministic, recorded structure (ORL-20),
resumable (checkpoint/continue/recover), and observable (monitor/metrics/health/
diagnostics/snapshot). It executes nothing and confers engineering-execution
authority only (RUNTIME-013 ORL-15/ORL-22; IP-01/DE-05).
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

from engine.foundation.obs.logging import get_logger
from engine.foundation.obs.telemetry import trace
from engine.runtime.execution.authorization import Authorization, authorize
from engine.runtime.execution.checkpoint import Checkpoint, checkpoint
from engine.runtime.execution.continuation import continue_execution, verify_continuation
from engine.runtime.execution.coordinator import ExecutionRun, coordinate
from engine.runtime.execution.diagnostics import ExecutionDiagnostics, diagnose
from engine.runtime.execution.federation import FederationView, federate
from engine.runtime.execution.health import ExecutionHealth, health
from engine.runtime.execution.isolation import IsolationView, isolate
from engine.runtime.execution.metrics import ExecutionMetrics, execution_metrics
from engine.runtime.execution.monitoring import ExecutionMonitor, monitor
from engine.runtime.execution.persistence import (
    persist_checkpoint,
    persist_run,
    persist_snapshot,
    restore_checkpoint,
)
from engine.runtime.execution.recovery import recover, recover_and_continue
from engine.runtime.execution.replay import replay
from engine.runtime.execution.replay_validation import (
    ReplayValidation,
    require_replay,
    validate_replay,
)
from engine.runtime.execution.rollback import RollbackPlan, rollback, rollback_plan
from engine.runtime.execution.scheduler import ExecutionSchedule, schedule
from engine.runtime.execution.snapshot import Snapshot, snapshot

if TYPE_CHECKING:  # pragma: no cover - typing only, avoids an import cycle
    from engine.runtime.composition import RuntimeComposition

_logger = get_logger("runtime.execution.platform")

#: The recorded execution-result format.
EXECUTION_RESULT_FORMAT = "ucos-execution-result/1.0.0"


@dataclass(frozen=True, slots=True)
class ExecutionResult:
    """A complete, deterministic execution result: the run plus its observations."""

    run: ExecutionRun
    monitor: ExecutionMonitor
    metrics: ExecutionMetrics
    health: ExecutionHealth
    diagnostics: ExecutionDiagnostics
    snapshot: Snapshot

    @property
    def run_id(self) -> str:
        return self.run.run_id

    @property
    def status(self) -> str:
        return self.run.status

    def to_dict(self) -> dict[str, Any]:
        return {
            "execution_result_format": EXECUTION_RESULT_FORMAT,
            "run_id": self.run.run_id,
            "status": self.run.status,
            "run": self.run.to_dict(),
            "monitor": self.monitor.to_dict(),
            "metrics": self.metrics.to_dict(),
            "health": self.health.to_dict(),
            "diagnostics": self.diagnostics.to_dict(),
            "snapshot": self.snapshot.to_dict(),
        }


class ExecutionPlatform:
    """The Universal Runtime Execution Platform — a thin, delegating facade."""

    __slots__ = ()

    # -- authorization / isolation / federation -------------------------------

    def authorize(
        self, composition: RuntimeComposition, *, subject: str = "engineering"
    ) -> Authorization:
        return authorize(composition, subject=subject)

    def isolate(self, composition: RuntimeComposition) -> IsolationView:
        return isolate(composition)

    def federate(self, composition: RuntimeComposition) -> FederationView:
        return federate(composition)

    # -- scheduling / coordination --------------------------------------------

    def schedule(self, composition: RuntimeComposition) -> ExecutionSchedule:
        return schedule(composition)

    def execute(
        self,
        composition: RuntimeComposition,
        *,
        outcomes: Mapping[str, str] | None = None,
        subject: str = "engineering",
    ) -> ExecutionRun:
        """Coordinate a full modelled execution of ``composition`` (deterministic)."""
        return coordinate(composition, outcomes=outcomes, subject=subject)

    # -- observability ---------------------------------------------------------

    def monitor(self, run: ExecutionRun) -> ExecutionMonitor:
        return monitor(run)

    def metrics(self, run: ExecutionRun, *, emit: bool = False) -> ExecutionMetrics:
        return execution_metrics(run, emit=emit)

    def health(self, run: ExecutionRun) -> ExecutionHealth:
        return health(run)

    def diagnose(self, run: ExecutionRun) -> ExecutionDiagnostics:
        return diagnose(run)

    def snapshot(self, run: ExecutionRun) -> Snapshot:
        return snapshot(run)

    # -- checkpoint / continuation / recovery ---------------------------------

    def checkpoint(self, run: ExecutionRun, *, through_stage: int | None = None) -> Checkpoint:
        return checkpoint(run, through_stage=through_stage)

    def continue_from(
        self,
        composition: RuntimeComposition,
        checkpoint: Checkpoint,
        *,
        outcomes: Mapping[str, str] | None = None,
        subject: str = "engineering",
    ) -> ExecutionRun:
        return continue_execution(composition, checkpoint, outcomes=outcomes, subject=subject)

    def recover(self, run: ExecutionRun) -> Checkpoint:
        return recover(run)

    def recover_and_continue(
        self,
        composition: RuntimeComposition,
        run: ExecutionRun,
        *,
        outcomes: Mapping[str, str] | None = None,
        subject: str = "engineering",
    ) -> ExecutionRun:
        return recover_and_continue(composition, run, outcomes=outcomes, subject=subject)

    def verify_continuation(self, original: ExecutionRun, resumed: ExecutionRun) -> bool:
        return verify_continuation(original, resumed)

    # -- rollback --------------------------------------------------------------

    def rollback_plan(self, run: ExecutionRun) -> RollbackPlan:
        return rollback_plan(run)

    def rollback(self, run: ExecutionRun) -> ExecutionRun:
        return rollback(run)

    # -- persistence -----------------------------------------------------------

    def persist_checkpoint(self, cp: Checkpoint) -> str:
        return persist_checkpoint(cp)

    def restore_checkpoint(self, blob: str) -> Checkpoint:
        return restore_checkpoint(blob)

    def persist_snapshot(self, snap: Snapshot) -> str:
        return persist_snapshot(snap)

    def persist_run(self, run: ExecutionRun) -> str:
        return persist_run(run.to_dict())

    # -- replay / replay validation -------------------------------------------

    def replay(self, composition: RuntimeComposition, run: ExecutionRun) -> ExecutionRun:
        return replay(composition, run)

    def validate_replay(
        self, composition: RuntimeComposition, run: ExecutionRun
    ) -> ReplayValidation:
        return validate_replay(composition, run)

    def require_replay(
        self, composition: RuntimeComposition, run: ExecutionRun
    ) -> ReplayValidation:
        return require_replay(composition, run)

    # -- end-to-end ------------------------------------------------------------

    def run(
        self,
        composition: RuntimeComposition,
        *,
        outcomes: Mapping[str, str] | None = None,
        subject: str = "engineering",
    ) -> ExecutionResult:
        """Execute ``composition`` end to end and bundle every observation.

        The whole result is deterministic (ORL-20): identical inputs yield a
        byte-identical :class:`ExecutionResult`.
        """
        with trace("runtime.execution.run", composition=composition.composition_id):
            execution = self.execute(composition, outcomes=outcomes, subject=subject)
            result = ExecutionResult(
                run=execution,
                monitor=self.monitor(execution),
                metrics=self.metrics(execution),
                health=self.health(execution),
                diagnostics=self.diagnose(execution),
                snapshot=self.snapshot(execution),
            )
        _logger.info(
            "runtime.execution.platform.run",
            run_id=result.run_id,
            status=result.status,
            composition_id=composition.composition_id,
        )
        return result


__all__ = [
    "EXECUTION_RESULT_FORMAT",
    "ExecutionResult",
    "ExecutionPlatform",
]
