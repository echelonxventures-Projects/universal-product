"""Unit tests for engine.graph.queries — traversal algorithms."""

from __future__ import annotations

import pytest

from engine.graph import queries
from engine.graph.model import Edge, KnowledgeGraph, Node


def _chain_graph():
    # A -> B -> C -> D (Depends-On), plus a side Consumes A -> D
    nodes = [Node(x, "Artifact") for x in ("A", "B", "C", "D")]
    edges = [
        Edge("E1", "A", "B", "Depends-On"),
        Edge("E2", "B", "C", "Depends-On"),
        Edge("E3", "C", "D", "Depends-On"),
        Edge("E4", "A", "D", "Consumes"),
    ]
    return KnowledgeGraph(nodes, edges)


def test_breadth_first_and_closures():
    g = _chain_graph()
    assert queries.breadth_first(g, "A", types=["Depends-On"]) == ("B", "C", "D")
    assert queries.descendants(g, "A", types=["Depends-On"]) == ("B", "C", "D")
    assert queries.ancestors(g, "D", types=["Depends-On"]) == ("C", "B", "A")
    # unfiltered includes the Consumes edge target too
    assert set(queries.descendants(g, "A")) == {"B", "C", "D"}


def test_shortest_path_variants():
    g = _chain_graph()
    assert queries.shortest_path(g, "A", "A") == ("A",)
    assert queries.shortest_path(g, "A", "D", types=["Depends-On"]) == ("A", "B", "C", "D")
    # with Consumes allowed, the direct A->D shortcut wins
    assert queries.shortest_path(g, "A", "D") == ("A", "D")
    assert queries.shortest_path(g, "D", "A") == ()  # unreachable forward
    assert queries.has_path(g, "A", "D") is True
    assert queries.has_path(g, "D", "A") is False


def test_topological_order_and_acyclic():
    g = _chain_graph()
    order = queries.topological_order(g, types=["Depends-On"])
    assert order.index("A") < order.index("B") < order.index("C") < order.index("D")
    assert queries.is_acyclic(g, types=["Depends-On"]) is True


def test_cycle_detection():
    nodes = [Node(x, "Artifact") for x in ("X", "Y", "Z")]
    edges = [
        Edge("E1", "X", "Y", "Depends-On"),
        Edge("E2", "Y", "Z", "Depends-On"),
        Edge("E3", "Z", "X", "Depends-On"),
    ]
    g = KnowledgeGraph(nodes, edges)
    assert queries.is_acyclic(g, types=["Depends-On"]) is False
    with pytest.raises(ValueError):
        queries.topological_order(g, types=["Depends-On"])
    cycle = queries.find_cycle(g, types=["Depends-On"])
    assert cycle and cycle[0] == cycle[-1]  # closed cycle path
    # acyclic graph -> empty cycle
    assert queries.find_cycle(_chain_graph(), types=["Depends-On"]) == ()


def test_connected_component():
    nodes = [Node(x, "Artifact") for x in ("A", "B", "C", "ISO")]
    edges = [Edge("E1", "A", "B", "Depends-On"), Edge("E2", "B", "C", "Consumes")]
    g = KnowledgeGraph(nodes, edges)
    assert queries.connected_component(g, "A") == ("A", "B", "C")
    assert queries.connected_component(g, "ISO") == ("ISO",)


def test_self_loop_cycle():
    g = KnowledgeGraph(nodes=[Node("A", "Artifact")], edges=[Edge("E", "A", "A", "Depends-On")])
    assert queries.find_cycle(g, types=["Depends-On"]) == ("A", "A")


def test_a_shortest_path_search_does_not_re_enter_a_node_it_has_already_reached():
    """THE VISITED SET IS WHAT MAKES A BREADTH-FIRST SEARCH TERMINATE.

    A diamond — two routes into one node — re-queues that node once per route without the
    guard, and every subsequent level compounds it. On a cycle it never terminates at all.
    The answer is unchanged either way, which is exactly why the guard is invisible until a
    graph gives the search a second way in.
    """
    graph = KnowledgeGraph()
    for node_id in ("UCOS-A-000001", "UCOS-B-000001", "UCOS-C-000001", "UCOS-D-000001"):
        graph.add_node(Node(node_id, "artifact", version="1.0.0"))
    for index, (src, dst) in enumerate(
        (
            ("UCOS-A-000001", "UCOS-B-000001"),
            ("UCOS-A-000001", "UCOS-C-000001"),
            ("UCOS-B-000001", "UCOS-D-000001"),
            ("UCOS-C-000001", "UCOS-D-000001"),
            ("UCOS-D-000001", "UCOS-A-000001"),
        ),
        start=1,
    ):
        graph.add_edge(Edge(f"UCOS-EDGE-{index:06d}", src, dst, "Depends-On"))

    # A goal REACHED THROUGH THE SECOND ROUTE: the search must find D once, not twice.
    path = queries.shortest_path(graph, "UCOS-B-000001", "UCOS-C-000001")
    assert path[0] == "UCOS-B-000001" and path[-1] == "UCOS-C-000001"
    assert len(path) == len(set(path))

    path = queries.shortest_path(graph, "UCOS-A-000001", "UCOS-D-000001")
    assert path[0] == "UCOS-A-000001"
    assert path[-1] == "UCOS-D-000001"
    assert len(path) == len(set(path)), "the search walked a node twice"
    assert len(path) == 3


def test_a_topological_order_ignores_an_edge_whose_endpoint_is_outside_the_subgraph():
    """ORDERING IS OVER THE NODES IT WAS GIVEN, NOT OVER EVERY EDGE THE GRAPH HOLDS.

    An edge can legitimately point outside the node set being ordered — a projection, or an
    ordering restricted to one kind. Counting its in-degree would credit a node that is not
    being ordered, and the ready set would then never include the node that depends on it:
    the order would silently come back short.
    """
    graph = KnowledgeGraph()
    for node_id in ("UCOS-A-000001", "UCOS-B-000001"):
        graph.add_node(Node(node_id, "artifact", version="1.0.0"))
    graph.add_edge(Edge("UCOS-EDGE-000001", "UCOS-A-000001", "UCOS-B-000001", "Depends-On"))
    graph.add_edge(Edge("UCOS-EDGE-000002", "UCOS-OUTSIDE-000001", "UCOS-B-000001", "Depends-On"))

    order = queries.topological_order(graph)
    assert set(order) == {"UCOS-A-000001", "UCOS-B-000001"}
    assert order.index("UCOS-A-000001") < order.index("UCOS-B-000001")
