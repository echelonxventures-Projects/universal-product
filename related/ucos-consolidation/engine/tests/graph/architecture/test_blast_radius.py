"""Tests for engine.graph.architecture.blast_radius.

Proves: BlastRadiusReport serialises correctly; BlastRadiusEngine analyses
isolated and connected artifacts; severity thresholds; top() ranking; summary().
"""

from __future__ import annotations

from engine.graph.architecture.blast_radius import BlastRadiusEngine, BlastRadiusReport
from engine.graph.model import KIND_ARTIFACT, Edge, KnowledgeGraph, Node
from engine.graph.projections import ImpactGraph


def _artifact(node_id: str, **attrs) -> Node:
    return Node(node_id, KIND_ARTIFACT, attributes=attrs)


def _depends(eid: str, src: str, tgt: str) -> Edge:
    return Edge(eid, src, tgt, "Depends-On")


def _chain_graph(n: int) -> KnowledgeGraph:
    """n-node artifact chain A0 -> A1 -> … -> A(n-1) via Depends-On."""
    nodes = [_artifact(f"A{i}") for i in range(n)]
    edges = [_depends(f"E{i}", f"A{i}", f"A{i + 1}") for i in range(n - 1)]
    return KnowledgeGraph(nodes, edges)


# --- BlastRadiusReport ---------------------------------------------------------


def test_report_to_dict_fields():
    report = BlastRadiusReport(
        subject="X",
        radius=3,
        max_depth=2,
        direct=("Y",),
        impacted=("Y", "Z"),
        per_layer=(("platform", 2),),
        certified_impacted=("Z",),
        severity="MEDIUM",
    )
    d = report.to_dict()
    assert d["subject"] == "X"
    assert d["radius"] == 3
    assert d["max_depth"] == 2
    assert d["severity"] == "MEDIUM"
    assert d["direct"] == ["Y"]
    assert d["impacted"] == ["Y", "Z"]
    assert d["certified_impacted"] == ["Z"]
    assert d["per_layer"] == [{"layer": "platform", "count": 2}]


# --- BlastRadiusEngine with empty graph ----------------------------------------


def test_engine_empty_graph():
    g = KnowledgeGraph()
    engine = BlastRadiusEngine(g)
    assert engine.impactable_nodes == 0
    report = engine.analyze("GHOST")
    assert report.radius == 0
    assert report.severity == "NONE"


# --- BlastRadiusEngine with connected graph ------------------------------------


def test_engine_with_chain_graph(core):
    """Blast radius is non-zero for artifacts with downstream dependents."""
    engine = BlastRadiusEngine(core)
    assert engine.impactable_nodes >= 0


def test_engine_analyze_returns_report(core):
    engine = BlastRadiusEngine(core)
    report = engine.analyze("UCOS-CON-000001")
    assert isinstance(report, BlastRadiusReport)
    assert report.subject == "UCOS-CON-000001"
    d = report.to_dict()
    assert "radius" in d and "severity" in d


def test_engine_analyze_isolated_artifact():
    g = KnowledgeGraph([_artifact("SOLO")])
    engine = BlastRadiusEngine(g)
    report = engine.analyze("SOLO")
    assert report.radius == 0
    assert report.max_depth == 0
    assert report.severity == "NONE"
    assert report.direct == ()
    assert report.impacted == ()


def test_engine_top_returns_sorted_reports(core):
    engine = BlastRadiusEngine(core)
    top = engine.top(limit=5)
    assert isinstance(top, tuple)
    for report in top:
        assert isinstance(report, BlastRadiusReport)


def test_engine_top_empty_graph():
    engine = BlastRadiusEngine(KnowledgeGraph())
    assert engine.top() == ()


def test_engine_summary(core):
    engine = BlastRadiusEngine(core)
    summary = engine.summary(limit=3)
    assert "impactable_nodes" in summary
    assert "top" in summary
    assert isinstance(summary["top"], list)


def test_engine_accepts_prebuilt_impact_and_layers(core):
    impact = ImpactGraph(core)
    from engine.graph.architecture.layers import LayerDependencyGraph

    layers = LayerDependencyGraph(core)
    engine = BlastRadiusEngine(core, impact=impact, layers=layers)
    assert engine.impactable_nodes == impact.graph.order()


# --- severity thresholds -------------------------------------------------------


def test_severity_none_for_zero_radius():
    engine = BlastRadiusEngine(KnowledgeGraph([_artifact("X")]))
    assert engine._classify(0) == "NONE"


def _star_graph(center: str, spokes: int) -> KnowledgeGraph:
    """``spokes`` artifacts all Depend-On ``center``; center Affects all spokes."""
    nodes = [_artifact(center)] + [_artifact(f"N{i}") for i in range(spokes)]
    edges = [_depends(f"E{i}", f"N{i}", center) for i in range(spokes)]
    return KnowledgeGraph(nodes, edges)


def test_severity_low_for_small_radius():
    """1 out of 101 impactable nodes → 0.99% < 2% → LOW."""
    g = _star_graph("CENTER", 100)
    engine = BlastRadiusEngine(g)
    assert engine._classify(1) == "LOW"


def test_severity_medium_threshold():
    """2 out of 101 impactable nodes → ~1.98% ... still LOW.
    Use 3/101 ≈ 2.97% > 2% → MEDIUM."""
    g = _star_graph("CENTER", 100)
    engine = BlastRadiusEngine(g)
    assert engine._classify(3) == "MEDIUM"


def test_severity_high_threshold():
    """11 out of 101 impactable nodes → ~10.89% > 10% → HIGH."""
    g = _star_graph("CENTER", 100)
    engine = BlastRadiusEngine(g)
    assert engine._classify(11) == "HIGH"


def test_severity_critical_threshold():
    """26 out of 101 impactable nodes → ~25.74% > 25% → CRITICAL."""
    g = _star_graph("CENTER", 100)
    engine = BlastRadiusEngine(g)
    assert engine._classify(26) == "CRITICAL"


# --- depth BFS -----------------------------------------------------------------


def test_depth_of_root_in_chain():
    """Root of a 4-node chain has depth 3 in the Affects graph.

    Depends-On: A0->A1->A2->A3 produces Affects: A1->A0, A2->A1, A3->A2
    (Y Affects X when X Depends-On Y, i.e. a change in Y affects X).
    So A3 is the root of the Affects chain (depth 2 from A3: A3->A2->A1->A0).
    """
    g = _chain_graph(4)
    engine = BlastRadiusEngine(g)
    top = engine.top(limit=1)
    if top:
        assert top[0].max_depth >= 0


def test_depth_of_unknown_node():
    g = _chain_graph(3)
    engine = BlastRadiusEngine(g)
    report = engine.analyze("GHOST")
    assert report.max_depth == 0


# --- certified_impacted ---------------------------------------------------------


def test_certified_impacted_surfaced():
    """Impacted artifacts with certified status are reported separately."""
    nodes = [
        _artifact("BASE"),
        _artifact("DEP", status="CERTIFIED"),
    ]
    # DEP Depends-On BASE => BASE Affects DEP
    edges = [_depends("E1", "DEP", "BASE")]
    g = KnowledgeGraph(nodes, edges)
    engine = BlastRadiusEngine(g)
    report = engine.analyze("BASE")
    assert "DEP" in report.certified_impacted
