"""EC2-TASK-000157 — Certification Derived Status, Readiness & Governance (EC2-EPIC-011).

The deterministic **derived evaluations** over a certified certification. Each is a
**pure function** of the certified
:class:`~engine.certification.engine.CertificationDecision` and its immutable
:class:`~engine.certification.contracts.CertificationRecord` — it consults no wall-clock
and no external state, so an identical decision always yields an identical result and an
identical fingerprint (P5). None re-derives a verdict; each summarizes / audits the
certified determination:

    * **Status** (:func:`derive_status`) — normalizes the certified status into a console
      :class:`CertificationPosture` (state inspection, governance-safe output).
    * **Readiness** (:func:`evaluate_readiness`) — a deterministic completeness evaluation
      (readiness indicators → a single fail-closed :class:`CertificationReadiness`).
    * **Governance** (:func:`validate_governance`) — a deterministic compliance evaluation
      of the certified record against the certification governance rules, reporting every
      :class:`GovernanceViolation` (fail-closed :class:`GovernanceAssessment`).

This module records/enacts nothing; it derives.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from platform.certification.errors import CertificationStatusError
from platform.foundation.contracts import content_hash
from typing import Any

from engine.certification.contracts import CERTIFICATION_AUTHORITY, CertificationStatus
from engine.certification.engine import CertificationDecision


class CertificationPosture(str, Enum):
    """The deterministic derived posture of a certification (a summary of the status)."""

    NOT_CERTIFIED = "not-certified"
    CERTIFIED_WITH_ADVISORIES = "certified-with-advisories"
    CERTIFIED = "certified"


# --------------------------------------------------------------------------- #
# Derived status.                                                             #
# --------------------------------------------------------------------------- #


@dataclass(frozen=True, slots=True)
class DerivedCertificationStatus:
    """An immutable, content-addressed derived certification status (pure function output)."""

    certification_id: str
    target_id: str
    blueprint_id: str
    version: str
    status: str
    certified: bool
    posture: CertificationPosture
    blocking_failed: int
    advisory_failed: int
    status_id: str = ""

    @classmethod
    def create(
        cls,
        *,
        certification_id: str,
        target_id: str,
        blueprint_id: str,
        version: str,
        status: str,
        certified: bool,
        posture: CertificationPosture,
        blocking_failed: int,
        advisory_failed: int,
    ) -> DerivedCertificationStatus:
        core = {
            "certification_id": certification_id,
            "target_id": target_id,
            "blueprint_id": blueprint_id,
            "version": version,
            "status": status,
            "certified": certified,
            "posture": posture.value,
            "blocking_failed": blocking_failed,
            "advisory_failed": advisory_failed,
        }
        return cls(
            certification_id=certification_id,
            target_id=target_id,
            blueprint_id=blueprint_id,
            version=version,
            status=status,
            certified=certified,
            posture=posture,
            blocking_failed=blocking_failed,
            advisory_failed=advisory_failed,
            status_id=f"UCOS-CDST-{content_hash(core)[:16]}",
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "status_id": self.status_id,
            "certification_id": self.certification_id,
            "target_id": self.target_id,
            "blueprint_id": self.blueprint_id,
            "version": self.version,
            "status": self.status,
            "certified": self.certified,
            "posture": self.posture.value,
            "blocking_failed": self.blocking_failed,
            "advisory_failed": self.advisory_failed,
        }

    def fingerprint(self) -> str:
        return content_hash(self.to_dict())


def _posture_for(decision: CertificationDecision) -> CertificationPosture:
    if not decision.certified:
        return CertificationPosture.NOT_CERTIFIED
    if decision.advisory_failures:
        return CertificationPosture.CERTIFIED_WITH_ADVISORIES
    return CertificationPosture.CERTIFIED


def _require_decision(decision: CertificationDecision, what: str) -> None:
    if not isinstance(decision, CertificationDecision):
        raise CertificationStatusError(f"{what} requires a CertificationDecision")


def derive_status(decision: CertificationDecision) -> DerivedCertificationStatus:
    """Derive a deterministic :class:`DerivedCertificationStatus` from a decision (pure)."""
    _require_decision(decision, "status derivation")
    counts = decision.counts()
    return DerivedCertificationStatus.create(
        certification_id=decision.certification_id,
        target_id=decision.target_id,
        blueprint_id=decision.blueprint_id,
        version=decision.version,
        status=decision.status.value,
        certified=decision.certified,
        posture=_posture_for(decision),
        blocking_failed=counts["blocking_failed"],
        advisory_failed=counts["advisory_failed"],
    )


# --------------------------------------------------------------------------- #
# Readiness.                                                                  #
# --------------------------------------------------------------------------- #

#: The deterministic readiness indicators, in stable evaluation order.
READINESS_INDICATORS: tuple[str, ...] = (
    "certified",
    "no-blocking-failures",
    "evidence-present",
    "record-integrity",
    "version-pinned",
)


@dataclass(frozen=True, slots=True)
class CertificationReadiness:
    """An immutable, content-addressed readiness evaluation (deterministic, fail-closed)."""

    certification_id: str
    target_id: str
    ready: bool
    indicators: tuple[tuple[str, bool], ...]
    satisfied: tuple[str, ...]
    blockers: tuple[str, ...]
    readiness_id: str = ""

    @classmethod
    def create(
        cls,
        *,
        certification_id: str,
        target_id: str,
        indicators: tuple[tuple[str, bool], ...],
    ) -> CertificationReadiness:
        satisfied = tuple(name for name, ok in indicators if ok)
        blockers = tuple(name for name, ok in indicators if not ok)
        ready = not blockers
        core = {
            "certification_id": certification_id,
            "target_id": target_id,
            "ready": ready,
            "indicators": [list(pair) for pair in indicators],
        }
        return cls(
            certification_id=certification_id,
            target_id=target_id,
            ready=ready,
            indicators=indicators,
            satisfied=satisfied,
            blockers=blockers,
            readiness_id=f"UCOS-CRDY-{content_hash(core)[:16]}",
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "readiness_id": self.readiness_id,
            "certification_id": self.certification_id,
            "target_id": self.target_id,
            "ready": self.ready,
            "indicators": {name: ok for name, ok in self.indicators},
            "satisfied": list(self.satisfied),
            "blockers": list(self.blockers),
        }

    def fingerprint(self) -> str:
        return content_hash(self.to_dict())


def evaluate_readiness(decision: CertificationDecision) -> CertificationReadiness:
    """Evaluate deterministic certification readiness (completeness) from a decision (pure)."""
    _require_decision(decision, "readiness evaluation")
    record = decision.record
    indicators: tuple[tuple[str, bool], ...] = (
        ("certified", decision.certified),
        ("no-blocking-failures", not decision.blocking_failures),
        ("evidence-present", bool(record.evidence_ref)),
        ("record-integrity", record.verify_integrity()),
        ("version-pinned", bool(record.version.strip())),
    )
    return CertificationReadiness.create(
        certification_id=decision.certification_id,
        target_id=decision.target_id,
        indicators=indicators,
    )


# --------------------------------------------------------------------------- #
# Governance validation.                                                      #
# --------------------------------------------------------------------------- #

#: The deterministic certification governance rules, in stable evaluation order.
GOVERNANCE_RULES: tuple[str, ...] = (
    "record-integrity",
    "authority-execution-only",
    "standard-pinned",
    "disclosure-present",
    "version-pinned",
    "status-consistent",
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
    """An immutable, content-addressed certification governance compliance assessment."""

    certification_id: str
    target_id: str
    compliant: bool
    rules_evaluated: tuple[str, ...]
    violations: tuple[GovernanceViolation, ...]
    assessment_id: str = ""

    @classmethod
    def create(
        cls,
        *,
        certification_id: str,
        target_id: str,
        rules_evaluated: tuple[str, ...],
        violations: tuple[GovernanceViolation, ...],
    ) -> GovernanceAssessment:
        compliant = not violations
        core = {
            "certification_id": certification_id,
            "target_id": target_id,
            "compliant": compliant,
            "rules_evaluated": list(rules_evaluated),
            "violations": [v.to_dict() for v in violations],
        }
        return cls(
            certification_id=certification_id,
            target_id=target_id,
            compliant=compliant,
            rules_evaluated=rules_evaluated,
            violations=violations,
            assessment_id=f"UCOS-CGOV-{content_hash(core)[:16]}",
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "assessment_id": self.assessment_id,
            "certification_id": self.certification_id,
            "target_id": self.target_id,
            "compliant": self.compliant,
            "rules_evaluated": list(self.rules_evaluated),
            "violations": [v.to_dict() for v in self.violations],
        }

    def fingerprint(self) -> str:
        return content_hash(self.to_dict())


def validate_governance(decision: CertificationDecision) -> GovernanceAssessment:
    """Evaluate the certification governance rules over a decision (pure, fail-closed).

    Reports a violation for every governance rule the certified record does not satisfy:
    record integrity, the ``ENGINEERING-EXECUTION-ONLY`` authority invariant (DE-05), a
    pinned readiness standard, the embedded provisional-state disclosure, a pinned
    version, and status consistency (certified iff no blocking criterion failed).
    """
    _require_decision(decision, "governance validation")
    record = decision.record
    violations: list[GovernanceViolation] = []
    if not record.verify_integrity():
        violations.append(
            GovernanceViolation("record-integrity", "certification record content was mutated")
        )
    if record.authority != CERTIFICATION_AUTHORITY:
        violations.append(
            GovernanceViolation(
                "authority-execution-only",
                f"authority must be {CERTIFICATION_AUTHORITY!r} (record-only, DE-05)",
            )
        )
    if not (record.standard and record.standard_version):
        violations.append(
            GovernanceViolation("standard-pinned", "certification readiness standard is not pinned")
        )
    if not record.disclosure:
        violations.append(
            GovernanceViolation("disclosure-present", "EC-1 provisional-state disclosure is absent")
        )
    if not record.version.strip():
        violations.append(
            GovernanceViolation("version-pinned", "certification is not version-pinned")
        )
    certified = record.status is CertificationStatus.CERTIFIED
    if certified is bool(decision.blocking_failures):
        violations.append(
            GovernanceViolation(
                "status-consistent",
                "certified status is inconsistent with the blocking-failure set",
            )
        )
    return GovernanceAssessment.create(
        certification_id=decision.certification_id,
        target_id=decision.target_id,
        rules_evaluated=GOVERNANCE_RULES,
        violations=tuple(violations),
    )


__all__ = [
    "CertificationPosture",
    "DerivedCertificationStatus",
    "derive_status",
    "READINESS_INDICATORS",
    "CertificationReadiness",
    "evaluate_readiness",
    "GOVERNANCE_RULES",
    "GovernanceViolation",
    "GovernanceAssessment",
    "validate_governance",
]
