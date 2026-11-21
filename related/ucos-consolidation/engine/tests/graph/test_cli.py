"""Tests for engine.graph.cli — the read-only operational command surface."""

from __future__ import annotations

import json

import pytest

from engine.graph import cli
from engine.graph.errors import ProjectionError


def _run(capsys, data_dir, *args):
    code = cli.main(["--data-dir", str(data_dir), *args])
    out = capsys.readouterr().out
    return code, out


def test_summary(capsys, graph_data_dir):
    code, out = _run(capsys, graph_data_dir, "summary")
    assert code == 0
    doc = json.loads(out)
    assert doc["contract"]["name"] == "knowledge.graph"


def test_projections(capsys, graph_data_dir):
    code, out = _run(capsys, graph_data_dir, "projections")
    assert code == 0
    assert len(json.loads(out)) == 10


def test_node_found_and_missing(capsys, graph_data_dir):
    code, out = _run(capsys, graph_data_dir, "node", "UCOS-BOOK-000000")
    assert code == 0
    assert json.loads(out)["id"] == "UCOS-BOOK-000000"
    code, out = _run(capsys, graph_data_dir, "node", "UCOS-NOPE-000000")
    assert code == 1
    assert "error" in json.loads(out)


def test_neighbors(capsys, graph_data_dir):
    code, out = _run(capsys, graph_data_dir, "neighbors", "UCOS-ARCH-000001")
    assert code == 0
    doc = json.loads(out)
    assert doc["degree"] > 0
    code, out = _run(capsys, graph_data_dir, "neighbors", "UCOS-NOPE-000000")
    assert code == 1


def test_deps(capsys, graph_data_dir):
    code, out = _run(capsys, graph_data_dir, "deps", "UCOS-IMP-000001")
    assert code == 0
    doc = json.loads(out)
    assert "UCOS-ARCH-000001" in doc["dependencies"]
    # a node absent from the dependency projection
    code, out = _run(capsys, graph_data_dir, "deps", "UCOS-NOPE-000000")
    assert code == 1


def test_impact(capsys, graph_data_dir):
    code, out = _run(capsys, graph_data_dir, "impact", "UCOS-CON-000001")
    assert code == 0
    doc = json.loads(out)
    assert doc["blast_radius"] >= 2


def test_trace(capsys, graph_data_dir):
    code, out = _run(capsys, graph_data_dir, "trace", "UCOS-IMP-000001")
    assert code == 0
    doc = json.loads(out)
    assert "UCOS-ARCH-000001" in doc["trace_forward"]


def test_validate(capsys, graph_data_dir):
    code, out = _run(capsys, graph_data_dir, "validate")
    assert code == 0
    assert json.loads(out)["is_valid"] is True


def test_visualize_dot(capsys, graph_data_dir):
    code, out = _run(
        capsys, graph_data_dir, "visualize", "--projection", "dependency", "--format", "dot"
    )
    assert code == 0
    assert out.startswith("digraph")


def test_evidence_stdout(capsys, graph_data_dir):
    code, out = _run(capsys, graph_data_dir, "evidence")
    assert code == 0
    assert json.loads(out)["operational"] is True


def test_evidence_to_file(capsys, graph_data_dir, tmp_path):
    target = tmp_path / "evidence.json"
    code, out = _run(capsys, graph_data_dir, "evidence", "--out", str(target))
    assert code == 0
    assert target.is_file()
    assert json.loads(out)["wrote"] == str(target)


def test_missing_subcommand_errors(capsys):
    with pytest.raises(SystemExit):
        cli.main([])


def test_a_graph_fault_exits_two_and_emits_the_error_document(
    capsys, graph_data_dir, monkeypatch
) -> None:
    """THREE EXIT CODES, THREE MEANINGS, and the third had never run.

    ``0`` is an answer, ``1`` is "no such node" — a real answer about a graph that WAS read —
    and ``2`` is a graph fault: something in the graph layer refused. Collapsing the last two
    would make a projection that cannot be built indistinguishable from a node that does not
    exist, and an operator would go looking for an artifact when the projection was the
    problem. The error document is emitted alongside the code so the exit is accompanied by
    its reason rather than by a bare number.
    """

    def refusing(name, core, **kwargs):
        raise ProjectionError("projection could not be built", projection=name)

    monkeypatch.setattr("engine.graph.adapter.build_projection", refusing)

    code, out = _run(capsys, graph_data_dir, "projections")

    assert code == 2
    document = json.loads(out)
    assert document["code"]
    assert "projection could not be built" in document["message"]
