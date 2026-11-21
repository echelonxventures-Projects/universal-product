"""Tests for TASK-000013 relationship graph adapter (EPIC-002)."""

from __future__ import annotations

import pytest

from engine.registry.errors import RegistryValidationError
from engine.registry.graph import RelationshipGraph
from engine.registry.models import Relationship


@pytest.fixture
def graph(source) -> RelationshipGraph:
    return RelationshipGraph.from_source(source)


def test_count_len_iter_all(graph):
    assert graph.count() == 4
    assert len(graph) == 4
    assert len(list(iter(graph))) == 4
    assert len(graph.all()) == 4


def test_edge_lookup(graph):
    assert graph.edge("UEDGE-000000003").type == "Depends-On"
    assert graph.edge("missing") is None


def test_edges_from_and_to(graph):
    out = graph.edges_from("UCOS-ENG-000001")
    assert len(out) == 2
    typed = graph.edges_from("UCOS-ENG-000001", type="Depends-On")
    assert len(typed) == 1
    inbound = graph.edges_to("UCOS-BOOK-000000")
    assert {e.type for e in inbound} == {"Parent"}
    assert graph.edges_to("UCOS-BOOK-000000", type="Child") == ()


def test_edges_of_type(graph):
    assert len(graph.edges_of_type("Parent")) == 2
    assert len(graph.edges_of_type("Depends-On")) == 1


def test_successors_predecessors_neighbors(graph):
    assert set(graph.successors("UCOS-ENG-000001")) == {
        "UCOS-REG-000001",
        "UCOS-BOOK-000000",
    }
    # REG has two inbound edges: BOOK -Child-> REG and ENG -Depends-On-> REG.
    assert set(graph.predecessors("UCOS-REG-000001")) == {
        "UCOS-ENG-000001",
        "UCOS-BOOK-000000",
    }
    assert graph.predecessors("UCOS-REG-000001", type="Depends-On") == ("UCOS-ENG-000001",)
    assert "UCOS-BOOK-000000" in graph.neighbors("UCOS-ENG-000001")
    # REG has both predecessors (BOOK, ENG) and a successor (BOOK), exercising
    # both directions of neighbors().
    assert set(graph.neighbors("UCOS-REG-000001")) == {
        "UCOS-BOOK-000000",
        "UCOS-ENG-000001",
    }


def test_degree_and_has_node_and_nodes(graph):
    assert graph.degree("UCOS-ENG-000001") == 2
    assert graph.has_node("UCOS-BOOK-000000")
    assert not graph.has_node("UCOS-ZZZ-000000")
    assert "UCOS-ENG-000001" in graph.nodes()


def test_types(graph):
    assert graph.types() == ("Child", "Depends-On", "Parent")


def test_dependency_helpers(graph):
    assert graph.dependencies_of("UCOS-ENG-000001") == ("UCOS-REG-000001",)
    assert graph.dependents_of("UCOS-REG-000001") == ("UCOS-ENG-000001",)


def test_parent_child_helpers(graph):
    assert graph.parents_of("UCOS-ENG-000001") == ("UCOS-BOOK-000000",)
    assert graph.children_of("UCOS-BOOK-000000") == ("UCOS-REG-000001",)


def test_duplicate_edge_id_rejected():
    edge = Relationship.from_dict({"edge_id": "UEDGE-1", "from": "A", "to": "B", "type": "Uses"})
    with pytest.raises(RegistryValidationError):
        RelationshipGraph([edge, edge])


def test_real_corpus_graph_loads(real_data_dir):
    from engine.registry.source import RegistrySource

    graph = RelationshipGraph.from_source(RegistrySource(real_data_dir))
    assert graph.count() > 0
    assert "Depends-On" in graph.types()
