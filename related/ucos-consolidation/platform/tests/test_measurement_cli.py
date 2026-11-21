"""UCOS-EPIC-004 — Universal Measurement Engine CLI tests (UCOS-UMA-001)."""

from __future__ import annotations

import json
from pathlib import Path
from platform.measurement.cli import main

import pytest

from engine.registry.models import TRACE_STAGES


def _write_registry(data_dir: Path, *, complete: bool) -> None:
    """Write a minimal 00-BOOK/DATA-shaped registry substrate for the CLI to measure."""
    full_trace = {stage: [f"UCOS-A001-{stage}"] for stage in TRACE_STAGES}
    artifacts = [
        {
            "universal_id": "UCOS-A001",
            "name": "A1",
            "volume": "V-001",
            "page_start": 1,
            "page_end": 2,
            "status": "CERTIFIED",
            "version": "1.0.0",
            "path": "a1.md",
            "program": "PROG-1",
            "category": "CAT-A",
            "owner": "ORG-CORE",
            "traceability": full_trace,
        },
        {
            "universal_id": "UCOS-A002",
            "name": "A2",
            "volume": "V-001",
            "page_start": 3,
            "page_end": 4,
            "status": "CERTIFIED",
            "version": "1.0.0",
            "path": "a2.md",
            "program": "PROG-1",
            "category": "CAT-A",
            "owner": "ORG-CORE",
            "traceability": {stage: [f"UCOS-A002-{stage}"] for stage in TRACE_STAGES},
        },
    ]
    if not complete:
        artifacts.append(
            {
                "universal_id": "UCOS-A003",
                "name": "A3",
                "volume": "V-UNKNOWN",
                "page_start": 5,
                "page_end": 6,
                "status": "IN_PROGRESS",
                "version": "1.0.0",
                "path": "a3.md",
                "program": "PROG-1",
                "category": "CAT-A",
                "owner": "UNASSIGNED",
                "traceability": {"requirement": ["UCOS-A003-requirement"]},
            }
        )
    (data_dir / "artifacts.json").write_text(json.dumps({"artifacts": artifacts}), encoding="utf-8")
    (data_dir / "relationships.json").write_text(
        json.dumps(
            {
                "relationships": [
                    {
                        "edge_id": "E1",
                        "from": "UCOS-A001",
                        "to": "UCOS-A002",
                        "type": "Depends-On",
                    }
                ]
            }
        ),
        encoding="utf-8",
    )
    (data_dir / "volumes.json").write_text(
        json.dumps(
            {
                "volumes": [
                    {
                        "volume_id": "V-001",
                        "serial": 1,
                        "name": "V1",
                        "category": "CAT-A",
                        "status": "ACTIVE",
                        "artifact_count": 2,
                    }
                ]
            }
        ),
        encoding="utf-8",
    )


@pytest.fixture()
def complete_dir(tmp_path: Path) -> Path:
    _write_registry(tmp_path, complete=True)
    return tmp_path


@pytest.fixture()
def gapped_dir(tmp_path: Path) -> Path:
    _write_registry(tmp_path, complete=False)
    return tmp_path


@pytest.mark.parametrize(
    "command", ["report", "enumerate", "metrics", "coverage", "gaps", "evidence", "health"]
)
def test_each_command_succeeds(command: str, complete_dir: Path):
    assert main([command, "--data-dir", str(complete_dir)]) == 0


def test_report_json_emits_machine_body(complete_dir: Path, capsys):
    rc = main(["report", "--json", "--data-dir", str(complete_dir)])
    assert rc == 0
    out = json.loads(capsys.readouterr().out)
    assert out["uma_id"] == "UCOS-UMA-001"
    assert out["counts"]["artifacts"] == 2


def test_health_strict_fails_on_gapped_registry(gapped_dir: Path):
    # complete registry: strict health passes.
    # gapped registry: strict health returns non-zero (fail-closed).
    assert main(["health", "--strict", "--data-dir", str(gapped_dir)]) == 1


def test_gaps_json_reports_structural_gaps(gapped_dir: Path, capsys):
    rc = main(["gaps", "--json", "--data-dir", str(gapped_dir)])
    assert rc == 0
    out = json.loads(capsys.readouterr().out)
    assert out["structural_count"] >= 1


def test_bad_data_dir_exits_two(tmp_path: Path):
    missing = tmp_path / "does-not-exist"
    assert main(["report", "--data-dir", str(missing)]) == 2
