"""Unit tests for engine.graph.architecture.reachability.

Proves that traversal is constrained to the named relation family (so a "reachable"
answer is semantically interpretable), that both senses of every family work, that
results are sorted and exclude the source, and that unknown families and absent
nodes fail closed with ReachabilityError rather than returning an empty answer.
"""

from __future__ import annotations

import pytest

from engine.graph.architecture.errors import ReachabilityError
from engine.graph.architecture.reachability import (
    RELATION_FAMILIES,
    ReachabilityResult,
    SemanticReachability,
)
from engine.graph.model import KIND_ARTIFACT, Edge, KnowledgeGraph, Node


def _graph() -> KnowledgeGraph:
    # A -Depends-On-> B -Depends-On-> C   (dependency family)
    # A -Consumes->  D                    (capability family)
    # A -Implements-> E                   (traceability family)
    nodes = [Node(x, KIND_ARTIFACT) for x in ("A", "B", "C", "D", "E")]
    edges = [
        Edge("E1", "A", "B", "Depends-On"),
        Edge("E2", "B", "C", "Depends-On"),
        Edge("E3", "A", "D", "Consumes"),
        Edge("E4", "A", "E", "Implements"),
    ]
    return KnowledgeGraph(nodes, edges)


def _reach() -> SemanticReachability:
    return SemanticReachability(_graph())


# --- families --------------------------------------------------------------------


def test_families_are_sorted_and_cover_the_declared_vocabulary():
    assert SemanticReachability.families() == tuple(sorted(RELATION_FAMILIES))
    assert set(SemanticReachability.families()) == {
        "capability",
        "dependency",
        "requirement",
        "structural",
        "traceability",
    }


def test_unknown_family_fails_closed():
    with pytest.raises(ReachabilityError) as exc:
        _reach().reachable("A", "not-a-family")
    assert exc.value.code == "AIG-REACH-001"


def test_unknown_family_on_path_fails_closed():
    with pytest.raises(ReachabilityError):
        _reach().path("A", "B", "not-a-family")


# --- reachable -------------------------------------------------------------------


def test_reachable_follows_the_dependency_family_transitively():
    result = _reach().reachable("A", "dependency")
    assert result.reachable == ("B", "C")
    assert result.count == 2
    assert result.source == "A"
    assert result.inbound is False


def test_reachable_excludes_the_source_itself():
    assert "A" not in _reach().reachable("A", "dependency").reachable


def test_reachable_is_constrained_to_its_family():
    # D is reachable only via Consumes, so the dependency family must not see it
    reach = _reach()
    assert "D" not in reach.reachable("A", "dependency").reachable
    assert reach.reachable("A", "capability").reachable == ("D",)
    assert reach.reachable("A", "traceability").reachable == ("E",)


def test_reachable_inbound_traverses_the_family_in_reverse():
    result = _reach().reachable("C", "dependency", inbound=True)
    assert result.reachable == ("A", "B")
    assert result.inbound is True


def test_reachable_terminal_node_has_an_empty_forward_set():
    result = _reach().reachable("C", "dependency")
    assert result.reachable == ()
    assert result.count == 0


def test_reachable_family_with_no_edges_is_empty_not_an_error():
    assert _reach().reachable("A", "requirement").reachable == ()


def test_reachable_rejects_an_absent_node():
    with pytest.raises(ReachabilityError):
        _reach().reachable("GHOST", "dependency")


def test_reachable_is_deterministic_across_repeated_queries():
    reach = _reach()
    assert reach.reachable("A", "dependency") == reach.reachable("A", "dependency")


# --- path / can_reach ------------------------------------------------------------


def test_path_returns_the_shortest_semantic_path_including_endpoints():
    assert _reach().path("A", "C", "dependency") == ("A", "B", "C")


def test_path_is_empty_when_the_target_is_unreachable_in_that_family():
    # D is reachable from A, but only through Consumes — not the dependency family
    assert _reach().path("A", "D", "dependency") == ()


def test_path_reverse_direction_is_empty_without_inbound():
    assert _reach().path("C", "A", "dependency") == ()


def test_path_inbound_traverses_backwards():
    assert _reach().path("C", "A", "dependency", inbound=True) == ("C", "B", "A")


def test_path_rejects_an_absent_source_or_target():
    reach = _reach()
    with pytest.raises(ReachabilityError):
        reach.path("GHOST", "A", "dependency")
    with pytest.raises(ReachabilityError):
        reach.path("A", "GHOST", "dependency")


def test_can_reach_agrees_with_path():
    reach = _reach()
    assert reach.can_reach("A", "C", "dependency") is True
    assert reach.can_reach("A", "D", "dependency") is False
    assert reach.can_reach("C", "A", "dependency", inbound=True) is True


# --- projections -----------------------------------------------------------------


def test_result_to_dict_projects_every_field():
    result = ReachabilityResult(source="A", family="dependency", inbound=False, reachable=("B",))
    assert result.to_dict() == {
        "source": "A",
        "family": "dependency",
        "inbound": False,
        "count": 1,
        "reachable": ["B"],
    }


def test_summary_reports_every_family_forward():
    summary = _reach().summary("A")
    assert summary["source"] == "A"
    assert summary["families"] == {
        "capability": 1,
        "dependency": 2,
        "requirement": 0,
        "structural": 0,
        "traceability": 1,
    }


def test_summary_rejects_an_absent_node():
    with pytest.raises(ReachabilityError):
        _reach().summary("GHOST")
