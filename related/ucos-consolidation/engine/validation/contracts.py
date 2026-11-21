"""TASK-000046 — Validation Contracts (EPIC-007).

The value types that flow across the Validation Layer boundary. Every type is
**immutable, typed, deterministic, and serializable** and holds no runtime state:

    * :class:`Severity` — whether a check is acceptance-blocking or advisory.
    * :class:`CheckStatus` — the outcome of a single check.
    * :class:`Verdict` — the aggregate verdict of a report.
    * :class:`ValidationRequest` — a request to validate a target.
    * :class:`ValidationSubject` — the normalized, type-independent projection of a
      generated artifact that checks evaluate (built from a runtime unit or raw
      fields), so validation is decoupled from the producer.
    * :class:`ValidationFinding` — the immutable outcome of one check.
    * :class:`ValidationReport` — the ordered, deterministic aggregate.

The subject is normalized (like the Factory Layer's classification) so the same
checks validate any generated artifact without per-type branches.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field
from enum import Enum
from typing import TYPE_CHECKING, Any

from engine.validation.errors import ValidationSubjectError

if TYPE_CHECKING:  # pragma: no cover - typing only
    from engine.runtime.assembly import RuntimeUnit

#: The semantic version of the Validation Layer contract surface (AR-03/PL-05).
VALIDATION_CONTRACT_VERSION = "1.0.0"


class Severity(str, Enum):
    """Whether a failing check blocks acceptance or is merely advisory."""

    BLOCKING = "blocking"
    ADVISORY = "advisory"


class CheckStatus(str, Enum):
    """The outcome of a single validation check."""

    PASS = "pass"  # noqa: S105 — enum member, not a credential
    FAIL = "fail"


class Verdict(str, Enum):
    """The aggregate verdict of a validation report."""

    PASS = "pass"  # noqa: S105 — enum member, not a credential
    FAIL = "fail"


@dataclass(frozen=True, slots=True)
class ValidationRequest:
    """An immutable request to validate a target (no runtime state)."""

    target_id: str
    strict: bool = False

    def to_dict(self) -> dict[str, Any]:
        return {"target_id": self.target_id, "strict": self.strict}


@dataclass(frozen=True, slots=True)
class ValidationFinding:
    """The immutable outcome of a single validation check."""

    check_id: str
    severity: Severity
    status: CheckStatus
    message: str = ""
    details: Mapping[str, Any] = field(default_factory=dict)

    @property
    def passed(self) -> bool:
        return self.status is CheckStatus.PASS

    @property
    def is_blocking_failure(self) -> bool:
        return self.status is CheckStatus.FAIL and self.severity is Severity.BLOCKING

    def to_dict(self) -> dict[str, Any]:
        return {
            "check_id": self.check_id,
            "severity": self.severity.value,
            "status": self.status.value,
            "message": self.message,
            "details": dict(self.details),
        }


@dataclass(frozen=True, slots=True)
class ValidationReport:
    """The ordered, deterministic aggregate of a validation run."""

    target_id: str
    blueprint_id: str
    verdict: Verdict
    findings: tuple[ValidationFinding, ...]

    @property
    def accepted(self) -> bool:
        return self.verdict is Verdict.PASS

    @property
    def blocking_failures(self) -> tuple[ValidationFinding, ...]:
        return tuple(f for f in self.findings if f.is_blocking_failure)

    @property
    def advisory_failures(self) -> tuple[ValidationFinding, ...]:
        return tuple(
            f
            for f in self.findings
            if f.status is CheckStatus.FAIL and f.severity is Severity.ADVISORY
        )

    def counts(self) -> dict[str, int]:
        passed = sum(1 for f in self.findings if f.passed)
        return {
            "total": len(self.findings),
            "passed": passed,
            "failed": len(self.findings) - passed,
            "blocking_failed": len(self.blocking_failures),
            "advisory_failed": len(self.advisory_failures),
        }

    def to_dict(self) -> dict[str, Any]:
        return {
            "target_id": self.target_id,
            "blueprint_id": self.blueprint_id,
            "verdict": self.verdict.value,
            "accepted": self.accepted,
            "counts": self.counts(),
            "findings": [f.to_dict() for f in self.findings],
        }


@dataclass(frozen=True, slots=True)
class ValidationSubject:
    """A normalized, type-independent projection of a generated artifact."""

    target_id: str
    blueprint_id: str
    provenance_chain: tuple[str, ...]
    signature: Mapping[str, Any]
    sbom: Mapping[str, Any]
    dependency_closure: tuple[Mapping[str, Any], ...]
    disclosure: Mapping[str, Any] | None
    package_sha256: str
    image_reference: str
    runtime_id: str | None = None
    blueprint_class: str | None = None

    @classmethod
    def from_runtime_unit(
        cls, unit: RuntimeUnit, *, blueprint_class: str | None = None
    ) -> ValidationSubject:
        """Project a :class:`~engine.runtime.assembly.RuntimeUnit` into a subject."""
        if not getattr(unit, "runtime_id", None):
            raise ValidationSubjectError("runtime unit has no runtime_id")
        return cls(
            target_id=unit.runtime_id,
            blueprint_id=unit.blueprint_id,
            provenance_chain=tuple(unit.provenance_chain),
            signature=dict(unit.signature),
            sbom=dict(unit.sbom),
            dependency_closure=tuple(dict(e) for e in unit.closure_records()),
            disclosure=dict(unit.disclosure) if unit.disclosure is not None else None,
            package_sha256=unit.package_sha256,
            image_reference=unit.image_reference,
            runtime_id=unit.runtime_id,
            blueprint_class=blueprint_class,
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "target_id": self.target_id,
            "blueprint_id": self.blueprint_id,
            "blueprint_class": self.blueprint_class,
            "provenance_chain": list(self.provenance_chain),
            "signature": dict(self.signature),
            "sbom": dict(self.sbom),
            "dependency_closure": [dict(e) for e in self.dependency_closure],
            "disclosure": dict(self.disclosure) if self.disclosure is not None else None,
            "package_sha256": self.package_sha256,
            "image_reference": self.image_reference,
            "runtime_id": self.runtime_id,
        }


__all__ = [
    "VALIDATION_CONTRACT_VERSION",
    "Severity",
    "CheckStatus",
    "Verdict",
    "ValidationRequest",
    "ValidationFinding",
    "ValidationReport",
    "ValidationSubject",
]
