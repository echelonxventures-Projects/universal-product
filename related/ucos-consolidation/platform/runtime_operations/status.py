"""EC2-TASK-000167 — Runtime Operation Derived Status & Governance (EC2-EPIC-012).

The deterministic **derived evaluations** over a governed runtime operation. Each is a
**pure function** of an immutable
:class:`~platform.runtime_operations.contracts.RuntimeOperationRecord` (and the certified
EC-1 descriptor it carries) — it consults no wall-clock and no external state, so an
identical operation always yields an identical result and an identical fingerprint (P5).
None re-derives a descriptor; each summarizes / audits the recorded operation:

    * **Status** (:func:`derive_status`) — normalizes the operation into a
      :class:`RuntimeOperationPosture` (governance-safe state inspection).
    * **Governance** (:func:`validate_governance`) — a deterministic compliance evaluation
      of the recorded operation against the runtime-operations governance rules, reporting
      every :class:`GovernanceViolation` (fail-closed :class:`GovernanceAssessment`).

This module records/enacts nothing; it derives.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from platform.foundation.contracts import content_hash
from platform.runtime_operations.contracts import RuntimeOperationKind, RuntimeOperationRecord
from platform.runtime_operations.errors import RuntimeOperationStatusError
from typing import Any

from engine.runtime.disclosure import disclosure_present

#: The authority every certified deployable descriptor carries (DE-05, record-only).
_ENGINEERING_EXECUTION_ONLY = "ENGINEERING-EXECUTION-ONLY"


class RuntimeOperationPosture(str, Enum):
    """The deterministic derived posture of a governed runtime operation."""

    DEPLOY_GOVERNED = "deploy-governed"
    ROLLBACK_REVERSIBLE = "rollback-reversible"
    ROLLBACK_IRREVERSIBLE = "rollback-irreversible"


# --------------------------------------------------------------------------- #
# Derived status.                                                             #
# --------------------------------------------------------------------------- #


@dataclass(frozen=True, slots=True)
class DerivedRuntimeOperationStatus:
    """An immutable, content-addressed derived operation status (pure function output)."""

    operation_id: str
    runtime_id: str
    kind: str
    environment: str
    certified: bool
    reversible: bool
    posture: RuntimeOperationPosture
    status_id: str = ""

    @classmethod
    def create(
        cls,
        *,
        operation_id: str,
        runtime_id: str,
        kind: str,
        environment: str,
        certified: bool,
        reversible: bool,
        posture: RuntimeOperationPosture,
    ) -> DerivedRuntimeOperationStatus:
        core = {
            "operation_id": operation_id,
            "runtime_id": runtime_id,
            "kind": kind,
            "environment": environment,
            "certified": certified,
            "reversible": reversible,
            "posture": posture.value,
        }
        return cls(
            operation_id=operation_id,
            runtime_id=runtime_id,
            kind=kind,
            environment=environment,
            certified=certified,
            reversible=reversible,
            posture=posture,
            status_id=f"UCOS-RODS-{content_hash(core)[:16]}",
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "status_id": self.status_id,
            "operation_id": self.operation_id,
            "runtime_id": self.runtime_id,
            "kind": self.kind,
            "environment": self.environment,
            "certified": self.certified,
            "reversible": self.reversible,
            "posture": self.posture.value,
        }

    def fingerprint(self) -> str:
        return content_hash(self.to_dict())


def _require_record(record: RuntimeOperationRecord, what: str) -> None:
    if not isinstance(record, RuntimeOperationRecord):
        raise RuntimeOperationStatusError(f"{what} requires a RuntimeOperationRecord")


def _posture_for(record: RuntimeOperationRecord) -> RuntimeOperationPosture:
    if record.kind is RuntimeOperationKind.DEPLOY:
        return RuntimeOperationPosture.DEPLOY_GOVERNED
    return (
        RuntimeOperationPosture.ROLLBACK_REVERSIBLE
        if record.reversible
        else RuntimeOperationPosture.ROLLBACK_IRREVERSIBLE
    )


def derive_status(record: RuntimeOperationRecord) -> DerivedRuntimeOperationStatus:
    """Derive a deterministic :class:`DerivedRuntimeOperationStatus` from a record (pure)."""
    _require_record(record, "status derivation")
    return DerivedRuntimeOperationStatus.create(
        operation_id=record.operation_id,
        runtime_id=record.runtime_id,
        kind=record.kind.value,
        environment=record.environment,
        certified=record.certified,
        reversible=record.reversible,
        posture=_posture_for(record),
    )


# --------------------------------------------------------------------------- #
# Governance validation.                                                      #
# --------------------------------------------------------------------------- #

#: The deterministic runtime-operations governance rules, in stable evaluation order.
GOVERNANCE_RULES: tuple[str, ...] = (
    "certified",
    "descriptor-matches-unit",
    "authority-execution-only",
    "disclosure-present",
    "provenance-present",
    "reversible-when-rollback",
)


@dataclass(frozen=True, slots=True)
class GovernanceViolation:
    """An immutable governance-rule violation (rule id + human-readable message)."""

    rule: str
    message: str

    def to_dict(self) -> dict[str, Any]:
        return {"rule": self.rule, "message": self.message}


@dataclass(frozen=True, slots=True)
class GovernanceAssessment:
    """An immutable, content-addressed runtime-operation governance compliance assessment."""

    operation_id: str
    runtime_id: str
    compliant: bool
    rules_evaluated: tuple[str, ...]
    violations: tuple[GovernanceViolation, ...]
    assessment_id: str = ""

    @classmethod
    def create(
        cls,
        *,
        operation_id: str,
        runtime_id: str,
        rules_evaluated: tuple[str, ...],
        violations: tuple[GovernanceViolation, ...],
    ) -> GovernanceAssessment:
        compliant = not violations
        core = {
            "operation_id": operation_id,
            "runtime_id": runtime_id,
            "compliant": compliant,
            "rules_evaluated": list(rules_evaluated),
            "violations": [v.to_dict() for v in violations],
        }
        return cls(
            operation_id=operation_id,
            runtime_id=runtime_id,
            compliant=compliant,
            rules_evaluated=rules_evaluated,
            violations=violations,
            assessment_id=f"UCOS-ROGV-{content_hash(core)[:16]}",
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "assessment_id": self.assessment_id,
            "operation_id": self.operation_id,
            "runtime_id": self.runtime_id,
            "compliant": self.compliant,
            "rules_evaluated": list(self.rules_evaluated),
            "violations": [v.to_dict() for v in self.violations],
        }

    def fingerprint(self) -> str:
        return content_hash(self.to_dict())


def validate_governance(record: RuntimeOperationRecord) -> GovernanceAssessment:
    """Evaluate the runtime-operations governance rules over a record (pure, fail-closed).

    Reports a violation for every governance rule the recorded operation does not satisfy:
    the unit is CERTIFIED, the governing descriptor targets exactly this unit, the
    descriptor carries the ``ENGINEERING-EXECUTION-ONLY`` authority (DE-05), the EC-1
    provisional-state disclosure is present, the runtime unit's provenance chain is
    present, and a rollback operation is reversible (IP-08).
    """
    _require_record(record, "governance validation")
    descriptor = record.descriptor
    disclosure = descriptor.disclosure
    violations: list[GovernanceViolation] = []
    if not record.certified:
        violations.append(GovernanceViolation("certified", "runtime unit is not CERTIFIED"))
    if descriptor.runtime_id != record.runtime_id:
        violations.append(
            GovernanceViolation(
                "descriptor-matches-unit", "descriptor runtime id does not match the unit"
            )
        )
    if disclosure.get("authority") != _ENGINEERING_EXECUTION_ONLY:
        violations.append(
            GovernanceViolation(
                "authority-execution-only",
                f"descriptor authority must be {_ENGINEERING_EXECUTION_ONLY!r} (DE-05)",
            )
        )
    if not disclosure_present(disclosure):
        violations.append(
            GovernanceViolation("disclosure-present", "EC-1 provisional-state disclosure is absent")
        )
    if not record.unit.provenance_chain:
        violations.append(
            GovernanceViolation("provenance-present", "runtime unit provenance chain is absent")
        )
    if record.kind is RuntimeOperationKind.ROLLBACK and not record.reversible:
        violations.append(
            GovernanceViolation(
                "reversible-when-rollback", "rollback operation is not reversible (IP-08)"
            )
        )
    return GovernanceAssessment.create(
        operation_id=record.operation_id,
        runtime_id=record.runtime_id,
        rules_evaluated=GOVERNANCE_RULES,
        violations=tuple(violations),
    )


__all__ = [
    "RuntimeOperationPosture",
    "DerivedRuntimeOperationStatus",
    "derive_status",
    "GOVERNANCE_RULES",
    "GovernanceViolation",
    "GovernanceAssessment",
    "validate_governance",
]
