"""Tests for engine.knowledge.integration.contracts — ArtifactIntent + vocabularies."""

from __future__ import annotations

import pytest

from engine.knowledge.integration.contracts import (
    CANONICAL_LAYERS,
    CONSTITUTIONAL_SEQUENCE,
    UKI_CONTRACT,
    ArtifactIntent,
    ConstitutionalLayer,
    Operation,
    SequenceStage,
    _as_opt_str,
)
from engine.knowledge.integration.errors import IntentError
from engine.knowledge.model import KnowledgeAuthority, KnowledgeKind, Lifecycle

from .conftest import make_intent


def test_contract_identity():
    assert UKI_CONTRACT.name == "knowledge.uki"
    assert str(UKI_CONTRACT.version) == "1.0.0"


def test_vocabularies_stable_and_complete():
    assert len(CANONICAL_LAYERS) == 21
    assert CANONICAL_LAYERS[0] is ConstitutionalLayer.CONSTITUTION
    assert [s.value for s in CONSTITUTIONAL_SEQUENCE] == [
        "discover",
        "analyze",
        "reuse",
        "extend",
        "compose",
        "create",
        "validate",
        "certify",
        "register",
        "evolve",
    ]
    assert SequenceStage.DISCOVER.value == "discover"


def test_intent_references_and_to_cko_roundtrip():
    intent = make_intent(
        "I-1",
        parent="P",
        dependencies=("D1", "D2"),
        consumers=("C1",),
        knowledge_links=("K1", "D1"),  # duplicate D1 collapses
    )
    refs = intent.references()
    assert refs[0] == "P"
    assert set(refs) == {"P", "D1", "D2", "C1", "K1"}
    cko = intent.to_cko(lifecycle=Lifecycle.DRAFT)
    assert cko.cko_id == "I-1"
    assert cko.lifecycle is Lifecycle.DRAFT
    assert cko.verify_integrity()
    assert intent.semantic_hash() == cko.semantic_hash()


def test_from_dict_defaults_and_roundtrip():
    payload = {
        "intent_id": "I-2",
        "kind": "pattern",
        "title": "T",
        "statement": "S",
        "universe": "U",
        "authority": "engineering",
        "owner": "O",
    }
    intent = ArtifactIntent.from_dict(payload)
    assert intent.operation is Operation.CREATE
    assert intent.kind is KnowledgeKind.PATTERN
    assert intent.authority is KnowledgeAuthority.ENGINEERING
    d = intent.to_dict()
    assert d["intent_id"] == "I-2"
    assert d["operation"] == "create"
    # a full roundtrip is stable
    assert ArtifactIntent.from_dict(d).to_dict() == d


def test_from_dict_rejects_bad_input():
    with pytest.raises(IntentError):
        ArtifactIntent.from_dict("not-a-mapping")
    with pytest.raises(IntentError):
        ArtifactIntent.from_dict({"kind": "pattern"})  # missing intent_id
    base = {
        "intent_id": "I",
        "kind": "pattern",
        "title": "T",
        "statement": "S",
        "universe": "U",
        "authority": "engineering",
        "owner": "O",
    }
    with pytest.raises(IntentError):
        ArtifactIntent.from_dict({**base, "operation": "nonsense"})
    with pytest.raises(IntentError):
        ArtifactIntent.from_dict({**base, "dependencies": "notalist"})
    with pytest.raises(IntentError):
        ArtifactIntent.from_dict({**base, "parent": 5})


def test_an_optional_string_field_accepts_a_string_a_null_and_nothing_else():
    """Three answers, and the accepting one had no test.

    ``_as_opt_str`` is what makes ``parent`` optional rather than absent-or-broken. Only the
    refusals were exercised, so the arm that lets a real value through was dead — a parser
    whose accepting path is untested is one that could reject everything and still look
    correct from its own suite.
    """

    assert _as_opt_str("UCKO-PARENT", field_name="parent") == "UCKO-PARENT"
    assert _as_opt_str(None, field_name="parent") is None
    with pytest.raises(IntentError) as excinfo:
        _as_opt_str(7, field_name="parent")
    assert excinfo.value.context["field"] == "parent"


def test_an_intent_that_declares_a_parent_lists_it_first_among_its_references():
    """``references`` is the ordered outbound closure a registration plan is built from, and
    the parent is part of it. An intent with no parent was the only shape tested, so a parent
    could have been dropped from every plan without a failure."""
    parented = make_intent(
        "CHILD",
        parent="UCKO-PARENT",
        dependencies=("UCKO-DEP",),
        knowledge_links=("UCKO-DEP",),
    )
    assert parented.references() == ("UCKO-PARENT", "UCKO-DEP")

    orphan = make_intent("ORPHAN", dependencies=("UCKO-DEP",))
    assert orphan.references() == ("UCKO-DEP",)
