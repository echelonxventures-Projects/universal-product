"""Tests for the ucos-uprf CLI, error surface, and metatype helpers."""

from __future__ import annotations

import json

from engine.provider.cli import main
from engine.provider.errors import (
    ProviderContractError,
    ProviderFrameworkError,
    ProviderSelectionError,
)
from engine.provider.metatypes import facet_keys


def test_cli_describe(capsys):
    assert main(["describe"]) == 0
    out = json.loads(capsys.readouterr().out)
    assert out["open_world"] is True


def test_cli_certify(capsys):
    assert main(["certify"]) == 0
    out = json.loads(capsys.readouterr().out)
    assert out["determination"] == "CERTIFIED"


def test_cli_prove(capsys):
    assert main(["prove"]) == 0
    out = json.loads(capsys.readouterr().out)
    assert out["passed"] is True


def test_cli_gate_alias(capsys):
    assert main(["--gate"]) == 0
    capsys.readouterr()


def test_cli_no_command_prints_help(capsys):
    assert main([]) == 0
    assert "ucos-uprf" in capsys.readouterr().out


def test_cli_evidence_writes(tmp_path, capsys):
    assert main(["evidence", str(tmp_path)]) == 0
    written = json.loads(capsys.readouterr().out)["written"]
    assert written
    for name in (
        "uprf-constitutional-compliance.json",
        "uprf-quality-gates.json",
        "uprf-architectural-proof.json",
        "uprf-framework-certification.json",
        "uprf-framework-description.json",
    ):
        path = tmp_path / name
        assert path.is_file()
        json.loads(path.read_text())


def test_error_hierarchy_and_context():
    err = ProviderContractError("bad", contract={"x": 1})
    assert isinstance(err, ProviderFrameworkError)
    assert err.to_dict()["error"] == "ProviderContractError"
    assert isinstance(ProviderSelectionError("s"), ProviderFrameworkError)


def test_facet_keys_sorted():
    keys = facet_keys()
    assert list(keys) == sorted(keys)
    assert "ProviderContract" in keys
