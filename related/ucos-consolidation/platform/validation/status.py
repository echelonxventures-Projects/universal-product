"""EC2-TASK-000148 — Validation Derived Status (EC2-EPIC-010).

The deterministic **derived-status** computation for a validation. A validation's
derived status is a **pure function** of its certified
:class:`~engine.validation.contracts.ValidationReport` — it consults no wall-clock and
no external state, so an identical report always yields an identical
:class:`DerivedValidationStatus` and an identical fingerprint (P5). It re-derives no
verdict; it summarizes the certified verdict into a console posture:

    * ``REJECTED``                 — the report was not accepted (a blocking failure).
    * ``ACCEPTED_WITH_ADVISORIES`` — accepted, but one or more advisory checks failed.
    * ``ACCEPTED``                 — accepted with no advisory failures.

This module records/enacts nothing; it derives.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from platform.foundation.contracts import content_hash
from platform.validation.errors import ValidationStatusError
from typing import Any

from engine.validation.contracts import ValidationReport


class ValidationPosture(str, Enum):
    """The deterministic derived posture of a validation (a summary of the verdict)."""

    REJECTED = "rejected"
    ACCEPTED_WITH_ADVISORIES = "accepted-with-advisories"
    ACCEPTED = "accepted"


@dataclass(frozen=True, slots=True)
class DerivedValidationStatus:
    """An immutable, content-addressed derived validation status (pure function output)."""

    target_id: str
    blueprint_id: str
    verdict: str
    accepted: bool
    posture: ValidationPosture
    blocking_failed: int
    advisory_failed: int
    status_id: str = ""

    @classmethod
    def create(
        cls,
        *,
        target_id: str,
        blueprint_id: str,
        verdict: str,
        accepted: bool,
        posture: ValidationPosture,
        blocking_failed: int,
        advisory_failed: int,
    ) -> DerivedValidationStatus:
        core = {
            "target_id": target_id,
            "blueprint_id": blueprint_id,
            "verdict": verdict,
            "accepted": accepted,
            "posture": posture.value,
            "blocking_failed": blocking_failed,
            "advisory_failed": advisory_failed,
        }
        return cls(
            target_id=target_id,
            blueprint_id=blueprint_id,
            verdict=verdict,
            accepted=accepted,
            posture=posture,
            blocking_failed=blocking_failed,
            advisory_failed=advisory_failed,
            status_id=f"UCOS-VDST-{content_hash(core)[:16]}",
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "status_id": self.status_id,
            "target_id": self.target_id,
            "blueprint_id": self.blueprint_id,
            "verdict": self.verdict,
            "accepted": self.accepted,
            "posture": self.posture.value,
            "blocking_failed": self.blocking_failed,
            "advisory_failed": self.advisory_failed,
        }

    def fingerprint(self) -> str:
        return content_hash(self.to_dict())


def _posture_for(report: ValidationReport) -> ValidationPosture:
    if not report.accepted:
        return ValidationPosture.REJECTED
    if report.advisory_failures:
        return ValidationPosture.ACCEPTED_WITH_ADVISORIES
    return ValidationPosture.ACCEPTED


def derive_status(report: ValidationReport) -> DerivedValidationStatus:
    """Derive a deterministic :class:`DerivedValidationStatus` from a report (pure)."""
    if not isinstance(report, ValidationReport):
        raise ValidationStatusError("status derivation requires a ValidationReport")
    counts = report.counts()
    return DerivedValidationStatus.create(
        target_id=report.target_id,
        blueprint_id=report.blueprint_id,
        verdict=report.verdict.value,
        accepted=report.accepted,
        posture=_posture_for(report),
        blocking_failed=counts["blocking_failed"],
        advisory_failed=counts["advisory_failed"],
    )


__all__ = [
    "ValidationPosture",
    "DerivedValidationStatus",
    "derive_status",
]
