"""EPIC-PLAT-003 — Repository Operations CLI tests (Terminal T5)."""

from __future__ import annotations

import json
from platform.repository_operations.cli import main
from platform.tests.repository_operations_helpers import (
    COVERAGE_XML_FULL,
    accepted_facts,
    rejected_facts,
)

import pytest


def _write_config(tmp_path, facts):
    (tmp_path / "coverage.xml").write_text(COVERAGE_XML_FULL, encoding="utf-8")
    config = {
        "repository_id": "R",
        "epic_id": "E",
        "stages": [
            {"stage_id": "freeze", "kind": "freeze", "params": {"paths": ["engine/a.py"]}},
            {"stage_id": "coverage", "kind": "coverage", "params": {"min_percent": 90}},
            {"stage_id": "acceptance", "kind": "acceptance", "params": {"facts": facts}},
        ],
    }
    path = tmp_path / "ops.json"
    path.write_text(json.dumps(config), encoding="utf-8")
    return path


def test_cli_pass_returns_zero(tmp_path, capsys):
    cfg = _write_config(tmp_path, accepted_facts())
    rc = main(["--config", str(cfg), "--repo-root", str(tmp_path)])
    assert rc == 0
    err = capsys.readouterr().err
    assert "VERDICT: PASS" in err
    assert "coverage:   line 100.0%" in err


def test_cli_fail_returns_one(tmp_path, capsys):
    cfg = _write_config(tmp_path, rejected_facts())
    rc = main(["--config", str(cfg), "--repo-root", str(tmp_path)])
    assert rc == 1
    assert "VERDICT: FAIL" in capsys.readouterr().err


def test_cli_json_output(tmp_path, capsys):
    cfg = _write_config(tmp_path, accepted_facts())
    rc = main(["--config", str(cfg), "--repo-root", str(tmp_path), "--json"])
    assert rc == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["verdict"] == "pass"
    assert payload["report_format"].startswith("ucos-repository-operations-report/")


def test_cli_resume_with_checkpoint(tmp_path):
    cfg = _write_config(tmp_path, accepted_facts())
    checkpoint = tmp_path / "cp.json"
    base = ["--config", str(cfg), "--repo-root", str(tmp_path), "--checkpoint", str(checkpoint)]
    assert main(base) == 0
    assert checkpoint.is_file()
    assert main([*base, "--resume"]) == 0


def test_cli_config_error_returns_two(tmp_path, capsys):
    rc = main(["--config", str(tmp_path / "absent.json"), "--repo-root", str(tmp_path)])
    assert rc == 2
    assert "repository operations error" in capsys.readouterr().err


def test_cli_requires_config_argument():
    with pytest.raises(SystemExit):
        main([])
