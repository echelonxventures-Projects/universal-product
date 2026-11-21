"""EPIC-PLAT-003 — Pipeline stage executor tests (Terminal T5)."""

from __future__ import annotations

import functools
import os
import subprocess
from platform.repository_operations.contracts import CoverageSummary, StageSpec
from platform.repository_operations.errors import (
    CoverageReportError,
    StageDefinitionError,
    StageExecutionError,
)
from platform.repository_operations.stages import execute_stage
from platform.tests.repository_operations_helpers import (
    COVERAGE_XML_FULL,
    COVERAGE_XML_LOW,
    accepted_facts,
    constant_runner,
    invalid_validation_subject,
    rejected_facts,
    valid_validation_subject,
)

import pytest


def _spec(kind, params, stage_id="s"):
    return StageSpec.from_mapping({"stage_id": stage_id, "kind": kind, "params": params})


def _run(spec, *, runner=None, repo_root="."):
    return execute_stage(spec, command_runner=runner or constant_runner(0), repo_root=repo_root)


# -- command -----------------------------------------------------------------
def test_command_stage_pass_and_fail():
    result, cov = _run(_spec("command", {"command": "verify"}), runner=constant_runner(0))
    assert result.passed and cov is None
    assert result.detail["returncode"] == 0

    result, _ = _run(_spec("command", {"command": "verify"}), runner=constant_runner(2))
    assert result.failed


def test_command_stage_requires_command_name():
    with pytest.raises(StageExecutionError):
        _run(_spec("command", {}))


def test_command_stage_rejects_non_canonical_command():
    with pytest.raises(StageDefinitionError):
        _run(_spec("command", {"command": "evil"}))


# -- acceptance --------------------------------------------------------------
def test_acceptance_stage_accepted():
    result, cov = _run(_spec("acceptance", {"facts": accepted_facts()}))
    assert result.passed and cov is None
    assert result.detail["readiness_verdict"] == "READY"
    assert result.evidence_ref.startswith("UCOS-ACCEPT-")


def test_acceptance_stage_rejected():
    result, _ = _run(_spec("acceptance", {"facts": rejected_facts()}))
    assert result.failed
    assert result.detail["readiness_verdict"] == "NOT-READY"


def test_acceptance_stage_requires_facts_mapping():
    with pytest.raises(StageExecutionError):
        _run(_spec("acceptance", {}))


def test_acceptance_stage_assimilation_error():
    with pytest.raises(StageExecutionError):
        _run(_spec("acceptance", {"facts": {"epic_id": "E"}}))


def test_acceptance_measured_coverage_overrides_declared_facts():
    """EIP-018 (FP-13): measurement replaces self-declared coverage.

    ``accepted_facts()`` declares complete coverage across every required dimension.
    Supplying a MEASURED summary that is incomplete must flip the verdict, proving the
    declared facts no longer decide the outcome.
    """
    measured = CoverageSummary(
        line_rate=0.5,
        branch_rate=0.5,
        lines_covered=1,
        lines_valid=2,
        branches_covered=1,
        branches_valid=2,
    )
    spec = _spec("acceptance", {"facts": accepted_facts(), "coverage_from_measurement": True})
    result, _ = execute_stage(
        spec,
        command_runner=constant_runner(0),
        repo_root=".",
        measured_coverage=measured,
    )
    assert result.failed
    assert result.detail["coverage_source"] == "measured"

    # Same facts, no measurement injection -> the declared facts still stand.
    declared, _ = _run(_spec("acceptance", {"facts": accepted_facts()}))
    assert declared.passed
    assert declared.detail["coverage_source"] == "declared"


def test_acceptance_measured_coverage_without_measurement_is_fail_closed():
    """Declaring measured coverage with no measurement must abort, not silently fall back."""
    spec = _spec("acceptance", {"facts": accepted_facts(), "coverage_from_measurement": True})
    with pytest.raises(StageExecutionError):
        _run(spec)


# -- validation --------------------------------------------------------------
def test_validation_stage_pass_and_fail():
    result, _ = _run(_spec("validation", {"subject": valid_validation_subject()}))
    assert result.passed
    assert result.detail["verdict"] == "pass"

    result, _ = _run(_spec("validation", {"subject": invalid_validation_subject()}))
    assert result.failed
    assert "signature-present" in result.detail["blocking_failures"]


def test_validation_stage_requires_subject():
    with pytest.raises(StageExecutionError):
        _run(_spec("validation", {}))


# -- certification -----------------------------------------------------------
def test_certification_stage_certified():
    result, _ = _run(
        _spec("certification", {"subject": valid_validation_subject(), "version": "1.2.3"})
    )
    assert result.passed
    assert result.detail["status"] == "certified"
    assert result.evidence_ref.startswith("UCOS-CERT-")


def test_certification_stage_not_certified():
    result, _ = _run(_spec("certification", {"subject": invalid_validation_subject()}))
    assert result.failed
    assert result.detail["status"] == "not-certified"


def test_certification_stage_requires_subject():
    with pytest.raises(StageExecutionError):
        _run(_spec("certification", {}))


# -- freeze ------------------------------------------------------------------
def test_freeze_stage_clean_and_violation():
    clean, _ = _run(_spec("freeze", {"paths": ["engine/x.py", "platform/y.py"]}))
    assert clean.passed
    assert clean.detail["checked"] == 2

    dirty, _ = _run(_spec("freeze", {"paths": ["00-BOOK/notes.md", "engine/ok.py"]}))
    assert dirty.failed
    assert dirty.detail["violations"] == ["00-BOOK/notes.md"]


def test_freeze_stage_empty_declared_subject_is_fail_closed():
    """EIP-018 (FP-14): an empty subject evidences nothing and must not pass.

    This previously asserted the opposite (``test_freeze_stage_default_empty_paths_pass``):
    a freeze stage with no paths returned PASSED, so the architecture-freeze guard in
    ``repo-operations.json`` — configured with ``paths: []`` — was a guaranteed pass over
    nothing at all.
    """
    with pytest.raises(StageExecutionError):
        _run(_spec("freeze", {}))
    with pytest.raises(StageExecutionError):
        _run(_spec("freeze", {"paths": []}))


def test_freeze_stage_rejects_unknown_subject_source():
    with pytest.raises(StageExecutionError):
        _run(_spec("freeze", {"subject": "guesswork"}))


def _init_repo(root):
    """A throwaway git work tree with one commit, so HEAD resolves."""
    env = {"GIT_CONFIG_GLOBAL": "/dev/null", "GIT_CONFIG_SYSTEM": "/dev/null"}
    run = functools.partial(subprocess.run, cwd=str(root), check=True, capture_output=True)
    run(["git", "init", "-q", "-b", "main"], env={**os.environ, **env})
    run(["git", "config", "user.email", "t@example.invalid"])
    run(["git", "config", "user.name", "t"])
    (root / "seed.txt").write_text("seed\n", encoding="utf-8")
    run(["git", "add", "seed.txt"])
    run(["git", "commit", "-q", "-m", "seed"], env={**os.environ, **env})


def test_freeze_stage_working_tree_subject_passes_on_non_corpus_write(tmp_path):
    _init_repo(tmp_path)
    (tmp_path / "engine").mkdir()
    (tmp_path / "engine" / "new.py").write_text("x = 1\n", encoding="utf-8")

    result, _ = _run(_spec("freeze", {"subject": "working-tree"}), repo_root=tmp_path)
    assert result.passed
    assert result.detail["subject_source"] == "working-tree"
    assert result.detail["violations"] == []
    # The subject was DERIVED from git, not declared in config: the untracked write
    # is what makes the count non-zero.
    assert result.detail["checked"] == 1


def test_freeze_stage_working_tree_subject_detects_real_corpus_write(tmp_path):
    """A write into the frozen corpus must be caught from the derived subject alone."""
    _init_repo(tmp_path)
    (tmp_path / "00-BOOK").mkdir()
    (tmp_path / "00-BOOK" / "smuggled.md").write_text("nope\n", encoding="utf-8")

    result, _ = _run(_spec("freeze", {"subject": "working-tree"}), repo_root=tmp_path)
    assert result.failed
    assert result.detail["violations"] == ["00-BOOK/smuggled.md"]


def test_freeze_stage_working_tree_subject_fails_closed_without_git(tmp_path):
    """No git work tree means the write set is unknown, which must abort, not pass."""
    with pytest.raises(StageExecutionError):
        _run(_spec("freeze", {"subject": "working-tree"}), repo_root=tmp_path)


def test_freeze_stage_rejects_non_list_paths():
    with pytest.raises(StageExecutionError):
        _run(_spec("freeze", {"paths": "00-BOOK/x"}))


# -- coverage ----------------------------------------------------------------
def test_coverage_stage_pass(tmp_path):
    (tmp_path / "coverage.xml").write_text(COVERAGE_XML_FULL, encoding="utf-8")
    result, cov = _run(
        _spec("coverage", {"path": "coverage.xml", "min_percent": 90}), repo_root=tmp_path
    )
    assert result.passed
    assert cov is not None and cov.line_percent == 100.0


def test_coverage_stage_below_threshold(tmp_path):
    (tmp_path / "coverage.xml").write_text(COVERAGE_XML_LOW, encoding="utf-8")
    result, cov = _run(_spec("coverage", {"min_percent": 90}), repo_root=tmp_path)
    assert result.failed
    assert cov is not None and cov.line_percent == 50.0


def test_coverage_stage_absolute_path(tmp_path):
    report = tmp_path / "cov.xml"
    report.write_text(COVERAGE_XML_FULL, encoding="utf-8")
    result, cov = _run(_spec("coverage", {"path": str(report)}), repo_root="/nowhere")
    assert result.passed and cov is not None


def test_coverage_stage_report_not_found(tmp_path):
    result, cov = _run(_spec("coverage", {"path": "missing.xml"}), repo_root=tmp_path)
    assert result.failed and cov is None
    assert "not found" in result.summary


def test_coverage_stage_bad_min_percent(tmp_path):
    with pytest.raises(StageExecutionError):
        _run(_spec("coverage", {"min_percent": "high"}), repo_root=tmp_path)


def test_coverage_stage_malformed_report(tmp_path):
    (tmp_path / "coverage.xml").write_text("<coverage ", encoding="utf-8")
    with pytest.raises(CoverageReportError):
        _run(_spec("coverage", {}), repo_root=tmp_path)
