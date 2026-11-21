"""UCOS-EPIC-005 — Universal Validation CLI tests (Terminal T5)."""

from __future__ import annotations

import json
from platform.tests.universal_validation_helpers import passing_facts
from platform.universal_validation import cli

import pytest


def _write_config(tmp_path, raw):
    path = tmp_path / "validation.json"
    path.write_text(json.dumps(raw), encoding="utf-8")
    return str(path)


def test_cli_pass_returns_zero(tmp_path, capsys):
    config = _write_config(tmp_path, {"target_id": "T", "facts": passing_facts()})
    code = cli.main(["--config", config])
    assert code == 0
    err = capsys.readouterr().err
    assert "VERDICT: PASS" in err


def test_cli_fail_returns_one(tmp_path, capsys):
    facts = passing_facts()
    facts["quality"]["tests"] = {"passed": 1, "failed": 2}
    config = _write_config(tmp_path, {"target_id": "T", "facts": facts})
    code = cli.main(["--config", config])
    assert code == 1
    err = capsys.readouterr().err
    assert "VERDICT: FAIL" in err
    assert "BLOCK quality.tests-passing" in err


def test_cli_bad_config_returns_two(tmp_path, capsys):
    config = _write_config(tmp_path, {"facts": {}})  # missing target_id
    code = cli.main(["--config", config])
    assert code == 2
    assert "universal validation error" in capsys.readouterr().err


def test_cli_json_and_evidence_output(tmp_path, capsys):
    config = _write_config(tmp_path, {"target_id": "T", "facts": passing_facts()})
    code = cli.main(["--config", config, "--json", "--evidence"])
    assert code == 0
    out = capsys.readouterr().out
    # two JSON documents were emitted (report then evidence); decode them in sequence.
    decoder = json.JSONDecoder()
    text = out.lstrip()
    report, end = decoder.raw_decode(text)
    assert report["report_format"].startswith("ucos-universal-validation-report/")
    evidence, _ = decoder.raw_decode(text[end:].lstrip())
    assert evidence["evidence_format"].startswith("ucos-universal-validation-evidence/")


def test_cli_requires_config():
    with pytest.raises(SystemExit):
        cli.main([])
