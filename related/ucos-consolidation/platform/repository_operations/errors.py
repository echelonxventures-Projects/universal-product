"""EPIC-PLAT-003 — Repository Operations Automation error taxonomy (Terminal T5).

The **Repository Operations Runtime** is the platform-layer *conductor* for Terminal
T5: it performs complete repository operational verification by **orchestrating the
existing canonical infrastructure** — the ``verify.sh`` / ``doctor.sh`` /
``bootstrap.sh`` entry points, the ``Makefile`` targets, and the certified EC-1
Acceptance / Validation / Certification engines — from a single, configuration-driven,
deterministic, resumable command. It creates **no parallel tooling**: every check it
runs is delegated to a canonical engine or a canonical script.

It reuses the EC-1 / Platform Foundation error discipline additively — it does not
fork or modify it. Every error is rooted in
:class:`~platform.foundation.errors.PlatformError` (itself rooted in the certified EC-1
:class:`~engine.foundation.obs.errors.FoundationError`), carries a stable,
category-prefixed ``code`` (``EC2-ROPS-*``) and structured, non-secret ``context`` so
failures are auditable (PL-02, IP-12) and machine-consumable.

The runtime is strictly *additive* and *record-only*: it consumes the certified
engines and the canonical scripts through their published surfaces only, mutates no
subject, invents no verdict (TP-01 — it aggregates the outcomes the canonical engines
produce), and never writes to the certified corpus (DP-03).
"""

from __future__ import annotations

from platform.foundation.errors import PlatformError


class RepositoryOperationsError(PlatformError):
    """Base class for all EC-2 Repository Operations Runtime errors (EPIC-PLAT-003)."""

    code = "EC2-ROPS-000"


class OperationsConfigError(RepositoryOperationsError):
    """The repository-operations configuration is missing, unreadable, or malformed."""

    code = "EC2-ROPS-CONFIG-001"


class StageDefinitionError(RepositoryOperationsError):
    """A pipeline stage declaration is malformed or names a non-canonical command."""

    code = "EC2-ROPS-STAGE-001"


class StageExecutionError(RepositoryOperationsError):
    """A pipeline stage could not be executed because its inputs are malformed.

    Raised for a *programming/configuration* fault (e.g. an acceptance stage without a
    ``facts`` mapping), never for a legitimate fail-closed verdict — a rejected
    repository or a below-threshold coverage report is reported as a FAILED
    :class:`~platform.repository_operations.contracts.StageResult`, not an exception.
    """

    code = "EC2-ROPS-EXEC-001"


class CoverageReportError(RepositoryOperationsError):
    """A coverage report (``coverage.xml``) is present but could not be parsed."""

    code = "EC2-ROPS-COVERAGE-001"


class CheckpointError(RepositoryOperationsError):
    """A resumable-run checkpoint could not be read, is malformed, or could not be saved."""

    code = "EC2-ROPS-CHECKPOINT-001"


class OperationsServiceError(RepositoryOperationsError):
    """The repository-operations service/orchestrator could not be composed."""

    code = "EC2-ROPS-SERVICE-001"


__all__ = [
    "RepositoryOperationsError",
    "OperationsConfigError",
    "StageDefinitionError",
    "StageExecutionError",
    "CoverageReportError",
    "CheckpointError",
    "OperationsServiceError",
]
