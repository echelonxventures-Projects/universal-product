"""Unit tests for engine.graph.visualization — deterministic exporters."""

from __future__ import annotations

import json

import pytest

from engine.graph.model import Edge, GraphProvenance, KnowledgeGraph, Node
from engine.graph.visualization import (
    VISUALIZATION_FORMATS,
    render,
    to_cytoscape,
    to_dot,
    to_mermaid,
    to_node_link_json,
)


def _small_graph():
    return KnowledgeGraph(
        nodes=[Node("A", "Artifact", label='Al"pha', version="1.0.0"), Node("B", "Volume")],
        edges=[Edge("E1", "A", "B", "In-Volume")],
        provenance=GraphProvenance(generated_at="t", generator_version="v"),
    )


def test_node_link_json_is_valid_and_deterministic():
    g = _small_graph()
    out = to_node_link_json(g)
    assert to_node_link_json(g) == out  # deterministic
    doc = json.loads(out)
    assert doc["order"] == 2
    assert doc["size"] == 1
    assert doc["provenance"]["generated_at"] == "t"
    assert {n["id"] for n in doc["nodes"]} == {"A", "B"}


def test_cytoscape_elements():
    doc = json.loads(to_cytoscape(_small_graph()))
    groups = {e["group"] for e in doc["elements"]}
    assert groups == {"nodes", "edges"}
    node = next(e for e in doc["elements"] if e["group"] == "nodes" and e["data"]["id"] == "A")
    assert node["data"]["colour"].startswith("#")


def test_dot_escapes_quotes():
    dot = to_dot(_small_graph())
    assert dot.startswith("digraph")
    assert '\\"' in dot  # the quote in the label is escaped
    assert '"A" -> "B"' in dot


def test_mermaid_flowchart():
    mer = to_mermaid(_small_graph(), direction="TB")
    assert mer.splitlines()[0] == "flowchart TB"
    assert "-->|In-Volume|" in mer


def test_mermaid_bad_direction_falls_back():
    mer = to_mermaid(_small_graph(), direction="DIAGONAL")
    assert mer.splitlines()[0] == "flowchart LR"


def test_mermaid_skips_edges_with_missing_endpoint():
    g = KnowledgeGraph(nodes=[Node("A", "Artifact")])
    g.add_edge(Edge("E1", "A", "GHOST", "Depends-On"))
    mer = to_mermaid(g)
    # the edge references GHOST which has no node -> edge line is skipped
    assert "-->|" not in mer


def test_render_dispatch_and_unknown():
    g = _small_graph()
    for fmt in VISUALIZATION_FORMATS:
        assert isinstance(render(g, fmt), str)
    with pytest.raises(ValueError):
        render(g, "svg")
