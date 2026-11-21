"""Unit tests for engine.graph.validation — mission-invariant checks."""

from __future__ import annotations

from engine.graph.model import Edge, KnowledgeGraph, Node
from engine.graph.validation import validate_graph


def test_valid_graph_report(core):
    report = validate_graph(core)
    assert report.is_valid is True
    assert report.duplicate_node_ids == ()
    assert report.malformed_node_ids == ()
    assert report.malformed_edge_ids == ()
    assert report.unversioned_artifacts == ()
    assert report.node_count == core.order()
    assert report.dependency_cycle == ()  # sample substrate is acyclic
    d = report.to_dict()
    assert d["is_valid"] is True


def test_malformed_identifiers_flagged():
    # a node with a non-immutable-looking id, and an artifact missing a version
    graph = KnowledgeGraph(
        nodes=[Node("weird id", "Artifact", version="1.0.0"), Node("A", "Artifact", version="")],
        edges=[Edge("not an edge id", "weird id", "A", "Depends-On")],
    )
    report = validate_graph(graph)
    assert "weird id" in report.malformed_node_ids
    assert "not an edge id" in report.malformed_edge_ids
    assert "A" in report.unversioned_artifacts
    assert report.is_valid is False


def test_dangling_endpoint_is_finding_not_failure():
    # edge points at a node that is not registered -> reported, but still valid
    graph = KnowledgeGraph(nodes=[Node("UCOS-A-000001", "Artifact", version="1.0.0")])
    graph.add_edge(Edge("UEDGE-000000001", "UCOS-A-000001", "UCOS-GHOST-000002", "Depends-On"))
    report = validate_graph(graph)
    assert "UCOS-GHOST-000002" in report.dangling_edge_endpoints
    assert report.is_valid is True  # dangling endpoints are findings


def test_dependency_cycle_fails_validity():
    """A reported Depends-On cycle FAILS validity — CEP-009 Art XV.2 (fail-closed).

    Negative path of the dependency gate (UCCEP-F-003 / WP-UCCEP-003 T-2): the
    cycle is reported *and* it invalidates the graph, so every caller of
    ``is_valid`` (CLI exit code, evidence ``operational``, CK-GRAPH) fails closed.
    """
    graph = KnowledgeGraph(
        nodes=[
            Node("UCOS-A-000001", "Artifact", version="1"),
            Node("UCOS-B-000002", "Artifact", version="1"),
        ],
        edges=[
            Edge("UEDGE-000000001", "UCOS-A-000001", "UCOS-B-000002", "Depends-On"),
            Edge("UEDGE-000000002", "UCOS-B-000002", "UCOS-A-000001", "Depends-On"),
        ],
    )
    report = validate_graph(graph)
    assert report.dependency_cycle  # a cycle was found and reported
    assert report.is_valid is False  # ... and it fails the mission invariants
    assert report.to_dict()["is_valid"] is False


def test_dependency_cycle_verdict_is_deterministic():
    """Repeated validation of the same substrate yields a byte-identical verdict."""
    graph = KnowledgeGraph(
        nodes=[
            Node("UCOS-A-000001", "Artifact", version="1"),
            Node("UCOS-B-000002", "Artifact", version="1"),
        ],
        edges=[
            Edge("UEDGE-000000001", "UCOS-A-000001", "UCOS-B-000002", "Depends-On"),
            Edge("UEDGE-000000002", "UCOS-B-000002", "UCOS-A-000001", "Depends-On"),
        ],
    )
    first = validate_graph(graph).to_dict()
    assert first == validate_graph(graph).to_dict()
    assert first == validate_graph(graph).to_dict()


def test_acyclic_dependency_chain_passes_validity():
    """Positive path: the same two artifacts in a single direction remain valid."""
    graph = KnowledgeGraph(
        nodes=[
            Node("UCOS-A-000001", "Artifact", version="1"),
            Node("UCOS-B-000002", "Artifact", version="1"),
        ],
        edges=[
            Edge("UEDGE-000000001", "UCOS-A-000001", "UCOS-B-000002", "Depends-On"),
        ],
    )
    report = validate_graph(graph)
    assert report.dependency_cycle == ()
    assert report.is_valid is True


def test_cycle_unasserted_when_acyclicity_not_required():
    """Opting out leaves the invariant unasserted rather than silently passing it."""
    graph = KnowledgeGraph(
        nodes=[
            Node("UCOS-A-000001", "Artifact", version="1"),
            Node("UCOS-B-000002", "Artifact", version="1"),
        ],
        edges=[
            Edge("UEDGE-000000001", "UCOS-A-000001", "UCOS-B-000002", "Depends-On"),
            Edge("UEDGE-000000002", "UCOS-B-000002", "UCOS-A-000001", "Depends-On"),
        ],
    )
    report = validate_graph(graph, require_acyclic_dependencies=False)
    assert report.dependency_cycle == ()
    assert report.is_valid is True


def test_synthetic_and_registry_identifiers_accepted():
    graph = KnowledgeGraph(
        nodes=[
            Node("CATEGORY::REG", "Category", version=""),
            Node("VOL-000", "Volume", version=""),
            Node("USIG-000000001", "Signal", version=""),
        ],
        edges=[
            Edge(
                "KGE::Of-Category::UCOS-A-000001=>CATEGORY::REG",
                "VOL-000",
                "CATEGORY::REG",
                "X",
            )
        ],
    )
    report = validate_graph(graph, require_acyclic_dependencies=False)
    assert report.malformed_node_ids == ()
    assert report.malformed_edge_ids == ()


def test_a_graph_holding_one_identifier_twice_reports_it_as_a_duplicate():
    """IDENTITY IS THE ONE THING A GRAPH CANNOT HAVE TWO OF.

    ``add_node`` refuses a conflicting re-add, so a graph built through it can never hold a
    duplicate — which is why this arm was dead. It is the check for a graph assembled another
    way: rehydrated from a document, or built by a projection that appended the same node
    twice. Two nodes under one id make every lookup answer arbitrarily, and the report names
    the id so the collision can be found rather than merely counted.
    """

    graph = KnowledgeGraph()
    node = Node("UCOS-TEST-000001", "artifact", version="1.0.0")
    graph.add_node(node)
    graph._nodes["UCOS-DUPLICATE-KEY"] = node  # noqa: SLF001 - deliberate corruption

    report = validate_graph(graph)
    assert "UCOS-TEST-000001" in report.to_dict().get("duplicate_node_ids", []) or any(
        "UCOS-TEST-000001" in str(v) for v in report.to_dict().values()
    )
