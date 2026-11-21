"""UCOS-EPIC-014 — Commercial Intelligence contracts (Terminal T5).

The immutable, deterministic value types the Commercial Intelligence engine speaks.
Every type is **immutable, typed, deterministic, and serializable** and holds no runtime
state, so an identical :class:`CommercialTarget` analyzed by an identical analyzer suite
yields a byte-identical :class:`CommercialIntelligenceReport` and content hash
(IMP-007 §5) — no wall-clock, locale, or ambient state leaks into any identity.

Two disciplines are constitutional here:

    * **Integer money.** :class:`Money` carries an ISO-4217-shaped currency and an
      *integer* count of minor units. No binary float ever touches a commercial amount,
      so a price, discount, quote or investment flow is reproducible on every machine.
      Combining two currencies raises rather than silently coercing.
    * **Fourteen governed domains.** :class:`CommercialDomain` enumerates the mandated
      commercial domains in canonical order, each classified by a :class:`DomainKind`
      (offer, commerce, governance, assurance) so the Commercial Validation report and
      the Commercial Certification verdict are deterministic *projections* of one
      report rather than independently asserted judgements.

Nothing here is bound to a specific market, product, price list, customer or currency:
the vocabulary defines the *shape*; the concrete commercial facts are supplied by the
target, and the concrete checks by the analyzers.
"""

from __future__ import annotations

import re
from collections.abc import Mapping
from dataclasses import dataclass, field
from enum import Enum
from platform.commercial_intelligence.errors import CommercialTargetError, MoneyError
from platform.foundation.contracts import content_hash
from typing import Any

from engine.runtime.disclosure import build_disclosure

#: The semantic version of the Commercial Intelligence contract surface (AR-03/PL-05).
COMMERCIAL_CONTRACT_VERSION = "1.0.0"

#: Format identifiers for the deliverables projected from a commercial run.
COMMERCIAL_REPORT_FORMAT = "ucos-commercial-intelligence-report/1.0.0"
COMMERCIAL_DASHBOARD_FORMAT = "ucos-commercial-intelligence-dashboard/1.0.0"

#: Commercial intelligence confers no constitutional authority (DE-05 / IP-01): a run
#: records engineering readiness only. Embedded verbatim in every report.
COMMERCIAL_AUTHORITY = "ENGINEERING-EXECUTION-ONLY"

#: One hundred percent expressed in basis points — the only percentage unit used, so
#: every proportional computation stays in integer arithmetic.
BASIS_POINTS_SCALE = 10_000

_CURRENCY_PATTERN = re.compile(r"^[A-Z]{3}$")


class DomainKind(str, Enum):
    """The family a commercial domain belongs to (drives the report's projections)."""

    OFFER = "offer"
    COMMERCE = "commerce"
    GOVERNANCE = "governance"
    ASSURANCE = "assurance"


class CommercialDomain(str, Enum):
    """The fourteen mandated commercial-intelligence domains, in canonical order."""

    MARKETPLACE_INTELLIGENCE = "marketplace_intelligence"
    LICENSING_INTELLIGENCE = "licensing_intelligence"
    PRODUCT_INTELLIGENCE = "product_intelligence"
    PORTFOLIO_INTELLIGENCE = "portfolio_intelligence"
    BUSINESS_DOCUMENTATION = "business_documentation"
    COMMERCIAL_PACKAGES = "commercial_packages"
    PRICING_INTELLIGENCE = "pricing_intelligence"
    INVESTMENT_INTELLIGENCE = "investment_intelligence"
    CUSTOMER_INTELLIGENCE = "customer_intelligence"
    POLICY_GOVERNANCE = "policy_governance"
    APPROVAL_INTELLIGENCE = "approval_intelligence"
    BUSINESS_EVIDENCE = "business_evidence"
    COMMERCIAL_VALIDATION = "commercial_validation"
    COMMERCIAL_CERTIFICATION = "commercial_certification"

    @classmethod
    def parse(cls, value: Any) -> CommercialDomain:
        """Parse a domain, raising :class:`CommercialTargetError` on an unknown one."""
        try:
            return cls(value)
        except ValueError as exc:
            raise CommercialTargetError(
                "unknown commercial-intelligence domain",
                domain=value,
                supported=[d.value for d in cls],
            ) from exc

    @property
    def order(self) -> int:
        """The canonical (declaration-order) index, for deterministic ordering."""
        return _DOMAIN_ORDER[self]

    @property
    def kind(self) -> DomainKind:
        """The family this domain belongs to."""
        return _DOMAIN_KIND[self]


_DOMAIN_ORDER: dict[CommercialDomain, int] = {d: i for i, d in enumerate(CommercialDomain)}

_DOMAIN_KIND: dict[CommercialDomain, DomainKind] = {
    CommercialDomain.MARKETPLACE_INTELLIGENCE: DomainKind.OFFER,
    CommercialDomain.LICENSING_INTELLIGENCE: DomainKind.COMMERCE,
    CommercialDomain.PRODUCT_INTELLIGENCE: DomainKind.OFFER,
    CommercialDomain.PORTFOLIO_INTELLIGENCE: DomainKind.OFFER,
    CommercialDomain.BUSINESS_DOCUMENTATION: DomainKind.GOVERNANCE,
    CommercialDomain.COMMERCIAL_PACKAGES: DomainKind.OFFER,
    CommercialDomain.PRICING_INTELLIGENCE: DomainKind.COMMERCE,
    CommercialDomain.INVESTMENT_INTELLIGENCE: DomainKind.COMMERCE,
    CommercialDomain.CUSTOMER_INTELLIGENCE: DomainKind.COMMERCE,
    CommercialDomain.POLICY_GOVERNANCE: DomainKind.GOVERNANCE,
    CommercialDomain.APPROVAL_INTELLIGENCE: DomainKind.GOVERNANCE,
    CommercialDomain.BUSINESS_EVIDENCE: DomainKind.ASSURANCE,
    CommercialDomain.COMMERCIAL_VALIDATION: DomainKind.ASSURANCE,
    CommercialDomain.COMMERCIAL_CERTIFICATION: DomainKind.ASSURANCE,
}


def domains_of_kind(kind: DomainKind) -> tuple[CommercialDomain, ...]:
    """Return the domains of ``kind`` in canonical order."""
    return tuple(d for d in sorted(CommercialDomain, key=lambda x: x.order) if d.kind is kind)


class Severity(str, Enum):
    """Whether a failing finding blocks the verdict or is merely advisory."""

    BLOCKING = "blocking"
    ADVISORY = "advisory"


class FindingStatus(str, Enum):
    """The fail-closed outcome of a single commercial check."""

    PASS = "pass"  # noqa: S105 — enum member, not a credential
    FAIL = "fail"


class Verdict(str, Enum):
    """The aggregate verdict of a domain report or commercial report (fail-closed)."""

    PASS = "pass"  # noqa: S105 — enum member, not a credential
    FAIL = "fail"


@dataclass(frozen=True, slots=True)
class Money:
    """An exact monetary amount: an ISO-4217-shaped currency and integer minor units.

    All commercial arithmetic in this package is integer arithmetic on ``minor_units``
    (cents, pence, …). Proportional operations take *basis points* and round half-up on
    the magnitude, so the result is identical on every platform and never drifts.
    """

    currency: str
    minor_units: int

    def __post_init__(self) -> None:
        if not isinstance(self.currency, str) or not _CURRENCY_PATTERN.match(self.currency):
            raise MoneyError(
                "a monetary amount requires a three-letter upper-case currency code",
                currency=self.currency,
            )
        if isinstance(self.minor_units, bool) or not isinstance(self.minor_units, int):
            raise MoneyError(
                "a monetary amount requires integer minor units (no floating point)",
                currency=self.currency,
                minor_units=repr(self.minor_units),
            )

    @classmethod
    def zero(cls, currency: str) -> Money:
        """The additive identity in ``currency``."""
        return cls(currency=currency, minor_units=0)

    @classmethod
    def from_mapping(cls, raw: Any, *, context: str = "amount") -> Money:
        """Assimilate ``{"currency": ..., "minor_units": ...}`` into a :class:`Money`."""
        if not isinstance(raw, Mapping):
            raise MoneyError("a monetary amount must be a mapping", context=context)
        return cls(currency=raw.get("currency"), minor_units=raw.get("minor_units"))

    def _require_same_currency(self, other: Money) -> None:
        if self.currency != other.currency:
            raise MoneyError(
                "monetary amounts in different currencies may not be combined",
                left=self.currency,
                right=other.currency,
            )

    def add(self, other: Money) -> Money:
        self._require_same_currency(other)
        return Money(self.currency, self.minor_units + other.minor_units)

    def subtract(self, other: Money) -> Money:
        self._require_same_currency(other)
        return Money(self.currency, self.minor_units - other.minor_units)

    def scale(self, factor: int) -> Money:
        """Multiply by an integer factor (e.g. a seat count or a quantity)."""
        if isinstance(factor, bool) or not isinstance(factor, int):
            raise MoneyError("a monetary amount may only be scaled by an integer", factor=factor)
        return Money(self.currency, self.minor_units * factor)

    def apply_basis_points(self, basis_points: int) -> Money:
        """Return ``basis_points`` (1/100 of a percent) of this amount, half-up rounded."""
        if isinstance(basis_points, bool) or not isinstance(basis_points, int):
            raise MoneyError("basis points must be an integer", basis_points=basis_points)
        magnitude = abs(self.minor_units) * basis_points
        rounded = (magnitude + BASIS_POINTS_SCALE // 2) // BASIS_POINTS_SCALE
        return Money(self.currency, -rounded if self.minor_units < 0 else rounded)

    @property
    def is_zero(self) -> bool:
        return self.minor_units == 0

    @property
    def is_negative(self) -> bool:
        return self.minor_units < 0

    def compare(self, other: Money) -> int:
        """Return -1, 0 or 1 — a total order within one currency."""
        self._require_same_currency(other)
        if self.minor_units == other.minor_units:
            return 0
        return -1 if self.minor_units < other.minor_units else 1

    def to_dict(self) -> dict[str, Any]:
        return {"currency": self.currency, "minor_units": self.minor_units}


def sum_money(amounts: tuple[Money, ...] | list[Money], *, currency: str) -> Money:
    """Sum ``amounts`` in ``currency``; an empty sequence yields zero in that currency."""
    total = Money.zero(currency)
    for amount in amounts:
        total = total.add(amount)
    return total


@dataclass(frozen=True, slots=True)
class CommercialTarget:
    """A normalized, domain-keyed projection of the commercial surface under analysis.

    ``facts`` maps a :class:`CommercialDomain` *value* to the immutable commercial
    evidence that domain's analyzers reason over. Analyzers read only the facts they
    need; an absent or malformed fact yields a fail-closed FAIL finding, never an
    exception and never an assumed commercial position.
    """

    target_id: str
    facts: Mapping[str, Mapping[str, Any]] = field(default_factory=dict)

    @classmethod
    def from_mapping(cls, raw: Mapping[str, Any]) -> CommercialTarget:
        """Assimilate a mapping into a normalized :class:`CommercialTarget`.

        Raises:
            CommercialTargetError: if the mapping lacks a target id, names an unknown
                domain, or a per-domain facts value is not a mapping (authoring faults).
        """
        if not isinstance(raw, Mapping):
            raise CommercialTargetError("a commercial target must be a mapping")
        target_id = raw.get("target_id")
        if not target_id or not isinstance(target_id, str):
            raise CommercialTargetError("a commercial target requires a non-empty target_id")
        raw_facts = raw.get("facts", {})
        if not isinstance(raw_facts, Mapping):
            raise CommercialTargetError("target facts must be a mapping", target_id=target_id)
        facts: dict[str, dict[str, Any]] = {}
        for key, value in raw_facts.items():
            domain = CommercialDomain.parse(key)
            if not isinstance(value, Mapping):
                raise CommercialTargetError(
                    "domain facts must be a mapping",
                    target_id=target_id,
                    domain=domain.value,
                )
            facts[domain.value] = dict(value)
        return cls(target_id=str(target_id), facts=facts)

    def domain_facts(self, domain: CommercialDomain) -> Mapping[str, Any]:
        """Return the (possibly empty) facts mapping for ``domain``."""
        return self.facts.get(domain.value, {})

    def declared_domains(self) -> tuple[CommercialDomain, ...]:
        """The domains this target declares facts for, in canonical order."""
        declared = {CommercialDomain(key) for key in self.facts}
        return tuple(sorted(declared, key=lambda d: d.order))

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
    """The immutable, deterministic outcome of a single commercial check."""

    check_id: str
    domain: CommercialDomain
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
            "domain": self.domain.value,
            "severity": self.severity.value,
            "status": self.status.value,
            "message": self.message,
        }

    def to_dict(self) -> dict[str, Any]:
        return {**self.core(), "details": dict(self.details)}


def passed(check_id: str, domain: CommercialDomain, message: str = "", **details: Any) -> Finding:
    """A blocking check that proved its commercial invariant."""
    return Finding(
        check_id=check_id,
        domain=domain,
        severity=Severity.BLOCKING,
        status=FindingStatus.PASS,
        message=message,
        details=details,
    )


def failed(
    check_id: str,
    domain: CommercialDomain,
    message: str,
    *,
    severity: Severity = Severity.BLOCKING,
    **details: Any,
) -> Finding:
    """A check that could not prove its commercial invariant (fail-closed)."""
    return Finding(
        check_id=check_id,
        domain=domain,
        severity=severity,
        status=FindingStatus.FAIL,
        message=message,
        details=details,
    )


@dataclass(frozen=True, slots=True)
class DomainReport:
    """The ordered, deterministic aggregate of one commercial domain's findings."""

    domain: CommercialDomain
    verdict: Verdict
    findings: tuple[Finding, ...]

    @classmethod
    def create(cls, domain: CommercialDomain, findings: tuple[Finding, ...]) -> DomainReport:
        """Aggregate ``findings`` for ``domain``; verdict FAIL iff a blocking check failed."""
        verdict = Verdict.FAIL if any(f.is_blocking_failure for f in findings) else Verdict.PASS
        return cls(domain=domain, verdict=verdict, findings=findings)

    @property
    def kind(self) -> DomainKind:
        return self.domain.kind

    @property
    def passed(self) -> bool:
        return self.verdict is Verdict.PASS

    def blocking_failures(self) -> tuple[str, ...]:
        return tuple(f.check_id for f in self.findings if f.is_blocking_failure)

    def advisory_failures(self) -> tuple[str, ...]:
        return tuple(f.check_id for f in self.findings if f.is_advisory_failure)

    def counts(self) -> dict[str, int]:
        ok = sum(1 for f in self.findings if f.passed)
        return {
            "total": len(self.findings),
            "passed": ok,
            "failed": len(self.findings) - ok,
            "blocking_failed": len(self.blocking_failures()),
            "advisory_failed": len(self.advisory_failures()),
        }

    def core(self) -> dict[str, Any]:
        return {
            "domain": self.domain.value,
            "kind": self.domain.kind.value,
            "verdict": self.verdict.value,
            "findings": [f.core() for f in self.findings],
        }

    def to_dict(self) -> dict[str, Any]:
        return {
            "domain": self.domain.value,
            "kind": self.domain.kind.value,
            "verdict": self.verdict.value,
            "passed": self.passed,
            "counts": self.counts(),
            "blocking_failures": list(self.blocking_failures()),
            "advisory_failures": list(self.advisory_failures()),
            "findings": [f.to_dict() for f in self.findings],
        }


@dataclass(frozen=True, slots=True)
class CommercialIntelligenceReport:
    """The content-addressed, cross-domain aggregate of one commercial-intelligence run.

    The report is a **pure function of the target and the ordered domain outcomes**: its
    ``report_sha256`` hashes only the domain/finding cores (never volatile per-finding
    detail and never any wall-clock), so an identical commercial surface analyzed by an
    identical suite reproduces a byte-identical report. It asserts
    ``ENGINEERING-EXECUTION-ONLY`` authority and carries the EC-1 provisional-state
    disclosure (DE-05 / IP-01) — a commercial run ratifies nothing.
    """

    target_id: str
    verdict: Verdict
    target_digest: str
    domain_reports: tuple[DomainReport, ...]
    authority: str
    disclosure: Mapping[str, Any]
    report_sha256: str

    @staticmethod
    def _core(
        *,
        target_id: str,
        verdict: Verdict,
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
    ) -> CommercialIntelligenceReport:
        """Aggregate domain reports into an immutable, content-addressed report.

        The verdict is fail-closed: FAIL iff any *blocking* check failed in any domain.
        """
        verdict = (
            Verdict.FAIL if any(r.verdict is Verdict.FAIL for r in domain_reports) else Verdict.PASS
        )
        disclosure = build_disclosure()
        core = cls._core(
            target_id=target_id,
            verdict=verdict,
            target_digest=target_digest,
            domain_reports=domain_reports,
            authority=COMMERCIAL_AUTHORITY,
            disclosure=disclosure,
        )
        return cls(
            target_id=target_id,
            verdict=verdict,
            target_digest=target_digest,
            domain_reports=domain_reports,
            authority=COMMERCIAL_AUTHORITY,
            disclosure=disclosure,
            report_sha256=content_hash(core),
        )

    @property
    def passed(self) -> bool:
        return self.verdict is Verdict.PASS

    @property
    def all_findings(self) -> tuple[Finding, ...]:
        return tuple(f for report in self.domain_reports for f in report.findings)

    def domains_run(self) -> tuple[str, ...]:
        return tuple(r.domain.value for r in self.domain_reports)

    def report_for(self, domain: CommercialDomain) -> DomainReport | None:
        """The report for ``domain``, or ``None`` when the domain was not run."""
        for report in self.domain_reports:
            if report.domain is domain:
                return report
        return None

    def reports_of_kind(self, kind: DomainKind) -> tuple[DomainReport, ...]:
        """The domain reports whose domain belongs to ``kind`` (canonical order)."""
        return tuple(r for r in self.domain_reports if r.domain.kind is kind)

    def counts(self) -> dict[str, int]:
        findings = self.all_findings
        ok = sum(1 for f in findings if f.passed)
        return {
            "domains": len(self.domain_reports),
            "total": len(findings),
            "passed": ok,
            "failed": len(findings) - ok,
            "blocking_failed": sum(1 for f in findings if f.is_blocking_failure),
            "advisory_failed": sum(1 for f in findings if f.is_advisory_failure),
        }

    def blocking_failures(self) -> tuple[str, ...]:
        return tuple(f.check_id for f in self.all_findings if f.is_blocking_failure)

    def advisory_failures(self) -> tuple[str, ...]:
        return tuple(f.check_id for f in self.all_findings if f.is_advisory_failure)

    def domain_verdicts(self) -> dict[str, str]:
        return {r.domain.value: r.verdict.value for r in self.domain_reports}

    def kind_verdicts(self) -> dict[str, str]:
        """The fail-closed verdict per domain family (a family with no run domain passes)."""
        return {
            kind.value: (
                Verdict.FAIL.value
                if any(not r.passed for r in self.reports_of_kind(kind))
                else Verdict.PASS.value
            )
            for kind in DomainKind
        }

    def dashboard(self) -> CommercialDashboard:
        """Project the deterministic Commercial Intelligence Dashboard from this report."""
        return CommercialDashboard.from_report(self)

    def to_dict(self) -> dict[str, Any]:
        return {
            "report_format": COMMERCIAL_REPORT_FORMAT,
            "target_id": self.target_id,
            "verdict": self.verdict.value,
            "passed": self.passed,
            "target_digest": self.target_digest,
            "counts": self.counts(),
            "domain_verdicts": self.domain_verdicts(),
            "kind_verdicts": self.kind_verdicts(),
            "blocking_failures": list(self.blocking_failures()),
            "advisory_failures": list(self.advisory_failures()),
            "domains": [r.to_dict() for r in self.domain_reports],
            "authority": self.authority,
            "disclosure": dict(self.disclosure),
            "report_sha256": self.report_sha256,
        }


@dataclass(frozen=True, slots=True)
class CommercialDashboard:
    """A deterministic, content-addressed dashboard projection of a commercial run."""

    target_id: str
    verdict: Verdict
    domains_total: int
    checks_total: int
    checks_passed: int
    checks_failed: int
    domain_verdicts: dict[str, str]
    kind_verdicts: dict[str, str]
    blocking_failures: tuple[str, ...]
    advisory_failures: tuple[str, ...]
    dashboard_sha256: str

    @classmethod
    def from_report(cls, report: CommercialIntelligenceReport) -> CommercialDashboard:
        counts = report.counts()
        core = {
            "target_id": report.target_id,
            "verdict": report.verdict.value,
            "domains_total": counts["domains"],
            "checks_total": counts["total"],
            "checks_passed": counts["passed"],
            "checks_failed": counts["failed"],
            "domain_verdicts": report.domain_verdicts(),
            "kind_verdicts": report.kind_verdicts(),
            "blocking_failures": list(report.blocking_failures()),
            "advisory_failures": list(report.advisory_failures()),
        }
        return cls(
            target_id=report.target_id,
            verdict=report.verdict,
            domains_total=counts["domains"],
            checks_total=counts["total"],
            checks_passed=counts["passed"],
            checks_failed=counts["failed"],
            domain_verdicts=report.domain_verdicts(),
            kind_verdicts=report.kind_verdicts(),
            blocking_failures=report.blocking_failures(),
            advisory_failures=report.advisory_failures(),
            dashboard_sha256=content_hash(core),
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "dashboard_format": COMMERCIAL_DASHBOARD_FORMAT,
            "target_id": self.target_id,
            "verdict": self.verdict.value,
            "domains_total": self.domains_total,
            "checks_total": self.checks_total,
            "checks_passed": self.checks_passed,
            "checks_failed": self.checks_failed,
            "domain_verdicts": dict(self.domain_verdicts),
            "kind_verdicts": dict(self.kind_verdicts),
            "blocking_failures": list(self.blocking_failures),
            "advisory_failures": list(self.advisory_failures),
            "dashboard_sha256": self.dashboard_sha256,
        }


__all__ = [
    "COMMERCIAL_CONTRACT_VERSION",
    "COMMERCIAL_REPORT_FORMAT",
    "COMMERCIAL_DASHBOARD_FORMAT",
    "COMMERCIAL_AUTHORITY",
    "BASIS_POINTS_SCALE",
    "DomainKind",
    "CommercialDomain",
    "domains_of_kind",
    "Severity",
    "FindingStatus",
    "Verdict",
    "Money",
    "sum_money",
    "CommercialTarget",
    "Finding",
    "passed",
    "failed",
    "DomainReport",
    "CommercialIntelligenceReport",
    "CommercialDashboard",
]
