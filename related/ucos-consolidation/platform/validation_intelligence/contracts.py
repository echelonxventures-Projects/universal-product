"""UCOS-EPIC-013 — Continuous Validation Intelligence contracts (Terminal T5).

The immutable, deterministic value types the Continuous Validation Intelligence engine
speaks. Every type is **immutable, typed, deterministic, and serializable** and holds
no runtime state, so an identical :class:`IntelligenceTarget` analyzed by an identical
analyzer suite yields a byte-identical :class:`ValidationIntelligenceReport` and content
hash (IMP-007 §5) — no wall-clock or ambient state leaks into any identity.

Where EPIC-005 validates a *single* system against static rules, EPIC-013 reasons over
seven **intelligence dimensions** that span capabilities, a repository's declared
completeness, and *baseline↔candidate* deltas:

    * :class:`IntelligenceDimension` — the seven dimensions, in the mission's canonical
      order, each classified by a :class:`DimensionKind` (consistency, completeness,
      compatibility, compliance) so the Compatibility Engine and Compliance Reports are
      deterministic *projections* of one report.
    * :class:`Severity` / :class:`FindingStatus` / :class:`Verdict` — fail-closed
      outcomes.
    * :class:`IntelligenceTarget` — the normalized, dimension-keyed projection of the
      system(s) under analysis; analyzers are pure functions of it.
    * :class:`Finding` — the immutable outcome of a single analysis check.
    * :class:`DimensionReport` — the ordered, deterministic per-dimension aggregate.
    * :class:`ValidationIntelligenceReport` — the content-addressed cross-dimension
      aggregate; it asserts ``ENGINEERING-EXECUTION-ONLY`` authority and carries the
      EC-1 provisional-state disclosure (DE-05 / IP-01).
    * :class:`CompatibilityReport` / :class:`ComplianceReport` — the two named
      deliverables, each a deterministic projection of the report over its dimensions.
    * :class:`IntelligenceDashboard` — the deterministic dashboard projection.

Nothing here is hardcoded to a specific system: the vocabulary defines the *shape*; the
concrete facts are supplied by the target, and the concrete checks by the analyzers.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field
from enum import Enum
from platform.foundation.contracts import content_hash
from platform.validation_intelligence.errors import IntelligenceTargetError
from typing import Any

from engine.runtime.disclosure import build_disclosure

#: The semantic version of the Validation Intelligence contract surface (AR-03/PL-05).
VALIDATION_INTELLIGENCE_CONTRACT_VERSION = "1.0.0"

#: Format identifiers for the four EPIC-013 deliverables.
INTELLIGENCE_REPORT_FORMAT = "ucos-validation-intelligence-report/1.0.0"
INTELLIGENCE_DASHBOARD_FORMAT = "ucos-validation-intelligence-dashboard/1.0.0"
COMPATIBILITY_REPORT_FORMAT = "ucos-validation-compatibility-report/1.0.0"
COMPLIANCE_REPORT_FORMAT = "ucos-validation-compliance-report/1.0.0"

#: Continuous validation intelligence confers no constitutional authority
#: (DE-05 / IP-01): a run records engineering readiness only. Embedded verbatim in
#: every report.
INTELLIGENCE_AUTHORITY = "ENGINEERING-EXECUTION-ONLY"


class DimensionKind(str, Enum):
    """The family a dimension belongs to (drives the report's projections)."""

    CONSISTENCY = "consistency"
    COMPLETENESS = "completeness"
    COMPATIBILITY = "compatibility"
    COMPLIANCE = "compliance"


class IntelligenceDimension(str, Enum):
    """The seven continuous-validation-intelligence dimensions, in canonical order."""

    CROSS_CAPABILITY_CONSISTENCY = "cross_capability_consistency"
    REPOSITORY_COMPLETENESS = "repository_completeness"
    CONTRACT_COMPATIBILITY = "contract_compatibility"
    ARCHITECTURE_COMPLIANCE = "architecture_compliance"
    RUNTIME_COMPATIBILITY = "runtime_compatibility"
    VERSION_COMPATIBILITY = "version_compatibility"
    GOVERNANCE_COMPLIANCE = "governance_compliance"

    @classmethod
    def parse(cls, value: Any) -> IntelligenceDimension:
        """Parse a dimension, raising :class:`IntelligenceTargetError` on an unknown one."""
        try:
            return cls(value)
        except ValueError as exc:
            raise IntelligenceTargetError(
                "unknown validation-intelligence dimension",
                dimension=value,
                supported=[d.value for d in cls],
            ) from exc

    @property
    def order(self) -> int:
        """The canonical (declaration-order) index, for deterministic ordering."""
        return _DIMENSION_ORDER[self]

    @property
    def kind(self) -> DimensionKind:
        """The family this dimension belongs to."""
        return _DIMENSION_KIND[self]


_DIMENSION_ORDER: dict[IntelligenceDimension, int] = {
    d: i for i, d in enumerate(IntelligenceDimension)
}

_DIMENSION_KIND: dict[IntelligenceDimension, DimensionKind] = {
    IntelligenceDimension.CROSS_CAPABILITY_CONSISTENCY: DimensionKind.CONSISTENCY,
    IntelligenceDimension.REPOSITORY_COMPLETENESS: DimensionKind.COMPLETENESS,
    IntelligenceDimension.CONTRACT_COMPATIBILITY: DimensionKind.COMPATIBILITY,
    IntelligenceDimension.ARCHITECTURE_COMPLIANCE: DimensionKind.COMPLIANCE,
    IntelligenceDimension.RUNTIME_COMPATIBILITY: DimensionKind.COMPATIBILITY,
    IntelligenceDimension.VERSION_COMPATIBILITY: DimensionKind.COMPATIBILITY,
    IntelligenceDimension.GOVERNANCE_COMPLIANCE: DimensionKind.COMPLIANCE,
}


def dimensions_of_kind(kind: DimensionKind) -> tuple[IntelligenceDimension, ...]:
    """Return the dimensions of ``kind`` in canonical order."""
    return tuple(d for d in sorted(IntelligenceDimension, key=lambda x: x.order) if d.kind is kind)


class Severity(str, Enum):
    """Whether a failing finding blocks the verdict or is merely advisory."""

    BLOCKING = "blocking"
    ADVISORY = "advisory"


class FindingStatus(str, Enum):
    """The fail-closed outcome of a single analysis check."""

    PASS = "pass"  # noqa: S105 — enum member, not a credential
    FAIL = "fail"


class Verdict(str, Enum):
    """The aggregate verdict of a dimension report or intelligence report (fail-closed)."""

    PASS = "pass"  # noqa: S105 — enum member, not a credential
    FAIL = "fail"


@dataclass(frozen=True, slots=True)
class IntelligenceTarget:
    """A normalized, dimension-keyed projection of the system(s) under analysis.

    ``facts`` maps an :class:`IntelligenceDimension` *value* to the immutable evidence
    that dimension's analyzers reason over. Analyzers read only the facts they need; an
    absent or malformed fact yields a fail-closed FAIL finding (never an exception).
    """

    target_id: str
    facts: Mapping[str, Mapping[str, Any]] = field(default_factory=dict)

    @classmethod
    def from_mapping(cls, raw: Mapping[str, Any]) -> IntelligenceTarget:
        """Assimilate a mapping into a normalized :class:`IntelligenceTarget`.

        Raises:
            IntelligenceTargetError: if the mapping lacks a target id, or a per-dimension
                facts value is not a mapping (a malformed *authoring* fault).
        """
        if not isinstance(raw, Mapping):
            raise IntelligenceTargetError("an intelligence target must be a mapping")
        target_id = raw.get("target_id")
        if not target_id or not isinstance(target_id, str):
            raise IntelligenceTargetError("an intelligence target requires a non-empty target_id")
        raw_facts = raw.get("facts", {})
        if not isinstance(raw_facts, Mapping):
            raise IntelligenceTargetError("target facts must be a mapping", target_id=target_id)
        facts: dict[str, dict[str, Any]] = {}
        for key, value in raw_facts.items():
            dimension = IntelligenceDimension.parse(key)
            if not isinstance(value, Mapping):
                raise IntelligenceTargetError(
                    "dimension facts must be a mapping",
                    target_id=target_id,
                    dimension=dimension.value,
                )
            facts[dimension.value] = dict(value)
        return cls(target_id=str(target_id), facts=facts)

    def dimension_facts(self, dimension: IntelligenceDimension) -> Mapping[str, Any]:
        """Return the (possibly empty) facts mapping for ``dimension``."""
        return self.facts.get(dimension.value, {})

    def to_dict(self) -> dict[str, Any]:
        return {
            "target_id": self.target_id,
            "facts": {key: dict(value) for key, value in sorted(self.facts.items())},
        }

    def digest(self) -> str:
        """The deterministic content hash of the target (a stable target identity)."""
        return content_hash(self.to_dict())


@dataclass(frozen=True, slots=True)
class Finding:
    """The immutable, deterministic outcome of a single analysis check."""

    check_id: str
    dimension: IntelligenceDimension
    severity: Severity
    status: FindingStatus
    message: str = ""
    details: Mapping[str, Any] = field(default_factory=dict)

    @property
    def passed(self) -> bool:
        return self.status is FindingStatus.PASS

    @property
    def failed(self) -> bool:
        return self.status is FindingStatus.FAIL

    @property
    def is_blocking_failure(self) -> bool:
        return self.failed and self.severity is Severity.BLOCKING

    @property
    def is_advisory_failure(self) -> bool:
        return self.failed and self.severity is Severity.ADVISORY

    def core(self) -> dict[str, Any]:
        """The canonical, hashable core of the finding (excludes volatile detail)."""
        return {
            "check_id": self.check_id,
            "dimension": self.dimension.value,
            "severity": self.severity.value,
            "status": self.status.value,
            "message": self.message,
        }

    def to_dict(self) -> dict[str, Any]:
        return {**self.core(), "details": dict(self.details)}


@dataclass(frozen=True, slots=True)
class DimensionReport:
    """The ordered, deterministic aggregate of one dimension's findings."""

    dimension: IntelligenceDimension
    verdict: Verdict
    findings: tuple[Finding, ...]

    @classmethod
    def create(
        cls, dimension: IntelligenceDimension, findings: tuple[Finding, ...]
    ) -> DimensionReport:
        """Aggregate ``findings`` for ``dimension``; verdict FAIL iff a blocking check failed."""
        verdict = Verdict.FAIL if any(f.is_blocking_failure for f in findings) else Verdict.PASS
        return cls(dimension=dimension, verdict=verdict, findings=findings)

    @property
    def kind(self) -> DimensionKind:
        return self.dimension.kind

    @property
    def passed(self) -> bool:
        return self.verdict is Verdict.PASS

    def blocking_failures(self) -> tuple[str, ...]:
        return tuple(f.check_id for f in self.findings if f.is_blocking_failure)

    def advisory_failures(self) -> tuple[str, ...]:
        return tuple(f.check_id for f in self.findings if f.is_advisory_failure)

    def counts(self) -> dict[str, int]:
        passed = sum(1 for f in self.findings if f.passed)
        return {
            "total": len(self.findings),
            "passed": passed,
            "failed": len(self.findings) - passed,
            "blocking_failed": len(self.blocking_failures()),
            "advisory_failed": len(self.advisory_failures()),
        }

    def core(self) -> dict[str, Any]:
        return {
            "dimension": self.dimension.value,
            "kind": self.dimension.kind.value,
            "verdict": self.verdict.value,
            "findings": [f.core() for f in self.findings],
        }

    def to_dict(self) -> dict[str, Any]:
        return {
            "dimension": self.dimension.value,
            "kind": self.dimension.kind.value,
            "verdict": self.verdict.value,
            "passed": self.passed,
            "counts": self.counts(),
            "blocking_failures": list(self.blocking_failures()),
            "advisory_failures": list(self.advisory_failures()),
            "findings": [f.to_dict() for f in self.findings],
        }


@dataclass(frozen=True, slots=True)
class ValidationIntelligenceReport:
    """The content-addressed, cross-dimension aggregate of a continuous-validation run.

    The report is a **pure function of the target and the ordered dimension outcomes**:
    its ``report_sha256`` hashes only the dimension/finding cores (never volatile
    per-finding detail or any wall-clock), so an identical target analyzed by an
    identical suite reproduces a byte-identical report. It asserts
    ``ENGINEERING-EXECUTION-ONLY`` authority and carries the EC-1 provisional-state
    disclosure (DE-05 / IP-01).
    """

    target_id: str
    verdict: Verdict
    target_digest: str
    dimension_reports: tuple[DimensionReport, ...]
    authority: str
    disclosure: Mapping[str, Any]
    report_sha256: str

    @staticmethod
    def _core(
        *,
        target_id: str,
        verdict: Verdict,
        target_digest: str,
        dimension_reports: tuple[DimensionReport, ...],
        authority: str,
        disclosure: Mapping[str, Any],
    ) -> dict[str, Any]:
        return {
            "target_id": target_id,
            "verdict": verdict.value,
            "target_digest": target_digest,
            "dimensions": [r.core() for r in dimension_reports],
            "authority": authority,
            "disclosure": dict(disclosure),
        }

    @classmethod
    def create(
        cls,
        *,
        target_id: str,
        target_digest: str,
        dimension_reports: tuple[DimensionReport, ...],
    ) -> ValidationIntelligenceReport:
        """Aggregate dimension reports into an immutable, content-addressed report.

        The verdict is fail-closed: FAIL iff any *blocking* check failed in any dimension.
        """
        verdict = (
            Verdict.FAIL
            if any(r.verdict is Verdict.FAIL for r in dimension_reports)
            else Verdict.PASS
        )
        disclosure = build_disclosure()
        core = cls._core(
            target_id=target_id,
            verdict=verdict,
            target_digest=target_digest,
            dimension_reports=dimension_reports,
            authority=INTELLIGENCE_AUTHORITY,
            disclosure=disclosure,
        )
        return cls(
            target_id=target_id,
            verdict=verdict,
            target_digest=target_digest,
            dimension_reports=dimension_reports,
            authority=INTELLIGENCE_AUTHORITY,
            disclosure=disclosure,
            report_sha256=content_hash(core),
        )

    @property
    def passed(self) -> bool:
        return self.verdict is Verdict.PASS

    @property
    def all_findings(self) -> tuple[Finding, ...]:
        return tuple(f for report in self.dimension_reports for f in report.findings)

    def dimensions_run(self) -> tuple[str, ...]:
        return tuple(r.dimension.value for r in self.dimension_reports)

    def reports_of_kind(self, kind: DimensionKind) -> tuple[DimensionReport, ...]:
        """The dimension reports whose dimension belongs to ``kind`` (canonical order)."""
        return tuple(r for r in self.dimension_reports if r.dimension.kind is kind)

    def counts(self) -> dict[str, int]:
        findings = self.all_findings
        passed = sum(1 for f in findings if f.passed)
        return {
            "dimensions": len(self.dimension_reports),
            "total": len(findings),
            "passed": passed,
            "failed": len(findings) - passed,
            "blocking_failed": sum(1 for f in findings if f.is_blocking_failure),
            "advisory_failed": sum(1 for f in findings if f.is_advisory_failure),
        }

    def blocking_failures(self) -> tuple[str, ...]:
        return tuple(f.check_id for f in self.all_findings if f.is_blocking_failure)

    def advisory_failures(self) -> tuple[str, ...]:
        return tuple(f.check_id for f in self.all_findings if f.is_advisory_failure)

    def dimension_verdicts(self) -> dict[str, str]:
        return {r.dimension.value: r.verdict.value for r in self.dimension_reports}

    def dashboard(self) -> IntelligenceDashboard:
        """Project the deterministic Validation Intelligence Dashboard from this report."""
        return IntelligenceDashboard.from_report(self)

    def compatibility_report(self) -> CompatibilityReport:
        """Project the Compatibility Engine's report from this report (deliverable)."""
        return CompatibilityReport.from_report(self)

    def compliance_report(self) -> ComplianceReport:
        """Project the Compliance Report from this report (deliverable)."""
        return ComplianceReport.from_report(self)

    def to_dict(self) -> dict[str, Any]:
        return {
            "report_format": INTELLIGENCE_REPORT_FORMAT,
            "target_id": self.target_id,
            "verdict": self.verdict.value,
            "passed": self.passed,
            "target_digest": self.target_digest,
            "counts": self.counts(),
            "dimension_verdicts": self.dimension_verdicts(),
            "blocking_failures": list(self.blocking_failures()),
            "advisory_failures": list(self.advisory_failures()),
            "dimensions": [r.to_dict() for r in self.dimension_reports],
            "authority": self.authority,
            "disclosure": dict(self.disclosure),
            "report_sha256": self.report_sha256,
        }


@dataclass(frozen=True, slots=True)
class IntelligenceDashboard:
    """A deterministic, content-addressed dashboard projection of an intelligence run."""

    target_id: str
    verdict: Verdict
    dimensions_total: int
    checks_total: int
    checks_passed: int
    checks_failed: int
    dimension_verdicts: dict[str, str]
    blocking_failures: tuple[str, ...]
    advisory_failures: tuple[str, ...]
    dashboard_sha256: str

    @classmethod
    def from_report(cls, report: ValidationIntelligenceReport) -> IntelligenceDashboard:
        counts = report.counts()
        core = {
            "target_id": report.target_id,
            "verdict": report.verdict.value,
            "dimensions_total": counts["dimensions"],
            "checks_total": counts["total"],
            "checks_passed": counts["passed"],
            "checks_failed": counts["failed"],
            "dimension_verdicts": report.dimension_verdicts(),
            "blocking_failures": list(report.blocking_failures()),
            "advisory_failures": list(report.advisory_failures()),
        }
        return cls(
            target_id=report.target_id,
            verdict=report.verdict,
            dimensions_total=counts["dimensions"],
            checks_total=counts["total"],
            checks_passed=counts["passed"],
            checks_failed=counts["failed"],
            dimension_verdicts=report.dimension_verdicts(),
            blocking_failures=report.blocking_failures(),
            advisory_failures=report.advisory_failures(),
            dashboard_sha256=content_hash(core),
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "dashboard_format": INTELLIGENCE_DASHBOARD_FORMAT,
            "target_id": self.target_id,
            "verdict": self.verdict.value,
            "dimensions_total": self.dimensions_total,
            "checks_total": self.checks_total,
            "checks_passed": self.checks_passed,
            "checks_failed": self.checks_failed,
            "dimension_verdicts": dict(self.dimension_verdicts),
            "blocking_failures": list(self.blocking_failures),
            "advisory_failures": list(self.advisory_failures),
            "dashboard_sha256": self.dashboard_sha256,
        }


@dataclass(frozen=True, slots=True)
class CompatibilityReport:
    """Deterministic projection of a report over its compatibility dimensions.

    The Compatibility Engine deliverable: ``compatible`` is true iff every
    compatibility dimension (contract, runtime, version) passed — i.e. no *breaking*
    change was detected. The report enumerates the breaking findings that would make a
    candidate incompatible with its baseline.
    """

    target_id: str
    compatible: bool
    dimension_verdicts: dict[str, str]
    breaking_changes: tuple[dict[str, Any], ...]
    report_sha256: str

    @classmethod
    def from_report(cls, report: ValidationIntelligenceReport) -> CompatibilityReport:
        compat_reports = report.reports_of_kind(DimensionKind.COMPATIBILITY)
        verdicts = {r.dimension.value: r.verdict.value for r in compat_reports}
        breaking = tuple(
            f.core() for r in compat_reports for f in r.findings if f.is_blocking_failure
        )
        compatible = all(r.passed for r in compat_reports)
        core = {
            "target_id": report.target_id,
            "compatible": compatible,
            "dimension_verdicts": verdicts,
            "breaking_changes": list(breaking),
        }
        return cls(
            target_id=report.target_id,
            compatible=compatible,
            dimension_verdicts=verdicts,
            breaking_changes=breaking,
            report_sha256=content_hash(core),
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "report_format": COMPATIBILITY_REPORT_FORMAT,
            "target_id": self.target_id,
            "compatible": self.compatible,
            "dimension_verdicts": dict(self.dimension_verdicts),
            "breaking_changes": [dict(c) for c in self.breaking_changes],
            "report_sha256": self.report_sha256,
        }


@dataclass(frozen=True, slots=True)
class ComplianceReport:
    """Deterministic projection of a report over its compliance dimensions.

    The Compliance Report deliverable: ``compliant`` is true iff every compliance
    dimension (architecture, governance) passed. The report enumerates the unmet
    (blocking) controls.
    """

    target_id: str
    compliant: bool
    dimension_verdicts: dict[str, str]
    violations: tuple[dict[str, Any], ...]
    report_sha256: str

    @classmethod
    def from_report(cls, report: ValidationIntelligenceReport) -> ComplianceReport:
        comp_reports = report.reports_of_kind(DimensionKind.COMPLIANCE)
        verdicts = {r.dimension.value: r.verdict.value for r in comp_reports}
        violations = tuple(
            f.core() for r in comp_reports for f in r.findings if f.is_blocking_failure
        )
        compliant = all(r.passed for r in comp_reports)
        core = {
            "target_id": report.target_id,
            "compliant": compliant,
            "dimension_verdicts": verdicts,
            "violations": list(violations),
        }
        return cls(
            target_id=report.target_id,
            compliant=compliant,
            dimension_verdicts=verdicts,
            violations=violations,
            report_sha256=content_hash(core),
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "report_format": COMPLIANCE_REPORT_FORMAT,
            "target_id": self.target_id,
            "compliant": self.compliant,
            "dimension_verdicts": dict(self.dimension_verdicts),
            "violations": [dict(v) for v in self.violations],
            "report_sha256": self.report_sha256,
        }


__all__ = [
    "VALIDATION_INTELLIGENCE_CONTRACT_VERSION",
    "INTELLIGENCE_REPORT_FORMAT",
    "INTELLIGENCE_DASHBOARD_FORMAT",
    "COMPATIBILITY_REPORT_FORMAT",
    "COMPLIANCE_REPORT_FORMAT",
    "INTELLIGENCE_AUTHORITY",
    "DimensionKind",
    "IntelligenceDimension",
    "dimensions_of_kind",
    "Severity",
    "FindingStatus",
    "Verdict",
    "IntelligenceTarget",
    "Finding",
    "DimensionReport",
    "ValidationIntelligenceReport",
    "IntelligenceDashboard",
    "CompatibilityReport",
    "ComplianceReport",
]
