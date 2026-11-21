"""Tests for engine.knowledge.model — the UKDA vocabularies (Part 01/05/12)."""

from __future__ import annotations

import pytest

from engine.knowledge.errors import (
    KnowledgeValidationError,
    LifecycleTransitionError,
    RelationshipError,
)
from engine.knowledge.model import (
    KnowledgeAuthority,
    KnowledgeKind,
    Lifecycle,
    RelationType,
    canonical_json,
    content_hash,
)


def test_canonical_json_is_deterministic_and_sorted():
    a = canonical_json({"b": 1, "a": 2})
    b = canonical_json({"a": 2, "b": 1})
    assert a == b == '{"a":2,"b":1}'
    assert content_hash({"a": 2, "b": 1}) == content_hash({"b": 1, "a": 2})


def test_knowledge_kind_coerce_ok_and_error():
    assert KnowledgeKind.coerce("decision") is KnowledgeKind.DECISION
    with pytest.raises(KnowledgeValidationError):
        KnowledgeKind.coerce("nonsense", context="x")


def test_authority_rank_and_outranks():
    assert KnowledgeAuthority.CONSTITUTIONAL.rank == 0
    assert KnowledgeAuthority.CONSTITUTIONAL.outranks(KnowledgeAuthority.ADVISORY)
    assert not KnowledgeAuthority.ADVISORY.outranks(KnowledgeAuthority.ENGINEERING)
    with pytest.raises(KnowledgeValidationError):
        KnowledgeAuthority.coerce("king")


def test_lifecycle_transitions_legal_and_illegal():
    assert Lifecycle.DRAFT.can_transition_to(Lifecycle.REVIEW)
    assert not Lifecycle.DRAFT.can_transition_to(Lifecycle.OPERATIONAL)
    Lifecycle.RATIFIED.require_transition(Lifecycle.IMPLEMENTED)  # no raise
    with pytest.raises(LifecycleTransitionError):
        Lifecycle.DRAFT.require_transition(Lifecycle.OPERATIONAL, at="obj")


def test_lifecycle_active_and_terminal_and_coerce():
    assert Lifecycle.OPERATIONAL.is_active
    assert not Lifecycle.DRAFT.is_active
    assert Lifecycle.HISTORICAL.is_terminal
    assert not Lifecycle.RATIFIED.is_terminal
    assert Lifecycle.coerce("draft") is Lifecycle.DRAFT
    with pytest.raises(KnowledgeValidationError):
        Lifecycle.coerce("zombie")


def test_relation_type_symmetry_and_coerce():
    assert RelationType.EQUIVALENT_TO.is_symmetric
    assert RelationType.CONFLICTS_WITH.is_symmetric
    assert RelationType.RELATED_TO.is_symmetric
    assert not RelationType.DEPENDS_ON.is_symmetric
    assert RelationType.coerce("depends-on") is RelationType.DEPENDS_ON
    with pytest.raises(RelationshipError):
        RelationType.coerce("teleports-to")
