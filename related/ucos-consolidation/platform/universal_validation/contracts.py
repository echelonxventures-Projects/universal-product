"""UCOS-EPIC-005 — Universal Validation contracts (Terminal T5).

The immutable, deterministic value types the Universal Validation Engine speaks.
Every type is **immutable, typed, deterministic, and serializable** and holds no
runtime state, so an identical :class:`ValidationTarget` validated by an identical
rule suite yields a byte-identical :class:`ValidationReport` and content hash
(IMP-007 §5) — no wall-clock or ambient state leaks into any identity.

    * :class:`ValidationDomain` — the seven universal validation domains, declared in
      the mission's canonical order (Architecture … Quality).
    * :class:`RuleSeverity` — whether a failing rule blocks the verdict or is advisory.
    * :class:`RuleStatus` / :class:`EngineVerdict` — fail-closed outcomes.
    * :class:`ValidationTarget` — the normalized, domain-keyed projection of the
      system under validation; rules are pure functions of it.
    * :class:`RuleResult` — the immutable outcome of a single rule.
    * :class:`DomainReport` — the ordered, deterministic per-domain aggregate.
    * :class:`ValidationReport` — the content-addressed cross-domain aggregate; it
      asserts ``ENGINEERING-EXECUTION-ONLY`` authority and carries the EC-1
      provisional-state disclosure (DE-05 / IP-01).
    * :class:`ValidationDashboard` — the deterministic dashboard projection.

Nothing here is hardcoded to a specific system: the vocabulary defines the *shape*;
the concrete facts are supplied by the target, and the concrete rules by the suite.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field
from enum import Enum
from platform.foundation.contracts import content_hash
from platform.universal_validation.errors import ValidationTargetError
from typing import Any

from engine.runtime.disclosure import build_disclosure

#: The semantic version of the Universal Validation contract surface (AR-03/PL-05).
UNIVERSAL_VALIDATION_CONTRACT_VERSION = "1.0.0"

#: The validation report format identifier.
VALIDATION_REPORT_FORMAT = "ucos-universal-validation-report/1.0.0"

#: The validation dashboard format identifier.
VALIDATION_DASHBOARD_FORMAT = "ucos-universal-validation-dashboard/1.0.0"

#: Universal validation confers no constitutional authority (DE-05 / IP-01): a run
#: records engineering readiness only. Embedded verbatim in every report.
VALIDATION_AUTHORITY = "ENGINEERING-EXECUTION-ONLY"


class ValidationDomain(str, Enum):
    """The seven universal validation domains, in the mission's canonical order."""

    ARCHITECTURE = "architecture"
    IMPLEMENTATION = "implementation"
    DEPENDENCY = "dependency"
    REGISTRY = "registry"
    SCHEMA = "schema"
    RUNTIME = "runtime"
    QUALITY = "quality"

    @classmethod
    def parse(cls, value: Any) -> ValidationDomain:
        """Parse a domain, raising :class:`ValidationTargetError` on an unknown one."""
        try:
            return cls(value)
        except ValueError as exc:
            raise ValidationTargetError(
                "unknown validation domain",
                domain=value,
                supported=[d.value for d in cls],
            ) from exc

    @property
    def order(self) -> int:
        """The canonical (declaration-order) index, for deterministic ordering."""
        return _DOMAIN_ORDER[self]


_DOMAIN_ORDER: dict[ValidationDomain, int] = {d: i for i, d in enumerate(ValidationDomain)}


class RuleSeverity(str, Enum):
    """Whether a failing rule blocks the verdict or is merely advisory."""

    BLOCKING = "blocking"
    ADVISORY = "advisory"


class RuleStatus(str, Enum):
    """The fail-closed outcome of a single validation rule."""

    PASS = "pass"  # noqa: S105 — enum member, not a credential
    FAIL = "fail"


class EngineVerdict(str, Enum):
    """The aggregate verdict of a domain report or a validation report (fail-closed)."""

    PASS = "pass"  # noqa: S105 — enum member, not a credential
    FAIL = "fail"


@dataclass(frozen=True, slots=True)
class ValidationTarget:
    """A normalized, domain-keyed projection of the system under validation.

    ``facts`` maps a :class:`ValidationDomain` *value* to the immutable evidence that
    domain's rules evaluate. Rules read only the facts they need; an absent or
    malformed fact yields a fail-closed FAIL finding (never an exception).
    """

    target_id: str
    facts: Mapping[str, Mapping[str, Any]] = field(default_factory=dict)

    @classmethod
    def from_mapping(cls, raw: Mapping[str, Any]) -> ValidationTarget:
        """Assimilate a mapping into a normalized :class:`ValidationTarget`.

        Raises:
            ValidationTargetError: if the mapping lacks a target id, or a per-domain
                facts value is not a mapping (a malformed *authoring* fault).
        """
        if not isinstance(raw, Mapping):
            raise ValidationTargetError("a validation target must be a mapping")
        target_id = raw.get("target_id")
        if not target_id or not isinstance(target_id, str):
            raise ValidationTargetError("a validation target requires a non-empty target_id")
        raw_facts = raw.get("facts", {})
        if not isinstance(raw_facts, Mapping):
            raise ValidationTargetError("target facts must be a mapping", target_id=target_id)
        facts: dict[str, dict[str, Any]] = {}
        for key, value in raw_facts.items():
            domain = ValidationDomain.parse(key)
            if not isinstance(value, Mapping):
                raise ValidationTargetError(
                    "domain facts must be a mapping",
                    target_id=target_id,
                    domain=domain.value,
                )
            facts[domain.value] = dict(value)
        return cls(target_id=str(target_id), facts=facts)

    def domain_facts(self, domain: ValidationDomain) -> Mapping[str, Any]:
        """Return the (possibly empty) facts mapping for ``domain``."""
        return self.facts.get(domain.value, {})

    def to_dict(self) -> dict[str, Any]:
        return {
            "target_id": self.target_id,
            "facts": {key: dict(value) for key, value in sorted(self.facts.items())},
        }

    def digest(self) -> str:
        """The deterministic content hash of the target (a stable target identity)."""
        return content_hash(self.to_dict())


@dataclass(frozen=True, slots=True)
class RuleResult:
    """The immutable, deterministic outcome of a single validation rule."""

    rule_id: str
    domain: ValidationDomain
    severity: RuleSeverity
    status: RuleStatus
    message: str = ""
    details: Mapping[str, Any] = field(default_factory=dict)

    @property
    def passed(self) -> bool:
        return self.status is RuleStatus.PASS

    @property
    def failed(self) -> bool:
        return self.status is RuleStatus.FAIL

    @property
    def is_blocking_failure(self) -> bool:
        return self.failed and self.severity is RuleSeverity.BLOCKING

    @property
    def is_advisory_failure(self) -> bool:
        return self.failed and self.severity is RuleSeverity.ADVISORY

    def core(self) -> dict[str, Any]:
        """The canonical, hashable core of the result (excludes volatile detail)."""
        return {
            "rule_id": self.rule_id,
            "domain": self.domain.value,
            "severity": self.severity.value,
            "status": self.status.value,
            "message": self.message,
        }

    def to_dict(self) -> dict[str, Any]:
        return {**self.core(), "details": dict(self.details)}


@dataclass(frozen=True, slots=True)
class DomainReport:
    """The ordered, deterministic aggregate of one domain's rule results."""

    domain: ValidationDomain
    verdict: EngineVerdict
    results: tuple[RuleResult, ...]

    @classmethod
    def create(cls, domain: ValidationDomain, results: tuple[RuleResult, ...]) -> DomainReport:
        """Aggregate ``results`` for ``domain``; verdict FAIL iff a blocking rule failed."""
        verdict = (
            EngineVerdict.FAIL
            if any(r.is_blocking_failure for r in results)
            else EngineVerdict.PASS
        )
        return cls(domain=domain, verdict=verdict, results=results)

    @property
    def passed(self) -> bool:
        return self.verdict is EngineVerdict.PASS

    def blocking_failures(self) -> tuple[str, ...]:
        return tuple(r.rule_id for r in self.results if r.is_blocking_failure)

    def advisory_failures(self) -> tuple[str, ...]:
        return tuple(r.rule_id for r in self.results if r.is_advisory_failure)

    def counts(self) -> dict[str, int]:
        passed = sum(1 for r in self.results if r.passed)
        return {
            "total": len(self.results),
            "passed": passed,
            "failed": len(self.results) - passed,
            "blocking_failed": len(self.blocking_failures()),
            "advisory_failed": len(self.advisory_failures()),
        }

    def core(self) -> dict[str, Any]:
        return {
            "domain": self.domain.value,
            "verdict": self.verdict.value,
            "results": [r.core() for r in self.results],
        }

    def to_dict(self) -> dict[str, Any]:
        return {
            "domain": self.domain.value,
            "verdict": self.verdict.value,
            "passed": self.passed,
            "counts": self.counts(),
            "blocking_failures": list(self.blocking_failures()),
            "advisory_failures": list(self.advisory_failures()),
            "results": [r.to_dict() for r in self.results],
        }


@dataclass(frozen=True, slots=True)
class ValidationReport:
    """The content-addressed, cross-domain aggregate of a universal validation run.

    The report is a **pure function of the target and the ordered domain outcomes**:
    its ``report_sha256`` hashes only the domain/rule cores (never volatile per-rule
    detail or any wall-clock), so an identical target validated by an identical suite
    reproduces a byte-identical report. It asserts ``ENGINEERING-EXECUTION-ONLY``
    authority and carries the EC-1 provisional-state disclosure (DE-05 / IP-01).
    """

    target_id: str
    verdict: EngineVerdict
    target_digest: str
    domain_reports: tuple[DomainReport, ...]
    authority: str
    disclosure: Mapping[str, Any]
    report_sha256: str

    @staticmethod
    def _core(
        *,
        target_id: str,
        verdict: EngineVerdict,
        target_digest: str,
        domain_reports: tuple[DomainReport, ...],
        authority: str,
        disclosure: Mapping[str, Any],
    ) -> dict[str, Any]:
        return {
            "target_id": target_id,
            "verdict": verdict.value,
            "target_digest": target_digest,
            "domains": [r.core() for r in domain_reports],
            "authority": authority,
            "disclosure": dict(disclosure),
        }

    @classmethod
    def create(
        cls,
        *,
        target_id: str,
        target_digest: str,
        domain_reports: tuple[DomainReport, ...],
    ) -> ValidationReport:
        """Aggregate domain reports into an immutable, content-addressed report.

        The verdict is fail-closed: FAIL iff any *blocking* rule failed in any domain.
        """
        verdict = (
            EngineVerdict.FAIL
            if any(r.verdict is EngineVerdict.FAIL for r in domain_reports)
            else EngineVerdict.PASS
        )
        disclosure = build_disclosure()
        core = cls._core(
            target_id=target_id,
            verdict=verdict,
            target_digest=target_digest,
            domain_reports=domain_reports,
            authority=VALIDATION_AUTHORITY,
            disclosure=disclosure,
        )
        return cls(
            target_id=target_id,
            verdict=verdict,
            target_digest=target_digest,
            domain_reports=domain_reports,
            authority=VALIDATION_AUTHORITY,
            disclosure=disclosure,
            report_sha256=content_hash(core),
        )

    @property
    def passed(self) -> bool:
        return self.verdict is EngineVerdict.PASS

    @property
    def all_results(self) -> tuple[RuleResult, ...]:
        return tuple(r for report in self.domain_reports for r in report.results)

    def domains_run(self) -> tuple[str, ...]:
        return tuple(r.domain.value for r in self.domain_reports)

    def counts(self) -> dict[str, int]:
        results = self.all_results
        passed = sum(1 for r in results if r.passed)
        return {
            "domains": len(self.domain_reports),
            "total": len(results),
            "passed": passed,
            "failed": len(results) - passed,
            "blocking_failed": sum(1 for r in results if r.is_blocking_failure),
            "advisory_failed": sum(1 for r in results if r.is_advisory_failure),
        }

    def blocking_failures(self) -> tuple[str, ...]:
        return tuple(r.rule_id for r in self.all_results if r.is_blocking_failure)

    def advisory_failures(self) -> tuple[str, ...]:
        return tuple(r.rule_id for r in self.all_results if r.is_advisory_failure)

    def domain_verdicts(self) -> dict[str, str]:
        return {r.domain.value: r.verdict.value for r in self.domain_reports}

    def dashboard(self) -> ValidationDashboard:
        """Project the deterministic Validation Dashboard from this report."""
        return ValidationDashboard.from_report(self)

    def to_dict(self) -> dict[str, Any]:
        return {
            "report_format": VALIDATION_REPORT_FORMAT,
            "target_id": self.target_id,
            "verdict": self.verdict.value,
            "passed": self.passed,
            "target_digest": self.target_digest,
            "counts": self.counts(),
            "domain_verdicts": self.domain_verdicts(),
            "blocking_failures": list(self.blocking_failures()),
            "advisory_failures": list(self.advisory_failures()),
            "domains": [r.to_dict() for r in self.domain_reports],
            "authority": self.authority,
            "disclosure": dict(self.disclosure),
            "report_sha256": self.report_sha256,
        }


@dataclass(frozen=True, slots=True)
class ValidationDashboard:
    """A deterministic, content-addressed dashboard projection of a validation run."""

    target_id: str
    verdict: EngineVerdict
    domains_total: int
    rules_total: int
    rules_passed: int
    rules_failed: int
    domain_verdicts: dict[str, str]
    blocking_failures: tuple[str, ...]
    advisory_failures: tuple[str, ...]
    dashboard_sha256: str

    @classmethod
    def from_report(cls, report: ValidationReport) -> ValidationDashboard:
        counts = report.counts()
        core = {
            "target_id": report.target_id,
            "verdict": report.verdict.value,
            "domains_total": counts["domains"],
            "rules_total": counts["total"],
            "rules_passed": counts["passed"],
            "rules_failed": counts["failed"],
            "domain_verdicts": report.domain_verdicts(),
            "blocking_failures": list(report.blocking_failures()),
            "advisory_failures": list(report.advisory_failures()),
        }
        return cls(
            target_id=report.target_id,
            verdict=report.verdict,
            domains_total=counts["domains"],
            rules_total=counts["total"],
            rules_passed=counts["passed"],
            rules_failed=counts["failed"],
            domain_verdicts=report.domain_verdicts(),
            blocking_failures=report.blocking_failures(),
            advisory_failures=report.advisory_failures(),
            dashboard_sha256=content_hash(core),
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "dashboard_format": VALIDATION_DASHBOARD_FORMAT,
            "target_id": self.target_id,
            "verdict": self.verdict.value,
            "domains_total": self.domains_total,
            "rules_total": self.rules_total,
            "rules_passed": self.rules_passed,
            "rules_failed": self.rules_failed,
            "domain_verdicts": dict(self.domain_verdicts),
            "blocking_failures": list(self.blocking_failures),
            "advisory_failures": list(self.advisory_failures),
            "dashboard_sha256": self.dashboard_sha256,
        }


__all__ = [
    "UNIVERSAL_VALIDATION_CONTRACT_VERSION",
    "VALIDATION_REPORT_FORMAT",
    "VALIDATION_DASHBOARD_FORMAT",
    "VALIDATION_AUTHORITY",
    "ValidationDomain",
    "RuleSeverity",
    "RuleStatus",
    "EngineVerdict",
    "ValidationTarget",
    "RuleResult",
    "DomainReport",
    "ValidationReport",
    "ValidationDashboard",
]
