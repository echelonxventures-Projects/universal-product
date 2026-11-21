"""Tests for engine.knowledge.graph — the Universal Knowledge Graph (Part 05)."""

from __future__ import annotations

import pytest

from engine.knowledge.errors import RelationshipError
from engine.knowledge.graph import KnowledgeEdge, KnowledgeGraph, derive_edges
from engine.knowledge.model import KnowledgeKind, RelationType

from .conftest import make_cko


def test_edge_validation_and_dict():
    edge = KnowledgeEdge("A", "B", RelationType.DEPENDS_ON, "note")
    assert edge.key() == ("A", "B", "depends-on")
    assert edge.to_dict()["type"] == "depends-on"
    assert edge == KnowledgeEdge("A", "B", RelationType.DEPENDS_ON)
    assert hash(edge) == hash(KnowledgeEdge("A", "B", RelationType.DEPENDS_ON))
    with pytest.raises(RelationshipError):
        KnowledgeEdge("", "B", RelationType.DEPENDS_ON)
    with pytest.raises(RelationshipError):
        KnowledgeEdge("A", "B", "depends-on")  # type: ignore[arg-type]


def test_derive_edges_from_topology():
    obj = make_cko(
        "X",
        parent="P",
        children=("C",),
        dependencies=("D",),
        consumers=("K",),
        supersedes=("S",),
        superseded_by="N",
        knowledge_links=("L",),
        decision_links=("DEC",),
    )
    edges = derive_edges(obj)
    kinds = {(e.source, e.target, e.type) for e in edges}
    assert ("X", "P", RelationType.EXTENDS) in kinds
    assert ("C", "X", RelationType.EXTENDS) in kinds
    assert ("X", "D", RelationType.DEPENDS_ON) in kinds
    assert ("K", "X", RelationType.CONSUMES) in kinds
    assert ("X", "S", RelationType.SUPERSEDES) in kinds
    assert ("N", "X", RelationType.SUPERSEDES) in kinds
    assert ("X", "L", RelationType.RELATED_TO) in kinds
    assert ("X", "DEC", RelationType.REFERENCES) in kinds


def test_graph_navigation_and_dedup():
    a = make_cko("A", dependencies=("B",))
    b = make_cko("B", dependencies=("C",))
    c = make_cko("C")
    g = KnowledgeGraph.from_objects([a, b, c])
    assert g.dependencies_of("A") == ("B",)
    assert g.dependents_of("B") == ("A",)
    assert "B" in g.nodes()
    assert RelationType.DEPENDS_ON in g.types()
    assert g.degree("B") == 2
    assert g.has_node("A") and not g.has_node("ZZ")
    assert set(g.neighbors("B")) == {"A", "C"}
    assert g.edges_of_type(RelationType.DEPENDS_ON)
    # transitive impact: change to C affects B then A
    assert set(g.impact_of("C")) == {"A", "B"}
    assert set(g.reachable_from("A")) == {"B", "C"}
    # duplicate edges are collapsed
    dup = KnowledgeGraph([KnowledgeEdge("A", "B", RelationType.DEPENDS_ON)] * 3)
    assert len(dup) == 1
    assert len(g.all()) >= 1
    assert list(iter(g))


def test_conflicts_symmetric():
    a = make_cko("A", knowledge_links=())
    g = KnowledgeGraph([KnowledgeEdge("A", "B", RelationType.CONFLICTS_WITH)])
    assert g.conflicts_of("A") == ("B",)
    assert g.conflicts_of("B") == ("A",)
    assert a.kind is KnowledgeKind.FACT


def test_edges_from_to_type_filter():
    g = KnowledgeGraph(
        [
            KnowledgeEdge("A", "B", RelationType.DEPENDS_ON),
            KnowledgeEdge("A", "C", RelationType.RELATED_TO),
        ]
    )
    assert len(g.edges_from("A")) == 2
    assert len(g.edges_from("A", type=RelationType.DEPENDS_ON)) == 1
    assert len(g.edges_to("B", type=RelationType.DEPENDS_ON)) == 1
    assert g.successors("A", type=RelationType.RELATED_TO) == ("C",)
    assert g.predecessors("C") == ("A",)


def test_a_node_reachable_by_two_routes_is_walked_once():
    """The visited set is what stops a diamond from being traversed twice, and a knowledge
    graph is full of diamonds — two objects depending on one shared foundation is the normal
    shape. Without the guard the walk re-enters the shared node on every route into it, and
    the traversal cost doubles for each additional path rather than the answer changing."""
    graph = KnowledgeGraph.from_objects(
        [
            make_cko("TOP", dependencies=("LEFT", "RIGHT")),
            make_cko("LEFT", dependencies=("SHARED",)),
            make_cko("RIGHT", dependencies=("SHARED",)),
            make_cko("SHARED"),
        ]
    )
    reached = graph.reachable_from("TOP")
    assert sorted(reached) == ["LEFT", "RIGHT", "SHARED"]
    assert len(reached) == len(set(reached)), "a node was walked more than once"
    affected = graph.impact_of("SHARED")
    assert sorted(affected) == ["LEFT", "RIGHT", "TOP"]
    assert len(affected) == len(set(affected))
