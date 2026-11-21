"""Tests for engine.knowledge.integration.composition — Deliverable 10."""

from __future__ import annotations

import pytest

from engine.knowledge.integration.composition import AutonomousComposer
from engine.knowledge.integration.errors import CompositionError
from engine.knowledge.model import KnowledgeKind

from .conftest import make_intent


def _compose_intent(intent_id: str = "NEW"):
    return make_intent(
        intent_id,
        title="Zeta",
        statement="orchestrating flows via bindings",
        dependencies=("COMP-A", "COMP-B"),
    )


def test_compose_from_sufficient_components(base):
    result = AutonomousComposer(base).compose(_compose_intent())
    assert result.sufficient
    assert result.components == ("COMP-A", "COMP-B")
    assert result.composed is not None
    assert result.composed["cko_id"] == "NEW"
    assert result.validated
    assert result.certified
    assert "components" in result.to_dict()


def test_compose_insufficient(base):
    result = AutonomousComposer(base).compose(make_intent("NEW"))  # no components
    assert not result.sufficient
    assert result.composed is None
    assert result.reasons


def test_compose_existing_identity(base):
    result = AutonomousComposer(base).compose(_compose_intent("COMP-A"))
    assert not result.sufficient
    assert any("identity" in r for r in result.reasons)


def test_require_raises_when_insufficient(base):
    composer = AutonomousComposer(base)
    with pytest.raises(CompositionError):
        composer.require(make_intent("NEW"))
    # a sufficient intent returns a result
    assert composer.require(_compose_intent()).sufficient


def test_an_intent_that_states_its_own_rationale_keeps_it(base):
    """The composer SUPPLIES a rationale only where the kind requires one and the intent
    gave none. Overwriting a stated rationale would replace an author's reason with a
    generated sentence, which is the one thing a composition must not do — the rationale is
    the part a reader uses to decide whether the composition was right."""
    stated = make_intent(
        "COMPOSED",
        title="Zeta",
        statement="orchestrating flows via bindings",
        dependencies=("COMP-A", "COMP-B"),
        rationale="Because the two components already answer this question together.",
    )
    result = AutonomousComposer(base).compose(stated)
    assert result.sufficient, result.reasons
    assert result.composed is not None
    assert result.composed["rationale"] == stated.rationale
    assert "autonomous constitutional composition" not in result.composed["rationale"]

    # The other arm, for contrast: no stated rationale and a kind that REQUIRES one.
    # PATTERN does not, which is why every existing composition test left the supplied
    # sentence unexecuted — the requirement is declared for DECISION, RULE and PRINCIPLE.

    needs_one = make_intent(
        "SUPPLIED",
        kind=KnowledgeKind.PRINCIPLE,
        title="Zeta",
        statement="orchestrating flows via bindings",
        dependencies=("COMP-A", "COMP-B"),
    )
    supplied = AutonomousComposer(base).compose(needs_one)
    assert supplied.composed is not None
    assert "autonomous constitutional composition" in supplied.composed["rationale"]
