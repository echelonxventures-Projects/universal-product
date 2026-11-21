"""UCOS-EPIC-005 — Universal Validation contract tests (Terminal T5)."""

from __future__ import annotations

from platform.universal_validation.contracts import (
    VALIDATION_AUTHORITY,
    DomainReport,
    EngineVerdict,
    RuleResult,
    RuleSeverity,
    RuleStatus,
    ValidationDomain,
    ValidationReport,
    ValidationTarget,
)
from platform.universal_validation.errors import ValidationTargetError

import pytest


def _result(rule_id, domain, severity, status):
    return RuleResult(rule_id=rule_id, domain=domain, severity=severity, status=status)


def test_domain_order_matches_mission_sequence():
    assert [d.value for d in ValidationDomain] == [
        "architecture",
        "implementation",
        "dependency",
        "registry",
        "schema",
        "runtime",
        "quality",
    ]
    assert ValidationDomain.ARCHITECTURE.order == 0
    assert ValidationDomain.QUALITY.order == 6


def test_domain_parse_rejects_unknown():
    with pytest.raises(ValidationTargetError):
        ValidationDomain.parse("nope")
    assert ValidationDomain.parse("runtime") is ValidationDomain.RUNTIME


def test_target_from_mapping_normalizes_and_digests():
    target = ValidationTarget.from_mapping(
        {"target_id": "T", "facts": {"quality": {"line_percent": 91.0}}}
    )
    assert target.target_id == "T"
    assert target.domain_facts(ValidationDomain.QUALITY) == {"line_percent": 91.0}
    assert target.domain_facts(ValidationDomain.RUNTIME) == {}
    # deterministic digest
    assert target.digest() == ValidationTarget.from_mapping(target.to_dict()).digest()


@pytest.mark.parametrize(
    "raw",
    [
        [],  # not a mapping
        {"facts": {}},  # missing target_id
        {"target_id": ""},  # empty target_id
        {"target_id": "T", "facts": []},  # facts not a mapping
        {"target_id": "T", "facts": {"quality": []}},  # domain facts not a mapping
        {"target_id": "T", "facts": {"bogus": {}}},  # unknown domain
    ],
)
def test_target_from_mapping_rejects_malformed(raw):
    with pytest.raises(ValidationTargetError):
        ValidationTarget.from_mapping(raw)


def test_rule_result_properties():
    blocking_fail = _result("r", ValidationDomain.QUALITY, RuleSeverity.BLOCKING, RuleStatus.FAIL)
    advisory_fail = _result("r", ValidationDomain.QUALITY, RuleSeverity.ADVISORY, RuleStatus.FAIL)
    passing = _result("r", ValidationDomain.QUALITY, RuleSeverity.BLOCKING, RuleStatus.PASS)
    assert blocking_fail.is_blocking_failure and not blocking_fail.is_advisory_failure
    assert advisory_fail.is_advisory_failure and not advisory_fail.is_blocking_failure
    assert passing.passed and not passing.failed
    assert "details" in blocking_fail.to_dict()
    assert "details" not in blocking_fail.core()


def test_domain_report_verdict_and_counts():
    results = (
        _result("a", ValidationDomain.QUALITY, RuleSeverity.BLOCKING, RuleStatus.PASS),
        _result("b", ValidationDomain.QUALITY, RuleSeverity.ADVISORY, RuleStatus.FAIL),
    )
    report = DomainReport.create(ValidationDomain.QUALITY, results)
    assert report.verdict is EngineVerdict.PASS  # only advisory failed
    assert report.counts() == {
        "total": 2,
        "passed": 1,
        "failed": 1,
        "blocking_failed": 0,
        "advisory_failed": 1,
    }
    assert report.advisory_failures() == ("b",)

    blocking = (_result("c", ValidationDomain.QUALITY, RuleSeverity.BLOCKING, RuleStatus.FAIL),)
    assert DomainReport.create(ValidationDomain.QUALITY, blocking).verdict is EngineVerdict.FAIL


def test_validation_report_aggregation_and_disclosure():
    dr_pass = DomainReport.create(
        ValidationDomain.ARCHITECTURE,
        (_result("x", ValidationDomain.ARCHITECTURE, RuleSeverity.BLOCKING, RuleStatus.PASS),),
    )
    dr_fail = DomainReport.create(
        ValidationDomain.QUALITY,
        (_result("y", ValidationDomain.QUALITY, RuleSeverity.BLOCKING, RuleStatus.FAIL),),
    )
    report = ValidationReport.create(
        target_id="T", target_digest="d", domain_reports=(dr_pass, dr_fail)
    )
    assert report.verdict is EngineVerdict.FAIL
    assert report.blocking_failures() == ("y",)
    assert report.domain_verdicts() == {"architecture": "pass", "quality": "fail"}
    assert report.authority == VALIDATION_AUTHORITY
    assert report.disclosure["asserts_constitutional_finality"] is False
    assert len(report.report_sha256) == 64
    payload = report.to_dict()
    assert payload["report_format"].startswith("ucos-universal-validation-report/")
    assert payload["passed"] is False


def test_validation_report_all_pass_verdict():
    dr = DomainReport.create(
        ValidationDomain.ARCHITECTURE,
        (_result("x", ValidationDomain.ARCHITECTURE, RuleSeverity.BLOCKING, RuleStatus.PASS),),
    )
    report = ValidationReport.create(target_id="T", target_digest="d", domain_reports=(dr,))
    assert report.verdict is EngineVerdict.PASS
    assert report.passed is True


def test_dashboard_projection_is_content_addressed():
    dr = DomainReport.create(
        ValidationDomain.QUALITY,
        (_result("y", ValidationDomain.QUALITY, RuleSeverity.BLOCKING, RuleStatus.FAIL),),
    )
    report = ValidationReport.create(target_id="T", target_digest="d", domain_reports=(dr,))
    dashboard = report.dashboard()
    assert dashboard.verdict is EngineVerdict.FAIL
    assert dashboard.rules_total == 1
    assert dashboard.blocking_failures == ("y",)
    assert len(dashboard.dashboard_sha256) == 64
    assert dashboard.to_dict()["dashboard_format"].startswith(
        "ucos-universal-validation-dashboard/"
    )
