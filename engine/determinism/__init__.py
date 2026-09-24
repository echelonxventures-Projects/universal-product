"""EC-1 Determinism Framework (EPIC-004) — constitutional determinism, measured.

Proves that identical certified blueprint inputs produce byte-identical outputs
across independent executions (IMP-007 §5). Built additively on the EC-1
Foundation (EPIC-001), Registry Adapter (EPIC-002), and Universal Compiler
(EPIC-003), which it reuses verbatim (Mandatory Rule 4). It writes only to
caller-provided locations and never to the certified corpus (DP-03).

Tasks: TASK-000031 (hermetic build controls), TASK-000032 (reproducibility
harness), TASK-000033 (determinism CI gate).
"""

from __future__ import annotations

from typing import Any

from engine.determinism.errors import (
    BlueprintResolutionError,
    DependencyLockError,
    DeterminismError,
    HermeticViolation,
    NonDeterministicOutputError,
    ReproducibilityError,
    ToolchainError,
)
from engine.determinism.hermetic import (
    NORMALIZED_ENVIRONMENT,
    NORMALIZED_LOCALE,
    NORMALIZED_TIMESTAMP,
    NORMALIZED_TIMEZONE,
    PINNED_PYTHON,
    PYTHON_REQUIRES,
    SOURCE_DATE_EPOCH,
    DependencyLockReport,
    HermeticEnvironment,
    hermetic_env,
)


def __getattr__(name: str) -> Any:
    """Resolve the reproducibility harness on first use rather than at package import.

    ``engine.determinism.reproduce`` is a declared command-line entry point, and a package
    that imports its own ``-m`` target eagerly makes the interpreter load that module twice
    and say so on stderr. Deferring the import keeps one clean invocation plane for the
    BC-2 comparator without changing what ``from engine.determinism import X`` returns.
    """
    import importlib

    # import_module, not ``from engine.determinism import reproduce``: the from-import
    # asks this package for an attribute it does not have yet, which re-enters here.
    reproduce = importlib.import_module("engine.determinism.reproduce")
    try:
        return getattr(reproduce, name)
    except AttributeError as exc:
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}") from exc


__all__ = [
    # hermetic controls
    "hermetic_env",
    "HermeticEnvironment",
    "DependencyLockReport",
    "PINNED_PYTHON",
    "PYTHON_REQUIRES",
    "SOURCE_DATE_EPOCH",
    "NORMALIZED_TIMESTAMP",
    "NORMALIZED_LOCALE",
    "NORMALIZED_TIMEZONE",
    "NORMALIZED_ENVIRONMENT",
    # reproducibility harness
    "double_build",
    "compare_builds",
    "ReproducibilityResult",
    "FileDiff",
    "BlueprintProvider",
    "DirectoryBlueprintProvider",
    "DEFAULT_BLUEPRINTS_DIR",
    "DEFAULT_SIGNING_KEY",
    "CATEGORIES",
    # cross-process initialization independence (BC-2)
    "compare_initialization",
    "initialization_gate",
    "InitializationScenario",
    "ScenarioObservation",
    "InitializationDivergence",
    "InitializationIndependenceResult",
    # errors
    "DeterminismError",
    "ToolchainError",
    "DependencyLockError",
    "HermeticViolation",
    "BlueprintResolutionError",
    "ReproducibilityError",
    "NonDeterministicOutputError",
]
