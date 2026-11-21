"""EPIC-PLAT-003 — Repository Operations service (Terminal T5).

The single composition point for the Repository Operations Runtime. It wires an
:class:`~platform.repository_operations.contracts.OperationsConfig` to the orchestrator
with the default (subprocess) canonical-command runner and an optional resumable
checkpoint, and exposes the one operation the mission asks for: perform complete
repository operational verification and return the deterministic report.

The service is strictly additive and record-only: it composes existing canonical
engines and scripts, invents no verdict (TP-01), and never writes to the certified
corpus (DP-03).
"""

from __future__ import annotations

from pathlib import Path
from platform.repository_operations.checkpoint import CheckpointStore
from platform.repository_operations.commands import CommandRunner, subprocess_command_runner
from platform.repository_operations.contracts import (
    ExecutionReport,
    OperationsConfig,
    RepositoryDashboard,
)
from platform.repository_operations.engine import RepositoryOperationsOrchestrator


class RepositoryOperationsService:
    """A thin facade over the orchestrator (one governed operation: verify)."""

    __slots__ = ("_orchestrator",)

    def __init__(self, orchestrator: RepositoryOperationsOrchestrator) -> None:
        self._orchestrator = orchestrator

    @property
    def orchestrator(self) -> RepositoryOperationsOrchestrator:
        return self._orchestrator

    @property
    def config(self) -> OperationsConfig:
        return self._orchestrator.config

    def verify_repository(self, *, resume: bool = False) -> ExecutionReport:
        """Perform complete repository operational verification (the T5 deliverable)."""
        return self._orchestrator.run(resume=resume)

    def dashboard(self, *, resume: bool = False) -> RepositoryDashboard:
        """Run the pipeline and project the Repository Dashboard from the report."""
        return self.verify_repository(resume=resume).dashboard()


def build_repository_operations_service(
    config: OperationsConfig,
    *,
    repo_root: str | Path,
    command_runner: CommandRunner | None = None,
    checkpoint_path: str | Path | None = None,
) -> RepositoryOperationsService:
    """Default composition of the Repository Operations Runtime.

    Uses the subprocess canonical-command runner (bound to ``repo_root``) unless a
    runner is injected, and a JSON checkpoint store when ``checkpoint_path`` is given.
    """
    runner = command_runner if command_runner is not None else subprocess_command_runner(repo_root)
    checkpoint_store = CheckpointStore(checkpoint_path) if checkpoint_path is not None else None
    orchestrator = RepositoryOperationsOrchestrator(
        config,
        command_runner=runner,
        repo_root=repo_root,
        checkpoint_store=checkpoint_store,
    )
    return RepositoryOperationsService(orchestrator)


__all__ = [
    "RepositoryOperationsService",
    "build_repository_operations_service",
]
