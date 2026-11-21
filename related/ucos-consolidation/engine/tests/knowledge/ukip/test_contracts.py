"""UKIP Part 01 — knowledge unit contracts and the Knowledge Once identity."""

from __future__ import annotations

import pytest

from engine.knowledge.cko import CanonicalKnowledgeObject
from engine.knowledge.model import KnowledgeAuthority, KnowledgeKind, Lifecycle, RelationType
from engine.knowledge.ukip.contracts import (
    KNOWLEDGE_ID_DIGEST_LEN,
    KNOWLEDGE_ID_PREFIX,
    KnowledgeUnit,
    ProviderKind,
    RelationDeclaration,
    SourceRef,
    normalize_text,
    unit_document,
)
from engine.knowledge.ukip.errors import UnitError
from engine.tests.knowledge.ukip.conftest import make_source, make_unit

# ---------------------------------------------------------------------------
# the anti-drift property: UKIP's duplicate identity IS the UKDA semantic hash
# ---------------------------------------------------------------------------


def test_knowledge_hash_equals_ukda_semantic_hash():
    """A unit and the canonical object it describes must share one identity.

    This is the single most important property in the layer: if these two hashes
    could diverge, UKIP would develop a second notion of "the same knowledge" and
    the Knowledge Once Principle would be unenforceable across providers.
    """
    obj = CanonicalKnowledgeObject.create(
        cko_id="UCKO-TEST-0001",
        kind=KnowledgeKind.PRINCIPLE,
        title="A Title",
        statement="  Knowledge Is Authored Once.  ",
        rationale="Because Duplication Drifts.",
        universe="TEST",
        authority=KnowledgeAuthority.CONSTITUTIONAL,
        owner="OWNER",
        lifecycle=Lifecycle.RATIFIED,
        version="1.0.0",
    )
    unit = make_unit(
        "probe",
        title="A Completely Different Title",
        statement=obj.statement,
        rationale=obj.rationale,
        kind=obj.kind,
        universe="OTHER",
        owner="SOMEONE-ELSE",
    )
    assert unit.knowledge_sha256() == obj.semantic_hash()


def test_identity_ignores_title_universe_owner_and_source():
    """Identity is the substance only: metadata cannot fork a second record."""
    left = make_unit("l", statement="Same substance.", rationale="Same why.")
    right = make_unit(
        "r",
        title="Different title",
        statement="Same substance.",
        rationale="Same why.",
        universe="ELSEWHERE",
        owner="OTHER-OWNER",
        version="9.9.9",
        source=make_source(provider_id="other", locator="other/loc"),
    )
    assert left.knowledge_sha256() == right.knowledge_sha256()
    assert left.knowledge_id() == right.knowledge_id()


def test_identity_is_case_and_edge_whitespace_insensitive():
    left = make_unit("l", statement="Knowledge Once.", rationale="R.")
    right = make_unit("r", statement="  knowledge once.  ", rationale="  r.  ")
    assert left.knowledge_sha256() == right.knowledge_sha256()


def test_identity_changes_with_kind():
    """Different kinds of claim about the same words are different knowledge."""
    left = make_unit("l", statement="X holds.", kind=KnowledgeKind.RULE)
    right = make_unit("r", statement="X holds.", kind=KnowledgeKind.GUIDELINE)
    assert left.knowledge_sha256() != right.knowledge_sha256()


def test_unclassified_unit_hashes_with_empty_kind():
    unit = make_unit("u", kind=None)
    assert unit.knowledge_core()["kind"] == ""
    assert unit.knowledge_id().startswith(KNOWLEDGE_ID_PREFIX + "-")


def test_knowledge_id_shape():
    unit = make_unit("u")
    prefix, _, digest = unit.knowledge_id().partition("-")
    assert prefix == KNOWLEDGE_ID_PREFIX
    assert len(digest) == KNOWLEDGE_ID_DIGEST_LEN
    assert digest == digest.upper()
    assert digest == unit.knowledge_sha256()[:KNOWLEDGE_ID_DIGEST_LEN].upper()


def test_unit_sha256_binds_the_source_but_knowledge_hash_does_not():
    left = make_unit("u")
    right = make_unit("u", source=make_source(locator="somewhere/else"))
    assert left.knowledge_sha256() == right.knowledge_sha256()
    assert left.unit_sha256() != right.unit_sha256()


# ---------------------------------------------------------------------------
# SourceRef
# ---------------------------------------------------------------------------


def test_source_citation_with_and_without_revision():
    assert make_source(revision="abc").citation == "test-provider:test/doc.md#section@abc"
    assert make_source(revision="").citation == "test-provider:test/doc.md#section"


def test_source_rejects_empty_provider_and_locator():
    with pytest.raises(UnitError):
        SourceRef(provider_id="", kind=ProviderKind.DOCUMENT, locator="l")
    with pytest.raises(UnitError):
        SourceRef(provider_id="p", kind=ProviderKind.DOCUMENT, locator="")


def test_source_rejects_non_enum_kind():
    with pytest.raises(UnitError):
        SourceRef(provider_id="p", kind="document", locator="l")


def test_source_round_trips():
    source = make_source(content_sha256="b" * 64)
    assert SourceRef.from_dict(source.to_dict()) == source


def test_source_from_dict_rejects_non_mapping_and_unknown_kind():
    with pytest.raises(UnitError):
        SourceRef.from_dict(["not", "a", "mapping"])
    with pytest.raises(UnitError):
        SourceRef.from_dict({"provider_id": "p", "kind": "telepathy", "locator": "l"})


def test_provider_kind_coerce_round_trip_and_failure():
    assert ProviderKind.coerce("document") is ProviderKind.DOCUMENT
    with pytest.raises(UnitError):
        ProviderKind.coerce("nope")


# ---------------------------------------------------------------------------
# RelationDeclaration
# ---------------------------------------------------------------------------


def test_relation_declaration_round_trips():
    declaration = RelationDeclaration(RelationType.DEPENDS_ON, "UKID-ABC", "note")
    assert RelationDeclaration.from_dict(declaration.to_dict()) == declaration


def test_relation_declaration_validates():
    with pytest.raises(UnitError):
        RelationDeclaration(RelationType.DEPENDS_ON, "")
    with pytest.raises(UnitError):
        RelationDeclaration("depends-on", "target")
    with pytest.raises(UnitError):
        RelationDeclaration.from_dict("not a mapping")


# ---------------------------------------------------------------------------
# KnowledgeUnit shape rules
# ---------------------------------------------------------------------------


def test_unit_requires_key_title_statement_and_source():
    with pytest.raises(UnitError):
        make_unit("")
    with pytest.raises(UnitError):
        make_unit("k", title="   ")
    with pytest.raises(UnitError):
        make_unit("k", statement="")
    with pytest.raises(UnitError):
        make_unit("k", source={"provider_id": "p"})


def test_unit_rejects_malformed_attributes():
    with pytest.raises(UnitError):
        KnowledgeUnit(
            key="k",
            title="t",
            statement="s",
            source=make_source(),
            attributes=(("only-one",),),
        )


def test_create_accepts_attribute_mapping_and_sorts_it():
    unit = KnowledgeUnit.create(
        key="k",
        title="t",
        statement="s",
        source=make_source(),
        attributes={"z": "1", "a": "2"},
    )
    assert unit.attributes == (("a", "2"), ("z", "1"))
    assert unit.attribute("a") == "2"
    assert unit.attribute("missing", "fallback") == "fallback"
    assert unit.attribute_map() == {"a": "2", "z": "1"}


def test_with_relations_dedupes_and_orders():
    unit = make_unit("k").with_relations(
        [
            RelationDeclaration(RelationType.DEPENDS_ON, "b"),
            RelationDeclaration(RelationType.DEPENDS_ON, "a"),
            RelationDeclaration(RelationType.DEPENDS_ON, "b"),
        ]
    )
    assert [r.target for r in unit.relations] == ["a", "b"]


def test_with_classification_marks_the_unit_classified():
    raw = make_unit(
        "k", kind=None, authority=None, lifecycle=None, universe="", owner="", version=""
    )
    assert not raw.is_classified
    classified = raw.with_classification(
        kind=KnowledgeKind.FACT,
        authority=KnowledgeAuthority.ADVISORY,
        lifecycle=Lifecycle.DRAFT,
        universe="U",
        owner="O",
        version="1.0.0",
    )
    assert classified.is_classified


def test_unit_round_trips_through_dict():
    unit = make_unit(
        "k",
        tags=("x", "y"),
        relations=(RelationDeclaration(RelationType.GOVERNS, "t", "n"),),
    ).with_relations(())
    payload = unit.to_dict()
    payload["attributes"] = unit.attribute_map()
    restored = KnowledgeUnit.from_dict(payload)
    assert restored.knowledge_sha256() == unit.knowledge_sha256()
    assert restored.relations == unit.relations
    assert restored.tags == unit.tags


def test_from_dict_rejects_malformed_payloads():
    good = make_unit("k").to_dict()
    good["attributes"] = {}
    with pytest.raises(UnitError):
        KnowledgeUnit.from_dict("not a mapping")
    with pytest.raises(UnitError):
        KnowledgeUnit.from_dict({**good, "source": "nope"})
    with pytest.raises(UnitError):
        KnowledgeUnit.from_dict({**good, "relations": {"not": "a list"}})
    with pytest.raises(UnitError):
        KnowledgeUnit.from_dict({**good, "attributes": ["not", "a", "map"]})
    with pytest.raises(UnitError):
        KnowledgeUnit.from_dict({**good, "tags": "not-a-list"})
    with pytest.raises(UnitError):
        KnowledgeUnit.from_dict({**good, "tags": [""]})
    with pytest.raises(UnitError):
        KnowledgeUnit.from_dict({**good, "rationale": 42})


def test_from_dict_tolerates_absent_classification():
    payload = {
        "key": "k",
        "title": "t",
        "statement": "s",
        "source": make_source().to_dict(),
    }
    unit = KnowledgeUnit.from_dict(payload)
    assert not unit.is_classified
    assert unit.kind is None


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------


def test_normalize_text_collapses_whitespace():
    assert normalize_text("  a\n\tb   c ") == "a b c"


def test_unit_document_is_deterministic_and_ordered():
    units = (
        make_unit("z", source=make_source(provider_id="b")),
        make_unit("a", source=make_source(provider_id="a")),
    )
    document = unit_document(units)
    assert document["count"] == 2
    assert [u["source"]["provider_id"] for u in document["units"]] == ["a", "b"]
    assert unit_document(units) == unit_document(reversed(units))


def test_a_raw_record_carrying_a_validity_window_is_refused_rather_than_guessed():
    """REFERRED, NOT REPAIRED — and the refusal is the honest form of that.

    ``engine.temporal`` (CMG-000002) declares no ``ValidityPeriod.from_dict``, so rehydrating
    a window from a wire record would mean inventing a parse for another owner's type. The
    two dishonest alternatives are both worse than raising: dropping the field silently
    turns a time-bounded claim into a timeless one, and guessing a parse authors a second
    definition of a primitive that already has an owner.

    A record with no validity still round-trips, so the refusal is about the gap and not
    about the wire format.
    """
    timeless = RelationDeclaration(RelationType.DEPENDS_ON, "UCKO-T", "note").to_dict()
    assert RelationDeclaration.from_dict(timeless).target == "UCKO-T"

    with pytest.raises(UnitError) as excinfo:
        RelationDeclaration.from_dict({**timeless, "validity": {"since": {}, "until": None}})
    assert "ValidityPeriod.from_dict" in str(excinfo.value)
    assert excinfo.value.context["at"] == "relation.validity"
