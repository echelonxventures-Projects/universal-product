"""Shared validation primitives — tri-state, fail-closed, gate-ready.

A check is tri-state on purpose. ``True`` is satisfied, ``False`` is violated, and
``None`` is *indeterminate*: the evidence required to decide is absent. An
indeterminate blocking check closes the gate exactly like a violation, because a
verdict that cannot be evidenced may not be asserted (no-fabrication).

Both the Research Validator and the Publication Validator are built from these
primitives, so the two report shapes — and the two gates — are identical.
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass, field
from typing import Any

#: Verdicts. CERTIFIED opens a gate; the other two close it.
VERDICT_CERTIFIED = "CERTIFIED"
VERDICT_INDETERMINATE = "INDETERMINATE"
VERDICT_FAILED = "FAILED"

#: Exit codes, matching the programme-engine convention already used repo-wide:
#: 0 gate open · 1 gate closed · 2 fail-closed abort (no verdict assertable).
EXIT_OPEN = 0
EXIT_CLOSED = 1
EXIT_ABORT = 2


@dataclass(frozen=True, slots=True)
class Check:
    """One validation obligation and its tri-state outcome."""

    check_id: str
    title: str
    obligation: str
    passed: bool | None
    blocking: bool = True
    detail: dict[str, Any] = field(default_factory=dict)

    @property
    def state(self) -> str:
        if self.passed is None:
            return VERDICT_INDETERMINATE
        return "PASS" if self.passed else "FAIL"

    def to_dict(self) -> dict[str, Any]:
        return {
            "check_id": self.check_id,
            "title": self.title,
            "obligation": self.obligation,
            "state": self.state,
            "blocking": self.blocking,
            "detail": self.detail,
        }


@dataclass(frozen=True, slots=True)
class ValidationReport:
    """A deterministic, gate-ready validation report."""

    subject: str
    programme: str
    checks: tuple[Check, ...]

    # -- partitions ------------------------------------------------------------

    def passed(self) -> tuple[Check, ...]:
        return tuple(c for c in self.checks if c.passed is True)

    def failed(self) -> tuple[Check, ...]:
        return tuple(c for c in self.checks if c.passed is False)

    def indeterminate(self) -> tuple[Check, ...]:
        return tuple(c for c in self.checks if c.passed is None)

    def blocking_failures(self) -> tuple[Check, ...]:
        return tuple(c for c in self.checks if c.blocking and c.passed is not True)

    # -- verdict ---------------------------------------------------------------

    @property
    def verdict(self) -> str:
        if any(c.blocking and c.passed is False for c in self.checks):
            return VERDICT_FAILED
        if any(c.blocking and c.passed is None for c in self.checks):
            return VERDICT_INDETERMINATE
        return VERDICT_CERTIFIED

    @property
    def gate_open(self) -> bool:
        return self.verdict == VERDICT_CERTIFIED

    @property
    def exit_code(self) -> int:
        return EXIT_OPEN if self.gate_open else EXIT_CLOSED

    def to_dict(self) -> dict[str, Any]:
        return {
            "subject": self.subject,
            "programme": self.programme,
            "verdict": self.verdict,
            "gate": "OPEN" if self.gate_open else "CLOSED",
            "checks_total": len(self.checks),
            "checks_passed": len(self.passed()),
            "checks_failed": len(self.failed()),
            "checks_indeterminate": len(self.indeterminate()),
            "blocking_failures": [c.check_id for c in self.blocking_failures()],
            "checks": [c.to_dict() for c in self.checks],
        }

    def summary_line(self) -> str:
        return (
            f"{self.programme}: {self.verdict} | "
            f"checks={len(self.passed())}/{len(self.checks)} PASS | "
            f"gate={'OPEN' if self.gate_open else 'CLOSED'}"
        )


def report(subject: str, programme: str, checks: Sequence[Check]) -> ValidationReport:
    """Build a report with checks ordered deterministically by id."""
    return ValidationReport(
        subject=subject,
        programme=programme,
        checks=tuple(sorted(checks, key=lambda c: c.check_id)),
    )


__all__ = [
    "EXIT_ABORT",
    "EXIT_CLOSED",
    "EXIT_OPEN",
    "VERDICT_CERTIFIED",
    "VERDICT_FAILED",
    "VERDICT_INDETERMINATE",
    "Check",
    "ValidationReport",
    "report",
]
