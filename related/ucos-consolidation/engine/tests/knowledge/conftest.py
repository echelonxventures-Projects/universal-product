"""Shared fixtures + factories for the UKDA Knowledge Layer tests.

All fixtures build small, self-contained knowledge bases in memory (or under
``tmp_path``); nothing touches the certified corpus (DP-03).
"""

from __future__ import annotations

import pytest

from engine.knowledge.cko import CanonicalKnowledgeObject, DecisionRecord, RejectedOption
from engine.knowledge.model import KnowledgeAuthority, KnowledgeKind, Lifecycle
from engine.knowledge.seed import build_seed_base
from engine.knowledge.store import KnowledgeBase


def make_cko(cko_id: str, **overrides) -> CanonicalKnowledgeObject:
    """Build a well-formed CKO with sensible defaults; override any field."""
    fields = {
        "cko_id": cko_id,
        "kind": KnowledgeKind.FACT,
        "title": f"Title {cko_id}",
        "statement": f"Statement for {cko_id}.",
        "universe": "TEST",
        "authority": KnowledgeAuthority.ENGINEERING,
        "owner": "TEST-OWNER",
        "lifecycle": Lifecycle.OPERATIONAL,
        "version": "1.0.0",
    }
    fields.update(overrides)
    return CanonicalKnowledgeObject.create(**fields)


def make_decision(decision_id: str, **overrides) -> DecisionRecord:
    """Build a reviewable decision record with sensible defaults."""
    fields = {
        "decision_id": decision_id,
        "title": f"Decision {decision_id}",
        "problem_statement": "A problem.",
        "context": "Some context.",
        "objective": "An objective.",
        "chosen_architecture": "The chosen architecture.",
        "rationale": "Because it is best.",
        "authority": KnowledgeAuthority.ARCHITECTURAL,
        "owner": "TEST-OWNER",
        "lifecycle": Lifecycle.RATIFIED,
        "version": "1.0.0",
        "review_authority": "TEST-REVIEW",
        "supersession_rules": "Only by a ratified successor.",
        "alternatives": ("A", "B"),
        "rejected_options": (RejectedOption("A", "worse"),),
    }
    fields.update(overrides)
    return DecisionRecord.create(**fields)


@pytest.fixture
def seed_base() -> KnowledgeBase:
    return build_seed_base()


@pytest.fixture
def store_dir(tmp_path):
    return tmp_path / "knowledge"
