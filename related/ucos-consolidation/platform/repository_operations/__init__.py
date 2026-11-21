"""EPIC-PLAT-003 — Repository Operations Automation (Terminal T5).

The platform-layer **conductor** that performs complete repository operational
verification from a single, configuration-driven, deterministic, resumable command by
**orchestrating the existing canonical infrastructure** — it introduces **no parallel
tooling**:

    * canonical scripts/targets — ``verify.sh`` (lint + tests/coverage + governance),
      ``doctor.sh`` (environment health), ``bootstrap.sh``, and the ``Makefile``;
    * the certified EC-1 **Acceptance** engine — repository discovery, context
      assimilation, ownership, dependencies, reuse, implementation, validation,
      certification, registration, traceability, 100% coverage, reconciliation,
      cross-EPIC integration, architecture consistency, repository health, and freeze
      readiness — plus the **Repository Readiness** report;
    * the certified EC-1 **Validation** and **Certification** engines;
    * the certified **frozen-corpus guard** (Architecture Freeze Check); and
    * the canonical **coverage** report (``coverage.xml``).

The run aggregates every stage outcome into a content-addressed **Execution Report**,
a **Repository Dashboard**, and a **Coverage Report** — deterministic (a pure function
of the config and stage outcomes; no wall-clock leaks into any identity), fail-closed
(FAIL iff any blocking stage failed), and resumable (passed stages are checkpointed).

It is strictly additive and record-only: it consumes the certified engines and scripts
through their published surfaces, invents no verdict (TP-01), and never writes to the
certified corpus (DP-03).
"""

from __future__ import annotations

from platform.repository_operations.checkpoint import Checkpoint, CheckpointStore
from platform.repository_operations.commands import (
    CANONICAL_COMMANDS,
    CommandRunner,
    resolve_command,
    subprocess_command_runner,
)
from platform.repository_operations.config import load_config, parse_config
from platform.repository_operations.contracts import (
    DASHBOARD_FORMAT,
    EXECUTION_REPORT_FORMAT,
    OPERATIONS_AUTHORITY,
    REPOSITORY_OPERATIONS_CONTRACT_VERSION,
    CoverageSummary,
    ExecutionReport,
    OperationsConfig,
    OperationsVerdict,
    RepositoryDashboard,
    StageKind,
    StageOutcome,
    StageResult,
    StageSpec,
)
from platform.repository_operations.coverage import load_coverage_summary, parse_coverage_xml
from platform.repository_operations.engine import RepositoryOperationsOrchestrator
from platform.repository_operations.errors import (
    CheckpointError,
    CoverageReportError,
    OperationsConfigError,
    OperationsServiceError,
    RepositoryOperationsError,
    StageDefinitionError,
    StageExecutionError,
)
from platform.repository_operations.service import (
    RepositoryOperationsService,
    build_repository_operations_service,
)
from platform.repository_operations.stages import execute_stage
from platform.repository_operations.subjects import build_validation_subject

__all__ = [
    # contracts
    "REPOSITORY_OPERATIONS_CONTRACT_VERSION",
    "EXECUTION_REPORT_FORMAT",
    "DASHBOARD_FORMAT",
    "OPERATIONS_AUTHORITY",
    "StageKind",
    "StageOutcome",
    "OperationsVerdict",
    "StageSpec",
    "OperationsConfig",
    "StageResult",
    "CoverageSummary",
    "ExecutionReport",
    "RepositoryDashboard",
    # config
    "parse_config",
    "load_config",
    # commands
    "CommandRunner",
    "CANONICAL_COMMANDS",
    "resolve_command",
    "subprocess_command_runner",
    # coverage
    "parse_coverage_xml",
    "load_coverage_summary",
    # subjects
    "build_validation_subject",
    # stages
    "execute_stage",
    # checkpoint
    "Checkpoint",
    "CheckpointStore",
    # orchestration
    "RepositoryOperationsOrchestrator",
    "RepositoryOperationsService",
    "build_repository_operations_service",
    # errors
    "RepositoryOperationsError",
    "OperationsConfigError",
    "StageDefinitionError",
    "StageExecutionError",
    "CoverageReportError",
    "CheckpointError",
    "OperationsServiceError",
]
