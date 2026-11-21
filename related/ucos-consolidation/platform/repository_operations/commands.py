"""EPIC-PLAT-003 — Canonical command reuse (Terminal T5).

The COMMAND stage **reuses the existing canonical entry points** — it never introduces
parallel tooling. Only the repository-standard scripts and ``make`` targets are
runnable; an arbitrary shell command is refused (fail-closed), which is the mechanism
that guarantees "reuse ``verify.sh`` / ``doctor.sh`` / ``bootstrap.sh`` / ``Makefile``,
do not create parallel tooling".

A :data:`CommandRunner` is any callable that runs a resolved argument vector and returns
its integer exit status. The default runner shells out through the standard library;
tests inject a deterministic in-memory runner (no subprocess), so the orchestration
logic is fully exercised without depending on the host environment.
"""

from __future__ import annotations

import subprocess
from collections.abc import Callable, Sequence
from pathlib import Path
from platform.repository_operations.errors import StageDefinitionError

#: A command runner: given a resolved argv, run it and return its exit status.
CommandRunner = Callable[[Sequence[str]], int]

#: The canonical, allow-listed commands. Each maps a logical name to the argv of an
#: existing repository entry point — reuse only, no parallel tooling. Values are tuples
#: so the mapping is effectively immutable.
CANONICAL_COMMANDS: dict[str, tuple[str, ...]] = {
    "bootstrap": ("./bootstrap.sh",),
    "bootstrap-verify": ("./bootstrap.sh", "--verify"),
    "doctor": ("./doctor.sh",),
    "verify": ("./verify.sh",),
    "verify-full": ("./verify.sh", "--full"),
    "verify-failfast": ("./verify.sh", "--failfast"),
    "make-verify": ("make", "verify"),
    "make-verify-full": ("make", "verify-full"),
    "make-lint": ("make", "lint"),
    "make-test": ("make", "test"),
}


def resolve_command(name: str) -> tuple[str, ...]:
    """Resolve a logical command name to its canonical argv (fail-closed).

    Raises:
        StageDefinitionError: if ``name`` is not one of the canonical, allow-listed
            commands — the guarantee that only existing infrastructure is invoked.
    """
    if name not in CANONICAL_COMMANDS:
        raise StageDefinitionError(
            "unknown or non-canonical command (parallel tooling is not permitted)",
            command=name,
            supported=sorted(CANONICAL_COMMANDS),
        )
    return CANONICAL_COMMANDS[name]


def subprocess_command_runner(repo_root: str | Path) -> CommandRunner:
    """Return a :data:`CommandRunner` that runs argv through the shell at ``repo_root``.

    The runner never uses ``shell=True`` and only ever receives an argv resolved from
    :data:`CANONICAL_COMMANDS`, so it cannot execute an arbitrary command string.
    """
    root = Path(repo_root)

    def _run(argv: Sequence[str]) -> int:
        completed = subprocess.run(  # noqa: S603 - canonical allow-listed argv, no shell
            list(argv),
            cwd=str(root),
            check=False,
        )
        return completed.returncode

    return _run


__all__ = [
    "CommandRunner",
    "CANONICAL_COMMANDS",
    "resolve_command",
    "subprocess_command_runner",
]
