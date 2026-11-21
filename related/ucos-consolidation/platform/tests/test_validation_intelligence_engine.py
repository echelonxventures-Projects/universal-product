"""UCOS-EPIC-013 — Continuous Validation Intelligence engine tests (Terminal T5).

The engine is the conductor: it composes a suite, runs it in a stable order, and
aggregates fail-closed. A malformed *engine composition* is an authoring fault and must
raise; a failing *target* is data and must never raise.
"""

from __future__ import annotations

from platform.tests._validation_intelligence_helpers import passing_target, target_with
from platform.validation_intelligence.analyzers import (
    DimensionAnalyzer,
    RepositoryCompletenessAnalyzer,
    default_analyzers,
)
from platform.validation_intelligence.contracts import (
    Finding,
    FindingStatus,
    IntelligenceDimension,
    IntelligenceTarget,
    Severity,
    Verdict,
)
from platform.validation_intelligence.engine import ContinuousValidationIntelligenceEngine
from platform.validation_intelligence.errors import IntelligenceEngineError

import pytest


class _Stub(DimensionAnalyzer):
    """An analyzer that emits one identifiable finding for a chosen dimension."""

    def __init__(
        self,
        dimension: IntelligenceDimension,
        check_id: str,
        status: FindingStatus = FindingStatus.PASS,
        severity: Severity = Severity.BLOCKING,
    ) -> None:
        self.dimension = dimension
        self._check_id = check_id
        self._status = status
        self._severity = severity

    def analyze(self, target: IntelligenceTarget) -> tuple[Finding, ...]:
        return (
            Finding(
                check_id=self._check_id,
                dimension=self.dimension,
                severity=self._severity,
                status=self._status,
                message=target.target_id,
            ),
        )


_COMPLETENESS = IntelligenceDimension.REPOSITORY_COMPLETENESS
_GOVERNANCE = IntelligenceDimension.GOVERNANCE_COMPLIANCE


# --- composition -----------------------------------------------------------------
def test_the_default_engine_runs_the_full_seven_dimension_suite():
    assert ContinuousValidationIntelligenceEngine().dimensions == tuple(
        sorted(IntelligenceDimension, key=lambda d: d.order)
    )


def test_an_explicit_analyzer_suite_is_used_verbatim():
    engine = ContinuousValidationIntelligenceEngine([_Stub(_COMPLETENESS, "only")])
    assert engine.dimensions == (_COMPLETENESS,)


def test_a_dimension_subset_scopes_the_builtin_suite():
    engine = ContinuousValidationIntelligenceEngine(dimensions=[_GOVERNANCE, _COMPLETENESS])
    assert engine.dimensions == (_COMPLETENESS, _GOVERNANCE)


def test_an_empty_dimension_selection_is_an_authoring_fault():
    with pytest.raises(IntelligenceEngineError) as exc:
        ContinuousValidationIntelligenceEngine(dimensions=[])
    assert "at least one" in str(exc.value)


def test_an_empty_analyzer_suite_is_an_authoring_fault():
    with pytest.raises(IntelligenceEngineError) as exc:
        ContinuousValidationIntelligenceEngine([])
    assert "no analyzers" in str(exc.value)


def test_a_selection_that_matches_no_analyzer_is_an_authoring_fault():
    """Filtering a suite down to nothing must fail loudly, not run an empty gate."""
    with pytest.raises(IntelligenceEngineError) as exc:
        ContinuousValidationIntelligenceEngine(
            [_Stub(_COMPLETENESS, "only")], dimensions=[_GOVERNANCE]
        )
    assert "no analyzers" in str(exc.value)


def test_the_dimensions_property_deduplicates_and_orders():
    engine = ContinuousValidationIntelligenceEngine(
        [
            _Stub(_GOVERNANCE, "g1"),
            _Stub(_COMPLETENESS, "c1"),
            _Stub(_GOVERNANCE, "g2"),
        ]
    )
    assert engine.dimensions == (_COMPLETENESS, _GOVERNANCE)


def test_analyzers_are_ordered_canonically_regardless_of_input_order():
    forward = ContinuousValidationIntelligenceEngine(
        [_Stub(_COMPLETENESS, "c"), _Stub(_GOVERNANCE, "g")]
    ).analyze(passing_target())
    reverse = ContinuousValidationIntelligenceEngine(
        [_Stub(_GOVERNANCE, "g"), _Stub(_COMPLETENESS, "c")]
    ).analyze(passing_target())
    assert forward.dimensions_run() == reverse.dimensions_run()
    assert forward.report_sha256 == reverse.report_sha256


# --- analysis --------------------------------------------------------------------
def test_analyze_requires_a_real_intelligence_target():
    engine = ContinuousValidationIntelligenceEngine([_Stub(_COMPLETENESS, "c")])
    with pytest.raises(IntelligenceEngineError):
        engine.analyze({"target_id": "not-a-target"})


def test_analyze_binds_the_report_to_the_target_identity():
    target = passing_target("t-identity")
    report = ContinuousValidationIntelligenceEngine().analyze(target)
    assert report.target_id == "t-identity"
    assert report.target_digest == target.digest()


def test_findings_are_grouped_under_their_own_dimension():
    engine = ContinuousValidationIntelligenceEngine(
        [_Stub(_COMPLETENESS, "c1"), _Stub(_GOVERNANCE, "g1"), _Stub(_COMPLETENESS, "c2")]
    )
    report = engine.analyze(passing_target())
    by_dimension = {r.dimension: [f.check_id for f in r.findings] for r in report.dimension_reports}
    assert by_dimension == {_COMPLETENESS: ["c1", "c2"], _GOVERNANCE: ["g1"]}


def test_a_dimension_with_no_findings_still_reports():
    class _Silent(DimensionAnalyzer):
        dimension = _COMPLETENESS

        def analyze(self, target):
            return ()

    report = ContinuousValidationIntelligenceEngine([_Silent()]).analyze(passing_target())
    assert report.dimensions_run() == (_COMPLETENESS.value,)
    assert report.verdict is Verdict.PASS


def test_the_run_verdict_fails_if_any_blocking_check_failed():
    engine = ContinuousValidationIntelligenceEngine(
        [_Stub(_COMPLETENESS, "ok"), _Stub(_GOVERNANCE, "bad", status=FindingStatus.FAIL)]
    )
    report = engine.analyze(passing_target())
    assert report.verdict is Verdict.FAIL
    assert report.blocking_failures() == ("bad",)


def test_an_advisory_failure_is_recorded_but_never_fails_the_run():
    engine = ContinuousValidationIntelligenceEngine(
        [_Stub(_COMPLETENESS, "note", status=FindingStatus.FAIL, severity=Severity.ADVISORY)]
    )
    report = engine.analyze(passing_target())
    assert report.verdict is Verdict.PASS
    assert report.advisory_failures() == ("note",)


def test_the_builtin_suite_passes_the_canonical_all_pass_target():
    report = ContinuousValidationIntelligenceEngine().analyze(passing_target())
    assert report.verdict is Verdict.PASS
    assert report.counts()["failed"] == 0
    assert len(report.dimension_reports) == 7


def test_one_bad_dimension_fails_the_run_and_names_itself():
    report = ContinuousValidationIntelligenceEngine().analyze(
        target_with("repository_completeness", gaps=4)
    )
    assert report.verdict is Verdict.FAIL
    assert report.dimension_verdicts()["repository_completeness"] == "fail"
    assert report.dimension_verdicts()["governance_compliance"] == "pass"


def test_a_scoped_engine_reports_only_its_selected_dimensions():
    engine = ContinuousValidationIntelligenceEngine(dimensions=[_COMPLETENESS])
    report = engine.analyze(target_with("governance_compliance", authority="CONSTITUTIONAL"))
    assert report.dimensions_run() == (_COMPLETENESS.value,)
    assert report.verdict is Verdict.PASS


def test_the_engine_never_mutates_the_target():
    """DP-03/TP-01: the engine records, it does not rewrite what it was given."""
    target = passing_target()
    before = target.digest()
    ContinuousValidationIntelligenceEngine().analyze(target)
    assert target.digest() == before


def test_the_builtin_suite_never_raises_on_an_empty_target():
    report = ContinuousValidationIntelligenceEngine().analyze(IntelligenceTarget(target_id="bare"))
    assert report.verdict is Verdict.FAIL
    assert len(report.dimension_reports) == 7


def test_a_real_analyzer_composes_with_the_engine():
    engine = ContinuousValidationIntelligenceEngine([RepositoryCompletenessAnalyzer()])
    assert engine.analyze(passing_target()).verdict is Verdict.PASS


def test_default_analyzers_and_the_default_engine_agree():
    explicit = ContinuousValidationIntelligenceEngine(default_analyzers())
    implicit = ContinuousValidationIntelligenceEngine()
    target = passing_target()
    assert explicit.analyze(target).report_sha256 == implicit.analyze(target).report_sha256
