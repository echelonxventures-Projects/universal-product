"""TASK-000049 — Validation Acceptance Gates (EPIC-007).

The acceptance gate turns a :class:`~engine.validation.contracts.ValidationReport`
into an accept/reject **decision**: a report is **accepted** iff its verdict is
PASS — i.e. no *blocking* check failed. Advisory failures never block acceptance
(they are recorded as evidence).

:func:`enforce_acceptance` returns a deterministic :class:`AcceptanceDecision`; in
``strict`` mode a rejected report additionally raises
:class:`~engine.validation.errors.AcceptanceGateError` carrying the failing checks
as evidence (Mandatory Rule 6 — every rejection is auditable).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from engine.foundation.obs.logging import get_logger
from engine.validation.contracts import ValidationReport
from engine.validation.errors import AcceptanceGateError

_logger = get_logger("validation.gate")


@dataclass(frozen=True, slots=True)
class AcceptanceDecision:
    """The immutable outcome of an acceptance gate over a validation report."""

    target_id: str
    blueprint_id: str
    accepted: bool
    verdict: str
    blocking_failures: tuple[str, ...]
    advisory_failures: tuple[str, ...]

    def to_dict(self) -> dict[str, Any]:
        return {
            "target_id": self.target_id,
            "blueprint_id": self.blueprint_id,
            "accepted": self.accepted,
            "verdict": self.verdict,
            "blocking_failures": list(self.blocking_failures),
            "advisory_failures": list(self.advisory_failures),
        }


def enforce_acceptance(report: ValidationReport, *, strict: bool = False) -> AcceptanceDecision:
    """Decide acceptance from ``report``; in strict mode raise on rejection.

    Raises:
        AcceptanceGateError: when ``strict`` and the report is not accepted.
    """
    decision = AcceptanceDecision(
        target_id=report.target_id,
        blueprint_id=report.blueprint_id,
        accepted=report.accepted,
        verdict=report.verdict.value,
        blocking_failures=tuple(f.check_id for f in report.blocking_failures),
        advisory_failures=tuple(f.check_id for f in report.advisory_failures),
    )
    _logger.info(
        "validation.gate.decided",
        target=report.target_id,
        accepted=decision.accepted,
        blocking_failed=len(decision.blocking_failures),
    )
    if strict and not decision.accepted:
        raise AcceptanceGateError(
            "validation acceptance gate rejected the artifact",
            target_id=report.target_id,
            blueprint_id=report.blueprint_id,
            blocking_failures=list(decision.blocking_failures),
        )
    return decision


__all__ = ["AcceptanceDecision", "enforce_acceptance"]
