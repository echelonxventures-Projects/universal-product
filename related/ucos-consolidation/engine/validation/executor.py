"""TASK-000047 — Validation Execution (EPIC-007).

The :class:`ValidationEngine` runs a suite of checks over a normalized
:class:`~engine.validation.contracts.ValidationSubject` and aggregates the
findings into a deterministic :class:`~engine.validation.contracts.ValidationReport`.

Execution is deterministic (IMP-007 §5): checks run in stable id order and the
report embeds no wall-clock or ambient state, so an identical subject yields a
byte-identical report. The verdict is **PASS** iff no *blocking* check failed;
advisory failures are recorded but do not fail the verdict (the acceptance gate
in TASK-000049 consumes this verdict).
"""

from __future__ import annotations

from collections.abc import Iterable

from engine.foundation.obs.logging import get_logger
from engine.foundation.obs.telemetry import trace
from engine.validation.checks import ValidationCheck, default_checks
from engine.validation.contracts import (
    ValidationReport,
    ValidationSubject,
    Verdict,
)

_logger = get_logger("validation.executor")


class ValidationEngine:
    """Runs a deterministic suite of checks over a validation subject."""

    __slots__ = ("_checks",)

    def __init__(self, checks: Iterable[ValidationCheck] | None = None) -> None:
        selected = tuple(checks) if checks is not None else default_checks()
        # Stable id order guarantees deterministic finding ordering.
        self._checks = tuple(sorted(selected, key=lambda c: c.check_id))

    @property
    def check_ids(self) -> tuple[str, ...]:
        return tuple(c.check_id for c in self._checks)

    def validate(self, subject: ValidationSubject) -> ValidationReport:
        """Evaluate every check over ``subject`` and aggregate a report."""
        with trace("validation.validate", target=subject.target_id):
            findings = tuple(check.evaluate(subject) for check in self._checks)
            verdict = Verdict.FAIL if any(f.is_blocking_failure for f in findings) else Verdict.PASS
            report = ValidationReport(
                target_id=subject.target_id,
                blueprint_id=subject.blueprint_id,
                verdict=verdict,
                findings=findings,
            )
        _logger.info(
            "validation.completed",
            target=subject.target_id,
            verdict=verdict.value,
            blocking_failed=len(report.blocking_failures),
        )
        return report


def validate_runtime_unit(unit, *, checks=None) -> ValidationReport:
    """Convenience: validate a runtime unit with the default (or supplied) suite."""
    subject = ValidationSubject.from_runtime_unit(unit)
    return ValidationEngine(checks).validate(subject)


__all__ = ["ValidationEngine", "validate_runtime_unit"]
