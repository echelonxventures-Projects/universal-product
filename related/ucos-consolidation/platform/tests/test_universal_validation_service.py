"""UCOS-EPIC-005 — Universal Validation service tests (Terminal T5)."""

from __future__ import annotations

from platform.tests.universal_validation_helpers import passing_target
from platform.universal_validation.config import parse_config
from platform.universal_validation.contracts import EngineVerdict, ValidationDomain
from platform.universal_validation.evidence import ValidationEvidence
from platform.universal_validation.service import (
    UniversalValidationService,
    build_universal_validation_service,
)


def test_service_validate_dashboard_evidence():
    service = build_universal_validation_service()
    target = passing_target()
    report = service.validate(target)
    assert report.verdict is EngineVerdict.PASS
    dashboard = service.dashboard(target)
    assert dashboard.verdict is EngineVerdict.PASS
    assert dashboard.dashboard_sha256 == report.dashboard().dashboard_sha256
    evidence = service.evidence(target)
    assert isinstance(evidence, ValidationEvidence)
    assert evidence.report_sha256 == report.report_sha256


def test_service_honours_config_domain_subset():
    config = parse_config({"target_id": "T", "domains": ["runtime"], "facts": {}})
    service = build_universal_validation_service(config)
    assert service.engine.domains == (ValidationDomain.RUNTIME,)


def test_build_with_explicit_rules():
    from platform.universal_validation.rules import CoverageThresholdRule

    service = build_universal_validation_service(rules=[CoverageThresholdRule()])
    assert service.engine.rule_ids == ("quality.coverage-threshold",)


def test_service_exposes_engine():
    service = build_universal_validation_service()
    assert isinstance(service, UniversalValidationService)
    assert service.engine is service.engine
