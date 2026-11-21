"""EPIC-VAL-003 — Repository Governance Pipeline end-to-end tests.

Proves the mission end to end: the pipeline **reuses** the Validation, Certification,
and Acceptance engines and generates every unified artifact — governance evidence,
repository decision, certificate, acceptance, readiness, and the freeze
recommendation — deterministically and fail-closed.
"""

from __future__ import annotations

import pytest

from engine.governance.contracts import GovernanceInput, GovernanceStatus
from engine.governance.errors import GovernanceRejectedError
from engine.governance.freeze import DO_NOT_FREEZE, FREEZE
from engine.governance.pipeline import (
    RepositoryGovernancePipeline,
    enforce_governance,
    govern_repository,
)

from .conftest import replace_facts


def test_full_pipeline_governs_a_valid_repository(governed_report):
    """A fully governable repository flows to GOVERNED + FREEZE with intact evidence."""
    report = governed_report
    assert report.status is GovernanceStatus.GOVERNED
    assert report.governed is True

    # Every stage passed and every unit was validated + certified (reused engines).
    assert report.repository_decision.validation_passed is True
    assert report.repository_decision.certification_passed is True
    assert report.repository_decision.acceptance_passed is True
    assert all(u.validated and u.certified for u in report.units)

    # Unified artifacts are all present and self-consistent.
    assert report.repository_acceptance.accepted is True
    assert report.repository_certificate.accepted is True
    assert report.repository_readiness.ready is True
    assert report.freeze_recommendation.recommendation == FREEZE
    assert report.freeze_recommendation.rationale == ()

    # The report is a tamper-evident commitment over every subordinate artifact.
    assert report.verify_integrity() is True
    report.require_integrity()


def test_ledger_records_every_certification(governed_report):
    """Certification is recorded in the append-only, hash-chained ledger."""
    ledger = governed_report.ledger
    assert len(ledger) == len(governed_report.units)
    assert ledger.verify() is True
    assert governed_report.governance_evidence.ledger_head == ledger.head_hash


def test_governance_evidence_closes_the_chain(governed_report):
    """The unified evidence references each unit's validation + certification evidence."""
    evidence = governed_report.governance_evidence
    assert len(evidence.validation_evidence_refs) == len(governed_report.units)
    assert len(evidence.certification_evidence_refs) == len(governed_report.units)
    assert evidence.acceptance_evidence_ref
    assert evidence.counts["validated"] == len(governed_report.units)
    assert evidence.verify_integrity() is True


def test_pipeline_is_deterministic(valid_input):
    """An identical input yields a byte-identical governance report (IMP-007 §5)."""
    a = RepositoryGovernancePipeline().govern(valid_input)
    b = RepositoryGovernancePipeline().govern(valid_input)
    assert a.governance_sha256 == b.governance_sha256
    assert a.to_dict() == b.to_dict()


def test_govern_repository_convenience(valid_input):
    report = govern_repository(valid_input)
    assert report.governed is True


def test_pipeline_fails_closed_on_repository_blocker(governance_units, repository_facts):
    """A repository-level freeze blocker rejects acceptance → NOT-GOVERNED + DO-NOT-FREEZE."""
    facts = replace_facts(repository_facts, freeze_blockers=["open-pr"])
    gi = GovernanceInput(
        repository_id="UCOS-REPO-0003",
        epic_id="EPIC-VAL-003",
        units=governance_units,
        repository_facts=facts,
    )
    report = RepositoryGovernancePipeline().govern(gi)
    assert report.status is GovernanceStatus.NOT_GOVERNED
    assert report.repository_decision.acceptance_passed is False
    assert "acceptance:freeze-readiness" in report.repository_decision.blocking_reasons
    assert report.freeze_recommendation.recommendation == DO_NOT_FREEZE
    assert report.freeze_recommendation.rationale != ()
    assert report.verify_integrity() is True


def test_pipeline_fails_closed_on_coverage_gap(governance_units, repository_facts):
    """Sub-100% coverage rejects acceptance (the 100% coverage invariant, fail-closed)."""
    facts = replace_facts(
        repository_facts,
        coverage=[{"name": "statements", "covered": 90, "total": 100}],
    )
    gi = GovernanceInput(
        repository_id="UCOS-REPO-0003",
        epic_id="EPIC-VAL-003",
        units=governance_units,
        repository_facts=facts,
    )
    report = RepositoryGovernancePipeline().govern(gi)
    assert report.governed is False
    assert "acceptance:coverage-complete" in report.repository_decision.blocking_reasons


def test_enforce_governance_strict_passes_when_governed(governed_report):
    assert enforce_governance(governed_report, strict=True) is governed_report


def test_enforce_governance_strict_raises_when_not_governed(governance_units, repository_facts):
    facts = replace_facts(repository_facts, freeze_blockers=["x"])
    gi = GovernanceInput(
        repository_id="UCOS-REPO-0003",
        epic_id="EPIC-VAL-003",
        units=governance_units,
        repository_facts=facts,
    )
    report = RepositoryGovernancePipeline().govern(gi)
    with pytest.raises(GovernanceRejectedError) as exc:
        enforce_governance(report, strict=True)
    assert exc.value.context["repository_id"] == "UCOS-REPO-0003"
    assert exc.value.context["freeze_recommendation"] == DO_NOT_FREEZE


def test_enforce_governance_non_strict_never_raises(governance_units, repository_facts):
    facts = replace_facts(repository_facts, freeze_blockers=["x"])
    gi = GovernanceInput(
        repository_id="UCOS-REPO-0003",
        epic_id="EPIC-VAL-003",
        units=governance_units,
        repository_facts=facts,
    )
    report = RepositoryGovernancePipeline().govern(gi)
    assert enforce_governance(report) is report


def test_pipeline_accepts_custom_suites(valid_input):
    """Custom validation checks / certification criteria / acceptance gates are honored."""
    from engine.acceptance.gates import default_gates
    from engine.certification.criteria import default_criteria
    from engine.validation.checks import default_checks

    pipeline = RepositoryGovernancePipeline(
        checks=default_checks(),
        criteria=default_criteria(),
        gates=default_gates(),
    )
    report = pipeline.govern(valid_input)
    assert report.governed is True
