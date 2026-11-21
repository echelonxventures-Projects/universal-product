"""TASK-000003 — Frozen-path guard.

Enforces DP-03 / C-01: the certified corpus is read-only to implementation. Any
change touching ``00-BOOK/``, ``00-SOURCE/``, or ``99-FREEZE/`` is a security
violation. Usable as a library (:func:`assert_no_frozen_write`) and as a CLI
(``ec1-frozen-guard``) for pre-commit hooks and CI.

What this guard protects, and what it does NOT prohibit
-------------------------------------------------------
It protects an **immutable historical baseline**: the certified corpus is the
append-only record the system evolved *from*, so rewriting it would falsify
history rather than advance it. It does not place the corpus outside evolution.
The forward channel is supersession — a new object carrying new identity and a
lineage edge to what it supersedes (CEP-007 XIII), or amendment of the governing
instrument (CEP-009), continuing through the Article-14 perpetual cycle
(``engine/uckp/evolution.py``). Identity is immutable, history is append-only,
and evolution is unlimited through those channels; only in-place modification of
a certified artifact is refused.

Stated because a prohibition that names no channel reads as a prohibition on
change itself (UNIVERSAL-LIFECYCLE-SEMANTIC-RESCAN-REGISTER.md §5). Behaviour is
unchanged by that clarification: no prefix is removed and no write is admitted.
"""

from __future__ import annotations

import sys
from collections.abc import Iterable

from engine.foundation.obs.errors import SecurityViolation

FROZEN_PREFIXES: tuple[str, ...] = ("00-BOOK/", "00-SOURCE/", "99-FREEZE/")


def _normalize(path: str) -> str:
    """Normalize to a repo-relative POSIX path for prefix comparison."""
    normalized = str(path).strip().replace("\\", "/")
    while normalized.startswith("./"):
        normalized = normalized[2:]
    normalized = normalized.lstrip("/")
    return normalized


def find_frozen_writes(paths: Iterable[str]) -> list[str]:
    """Return the subset of ``paths`` that fall under a frozen prefix."""
    violations: list[str] = []
    for path in paths:
        normalized = _normalize(path)
        if not normalized:
            continue
        if any(
            normalized == prefix.rstrip("/") or normalized.startswith(prefix)
            for prefix in FROZEN_PREFIXES
        ):
            violations.append(normalized)
    return violations


def assert_no_frozen_write(paths: Iterable[str]) -> None:
    """Raise :class:`SecurityViolation` if any path targets the frozen corpus."""
    violations = find_frozen_writes(paths)
    if violations:
        raise SecurityViolation(
            "writes to the read-only certified corpus are forbidden (DP-03)",
            paths=violations,
        )


def main(argv: list[str] | None = None) -> int:
    """CLI entry point. Paths come from argv and/or ``--stdin``.

    Returns 0 when clean, 1 when a frozen-path write is detected.
    """
    args = list(sys.argv[1:] if argv is None else argv)
    paths: list[str] = []
    if "--stdin" in args:
        args.remove("--stdin")
        paths.extend(line.strip() for line in sys.stdin.read().splitlines() if line.strip())
    paths.extend(args)

    violations = find_frozen_writes(paths)
    if violations:
        print(
            "EC-1 frozen-path guard: writes to the read-only corpus are forbidden (DP-03):",
            file=sys.stderr,
        )
        for path in violations:
            print(f"  - {path}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())


__all__ = ["FROZEN_PREFIXES", "find_frozen_writes", "assert_no_frozen_write", "main"]
