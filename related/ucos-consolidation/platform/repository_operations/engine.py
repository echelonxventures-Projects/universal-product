"""EPIC-PLAT-003 — Repository Operations orchestrator (Terminal T5).

The :class:`RepositoryOperationsOrchestrator` is the single conductor that performs
**complete repository operational verification** by running a configuration-driven
pipeline of stages — each delegating to existing canonical machinery — and aggregating
their outcomes into a deterministic, content-addressed
:class:`~platform.repository_operations.contracts.ExecutionReport` (and, from it, a
:class:`~platform.repository_operations.contracts.RepositoryDashboard`).

Execution is:

    * **configuration driven** — the stages come entirely from an
      :class:`~platform.repository_operations.contracts.OperationsConfig`; nothing is
      hardcoded;
    * **deterministic** — the report is a pure function of the config and the ordered
      stage outcomes; no wall-clock or ambient state enters any identity;
    * **resumable** — PASSED stages are checkpointed (keyed to the config digest); a
      resumed run skips them and re-runs only what has not yet passed; and
    * **fail-closed** — the verdict is FAIL iff any blocking stage failed. Like
      ``verify.sh``, every stage runs (unless resumed-skipped) and is then summarized.
"""

from __future__ import annotations

from pathlib import Path
from platform.repository_operations.checkpoint import Checkpoint, CheckpointStore
from platform.repository_operations.commands import CommandRunner
from platform.repository_operations.contracts import (
    CoverageSummary,
    ExecutionReport,
    OperationsConfig,
    StageOutcome,
    StageResult,
)
from platform.repository_operations.errors import OperationsServiceError
from platform.repository_operations.stages import execute_stage


class RepositoryOperationsOrchestrator:
    """Runs a declarative operations pipeline over the existing canonical engines."""

    __slots__ = ("_config", "_command_runner", "_repo_root", "_checkpoint_store")

    def __init__(
        self,
        config: OperationsConfig,
        *,
        command_runner: CommandRunner,
        repo_root: str | Path,
        checkpoint_store: CheckpointStore | None = None,
    ) -> None:
        if not isinstance(config, OperationsConfig):
            raise OperationsServiceError("a valid OperationsConfig is required")
        if not callable(command_runner):
            raise OperationsServiceError("command_runner must be callable")
        if checkpoint_store is not None and not isinstance(checkpoint_store, CheckpointStore):
            raise OperationsServiceError("checkpoint_store must be a CheckpointStore when provided")
        self._config = config
        self._command_runner = command_runner
        self._repo_root = Path(repo_root)
        self._checkpoint_store = checkpoint_store

    @property
    def config(self) -> OperationsConfig:
        return self._config

    @property
    def checkpoint_store(self) -> CheckpointStore | None:
        return self._checkpoint_store

    def run(self, *, resume: bool = False) -> ExecutionReport:
        """Execute the pipeline and return the aggregated, content-addressed report."""
        completed = self._resume_state() if resume else {}

        results: list[StageResult] = []
        coverage: CoverageSummary | None = None
        resumed = False

        for spec in self._config.stages:
            if spec.stage_id in completed:
                results.append(
                    StageResult.create(
                        spec,
                        StageOutcome.SKIPPED,
                        "skipped (reused from checkpoint)",
                        evidence_ref=completed[spec.stage_id],
                    )
                )
                resumed = True
                continue
            result, stage_coverage = execute_stage(
                spec,
                command_runner=self._command_runner,
                repo_root=self._repo_root,
                measured_coverage=coverage,
            )
            results.append(result)
            if stage_coverage is not None:
                coverage = stage_coverage

        self._save_checkpoint(results)

        return ExecutionReport.create(
            repository_id=self._config.repository_id,
            epic_id=self._config.epic_id,
            config_digest=self._config.digest(),
            stage_results=tuple(results),
            coverage=coverage,
            resumed=resumed,
        )

    def _resume_state(self) -> dict[str, str]:
        """Load the checkpoint's PASSED-stage set, but only for the current config."""
        if self._checkpoint_store is None:
            return {}
        checkpoint = self._checkpoint_store.load()
        if checkpoint is None or checkpoint.config_digest != self._config.digest():
            # A missing or stale (different-config) checkpoint forces a clean run.
            return {}
        return dict(checkpoint.completed)

    def _save_checkpoint(self, results: list[StageResult]) -> None:
        if self._checkpoint_store is None:
            return
        completed = {r.stage_id: r.evidence_ref for r in results if not r.failed}
        self._checkpoint_store.save(
            Checkpoint(config_digest=self._config.digest(), completed=completed)
        )


__all__ = ["RepositoryOperationsOrchestrator"]
