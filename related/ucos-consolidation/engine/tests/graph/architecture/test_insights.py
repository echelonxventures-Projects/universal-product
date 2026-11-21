"""Tests for engine.graph.architecture.insights.

Proves: build_insights_report covers all fields; standalone (no pre-built engines)
and with pre-built engines; _findings surfaces inversions, layer cycles,
and circular dependencies.
"""

from __future__ import annotations

from engine.graph.architecture.blast_radius import BlastRadiusEngine
from engine.graph.architecture.critical_path import CriticalPathEngine
from engine.graph.architecture.dependency_intelligence import DependencyIntelligence
from engine.graph.architecture.insights import INSIGHTS_VERSION, build_insights_report
from engine.graph.architecture.layers import LayerDependencyGraph
from engine.graph.model import KIND_ARTIFACT, Edge, KnowledgeGraph, Node


def _artifact(nid: str, category: str = "IMP") -> Node:
    return Node(nid, KIND_ARTIFACT, attributes={"category": category})


def _depends(eid: str, src: str, tgt: str) -> Edge:
    return Edge(eid, src, tgt, "Depends-On")


# --- standalone (no pre-built engines) ----------------------------------------


def test_empty_graph_standalone():
    g = KnowledgeGraph()
    report = build_insights_report(g)
    assert report["insights_version"] == INSIGHTS_VERSION
    assert report["totals"]["artifacts"] == 0
    assert report["totals"]["nodes"] == 0
    assert report["findings"] == []
    assert report["healthy"] is True


def test_simple_graph_standalone():
    nodes = [_artifact(n) for n in ("A", "B", "C")]
    edges = [_depends("E1", "A", "B"), _depends("E2", "B", "C")]
    g = KnowledgeGraph(nodes, edges)
    report = build_insights_report(g)
    assert report["totals"]["artifacts"] == 3
    assert "dependency_intelligence" in report
    assert "layer_intelligence" in report
    assert "circular_dependencies" in report
    assert "critical_path" in report
    assert "blast_radius" in report


def test_report_with_real_corpus(core):
    report = build_insights_report(core)
    assert report["insights_version"] == INSIGHTS_VERSION
    assert report["totals"]["artifacts"] >= 0


# --- with pre-built engines ---------------------------------------------------


def test_with_prebuilt_engines(core):
    dependency = DependencyIntelligence(core)
    layers = LayerDependencyGraph(core)
    critical = CriticalPathEngine(core)
    blast = BlastRadiusEngine(core, layers=layers)
    report = build_insights_report(
        core,
        dependency=dependency,
        layers=layers,
        critical=critical,
        blast=blast,
        limit=5,
    )
    assert report["insights_version"] == INSIGHTS_VERSION
    assert isinstance(report["findings"], list)


# --- _findings (layer inversions, cycles, circular) ---------------------------


def test_findings_layer_inversion():
    # CON (constitution layer) depends on IMP (implementation layer)
    # => that is an inversion (higher layer depending on lower)
    nodes = [
        _artifact("CON-1", "CON"),
        _artifact("IMP-1", "IMP"),
    ]
    # IMP at greater depth than CON → CON Depends-On IMP = inversion
    edges = [_depends("E1", "CON-1", "IMP-1")]
    g = KnowledgeGraph(nodes, edges)
    report = build_insights_report(g)
    # There should be at least a layer_inversion finding
    kinds = [f["kind"] for f in report["findings"]]
    assert "layer_inversion" in kinds


def test_findings_circular_dependency():
    nodes = [_artifact(n) for n in ("X", "Y")]
    edges = [_depends("E1", "X", "Y"), _depends("E2", "Y", "X")]
    g = KnowledgeGraph(nodes, edges)
    report = build_insights_report(g)
    kinds = [f["kind"] for f in report["findings"]]
    assert "circular_dependency" in kinds
    assert report["healthy"] is False


def test_findings_sorted_by_kind_then_detail():
    nodes = [_artifact(n) for n in ("X", "Y")]
    edges = [_depends("E1", "X", "Y"), _depends("E2", "Y", "X")]
    g = KnowledgeGraph(nodes, edges)
    report = build_insights_report(g)
    kinds = [f["kind"] for f in report["findings"]]
    assert kinds == sorted(kinds)


# --- blast_radius section of report -------------------------------------------


def test_blast_radius_section_present():
    nodes = [_artifact(n) for n in ("A", "B")]
    edges = [_depends("E1", "A", "B")]
    g = KnowledgeGraph(nodes, edges)
    report = build_insights_report(g, limit=5)
    br = report["blast_radius"]
    assert "impactable_nodes" in br
    assert "top" in br


def test_findings_layer_cycle():
    """A CYCLE BETWEEN LAYERS IS NOT THE SAME FINDING AS A CYCLE BETWEEN ARTIFACTS.

    ``layer_inversion`` says one layer depends upward on another; ``circular_dependency``
    says two artifacts depend on each other. ``layer_cycle`` is the third thing: two LAYERS
    that each depend on the other, which no single inversion describes and no artifact cycle
    implies. Its loop had never run, because the fixtures produce inversions and artifact
    cycles but never a mutual layer dependency.
    """
    nodes = [
        _artifact("CON-1", "CON"),
        _artifact("IMP-1", "IMP"),
    ]
    edges = [
        _depends("E1", "CON-1", "IMP-1"),
        _depends("E2", "IMP-1", "CON-1"),
    ]
    report = build_insights_report(KnowledgeGraph(nodes, edges))
    kinds = [f["kind"] for f in report["findings"]]

    assert "layer_cycle" in kinds
    detail = next(f["detail"] for f in report["findings"] if f["kind"] == "layer_cycle")
    assert isinstance(detail, list) and detail
