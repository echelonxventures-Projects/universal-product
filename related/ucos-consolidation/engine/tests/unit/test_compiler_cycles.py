"""TASK-000022/000029 — cycle detection tests."""

from __future__ import annotations

import pytest

from engine.compiler.cycles import assert_acyclic, detect_cycle, topological_order
from engine.compiler.errors import CyclicDependencyError


def test_detect_cycle_none_for_dag():
    graph = {"a": ["b"], "b": ["c"], "c": []}
    assert detect_cycle(graph) is None
    assert_acyclic(graph)  # does not raise


def test_detect_direct_cycle():
    graph = {"a": ["b"], "b": ["a"]}
    cycle = detect_cycle(graph)
    assert cycle is not None
    assert cycle[0] == cycle[-1]


def test_detect_self_loop():
    assert detect_cycle({"a": ["a"]}) == ("a", "a")


def test_assert_acyclic_raises_with_cycle_path():
    with pytest.raises(CyclicDependencyError) as exc:
        assert_acyclic({"a": ["b"], "b": ["c"], "c": ["a"]})
    assert exc.value.context["cycle"][0] == exc.value.context["cycle"][-1]


def test_topological_order_dependencies_first():
    graph = {"a": ["b"], "b": ["c"], "c": []}
    order = topological_order(graph)
    assert order.index("c") < order.index("b") < order.index("a")


def test_topological_order_deterministic():
    graph = {"a": ["c"], "b": ["c"], "c": [], "d": []}
    assert topological_order(graph) == topological_order(dict(graph))


def test_topological_order_raises_on_cycle():
    with pytest.raises(CyclicDependencyError):
        topological_order({"a": ["b"], "b": ["a"]})


def test_edges_referencing_absent_nodes_are_materialised():
    # 'b' is only referenced as an edge target; it must appear as a node.
    order = topological_order({"a": ["b"]})
    assert set(order) == {"a", "b"}


def test_detect_cycle_revisits_fully_explored_node():
    # Diamond DAG: after 'c' is fully explored (BLACK) via 'b', node 'a' re-encounters
    # it as its second neighbour. This exercises the "neighbour already BLACK" branch
    # (skip and continue) without discovering a cycle.
    graph = {"a": ["b", "c"], "b": ["c"], "c": []}
    assert detect_cycle(graph) is None
    assert_acyclic(graph)  # does not raise


def test_topological_order_multiple_children_insertion():
    # A single root with several dependencies exercises ordered insertion.
    order = topological_order({"a": ["x", "y", "z"], "x": [], "y": [], "z": []})
    assert order.index("a") == len(order) - 1
    assert set(order[:-1]) == {"x", "y", "z"}
