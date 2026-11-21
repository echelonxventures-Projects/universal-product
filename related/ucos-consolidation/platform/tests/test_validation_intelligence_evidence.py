"""UCOS-EPIC-013 — Validation Intelligence evidence tests (Terminal T5).

Mandatory Rule 6: every determination yields evidence. The record must be
self-contained (a downstream gate reads one artifact), deterministic (no wall-clock
leaks into the identity), and honest (it restates the report's verdict rather than
inventing one).
"""

from __future__ import annotations

from platform.tests._validation_intelligence_helpers import passing_target, target_with
from platform.validation_intelligence.contracts import INTELLIGENCE_AUTHORITY
from platform.validation_intelligence.engine import ContinuousValidationIntelligenceEngine
from platform.validation_intelligence.evidence import (
    EVIDENCE_FORMAT,
    ValidationIntelligenceEvidence,
    build_validation_intelligence_evidence,
)


def _evidence(target=None) -> ValidationIntelligenceEvidence:
    report = ContinuousValidationIntelligenceEngine().analyze(target or passing_target())
    return build_validation_intelligence_evidence(report)


def test_the_evidence_format_is_declared():
    assert EVIDENCE_FORMAT == "ucos-validation-intelligence-evidence/1.0.0"
    assert _evidence().to_dict()["evidence_format"] == EVIDENCE_FORMAT


def test_evidence_restates_a_passing_run():
    evidence = _evidence()
    assert evidence.verdict == "pass"
    assert evidence.passed is True
    assert evidence.compatible is True
    assert evidence.compliant is True
    assert evidence.blocking_failures == ()


def test_evidence_restates_a_failing_run_and_names_the_blocking_check():
    evidence = _evidence(target_with("repository_completeness", gaps=2))
    assert evidence.verdict == "fail"
    assert evidence.passed is False
    assert "repository_completeness.no-gaps" in evidence.blocking_failures


def test_evidence_binds_to_the_report_and_target_identities():
    report = ContinuousValidationIntelligenceEngine().analyze(passing_target("bound"))
    evidence = build_validation_intelligence_evidence(report)
    assert evidence.target_id == "bound"
    assert evidence.report_sha256 == report.report_sha256
    assert evidence.target_digest == report.target_digest


def test_evidence_records_every_dimension_and_check():
    report = ContinuousValidationIntelligenceEngine().analyze(passing_target())
    evidence = build_validation_intelligence_evidence(report)
    assert len(evidence.dimensions_run) == 7
    assert len(evidence.checks_run) == report.counts()["total"]
    assert len(evidence.findings) == report.counts()["total"]


def test_evidence_embeds_both_headline_projections():
    """One self-contained artifact: a consumer needs no second call."""
    evidence = _evidence()
    assert evidence.compatibility_report["report_format"]
    assert evidence.compliance_report["report_format"]
    assert evidence.compatibility_report["compatible"] is True
    assert evidence.compliance_report["compliant"] is True


def test_a_compatibility_break_is_visible_in_the_evidence():
    evidence = _evidence(target_with("contract_compatibility", candidate=[]))
    assert evidence.compatible is False
    assert evidence.compliant is True
    assert evidence.compatibility_report["breaking_changes"]


def test_a_compliance_violation_is_visible_in_the_evidence():
    evidence = _evidence(target_with("governance_compliance", authority="CONSTITUTIONAL"))
    assert evidence.compliant is False
    assert evidence.compatible is True
    assert evidence.compliance_report["violations"]


def test_evidence_carries_bounded_authority_and_the_disclosure():
    evidence = _evidence()
    assert evidence.authority == INTELLIGENCE_AUTHORITY
    assert evidence.disclosure


def test_evidence_hash_is_reproducible_for_an_identical_run():
    assert _evidence().evidence_sha256 == _evidence().evidence_sha256


def test_evidence_hash_changes_when_the_verdict_changes():
    passing = _evidence()
    failing = _evidence(target_with("repository_completeness", gaps=1))
    assert passing.evidence_sha256 != failing.evidence_sha256


def test_to_dict_carries_the_hash_and_round_trips_the_core():
    evidence = _evidence()
    payload = evidence.to_dict()
    assert payload["evidence_sha256"] == evidence.evidence_sha256
    assert payload["target_id"] == evidence.target_id
    assert payload["counts"] == evidence.counts


def test_to_dict_is_json_serializable():
    import json

    assert json.loads(json.dumps(_evidence().to_dict(), sort_keys=True))["verdict"] == "pass"
