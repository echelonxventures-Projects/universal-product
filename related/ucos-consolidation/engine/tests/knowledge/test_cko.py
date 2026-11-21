"""Tests for engine.knowledge.cko — CKO + Universal Decision Model (Part 02/03)."""

from __future__ import annotations

import dataclasses

import pytest

from engine.knowledge.cko import (
    CanonicalKnowledgeObject,
    DecisionRecord,
    RejectedOption,
    _as_str,
    _as_str_list,
)
from engine.knowledge.errors import (
    KnowledgeIntegrityError,
    KnowledgeValidationError,
    LifecycleTransitionError,
)
from engine.knowledge.model import KnowledgeAuthority, KnowledgeKind, Lifecycle

from .conftest import make_cko, make_decision


def test_create_seals_hash_and_verifies():
    obj = make_cko("UCKO-T-0001")
    assert obj.content_sha256
    assert obj.verify_integrity()
    obj.require_integrity()  # no raise


def test_require_integrity_raises_after_mutation():
    obj = make_cko("UCKO-T-0002")
    mutated = dataclasses.replace(obj, title="tampered")  # hash no longer matches
    assert not mutated.verify_integrity()
    with pytest.raises(KnowledgeIntegrityError):
        mutated.require_integrity()


def test_from_dict_roundtrip_and_all_links():
    obj = make_cko(
        "UCKO-T-0003",
        parent="UCKO-P",
        children=("UCKO-C",),
        dependencies=("UCKO-D",),
        consumers=("UCKO-K",),
        supersedes=("UCKO-S",),
        superseded_by="UCKO-N",
        knowledge_links=("UCKO-L",),
    )
    restored = CanonicalKnowledgeObject.from_dict(obj.to_dict())
    assert restored == obj
    expected_links = {"UCKO-P", "UCKO-C", "UCKO-D", "UCKO-K", "UCKO-S", "UCKO-N", "UCKO-L"}
    assert set(obj.all_links()) == expected_links


def test_from_dict_without_hash_is_sealed():
    payload = make_cko("UCKO-T-0004").to_dict()
    del payload["content_sha256"]
    restored = CanonicalKnowledgeObject.from_dict(payload)
    assert restored.verify_integrity()


def test_from_dict_with_bad_stored_hash_raises():
    payload = make_cko("UCKO-T-0005").to_dict()
    payload["content_sha256"] = "0" * 64
    with pytest.raises(KnowledgeIntegrityError):
        CanonicalKnowledgeObject.from_dict(payload)


def test_from_dict_missing_required_field():
    payload = make_cko("UCKO-T-0006").to_dict()
    del payload["title"]
    with pytest.raises(KnowledgeValidationError):
        CanonicalKnowledgeObject.from_dict(payload)


def test_from_dict_type_errors():
    with pytest.raises(KnowledgeValidationError):
        CanonicalKnowledgeObject.from_dict("not a mapping")
    payload = make_cko("UCKO-T-0007").to_dict()
    payload["tags"] = ["ok", 3]
    with pytest.raises(KnowledgeValidationError):
        CanonicalKnowledgeObject.from_dict(payload)
    payload2 = make_cko("UCKO-T-0008").to_dict()
    payload2["parent"] = 5
    with pytest.raises(KnowledgeValidationError):
        CanonicalKnowledgeObject.from_dict(payload2)


def test_transition_to_legal_and_illegal():
    obj = make_cko("UCKO-T-0009", lifecycle=Lifecycle.RATIFIED)
    moved = obj.transition_to(Lifecycle.IMPLEMENTED, updated="2026-01-01")
    assert moved.lifecycle is Lifecycle.IMPLEMENTED
    assert moved.updated == "2026-01-01"
    assert moved.verify_integrity()
    with pytest.raises(LifecycleTransitionError):
        obj.transition_to(Lifecycle.HISTORICAL)


def test_is_active_property():
    assert make_cko("UCKO-T-0010", lifecycle=Lifecycle.OPERATIONAL).is_active
    assert not make_cko("UCKO-T-0011", lifecycle=Lifecycle.DRAFT).is_active


def test_semantic_hash_ignores_identity():
    a = make_cko("UCKO-A", statement="same knowledge", rationale="r")
    b = make_cko("UCKO-B", statement="same knowledge", rationale="r")
    assert a.semantic_hash() == b.semantic_hash()
    assert a.content_sha256 != b.content_sha256


def test_rejected_option_from_dict_errors():
    opt = RejectedOption.from_dict({"option": "o", "reason": "r"}, at="x")
    assert opt == RejectedOption("o", "r")
    with pytest.raises(KnowledgeValidationError):
        RejectedOption.from_dict("nope", at="x")
    with pytest.raises(KnowledgeValidationError):
        RejectedOption.from_dict({"option": "o"}, at="x")


def test_decision_create_roundtrip_and_reviewable():
    dec = make_decision("UKDA-DEC-T1")
    assert dec.is_reviewable
    assert dec.verify_integrity()
    restored = DecisionRecord.from_dict(dec.to_dict())
    assert restored == dec


def test_decision_not_reviewable_when_incomplete():
    dec = make_decision("UKDA-DEC-T2", alternatives=())
    assert not dec.is_reviewable


def test_decision_from_dict_errors():
    with pytest.raises(KnowledgeValidationError):
        DecisionRecord.from_dict("nope")
    payload = make_decision("UKDA-DEC-T3").to_dict()
    del payload["problem_statement"]
    with pytest.raises(KnowledgeValidationError):
        DecisionRecord.from_dict(payload)
    payload2 = make_decision("UKDA-DEC-T4").to_dict()
    payload2["rejected_options"] = "not-a-list"
    with pytest.raises(KnowledgeValidationError):
        DecisionRecord.from_dict(payload2)


def test_decision_bad_stored_hash_and_transition():
    payload = make_decision("UKDA-DEC-T5").to_dict()
    payload["content_sha256"] = "f" * 64
    with pytest.raises(KnowledgeIntegrityError):
        DecisionRecord.from_dict(payload)
    dec = make_decision("UKDA-DEC-T6", lifecycle=Lifecycle.RATIFIED)
    moved = dec.transition_to(Lifecycle.IMPLEMENTED)
    assert moved.lifecycle is Lifecycle.IMPLEMENTED
    with pytest.raises(LifecycleTransitionError):
        dec.transition_to(Lifecycle.HISTORICAL)


def test_decision_require_integrity_raises():
    dec = make_decision("UKDA-DEC-T7")
    mutated = dataclasses.replace(dec, rationale="changed")
    with pytest.raises(KnowledgeIntegrityError):
        mutated.require_integrity()


def test_kind_and_authority_are_enforced_on_parse():
    payload = make_cko(
        "UCKO-T-0012",
        kind=KnowledgeKind.PRINCIPLE,
        authority=KnowledgeAuthority.CONSTITUTIONAL,
    ).to_dict()
    payload["kind"] = "bogus"
    with pytest.raises(KnowledgeValidationError):
        CanonicalKnowledgeObject.from_dict(payload)


def test_a_required_string_field_must_be_a_non_empty_string():
    """``_as_str`` is the parser's floor. Every seed and fixture record is well formed, so
    the refusal never ran — and the shapes it refuses are exactly what a hand-edited or
    round-tripped store produces: a null where a title belongs, an integer id, an empty
    string that reads as present and carries nothing."""

    assert _as_str("a title", field_name="title", at="X") == "a title"
    for wrong in ("", None, 7, ["a title"], {"title": "a title"}):
        with pytest.raises(KnowledgeValidationError) as excinfo:
            _as_str(wrong, field_name="title", at="X")
        assert excinfo.value.context["field"] == "title"


def test_an_absent_string_list_is_an_empty_tuple_and_not_a_refusal():
    """Optional list fields are ABSENT, not empty-by-mistake. Refusing ``None`` would make
    every optional link field mandatory, and a record that declares no consumers would be
    unparseable rather than simply unlinked."""

    assert _as_str_list(None, field_name="consumers", at="X") == ()
    assert _as_str_list([], field_name="consumers", at="X") == ()
    assert _as_str_list(["a", "b"], field_name="consumers", at="X") == ("a", "b")
    with pytest.raises(KnowledgeValidationError):
        _as_str_list(["a", 7], field_name="consumers", at="X")


def test_a_record_carrying_no_content_hash_is_sealed_rather_than_verified():
    """TWO WAYS IN, and only the verifying one had a test.

    A record that already carries a content hash is checked against it, because a stored
    object whose bytes no longer match its seal has been edited. A record that carries none
    has nothing to check — it is being admitted for the first time — so it is SEALED, and
    the resulting object then verifies. Refusing it would make the parser unable to admit
    any record a producer had not already sealed.
    """
    original = make_cko("A")
    record = original.to_dict()
    assert record["content_sha256"]

    unsealed = dict(record)
    unsealed.pop("content_sha256")
    admitted = CanonicalKnowledgeObject.from_dict(unsealed)
    assert admitted.content_sha256 == original.content_sha256
    assert admitted.verify_integrity()

    verified = CanonicalKnowledgeObject.from_dict(record)
    assert verified.content_sha256 == original.content_sha256

    tampered = dict(record)
    tampered["title"] = "a title the seal was not computed over"
    with pytest.raises(KnowledgeIntegrityError):
        CanonicalKnowledgeObject.from_dict(tampered)


def test_a_decision_record_carrying_no_content_hash_is_sealed_rather_than_verified():
    """The same two-way admission as an object's, on the type that records decisions.

    ``DecisionRecord`` seals its own content, and its parser has to admit a record a producer
    has not sealed — otherwise a decision could only ever be read back, never authored from a
    plain document. The verifying arm was covered by every round-trip; the sealing arm, which
    is the one an author takes, was not.
    """
    original = make_decision("UDR-SEAL")
    record = original.to_dict()
    assert record["content_sha256"]

    unsealed = dict(record)
    unsealed.pop("content_sha256")
    admitted = DecisionRecord.from_dict(unsealed)
    assert admitted.content_sha256 == original.content_sha256
    assert admitted.verify_integrity()

    tampered = dict(record)
    tampered["rationale"] = "a rationale the seal was not computed over"
    with pytest.raises(KnowledgeIntegrityError):
        DecisionRecord.from_dict(tampered)
