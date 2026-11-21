"""UCOS-EPIC-013 — Continuous Validation Intelligence service tests (Terminal T5).

The service is the single composition point. These tests prove that composition honours
the configuration's dimension scope, that every facade operation is a projection of one
analysis (never a second, differently-composed run), and that the facade invents no
verdict of its own (TP-01).
"""

from __future__ import annotations

from platform.tests._validation_intelligence_helpers import (
    passing_config_mapping,
    passing_target,
    target_with,
)
from platform.validation_intelligence.analyzers import RepositoryCompletenessAnalyzer
from platform.validation_intelligence.config import parse_config
from platform.validation_intelligence.contracts import (
    CompatibilityReport,
    ComplianceReport,
    IntelligenceDashboard,
    IntelligenceDimension,
    ValidationIntelligenceReport,
    Verdict,
)
from platform.validation_intelligence.engine import ContinuousValidationIntelligenceEngine
from platform.validation_intelligence.errors import IntelligenceEngineError
from platform.validation_intelligence.evidence import ValidationIntelligenceEvidence
from platform.validation_intelligence.service import (
    ContinuousValidationIntelligenceService,
    build_validation_intelligence_service,
)

import pytest


# --- composition -----------------------------------------------------------------
def test_the_default_composition_runs_the_full_suite():
    service = build_validation_intelligence_service()
    assert len(service.engine.dimensions) == 7


def test_a_config_without_dimensions_composes_the_full_suite():
    service = build_validation_intelligence_service(parse_config(passing_config_mapping()))
    assert len(service.engine.dimensions) == 7


def test_a_config_dimension_subset_scopes_the_engine():
    config = parse_config(
        {"target_id": "t", "dimensions": ["repository_completeness", "governance_compliance"]}
    )
    service = build_validation_intelligence_service(config)
    assert service.engine.dimensions == (
        IntelligenceDimension.REPOSITORY_COMPLETENESS,
        IntelligenceDimension.GOVERNANCE_COMPLIANCE,
    )


def test_an_explicit_analyzer_suite_is_used_verbatim():
    service = build_validation_intelligence_service(analyzers=[RepositoryCompletenessAnalyzer()])
    assert service.engine.dimensions == (IntelligenceDimension.REPOSITORY_COMPLETENESS,)


def test_a_config_scope_and_an_explicit_suite_intersect():
    config = parse_config({"target_id": "t", "dimensions": ["repository_completeness"]})
    service = build_validation_intelligence_service(
        config, analyzers=[RepositoryCompletenessAnalyzer()]
    )
    assert service.engine.dimensions == (IntelligenceDimension.REPOSITORY_COMPLETENESS,)


def test_a_scope_that_excludes_every_analyzer_is_an_authoring_fault():
    config = parse_config({"target_id": "t", "dimensions": ["governance_compliance"]})
    with pytest.raises(IntelligenceEngineError):
        build_validation_intelligence_service(config, analyzers=[RepositoryCompletenessAnalyzer()])


def test_the_engine_is_exposed_for_inspection():
    engine = ContinuousValidationIntelligenceEngine()
    service = ContinuousValidationIntelligenceService(engine)
    assert service.engine is engine


# --- facade operations -----------------------------------------------------------
def test_analyze_returns_the_intelligence_report():
    report = build_validation_intelligence_service().analyze(passing_target())
    assert isinstance(report, ValidationIntelligenceReport)
    assert report.verdict is Verdict.PASS


def test_dashboard_projects_the_same_run():
    service = build_validation_intelligence_service()
    target = passing_target()
    dashboard = service.dashboard(target)
    assert isinstance(dashboard, IntelligenceDashboard)
    assert dashboard.dashboard_sha256 == service.analyze(target).dashboard().dashboard_sha256


def test_compatibility_projects_the_same_run():
    service = build_validation_intelligence_service()
    target = passing_target()
    report = service.compatibility(target)
    assert isinstance(report, CompatibilityReport)
    assert report.report_sha256 == service.analyze(target).compatibility_report().report_sha256


def test_compliance_projects_the_same_run():
    service = build_validation_intelligence_service()
    target = passing_target()
    report = service.compliance(target)
    assert isinstance(report, ComplianceReport)
    assert report.report_sha256 == service.analyze(target).compliance_report().report_sha256


def test_evidence_projects_the_same_run():
    service = build_validation_intelligence_service()
    target = passing_target()
    evidence = service.evidence(target)
    assert isinstance(evidence, ValidationIntelligenceEvidence)
    assert evidence.report_sha256 == service.analyze(target).report_sha256


# --- the facade records, it does not decide --------------------------------------
def test_the_facade_reports_a_failing_target_without_raising():
    """A failing target is data (TP-01), never an exception."""
    service = build_validation_intelligence_service()
    report = service.analyze(target_with("governance_compliance", controls=[]))
    assert report.verdict is Verdict.FAIL
    assert report.dimension_verdicts()["governance_compliance"] == "fail"


def test_every_projection_agrees_with_the_report_on_a_failing_run():
    service = build_validation_intelligence_service()
    target = target_with("runtime_compatibility", provided={"interfaces": [], "abi": "9.0.0"})
    report = service.analyze(target)
    assert report.verdict is Verdict.FAIL
    assert service.compatibility(target).compatible is False
    assert service.compliance(target).compliant is True
    assert service.dashboard(target).verdict is Verdict.FAIL
    assert service.evidence(target).passed is False


def test_a_scoped_service_ignores_dimensions_it_was_not_asked_to_run():
    config = parse_config({"target_id": "t", "dimensions": ["repository_completeness"]})
    service = build_validation_intelligence_service(config)
    report = service.analyze(target_with("governance_compliance", authority="CONSTITUTIONAL"))
    assert report.dimensions_run() == ("repository_completeness",)
    assert report.verdict is Verdict.PASS


def test_repeated_calls_are_stable():
    service = build_validation_intelligence_service()
    target = passing_target()
    assert service.analyze(target).report_sha256 == service.analyze(target).report_sha256
