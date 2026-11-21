"""Unit tests for engine.graph.architecture.layers.

Proves the layer model's legislated behaviour: every artifact lands in exactly one
layer, the category→layer mapping is deterministic and case-insensitive, unknown
categories fall through to UNCLASSIFIED and are excluded from inversion logic, and
inversions/cycles are surfaced read-only from the artifact Depends-On relation.
"""

from __future__ import annotations

from engine.graph.architecture.layers import (
    LAYER_ORDER,
    UNCLASSIFIED,
    LayerDependency,
    LayerDependencyGraph,
    layer_depth,
    layer_of_category,
)
from engine.graph.model import KIND_ARTIFACT, Edge, KnowledgeGraph, Node


def _artifact(node_id: str, category: str) -> Node:
    return Node(node_id, KIND_ARTIFACT, attributes={"category": category})


def _graph(nodes, edges) -> KnowledgeGraph:
    return KnowledgeGraph(nodes, edges)


def _depends(edge_id: str, source: str, target: str) -> Edge:
    return Edge(edge_id, source, target, "Depends-On")


# --- category / depth mapping ----------------------------------------------------


def test_layer_of_category_maps_the_certified_vocabulary():
    assert layer_of_category("CON") == "constitution"
    assert layer_of_category("ARCH") == "architecture"
    assert layer_of_category("SEC") == "security"


def test_layer_of_category_is_case_insensitive():
    assert layer_of_category("con") == layer_of_category("CON") == "constitution"


def test_layer_of_category_falls_through_to_unclassified():
    assert layer_of_category("NOT-A-CATEGORY") == UNCLASSIFIED
    assert layer_of_category("") == UNCLASSIFIED


def test_layer_depth_follows_the_declared_stack_order():
    assert layer_depth("book") == 0
    assert layer_depth(LAYER_ORDER[-1]) == len(LAYER_ORDER) - 1
    # the stack is strictly increasing in the declared order
    depths = [layer_depth(name) for name in LAYER_ORDER]
    assert depths == sorted(depths)
    assert len(set(depths)) == len(depths)


def test_layer_depth_of_unclassified_is_negative():
    assert layer_depth(UNCLASSIFIED) == -1
    assert layer_depth("nonsense") == -1


# --- classification --------------------------------------------------------------


def test_every_artifact_is_classified_into_exactly_one_layer():
    graph = _graph([_artifact("A", "CON"), _artifact("B", "APP")], [])
    layers = LayerDependencyGraph(graph)
    assert layers.layer_of("A") == "constitution"
    assert layers.layer_of("B") == "application"
    assert layers.members("constitution") == ("A",)
    assert layers.members("application") == ("B",)


def test_layer_of_an_unknown_node_is_empty():
    layers = LayerDependencyGraph(_graph([_artifact("A", "CON")], []))
    assert layers.layer_of("GHOST") == ""


def test_members_are_sorted_and_unknown_layer_is_empty():
    graph = _graph([_artifact("Z", "CON"), _artifact("A", "CON")], [])
    layers = LayerDependencyGraph(graph)
    assert layers.members("constitution") == ("A", "Z")
    assert layers.members("no-such-layer") == ()


def test_layers_lists_only_populated_layers_in_stack_order():
    graph = _graph([_artifact("A", "APP"), _artifact("B", "CON")], [])
    # application is deeper in the stack than constitution, so constitution first
    assert LayerDependencyGraph(graph).layers() == ("constitution", "application")


def test_layers_appends_unclassified_last():
    graph = _graph([_artifact("A", "WEIRD"), _artifact("B", "CON")], [])
    assert LayerDependencyGraph(graph).layers() == ("constitution", UNCLASSIFIED)


def test_graph_with_no_artifacts_has_no_layers():
    layers = LayerDependencyGraph(_graph([], []))
    assert layers.layers() == ()
    assert layers.dependencies() == ()
    assert layers.is_stratified() is True


# --- dependency aggregation ------------------------------------------------------


def test_edges_aggregate_into_weighted_layer_dependencies():
    graph = _graph(
        [
            _artifact("A1", "APP"),
            _artifact("A2", "APP"),
            _artifact("C1", "CON"),
        ],
        [_depends("E1", "A1", "C1"), _depends("E2", "A2", "C1")],
    )
    deps = LayerDependencyGraph(graph).dependencies()
    assert len(deps) == 1
    assert deps[0].source == "application"
    assert deps[0].target == "constitution"
    assert deps[0].weight == 2  # two artifact edges, one layer edge


def test_dependencies_are_ordered_by_source_then_target():
    graph = _graph(
        [_artifact("A", "APP"), _artifact("C", "CON"), _artifact("S", "SVC")],
        [_depends("E1", "S", "C"), _depends("E2", "A", "C")],
    )
    deps = LayerDependencyGraph(graph).dependencies()
    assert [(d.source, d.target) for d in deps] == [
        ("application", "constitution"),
        ("service", "constitution"),
    ]


def test_dependencies_of_returns_only_outbound_edges():
    graph = _graph(
        [_artifact("A", "APP"), _artifact("C", "CON")],
        [_depends("E1", "A", "C")],
    )
    layers = LayerDependencyGraph(graph)
    assert len(layers.dependencies_of("application")) == 1
    assert layers.dependencies_of("constitution") == ()


def test_edges_touching_non_artifact_endpoints_are_ignored():
    # a Depends-On edge into a Volume node has no layer and must not be aggregated
    graph = _graph(
        [_artifact("A", "APP"), Node("VOL-1", "Volume")],
        [_depends("E1", "A", "VOL-1")],
    )
    assert LayerDependencyGraph(graph).dependencies() == ()


def test_non_depends_on_edges_are_ignored():
    graph = _graph(
        [_artifact("A", "APP"), _artifact("C", "CON")],
        [Edge("E1", "A", "C", "Consumes")],
    )
    assert LayerDependencyGraph(graph).dependencies() == ()


# --- inversions ------------------------------------------------------------------


def test_downward_dependency_is_healthy_not_an_inversion():
    # application (deep) -> constitution (shallow) is the intended direction
    graph = _graph(
        [_artifact("A", "APP"), _artifact("C", "CON")],
        [_depends("E1", "A", "C")],
    )
    layers = LayerDependencyGraph(graph)
    assert layers.inversions() == ()
    assert layers.is_stratified() is True


def test_upward_dependency_is_an_inversion():
    # constitution (shallow) -> application (deep) points up the stack
    graph = _graph(
        [_artifact("C", "CON"), _artifact("A", "APP")],
        [_depends("E1", "C", "A")],
    )
    layers = LayerDependencyGraph(graph)
    inversions = layers.inversions()
    assert len(inversions) == 1
    assert (inversions[0].source, inversions[0].target) == ("constitution", "application")
    assert layers.is_stratified() is False


def test_same_layer_dependency_is_never_an_inversion():
    graph = _graph(
        [_artifact("A", "APP"), _artifact("B", "APP")],
        [_depends("E1", "A", "B")],
    )
    layers = LayerDependencyGraph(graph)
    deps = layers.dependencies()
    assert len(deps) == 1
    assert deps[0].source == deps[0].target == "application"
    assert deps[0].inversion is False
    assert layers.inversions() == ()


def test_unclassified_layers_are_excluded_from_inversion_logic():
    # unclassified has no stack position, so neither direction can be an inversion
    graph = _graph(
        [_artifact("U", "WEIRD"), _artifact("C", "CON")],
        [_depends("E1", "U", "C"), _depends("E2", "C", "U")],
    )
    assert LayerDependencyGraph(graph).inversions() == ()


# --- cycles ----------------------------------------------------------------------


def test_layer_cycle_is_detected():
    graph = _graph(
        [_artifact("C", "CON"), _artifact("A", "APP")],
        [_depends("E1", "C", "A"), _depends("E2", "A", "C")],
    )
    layers = LayerDependencyGraph(graph)
    assert layers.cycles() == (("application", "constitution"),)
    assert layers.is_stratified() is False


def test_acyclic_layering_reports_no_cycles():
    graph = _graph(
        [_artifact("A", "APP"), _artifact("C", "CON")],
        [_depends("E1", "A", "C")],
    )
    assert LayerDependencyGraph(graph).cycles() == ()


def test_same_layer_self_edge_is_not_a_layer_cycle():
    # normalise_adjacency drops self-edges, so an intra-layer dependency is healthy
    graph = _graph(
        [_artifact("A", "APP"), _artifact("B", "APP")],
        [_depends("E1", "A", "B")],
    )
    layers = LayerDependencyGraph(graph)
    assert layers.cycles() == ()
    assert layers.is_stratified() is True


# --- projections -----------------------------------------------------------------


def test_layer_dependency_to_dict_round_trips_its_fields():
    dep = LayerDependency(source="application", target="constitution", weight=3, inversion=False)
    assert dep.to_dict() == {
        "source": "application",
        "target": "constitution",
        "weight": 3,
        "inversion": False,
    }


def test_summary_is_deterministic_and_complete():
    graph = _graph(
        [_artifact("C", "CON"), _artifact("A", "APP")],
        [_depends("E1", "C", "A")],
    )
    layers = LayerDependencyGraph(graph)
    summary = layers.summary()
    assert summary["layers"] == [
        {"layer": "constitution", "depth": layer_depth("constitution"), "members": 1},
        {"layer": "application", "depth": layer_depth("application"), "members": 1},
    ]
    assert summary["dependencies"] == [
        {
            "source": "constitution",
            "target": "application",
            "weight": 1,
            "inversion": True,
        }
    ]
    assert summary["inversions"] == summary["dependencies"]
    assert summary["cycles"] == []
    assert summary["is_stratified"] is False
    # deterministic: the same graph yields a byte-identical summary
    assert LayerDependencyGraph(graph).summary() == summary
