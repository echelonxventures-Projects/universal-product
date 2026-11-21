"""UCOS-EPIC-013 — Continuous Validation Intelligence analyzer tests (Terminal T5).

Each analyzer is a pure function of one dimension's facts. These tests prove the
mission's central mandate at the unit level: **an analyzer that cannot prove its
invariant records a FAIL** — absent evidence, malformed evidence, and an empty
declaration all fail closed, and none of them raises.
"""

from __future__ import annotations

from platform.tests._validation_intelligence_helpers import passing_target, target_with
from platform.validation_intelligence.analyzers import (
    ArchitectureComplianceAnalyzer,
    ContractCompatibilityAnalyzer,
    CrossCapabilityConsistencyAnalyzer,
    DimensionAnalyzer,
    GovernanceComplianceAnalyzer,
    RepositoryCompletenessAnalyzer,
    RuntimeCompatibilityAnalyzer,
    VersionCompatibilityAnalyzer,
    default_analyzers,
)
from platform.validation_intelligence.compatibility import CompatibilityEngine
from platform.validation_intelligence.contracts import (
    Finding,
    IntelligenceDimension,
    IntelligenceTarget,
    Severity,
)

import pytest

from engine.foundation.contracts.disclosure import build_disclosure


def _by_id(findings, check_id: str) -> Finding:
    matches = [f for f in findings if f.check_id == check_id]
    assert matches, f"{check_id} not in {[f.check_id for f in findings]}"
    return matches[0]


def _failed_ids(findings) -> list[str]:
    return [f.check_id for f in findings if f.failed]


# --- the analyzer base contract --------------------------------------------------
def test_every_builtin_analyzer_declares_a_dimension_and_description():
    for analyzer in default_analyzers():
        assert isinstance(analyzer.dimension, IntelligenceDimension)
        assert analyzer.description


def test_default_suite_covers_all_seven_dimensions_in_canonical_order():
    dimensions = [a.dimension for a in default_analyzers()]
    assert dimensions == sorted(IntelligenceDimension, key=lambda d: d.order)


def test_default_suite_shares_one_compatibility_engine():
    """One engine backs the three compatibility analyzers, so the suite composes once."""
    engine = CompatibilityEngine()
    analyzers = default_analyzers(engine)
    compat = [a for a in analyzers if isinstance(a, ContractCompatibilityAnalyzer)]
    assert compat and compat[0]._engine is engine


def test_analyzer_facts_helper_reads_only_its_own_dimension():
    analyzer = RepositoryCompletenessAnalyzer()
    target = passing_target()
    assert analyzer.facts(target) == target.dimension_facts(
        IntelligenceDimension.REPOSITORY_COMPLETENESS
    )


def test_analyzer_facts_helper_returns_empty_when_the_dimension_is_absent():
    assert RepositoryCompletenessAnalyzer().facts(IntelligenceTarget(target_id="t")) == {}


def test_a_custom_analyzer_may_emit_an_advisory_finding():
    """The severity default is blocking; advisory is available to custom analyzers."""

    class _Advisory(DimensionAnalyzer):
        dimension = IntelligenceDimension.REPOSITORY_COMPLETENESS

        def analyze(self, target):
            return (self._fail("custom.advisory", "noted", severity=Severity.ADVISORY),)

    finding = _Advisory().analyze(passing_target())[0]
    assert finding.is_advisory_failure
    assert not finding.is_blocking_failure


def test_the_analyzer_base_class_cannot_be_instantiated():
    with pytest.raises(TypeError):
        DimensionAnalyzer()


# --- cross-capability consistency ------------------------------------------------
@pytest.mark.parametrize("capabilities", [None, [], "not-a-list", {"id": "a"}])
def test_absent_or_malformed_capabilities_fail_closed(capabilities):
    findings = CrossCapabilityConsistencyAnalyzer().analyze(
        target_with("cross_capability_consistency", capabilities=capabilities)
    )
    assert _by_id(findings, "cross_capability.capabilities-declared").is_blocking_failure


@pytest.mark.parametrize("capability", ["nope", {"provides": []}, {"id": ""}])
def test_a_malformed_capability_declaration_fails_closed(capability):
    findings = CrossCapabilityConsistencyAnalyzer().analyze(
        target_with("cross_capability_consistency", capabilities=[capability])
    )
    assert _by_id(findings, "cross_capability.capabilities-declared").is_blocking_failure


def test_malformed_provides_or_requires_fails_closed():
    findings = CrossCapabilityConsistencyAnalyzer().analyze(
        target_with(
            "cross_capability_consistency",
            capabilities=[{"id": "a", "provides": "not-a-list", "requires": []}],
        )
    )
    finding = _by_id(findings, "cross_capability.capabilities-declared")
    assert finding.is_blocking_failure
    assert finding.details["capability"] == "a"


def test_consistent_capabilities_pass_every_check():
    findings = CrossCapabilityConsistencyAnalyzer().analyze(passing_target())
    assert _failed_ids(findings) == []
    assert len(findings) == 4


def test_duplicate_capability_ids_fail():
    findings = CrossCapabilityConsistencyAnalyzer().analyze(
        target_with(
            "cross_capability_consistency",
            capabilities=[
                {"id": "dup", "provides": ["x"], "requires": []},
                {"id": "dup", "provides": ["y"], "requires": []},
            ],
        )
    )
    finding = _by_id(findings, "cross_capability.ids-unique")
    assert finding.is_blocking_failure
    assert finding.details["duplicates"] == ["dup"]


def test_conflicting_providers_for_one_contract_fail():
    findings = CrossCapabilityConsistencyAnalyzer().analyze(
        target_with(
            "cross_capability_consistency",
            capabilities=[
                {"id": "a", "provides": ["shared"], "requires": []},
                {"id": "b", "provides": ["shared"], "requires": []},
            ],
        )
    )
    finding = _by_id(findings, "cross_capability.providers-unique")
    assert finding.is_blocking_failure
    assert finding.details["conflicts"] == {"shared": ["a", "b"]}


def test_a_required_contract_with_no_provider_fails():
    findings = CrossCapabilityConsistencyAnalyzer().analyze(
        target_with(
            "cross_capability_consistency",
            capabilities=[{"id": "a", "provides": [], "requires": ["ghost"]}],
        )
    )
    finding = _by_id(findings, "cross_capability.requirements-satisfied")
    assert finding.is_blocking_failure
    assert finding.details["dangling"] == ["ghost"]


# --- repository completeness -----------------------------------------------------
def test_a_complete_repository_passes_every_check():
    assert _failed_ids(RepositoryCompletenessAnalyzer().analyze(passing_target())) == []


@pytest.mark.parametrize("artifacts", [None, [], "not-a-list"])
def test_absent_required_artifacts_fail_closed(artifacts):
    findings = RepositoryCompletenessAnalyzer().analyze(
        target_with("repository_completeness", required_artifacts=artifacts)
    )
    assert _by_id(findings, "repository_completeness.artifacts-present").is_blocking_failure


@pytest.mark.parametrize("artifact", ["nope", {"present": True}])
def test_a_malformed_artifact_declaration_fails_closed(artifact):
    findings = RepositoryCompletenessAnalyzer().analyze(
        target_with("repository_completeness", required_artifacts=[artifact])
    )
    assert _by_id(findings, "repository_completeness.artifacts-present").is_blocking_failure


def test_a_missing_artifact_fails():
    findings = RepositoryCompletenessAnalyzer().analyze(
        target_with(
            "repository_completeness",
            required_artifacts=[{"id": "a", "present": True}, {"id": "b", "present": False}],
        )
    )
    finding = _by_id(findings, "repository_completeness.artifacts-present")
    assert finding.is_blocking_failure
    assert finding.details["missing"] == ["b"]


def test_an_artifact_defaults_to_absent_when_presence_is_undeclared():
    """Absence of evidence is not evidence of presence."""
    findings = RepositoryCompletenessAnalyzer().analyze(
        target_with("repository_completeness", required_artifacts=[{"id": "a"}])
    )
    assert _by_id(findings, "repository_completeness.artifacts-present").is_blocking_failure


@pytest.mark.parametrize("gaps", [None, "0", -1, True, 1.0])
def test_an_absent_or_malformed_gap_count_fails_closed(gaps):
    findings = RepositoryCompletenessAnalyzer().analyze(
        target_with("repository_completeness", gaps=gaps)
    )
    assert _by_id(findings, "repository_completeness.no-gaps").is_blocking_failure


def test_open_gaps_fail():
    findings = RepositoryCompletenessAnalyzer().analyze(
        target_with("repository_completeness", gaps=3)
    )
    finding = _by_id(findings, "repository_completeness.no-gaps")
    assert finding.is_blocking_failure
    assert finding.details["gaps"] == 3


@pytest.mark.parametrize("coverage", [None, "full", []])
def test_absent_or_malformed_coverage_fails_closed(coverage):
    findings = RepositoryCompletenessAnalyzer().analyze(
        target_with("repository_completeness", coverage=coverage)
    )
    assert _by_id(findings, "repository_completeness.coverage-complete").is_blocking_failure


@pytest.mark.parametrize(
    "coverage",
    [
        {"covered": "5", "total": 10},
        {"covered": 5, "total": "10"},
        {"covered": -1, "total": 10},
        {"covered": 5, "total": 0},
        {"covered": 5, "total": -1},
        {"covered": True, "total": 10},
        {"covered": 5, "total": True},
        {},
    ],
)
def test_malformed_coverage_counts_fail_closed(coverage):
    findings = RepositoryCompletenessAnalyzer().analyze(
        target_with("repository_completeness", coverage=coverage)
    )
    assert _by_id(findings, "repository_completeness.coverage-complete").is_blocking_failure


def test_incomplete_coverage_fails():
    findings = RepositoryCompletenessAnalyzer().analyze(
        target_with("repository_completeness", coverage={"covered": 9, "total": 10})
    )
    finding = _by_id(findings, "repository_completeness.coverage-complete")
    assert finding.is_blocking_failure
    assert finding.details == {"covered": 9, "total": 10}


# --- architecture compliance -----------------------------------------------------
def test_a_compliant_architecture_passes_every_check():
    assert _failed_ids(ArchitectureComplianceAnalyzer().analyze(passing_target())) == []


@pytest.mark.parametrize("policies", [None, [], "not-a-list"])
def test_absent_architecture_policies_fail_closed(policies):
    findings = ArchitectureComplianceAnalyzer().analyze(
        target_with("architecture_compliance", policies=policies)
    )
    assert _by_id(findings, "architecture_compliance.policies-declared").is_blocking_failure


@pytest.mark.parametrize("policy", ["nope", {"compliant": True}])
def test_a_malformed_architecture_policy_fails_closed(policy):
    findings = ArchitectureComplianceAnalyzer().analyze(
        target_with("architecture_compliance", policies=[policy])
    )
    assert _by_id(findings, "architecture_compliance.policies-declared").is_blocking_failure


def test_an_unmet_architecture_policy_fails():
    findings = ArchitectureComplianceAnalyzer().analyze(
        target_with("architecture_compliance", policies=[{"id": "p1", "compliant": False}])
    )
    finding = _by_id(findings, "architecture_compliance.policies-satisfied")
    assert finding.is_blocking_failure
    assert finding.details["unmet"] == ["p1"]


@pytest.mark.parametrize("changed", [None, "not-a-list"])
def test_absent_changed_paths_fail_closed(changed):
    findings = ArchitectureComplianceAnalyzer().analyze(
        target_with("architecture_compliance", changed_paths=changed)
    )
    assert _by_id(findings, "architecture_compliance.no-frozen-writes").is_blocking_failure


@pytest.mark.parametrize("path", ["00-BOOK/DATA/artifacts.json", "00-SOURCE/x", "99-FREEZE/y"])
def test_a_write_to_the_frozen_corpus_fails(path):
    """DP-03: the certified corpus is read-only; a write to it is a compliance violation."""
    findings = ArchitectureComplianceAnalyzer().analyze(
        target_with("architecture_compliance", changed_paths=[path])
    )
    finding = _by_id(findings, "architecture_compliance.no-frozen-writes")
    assert finding.is_blocking_failure
    assert finding.details["violations"] == [path]


def test_an_empty_change_set_writes_to_nothing_frozen():
    findings = ArchitectureComplianceAnalyzer().analyze(
        target_with("architecture_compliance", changed_paths=[])
    )
    finding = _by_id(findings, "architecture_compliance.no-frozen-writes")
    assert finding.passed
    assert finding.details["checked"] == 0


# --- governance compliance -------------------------------------------------------
def test_a_governed_target_passes_every_check():
    assert _failed_ids(GovernanceComplianceAnalyzer().analyze(passing_target())) == []


@pytest.mark.parametrize("controls", [None, [], "not-a-list"])
def test_absent_governance_controls_fail_closed(controls):
    findings = GovernanceComplianceAnalyzer().analyze(
        target_with("governance_compliance", controls=controls)
    )
    assert _by_id(findings, "governance_compliance.controls-declared").is_blocking_failure


@pytest.mark.parametrize("control", ["nope", {"satisfied": True}])
def test_a_malformed_governance_control_fails_closed(control):
    findings = GovernanceComplianceAnalyzer().analyze(
        target_with("governance_compliance", controls=[control])
    )
    assert _by_id(findings, "governance_compliance.controls-declared").is_blocking_failure


def test_an_unmet_governance_control_fails():
    findings = GovernanceComplianceAnalyzer().analyze(
        target_with("governance_compliance", controls=[{"id": "g1", "satisfied": False}])
    )
    finding = _by_id(findings, "governance_compliance.controls-satisfied")
    assert finding.is_blocking_failure
    assert finding.details["unmet"] == ["g1"]


@pytest.mark.parametrize(
    "authority", [None, "", "CONSTITUTIONAL", "engineering-execution-only", "ENGINEERING"]
)
def test_authority_beyond_engineering_execution_fails(authority):
    """IP-01: the engine may never assert authority it does not hold."""
    findings = GovernanceComplianceAnalyzer().analyze(
        target_with("governance_compliance", authority=authority)
    )
    finding = _by_id(findings, "governance_compliance.authority-bounded")
    assert finding.is_blocking_failure
    assert finding.details["expected"] == "ENGINEERING-EXECUTION-ONLY"


@pytest.mark.parametrize("disclosure", [None, {}, "present", {"disclosure_id": "wrong"}])
def test_an_absent_or_malformed_disclosure_fails_closed(disclosure):
    findings = GovernanceComplianceAnalyzer().analyze(
        target_with("governance_compliance", disclosure=disclosure)
    )
    assert _by_id(findings, "governance_compliance.disclosure-present").is_blocking_failure


def test_the_ec1_disclosure_is_accepted_and_echoed():
    disclosure = build_disclosure()
    findings = GovernanceComplianceAnalyzer().analyze(
        target_with("governance_compliance", disclosure=disclosure)
    )
    finding = _by_id(findings, "governance_compliance.disclosure-present")
    assert finding.passed
    assert finding.details["disclosure_id"] == disclosure["disclosure_id"]


# --- the delegating compatibility analyzers --------------------------------------
def test_contract_analyzer_delegates_to_the_compatibility_engine():
    findings = ContractCompatibilityAnalyzer().analyze(
        target_with("contract_compatibility", candidate=[])
    )
    assert findings[0].check_id == "contract_compatibility.c1"
    assert findings[0].is_blocking_failure


def test_runtime_analyzer_delegates_to_the_compatibility_engine():
    findings = RuntimeCompatibilityAnalyzer().analyze(
        target_with("runtime_compatibility", provided={"interfaces": [], "abi": "1.0.0"})
    )
    assert _by_id(findings, "runtime_compatibility.interfaces").is_blocking_failure


def test_version_analyzer_delegates_to_the_compatibility_engine():
    findings = VersionCompatibilityAnalyzer().analyze(
        target_with("version_compatibility", components=None)
    )
    assert findings[0].check_id == "version_compatibility.evidence"


@pytest.mark.parametrize(
    "analyzer_cls",
    [ContractCompatibilityAnalyzer, RuntimeCompatibilityAnalyzer, VersionCompatibilityAnalyzer],
)
def test_a_compatibility_analyzer_accepts_an_injected_engine(analyzer_cls):
    engine = CompatibilityEngine()
    assert analyzer_cls(engine)._engine is engine


@pytest.mark.parametrize(
    "analyzer_cls",
    [ContractCompatibilityAnalyzer, RuntimeCompatibilityAnalyzer, VersionCompatibilityAnalyzer],
)
def test_a_compatibility_analyzer_composes_its_own_engine_by_default(analyzer_cls):
    assert isinstance(analyzer_cls()._engine, CompatibilityEngine)


# --- the mandate, stated once over the whole suite -------------------------------
def test_no_builtin_analyzer_raises_on_a_target_with_no_facts():
    """Fail-closed means a FAIL finding, never an exception."""
    empty = IntelligenceTarget(target_id="empty")
    for analyzer in default_analyzers():
        findings = analyzer.analyze(empty)
        assert findings, analyzer.dimension
        assert any(f.is_blocking_failure for f in findings), analyzer.dimension
