"""The canonical object, the knowledge graph, and admission into the registry.

Articles 2 (canonical existence), 3 (zero duplication), 7 (executable relationships)
and 18 (reuse before create). The negative tests matter most here: this is where the
law is actually enforced, so each refusal needs a test that proves the refusal happens.
"""

from __future__ import annotations

import dataclasses

import pytest

from engine.uckp.errors import (
    CircularAuthorityError,
    DuplicateAuthorityError,
    FacetError,
    IntegrityError,
    LawViolation,
    RelationshipError,
    UnknownObjectError,
)
from engine.uckp.facets import REQUIRED_FACETS, Facet
from engine.uckp.graph import (
    OBJECT_SCOPE,
    UniversalKnowledgeEdge,
    UniversalKnowledgeGraph,
    derive_edges,
)
from engine.uckp.identity import urn_for
from engine.uckp.registry import (
    REGISTERED,
    REUSED,
    UniversalKnowledgeRegistry,
)
from engine.uckp.ucko import MINT_PROCEDURE, UCKO
from engine.uckp.values import (
    Attestation,
    AuditEntry,
    EvidenceRef,
    PersistenceBinding,
    ProjectionBinding,
    Relationship,
    RuntimeBinding,
)
from engine.uckp.vocabulary import build_vocabulary_registry

TEST_NAMESPACE = "test"

# --- the object -----------------------------------------------------------------


def test_a_minted_object_answers_every_facet(minimal_root):
    assert minimal_root.missing_facets() == ()
    minimal_root.require_complete()
    for facet in REQUIRED_FACETS:
        minimal_root.facet_value(facet)  # total: never raises


def test_facet_value_is_total_over_every_facet_and_refuses_a_stranger(minimal_root):
    assert minimal_root.facet_value("identity") is minimal_root.identity
    assert minimal_root.facet_value(Facet.LIFECYCLE) == minimal_root.lifecycle
    with pytest.raises(FacetError):
        minimal_root.facet_value("no-such-facet")


def test_an_incomplete_object_is_representable_and_refused(minimal_root):
    """A law that cannot be violated in the type system is a law never tested."""
    broken = dataclasses.replace(minimal_root, lifecycle="")
    assert Facet.LIFECYCLE in broken.missing_facets()
    with pytest.raises(FacetError, match="every universal facet"):
        broken.require_complete()


def test_the_seal_detects_any_edit_after_sealing(minimal_root):
    assert minimal_root.verify_integrity()
    minimal_root.require_integrity()
    tampered = dataclasses.replace(minimal_root, lifecycle="archived")
    assert not tampered.verify_integrity()
    with pytest.raises(IntegrityError):
        tampered.require_integrity()


def test_minting_records_a_replay_proof_that_holds(minimal_root):
    assert minimal_root.replay is not None
    assert minimal_root.replay.procedure == MINT_PROCEDURE
    assert minimal_root.verify_replay()


def test_the_substance_digest_excludes_the_proof_it_certifies(minimal_root):
    """Otherwise the assertion would be self-referential rather than well-founded."""
    without = dataclasses.replace(minimal_root, replay=None)
    assert without.substance_digest() == minimal_root.substance_digest()


def test_semantic_digest_hashes_meaning_alone_so_renaming_hides_nothing(mint_object, root_urn):
    left = mint_object("A", derives_from=root_urn, concept="same", definition="identical meaning")
    right = mint_object("B", derives_from=root_urn, concept="same", definition="identical meaning")
    assert left.ucko_id != right.ucko_id
    assert left.semantic_digest() == right.semantic_digest()


def test_minting_is_deterministic(root_urn, mint_object):
    first = mint_object("A", derives_from=root_urn)
    second = mint_object("A", derives_from=root_urn)
    assert first.content_sha256 == second.content_sha256


def test_an_object_self_describes(minimal_root):
    described = minimal_root.describe()
    assert described["ucko_id"] == minimal_root.ucko_id
    assert described["semantic_digest"] == minimal_root.semantic_digest()
    assert len(described["facets"]) == 33
    assert minimal_root.discovery.discoverable and minimal_root.discovery.self_describing


def test_an_object_round_trips_through_its_dict_form(minimal_child):
    restored = UCKO.from_dict(minimal_child.to_dict())
    assert restored.content_sha256 == minimal_child.content_sha256
    assert restored.to_dict() == minimal_child.to_dict()


def test_from_dict_refuses_a_record_whose_seal_does_not_match(minimal_root):
    record = minimal_root.to_dict()
    record["lifecycle"] = "archived"
    with pytest.raises(IntegrityError):
        UCKO.from_dict(record)


def test_from_dict_reseals_a_record_carrying_no_seal(minimal_root):
    record = minimal_root.to_dict()
    record.pop("content_sha256")
    assert UCKO.from_dict(record).content_sha256 == minimal_root.content_sha256


def test_from_dict_refuses_a_non_mapping():
    with pytest.raises(FacetError):
        UCKO.from_dict(["not", "a", "mapping"])


def test_require_lawful_refuses_an_unregistered_term(minimal_root, vocabularies, root_urn):
    minimal_root.require_lawful(vocabularies)
    unlawful = UCKO.mint(
        namespace=TEST_NAMESPACE,
        local_name="X",
        concept="c",
        definition="d",
        kind="no-such-kind",
        category="knowledge",
        authority_tier="engineering",
        derives_from=root_urn,
        owner="o",
    )
    with pytest.raises(LawViolation, match="not registered in this vocabulary"):
        unlawful.require_lawful(vocabularies)


def test_lifecycle_transition_is_lawful_only_along_declared_successors(minimal_root, vocabularies):
    # 'ratified' declares implemented / deprecated / superseded as its successors, so
    # 'operational' is two lawful steps away and not one.
    moved = minimal_root.transition_to("implemented", vocabularies)
    assert moved.lifecycle == "implemented"
    assert moved.verify_integrity() and moved.verify_replay()
    assert len(moved.temporal_history) == len(minimal_root.temporal_history) + 1
    assert len(moved.audit) == len(minimal_root.audit) + 1
    assert moved.transition_to("operational", vocabularies).lifecycle == "operational"
    with pytest.raises(LawViolation, match="unlawful lifecycle transition"):
        minimal_root.transition_to("no-such-stage", vocabularies)
    with pytest.raises(LawViolation, match="unlawful lifecycle transition"):
        minimal_root.transition_to("operational", vocabularies)


def test_a_transition_never_mutates_the_object_it_came_from(minimal_root, vocabularies):
    before = minimal_root.content_sha256
    minimal_root.transition_to("implemented", vocabularies)
    assert minimal_root.content_sha256 == before


def test_an_attested_verdict_must_name_the_authority_that_gave_it(minimal_root):
    """An attestation with no attesting authority is an unsourced claim."""
    with pytest.raises(FacetError, match="must name its authority"):
        Attestation("certification", verdict="certified")


@pytest.mark.parametrize(
    "mutate",
    [
        lambda obj: obj.with_relationships(Relationship("references", "urn:x", "knowledge")),
        lambda obj: obj.with_projection_binding(ProjectionBinding("json", "t", True, False)),
        lambda obj: obj.with_persistence_binding(PersistenceBinding("git", "l", False)),
        lambda obj: obj.with_runtime_binding(RuntimeBinding("python", "c", "a")),
        lambda obj: obj.with_attestation(
            Attestation("certification", verdict="certified", authority="test-certifier")
        ),
        lambda obj: obj.with_evidence(EvidenceRef("E", "d", "k", "l")),
        lambda obj: obj.with_evolution_state("state-1"),
        lambda obj: obj.with_audit(AuditEntry(actor="a", action="b", subject="c")),
    ],
)
def test_every_lawful_change_reseals_and_reproves(minimal_root, mutate):
    changed = mutate(minimal_root)
    assert changed.verify_integrity()
    assert changed.verify_replay()
    assert changed.content_sha256 != minimal_root.content_sha256


def test_with_relationships_is_idempotent_and_ordered(minimal_root):
    relationship = Relationship("references", "urn:x", "knowledge")
    once = minimal_root.with_relationships(relationship)
    twice = once.with_relationships(relationship)
    assert once.content_sha256 == twice.content_sha256


def test_with_evolution_state_is_idempotent(minimal_root):
    once = minimal_root.with_evolution_state("s1")
    assert once.with_evolution_state("s1") is once


def test_with_attestation_refuses_an_unknown_kind(minimal_root):
    with pytest.raises(FacetError, match="unknown attestation kind"):
        minimal_root.with_attestation(Attestation("no-such-kind"))


def test_unattested_facets_are_reported_and_clear_once_attested(minimal_root):
    assert set(minimal_root.unattested_facets()) == {
        Facet.CERTIFICATION,
        Facet.VALIDATION,
        Facet.VERIFICATION,
    }
    attested = minimal_root.with_attestation(
        Attestation("certification", verdict="certified", authority="a", standard="s")
    )
    assert Facet.CERTIFICATION not in attested.unattested_facets()


def test_referenced_ids_names_every_object_the_object_points_at(minimal_child, minimal_root):
    assert minimal_root.ucko_id in minimal_child.referenced_ids()


def test_a_self_grounding_root_does_not_reference_itself(minimal_root):
    assert minimal_root.ucko_id not in minimal_root.referenced_ids()


# --- the graph ------------------------------------------------------------------


def test_every_facet_relationship_becomes_an_edge(minimal_child):
    edges = derive_edges(minimal_child)
    assert edges
    assert all(isinstance(edge, UniversalKnowledgeEdge) for edge in edges)
    assert any(edge.relationship_class == "authority" for edge in edges)


def test_edge_derivation_is_deterministic_and_deduplicated(minimal_child):
    first = derive_edges(minimal_child)
    assert first == derive_edges(minimal_child)
    assert len({edge.key() for edge in first}) == len(first)


def test_the_graph_resolves_nodes_and_refuses_unknown_ones(minimal_registry, minimal_root):
    graph = minimal_registry.graph()
    assert graph.require_node(minimal_root.ucko_id).ucko_id == minimal_root.ucko_id
    assert graph.node("urn:ucos:ucko:test:NOPE") is None
    with pytest.raises(UnknownObjectError):
        graph.require_node("urn:ucos:ucko:test:NOPE")


def test_an_authority_chain_terminates_at_the_self_grounding_root(
    minimal_registry, minimal_root, minimal_child
):
    chain = minimal_registry.graph().authority_chain(minimal_child.ucko_id)
    assert chain[0] == minimal_child.ucko_id
    assert chain[-1] == minimal_root.ucko_id


def test_a_coherent_graph_has_no_dangling_edge_and_no_orphan(minimal_registry, minimal_root):
    graph = minimal_registry.graph()
    assert graph.dangling() == ()
    assert graph.orphans(minimal_root.ucko_id) == ()
    graph.require_acyclic_authority()


def test_a_relationship_to_a_nonexistent_object_dangles(mint_object, root_urn, vocabularies):
    """Article 7: a relationship that cannot be resolved is not a relationship."""
    orphaned = mint_object(
        "A",
        derives_from=root_urn,
        relationships=(Relationship("references", urn_for("test", "GHOST"), "knowledge"),),
    )
    graph = UniversalKnowledgeGraph((orphaned,))
    dangling = graph.dangling()
    assert dangling
    assert any(edge.target.endswith("GHOST") for edge in dangling)


def test_a_dangling_edge_cannot_be_executed(mint_object, root_urn):
    orphaned = mint_object(
        "A",
        derives_from=root_urn,
        relationships=(Relationship("references", urn_for("test", "GHOST"), "knowledge"),),
    )
    graph = UniversalKnowledgeGraph((orphaned,))
    ghost = next(edge for edge in graph.dangling() if edge.target.endswith("GHOST"))
    with pytest.raises((UnknownObjectError, RelationshipError)):
        graph.execute(ghost)


def test_an_executable_relationship_resolves_to_the_object_it_names(
    minimal_registry, minimal_child, minimal_root
):
    graph = minimal_registry.graph()
    edge = next(
        e
        for e in graph.out_edges(minimal_child.ucko_id)
        if e.target == minimal_root.ucko_id and e.scope == OBJECT_SCOPE
    )
    assert graph.execute(edge).ucko_id == minimal_root.ucko_id


def test_a_circular_authority_chain_is_refused(vocabularies):
    left_urn = urn_for(TEST_NAMESPACE, "LEFT")
    right_urn = urn_for(TEST_NAMESPACE, "RIGHT")
    left = UCKO.mint(
        namespace=TEST_NAMESPACE,
        local_name="LEFT",
        concept="left",
        definition="derives from right",
        kind="fact",
        category="knowledge",
        authority_tier="engineering",
        derives_from=right_urn,
        owner="o",
    )
    right = UCKO.mint(
        namespace=TEST_NAMESPACE,
        local_name="RIGHT",
        concept="right",
        definition="derives from left",
        kind="fact",
        category="knowledge",
        authority_tier="engineering",
        derives_from=left_urn,
        owner="o",
    )
    graph = UniversalKnowledgeGraph((left, right))
    assert graph.cycles("authority")
    with pytest.raises(CircularAuthorityError):
        graph.require_acyclic_authority()


def test_reachability_and_neighbours_are_derived_from_the_edges(
    minimal_registry, minimal_root, minimal_child
):
    graph = minimal_registry.graph()
    assert minimal_root.ucko_id in graph.neighbours(minimal_child.ucko_id)
    assert minimal_child.ucko_id in graph.reachable_from(minimal_child.ucko_id)
    assert graph.in_edges(minimal_root.ucko_id)


def test_the_graph_fingerprint_is_deterministic(minimal_registry):
    graph = minimal_registry.graph()
    assert graph.fingerprint() == graph.fingerprint()


def test_the_graph_counts_and_document_describe_it(minimal_registry):
    graph = minimal_registry.graph()
    counts = graph.counts()
    assert counts["nodes"] == 2
    document = graph.to_document()
    assert document["counts"]["nodes"] == 2
    assert graph.relationship_classes()
    assert graph.node_ids() and graph.nodes() and graph.roots() is not None
    assert graph.adjacency()
    assert graph.edges_of_class("authority")
    assert UniversalKnowledgeGraph.from_objects(graph.nodes()).fingerprint() == graph.fingerprint()


# --- the registry ---------------------------------------------------------------


def test_registration_admits_a_lawful_object(minimal_root, vocabularies):
    registry = UniversalKnowledgeRegistry(vocabularies=vocabularies)
    admission = registry.register(minimal_root)
    assert admission.outcome == REGISTERED
    assert registry.get(minimal_root.ucko_id) is not None
    assert registry.require(minimal_root.ucko_id).ucko_id == minimal_root.ucko_id


def test_registering_the_identical_object_twice_is_reuse_not_duplication(
    minimal_root, vocabularies
):
    """Article 18: reuse before create."""
    registry = UniversalKnowledgeRegistry(vocabularies=vocabularies)
    registry.register(minimal_root)
    assert registry.register(minimal_root).outcome == REUSED
    assert len(registry.objects()) == 1


def test_a_different_object_claiming_an_existing_identity_is_refused(
    minimal_root, vocabularies, minimal_registry
):
    impostor = dataclasses.replace(minimal_root, semantic_identity=minimal_root.semantic_identity)
    impostor = UCKO.mint(
        namespace=TEST_NAMESPACE,
        local_name="ROOT",
        concept="a different meaning",
        definition="claiming the same identity",
        kind="law",
        category="law",
        authority_tier="constitutional",
        derives_from=minimal_root.ucko_id,
        owner="o",
    )
    with pytest.raises(DuplicateAuthorityError, match="claims an existing identity"):
        minimal_registry.register(impostor)


def test_the_same_meaning_under_a_second_identity_is_refused(minimal_registry, minimal_root):
    """Article 3: a second definition of existing knowledge is a competing authority."""
    twin = UCKO.mint(
        namespace=TEST_NAMESPACE,
        local_name="ROOT-COPY",
        concept=minimal_root.semantic_identity.concept,
        definition=minimal_root.semantic_identity.definition,
        kind="law",
        category="law",
        authority_tier="constitutional",
        derives_from=minimal_root.ucko_id,
        owner="o",
    )
    with pytest.raises(DuplicateAuthorityError, match="already exists under another identity"):
        minimal_registry.register(twin)


def test_locate_finds_the_canonical_home_of_a_meaning(minimal_registry, minimal_root):
    found = minimal_registry.locate(
        minimal_root.semantic_identity.concept, minimal_root.semantic_identity.definition
    )
    assert found is not None and found.ucko_id == minimal_root.ucko_id
    assert minimal_registry.locate("nothing", "nowhere") is None


def test_require_refuses_an_unknown_identity(minimal_registry):
    with pytest.raises(UnknownObjectError):
        minimal_registry.require("urn:ucos:ucko:test:NOPE")


def test_exactly_one_constitutional_root_is_required(minimal_registry, minimal_root, mint_object):
    assert minimal_registry.require_single_root() == minimal_root.ucko_id
    second_root_urn = urn_for(TEST_NAMESPACE, "ROOT-2")
    minimal_registry.register(mint_object("ROOT-2", derives_from=second_root_urn))
    with pytest.raises(LawViolation, match="exactly one constitutional root"):
        minimal_registry.require_single_root()


def test_the_registry_indexes_by_every_declared_dimension(minimal_registry, minimal_root):
    assert minimal_registry.by_kind("law")
    assert minimal_registry.by_category("law")
    assert minimal_registry.by_authority("constitutional")
    assert minimal_registry.by_lifecycle(minimal_root.lifecycle)
    assert minimal_registry.by_owner("test-authority")
    assert minimal_registry.by_semantic_digest(minimal_root.semantic_digest()) is not None


def test_search_finds_by_free_text(minimal_registry):
    assert minimal_registry.search("root")
    assert minimal_registry.search("zzz-nothing") == ()


def test_the_registry_seal_is_deterministic_and_changes_with_content(
    minimal_registry, mint_object, root_urn
):
    before = minimal_registry.seal()
    assert before == minimal_registry.seal()
    minimal_registry.register(mint_object("EXTRA", derives_from=root_urn))
    assert minimal_registry.seal() != before


def test_replace_evolves_an_object_under_the_same_identity(
    minimal_registry, minimal_root, vocabularies
):
    moved = minimal_root.transition_to("implemented", vocabularies)
    replaced = minimal_registry.replace(moved)
    assert replaced.lifecycle == "implemented"
    assert minimal_registry.require(minimal_root.ucko_id).lifecycle == "implemented"


def test_replace_refuses_an_identity_that_does_not_exist(minimal_registry, mint_object, root_urn):
    with pytest.raises(UnknownObjectError):
        minimal_registry.replace(mint_object("ABSENT", derives_from=root_urn))


def test_duplicate_semantics_reports_nothing_for_a_lawful_registry(minimal_registry):
    assert minimal_registry.duplicate_semantics() == ()


def test_the_registry_describes_and_documents_itself(minimal_registry):
    described = minimal_registry.describe()
    assert described
    document = minimal_registry.to_document()
    assert document["counts"]["objects"] == 2
    assert minimal_registry.counts()["objects"] == 2
    assert minimal_registry.admissions()
    assert minimal_registry.providers()
    assert minimal_registry.ids()
    assert minimal_registry.vocabularies() is not None
    assert minimal_registry.authority_of(minimal_registry.require_single_root())


def test_discovery_finds_providers_without_manual_enumeration():
    """Article 8: nothing shall require manual enumeration."""
    registry = UniversalKnowledgeRegistry(vocabularies=build_vocabulary_registry())
    report = registry.discover("engine.uckp")
    assert report.providers_found
    assert report.objects_admitted > 0
    assert report.failures == ()
    assert report.modules_scanned > 1
    assert report.to_dict()["objects_admitted"] == report.objects_admitted


def test_discovery_records_an_unimportable_root_rather_than_raising():
    registry = UniversalKnowledgeRegistry(vocabularies=build_vocabulary_registry())
    report = registry.discover("engine.uckp.no_such_module_at_all")
    assert report.failures


# --- facet values: the coercions every ``from_dict`` depends on -------------------


def test_an_absent_sequence_or_mapping_decodes_to_the_empty_one():
    """A record that omits an optional facet is incomplete, not malformed."""
    from engine.uckp.values import DiscoveryDescriptor, MetadataSet

    assert DiscoveryDescriptor.from_dict(None).keywords == ()
    assert MetadataSet.from_dict(None).to_dict() == {}


def test_a_string_offered_where_a_sequence_belongs_is_refused():
    """``"abc"`` is iterable, so accepting it would silently produce three keywords."""
    from engine.uckp.values import DiscoveryDescriptor

    with pytest.raises(FacetError, match="must be a sequence, not a string"):
        DiscoveryDescriptor.from_dict({"keywords": "abc"})


def test_a_non_mapping_offered_where_a_facet_record_belongs_is_refused():
    from engine.uckp.values import ContextBinding

    with pytest.raises(FacetError, match="must be a mapping"):
        ContextBinding.from_dict("security")


def test_a_projection_that_claims_authority_or_is_not_generated_is_refused():
    """Article 4 in the type system: the binding cannot be constructed at all."""
    from engine.uckp.errors import ProjectionAuthorityError

    with pytest.raises(ProjectionAuthorityError, match="may not hold authority"):
        ProjectionBinding("markdown", "docs/x.md", authoritative=True)
    with pytest.raises(ProjectionAuthorityError, match="not generated is an independent authority"):
        ProjectionBinding("markdown", "docs/x.md", generated=False)


def test_a_persistence_mechanism_that_claims_authority_is_refused():
    from engine.uckp.errors import ProjectionAuthorityError

    with pytest.raises(ProjectionAuthorityError, match="may not hold authority"):
        PersistenceBinding("git", "refs/heads/main", authoritative=True)


# --- the object: an unanswered facet ---------------------------------------------


def test_a_facet_holding_none_is_reported_absent(minimal_root):
    """``replay`` is a facet, so an object with no proof is an incomplete object."""
    proofless = dataclasses.replace(minimal_root, replay=None)
    assert Facet.REPLAY in proofless.missing_facets()
    with pytest.raises(FacetError, match="does not answer every universal facet"):
        proofless.require_complete()


# --- the graph: edges, membership, resolution ------------------------------------


def test_an_evolution_state_becomes_a_state_scoped_edge(minimal_root):
    """The states an object passed through are part of its graph, not of its identity."""
    with_state = minimal_root.with_evolution_state("state-0001")
    edges = derive_edges(with_state)
    evolution = [edge for edge in edges if edge.relationship_class == "evolution"]
    assert [edge.target for edge in evolution] == ["state-0001"]
    assert all(edge.scope != OBJECT_SCOPE for edge in evolution)


def test_the_graph_refuses_the_same_object_twice(minimal_root):
    with pytest.raises(RelationshipError, match="appears twice in a graph"):
        UniversalKnowledgeGraph((minimal_root, minimal_root))


def test_the_graph_reports_its_size_and_membership(minimal_root, minimal_child):
    graph = UniversalKnowledgeGraph((minimal_root, minimal_child))
    assert len(graph) == 2
    assert minimal_root.ucko_id in graph
    assert urn_for(TEST_NAMESPACE, "ABSENT") not in graph


def test_only_an_object_scoped_edge_resolves_to_an_object(minimal_root):
    """An owner is not a UCKO, so an ownership edge must refuse to be dereferenced."""
    graph = UniversalKnowledgeGraph((minimal_root,))
    ownership = next(edge for edge in graph.edges() if edge.relationship_class == "ownership")
    with pytest.raises(RelationshipError, match="only object-scoped relationships"):
        graph.execute(ownership)


def test_reachability_from_an_identity_the_graph_does_not_hold_is_empty(minimal_root):
    graph = UniversalKnowledgeGraph((minimal_root,))
    assert graph.reachable_from(urn_for(TEST_NAMESPACE, "ABSENT")) == frozenset()


def test_an_authority_chain_that_re_enters_itself_is_refused(vocabularies):
    """Two objects deriving from each other: each chain walk would never terminate."""
    left_urn = urn_for(TEST_NAMESPACE, "LEFT")
    right_urn = urn_for(TEST_NAMESPACE, "RIGHT")
    left = UCKO.mint(
        namespace=TEST_NAMESPACE,
        local_name="LEFT",
        concept="left",
        definition="the left half of a circular authority",
        kind="rule",
        category="rule",
        authority_tier="engineering",
        derives_from=right_urn,
        owner="o",
    )
    right = UCKO.mint(
        namespace=TEST_NAMESPACE,
        local_name="RIGHT",
        concept="right",
        definition="the right half of a circular authority",
        kind="rule",
        category="rule",
        authority_tier="engineering",
        derives_from=left_urn,
        owner="o",
    )
    graph = UniversalKnowledgeGraph((left, right))
    with pytest.raises(CircularAuthorityError, match="re-enters itself"):
        graph.authority_chain(left_urn)


# --- the registry: admission records, iteration, replacement ---------------------


def test_an_admission_says_whether_it_created_a_home_and_serializes(minimal_root, vocabularies):
    registry = UniversalKnowledgeRegistry(vocabularies=vocabularies)
    created = registry.register(minimal_root)
    assert created.created_home is True
    reused = registry.register(minimal_root)
    assert reused.created_home is False
    record = reused.to_dict()
    assert record["outcome"] == REUSED
    assert record["ucko_id"] == minimal_root.ucko_id
    assert record["semantic_digest"] == minimal_root.semantic_digest()


def test_the_registry_admits_the_objects_it_is_constructed_with(minimal_root, minimal_child):
    registry = UniversalKnowledgeRegistry(
        (minimal_root, minimal_child), vocabularies=build_vocabulary_registry()
    )
    assert len(registry) == 2
    assert [obj.ucko_id for obj in registry] == list(registry.ids())


def test_searching_for_nothing_returns_nothing(minimal_registry):
    assert minimal_registry.search("   ") == ()


def _rehomed(obj: UCKO, concept: str, definition: str) -> UCKO:
    from engine.uckp.values import SemanticIdentity

    return dataclasses.replace(
        obj,
        semantic_identity=SemanticIdentity(concept=concept, definition=definition),
        replay=None,
    ).create_from_self()


def test_replacing_an_object_moves_its_meaning_to_the_same_home(minimal_registry, minimal_root):
    """Evolution changes what an object says; it never changes where it is homed."""
    successor = _rehomed(minimal_root, "test root law", "the same root, restated more precisely")
    minimal_registry.replace(successor)
    assert minimal_registry.require(minimal_root.ucko_id) is successor
    assert minimal_registry.by_semantic_digest(successor.semantic_digest()) is successor
    assert minimal_registry.by_semantic_digest(minimal_root.semantic_digest()) is None
    assert len(minimal_registry) == 2


def test_a_replacement_that_would_duplicate_another_home_is_refused(
    minimal_registry, minimal_root, minimal_child
):
    collision = _rehomed(
        minimal_root,
        minimal_child.semantic_identity.concept,
        minimal_child.semantic_identity.definition,
    )
    with pytest.raises(DuplicateAuthorityError, match="already homed elsewhere"):
        minimal_registry.replace(collision)


# --- the registry: discovery of strangers ---------------------------------------


def _write_package(tmp_path, name: str, modules: dict[str, str]) -> None:
    package = tmp_path / name
    package.mkdir()
    (package / "__init__.py").write_text("", encoding="utf-8")
    for module_name, body in modules.items():
        (package / f"{module_name}.py").write_text(body, encoding="utf-8")


def test_discovery_records_a_module_it_could_not_import_rather_than_raising(
    tmp_path, monkeypatch, vocabularies
):
    """One unimportable module must not make the whole universe unassemblable."""
    _write_package(
        tmp_path,
        "uckp_probe_broken",
        {"explodes": "raise RuntimeError('this module refuses to load')\n"},
    )
    monkeypatch.syspath_prepend(str(tmp_path))
    registry = UniversalKnowledgeRegistry(vocabularies=vocabularies)
    report = registry.discover("uckp_probe_broken")
    assert report.providers_found == ()
    assert any("explodes" in failure for failure in report.failures)
    assert "this module refuses to load" in " ".join(report.failures)


def test_a_provider_may_declare_its_objects_as_data_rather_than_a_callable(
    tmp_path, monkeypatch, vocabularies
):
    """``UCKO_OBJECTS`` is the declarative half of Article 8's provider hook."""
    _write_package(
        tmp_path,
        "uckp_probe_declared",
        {
            "declares": (
                "from engine.uckp.identity import urn_for\n"
                "from engine.uckp.ucko import UCKO\n"
                "UCKO_OBJECTS = (\n"
                "    UCKO.mint(\n"
                "        namespace='probe',\n"
                "        local_name='DECLARED',\n"
                "        concept='a declared provider object',\n"
                "        definition='an object offered as data rather than by a callable',\n"
                "        kind='fact',\n"
                "        category='knowledge',\n"
                "        authority_tier='engineering',\n"
                "        derives_from=urn_for('probe', 'DECLARED'),\n"
                "        owner='probe',\n"
                "    ),\n"
                ")\n"
            )
        },
    )
    monkeypatch.syspath_prepend(str(tmp_path))
    registry = UniversalKnowledgeRegistry(vocabularies=vocabularies)
    report = registry.discover("uckp_probe_declared")
    assert report.providers_found == ("uckp_probe_declared.declares",)
    assert report.objects_admitted == 1
    assert registry.get(urn_for("probe", "DECLARED")) is not None


# --- the last branches: each one a decision the derivation makes ------------------


def test_an_object_naming_no_owner_derives_no_ownership_edge(minimal_root):
    """Facet 7 is mandatory, so this is reached with a double — the branch still decides."""
    from engine.tests.uckp.doubles import Proxy

    ownerless = dataclasses.replace(minimal_root, ownership=Proxy(minimal_root.ownership, owner=""))
    edges = derive_edges(ownerless)
    assert [edge for edge in edges if edge.relationship_class == "ownership"] == []


def test_a_trace_link_whose_upstream_is_the_object_itself_derives_one_edge(minimal_root):
    """An object is not upstream of itself; recording that would be a self-loop."""
    from engine.uckp.values import TraceLink

    downstream = urn_for(TEST_NAMESPACE, "DOWNSTREAM")
    traced = dataclasses.replace(
        minimal_root,
        traceability=(TraceLink(upstream=minimal_root.ucko_id, downstream=downstream),),
        replay=None,
    ).create_from_self()
    trace_edges = [
        edge for edge in derive_edges(traced) if edge.relationship_class == "traceability"
    ]
    assert [edge.target for edge in trace_edges] == [downstream]


def test_reachability_ignores_an_edge_pointing_outside_the_graph(minimal_root, minimal_child):
    """A dangling edge is not a bridge: it must not widen the reachable set."""
    ghost = urn_for(TEST_NAMESPACE, "GHOST")
    pointing_out = dataclasses.replace(
        minimal_child,
        relationships=(
            *minimal_child.relationships,
            Relationship("references", ghost, "knowledge"),
        ),
        replay=None,
    ).create_from_self()
    graph = UniversalKnowledgeGraph((minimal_root, pointing_out))
    reachable = graph.reachable_from(minimal_root.ucko_id)
    assert reachable == frozenset({minimal_root.ucko_id, pointing_out.ucko_id})
    assert ghost not in reachable


def test_one_cycle_reached_by_two_edges_is_reported_once(vocabularies):
    """A cycle is a set of objects, not a set of edges, so two routes are still one cycle."""
    left_urn = urn_for(TEST_NAMESPACE, "CYCLE-LEFT")
    right_urn = urn_for(TEST_NAMESPACE, "CYCLE-RIGHT")
    left = UCKO.mint(
        namespace=TEST_NAMESPACE,
        local_name="CYCLE-LEFT",
        concept="cycle left",
        definition="one end of a knowledge cycle reached by two relations",
        kind="fact",
        category="knowledge",
        authority_tier="engineering",
        derives_from=left_urn,
        owner="o",
        relationships=(Relationship("references", right_urn, "knowledge"),),
    )
    right = UCKO.mint(
        namespace=TEST_NAMESPACE,
        local_name="CYCLE-RIGHT",
        concept="cycle right",
        definition="the other end, pointing back twice under two different relations",
        kind="fact",
        category="knowledge",
        authority_tier="engineering",
        derives_from=right_urn,
        owner="o",
        relationships=(
            Relationship("references", left_urn, "knowledge"),
            Relationship("related-to", left_urn, "knowledge"),
        ),
    )
    cycles = UniversalKnowledgeGraph((left, right)).cycles("knowledge")
    assert len(cycles) == 1
    assert set(cycles[0]) == {left_urn, right_urn}


def test_discovery_accepts_a_root_that_is_a_module_rather_than_a_package(vocabularies):
    """``engine.uckp.canonical`` has no submodules; a root without children is still a root."""
    registry = UniversalKnowledgeRegistry(vocabularies=vocabularies)
    report = registry.discover("engine.uckp.canonical")
    assert report.modules_scanned == 1
    assert report.failures == ()
    assert report.objects_admitted == 0


def test_an_object_offered_with_a_replay_proof_keeps_the_one_it_was_given(minimal_root):
    """Construction derives a proof only when none was supplied; it never overwrites one."""
    from engine.uckp.values import ReplayProof

    declared = ReplayProof(
        procedure="uckp.test/1.0.0",
        input_digest=minimal_root.semantic_digest(),
        output_digest="a digest recorded by a prior era",
    )
    rebuilt = UCKO.create(
        **{
            field.name: getattr(minimal_root, field.name)
            for field in dataclasses.fields(minimal_root)
            if field.name not in {"content_sha256", "replay"}
        },
        replay=declared,
    )
    assert rebuilt.replay == declared
    assert rebuilt.verify_integrity()
    assert rebuilt.verify_replay() is False
