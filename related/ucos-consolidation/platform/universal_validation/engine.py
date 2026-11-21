"""UCOS-EPIC-005 — Universal Validation Engine (Terminal T5).

The :class:`UniversalValidationEngine` is the single conductor of the validation
*runtime*: it runs a suite of :class:`~platform.universal_validation.rules.ValidationRule`
objects over a normalized
:class:`~platform.universal_validation.contracts.ValidationTarget`, groups their
findings by domain, and aggregates them into a deterministic, content-addressed
:class:`~platform.universal_validation.contracts.ValidationReport` (and, from it, a
:class:`~platform.universal_validation.contracts.ValidationDashboard`).

Execution is:

    * **deterministic** — rules run in stable ``(domain-order, rule-id)`` order and the
      report embeds no wall-clock or ambient state, so an identical target validated by
      an identical suite yields a byte-identical report and content hash (IMP-007 §5);
    * **fail-closed** — a domain's verdict is FAIL iff any *blocking* rule failed, and
      the run verdict is FAIL iff any domain failed; advisory failures are recorded as
      evidence but never fail the verdict; and
    * **evidence-producing** — every rule outcome is captured in the report, and the
      report is the input to
      :func:`~platform.universal_validation.evidence.build_validation_evidence`.

The engine invents no verdict beyond aggregating its rules (TP-01) and never mutates a
target or writes to the certified corpus (DP-03).
"""

from __future__ import annotations

from collections.abc import Iterable
from platform.universal_validation.contracts import (
    DomainReport,
    ValidationDomain,
    ValidationReport,
    ValidationTarget,
)
from platform.universal_validation.errors import ValidationEngineError
from platform.universal_validation.rules import ValidationRule, default_rules

from engine.foundation.obs.logging import get_logger
from engine.foundation.obs.telemetry import trace

_logger = get_logger("universal_validation.engine")


class UniversalValidationEngine:
    """Runs a deterministic, fail-closed suite of rules over a validation target."""

    __slots__ = ("_rules",)

    def __init__(
        self,
        rules: Iterable[ValidationRule] | None = None,
        *,
        domains: Iterable[ValidationDomain] | None = None,
    ) -> None:
        selected = tuple(rules) if rules is not None else default_rules()
        if domains is not None:
            allowed = set(domains)
            if not allowed:
                raise ValidationEngineError("at least one validation domain must be selected")
            selected = tuple(r for r in selected if r.domain in allowed)
        if not selected:
            raise ValidationEngineError("the validation engine has no rules to run")
        # Stable (domain-order, rule-id) ordering guarantees deterministic findings.
        self._rules = tuple(sorted(selected, key=lambda r: (r.domain.order, r.rule_id)))

    @property
    def rule_ids(self) -> tuple[str, ...]:
        return tuple(r.rule_id for r in self._rules)

    @property
    def domains(self) -> tuple[ValidationDomain, ...]:
        """The distinct domains covered by the suite, in canonical order."""
        seen: dict[ValidationDomain, None] = {}
        for rule in self._rules:
            seen.setdefault(rule.domain, None)
        return tuple(sorted(seen, key=lambda d: d.order))

    def validate(self, target: ValidationTarget) -> ValidationReport:
        """Evaluate every rule over ``target`` and aggregate a content-addressed report."""
        if not isinstance(target, ValidationTarget):
            raise ValidationEngineError("a valid ValidationTarget is required")
        with trace("universal_validation.validate", target=target.target_id):
            grouped: dict[ValidationDomain, list] = {domain: [] for domain in self.domains}
            for rule in self._rules:
                grouped[rule.domain].append(rule.evaluate(target))
            domain_reports = tuple(
                DomainReport.create(domain, tuple(grouped[domain])) for domain in self.domains
            )
            report = ValidationReport.create(
                target_id=target.target_id,
                target_digest=target.digest(),
                domain_reports=domain_reports,
            )
        _logger.info(
            "universal_validation.completed",
            target=target.target_id,
            verdict=report.verdict.value,
            domains=len(domain_reports),
            blocking_failed=len(report.blocking_failures()),
        )
        return report


__all__ = ["UniversalValidationEngine"]
