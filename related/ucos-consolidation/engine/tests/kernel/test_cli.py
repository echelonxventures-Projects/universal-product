"""Tests for the ucos-kernel CLI."""

from __future__ import annotations

import json

from engine.kernel.cli import main


def test_describe(capsys):
    assert main(["describe"]) == 0
    out = json.loads(capsys.readouterr().out)
    assert out["root_metatype"] == "MetaType"


def test_certify(capsys):
    assert main(["certify"]) == 0
    out = json.loads(capsys.readouterr().out)
    assert out["determination"] == "CERTIFIED"


def test_prove_passes(capsys):
    assert main(["prove"]) == 0
    out = json.loads(capsys.readouterr().out)
    assert out["passed"] is True


def test_gate_alias(capsys):
    assert main(["--gate"]) == 0
    capsys.readouterr()


def test_no_command_prints_help(capsys):
    assert main([]) == 0
    assert "ucos-kernel" in capsys.readouterr().out


def test_evidence_writes_files(tmp_path, capsys):
    rc = main(["evidence", str(tmp_path)])
    assert rc == 0
    written = json.loads(capsys.readouterr().out)["written"]
    assert written
    for name in (
        "constitutional-compliance-report.json",
        "quality-gates.json",
        "architectural-proof.json",
        "kernel-self-certification.json",
        "kernel-description.json",
        "kernel-snapshot.json",
    ):
        path = tmp_path / name
        assert path.is_file()
        json.loads(path.read_text())  # valid JSON
