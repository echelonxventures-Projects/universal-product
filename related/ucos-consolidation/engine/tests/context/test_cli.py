"""UCXI-000001 Part 14 — CLI tests.

Every command must emit parseable canonical JSON on stdout and carry gate exit
semantics: 0 the assertion holds, 1 it does not, 2 the request could not be assessed.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from engine.context.certification import VERDICT_CERTIFIED
from engine.context.cli import build_parser, main


def _run(capsys: pytest.CaptureFixture[str], *argv: str) -> tuple[int, dict]:
    code = main(list(argv))
    out = capsys.readouterr().out
    return code, json.loads(out)


def test_parser_requires_a_command() -> None:
    with pytest.raises(SystemExit):
        build_parser().parse_args([])


def test_constitution_command(capsys: pytest.CaptureFixture[str]) -> None:
    code, payload = _run(capsys, "constitution")
    assert code == 0
    assert payload["constitution"]["count"] == 12
    assert payload["assessment"]["is_compliant"] is True


def test_taxonomy_and_ontology_commands(capsys: pytest.CaptureFixture[str]) -> None:
    code, taxonomy = _run(capsys, "taxonomy")
    assert code == 0
    assert len(taxonomy["universal_kinds"]) == 16

    code, ontology = _run(capsys, "ontology")
    assert code == 0
    assert len(ontology["dimensions"]) == 16


def test_registry_command(capsys: pytest.CaptureFixture[str]) -> None:
    code, payload = _run(capsys, "registry")
    assert code == 0
    assert payload["summary"]["contexts"] == 16
    assert payload["seal"]

    code, verbose = _run(capsys, "--verbose", "registry")
    assert code == 0
    assert len(verbose["contexts"]) == 16
    assert len(verbose["audit"]) == 16


def test_registry_command_on_an_empty_set(capsys: pytest.CaptureFixture[str]) -> None:
    code, payload = _run(capsys, "--empty", "registry")
    assert code == 0
    assert payload["summary"]["contexts"] == 0


def test_resolve_commands(capsys: pytest.CaptureFixture[str]) -> None:
    code, resolved = _run(capsys, "resolve", "temporal")
    assert code == 0
    assert resolved["kind"] == "temporal"

    code, report = _run(capsys, "resolve-all")
    assert code == 0
    assert report["all_resolvable"] is True

    code, report = _run(capsys, "--empty", "resolve-all")
    assert code == 1
    assert report["all_resolvable"] is False


def test_resolve_refusal_is_exit_two(capsys: pytest.CaptureFixture[str]) -> None:
    code, payload = _run(capsys, "--empty", "resolve", "temporal")
    assert code == 2
    assert payload["code"].startswith("CTX-RES")


def test_compose_commands(capsys: pytest.CaptureFixture[str]) -> None:
    code, summary = _run(capsys, "compose", "--require-universal")
    assert code == 0
    assert summary["universally_complete"] is True

    code, full = _run(capsys, "--verbose", "compose")
    assert code == 0
    assert len(full["members"]) == 16

    code, payload = _run(capsys, "--empty", "compose")
    assert code == 2  # an empty composition is refused, not merely reported


def test_graph_and_impact_commands(capsys: pytest.CaptureFixture[str]) -> None:
    code, summary = _run(capsys, "graph")
    assert code == 0
    assert summary["valid"] is True

    code, full = _run(capsys, "--verbose", "graph")
    assert code == 0
    context_id = next(node["id"] for node in full["nodes"] if node["kind"] == "Context")

    code, impact = _run(capsys, "impact", context_id)
    assert code == 0
    assert impact["taxon"]
    assert impact["blast_radius"] == 0

    code, missing = _run(capsys, "impact", "UCOS-CTX-000000000000")
    assert code == 1
    assert missing["error"]


def test_runtime_command(capsys: pytest.CaptureFixture[str]) -> None:
    code, payload = _run(capsys, "runtime")
    assert code == 0
    assert payload["released"] is True
    assert payload["frames"] == ["ucos-universal"]
    assert len(payload["kinds"]) == 16


def test_validate_command(capsys: pytest.CaptureFixture[str]) -> None:
    code, summary = _run(capsys, "validate")
    assert code == 0
    assert summary["is_valid"] is True

    code, full = _run(capsys, "--verbose", "validate", "--strict")
    assert code == 0
    assert full["is_clean"] is True

    code, empty = _run(capsys, "--empty", "validate", "--strict")
    assert code == 1  # advisories fail under --strict
    assert empty["is_valid"] is True

    code, empty = _run(capsys, "--empty", "validate")
    assert code == 0


def test_certify_command(capsys: pytest.CaptureFixture[str]) -> None:
    code, summary = _run(capsys, "certify")
    assert code == 0
    assert summary["verdict"] == VERDICT_CERTIFIED

    code, full = _run(capsys, "--verbose", "certify")
    assert code == 0
    assert len(full["dimensions"]) == 8

    code, degraded = _run(capsys, "--empty", "certify")
    assert code == 1
    assert degraded["certified"] is False


def test_evidence_command(capsys: pytest.CaptureFixture[str], tmp_path: Path) -> None:
    code, index = _run(capsys, "evidence")
    assert code == 0
    assert index["verdict"] == VERDICT_CERTIFIED

    code, full = _run(capsys, "--verbose", "evidence")
    assert code == 0
    assert full["operational"] is True

    out = tmp_path / "evidence.json"
    index_out = tmp_path / "index.json"
    code, payload = _run(capsys, "evidence", "--out", str(out), "--index-out", str(index_out))
    assert code == 0
    assert out.exists() and index_out.exists()
    assert payload["index"]["seal_sha256"]
    assert json.loads(out.read_text(encoding="utf-8"))["programme"] == "UCXI-000001"

    code, degraded = _run(capsys, "--empty", "evidence")
    assert code == 1
    assert degraded["operational"] is False


# --------------------------------------------------------------------------- #
# Part 15/16 — the location surface                                            #
# --------------------------------------------------------------------------- #


def test_frames_command(capsys: pytest.CaptureFixture[str]) -> None:
    code, coverage = _run(capsys, "frames")
    assert code == 0
    assert coverage["frame_count"] > 0
    assert coverage["complete_frames"] + coverage["incomplete_frames"] == coverage["frame_count"]

    code, document = _run(capsys, "--verbose", "frames")
    assert code == 0
    assert document["closed_set"] is False


def test_location_command_resolves_a_frame(capsys: pytest.CaptureFixture[str]) -> None:
    code, payload = _run(capsys, "location", "--frame", "planetary-a1")
    assert code == 0
    assert payload["complete"] is True
    assert payload["unresolved"] == []
    assert payload["digest"]


def test_location_command_fails_closed_on_an_incomplete_frame(
    capsys: pytest.CaptureFixture[str],
) -> None:
    code, payload = _run(capsys, "location", "--frame", "partial-frame-p0")
    assert code == 1
    assert payload["complete"] is False
    assert payload["unresolved"]


def test_location_command_reports_the_whole_architecture(
    capsys: pytest.CaptureFixture[str],
) -> None:
    code, payload = _run(capsys, "location")
    assert code == 0
    assert payload["defaults"] == []
    assert payload["location_axis"] == "location"


def test_location_command_can_show_what_it_registered(
    capsys: pytest.CaptureFixture[str],
) -> None:
    code, payload = _run(capsys, "--verbose", "location", "--frame", "planetary-a1")
    assert code == 0
    assert payload["registered"]
    assert {record["boundary"] for record in payload["registered"]} == {"planetary-a1"}


def test_rebase_command(capsys: pytest.CaptureFixture[str]) -> None:
    code, payload = _run(capsys, "rebase", "--frames", "planetary-a1", "planetary-b4")
    assert code == 0
    assert payload["differing_count"] > 0

    code, unchanged = _run(capsys, "rebase", "--frames", "planetary-a1", "planetary-a1")
    assert code == 1
    assert unchanged["axes_differing"] == []


def test_location_validate_command(capsys: pytest.CaptureFixture[str]) -> None:
    code, summary = _run(capsys, "location-validate")
    assert code == 0
    assert summary["violations"] == 0

    code, full = _run(capsys, "--verbose", "location-validate", "--strict")
    assert code == 0
    assert full["is_clean"] is True


def test_location_certify_command(capsys: pytest.CaptureFixture[str]) -> None:
    code, summary = _run(capsys, "location-certify")
    assert code == 0
    assert summary["verdict"] == VERDICT_CERTIFIED

    code, full = _run(capsys, "--verbose", "location-certify")
    assert code == 0
    assert full["certified"] is True


def test_location_replay_command(capsys: pytest.CaptureFixture[str]) -> None:
    code, payload = _run(capsys, "location-replay")
    assert code == 0
    assert payload["fixed_point"] is True
    assert payload["drifted"] == []


def test_evidence_writes_the_document_without_an_index_when_none_is_asked_for(
    capsys: pytest.CaptureFixture[str], tmp_path
) -> None:
    """``--index-out`` is OPTIONAL, and the arm that skips it had never run — every existing
    evidence test asks for both. A caller writing only the full document must not have an
    index written beside it under a name they never supplied."""
    out = tmp_path / "evidence.json"
    code, payload = _run(capsys, "evidence", "--out", str(out))

    assert code in (0, 1)
    assert out.exists()
    assert payload["wrote"] == str(out)
    assert payload["index"]
    assert not list(tmp_path.glob("index*.json"))
