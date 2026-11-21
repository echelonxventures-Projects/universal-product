"""Tests for engine.knowledge.integration.dependency — Deliverable 4."""

from __future__ import annotations

from engine.knowledge.integration.dependency import DependencyIntegration
from engine.knowledge.store import KnowledgeBase

from .conftest import make_cko, make_intent


def _base():
    return KnowledgeBase(
        [
            make_cko("A", dependencies=("B",), consumers=("C",)),
            make_cko("B"),
            make_cko("C"),
        ]
    )


def test_view_of_existing_node():
    integ = DependencyIntegration(_base())
    view = integ.view("A")
    assert view.dependencies == ("B",)
    assert view.providers == ("B",)
    assert view.consumers == ("C",)
    assert view.dependents == ()
    assert view.impact == ("C",)
    # composition = every edge touching A (A->B and C->A)
    assert len(view.composition) == 2
    d = view.to_dict()
    assert d["node"] == "A"
    assert d["dependencies"] == ["B"]
    assert integ.graph is not None


def test_view_of_intent_projected_into_graph():
    integ = DependencyIntegration(_base())
    intent = make_intent("NEW", dependencies=("A",))
    view = integ.view_intent(intent)
    assert view.node == "NEW"
    assert view.dependencies == ("A",)
    # transitive providers reach A then B
    assert set(view.providers) == {"A", "B"}
    assert len(view.composition) == 1
