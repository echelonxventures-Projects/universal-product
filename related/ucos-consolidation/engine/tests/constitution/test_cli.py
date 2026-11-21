"""UCOS-CEL-0001 — the CLI emits evidence, and its exit code is the verdict.

Two things are asserted of every subcommand: that stdout parses as JSON and nothing else
is written to it, and that the exit code tracks the constitutional condition rather than
merely tracking whether the program crashed. A gate that prints ``FAIL`` and exits 0 is
not a gate, and that is the failure this file exists to catch.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from engine.constitution import catalog
from engine.constitution.cli import main
from engine.nucleus import lifecycle as ucl
from engine.tests.constitution.conftest import declare, population

REPORTING = ["law", "mandate", "catalog", "gateway", "seal", "replay"]
GATING = ["population", "graph", "authority", "legality", "plan", "acceptance", "cycle"]


@pytest.mark.parametrize("command", REPORTING + GATING)
def test_every_subcommand_emits_json_and_exits_zero_on_the_system(command, capsys) -> None:
    assert main([command]) == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["digest"]


def _violating(tmp_path: Path) -> str:
    """A population that breaks every gate at once: incomplete, dangling and self-certifying."""
    document = population(
        declare(
            "broken",
            dependencies=("ghost",),
            certifications=("broken",),
            governance_rules=(),
        )
    )
    path = tmp_path / "population.json"
    path.write_text(json.dumps(document.to_dict()), encoding="utf-8")
    return str(path)


@pytest.mark.parametrize("command", GATING)
def test_every_gating_subcommand_exits_one_on_a_violating_population(
    command, tmp_path: Path, capsys
) -> None:
    assert main(["--population", _violating(tmp_path), command]) == 1
    assert json.loads(capsys.readouterr().out)


def test_replay_still_settles_over_a_violating_population(tmp_path: Path, capsys) -> None:
    """Determinism is orthogonal to legality: a broken state must fail the *same way* twice.

    ``replay`` is not a legality gate, and making it exit 1 here would conflate "this state
    is wrong" with "this state is unstable" — two failures with entirely different fixes.
    """
    assert main(["--population", _violating(tmp_path), "replay"]) == 0
    assert json.loads(capsys.readouterr().out)["fixed_point"] is True


def test_a_lawful_population_document_round_trips(tmp_path: Path, capsys) -> None:
    system = catalog.build_population()
    path = tmp_path / "system.json"
    path.write_text(json.dumps(system.to_dict()), encoding="utf-8")
    assert main(["--population", str(path), "acceptance"]) == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["status"] == "PASS"
    assert payload["scope"]["population_digest"] == system.digest()


def test_the_assimilate_subcommand_gates_on_reuse(capsys) -> None:
    assert main(["assimilate", "--subject", "constitution.law"]) == 1
    refused = json.loads(capsys.readouterr().out)
    assert refused["status"] == "REUSE"
    assert "constitution.law" in refused["reuse_targets"]

    assert main(["assimilate", "--subject", "genuinely.new", "--outputs", "novel"]) == 0
    assert json.loads(capsys.readouterr().out)["status"] == "CREATE"


def test_the_lifecycle_subcommand_runs_ucl_000001(capsys) -> None:
    assert main(["lifecycle", "--subject", "repository"]) == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["declared_stage_count"] == len(ucl.STAGES)
    assert payload["stage_count"] == payload["declared_stage_count"]


def test_a_malformed_population_document_fails_closed(tmp_path: Path, capsys) -> None:
    path = tmp_path / "bad.json"
    path.write_text(json.dumps({"records": "not a list"}), encoding="utf-8")
    assert main(["--population", str(path), "acceptance"]) == 1
    assert "error" in json.loads(capsys.readouterr().out)


def test_output_is_byte_identical_across_runs(capsys) -> None:
    main(["acceptance"])
    first = capsys.readouterr().out
    main(["acceptance"])
    assert capsys.readouterr().out == first
