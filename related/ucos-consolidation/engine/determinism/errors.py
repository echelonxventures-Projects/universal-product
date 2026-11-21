"""TASK-000031 — Determinism Framework error taxonomy (EPIC-004).

The Determinism Framework reuses the EC-1 Foundation error discipline
(TASK-000006): every error is rooted in :class:`FoundationError`, carries a
stable, category-prefixed ``code`` and structured, non-secret ``context`` so
failures are auditable (PL-02, IP-12) and machine-consumable.

Determinism is *measured, not assumed* (Mandatory Rule 5): when a hermetic
control is breached or a reproducibility divergence is detected, the framework
fails loudly and every failure carries evidence (Mandatory Rule 6).
"""

from __future__ import annotations

from engine.foundation.obs.errors import FoundationError


class DeterminismError(FoundationError):
    """Base class for all Determinism Framework errors (EPIC-004)."""

    code = "DET-000"


class ToolchainError(DeterminismError):
    """The active toolchain does not match the pinned specification (TASK-000031)."""

    code = "DET-TOOLCHAIN-001"


class DependencyLockError(DeterminismError):
    """Runtime/dev dependencies are unpinned or unexpectedly present (TASK-000031)."""

    code = "DET-DEPLOCK-001"


class HermeticViolation(DeterminismError):
    """A hermetic-build invariant was violated (TASK-000031)."""

    code = "DET-HERMETIC-001"


class BlueprintResolutionError(DeterminismError):
    """A blueprint id could not be resolved to an input document (TASK-000032)."""

    code = "DET-BP-404"


class ReproducibilityError(DeterminismError):
    """A build required by the reproducibility harness failed (TASK-000032)."""

    code = "DET-REPRO-001"


class NonDeterministicOutputError(DeterminismError):
    """Independent executions produced divergent (non-byte-identical) output.

    Raised only when a caller opts into strict mode; by default the harness
    reports divergence as evidence rather than raising (Mandatory Rule 6).
    """

    code = "DET-DIVERGENCE-001"


__all__ = [
    "DeterminismError",
    "ToolchainError",
    "DependencyLockError",
    "HermeticViolation",
    "BlueprintResolutionError",
    "ReproducibilityError",
    "NonDeterministicOutputError",
]
