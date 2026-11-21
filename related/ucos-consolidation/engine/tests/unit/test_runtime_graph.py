"""TASK-000038 — Runtime Composition Graph unit tests (EPIC-006).

Exercises the runtime dependency graph: deterministic ordering/levelling (reusing
the compiler's cycle/topological primitives), closure + acyclicity gates, and the
neighbour/root/leaf queries used by context resolution and the execution planner.
"""

from __future__ import annotations

import pytest

from engine.runtime.errors import RuntimeGraphError
from engine.runtime.graph import DEPENDS_ON, RuntimeGraph


@pytest.fixture
def diamond() -> RuntimeGraph:
    """A → {B, C} → D dependency diamond."""
    return RuntimeGraph.of({"a": (), "b": ("a",), "c": ("a",), "d": ("b", "c")})


# -- construction gates -------------------------------------------------------


def test_empty_graph_is_valid():
    graph = RuntimeGraph({})
    assert graph.count() == 0
    assert graph.order() == ()
    assert graph.levels() == ()


def test_non_string_node_rejected():
    with pytest.raises(RuntimeGraphError):
        RuntimeGraph({"": ()})


def test_self_dependency_rejected():
    with pytest.raises(RuntimeGraphError) as exc:
        RuntimeGraph({"a": ("a",)})
    assert "itself" in exc.value.message


def test_open_graph_rejected():
    with pytest.raises(RuntimeGraphError) as exc:
        RuntimeGraph({"a": ("missing",)})
    assert "open graph" in exc.value.message
    assert exc.value.code == "RT-GRAPH-001"


def test_cycle_rejected_with_path():
    with pytest.raises(RuntimeGraphError) as exc:
        RuntimeGraph({"a": ("b",), "b": ("a",)})
    assert "circular" in exc.value.message
    assert exc.value.context["cycle"][0] == exc.value.context["cycle"][-1]


# -- ordering / levelling -----------------------------------------------------


def test_topological_order_dependencies_first(diamond):
    order = diamond.order()
    assert order.index("a") < order.index("b")
    assert order.index("a") < order.index("c")
    assert order.index("b") < order.index("d")
    assert order.index("c") < order.index("d")


def test_levels_group_independent_nodes(diamond):
    assert diamond.levels() == (("a",), ("b", "c"), ("d",))


def test_depth(diamond):
    assert diamond.depth("a") == 0
    assert diamond.depth("b") == 1
    assert diamond.depth("d") == 2


# -- neighbour / membership queries -------------------------------------------


def test_dependencies_and_dependents(diamond):
    assert diamond.dependencies_of("d") == ("b", "c")
    assert diamond.dependents_of("a") == ("b", "c")
    assert diamond.dependencies_of("a") == ()


def test_roots_and_leaves(diamond):
    assert diamond.roots() == ("a",)
    assert diamond.leaves() == ("d",)


def test_nodes_and_edges_sorted(diamond):
    assert diamond.nodes() == ("a", "b", "c", "d")
    assert diamond.edges() == (("b", "a"), ("c", "a"), ("d", "b"), ("d", "c"))


def test_membership(diamond):
    assert diamond.has_node("a")
    assert "a" in diamond
    assert "zzz" not in diamond
    assert len(diamond) == 4


def test_unknown_node_queries_raise(diamond):
    for query in (diamond.dependencies_of, diamond.dependents_of, diamond.depth):
        with pytest.raises(RuntimeGraphError):
            query("unknown")


def test_deduplicates_edges():
    graph = RuntimeGraph({"a": (), "b": ("a", "a")})
    assert graph.dependencies_of("b") == ("a",)


def test_to_dict(diamond):
    blob = diamond.to_dict()
    assert blob["edge_type"] == DEPENDS_ON
    assert blob["nodes"] == ["a", "b", "c", "d"]
    assert blob["roots"] == ["a"]
    assert blob["leaves"] == ["d"]
    assert {"universe": "d", "depends_on": "b"} in blob["edges"]
