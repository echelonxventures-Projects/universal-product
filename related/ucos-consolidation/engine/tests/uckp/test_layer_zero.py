"""Layer Zero: the canonical primitive, the error taxonomy, identity, facets, values.

These are the modules everything else is built on, so the tests are about properties
rather than examples: determinism, purity, totality, and refusal.
"""

from __future__ import annotations

import dataclasses
import uuid

import pytest

from engine.foundation.obs.errors import FoundationError
from engine.uckp.canonical import (
    CANONICAL_PROFILE,
    DIGEST_ALGORITHM,
    canonical_bytes,
    canonical_json,
    content_hash,
    digests_match,
)
from engine.uckp.errors import (
    FacetError,
    IdentityError,
    UCKPError,
)
from engine.uckp.facets import FACET_ATTRIBUTES, REQUIRED_FACETS, Facet
from engine.uckp.identity import (
    UCKO_URN_PREFIX,
    UCKP_NAMESPACE_NAME,
    UCKP_NAMESPACE_UUID,
    UniversalIdentity,
    urn_for,
    uuid_for,
)
from engine.uckp.payload import canonical_payload
from engine.uckp.values import (
    Attestation,
    AuditEntry,
    AuthorityBinding,
    Constraint,
    ContextBinding,
    DiscoveryDescriptor,
    EvidenceRef,
    MetadataSet,
    OntologyRef,
    Ownership,
    PersistenceBinding,
    Policy,
    ProjectionBinding,
    ProvenanceStep,
    Relationship,
    ReplayProof,
    SemanticIdentity,
    TaxonomyRef,
    TemporalEvent,
    TraceLink,
)

# --- canonical primitive --------------------------------------------------------


def test_canonical_json_is_sorted_compact_and_unicode_preserving():
    assert canonical_json({"b": 1, "a": 2}) == '{"a":2,"b":1}'
    assert canonical_json({"k": "héllo ✓"}) == '{"k":"héllo ✓"}'


def test_canonical_json_is_order_independent():
    assert canonical_json({"a": 1, "b": 2}) == canonical_json({"b": 2, "a": 1})


def test_canonical_bytes_is_utf8_of_canonical_json():
    payload = {"k": "ünïcode"}
    assert canonical_bytes(payload) == canonical_json(payload).encode("utf-8")


def test_content_hash_is_deterministic_across_calls():
    payload = {"nested": [1, {"a": None}], "t": True}
    assert content_hash(payload) == content_hash(payload)
    assert len(content_hash(payload)) == 64


def test_content_hash_distinguishes_different_content():
    assert content_hash({"a": 1}) != content_hash({"a": 2})


def test_digests_match_is_canonical_equality_not_object_equality():
    assert digests_match({"a": 1, "b": 2}, {"b": 2, "a": 1})
    assert not digests_match({"a": 1}, {"a": "1"})


def test_the_primitive_declares_the_profile_that_produced_it():
    # A digest that cannot name its normalization is not replayable across serializers.
    assert DIGEST_ALGORITHM == "sha256"
    assert CANONICAL_PROFILE.startswith("ucos-uckp-canonical-json/")


def test_layer_zero_imports_only_the_standard_library():
    """The property that makes Layer Zero safe for the whole repository to depend on."""
    import ast
    from pathlib import Path

    source = Path(canonical_json.__code__.co_filename).read_text(encoding="utf-8")
    imported: set[str] = set()
    for node in ast.walk(ast.parse(source)):
        if isinstance(node, ast.Import):
            imported.update(alias.name.split(".")[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imported.add(node.module.split(".")[0])
    assert imported <= {"hashlib", "json", "typing", "__future__"}


# --- errors ---------------------------------------------------------------------


def test_every_uckp_error_is_a_foundation_error_with_a_stable_code():
    assert issubclass(UCKPError, FoundationError)
    assert UCKPError.code == "UCKP-000"
    assert IdentityError.code == "UCKP-IDENTITY-001"


def test_errors_carry_structured_context():
    error = IdentityError("bad identity", urn="urn:x")
    assert "bad identity" in str(error)


# --- identity -------------------------------------------------------------------


def test_minting_is_pure_and_reproducible():
    first = UniversalIdentity.mint("ucos", "THING-1")
    second = UniversalIdentity.mint("ucos", "THING-1")
    assert first == second
    assert first.urn == f"{UCKO_URN_PREFIX}:ucos:THING-1"


def test_identity_reads_no_clock_and_no_location():
    identity = UniversalIdentity.mint("ucos", "THING-1")
    record = identity.to_dict()
    assert set(record) == {"namespace", "local_name", "urn", "uuid"}


def test_uuid_is_name_based_version_five():
    identity = UniversalIdentity.mint("ucos", "THING-1")
    assert uuid.UUID(identity.uuid).version == 5
    assert identity.uuid == uuid_for(identity.urn)
    assert UCKP_NAMESPACE_UUID == uuid.uuid5(uuid.NAMESPACE_URL, UCKP_NAMESPACE_NAME)


def test_parse_is_the_inverse_of_minting():
    identity = UniversalIdentity.mint("ucos", "THING-1")
    assert UniversalIdentity.parse(identity.urn) == identity


@pytest.mark.parametrize("bad", ["", "not-a-urn", "urn:ucos:ucko:onlynamespace"])
def test_parse_refuses_a_malformed_urn(bad):
    with pytest.raises(IdentityError):
        UniversalIdentity.parse(bad)


@pytest.mark.parametrize("namespace", ["UPPER", "", "has space", "-leading"])
def test_mint_refuses_a_malformed_namespace(namespace):
    with pytest.raises(IdentityError):
        UniversalIdentity.mint(namespace, "NAME")


@pytest.mark.parametrize("local", ["", "has space", "-leading", "x" * 200])
def test_mint_refuses_a_malformed_local_name(local):
    with pytest.raises(IdentityError):
        UniversalIdentity.mint("ucos", local)


def test_verify_detects_a_post_hoc_edit_of_a_derived_field():
    identity = UniversalIdentity.mint("ucos", "THING-1")
    assert identity.verify()
    identity.require_intact()
    tampered = UniversalIdentity(
        namespace="ucos", local_name="THING-1", urn=identity.urn, uuid="0" * 36
    )
    assert not tampered.verify()
    with pytest.raises(IdentityError):
        tampered.require_intact()


def test_an_identity_may_never_change_once_minted():
    identity = UniversalIdentity.mint("ucos", "THING-1")
    identity.require_unchanged(UniversalIdentity.mint("ucos", "THING-1"))
    with pytest.raises(IdentityError):
        identity.require_unchanged(UniversalIdentity.mint("ucos", "THING-2"))


def test_from_dict_refuses_a_declared_field_that_contradicts_the_minting_function():
    identity = UniversalIdentity.mint("ucos", "THING-1")
    assert UniversalIdentity.from_dict(identity.to_dict()) == identity
    with pytest.raises(IdentityError):
        UniversalIdentity.from_dict({**identity.to_dict(), "urn": "urn:ucos:ucko:ucos:OTHER"})
    with pytest.raises(IdentityError):
        UniversalIdentity.from_dict({**identity.to_dict(), "uuid": "0" * 36})
    with pytest.raises(IdentityError):
        UniversalIdentity.from_dict("not a mapping")


def test_identity_renders_as_its_urn():
    assert str(UniversalIdentity.mint("ucos", "X")) == "urn:ucos:ucko:ucos:X"


def test_urn_for_is_pure():
    assert urn_for("a", "B") == "urn:ucos:ucko:a:B"


# --- facets ---------------------------------------------------------------------


def test_there_are_thirty_three_facets_and_all_are_required():
    assert len(Facet) == 33
    assert REQUIRED_FACETS == tuple(Facet)


def test_required_facets_is_derived_from_the_enum_not_restated():
    # A new facet cannot be added and forgotten.
    assert set(REQUIRED_FACETS) == set(Facet)
    assert FACET_ATTRIBUTES == tuple(facet.value.replace("-", "_") for facet in Facet)


def test_every_facet_declares_the_question_it_answers():
    for facet in Facet:
        assert facet.question.endswith("?")


def test_facet_coerce_accepts_a_member_a_name_and_refuses_a_stranger():
    assert Facet.coerce(Facet.IDENTITY) is Facet.IDENTITY
    assert Facet.coerce("semantic-identity") is Facet.SEMANTIC_IDENTITY
    assert Facet.coerce(" AUDIT ") is Facet.AUDIT
    with pytest.raises(FacetError):
        Facet.coerce("no-such-facet")


def test_facet_attribute_is_the_python_name():
    assert Facet.SEMANTIC_IDENTITY.attribute == "semantic_identity"


# --- values ---------------------------------------------------------------------


def test_semantic_identity_digests_meaning_and_normalises_it():
    left = SemanticIdentity(concept="  Thing ", definition="A  Meaning ")
    right = SemanticIdentity(concept="thing", definition="a meaning")
    assert left.digest() == right.digest()
    assert "concept" in left.normalised()


def test_semantic_digest_changes_when_meaning_changes():
    assert SemanticIdentity("a", "x").digest() != SemanticIdentity("a", "y").digest()


def test_replay_proof_holds_only_for_the_output_it_certifies():
    proof = ReplayProof(procedure="p/1.0.0", input_digest="in", output_digest="out")
    assert proof.holds("out")
    assert not proof.holds("other")


def test_metadata_set_is_ordered_and_addressable():
    metadata = MetadataSet.of({"b": 1, "a": 2}, c=3)
    assert metadata.keys() == ("a", "b", "c")
    assert metadata.get("a") == "2"
    assert metadata.get("missing", "fallback") == "fallback"
    assert metadata.as_dict() == {"a": "2", "b": "1", "c": "3"}


def test_authority_binding_requires_a_parent():
    with pytest.raises(FacetError):
        AuthorityBinding(tier="constitutional", derives_from="")
    with pytest.raises(FacetError):
        AuthorityBinding(tier="", derives_from="urn:x")


@pytest.mark.parametrize(
    "value",
    [
        Attestation("certification"),
        AuditEntry(actor="a", action="b", subject="c"),
        AuthorityBinding(tier="constitutional", derives_from="urn:x"),
        Constraint(constraint_id="C", expression="always"),
        ContextBinding("security", "open"),
        DiscoveryDescriptor(),
        EvidenceRef(evidence_id="E", digest="d", kind="k", locator="l"),
        MetadataSet.of({"a": "b"}),
        OntologyRef(ontology_id="o", class_id="c"),
        Ownership(owner="o"),
        PersistenceBinding("git", "loc", False),
        Policy(policy_id="P", statement="s", enforcement="fail-closed"),
        ProjectionBinding("json", "t", True, False),
        ProvenanceStep(actor="a", action="b", source="s"),
        Relationship("depends-on", "urn:x", "knowledge"),
        ReplayProof(procedure="p", input_digest="i", output_digest="o"),
        SemanticIdentity(concept="c", definition="d"),
        TaxonomyRef(kind="fact", category="knowledge"),
        TemporalEvent(sequence=0, event="e"),
        TraceLink(upstream="u", downstream="d", kind="requirement"),
    ],
)
def test_every_value_round_trips_through_its_own_dict_form(value):
    """Serializability is a constitutional requirement, not a convenience."""
    record = value.to_dict()
    assert content_hash(record) == content_hash(type(value).from_dict(record).to_dict())


def test_attestation_defaults_to_unattested_and_never_to_attested():
    assert not Attestation("certification").attested


def test_unattested_is_distinguishable_from_absent():
    # Article 6: a facet may be unattested but never absent.
    attestation = Attestation("validation")
    assert attestation.to_dict()["kind"] == "validation"
    assert not attestation.attested


def test_the_canonical_payload_refuses_a_value_it_would_have_to_guess_about() -> None:
    """INVERSION IS THE REMEDY, AND REFUSAL IS WHAT KEEPS IT HONEST.

    Every declaration this renders is built from scalars, mappings, sequences, sets and other
    dataclasses, so the refusal at the end had no case — and it is the whole reason the
    renderer is safe to invert. A value it cannot render has exactly two other options:
    render it as its ``repr``, which puts a memory address into a certification identity and
    makes the digest non-deterministic, or drop it, which leaves a field out of the identity
    the inversion promised would be there. Refusing is the only answer that keeps "a new
    field is covered on the day it is written" true.

    The arms it DOES render are asserted beside it, because a refusal with no admitted cases
    is indistinguishable from a renderer that refuses everything.
    """

    @dataclasses.dataclass(frozen=True)
    class _Declared:
        name: str
        weights: tuple[int, ...]
        labels: frozenset[str]
        nested: dict[str, int]

    rendered = canonical_payload(_Declared("n", (1, 2), frozenset({"b", "a"}), {"k": 1}))

    assert rendered == {
        "name": "n",
        "weights": [1, 2],
        "labels": ["a", "b"],
        "nested": {"k": 1},
    }
    assert canonical_payload(_Declared("n", (1, 2), frozenset(), {}), exclude=("name",)) == {
        "weights": [1, 2],
        "labels": [],
        "nested": {},
    }

    with pytest.raises(TypeError, match="without guessing"):
        canonical_payload(object())
    with pytest.raises(TypeError, match="without guessing"):
        canonical_payload({"declared": object()})
