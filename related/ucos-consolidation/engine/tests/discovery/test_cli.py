"""Tests for engine.discovery.cli — the operational discovery command surface."""

from __future__ import annotations

import json

from engine.discovery.cli import build_parser, main


def _run(capsys, argv):
    code = main(argv)
    out = capsys.readouterr().out
    return code, out


def test_cli_discover_clean_exit_zero(capsys, clean_data_dir):
    code, out = _run(capsys, ["--data-dir", str(clean_data_dir), "discover"])
    assert code == 0
    payload = json.loads(out)
    assert payload["complete"] is True
    assert payload["engine_id"] == "UCOS-DISCOVERY-ENGINE"
    assert len(payload["results"]) == 8


def test_cli_discover_gapped_exit_one(capsys, gapped_data_dir):
    code, out = _run(capsys, ["--data-dir", str(gapped_data_dir), "discover"])
    assert code == 1
    assert json.loads(out)["complete"] is False


def test_cli_dimension(capsys, clean_data_dir):
    code, out = _run(capsys, ["--data-dir", str(clean_data_dir), "dimension", "dependency"])
    assert code == 0
    assert json.loads(out)["dimension"] == "dependency"


def test_cli_coverage(capsys, clean_data_dir):
    code, out = _run(capsys, ["--data-dir", str(clean_data_dir), "coverage"])
    assert code == 0
    assert json.loads(out)["schema"] == "ucos-discovery-coverage/1.0.0"


def test_cli_evidence_writes_bundle(capsys, clean_data_dir, tmp_path):
    out_dir = tmp_path / "ev"
    code, out = _run(
        capsys,
        ["--data-dir", str(clean_data_dir), "evidence", "--out", str(out_dir)],
    )
    assert code == 0
    payload = json.loads(out)
    assert payload["complete"] is True
    assert (out_dir / "discovery-evidence-record.json").is_file()


def test_cli_source_error_returns_two(capsys, tmp_path):
    missing = tmp_path / "nope"
    code, out = _run(capsys, ["--data-dir", str(missing), "discover"])
    assert code == 2
    assert "code" in json.loads(out)


def test_cli_parser_requires_subcommand():
    parser = build_parser()
    # argparse exits (SystemExit) when no subcommand is given
    try:
        parser.parse_args([])
    except SystemExit as exc:
        assert exc.code != 0
    else:  # pragma: no cover - defensive
        raise AssertionError("expected SystemExit")
