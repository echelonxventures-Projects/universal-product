"""UKDA Part 10 — Knowledge Validation (EPIC-UKDA).

Automatic validation of the canonical knowledge base against the invariants the
Knowledge Once Principle requires. Each **check** is an immutable, deterministic
predicate over a :class:`~engine.knowledge.store.KnowledgeBase` (via its
:class:`~engine.knowledge.intelligence.KnowledgeIntelligence` facade) and yields a
:class:`KnowledgeFinding`. The suite enforces:

    * no duplicated knowledge / decision (content-hash uniqueness);
    * no conflicting active decision;
    * no orphan knowledge;
    * no undocumented decision;
    * no missing rationale / ownership;
    * no broken references / dependencies;
    * no undocumented exception.

The report is *fail-closed*: any BLOCKING failure makes the base not-valid.
Execution is deterministic (checks run in stable id order, no wall-clock), so an
identical base yields a byte-identical report.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Iterable
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, ClassVar

from engine.knowledge.intelligence import KnowledgeIntelligence
from engine.knowledge.model import KnowledgeKind
from engine.knowledge.store import KnowledgeBase


class Severity(str, Enum):
    BLOCKING = "blocking"
    ADVISORY = "advisory"


class CheckStatus(str, Enum):
    PASS = "pass"  # noqa: S105 — enum member, not a credential
    FAIL = "fail"


class Verdict(str, Enum):
    VALID = "valid"
    NOT_VALID = "not-valid"


@dataclass(frozen=True, slots=True)
class KnowledgeFinding:
    """The immutable outcome of a single knowledge validation check."""

    check_id: str
    severity: Severity
    status: CheckStatus
    message: str = ""
    offenders: tuple[str, ...] = ()

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
            "offenders": list(self.offenders),
        }


@dataclass(frozen=True, slots=True)
class KnowledgeValidationReport:
    """The aggregate, deterministic verdict over the knowledge base (Part 10)."""

    verdict: Verdict
    findings: tuple[KnowledgeFinding, ...] = field(default_factory=tuple)

    @property
    def accepted(self) -> bool:
        return self.verdict is Verdict.VALID

    @property
    def blocking_failures(self) -> tuple[KnowledgeFinding, ...]:
        return tuple(f for f in self.findings if f.is_blocking_failure)

    def counts(self) -> dict[str, int]:
        passed = sum(1 for f in self.findings if f.passed)
        return {
            "total": len(self.findings),
            "passed": passed,
            "failed": len(self.findings) - passed,
            "blocking_failed": len(self.blocking_failures),
        }

    def to_dict(self) -> dict[str, Any]:
        return {
            "verdict": self.verdict.value,
            "accepted": self.accepted,
            "counts": self.counts(),
            "findings": [f.to_dict() for f in self.findings],
        }


class KnowledgeCheck(ABC):
    """The common contract for a single knowledge validation check."""

    check_id: ClassVar[str]
    severity: ClassVar[Severity]
    description: ClassVar[str] = ""

    @abstractmethod
    def evaluate(self, intel: KnowledgeIntelligence) -> KnowledgeFinding:
        raise NotImplementedError  # pragma: no cover

    def _passed(self, message: str = "") -> KnowledgeFinding:
        return KnowledgeFinding(
            check_id=self.check_id,
            severity=self.severity,
            status=CheckStatus.PASS,
            message=message or f"{self.check_id} satisfied",
        )

    def _failed(self, message: str, offenders: Iterable[str] = ()) -> KnowledgeFinding:
        return KnowledgeFinding(
            check_id=self.check_id,
            severity=self.severity,
            status=CheckStatus.FAIL,
            message=message,
            offenders=tuple(offenders),
        )


class NoDuplicateKnowledgeCheck(KnowledgeCheck):
    check_id = "no-duplicate-knowledge"
    severity = Severity.BLOCKING
    description = "No two canonical objects share identical authored content."

    def evaluate(self, intel: KnowledgeIntelligence) -> KnowledgeFinding:
        dupes = intel.find_duplicates()
        if dupes:
            offenders = tuple(cid for d in dupes for cid in d.cko_ids)
            return self._failed("duplicated canonical knowledge detected", offenders)
        return self._passed()


class NoConflictingDecisionCheck(KnowledgeCheck):
    check_id = "no-conflicting-decision"
    severity = Severity.BLOCKING
    description = "No two active objects are declared to conflict."

    def evaluate(self, intel: KnowledgeIntelligence) -> KnowledgeFinding:
        conflicts = intel.find_conflicts()
        if conflicts:
            offenders = tuple(f"{c.left}~{c.right}" for c in conflicts)
            return self._failed("conflicting active knowledge detected", offenders)
        return self._passed()


class NoOrphanKnowledgeCheck(KnowledgeCheck):
    check_id = "no-orphan-knowledge"
    severity = Severity.ADVISORY
    description = "Every non-root object participates in at least one relationship."

    def evaluate(self, intel: KnowledgeIntelligence) -> KnowledgeFinding:
        orphans = intel.find_orphans()
        if orphans:
            return self._failed("orphan knowledge detected", orphans)
        return self._passed()


class NoBrokenReferenceCheck(KnowledgeCheck):
    check_id = "no-broken-reference"
    severity = Severity.BLOCKING
    description = "Every link and dependency resolves to an existing object/decision."

    def evaluate(self, intel: KnowledgeIntelligence) -> KnowledgeFinding:
        broken = intel.find_broken_references()
        if broken:
            offenders = tuple(f"{src}->{tgt}" for src, tgt in broken)
            return self._failed("broken references/dependencies detected", offenders)
        return self._passed()


class EveryDecisionDocumentedCheck(KnowledgeCheck):
    check_id = "every-decision-documented"
    severity = Severity.BLOCKING
    description = "Every DECISION object links a recorded decision."

    def evaluate(self, intel: KnowledgeIntelligence) -> KnowledgeFinding:
        undocumented = intel.find_undocumented_decisions()
        if undocumented:
            return self._failed("undocumented decisions detected", undocumented)
        return self._passed()


class RationalePresentCheck(KnowledgeCheck):
    check_id = "rationale-present"
    severity = Severity.BLOCKING
    description = "Every decision/rule object carries a permanent rationale."

    def evaluate(self, intel: KnowledgeIntelligence) -> KnowledgeFinding:
        offenders = tuple(intel.coverage().objects_missing_rationale)
        if offenders:
            return self._failed("objects missing required rationale", offenders)
        return self._passed()


class OwnershipPresentCheck(KnowledgeCheck):
    check_id = "ownership-present"
    severity = Severity.BLOCKING
    description = "Every canonical object has an assigned owner."

    def evaluate(self, intel: KnowledgeIntelligence) -> KnowledgeFinding:
        offenders = tuple(intel.coverage().objects_missing_owner)
        if offenders:
            return self._failed("objects missing an owner", offenders)
        return self._passed()


class DocumentedExceptionCheck(KnowledgeCheck):
    check_id = "documented-exception"
    severity = Severity.BLOCKING
    description = "Every EXCEPTION object references the rule/policy it excepts."

    def evaluate(self, intel: KnowledgeIntelligence) -> KnowledgeFinding:
        offenders = tuple(
            obj.cko_id
            for obj in intel.base.by_kind(KnowledgeKind.EXCEPTION)
            if not (obj.knowledge_links or obj.dependencies or obj.parent)
        )
        if offenders:
            return self._failed("undocumented exceptions detected", offenders)
        return self._passed()


class IntegritySealedCheck(KnowledgeCheck):
    check_id = "integrity-sealed"
    severity = Severity.BLOCKING
    description = "Every object and decision verifies its content hash."

    def evaluate(self, intel: KnowledgeIntelligence) -> KnowledgeFinding:
        offenders: list[str] = []
        for obj in intel.base.objects():
            if not obj.verify_integrity():
                offenders.append(obj.cko_id)
        for dec in intel.base.decisions():
            if not dec.verify_integrity():
                offenders.append(dec.decision_id)
        if offenders:
            return self._failed("content-hash integrity failures detected", offenders)
        return self._passed()


def default_checks() -> tuple[KnowledgeCheck, ...]:
    """Return the built-in knowledge validation suite in stable id order."""
    checks: tuple[KnowledgeCheck, ...] = (
        DocumentedExceptionCheck(),
        EveryDecisionDocumentedCheck(),
        IntegritySealedCheck(),
        NoBrokenReferenceCheck(),
        NoConflictingDecisionCheck(),
        NoDuplicateKnowledgeCheck(),
        NoOrphanKnowledgeCheck(),
        OwnershipPresentCheck(),
        RationalePresentCheck(),
    )
    return tuple(sorted(checks, key=lambda c: c.check_id))


class KnowledgeValidator:
    """Runs the deterministic knowledge validation suite (Part 10)."""

    __slots__ = ("_checks",)

    def __init__(self, checks: Iterable[KnowledgeCheck] | None = None) -> None:
        selected = tuple(checks) if checks is not None else default_checks()
        self._checks = tuple(sorted(selected, key=lambda c: c.check_id))

    @property
    def check_ids(self) -> tuple[str, ...]:
        return tuple(c.check_id for c in self._checks)

    def validate(self, base: KnowledgeBase) -> KnowledgeValidationReport:
        intel = KnowledgeIntelligence(base)
        findings = tuple(check.evaluate(intel) for check in self._checks)
        verdict = (
            Verdict.NOT_VALID if any(f.is_blocking_failure for f in findings) else Verdict.VALID
        )
        return KnowledgeValidationReport(verdict=verdict, findings=findings)


def validate_base(base: KnowledgeBase) -> KnowledgeValidationReport:
    """Convenience: validate a base with the default suite."""
    return KnowledgeValidator().validate(base)


__all__ = [
    "Severity",
    "CheckStatus",
    "Verdict",
    "KnowledgeFinding",
    "KnowledgeValidationReport",
    "KnowledgeCheck",
    "NoDuplicateKnowledgeCheck",
    "NoConflictingDecisionCheck",
    "NoOrphanKnowledgeCheck",
    "NoBrokenReferenceCheck",
    "EveryDecisionDocumentedCheck",
    "RationalePresentCheck",
    "OwnershipPresentCheck",
    "DocumentedExceptionCheck",
    "IntegritySealedCheck",
    "default_checks",
    "KnowledgeValidator",
    "validate_base",
]
