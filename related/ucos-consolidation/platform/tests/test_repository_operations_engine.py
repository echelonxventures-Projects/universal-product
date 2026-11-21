"""EPIC-PLAT-003 — Repository Operations orchestrator tests (Terminal T5)."""

from __future__ import annotations

from platform.repository_operations.checkpoint import Checkpoint, CheckpointStore
from platform.repository_operations.config import parse_config
from platform.repository_operations.contracts import OperationsVerdict, StageOutcome
from platform.repository_operations.engine import RepositoryOperationsOrchestrator
from platform.repository_operations.errors import OperationsServiceError
from platform.tests.repository_operations_helpers import (
    COVERAGE_XML_FULL,
    acceptance_stage,
    constant_runner,
)

import pytest


def _config(tmp_path, *, command_code_stage=True):
    stages = [
        {"stage_id": "freeze", "kind": "freeze", "params": {"paths": ["engine/a.py"]}},
        {
            "stage_id": "coverage",
            "kind": "coverage",
            "params": {"path": "coverage.xml", "min_percent": 90},
        },
        acceptance_stage(),
    ]
    if command_code_stage:
        stages.insert(0, {"stage_id": "verify", "kind": "command", "params": {"command": "verify"}})
    (tmp_path / "coverage.xml").write_text(COVERAGE_XML_FULL, encoding="utf-8")
    return parse_config({"repository_id": "R", "epic_id": "E", "stages": stages})


def _orchestrator(tmp_path, *, runner=None, store=None):
    return RepositoryOperationsOrchestrator(
        _config(tmp_path),
        command_runner=runner or constant_runner(0),
        repo_root=tmp_path,
        checkpoint_store=store,
    )


def test_run_all_pass_captures_coverage(tmp_path):
    report = _orchestrator(tmp_path).run()
    assert report.verdict is OperationsVerdict.PASS
    assert report.coverage is not None and report.coverage.line_percent == 100.0
    assert {r.stage_id for r in report.stage_results} == {
        "verify",
        "freeze",
        "coverage",
        "acceptance",
    }


def test_run_fail_when_blocking_command_fails(tmp_path):
    report = _orchestrator(tmp_path, runner=constant_runner(1)).run()
    assert report.verdict is OperationsVerdict.FAIL
    assert "verify" in report.blocking_failures()
    # non-command stages still ran (run-all-then-summarize contract).
    assert any(r.stage_id == "acceptance" and r.passed for r in report.stage_results)


def test_resume_skips_passed_stages(tmp_path):
    store = CheckpointStore(tmp_path / "cp.json")
    first = _orchestrator(tmp_path, store=store).run()
    assert not first.resumed

    # A resumed run with a runner that would fail proves passed stages are skipped.
    second = _orchestrator(tmp_path, runner=constant_runner(1), store=store).run(resume=True)
    assert second.resumed
    assert second.verdict is OperationsVerdict.PASS
    verify = next(r for r in second.stage_results if r.stage_id == "verify")
    assert verify.outcome is StageOutcome.SKIPPED


def test_resume_ignores_stale_checkpoint(tmp_path):
    store = CheckpointStore(tmp_path / "cp.json")
    store.save(Checkpoint(config_digest="stale-digest", completed={"verify": "x"}))
    report = _orchestrator(tmp_path, runner=constant_runner(1), store=store).run(resume=True)
    # stale checkpoint discarded → verify re-runs and fails.
    assert report.verdict is OperationsVerdict.FAIL
    assert not report.resumed


def test_run_without_store_does_not_persist(tmp_path):
    report = _orchestrator(tmp_path, store=None).run(resume=True)
    assert report.verdict is OperationsVerdict.PASS


def test_orchestrator_validates_arguments(tmp_path):
    config = _config(tmp_path)
    with pytest.raises(OperationsServiceError):
        RepositoryOperationsOrchestrator(
            "nope",
            command_runner=constant_runner(0),
            repo_root=tmp_path,  # type: ignore[arg-type]
        )
    with pytest.raises(OperationsServiceError):
        RepositoryOperationsOrchestrator(config, command_runner="x", repo_root=tmp_path)  # type: ignore[arg-type]
    with pytest.raises(OperationsServiceError):
        RepositoryOperationsOrchestrator(
            config,
            command_runner=constant_runner(0),
            repo_root=tmp_path,
            checkpoint_store="x",  # type: ignore[arg-type]
        )


def test_orchestrator_exposes_config_and_store(tmp_path):
    store = CheckpointStore(tmp_path / "cp.json")
    orch = _orchestrator(tmp_path, store=store)
    assert orch.config.repository_id == "R"
    assert orch.checkpoint_store is store
