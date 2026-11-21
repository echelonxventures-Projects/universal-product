"""EPIC-PLAT-003 — Repository Operations contract tests (Terminal T5)."""

from __future__ import annotations

from platform.repository_operations.contracts import (
    CoverageSummary,
    ExecutionReport,
    OperationsConfig,
    OperationsVerdict,
    RepositoryDashboard,
    StageKind,
    StageOutcome,
    StageResult,
    StageSpec,
)
from platform.repository_operations.errors import (
    OperationsConfigError,
    StageDefinitionError,
)

import pytest


def _command_spec(stage_id: str = "s1", *, blocking: bool = True) -> StageSpec:
    return StageSpec.from_mapping(
        {
            "stage_id": stage_id,
            "kind": "command",
            "params": {"command": "verify"},
            "blocking": blocking,
        }
    )


def test_stage_kind_parse_valid_and_invalid():
    assert StageKind.parse("acceptance") is StageKind.ACCEPTANCE
    with pytest.raises(StageDefinitionError):
        StageKind.parse("nope")


def test_stage_spec_from_mapping_valid_and_to_dict():
    spec = StageSpec.from_mapping({"stage_id": "s1", "kind": "freeze"})
    assert spec.kind is StageKind.FREEZE
    assert spec.blocking is True
    assert spec.to_dict() == {"stage_id": "s1", "kind": "freeze", "params": {}, "blocking": True}


def test_stage_spec_rejects_non_mapping_missing_id_and_bad_params():
    with pytest.raises(StageDefinitionError):
        StageSpec.from_mapping([1, 2, 3])  # type: ignore[arg-type]
    with pytest.raises(StageDefinitionError):
        StageSpec.from_mapping({"kind": "freeze"})
    with pytest.raises(StageDefinitionError):
        StageSpec.from_mapping({"stage_id": "s", "kind": "freeze", "params": [1]})


def test_operations_config_from_mapping_and_digest():
    config = OperationsConfig.from_mapping(
        {
            "repository_id": "R",
            "epic_id": "E",
            "stages": [{"stage_id": "s1", "kind": "freeze", "params": {"paths": []}}],
        }
    )
    assert config.repository_id == "R"
    assert len(config.stages) == 1
    assert config.digest() == config.digest()
    assert config.to_dict()["stages"][0]["stage_id"] == "s1"


def test_operations_config_rejects_malformed_inputs():
    with pytest.raises(OperationsConfigError):
        OperationsConfig.from_mapping("not-a-mapping")  # type: ignore[arg-type]
    with pytest.raises(OperationsConfigError):
        OperationsConfig.from_mapping({"repository_id": "R", "stages": []})
    with pytest.raises(OperationsConfigError):
        OperationsConfig.from_mapping({"repository_id": "R", "epic_id": "E", "stages": "x"})
    with pytest.raises(OperationsConfigError):
        OperationsConfig.from_mapping({"repository_id": "R", "epic_id": "E", "stages": []})


def test_operations_config_rejects_duplicate_stage_ids():
    with pytest.raises(OperationsConfigError):
        OperationsConfig.from_mapping(
            {
                "repository_id": "R",
                "epic_id": "E",
                "stages": [
                    {"stage_id": "dup", "kind": "freeze"},
                    {"stage_id": "dup", "kind": "freeze"},
                ],
            }
        )


def test_stage_result_properties_core_and_to_dict():
    spec = _command_spec()
    passed = StageResult.create(spec, StageOutcome.PASSED, "ok", evidence_ref="e", detail={"a": 1})
    assert passed.passed and not passed.failed and not passed.skipped
    assert not passed.is_blocking_failure
    assert passed.core()["evidence_ref"] == "e"
    assert passed.to_dict()["detail"] == {"a": 1}

    failed = StageResult.create(spec, StageOutcome.FAILED, "bad")
    assert failed.failed and failed.is_blocking_failure

    advisory = StageResult.create(_command_spec(blocking=False), StageOutcome.FAILED, "bad")
    assert advisory.failed and not advisory.is_blocking_failure

    skipped = StageResult.create(spec, StageOutcome.SKIPPED, "reused")
    assert skipped.skipped


def test_coverage_summary_percentages_and_meets():
    summary = CoverageSummary(
        line_rate=0.9234,
        branch_rate=0.5,
        lines_covered=92,
        lines_valid=100,
        branches_covered=1,
        branches_valid=2,
    )
    assert summary.line_percent == 92.34
    assert summary.branch_percent == 50.0
    assert summary.meets(90.0)
    assert not summary.meets(95.0)
    assert summary.to_dict()["lines_covered"] == 92


def _result(stage_id, outcome, *, blocking=True):
    spec = StageSpec.from_mapping({"stage_id": stage_id, "kind": "freeze", "blocking": blocking})
    return StageResult.create(spec, outcome, "s")


def test_execution_report_pass_and_fail_verdict():
    coverage = CoverageSummary(1.0, 1.0, 10, 10, 4, 4)
    ok = ExecutionReport.create(
        repository_id="R",
        epic_id="E",
        config_digest="d",
        stage_results=(_result("a", StageOutcome.PASSED),),
        coverage=coverage,
    )
    assert ok.verdict is OperationsVerdict.PASS
    assert ok.passed
    assert ok.counts()["passed"] == 1
    assert ok.to_dict()["coverage"]["line_percent"] == 100.0

    failing = ExecutionReport.create(
        repository_id="R",
        epic_id="E",
        config_digest="d",
        stage_results=(
            _result("a", StageOutcome.FAILED),
            _result("b", StageOutcome.FAILED, blocking=False),
            _result("c", StageOutcome.SKIPPED),
        ),
        resumed=True,
    )
    assert failing.verdict is OperationsVerdict.FAIL
    assert failing.blocking_failures() == ("a",)
    assert failing.counts() == {
        "total": 3,
        "passed": 0,
        "failed": 2,
        "skipped": 1,
        "blocking_failed": 1,
    }
    assert failing.to_dict()["coverage"] is None
    assert failing.resumed is True


def test_execution_report_dashboard_projection_with_and_without_coverage():
    coverage = CoverageSummary(1.0, 1.0, 10, 10, 4, 4)
    report = ExecutionReport.create(
        repository_id="R",
        epic_id="E",
        config_digest="d",
        stage_results=(_result("a", StageOutcome.PASSED), _result("b", StageOutcome.FAILED)),
        coverage=coverage,
    )
    dash = report.dashboard()
    assert isinstance(dash, RepositoryDashboard)
    assert dash.coverage_line_percent == 100.0
    assert dash.blocking_failures == ("b",)
    assert dash.stage_status == {"a": "passed", "b": "failed"}
    assert dash.to_dict()["dashboard_sha256"] == dash.dashboard_sha256

    no_cov = ExecutionReport.create(
        repository_id="R",
        epic_id="E",
        config_digest="d",
        stage_results=(_result("a", StageOutcome.PASSED),),
    )
    assert no_cov.dashboard().coverage_line_percent is None
