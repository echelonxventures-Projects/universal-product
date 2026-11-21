"""UCOS-EPIC-013 — Continuous Validation Intelligence CLI tests (Terminal T5).

The one-command surface. Its contract is the exit status — ``0`` PASS, ``1`` FAIL, ``2``
authoring/execution fault — and the separation of streams: the human summary goes to
stderr so the machine-readable JSON on stdout stays pipeable.
"""

from __future__ import annotations

import json
from pathlib import Path
from platform.tests._validation_intelligence_helpers import facts_with, passing_config_mapping
from platform.validation_intelligence.cli import main
from typing import Any

import pytest


def _config_file(tmp_path: Path, payload: dict[str, Any], name: str = "intel.json") -> str:
    path = tmp_path / name
    path.write_text(json.dumps(payload), encoding="utf-8")
    return str(path)


@pytest.fixture
def passing_config(tmp_path: Path) -> str:
    return _config_file(tmp_path, passing_config_mapping("cli-target"))


@pytest.fixture
def failing_config(tmp_path: Path) -> str:
    payload = {"target_id": "cli-target", "facts": facts_with("repository_completeness", gaps=3)}
    return _config_file(tmp_path, payload, "failing.json")


# --- exit status -----------------------------------------------------------------
def test_a_passing_run_exits_zero(passing_config):
    assert main(["--config", passing_config]) == 0


def test_a_failing_run_exits_one(failing_config):
    """Fail-closed: a FAIL verdict must be visible to a shell gate."""
    assert main(["--config", failing_config]) == 1


def test_a_missing_config_exits_two(tmp_path, capsys):
    assert main(["--config", str(tmp_path / "absent.json")]) == 2
    assert "validation intelligence error" in capsys.readouterr().err


def test_a_malformed_config_exits_two(tmp_path, capsys):
    path = tmp_path / "bad.json"
    path.write_text("{not json", encoding="utf-8")
    assert main(["--config", str(path)]) == 2
    assert "validation intelligence error" in capsys.readouterr().err


def test_an_unknown_dimension_in_the_config_exits_two(tmp_path):
    path = _config_file(tmp_path, {"target_id": "t", "dimensions": ["bogus"]}, "dim.json")
    assert main(["--config", path]) == 2


def test_an_execution_fault_exits_two_without_emitting_a_report(tmp_path, capsys):
    """An authoring fault must never be mistaken for a clean PASS."""
    path = _config_file(tmp_path, {"target_id": "t", "facts": {"bogus_dimension": {}}}, "f.json")
    assert main(["--config", path]) == 2
    assert capsys.readouterr().out == ""


def test_the_config_argument_is_required():
    with pytest.raises(SystemExit) as exc:
        main([])
    assert exc.value.code == 2


# --- the human summary lands on stderr -------------------------------------------
def test_the_summary_is_written_to_stderr(passing_config, capsys):
    main(["--config", passing_config])
    captured = capsys.readouterr()
    assert "CONTINUOUS VALIDATION INTELLIGENCE SUMMARY" in captured.err
    assert "VERDICT: PASS" in captured.err
    assert captured.out == ""


def test_the_summary_names_the_target_and_every_dimension(passing_config, capsys):
    main(["--config", passing_config])
    err = capsys.readouterr().err
    assert "target: cli-target" in err
    for dimension in (
        "cross_capability_consistency",
        "repository_completeness",
        "contract_compatibility",
        "architecture_compliance",
        "runtime_compatibility",
        "version_compatibility",
        "governance_compliance",
    ):
        assert dimension in err


def test_the_summary_reports_compatibility_and_compliance(passing_config, capsys):
    main(["--config", passing_config])
    err = capsys.readouterr().err
    assert "compatible: True" in err
    assert "compliant:  True" in err


def test_a_failing_summary_marks_the_blocking_check(failing_config, capsys):
    main(["--config", failing_config])
    err = capsys.readouterr().err
    assert "VERDICT: FAIL" in err
    assert "BLOCK repository_completeness.no-gaps" in err


def test_the_summary_totals_the_checks(passing_config, capsys):
    main(["--config", passing_config])
    assert "across 7 dimensions" in capsys.readouterr().err


# --- machine-readable stdout -----------------------------------------------------
def test_json_emits_the_report_on_stdout(passing_config, capsys):
    main(["--config", passing_config, "--json"])
    payload = json.loads(capsys.readouterr().out)
    assert payload["report_format"] == "ucos-validation-intelligence-report/1.0.0"
    assert payload["target_id"] == "cli-target"
    assert payload["verdict"] == "pass"


def test_compatibility_emits_the_compatibility_report(passing_config, capsys):
    main(["--config", passing_config, "--compatibility"])
    payload = json.loads(capsys.readouterr().out)
    assert payload["report_format"] == "ucos-validation-compatibility-report/1.0.0"
    assert payload["compatible"] is True


def test_compliance_emits_the_compliance_report(passing_config, capsys):
    main(["--config", passing_config, "--compliance"])
    payload = json.loads(capsys.readouterr().out)
    assert payload["report_format"] == "ucos-validation-compliance-report/1.0.0"
    assert payload["compliant"] is True


def test_evidence_emits_the_evidence_record(passing_config, capsys):
    main(["--config", passing_config, "--evidence"])
    payload = json.loads(capsys.readouterr().out)
    assert payload["evidence_format"] == "ucos-validation-intelligence-evidence/1.0.0"
    assert payload["evidence_sha256"]


def test_every_emission_flag_composes(passing_config, capsys):
    main(
        [
            "--config",
            passing_config,
            "--json",
            "--compatibility",
            "--compliance",
            "--evidence",
        ]
    )
    decoder = json.JSONDecoder()
    out = capsys.readouterr().out
    formats, index = [], 0
    while index < len(out):
        if out[index].isspace():
            index += 1
            continue
        payload, index = decoder.raw_decode(out, index)
        formats.append(payload.get("report_format") or payload.get("evidence_format"))
    assert formats == [
        "ucos-validation-intelligence-report/1.0.0",
        "ucos-validation-compatibility-report/1.0.0",
        "ucos-validation-compliance-report/1.0.0",
        "ucos-validation-intelligence-evidence/1.0.0",
    ]


def test_emitted_json_is_key_sorted_for_replay_stability(passing_config, capsys):
    """Deterministic evidence: the same run must emit byte-identical JSON."""
    main(["--config", passing_config, "--json"])
    first = capsys.readouterr().out
    main(["--config", passing_config, "--json"])
    assert capsys.readouterr().out == first


def test_a_failing_run_still_emits_its_report(failing_config, capsys):
    assert main(["--config", failing_config, "--json"]) == 1
    payload = json.loads(capsys.readouterr().out)
    assert payload["verdict"] == "fail"
    assert "repository_completeness.no-gaps" in payload["blocking_failures"]


# --- configuration drives the run ------------------------------------------------
def test_a_declared_dimension_subset_scopes_the_cli_run(tmp_path, capsys):
    payload = {
        "target_id": "scoped",
        "dimensions": ["repository_completeness"],
        "facts": passing_config_mapping()["facts"],
    }
    assert main(["--config", _config_file(tmp_path, payload, "scoped.json"), "--json"]) == 0
    report = json.loads(capsys.readouterr().out)
    assert list(report["dimension_verdicts"]) == ["repository_completeness"]


def test_a_toml_config_is_accepted(tmp_path, capsys):
    path = tmp_path / "intel.toml"
    path.write_text(
        'target_id = "toml-target"\ndimensions = ["repository_completeness"]\n\n'
        "[facts.repository_completeness]\ngaps = 0\n"
        'required_artifacts = [{ id = "a", present = true }]\n\n'
        "[facts.repository_completeness.coverage]\ncovered = 1\ntotal = 1\n",
        encoding="utf-8",
    )
    assert main(["--config", str(path)]) == 0
    assert "toml-target" in capsys.readouterr().err
