"""UCOS-EPIC-006 — Certification Rules (Terminal T6).

A **certification rule** is an immutable, deterministic predicate over a
:class:`~engine.universal_certification.contracts.UniversalCertificationSubject` and
the :class:`~engine.universal_certification.compliance.ComplianceReport` produced for
it. Each rule has a stable id and a severity, and returns a
:class:`~engine.universal_certification.contracts.RuleFinding`. Rules are pure
functions of their inputs — no secrets, no mutation, no wall-clock — so identical
inputs yield identical findings.

The built-in suite is *sound*: because the subject is a pure projection of the three
consumed inputs (validation, measurement, repository truth), every rule **aggregates**
an upstream verdict and never re-judges an artifact (TP-01). The suite requires that
compliance is conformant, that validation accepted the target with reproducible
evidence, that measurements were consumed and every blocking measurement is satisfied,
that the repository-truth closure is consistent, that the provisional-state disclosure
was validated (DE-05), and that the certificate is version-pinned (URS-L-20). The
architecture is open: callers may supply their own rules to the engine.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, ClassVar

from engine.universal_certification.compliance import ComplianceReport
from engine.universal_certification.contracts import (
    RuleFinding,
    RuleSeverity,
    RuleStatus,
    UniversalCertificationSubject,
)


class CertificationRule(ABC):
    """The common contract for a single certification rule (architecture unit)."""

    rule_id: ClassVar[str]
    severity: ClassVar[RuleSeverity]
    description: ClassVar[str] = ""

    @abstractmethod
    def evaluate(
        self,
        subject: UniversalCertificationSubject,
        compliance: ComplianceReport,
    ) -> RuleFinding:
        """Return a finding for the subject + compliance report (never raises here)."""
        raise NotImplementedError  # pragma: no cover

    # -- helpers ---------------------------------------------------------------

    def _passed(self, message: str = "", **details: Any) -> RuleFinding:
        return RuleFinding(
            rule_id=self.rule_id,
            severity=self.severity,
            status=RuleStatus.PASS,
            message=message or f"{self.rule_id} satisfied",
            details=details,
        )

    def _failed(self, message: str, **details: Any) -> RuleFinding:
        return RuleFinding(
            rule_id=self.rule_id,
            severity=self.severity,
            status=RuleStatus.FAIL,
            message=message,
            details=details,
        )


class ComplianceConformantRule(CertificationRule):
    """The Compliance Engine reported an overall CONFORMANT verdict."""

    rule_id = "compliance-conformant"
    severity = RuleSeverity.BLOCKING
    description = "The aggregated compliance report is conformant (no blocking frame failed)."

    def evaluate(self, subject, compliance):
        if not compliance.conformant:
            return self._failed(
                "compliance is non-conformant",
                non_conformances=list(compliance.non_conformances),
            )
        return self._passed(frames=compliance.counts()["total"])


class ValidationAcceptedRule(CertificationRule):
    """Validation accepted the target — the core certification aggregation."""

    rule_id = "validation-accepted"
    severity = RuleSeverity.BLOCKING
    description = "The consumed validation verdict is PASS with no blocking failure."

    def evaluate(self, subject, compliance):
        v = subject.validation
        if not v.accepted or v.verdict != "pass":
            return self._failed(
                "validation did not accept the target",
                verdict=v.verdict,
                blocking_failures=list(v.blocking_failures),
            )
        return self._passed(verdict=v.verdict)


class ValidationEvidencePresentRule(CertificationRule):
    """Reproducible validation evidence is present and referenced (soundness)."""

    rule_id = "validation-evidence-present"
    severity = RuleSeverity.BLOCKING
    description = "A validation evidence record is present and content-hashable."

    def evaluate(self, subject, compliance):
        v = subject.validation
        if not v.evidence_present or not v.evidence_sha256:
            return self._failed("validation evidence is absent; cannot certify")
        return self._passed(evidence_sha256=v.evidence_sha256)


class MeasurementsPresentRule(CertificationRule):
    """At least one measurement was consumed (measurement over assertion)."""

    rule_id = "measurements-present"
    severity = RuleSeverity.BLOCKING
    description = "The certification consumed a non-empty set of measurement results."

    def evaluate(self, subject, compliance):
        if not subject.measurement.present:
            return self._failed("no measurements were consumed; cannot certify")
        return self._passed(total=subject.measurement.counts()["total"])


class MeasurementsSatisfiedRule(CertificationRule):
    """Every blocking measurement is satisfied against its threshold."""

    rule_id = "measurements-satisfied"
    severity = RuleSeverity.BLOCKING
    description = "No blocking measurement fell short of its threshold."

    def evaluate(self, subject, compliance):
        shortfalls = subject.measurement.blocking_shortfalls
        if shortfalls:
            return self._failed(
                "one or more blocking measurements fell short",
                blocking_shortfalls=list(shortfalls),
            )
        return self._passed(counts=subject.measurement.counts())


class RepositoryTruthConsistentRule(CertificationRule):
    """The repository-truth attestation is closed, fully homed, and gap-free."""

    rule_id = "repository-truth-consistent"
    severity = RuleSeverity.BLOCKING
    description = "The consumed repository-truth closure is consistent (URS-L-20/21)."

    def evaluate(self, subject, compliance):
        rt = subject.repository_truth
        if not rt.consistent:
            return self._failed(
                "repository truth is not consistent",
                closed=rt.closed,
                fully_homed=rt.fully_homed,
                open_gap_categories=list(rt.open_gap_categories),
                gap_total=rt.gap_total,
            )
        return self._passed(total_concepts=rt.total_concepts)


class DisclosurePresentRule(CertificationRule):
    """The EC-1 provisional-state disclosure invariant was validated (DE-05)."""

    rule_id = "disclosure-present"
    severity = RuleSeverity.BLOCKING
    description = "Validation ran and passed the EC-1 provisional-state disclosure check."

    def evaluate(self, subject, compliance):
        if not subject.validation.disclosure_validated:
            return self._failed("provisional-state disclosure was not validated")
        return self._passed()


class VersionPinnedRule(CertificationRule):
    """The certification is pinned to a concrete artifact version (URS-L-20)."""

    rule_id = "version-pinned"
    severity = RuleSeverity.BLOCKING
    description = "A non-empty version pin is present so the certificate is version-scoped."

    def evaluate(self, subject, compliance):
        if not subject.version.strip():
            return self._failed("certification is not version-pinned")
        return self._passed(version=subject.version)


class MeasurementCompleteRule(CertificationRule):
    """Every measurement passed, including advisory ones (advisory signal)."""

    rule_id = "measurement-complete"
    severity = RuleSeverity.ADVISORY
    description = "No measurement fell short, including advisory measurements."

    def evaluate(self, subject, compliance):
        advisory = subject.measurement.advisory_shortfalls
        if advisory:
            return self._failed(
                "one or more advisory measurements fell short",
                advisory_shortfalls=list(advisory),
            )
        return self._passed(total=subject.measurement.counts()["total"])


class ValidationCompleteRule(CertificationRule):
    """Every validation check passed, including advisory checks (advisory signal)."""

    rule_id = "validation-complete"
    severity = RuleSeverity.ADVISORY
    description = "No validation check failed, including advisory checks."

    def evaluate(self, subject, compliance):
        failed = int(subject.validation.counts.get("failed", 0))
        if failed:
            return self._failed("one or more validation checks failed", failed=failed)
        return self._passed(total=int(subject.validation.counts.get("total", 0)))


def default_rules() -> tuple[CertificationRule, ...]:
    """Return the built-in certification rule suite, ordered deterministically by id."""
    rules: tuple[CertificationRule, ...] = (
        ComplianceConformantRule(),
        DisclosurePresentRule(),
        MeasurementCompleteRule(),
        MeasurementsPresentRule(),
        MeasurementsSatisfiedRule(),
        RepositoryTruthConsistentRule(),
        ValidationAcceptedRule(),
        ValidationCompleteRule(),
        ValidationEvidencePresentRule(),
        VersionPinnedRule(),
    )
    return tuple(sorted(rules, key=lambda r: r.rule_id))


__all__ = [
    "CertificationRule",
    "ComplianceConformantRule",
    "ValidationAcceptedRule",
    "ValidationEvidencePresentRule",
    "MeasurementsPresentRule",
    "MeasurementsSatisfiedRule",
    "RepositoryTruthConsistentRule",
    "DisclosurePresentRule",
    "VersionPinnedRule",
    "MeasurementCompleteRule",
    "ValidationCompleteRule",
    "default_rules",
]
