"""TASK-000031 — Hermetic build controls (EPIC-004, IMP-007 §5).

Determinism and reproducibility are compilation invariants: identical registered
inputs and a **pinned toolchain** yield byte-identical outputs (fixed ordering,
normalized timestamps, pinned dependency versions, no ambient state). This module
makes those preconditions **explicit, measurable, and enforceable** rather than
assumed (Mandatory Rule 5).

:func:`hermetic_env` returns a :class:`HermeticEnvironment` — a frozen, hashable
description of the normalized build environment plus the controls that verify and
apply it:

    * **pinned toolchain verification** — the running interpreter satisfies the
      pinned minimum, and the compiler toolchain identity/version are fixed;
    * **normalized timestamps** — a single ``SOURCE_DATE_EPOCH`` (1970-01-01T00:00Z)
      so no wall-clock leaks into artifacts;
    * **deterministic ordering** — a canonical sort helper used wherever order
      would otherwise be ambient;
    * **deterministic serialization validation** — round-trips an IR through the
      compiler serializer and asserts byte-stability;
    * **environment / locale / timezone normalization** — ``LC_ALL=C``, ``TZ=UTC``,
      ``PYTHONHASHSEED=0`` … applied within a restoring context manager;
    * **file ordering normalization** — deterministic path ordering;
    * **dependency locking verification** — the project declares zero unpinned
      runtime dependencies and only exactly-pinned (``==``) dev dependencies.

Two independently constructed hermetic environments are identical (same
``fingerprint``), so two clean environments produce identical compiler inputs.
Stdlib-only (TP-04/TP-05).
"""

from __future__ import annotations

import hashlib
import json
import os
import sys
import time
import tomllib
from collections.abc import Iterable, Iterator
from contextlib import contextmanager
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, TypeVar

from engine.compiler.packaging import COMPILER_TOOLCHAIN, TOOLCHAIN_VERSION
from engine.compiler.serialization import deserialize, serialize
from engine.determinism.errors import (
    DependencyLockError,
    HermeticViolation,
    ToolchainError,
)
from engine.foundation.obs.logging import get_logger

_logger = get_logger("determinism.hermetic")

_T = TypeVar("_T")

# --- pinned normalization constants (IMP-007 §5) ----------------------------- #

#: Pinned minimum interpreter (matches pyproject ``requires-python = ">=3.12"``).
PINNED_PYTHON: tuple[int, int] = (3, 12)
PYTHON_REQUIRES = ">=3.12"

#: Normalized, wall-clock-free build epoch and its ISO rendering.
SOURCE_DATE_EPOCH = 0
NORMALIZED_TIMESTAMP = "1970-01-01T00:00:00+00:00"

#: Normalized locale and timezone (stable collation + no local-time drift).
NORMALIZED_LOCALE = "C"
NORMALIZED_TIMEZONE = "UTC"

#: The canonical, normalized process environment for a hermetic build.
NORMALIZED_ENVIRONMENT: dict[str, str] = {
    "LC_ALL": NORMALIZED_LOCALE,
    "LANG": NORMALIZED_LOCALE,
    "LC_CTYPE": NORMALIZED_LOCALE,
    "TZ": NORMALIZED_TIMEZONE,
    "PYTHONHASHSEED": "0",
    "PYTHONUTF8": "1",
    "SOURCE_DATE_EPOCH": str(SOURCE_DATE_EPOCH),
}


def _repository_root() -> Path:
    """``engine/determinism/hermetic.py`` → parents[2] is the repository root."""
    return Path(__file__).resolve().parents[2]


@dataclass(frozen=True, slots=True)
class DependencyLockReport:
    """The result of verifying the project's dependency locking (IMP-007 §5)."""

    runtime_dependencies: tuple[str, ...]
    dev_dependencies: tuple[str, ...]
    locked: bool

    def to_dict(self) -> dict[str, Any]:
        return {
            "runtime_dependencies": list(self.runtime_dependencies),
            "dev_dependencies": list(self.dev_dependencies),
            "locked": self.locked,
        }


@dataclass(frozen=True, slots=True)
class HermeticEnvironment:
    """An immutable, hashable description of a normalized, reproducible build env."""

    toolchain: str
    toolchain_version: str
    python_requires: str
    source_date_epoch: int
    normalized_timestamp: str
    locale: str
    timezone: str
    _environment: tuple[tuple[str, str], ...] = field(default_factory=tuple)

    # -- normalized views ------------------------------------------------------

    def normalized_environment(self) -> dict[str, str]:
        """The canonical process-environment overrides for a hermetic build."""
        return dict(self._environment)

    def timestamp(self) -> str:
        """The single normalized timestamp; no wall-clock is ever consulted."""
        return self.normalized_timestamp

    # -- deterministic ordering (IMP-007 §5) -----------------------------------

    @staticmethod
    def order(items: Iterable[_T], *, key: Any = None) -> list[_T]:
        """Return ``items`` in a deterministic (sorted) order."""
        return sorted(items, key=key) if key is not None else sorted(items)

    @staticmethod
    def order_paths(paths: Iterable[str | Path]) -> list[str]:
        """Return file paths in deterministic, normalized POSIX order."""
        return sorted(Path(p).as_posix() for p in paths)

    # -- pinned toolchain verification -----------------------------------------

    def verify_toolchain(self) -> None:
        """Verify the running interpreter and compiler toolchain are pinned."""
        current = sys.version_info[:2]
        if current < PINNED_PYTHON:
            raise ToolchainError(
                "interpreter does not satisfy the pinned toolchain",
                required=self.python_requires,
                found=f"{current[0]}.{current[1]}",
            )
        if self.toolchain != COMPILER_TOOLCHAIN or self.toolchain_version != TOOLCHAIN_VERSION:
            raise ToolchainError(
                "compiler toolchain identity drifted from the pinned value",
                expected=f"{COMPILER_TOOLCHAIN}@{TOOLCHAIN_VERSION}",
                found=f"{self.toolchain}@{self.toolchain_version}",
            )

    # -- dependency locking verification ---------------------------------------

    def verify_dependency_lock(self, pyproject: str | Path | None = None) -> DependencyLockReport:
        """Verify runtime deps are absent and dev deps are exactly pinned (``==``)."""
        path = Path(pyproject) if pyproject is not None else _repository_root() / "pyproject.toml"
        if not path.is_file():
            raise DependencyLockError("pyproject.toml not found", path=str(path))
        try:
            data = tomllib.loads(path.read_text(encoding="utf-8"))
        except tomllib.TOMLDecodeError as exc:  # pragma: no cover - defensive
            raise DependencyLockError("pyproject.toml is not valid TOML", detail=str(exc)) from exc

        project = data.get("project", {})
        runtime = tuple(project.get("dependencies", []) or ())
        dev = tuple((project.get("optional-dependencies", {}) or {}).get("dev", []) or ())

        unpinned_dev = [spec for spec in dev if "==" not in spec]
        locked = not runtime and not unpinned_dev
        if not locked:
            raise DependencyLockError(
                "dependencies are not fully locked for a reproducible build",
                runtime=list(runtime),
                unpinned_dev=unpinned_dev,
            )
        return DependencyLockReport(runtime_dependencies=runtime, dev_dependencies=dev, locked=True)

    # -- deterministic serialization validation --------------------------------

    def validate_serialization(self, ir: Any) -> bool:
        """Round-trip ``ir`` through the compiler serializer; assert byte-stability."""
        once = serialize(ir)
        twice = serialize(deserialize(once))
        if once != twice:
            raise HermeticViolation(
                "IR serialization is not byte-stable under round-trip",
                blueprint_id=getattr(ir, "blueprint_id", None),
            )
        return True

    # -- environment application (restoring) -----------------------------------

    @contextmanager
    def apply(self) -> Iterator[HermeticEnvironment]:
        """Apply the normalized environment for the duration of the context.

        Sets locale/timezone/hash-seed/epoch environment variables (and refreshes
        the process timezone where supported), restoring the prior state on exit.
        The compiler itself consults only sorted orderings and no wall-clock, so
        this normalization guarantees identical inputs to spawned toolchains and
        removes ambient drift.
        """
        overrides = self.normalized_environment()
        previous: dict[str, str | None] = {k: os.environ.get(k) for k in overrides}
        os.environ.update(overrides)
        _refresh_timezone()
        try:
            yield self
        finally:
            for key, value in previous.items():
                if value is None:
                    os.environ.pop(key, None)
                else:
                    os.environ[key] = value
            _refresh_timezone()

    # -- evidence --------------------------------------------------------------

    def to_dict(self) -> dict[str, Any]:
        """A canonical, serialisable description (basis for the fingerprint)."""
        return {
            "toolchain": self.toolchain,
            "toolchain_version": self.toolchain_version,
            "python_requires": self.python_requires,
            "source_date_epoch": self.source_date_epoch,
            "normalized_timestamp": self.normalized_timestamp,
            "locale": self.locale,
            "timezone": self.timezone,
            "environment": dict(self._environment),
        }

    def fingerprint(self) -> str:
        """A stable SHA-256 over the environment definition (evidence anchor)."""
        canonical = json.dumps(
            self.to_dict(), sort_keys=True, separators=(",", ":"), ensure_ascii=False
        )
        return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def _refresh_timezone() -> None:
    """Refresh the process timezone from ``TZ`` where the platform supports it."""
    tzset = getattr(time, "tzset", None)
    if tzset is not None:  # pragma: no branch - present on POSIX
        tzset()


def hermetic_env() -> HermeticEnvironment:
    """Construct the canonical hermetic build environment (verified toolchain).

    The returned environment is fully deterministic: two independent calls yield
    equal environments with an identical :meth:`~HermeticEnvironment.fingerprint`,
    so two clean environments produce identical compiler inputs.
    """
    env = HermeticEnvironment(
        toolchain=COMPILER_TOOLCHAIN,
        toolchain_version=TOOLCHAIN_VERSION,
        python_requires=PYTHON_REQUIRES,
        source_date_epoch=SOURCE_DATE_EPOCH,
        normalized_timestamp=NORMALIZED_TIMESTAMP,
        locale=NORMALIZED_LOCALE,
        timezone=NORMALIZED_TIMEZONE,
        _environment=tuple(sorted(NORMALIZED_ENVIRONMENT.items())),
    )
    env.verify_toolchain()
    _logger.info("determinism.hermetic.ready", fingerprint=env.fingerprint())
    return env


__all__ = [
    "PINNED_PYTHON",
    "PYTHON_REQUIRES",
    "SOURCE_DATE_EPOCH",
    "NORMALIZED_TIMESTAMP",
    "NORMALIZED_LOCALE",
    "NORMALIZED_TIMEZONE",
    "NORMALIZED_ENVIRONMENT",
    "DependencyLockReport",
    "HermeticEnvironment",
    "hermetic_env",
]
