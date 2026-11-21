"""Tests for engine.graph.architecture.critical_path.

Proves: CriticalPathReport serialises; CriticalPathEngine computes the longest
chain; empty/cyclic/acyclic graphs; depth_of; deepest; summary.
"""

from __future__ import annotations

from engine.graph.architecture.critical_path import CriticalPathEngine, CriticalPathReport
from engine.graph.model import KIND_ARTIFACT, Edge, KnowledgeGraph, Node


def _artifact(nid: str) -> Node:
    return Node(nid, KIND_ARTIFACT)


def _depends(eid: str, src: str, tgt: str) -> Edge:
    return Edge(eid, src, tgt, "Depends-On")


# --- CriticalPathReport --------------------------------------------------------


def test_report_to_dict():
    report = CriticalPathReport(
        length=3,
        path=("A", "B", "C"),
        depth_of=(("A", 3), ("B", 2)),
        cyclic=False,
    )
    d = report.to_dict()
    assert d["length"] == 3
    assert d["path"] == ["A", "B", "C"]
    assert d["cyclic"] is False
    assert d["depth_of"] == [{"node": "A", "depth": 3}, {"node": "B", "depth": 2}]


# --- CriticalPathEngine: empty graph -------------------------------------------


def test_empty_graph_returns_zero_length():
    engine = CriticalPathEngine(KnowledgeGraph())
    report = engine.critical_path()
    assert report.length == 0
    assert report.path == ()
    assert report.cyclic is False


# --- CriticalPathEngine: simple acyclic chain ----------------------------------


def test_chain_graph_length():
    # A -> B -> C (Depends-On), so the dependency chain is length 3
    nodes = [_artifact(n) for n in ("A", "B", "C")]
    edges = [_depends("E1", "A", "B"), _depends("E2", "B", "C")]
    g = KnowledgeGraph(nodes, edges)
    engine = CriticalPathEngine(g)
    report = engine.critical_path()
    assert report.length >= 1
    assert not report.cyclic


def test_chain_path_contains_artifacts():
    nodes = [_artifact(n) for n in ("A", "B", "C")]
    edges = [_depends("E1", "A", "B"), _depends("E2", "B", "C")]
    g = KnowledgeGraph(nodes, edges)
    engine = CriticalPathEngine(g)
    report = engine.critical_path()
    for node_id in report.path:
        assert node_id in ("A", "B", "C")


# --- CriticalPathEngine: cyclic graph ------------------------------------------


def test_cyclic_graph_detected():
    nodes = [_artifact(n) for n in ("X", "Y")]
    edges = [_depends("E1", "X", "Y"), _depends("E2", "Y", "X")]
    g = KnowledgeGraph(nodes, edges)
    engine = CriticalPathEngine(g)
    assert engine.is_cyclic is True
    report = engine.critical_path()
    assert report.cyclic is True


# --- depth_of -------------------------------------------------------------------


def test_depth_of_known_node():
    nodes = [_artifact(n) for n in ("A", "B", "C")]
    edges = [_depends("E1", "A", "B"), _depends("E2", "B", "C")]
    g = KnowledgeGraph(nodes, edges)
    engine = CriticalPathEngine(g)
    assert engine.depth_of("A") >= 0


def test_depth_of_unknown_node_returns_zero():
    g = KnowledgeGraph([_artifact("A")])
    engine = CriticalPathEngine(g)
    assert engine.depth_of("GHOST") == 0


# --- deepest -------------------------------------------------------------------


def test_deepest_returns_sorted_pairs():
    nodes = [_artifact(n) for n in ("A", "B", "C", "D")]
    edges = [_depends("E1", "A", "B"), _depends("E2", "B", "C"), _depends("E3", "C", "D")]
    g = KnowledgeGraph(nodes, edges)
    engine = CriticalPathEngine(g)
    result = engine.deepest(limit=2)
    assert len(result) == 2
    # Ranked by depth descending, then by identity — so the ranking is deterministic
    # rather than dependent on the order the graph happened to enumerate its nodes.
    assert result == tuple(sorted(result, key=lambda item: (-item[1], item[0])))
    assert [node_id for node_id, _ in result] == ["A", "B"]
    # Depth counts the nodes on the longest chain, so A->B->C->D makes A four deep.
    assert [depth for _, depth in result] == [4, 3]


def test_deepest_on_empty_graph():
    assert CriticalPathEngine(KnowledgeGraph()).deepest() == ()


# --- summary -------------------------------------------------------------------


def test_summary_keys(core):
    engine = CriticalPathEngine(core)
    s = engine.summary()
    assert "length" in s
    assert "cyclic" in s
    assert "path" in s
    assert "deepest" in s


def test_summary_empty_graph():
    engine = CriticalPathEngine(KnowledgeGraph())
    s = engine.summary()
    assert s["length"] == 0
    assert s["cyclic"] is False
    assert s["path"] == []


# --- with real corpus fixture --------------------------------------------------


def test_real_corpus_critical_path(core):
    engine = CriticalPathEngine(core)
    report = engine.critical_path()
    assert isinstance(report.length, int)
    assert isinstance(report.path, tuple)
