"""Tests for engine.graph.architecture.dependency_intelligence.

Proves: CapabilityDependencyGraph direct/transitive/cycles; _closure;
CircularDependencyReport properties; detect_circular_dependencies;
DependencyIntelligence all methods.
"""

from __future__ import annotations

from engine.graph.architecture.dependency_intelligence import (
    CapabilityDependencyGraph,
    CircularDependencyReport,
    DependencyIntelligence,
    _closure,
    detect_circular_dependencies,
)
from engine.graph.model import KIND_ARTIFACT, Edge, KnowledgeGraph, Node


def _artifact(nid: str) -> Node:
    return Node(nid, KIND_ARTIFACT)


def _edge(eid: str, src: str, tgt: str, etype: str) -> Edge:
    return Edge(eid, src, tgt, etype)


def _depends(eid: str, src: str, tgt: str) -> Edge:
    return _edge(eid, src, tgt, "Depends-On")


def _consumes(eid: str, src: str, tgt: str) -> Edge:
    return _edge(eid, src, tgt, "Consumes")


# --- CapabilityDependencyGraph --------------------------------------------------


def test_cap_empty_graph():
    cdg = CapabilityDependencyGraph(KnowledgeGraph())
    assert cdg.consumes("X") == ()
    assert cdg.provides_for("X") == ()
    assert cdg.transitive_consumes("X") == ()
    assert cdg.cycles() == ()


def test_cap_direct_relationships():
    nodes = [_artifact(n) for n in ("A", "B", "C")]
    edges = [_consumes("E1", "A", "B"), _consumes("E2", "A", "C")]
    g = KnowledgeGraph(nodes, edges)
    cdg = CapabilityDependencyGraph(g)
    assert "B" in cdg.consumes("A")
    assert "C" in cdg.consumes("A")
    assert "A" in cdg.provides_for("B")
    assert "A" in cdg.provides_for("C")


def test_cap_transitive_consumes():
    nodes = [_artifact(n) for n in ("A", "B", "C")]
    edges = [_consumes("E1", "A", "B"), _consumes("E2", "B", "C")]
    g = KnowledgeGraph(nodes, edges)
    cdg = CapabilityDependencyGraph(g)
    transitive = cdg.transitive_consumes("A")
    assert "B" in transitive
    assert "C" in transitive


def test_cap_transitive_consumes_unknown_node():
    cdg = CapabilityDependencyGraph(KnowledgeGraph([_artifact("X")]))
    assert cdg.transitive_consumes("GHOST") == ()


def test_cap_cycles_detected():
    nodes = [_artifact(n) for n in ("X", "Y")]
    edges = [_consumes("E1", "X", "Y"), _consumes("E2", "Y", "X")]
    g = KnowledgeGraph(nodes, edges)
    cdg = CapabilityDependencyGraph(g)
    cycles = cdg.cycles()
    assert len(cycles) >= 1


def test_cap_adjacency():
    nodes = [_artifact(n) for n in ("A", "B")]
    edges = [_consumes("E1", "A", "B")]
    g = KnowledgeGraph(nodes, edges)
    cdg = CapabilityDependencyGraph(g)
    adj = cdg.adjacency()
    assert "B" in adj["A"]


def test_cap_summary():
    nodes = [_artifact(n) for n in ("A", "B")]
    edges = [_consumes("E1", "A", "B")]
    g = KnowledgeGraph(nodes, edges)
    cdg = CapabilityDependencyGraph(g)
    s = cdg.summary()
    assert "nodes" in s and "edges" in s and "cycles" in s


# --- CircularDependencyReport --------------------------------------------------


def test_circular_report_no_cycles():
    r = CircularDependencyReport()
    assert not r.has_cycles
    assert r.largest_cycle == ()
    d = r.to_dict()
    assert d["has_cycles"] is False
    assert d["count"]["depends_on"] == 0


def test_circular_report_with_cycles():
    cycle = (("A", "B"),)
    r = CircularDependencyReport(depends_on_cycles=cycle)
    assert r.has_cycles
    assert r.largest_cycle == ("A", "B")


def test_circular_report_largest_cycle_tie_break():
    r = CircularDependencyReport(
        depends_on_cycles=(("A", "B"),),
        capability_cycles=(("X", "Y", "Z"),),
    )
    assert len(r.largest_cycle) == 3


# --- detect_circular_dependencies ----------------------------------------------


def test_detect_acyclic_graph():
    nodes = [_artifact(n) for n in ("A", "B", "C")]
    edges = [_depends("E1", "A", "B"), _depends("E2", "B", "C")]
    g = KnowledgeGraph(nodes, edges)
    report = detect_circular_dependencies(g)
    assert not report.has_cycles


def test_detect_depends_on_cycle():
    nodes = [_artifact(n) for n in ("X", "Y")]
    edges = [_depends("E1", "X", "Y"), _depends("E2", "Y", "X")]
    g = KnowledgeGraph(nodes, edges)
    report = detect_circular_dependencies(g)
    assert report.has_cycles
    assert len(report.depends_on_cycles) >= 1


def test_detect_combined_cycle():
    """Cycle only visible when Depends-On and Consumes are unioned."""
    nodes = [_artifact(n) for n in ("A", "B")]
    edges = [_depends("E1", "A", "B"), _consumes("E2", "B", "A")]
    g = KnowledgeGraph(nodes, edges)
    report = detect_circular_dependencies(g)
    assert report.has_cycles


# --- DependencyIntelligence ----------------------------------------------------


def test_dep_intel_dependencies_of():
    nodes = [_artifact(n) for n in ("A", "B", "C")]
    edges = [_depends("E1", "A", "B"), _depends("E2", "A", "C")]
    g = KnowledgeGraph(nodes, edges)
    di = DependencyIntelligence(g)
    deps = di.dependencies_of("A")
    assert "B" in deps and "C" in deps


def test_dep_intel_dependencies_of_unknown():
    di = DependencyIntelligence(KnowledgeGraph([_artifact("X")]))
    assert di.dependencies_of("GHOST") == ()


def test_dep_intel_transitive_dependencies():
    nodes = [_artifact(n) for n in ("A", "B", "C")]
    edges = [_depends("E1", "A", "B"), _depends("E2", "B", "C")]
    g = KnowledgeGraph(nodes, edges)
    di = DependencyIntelligence(g)
    transitive = di.transitive_dependencies("A")
    assert "C" in transitive


def test_dep_intel_transitive_unknown():
    di = DependencyIntelligence(KnowledgeGraph([_artifact("X")]))
    assert di.transitive_dependencies("GHOST") == ()


def test_dep_intel_circular_memoised():
    g = KnowledgeGraph([_artifact("A"), _artifact("B")], [_depends("E1", "A", "B")])
    di = DependencyIntelligence(g)
    r1 = di.circular()
    r2 = di.circular()
    assert r1 is r2


def test_dep_intel_fan_in_and_out():
    nodes = [_artifact(n) for n in ("A", "B", "C")]
    edges = [_depends("E1", "A", "B"), _depends("E2", "C", "B")]
    g = KnowledgeGraph(nodes, edges)
    di = DependencyIntelligence(g)
    assert di.fan_in("B") == 2
    assert di.fan_out("A") == 1
    assert di.fan_out("B") == 0


def test_dep_intel_hubs():
    nodes = [_artifact(n) for n in ("A", "B", "C", "D")]
    edges = [_depends(f"E{i}", n, "A") for i, n in enumerate(("B", "C", "D"))]
    g = KnowledgeGraph(nodes, edges)
    di = DependencyIntelligence(g)
    hubs = di.hubs(limit=5)
    assert hubs[0][0] == "A"
    assert hubs[0][1] == 3


def test_dep_intel_capability_property():
    g = KnowledgeGraph([_artifact("X")])
    di = DependencyIntelligence(g)
    assert isinstance(di.capability, CapabilityDependencyGraph)


def test_dep_intel_summary(core):
    di = DependencyIntelligence(core)
    s = di.summary()
    assert "depends_on" in s
    assert "capability" in s
    assert "circular" in s
    assert "top_hubs" in s


def test_the_transitive_closure_visits_a_diamond_once_and_never_returns_to_its_origin():
    """TWO GUARDS, TWO DIFFERENT NON-TERMINATIONS, and an acyclic tree trips neither.

    ``current in seen`` stops a DIAMOND from being expanded once per route into it — the
    answer is the same either way, which is exactly why the guard is invisible until a graph
    offers a second path. ``current == start`` stops a CYCLE from putting the origin into its
    own closure, which would make every capability in a cycle report itself as one of its own
    transitive dependencies.
    """

    adjacency = {
        "A": ("B", "C"),
        "B": ("D",),
        "C": ("D",),
        "D": ("A",),
    }
    reached = _closure(adjacency, "A")

    assert reached == ("B", "C", "D")
    assert "A" not in reached
