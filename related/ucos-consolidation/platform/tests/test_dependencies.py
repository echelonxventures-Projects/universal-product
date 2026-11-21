"""EC2-TASK-000059 — Platform dependency model tests."""

from __future__ import annotations

from platform.foundation.dependencies import DependencyGraph, DependencyNode
from platform.foundation.errors import DependencyError

import pytest


def test_node_requires_id():
    with pytest.raises(DependencyError):
        DependencyNode("")


def test_topological_order_is_deterministic():
    g = DependencyGraph()
    g.add("c", ["a", "b"])
    g.add("b", ["a"])
    g.add("a")
    order = g.topological_order()
    assert order == ("a", "b", "c")
    # dependencies always precede dependents
    assert order.index("a") < order.index("b") < order.index("c")


def test_parallel_roots_sorted_deterministically():
    g = DependencyGraph()
    g.add("z")
    g.add("a")
    g.add("m", ["a", "z"])
    assert g.topological_order() == ("a", "z", "m")


def test_duplicate_node_rejected():
    g = DependencyGraph()
    g.add("a")
    with pytest.raises(DependencyError):
        g.add("a")


def test_unknown_dependency_rejected():
    g = DependencyGraph()
    g.add("a", ["missing"])
    with pytest.raises(DependencyError) as exc:
        g.validate()
    assert exc.value.context["missing"] == "missing"


def test_cycle_detected():
    g = DependencyGraph()
    g.add("a", ["b"])
    g.add("b", ["a"])
    assert g.has_cycle() is True
    with pytest.raises(DependencyError):
        g.topological_order()


def test_has_cycle_false_for_unknown_dependency():
    g = DependencyGraph()
    g.add("a", ["missing"])
    # unknown-dependency is not a cycle
    assert g.has_cycle() is False


def test_has_cycle_false_for_valid_acyclic_graph():
    g = DependencyGraph()
    g.add("a")
    g.add("b", ["a"])
    assert g.has_cycle() is False


def test_dependencies_and_dependents():
    g = DependencyGraph()
    g.add("a")
    g.add("b", ["a"])
    g.add("c", ["a"])
    assert g.dependencies_of("b") == ("a",)
    assert g.dependents_of("a") == ("b", "c")
    assert "a" in g
    assert len(g) == 3
    assert g.node_ids == ("a", "b", "c")


def test_require_unknown_node_raises():
    g = DependencyGraph()
    with pytest.raises(DependencyError):
        g.dependencies_of("nope")


def test_to_dict():
    g = DependencyGraph()
    g.add("a")
    g.add("b", ["a"])
    d = g.to_dict()
    assert d["node_count"] == 2
    assert {n["node_id"] for n in d["nodes"]} == {"a", "b"}
