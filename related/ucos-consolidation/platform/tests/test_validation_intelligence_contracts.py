"""UCOS-EPIC-013 — Continuous Validation Intelligence contract tests (Terminal T5).

The vocabulary the engine speaks: dimension identity and ordering, fail-closed
aggregation, and the three deterministic projections. Every assertion here is about the
*shape* of the contract, never about a particular system's facts.
"""

from __future__ import annotations

from platform.validation_intelligence.compliance import build_compliance_report
from platform.validation_intelligence.contracts import (
    COMPATIBILITY_REPORT_FORMAT,
    COMPLIANCE_REPORT_FORMAT,
    INTELLIGENCE_AUTHORITY,
    INTELLIGENCE_DASHBOARD_FORMAT,
    INTELLIGENCE_REPORT_FORMAT,
    VALIDATION_INTELLIGENCE_CONTRACT_VERSION,
    CompatibilityReport,
    ComplianceReport,
    DimensionKind,
    DimensionReport,
    Finding,
    FindingStatus,
    IntelligenceDashboard,
    IntelligenceDimension,
    IntelligenceTarget,
    Severity,
    ValidationIntelligenceReport,
    Verdict,
    dimensions_of_kind,
)
from platform.validation_intelligence.errors import IntelligenceTargetError

import pytest


def _finding(
    dimension: IntelligenceDimension,
    *,
    check_id: str = "check",
    severity: Severity = Severity.BLOCKING,
    status: FindingStatus = FindingStatus.PASS,
) -> Finding:
    return Finding(
        check_id=check_id,
        dimension=dimension,
        severity=severity,
        status=status,
        message="m",
        details={"volatile": object.__repr__},
    )


def _report(*dimension_reports: DimensionReport) -> ValidationIntelligenceReport:
    return ValidationIntelligenceReport.create(
        target_id="t", target_digest="digest", dimension_reports=tuple(dimension_reports)
    )


# --- formats and authority -------------------------------------------------------
def test_contract_surface_declares_stable_format_identifiers():
    assert VALIDATION_INTELLIGENCE_CONTRACT_VERSION == "1.0.0"
    assert INTELLIGENCE_REPORT_FORMAT == "ucos-validation-intelligence-report/1.0.0"
    assert INTELLIGENCE_DASHBOARD_FORMAT == "ucos-validation-intelligence-dashboard/1.0.0"
    assert COMPATIBILITY_REPORT_FORMAT == "ucos-validation-compatibility-report/1.0.0"
    assert COMPLIANCE_REPORT_FORMAT == "ucos-validation-compliance-report/1.0.0"


def test_authority_is_bounded_to_engineering_execution():
    """DE-05 / IP-01: a run records engineering readiness, never constitutional authority."""
    assert INTELLIGENCE_AUTHORITY == "ENGINEERING-EXECUTION-ONLY"


# --- dimensions ------------------------------------------------------------------
def test_seven_dimensions_are_declared_in_canonical_order():
    assert [d.value for d in IntelligenceDimension] == [
        "cross_capability_consistency",
        "repository_completeness",
        "contract_compatibility",
        "architecture_compliance",
        "runtime_compatibility",
        "version_compatibility",
        "governance_compliance",
    ]


def test_dimension_order_is_declaration_order():
    assert [d.order for d in IntelligenceDimension] == list(range(7))


def test_every_dimension_has_a_kind():
    assert all(isinstance(d.kind, DimensionKind) for d in IntelligenceDimension)


def test_parse_accepts_a_known_dimension():
    parsed = IntelligenceDimension.parse("governance_compliance")
    assert parsed is IntelligenceDimension.GOVERNANCE_COMPLIANCE


def test_parse_rejects_an_unknown_dimension_with_the_supported_set():
    with pytest.raises(IntelligenceTargetError) as exc:
        IntelligenceDimension.parse("not-a-dimension")
    assert exc.value.context["dimension"] == "not-a-dimension"
    assert len(exc.value.context["supported"]) == 7


def test_dimensions_of_kind_partitions_the_seven_dimensions():
    grouped = [d for kind in DimensionKind for d in dimensions_of_kind(kind)]
    assert sorted(grouped, key=lambda d: d.order) == sorted(
        IntelligenceDimension, key=lambda d: d.order
    )


def test_dimensions_of_kind_returns_canonical_order():
    compat = dimensions_of_kind(DimensionKind.COMPATIBILITY)
    assert compat == (
        IntelligenceDimension.CONTRACT_COMPATIBILITY,
        IntelligenceDimension.RUNTIME_COMPATIBILITY,
        IntelligenceDimension.VERSION_COMPATIBILITY,
    )


def test_compliance_kind_covers_architecture_and_governance():
    assert dimensions_of_kind(DimensionKind.COMPLIANCE) == (
        IntelligenceDimension.ARCHITECTURE_COMPLIANCE,
        IntelligenceDimension.GOVERNANCE_COMPLIANCE,
    )


# --- IntelligenceTarget ----------------------------------------------------------
def test_target_from_mapping_normalizes_facts():
    target = IntelligenceTarget.from_mapping(
        {"target_id": "t1", "facts": {"repository_completeness": {"gaps": 0}}}
    )
    assert target.target_id == "t1"
    assert target.facts == {"repository_completeness": {"gaps": 0}}


def test_target_from_mapping_defaults_to_empty_facts():
    assert IntelligenceTarget.from_mapping({"target_id": "t1"}).facts == {}


def test_target_from_mapping_rejects_a_non_mapping():
    with pytest.raises(IntelligenceTargetError):
        IntelligenceTarget.from_mapping(["not", "a", "mapping"])


def test_target_from_mapping_rejects_an_absent_target_id():
    with pytest.raises(IntelligenceTargetError):
        IntelligenceTarget.from_mapping({"facts": {}})


def test_target_from_mapping_rejects_a_non_string_target_id():
    with pytest.raises(IntelligenceTargetError):
        IntelligenceTarget.from_mapping({"target_id": 17})


def test_target_from_mapping_rejects_non_mapping_facts():
    with pytest.raises(IntelligenceTargetError) as exc:
        IntelligenceTarget.from_mapping({"target_id": "t1", "facts": ["nope"]})
    assert exc.value.context["target_id"] == "t1"


def test_target_from_mapping_rejects_an_unknown_dimension_key():
    with pytest.raises(IntelligenceTargetError):
        IntelligenceTarget.from_mapping({"target_id": "t1", "facts": {"bogus": {}}})


def test_target_from_mapping_rejects_non_mapping_dimension_facts():
    with pytest.raises(IntelligenceTargetError) as exc:
        IntelligenceTarget.from_mapping(
            {"target_id": "t1", "facts": {"repository_completeness": ["nope"]}}
        )
    assert exc.value.context["dimension"] == "repository_completeness"


def test_dimension_facts_returns_empty_for_an_undeclared_dimension():
    target = IntelligenceTarget(target_id="t1", facts={})
    assert target.dimension_facts(IntelligenceDimension.RUNTIME_COMPATIBILITY) == {}


def test_target_to_dict_sorts_facts_for_determinism():
    target = IntelligenceTarget(
        target_id="t1", facts={"version_compatibility": {}, "architecture_compliance": {}}
    )
    assert list(target.to_dict()["facts"]) == ["architecture_compliance", "version_compatibility"]


def test_target_digest_is_insensitive_to_fact_insertion_order():
    first = IntelligenceTarget(target_id="t", facts={"repository_completeness": {}, "graph": {}})
    second = IntelligenceTarget(target_id="t", facts={"graph": {}, "repository_completeness": {}})
    assert first.digest() == second.digest()


def test_target_digest_changes_with_the_facts():
    a = IntelligenceTarget(target_id="t", facts={"repository_completeness": {"gaps": 0}})
    b = IntelligenceTarget(target_id="t", facts={"repository_completeness": {"gaps": 1}})
    assert a.digest() != b.digest()


# --- Finding ---------------------------------------------------------------------
def test_finding_status_predicates_are_exclusive():
    passed = _finding(IntelligenceDimension.REPOSITORY_COMPLETENESS)
    failed = _finding(IntelligenceDimension.REPOSITORY_COMPLETENESS, status=FindingStatus.FAIL)
    assert passed.passed and not passed.failed
    assert failed.failed and not failed.passed


def test_only_a_failing_blocking_finding_is_a_blocking_failure():
    blocking_pass = _finding(IntelligenceDimension.REPOSITORY_COMPLETENESS)
    blocking_fail = _finding(
        IntelligenceDimension.REPOSITORY_COMPLETENESS, status=FindingStatus.FAIL
    )
    advisory_fail = _finding(
        IntelligenceDimension.REPOSITORY_COMPLETENESS,
        status=FindingStatus.FAIL,
        severity=Severity.ADVISORY,
    )
    assert not blocking_pass.is_blocking_failure
    assert blocking_fail.is_blocking_failure
    assert not blocking_fail.is_advisory_failure
    assert advisory_fail.is_advisory_failure
    assert not advisory_fail.is_blocking_failure


def test_finding_core_excludes_volatile_details():
    """The hashable core must not carry per-run detail, or determinism is lost."""
    core = _finding(IntelligenceDimension.REPOSITORY_COMPLETENESS).core()
    assert "details" not in core
    assert set(core) == {"check_id", "dimension", "severity", "status", "message"}


def test_finding_to_dict_carries_details():
    finding = Finding(
        check_id="c",
        dimension=IntelligenceDimension.REPOSITORY_COMPLETENESS,
        severity=Severity.BLOCKING,
        status=FindingStatus.PASS,
        details={"k": "v"},
    )
    assert finding.to_dict()["details"] == {"k": "v"}


# --- DimensionReport -------------------------------------------------------------
def test_dimension_report_passes_when_no_blocking_check_failed():
    report = DimensionReport.create(
        IntelligenceDimension.REPOSITORY_COMPLETENESS,
        (_finding(IntelligenceDimension.REPOSITORY_COMPLETENESS),),
    )
    assert report.verdict is Verdict.PASS
    assert report.passed


def test_dimension_report_fails_on_a_blocking_failure():
    report = DimensionReport.create(
        IntelligenceDimension.REPOSITORY_COMPLETENESS,
        (_finding(IntelligenceDimension.REPOSITORY_COMPLETENESS, status=FindingStatus.FAIL),),
    )
    assert report.verdict is Verdict.FAIL


def test_an_advisory_failure_never_fails_the_dimension_verdict():
    """The mission mandate: advisory failures are evidence, not a verdict."""
    report = DimensionReport.create(
        IntelligenceDimension.REPOSITORY_COMPLETENESS,
        (
            _finding(
                IntelligenceDimension.REPOSITORY_COMPLETENESS,
                status=FindingStatus.FAIL,
                severity=Severity.ADVISORY,
            ),
        ),
    )
    assert report.verdict is Verdict.PASS
    assert report.advisory_failures() == ("check",)
    assert report.blocking_failures() == ()


def test_dimension_report_counts_are_consistent():
    dimension = IntelligenceDimension.REPOSITORY_COMPLETENESS
    report = DimensionReport.create(
        dimension,
        (
            _finding(dimension, check_id="a"),
            _finding(dimension, check_id="b", status=FindingStatus.FAIL),
            _finding(
                dimension, check_id="c", status=FindingStatus.FAIL, severity=Severity.ADVISORY
            ),
        ),
    )
    assert report.counts() == {
        "total": 3,
        "passed": 1,
        "failed": 2,
        "blocking_failed": 1,
        "advisory_failed": 1,
    }


def test_dimension_report_kind_follows_its_dimension():
    report = DimensionReport.create(IntelligenceDimension.VERSION_COMPATIBILITY, ())
    assert report.kind is DimensionKind.COMPATIBILITY


def test_empty_dimension_report_passes_vacuously():
    assert DimensionReport.create(IntelligenceDimension.VERSION_COMPATIBILITY, ()).passed


def test_dimension_report_to_dict_is_serializable():
    dimension = IntelligenceDimension.REPOSITORY_COMPLETENESS
    payload = DimensionReport.create(dimension, (_finding(dimension),)).to_dict()
    assert payload["dimension"] == dimension.value
    assert payload["kind"] == "completeness"
    assert payload["verdict"] == "pass"
    assert payload["passed"] is True
    assert len(payload["findings"]) == 1


# --- ValidationIntelligenceReport ------------------------------------------------
def test_report_fails_if_any_dimension_failed():
    ok = DimensionReport.create(
        IntelligenceDimension.REPOSITORY_COMPLETENESS,
        (_finding(IntelligenceDimension.REPOSITORY_COMPLETENESS),),
    )
    bad = DimensionReport.create(
        IntelligenceDimension.GOVERNANCE_COMPLIANCE,
        (_finding(IntelligenceDimension.GOVERNANCE_COMPLIANCE, status=FindingStatus.FAIL),),
    )
    assert _report(ok, bad).verdict is Verdict.FAIL
    assert _report(ok).verdict is Verdict.PASS


def test_report_asserts_bounded_authority_and_carries_disclosure():
    report = _report(DimensionReport.create(IntelligenceDimension.REPOSITORY_COMPLETENESS, ()))
    assert report.authority == INTELLIGENCE_AUTHORITY
    assert report.disclosure


def test_report_hash_is_stable_across_identical_constructions():
    def build() -> ValidationIntelligenceReport:
        dimension = IntelligenceDimension.REPOSITORY_COMPLETENESS
        return _report(DimensionReport.create(dimension, (_finding(dimension),)))

    assert build().report_sha256 == build().report_sha256


def test_report_hash_ignores_volatile_finding_details():
    """Two runs differing only in per-finding detail must reproduce one identity."""
    dimension = IntelligenceDimension.REPOSITORY_COMPLETENESS
    base = dict(
        check_id="c", dimension=dimension, severity=Severity.BLOCKING, status=FindingStatus.PASS
    )
    first = _report(DimensionReport.create(dimension, (Finding(**base, details={"t": 1}),)))
    second = _report(DimensionReport.create(dimension, (Finding(**base, details={"t": 2}),)))
    assert first.report_sha256 == second.report_sha256


def test_report_hash_changes_with_a_verdict():
    dimension = IntelligenceDimension.REPOSITORY_COMPLETENESS
    passing = _report(DimensionReport.create(dimension, (_finding(dimension),)))
    failing = _report(
        DimensionReport.create(dimension, (_finding(dimension, status=FindingStatus.FAIL),))
    )
    assert passing.report_sha256 != failing.report_sha256


def test_report_aggregates_findings_and_counts_across_dimensions():
    a = IntelligenceDimension.REPOSITORY_COMPLETENESS
    b = IntelligenceDimension.GOVERNANCE_COMPLIANCE
    report = _report(
        DimensionReport.create(a, (_finding(a, check_id="a1"),)),
        DimensionReport.create(b, (_finding(b, check_id="b1", status=FindingStatus.FAIL),)),
    )
    assert report.dimensions_run() == (a.value, b.value)
    assert [f.check_id for f in report.all_findings] == ["a1", "b1"]
    assert report.counts() == {
        "dimensions": 2,
        "total": 2,
        "passed": 1,
        "failed": 1,
        "blocking_failed": 1,
        "advisory_failed": 0,
    }
    assert report.blocking_failures() == ("b1",)
    assert report.dimension_verdicts() == {a.value: "pass", b.value: "fail"}


def test_reports_of_kind_selects_only_that_kind():
    compat = IntelligenceDimension.VERSION_COMPATIBILITY
    compliance = IntelligenceDimension.GOVERNANCE_COMPLIANCE
    report = _report(DimensionReport.create(compat, ()), DimensionReport.create(compliance, ()))
    assert report.reports_of_kind(DimensionKind.COMPATIBILITY)[0].dimension is compat
    assert report.reports_of_kind(DimensionKind.COMPLIANCE)[0].dimension is compliance
    assert report.reports_of_kind(DimensionKind.CONSISTENCY) == ()


def test_report_to_dict_is_serializable_and_self_describing():
    dimension = IntelligenceDimension.REPOSITORY_COMPLETENESS
    payload = _report(DimensionReport.create(dimension, (_finding(dimension),))).to_dict()
    assert payload["report_format"] == INTELLIGENCE_REPORT_FORMAT
    assert payload["authority"] == INTELLIGENCE_AUTHORITY
    assert payload["passed"] is True
    assert payload["report_sha256"]


# --- projections -----------------------------------------------------------------
def test_dashboard_projects_the_report_counts():
    a = IntelligenceDimension.REPOSITORY_COMPLETENESS
    report = _report(
        DimensionReport.create(
            a, (_finding(a, check_id="a1"), _finding(a, check_id="a2", status=FindingStatus.FAIL))
        )
    )
    dashboard = report.dashboard()
    assert isinstance(dashboard, IntelligenceDashboard)
    assert dashboard.verdict is Verdict.FAIL
    assert (dashboard.checks_total, dashboard.checks_passed, dashboard.checks_failed) == (2, 1, 1)
    assert dashboard.blocking_failures == ("a2",)
    assert dashboard.to_dict()["dashboard_format"] == INTELLIGENCE_DASHBOARD_FORMAT


def test_compatibility_report_is_compatible_only_when_every_compat_dimension_passed():
    contract = IntelligenceDimension.CONTRACT_COMPATIBILITY
    passing = _report(DimensionReport.create(contract, (_finding(contract),)))
    failing = _report(
        DimensionReport.create(contract, (_finding(contract, status=FindingStatus.FAIL),))
    )
    assert passing.compatibility_report().compatible is True
    assert failing.compatibility_report().compatible is False
    assert failing.compatibility_report().breaking_changes[0]["check_id"] == "check"


def test_compatibility_report_ignores_compliance_dimensions():
    """A governance failure is not a compatibility break."""
    governance = IntelligenceDimension.GOVERNANCE_COMPLIANCE
    report = _report(
        DimensionReport.create(governance, (_finding(governance, status=FindingStatus.FAIL),))
    )
    compat = report.compatibility_report()
    assert isinstance(compat, CompatibilityReport)
    assert compat.compatible is True
    assert compat.breaking_changes == ()


def test_compliance_report_is_compliant_only_when_every_compliance_dimension_passed():
    governance = IntelligenceDimension.GOVERNANCE_COMPLIANCE
    passing = _report(DimensionReport.create(governance, (_finding(governance),)))
    failing = _report(
        DimensionReport.create(governance, (_finding(governance, status=FindingStatus.FAIL),))
    )
    assert passing.compliance_report().compliant is True
    assert failing.compliance_report().compliant is False
    assert failing.compliance_report().violations[0]["check_id"] == "check"


def test_compliance_report_ignores_compatibility_dimensions():
    contract = IntelligenceDimension.CONTRACT_COMPATIBILITY
    report = _report(
        DimensionReport.create(contract, (_finding(contract, status=FindingStatus.FAIL),))
    )
    compliance = report.compliance_report()
    assert isinstance(compliance, ComplianceReport)
    assert compliance.compliant is True
    assert compliance.violations == ()


def test_projection_to_dicts_are_self_describing():
    dimension = IntelligenceDimension.CONTRACT_COMPATIBILITY
    report = _report(DimensionReport.create(dimension, (_finding(dimension),)))
    assert report.compatibility_report().to_dict()["report_format"] == COMPATIBILITY_REPORT_FORMAT
    assert report.compliance_report().to_dict()["report_format"] == COMPLIANCE_REPORT_FORMAT


def test_the_compliance_deliverable_function_matches_the_projection():
    """The named EPIC-013 deliverable is the projection, not a second opinion (TP-01)."""
    dimension = IntelligenceDimension.GOVERNANCE_COMPLIANCE
    report = _report(
        DimensionReport.create(dimension, (_finding(dimension, status=FindingStatus.FAIL),))
    )
    built = build_compliance_report(report)
    assert built.compliant is False
    assert built.report_sha256 == ComplianceReport.from_report(report).report_sha256


def test_projection_hashes_are_deterministic():
    dimension = IntelligenceDimension.CONTRACT_COMPATIBILITY
    report = _report(DimensionReport.create(dimension, (_finding(dimension),)))
    assert report.compatibility_report().report_sha256 == (
        CompatibilityReport.from_report(report).report_sha256
    )
    assert report.compliance_report().report_sha256 == (
        ComplianceReport.from_report(report).report_sha256
    )
    assert report.dashboard().dashboard_sha256 == (
        IntelligenceDashboard.from_report(report).dashboard_sha256
    )
