"""Tests for engine.graph.architecture.visualization.

Proves: ArchitectureModel renders JSON/Mermaid/DOT correctly; invalid format
raises ValueError; layer_diagram, capability_diagram, condensation_diagram
build correct models; _dot_escape handles special chars.
"""

from __future__ import annotations

import json

import pytest

from engine.graph.architecture.dependency_intelligence import CapabilityDependencyGraph
from engine.graph.architecture.layers import LayerDependencyGraph
from engine.graph.architecture.visualization import (
    VISUALIZATION_FORMATS,
    ArchitectureModel,
    ModelEdge,
    ModelNode,
    capability_diagram,
    condensation_diagram,
    layer_diagram,
)
from engine.graph.model import KIND_ARTIFACT, Edge, KnowledgeGraph, Node


def _artifact(nid: str, category: str = "IMP") -> Node:
    return Node(nid, KIND_ARTIFACT, attributes={"category": category})


def _depends(eid: str, src: str, tgt: str) -> Edge:
    return Edge(eid, src, tgt, "Depends-On")


def _consumes(eid: str, src: str, tgt: str) -> Edge:
    return Edge(eid, src, tgt, "Consumes")


def _simple_model() -> ArchitectureModel:
    nodes = (ModelNode("n1", "Node One"), ModelNode("n2", "Node Two"))
    edges = (ModelEdge("n1", "n2", weight=3, flag="INVERSION"),)
    return ArchitectureModel(name="test-model", nodes=nodes, edges=edges)


# --- VISUALIZATION_FORMATS -----------------------------------------------------


def test_formats_tuple():
    assert "json" in VISUALIZATION_FORMATS
    assert "mermaid" in VISUALIZATION_FORMATS
    assert "dot" in VISUALIZATION_FORMATS


# --- ArchitectureModel.to_json -------------------------------------------------


def test_to_json_valid():
    model = _simple_model()
    doc = json.loads(model.to_json())
    assert doc["name"] == "test-model"
    assert len(doc["nodes"]) == 2
    assert len(doc["edges"]) == 1
    assert doc["edges"][0]["weight"] == 3
    assert doc["edges"][0]["flag"] == "INVERSION"


def test_to_json_no_indent():
    model = _simple_model()
    raw = model.to_json(indent=None)
    assert "\n" not in raw


# --- ArchitectureModel.to_mermaid ----------------------------------------------


def test_to_mermaid_default_direction():
    model = _simple_model()
    mermaid = model.to_mermaid()
    assert mermaid.startswith("flowchart TB")
    assert "n0" in mermaid
    assert "n1" in mermaid
    assert "INVERSION" in mermaid


def test_to_mermaid_custom_direction():
    model = _simple_model()
    mermaid = model.to_mermaid(direction="LR")
    assert mermaid.startswith("flowchart LR")


def test_to_mermaid_invalid_direction_defaults_to_tb():
    model = _simple_model()
    mermaid = model.to_mermaid(direction="INVALID")
    assert mermaid.startswith("flowchart TB")


def test_to_mermaid_empty_model():
    model = ArchitectureModel("empty", nodes=(), edges=())
    mermaid = model.to_mermaid()
    assert "flowchart" in mermaid


def test_to_mermaid_edge_skipped_for_missing_node():
    nodes = (ModelNode("n1", "One"),)
    edges = (ModelEdge("n1", "GHOST"),)
    model = ArchitectureModel("m", nodes=nodes, edges=edges)
    mermaid = model.to_mermaid()
    assert "-->" not in mermaid


# --- ArchitectureModel.to_dot --------------------------------------------------


def test_to_dot_valid():
    model = _simple_model()
    dot = model.to_dot()
    assert 'digraph "test-model"' in dot
    assert "n1" in dot
    assert "n2" in dot
    assert "INVERSION" in dot


def test_to_dot_edge_with_flag_is_red():
    model = _simple_model()
    dot = model.to_dot()
    assert 'color="red"' in dot


def test_to_dot_edge_without_flag_no_red():
    nodes = (ModelNode("a", "A"), ModelNode("b", "B"))
    edges = (ModelEdge("a", "b", weight=1, flag=""),)
    model = ArchitectureModel("plain", nodes=nodes, edges=edges)
    dot = model.to_dot()
    assert 'color="red"' not in dot


def test_to_dot_escapes_special_chars():
    nodes = (ModelNode('a"b', 'Lab"el'),)
    model = ArchitectureModel('dia"gram', nodes=nodes, edges=())
    dot = model.to_dot()
    assert '\\"' in dot


# --- ArchitectureModel.render --------------------------------------------------


def test_render_json():
    model = _simple_model()
    out = model.render("json")
    assert json.loads(out)["name"] == "test-model"


def test_render_mermaid():
    model = _simple_model()
    out = model.render("mermaid")
    assert "flowchart" in out


def test_render_dot():
    model = _simple_model()
    out = model.render("dot")
    assert "digraph" in out


def test_render_unknown_format_raises():
    model = _simple_model()
    with pytest.raises(ValueError, match="unknown visualization format"):
        model.render("xml")


# --- layer_diagram -------------------------------------------------------------


def test_layer_diagram_empty_graph():
    g = KnowledgeGraph()
    layers = LayerDependencyGraph(g)
    model = layer_diagram(layers)
    assert model.name == "layer-dependency"
    assert isinstance(model.nodes, tuple)
    assert isinstance(model.edges, tuple)


def test_layer_diagram_with_artifacts(core):
    layers = LayerDependencyGraph(core)
    model = layer_diagram(layers)
    assert model.name == "layer-dependency"
    for node in model.nodes:
        assert isinstance(node.meta.get("members"), int)


# --- capability_diagram --------------------------------------------------------


def test_capability_diagram_empty_graph():
    g = KnowledgeGraph()
    cdg = CapabilityDependencyGraph(g)
    model = capability_diagram(cdg)
    assert model.name == "capability-dependency"
    assert model.nodes == ()
    assert model.edges == ()


def test_capability_diagram_with_edges():
    nodes = [Node(n, KIND_ARTIFACT) for n in ("A", "B", "C")]
    edges = [_consumes("E1", "A", "B"), _consumes("E2", "A", "C")]
    g = KnowledgeGraph(nodes, edges)
    cdg = CapabilityDependencyGraph(g)
    model = capability_diagram(cdg)
    node_ids = {n.node_id for n in model.nodes}
    assert "A" in node_ids and "B" in node_ids and "C" in node_ids
    assert len(model.edges) == 2


# --- condensation_diagram ------------------------------------------------------


def test_condensation_diagram_empty_graph():
    g = KnowledgeGraph()
    model = condensation_diagram(g)
    assert model.name == "dependency-condensation"
    assert model.nodes == ()
    assert model.edges == ()


def test_condensation_diagram_acyclic(core):
    model = condensation_diagram(core)
    assert model.name == "dependency-condensation"
    for node in model.nodes:
        assert isinstance(node.meta.get("size"), int)


def test_condensation_diagram_cyclic():
    nodes = [Node(n, KIND_ARTIFACT) for n in ("X", "Y")]
    edges = [_depends("E1", "X", "Y"), _depends("E2", "Y", "X")]
    g = KnowledgeGraph(nodes, edges)
    model = condensation_diagram(g)
    cyclic_nodes = [n for n in model.nodes if n.meta.get("cyclic")]
    assert len(cyclic_nodes) >= 1
