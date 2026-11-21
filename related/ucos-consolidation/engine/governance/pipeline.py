"""EPIC-VAL-003 — Repository Governance Pipeline (Terminal T3).

The :class:`RepositoryGovernancePipeline` is the canonical end-to-end constitutional
governance flow. It **reuses** the already-built engines — it creates no new
validation, certification, or acceptance logic — and sequences them into one
deterministic, fail-closed determination:

    Validation (EPIC-007) → Certification (EPIC-008) → Acceptance (EPIC-VAL-002)
        → Repository Readiness → Architecture Freeze

For every unit it runs the real :class:`~engine.validation.executor.ValidationEngine`,
builds Validation Evidence, certifies that evidence through the real
:class:`~engine.certification.engine.CertificationEngine`, records the immutable
certification in the append-only :class:`~engine.certification.ledger.CertificationLedger`,
and derives the unit's ``validated`` / ``certified`` acceptance facts **from those
real runs** (never from caller assertion — soundness, TP-01). It assimilates those
derived facts with the repository-level facts, runs the real
:class:`~engine.acceptance.engine.AcceptanceEngine`, and generates the unified
repository decision, certificate, acceptance, readiness, evidence, and the
architecture-freeze recommendation — bundled into one
:class:`~engine.governance.report.RepositoryGovernanceReport`.

The flow is fully deterministic (IMP-007 §5): units execute in stable id order and no
artifact embeds wall-clock or ambient state, so an identical
:class:`~engine.governance.contracts.GovernanceInput` yields a byte-identical report.
It is fail-closed: the repository is GOVERNED iff every stage passed, and
:func:`enforce_governance` turns a not-governed report into a hard, auditable gate.
"""

from __future__ import annotations

from collections.abc import Iterable
from typing import Any

from engine.acceptance.contracts import RepositorySubject
from engine.acceptance.engine import AcceptanceEngine
from engine.acceptance.evidence import build_acceptance_evidence
from engine.acceptance.gates import AcceptanceGate
from engine.acceptance.readiness import build_repository_readiness
from engine.certification.criteria import CertificationCriterion
from engine.certification.engine import certify_validation
from engine.certification.evidence import build_certification_evidence
from engine.certification.ledger import CertificationLedger
from engine.foundation.obs.logging import get_logger
from engine.foundation.obs.telemetry import trace
from engine.governance.contracts import (
    ACCEPTANCE_STAGE,
    CERTIFICATION_STAGE,
    VALIDATION_STAGE,
    GovernanceInput,
    RepositoryDecision,
    StageOutcome,
)
from engine.governance.errors import GovernanceRejectedError
from engine.governance.evidence import build_governance_evidence
from engine.governance.freeze import build_freeze_recommendation
from engine.governance.report import GovernedUnit, RepositoryGovernanceReport
from engine.runtime.disclosure import build_disclosure
from engine.validation.checks import ValidationCheck
from engine.validation.evidence import build_validation_evidence
from engine.validation.executor import ValidationEngine

_logger = get_logger("governance.pipeline")


class RepositoryGovernancePipeline:
    """Sequences Validation → Certification → Acceptance into one governance flow.

    The pipeline holds only the (deterministic, stateless) engines; it retains no
    per-run state, so a single instance may govern any number of repositories.
    Custom validation checks, certification criteria, or acceptance gates may be
    supplied to specialize the suite without re-implementing the engines.
    """

    __slots__ = ("_validation", "_criteria", "_acceptance")

    def __init__(
        self,
        *,
        checks: Iterable[ValidationCheck] | None = None,
        criteria: Iterable[CertificationCriterion] | None = None,
        gates: Iterable[AcceptanceGate] | None = None,
    ) -> None:
        self._validation = ValidationEngine(checks)
        # Criteria are materialized once so certify_validation reuses a stable suite.
        self._criteria = tuple(criteria) if criteria is not None else None
        self._acceptance = AcceptanceEngine(gates)

    def govern(self, governance_input: GovernanceInput) -> RepositoryGovernanceReport:
        """Run the full governance flow and emit the unified governance report."""
        with trace("governance.govern", repository=governance_input.repository_id):
            ledger = CertificationLedger()
            governed_units = self._govern_units(governance_input, ledger)

            subject = self._assimilate(governance_input, governed_units)
            acceptance = self._acceptance.accept(subject)
            acceptance_evidence = build_acceptance_evidence(acceptance)
            readiness = build_repository_readiness(acceptance)

            decision = self._decide(governance_input, governed_units, acceptance)

            governance_evidence = build_governance_evidence(
                repository_id=governance_input.repository_id,
                epic_id=governance_input.epic_id,
                units=governed_units,
                acceptance_evidence=acceptance_evidence,
                ledger=ledger,
            )
            freeze_recommendation = build_freeze_recommendation(decision, readiness)

            report = RepositoryGovernanceReport.assemble(
                units=governed_units,
                ledger=ledger,
                decision=decision,
                acceptance=acceptance,
                readiness=readiness,
                governance_evidence=governance_evidence,
                freeze_recommendation=freeze_recommendation,
            )
        _logger.info(
            "governance.decided",
            repository=governance_input.repository_id,
            epic=governance_input.epic_id,
            status=report.status.value,
            freeze=freeze_recommendation.recommendation,
            units=len(governed_units),
        )
        return report

    # -- stages ---------------------------------------------------------------

    def _govern_units(
        self, governance_input: GovernanceInput, ledger: CertificationLedger
    ) -> tuple[GovernedUnit, ...]:
        """Validate then certify every unit in stable id order (deterministic)."""
        governed: list[GovernedUnit] = []
        for unit in governance_input.ordered_units():
            report = self._validation.validate(unit.subject)
            validation_evidence = build_validation_evidence(report)
            certification = certify_validation(
                report,
                validation_evidence,
                version=unit.version,
                certification_class=unit.certification_class,
                criteria=self._criteria,
            )
            certification_evidence = build_certification_evidence(certification)
            ledger_entry = ledger.append(certification.record)
            governed.append(
                GovernedUnit(
                    unit_id=unit.unit_id,
                    validation_report=report,
                    validation_evidence=validation_evidence,
                    certification_decision=certification,
                    certification_evidence=certification_evidence,
                    ledger_entry=ledger_entry,
                )
            )
        return tuple(governed)

    def _assimilate(
        self,
        governance_input: GovernanceInput,
        governed_units: tuple[GovernedUnit, ...],
    ) -> RepositorySubject:
        """Merge the derived per-unit facts with the repository-level facts.

        The per-unit ``validated`` / ``certified`` facts are taken from the real
        engine runs; ownership, registration, and traceability come from the unit's
        declared acceptance metadata. The repository-level facts (dependencies,
        reuse, inventory, coverage, integrations, architecture, health, freeze
        blockers) pass through unchanged.
        """
        by_id = {u.unit_id: u for u in governed_units}
        unit_facts: list[dict[str, Any]] = []
        for unit in governance_input.ordered_units():
            governed = by_id[unit.unit_id]
            unit_facts.append(
                {
                    "unit_id": unit.unit_id,
                    "owner": unit.owner,
                    "implemented": True,
                    "validated": governed.validated,
                    "certified": governed.certified,
                    "registered": unit.registered,
                    "traceability": list(unit.traceability),
                }
            )
        facts: dict[str, Any] = dict(governance_input.repository_facts)
        facts["repository_id"] = governance_input.repository_id
        facts["epic_id"] = governance_input.epic_id
        facts["units"] = unit_facts
        return RepositorySubject.from_mapping(facts)

    def _decide(
        self,
        governance_input: GovernanceInput,
        governed_units: tuple[GovernedUnit, ...],
        acceptance: Any,
    ) -> RepositoryDecision:
        """Aggregate the three stage outcomes into the unified repository decision."""
        total = len(governed_units)
        validation = StageOutcome.of(
            VALIDATION_STAGE,
            total=total,
            failures=tuple(u.unit_id for u in governed_units if not u.validated),
        )
        certification = StageOutcome.of(
            CERTIFICATION_STAGE,
            total=total,
            failures=tuple(u.unit_id for u in governed_units if not u.certified),
        )
        accept_stage = StageOutcome.of(
            ACCEPTANCE_STAGE,
            total=len(acceptance.findings),
            failures=tuple(acceptance.blocking_failures),
        )
        return RepositoryDecision.create(
            repository_id=governance_input.repository_id,
            epic_id=governance_input.epic_id,
            validation=validation,
            certification=certification,
            acceptance=accept_stage,
            disclosure=build_disclosure(),
        )


def govern_repository(
    governance_input: GovernanceInput,
    *,
    checks: Iterable[ValidationCheck] | None = None,
    criteria: Iterable[CertificationCriterion] | None = None,
    gates: Iterable[AcceptanceGate] | None = None,
) -> RepositoryGovernanceReport:
    """Convenience: govern a repository with the default (or supplied) suites."""
    pipeline = RepositoryGovernancePipeline(checks=checks, criteria=criteria, gates=gates)
    return pipeline.govern(governance_input)


def enforce_governance(
    report: RepositoryGovernanceReport, *, strict: bool = False
) -> RepositoryGovernanceReport:
    """Return ``report``; in strict mode raise when the repository is not governed.

    Raises:
        GovernanceRejectedError: when ``strict`` and the repository is not governed —
            carrying the unified decision's blocking reasons and the freeze
            recommendation as evidence (every refusal is auditable, fail-closed).
    """
    if strict and not report.governed:
        raise GovernanceRejectedError(
            "governance pipeline refused a not-governed repository",
            repository_id=report.repository_id,
            epic_id=report.epic_id,
            blocking_reasons=list(report.repository_decision.blocking_reasons),
            freeze_recommendation=report.freeze_recommendation.recommendation,
        )
    return report


__all__ = [
    "RepositoryGovernancePipeline",
    "govern_repository",
    "enforce_governance",
]
