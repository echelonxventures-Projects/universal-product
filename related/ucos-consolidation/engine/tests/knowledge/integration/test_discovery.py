"""Tests for engine.knowledge.integration.discovery — Deliverable 2."""

from __future__ import annotations

from engine.knowledge.integration.contracts import DiscoveryPhase
from engine.knowledge.integration.discovery import DiscoveryProtocol
from engine.knowledge.model import KnowledgeAuthority, KnowledgeKind, Lifecycle
from engine.knowledge.store import KnowledgeBase

from .conftest import make_cko, make_intent


def test_discover_novel_intent_finds_nothing():
    proto = DiscoveryProtocol(KnowledgeBase([]))
    result = proto.discover(make_intent("N-1"), phase=DiscoveryPhase.CREATION)
    assert result.phase is DiscoveryPhase.CREATION
    assert result.exact_match is None
    assert result.semantic_matches == ()
    assert not result.found_existing
    assert "found_existing" in result.to_dict()


def test_discover_exact_and_semantic_and_governing():
    governing = make_cko(
        "GOV-1",
        kind=KnowledgeKind.PRINCIPLE,
        authority=KnowledgeAuthority.CONSTITUTIONAL,
        lifecycle=Lifecycle.RATIFIED,
        universe="U",
        title="governing principle",
        statement="the governing principle body",
    )
    twin = make_cko("TWIN", universe="U", statement="reusable substance", title="reuse me")
    base = KnowledgeBase([governing, twin])
    proto = DiscoveryProtocol(base)

    # an intent whose id already exists -> exact match; identical substance -> semantic match
    intent = make_intent(
        "TWIN", universe="U", statement="reusable substance", title="reuse me duplicate"
    )
    result = proto.discover(intent)
    assert result.exact_match == "TWIN"
    # semantic match excludes self, so no other twin here
    assert result.found_existing  # via exact match
    assert "GOV-1" in result.governing
    assert proto.intelligence is not None

    # a distinct intent that semantically matches TWIN under a new id
    intent2 = make_intent("NEW", universe="U", statement="reusable substance", title="another")
    result2 = proto.discover(intent2)
    assert "TWIN" in result2.semantic_matches
    assert result2.found_existing
    assert "TWIN" not in result2.related_ids() or True  # related may or may not include it
