"""Shared fixtures + factories for the UKI integration tests.

All fixtures build small, self-contained in-memory knowledge bases; nothing touches
the certified corpus (DP-03).
"""

from __future__ import annotations

import pytest

from engine.knowledge.cko import CanonicalKnowledgeObject
from engine.knowledge.integration.contracts import ArtifactIntent, Operation
from engine.knowledge.model import KnowledgeAuthority, KnowledgeKind, Lifecycle
from engine.knowledge.store import KnowledgeBase


def make_cko(cko_id: str, **overrides) -> CanonicalKnowledgeObject:
    """Build a well-formed, active CKO with sensible defaults."""
    fields = {
        "cko_id": cko_id,
        "kind": KnowledgeKind.PATTERN,
        "title": f"Title {cko_id}",
        "statement": f"Statement for {cko_id}.",
        "universe": "TEST",
        "authority": KnowledgeAuthority.ENGINEERING,
        "owner": "TEAM-A",
        "lifecycle": Lifecycle.OPERATIONAL,
        "version": "1.0.0",
    }
    fields.update(overrides)
    return CanonicalKnowledgeObject.create(**fields)


def make_intent(intent_id: str, **overrides) -> ArtifactIntent:
    """Build a well-formed CREATE intent with sensible defaults."""
    fields = {
        "intent_id": intent_id,
        "kind": KnowledgeKind.PATTERN,
        "title": f"Intent {intent_id}",
        "statement": f"A uniquely described proposed capability {intent_id}.",
        "universe": "TEST",
        "authority": KnowledgeAuthority.ENGINEERING,
        "owner": "TEAM-A",
        "operation": Operation.CREATE,
    }
    fields.update(overrides)
    return ArtifactIntent(**fields)


@pytest.fixture
def base() -> KnowledgeBase:
    """A small base with two active, unrelated components in universe TEST."""
    return KnowledgeBase(
        [
            make_cko("COMP-A", title="alpha component", statement="the alpha component substance"),
            make_cko("COMP-B", title="beta component", statement="the beta component substance"),
        ]
    )


@pytest.fixture
def empty_base() -> KnowledgeBase:
    return KnowledgeBase([])
