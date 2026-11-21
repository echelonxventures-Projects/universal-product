"""UCOS-EPIC-014 — Validation Generation (Terminal T7).

The third owned capability. **Validation Generation** turns a policy-derived
:class:`~platform.universal_assurance.planning.AssurancePlan` into an executable
:class:`GeneratedSuite` by *binding* every planned obligation to a concrete
implementation in the **reused** validation platform:

    * an obligation of kind ``validation-rule`` binds to a
      :class:`~platform.universal_validation.rules.ValidationRule` in the reused
      built-in suite (:func:`~platform.universal_validation.rules.default_rules`), and
    * an obligation of kind ``intelligence-dimension`` binds to an
      :class:`~platform.validation_intelligence.contracts.IntelligenceDimension`
      analyzed by the reused Continuous Validation Intelligence engine.

Nothing is generated *ex nihilo*: generation never writes a new rule implementation. It
resolves declared refs against the reusable catalogue, so the policy stays the only
place obligations are enumerated and the platform stays the only place they are
implemented (no duplication — the mission's reuse mandate).

Generation is **fail-closed**: an obligation whose ref resolves to no implementation is
recorded as **unbound** with the reason, never dropped and never assumed to pass. A
divergence between the severity the *policy* declares and the severity the *reused
implementation* carries is recorded explicitly; at execution time the **policy severity
governs**, because the policy is the assurance authority.

Generation is **measurable** (:meth:`GeneratedSuite.observations`) and **reproducible**:
checks are ordered canonically and the suite embeds no wall-clock, so an identical plan
yields a byte-identical suite and ``suite_sha256`` (IMP-007 §5).
"""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from platform.foundation.contracts import content_hash
from platform.universal_assurance.contracts import ObligationKind, Severity
from platform.universal_assurance.errors import AssuranceGenerationError
from platform.universal_assurance.planning import (
    REASON_UNSATISFIABLE,
    AssurancePlan,
    PlannedObligation,
)
from platform.universal_validation.contracts import ValidationDomain
from platform.universal_validation.rules import ValidationRule, default_rules
from platform.validation_intelligence.contracts import IntelligenceDimension
from typing import Any

#: The generated-suite format identifier.
SUITE_FORMAT = "ucos-assurance-validation-suite/1.0.0"

#: The reasons an obligation may fail to bind (recorded, never raised).
UNBOUND_UNKNOWN_RULE = "unknown-validation-rule"
UNBOUND_UNKNOWN_DIMENSION = "unknown-intelligence-dimension"
UNBOUND_UNSUPPORTED_KIND = "unsupported-obligation-kind"
#: Reused from planning: the same condition must not carry two spellings.
UNBOUND_UNSATISFIABLE = REASON_UNSATISFIABLE


class RuleCatalog:
    """A read-only index of the reusable validation implementations, keyed by ref.

    The catalogue is the *only* bridge between a policy ref and an implementation. It
    is built from the reused platform suites, so this package contributes no rule of its
    own (reuse, not duplication).
    """

    __slots__ = ("_rules", "_dimensions")

    def __init__(
        self,
        rules: Iterable[ValidationRule] | None = None,
        *,
        dimensions: Iterable[IntelligenceDimension] | None = None,
    ) -> None:
        selected = tuple(rules) if rules is not None else default_rules()
        index: dict[str, ValidationRule] = {}
        for rule in selected:
            rule_id = getattr(rule, "rule_id", None)
            if not isinstance(rule_id, str) or not rule_id:
                raise AssuranceGenerationError(
                    "a catalogued validation rule has no rule_id",
                    rule=type(rule).__name__,
                )
            if rule_id in index:
                raise AssuranceGenerationError(
                    "the rule catalogue declares a duplicate rule id", rule_id=rule_id
                )
            index[rule_id] = rule
        self._rules = index
        self._dimensions = frozenset(
            dimensions if dimensions is not None else tuple(IntelligenceDimension)
        )

    @property
    def rule_ids(self) -> tuple[str, ...]:
        return tuple(sorted(self._rules))

    @property
    def dimension_ids(self) -> tuple[str, ...]:
        return tuple(sorted(d.value for d in self._dimensions))

    def rule(self, ref: str) -> ValidationRule | None:
        """The catalogued rule for ``ref``, or ``None`` when unknown (fail-closed)."""
        return self._rules.get(ref)

    def dimension(self, ref: str) -> IntelligenceDimension | None:
        """The catalogued intelligence dimension for ``ref``, or ``None`` when unknown."""
        for dimension in self._dimensions:
            if dimension.value == ref:
                return dimension
        return None

    def to_dict(self) -> dict[str, Any]:
        return {"rules": list(self.rule_ids), "dimensions": list(self.dimension_ids)}


@dataclass(frozen=True, slots=True)
class GeneratedCheck:
    """One planned obligation bound (or provably not bound) to a reused implementation."""

    obligation_id: str
    kind: ObligationKind
    ref: str
    policy_severity: Severity
    bound: bool
    unbound_reason: str = ""
    implementation: str = ""
    domain: str = ""
    dimension: str = ""
    implementation_severity: str = ""

    @property
    def severity_diverges(self) -> bool:
        """True iff the reused implementation's severity differs from the policy's."""
        return bool(self.implementation_severity) and (
            self.implementation_severity != self.policy_severity.value
        )

    @property
    def is_blocking_shortfall(self) -> bool:
        """True iff a *blocking* obligation could not be bound (fail-closed)."""
        return not self.bound and self.policy_severity is Severity.BLOCKING

    def core(self) -> dict[str, Any]:
        return {
            "obligation_id": self.obligation_id,
            "kind": self.kind.value,
            "ref": self.ref,
            "policy_severity": self.policy_severity.value,
            "bound": self.bound,
            "unbound_reason": self.unbound_reason,
            "implementation": self.implementation,
            "domain": self.domain,
            "dimension": self.dimension,
            "implementation_severity": self.implementation_severity,
        }

    def to_dict(self) -> dict[str, Any]:
        return {**self.core(), "severity_diverges": self.severity_diverges}


@dataclass(frozen=True, slots=True)
class GeneratedSuite:
    """An immutable, content-addressed executable suite generated from a plan."""

    suite_id: str
    plan_id: str
    subject_id: str
    policy_digest: str
    plan_sha256: str
    checks: tuple[GeneratedCheck, ...]
    rules: tuple[ValidationRule, ...]
    dimensions: tuple[IntelligenceDimension, ...]
    catalog_rule_ids: tuple[str, ...]
    suite_sha256: str

    @staticmethod
    def _core(
        *,
        plan_id: str,
        subject_id: str,
        policy_digest: str,
        plan_sha256: str,
        checks: tuple[GeneratedCheck, ...],
        dimensions: tuple[IntelligenceDimension, ...],
    ) -> dict[str, Any]:
        return {
            "suite_format": SUITE_FORMAT,
            "plan_id": plan_id,
            "subject_id": subject_id,
            "policy_digest": policy_digest,
            "plan_sha256": plan_sha256,
            "checks": [check.core() for check in checks],
            "dimensions": [dimension.value for dimension in dimensions],
        }

    @classmethod
    def create(
        cls,
        *,
        plan: AssurancePlan,
        checks: Iterable[GeneratedCheck],
        rules: Iterable[ValidationRule],
        dimensions: Iterable[IntelligenceDimension],
        catalog_rule_ids: Iterable[str],
    ) -> GeneratedSuite:
        ordered_checks = tuple(sorted(checks, key=lambda c: (c.kind.order, c.ref, c.obligation_id)))
        ordered_rules = tuple(sorted(rules, key=lambda r: (r.domain.order, r.rule_id)))
        ordered_dimensions = tuple(sorted(set(dimensions), key=lambda d: d.order))
        core = cls._core(
            plan_id=plan.plan_id,
            subject_id=plan.subject_id,
            policy_digest=plan.policy_digest,
            plan_sha256=plan.plan_sha256,
            checks=ordered_checks,
            dimensions=ordered_dimensions,
        )
        digest = content_hash(core)
        return cls(
            suite_id=f"UCOS-VSUITE-{digest[:16]}",
            plan_id=plan.plan_id,
            subject_id=plan.subject_id,
            policy_digest=plan.policy_digest,
            plan_sha256=plan.plan_sha256,
            checks=ordered_checks,
            rules=ordered_rules,
            dimensions=ordered_dimensions,
            catalog_rule_ids=tuple(sorted(set(catalog_rule_ids))),
            suite_sha256=digest,
        )

    # -- derived, measurable properties ----------------------------------------

    @property
    def bound_checks(self) -> tuple[GeneratedCheck, ...]:
        return tuple(check for check in self.checks if check.bound)

    @property
    def unbound_checks(self) -> tuple[GeneratedCheck, ...]:
        return tuple(check for check in self.checks if not check.bound)

    def blocking_shortfalls(self) -> tuple[str, ...]:
        """The ids of blocking obligations with no bound implementation (fail-closed)."""
        return tuple(check.obligation_id for check in self.checks if check.is_blocking_shortfall)

    def advisory_shortfalls(self) -> tuple[str, ...]:
        return tuple(
            check.obligation_id
            for check in self.checks
            if not check.bound and check.policy_severity is Severity.ADVISORY
        )

    def severity_divergences(self) -> tuple[str, ...]:
        return tuple(check.obligation_id for check in self.checks if check.severity_diverges)

    @property
    def complete(self) -> bool:
        """True iff every *blocking* obligation bound to an implementation."""
        return not self.blocking_shortfalls()

    def rule_ids(self) -> tuple[str, ...]:
        return tuple(rule.rule_id for rule in self.rules)

    def domains(self) -> tuple[ValidationDomain, ...]:
        seen: dict[ValidationDomain, None] = {}
        for rule in self.rules:
            seen.setdefault(rule.domain, None)
        return tuple(sorted(seen, key=lambda d: d.order))

    def severity_for(self, ref: str) -> Severity | None:
        """The *policy* severity governing the check bound to ``ref`` (policy wins)."""
        for check in self.checks:
            if check.ref == ref:
                return check.policy_severity
        return None

    def obligations_for_ref(self, ref: str) -> tuple[str, ...]:
        return tuple(check.obligation_id for check in self.checks if check.ref == ref)

    def binding_coverage(self) -> float:
        """The bound/planned ratio (1.0 when the plan admitted nothing)."""
        if not self.checks:
            return 1.0
        return len(self.bound_checks) / len(self.checks)

    def counts(self) -> dict[str, int]:
        return {
            "checks": len(self.checks),
            "bound": len(self.bound_checks),
            "unbound": len(self.unbound_checks),
            "rules": len(self.rules),
            "domains": len(self.domains()),
            "dimensions": len(self.dimensions),
            "blocking_shortfalls": len(self.blocking_shortfalls()),
            "advisory_shortfalls": len(self.advisory_shortfalls()),
            "severity_divergences": len(self.severity_divergences()),
        }

    def observations(self) -> dict[str, float]:
        """The numeric facts the policy's generation metrics are evaluated against."""
        counts = self.counts()
        return {
            "suite.checks": float(counts["checks"]),
            "suite.bound_obligations": float(counts["bound"]),
            "suite.unbound_obligations": float(counts["unbound"]),
            "suite.binding_coverage": self.binding_coverage(),
            "suite.rules": float(counts["rules"]),
            "suite.dimensions": float(counts["dimensions"]),
            "suite.severity_divergences": float(counts["severity_divergences"]),
        }

    def to_dict(self) -> dict[str, Any]:
        return {
            "suite_format": SUITE_FORMAT,
            "suite_id": self.suite_id,
            "plan_id": self.plan_id,
            "subject_id": self.subject_id,
            "policy_digest": self.policy_digest,
            "plan_sha256": self.plan_sha256,
            "complete": self.complete,
            "counts": self.counts(),
            "binding_coverage": self.binding_coverage(),
            "rule_ids": list(self.rule_ids()),
            "domains": [domain.value for domain in self.domains()],
            "dimensions": [dimension.value for dimension in self.dimensions],
            "blocking_shortfalls": list(self.blocking_shortfalls()),
            "advisory_shortfalls": list(self.advisory_shortfalls()),
            "severity_divergences": list(self.severity_divergences()),
            "checks": [check.to_dict() for check in self.checks],
            "catalog_rule_ids": list(self.catalog_rule_ids),
            "observations": self.observations(),
            "suite_sha256": self.suite_sha256,
        }


class SuiteGenerator:
    """**Validation Generation** — binds a plan to the reused implementations."""

    __slots__ = ("_catalog",)

    def __init__(self, catalog: RuleCatalog | None = None) -> None:
        self._catalog = catalog if catalog is not None else RuleCatalog()

    @property
    def catalog(self) -> RuleCatalog:
        return self._catalog

    def generate(self, plan: AssurancePlan) -> GeneratedSuite:
        """Generate the executable suite for ``plan`` (never raises on an unbound ref)."""
        if not isinstance(plan, AssurancePlan):
            raise AssuranceGenerationError("validation generation requires an AssurancePlan")
        checks: list[GeneratedCheck] = []
        rules: dict[str, ValidationRule] = {}
        dimensions: list[IntelligenceDimension] = []
        for item in plan.planned:
            check = self._bind(item, rules, dimensions)
            if check is not None:
                checks.append(check)
        return GeneratedSuite.create(
            plan=plan,
            checks=checks,
            rules=rules.values(),
            dimensions=dimensions,
            catalog_rule_ids=self._catalog.rule_ids,
        )

    def _bind(
        self,
        item: PlannedObligation,
        rules: dict[str, ValidationRule],
        dimensions: list[IntelligenceDimension],
    ) -> GeneratedCheck | None:
        obligation = item.obligation
        if obligation.kind is ObligationKind.VALIDATION_RULE:
            return self._bind_rule(item, rules)
        if obligation.kind is ObligationKind.INTELLIGENCE_DIMENSION:
            return self._bind_dimension(item, dimensions)
        # Certification obligations are bound by the certification executor, not here.
        return None

    def _bind_rule(
        self, item: PlannedObligation, rules: dict[str, ValidationRule]
    ) -> GeneratedCheck:
        obligation = item.obligation
        if not item.satisfiable:
            return GeneratedCheck(
                obligation_id=obligation.id,
                kind=obligation.kind,
                ref=obligation.ref,
                policy_severity=obligation.severity,
                bound=False,
                unbound_reason=UNBOUND_UNSATISFIABLE,
            )
        rule = self._catalog.rule(obligation.ref)
        if rule is None:
            return GeneratedCheck(
                obligation_id=obligation.id,
                kind=obligation.kind,
                ref=obligation.ref,
                policy_severity=obligation.severity,
                bound=False,
                unbound_reason=UNBOUND_UNKNOWN_RULE,
            )
        rules[rule.rule_id] = rule
        return GeneratedCheck(
            obligation_id=obligation.id,
            kind=obligation.kind,
            ref=obligation.ref,
            policy_severity=obligation.severity,
            bound=True,
            implementation=f"{type(rule).__module__}.{type(rule).__name__}",
            domain=rule.domain.value,
            implementation_severity=rule.severity.value,
        )

    def _bind_dimension(
        self, item: PlannedObligation, dimensions: list[IntelligenceDimension]
    ) -> GeneratedCheck:
        obligation = item.obligation
        if not item.satisfiable:
            return GeneratedCheck(
                obligation_id=obligation.id,
                kind=obligation.kind,
                ref=obligation.ref,
                policy_severity=obligation.severity,
                bound=False,
                unbound_reason=UNBOUND_UNSATISFIABLE,
            )
        dimension = self._catalog.dimension(obligation.ref)
        if dimension is None:
            return GeneratedCheck(
                obligation_id=obligation.id,
                kind=obligation.kind,
                ref=obligation.ref,
                policy_severity=obligation.severity,
                bound=False,
                unbound_reason=UNBOUND_UNKNOWN_DIMENSION,
            )
        dimensions.append(dimension)
        return GeneratedCheck(
            obligation_id=obligation.id,
            kind=obligation.kind,
            ref=obligation.ref,
            policy_severity=obligation.severity,
            bound=True,
            implementation="platform.validation_intelligence.analyzers",
            dimension=dimension.value,
        )


def obligations_by_ref(suite: GeneratedSuite) -> Mapping[str, tuple[str, ...]]:
    """Index the suite's obligation ids by the ref they bound to (deterministic)."""
    index: dict[str, list[str]] = {}
    for check in suite.checks:
        index.setdefault(check.ref, []).append(check.obligation_id)
    return {ref: tuple(sorted(ids)) for ref, ids in sorted(index.items())}


__all__ = [
    "SUITE_FORMAT",
    "UNBOUND_UNKNOWN_RULE",
    "UNBOUND_UNKNOWN_DIMENSION",
    "UNBOUND_UNSUPPORTED_KIND",
    "UNBOUND_UNSATISFIABLE",
    "RuleCatalog",
    "GeneratedCheck",
    "GeneratedSuite",
    "SuiteGenerator",
    "obligations_by_ref",
]
