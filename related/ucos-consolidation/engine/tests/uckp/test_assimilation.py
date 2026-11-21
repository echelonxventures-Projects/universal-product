"""Article 19: every existing UCOS artifact assimilated, losslessly and invertibly.

Losslessness is asserted by measurement over the whole corpus, not by inspection of a
sample: :func:`verify_invertible` reconstructs every source record from its object and
compares canonical digests. The negative tests then prove the check can fail, because
an invertibility test that cannot detect a loss is not evidence of anything.

Corpus counts are DERIVED from the register under measurement (the ``corpus_size``
fixture), never transcribed as literals — see the rationale on that fixture.
"""

from __future__ import annotations

import dataclasses
import json
import re
from collections import Counter

import pytest

from engine.uckp.assimilation import (
    ARTIFACT_REGISTRY_PATH,
    ASSIMILATED_CATEGORY,
    ASSIMILATED_KIND,
    ASSIMILATED_TIER,
    ASSIMILATION_NAMESPACE,
    NATIVE_CATEGORY_VOCABULARY,
    NATIVE_PROGRAM_VOCABULARY,
    NATIVE_RECORD_KEY,
    AssimilationReport,
    artifact_urn,
    assimilate_artifact,
    load_artifact_registry,
    native_lifecycle,
    native_term,
    reconstruct_artifact,
    register_native_vocabularies,
    require_lossless,
    semantic_definition,
    verify_invertible,
)
from engine.uckp.canonical import canonical_json, content_hash
from engine.uckp.errors import AssimilationError
from engine.uckp.identity import urn_for
from engine.uckp.validation import CERTIFIED, validate_universe
from engine.uckp.values import MetadataSet
from engine.uckp.vocabulary import LIFECYCLE_STAGE, build_vocabulary_registry

# --- the source -----------------------------------------------------------------


def test_the_registry_is_read_with_a_digest_naming_the_state_assimilated(repo_root, corpus_size):
    digest, records = load_artifact_registry(repo_root)
    assert len(digest) == 64
    assert len(records) == corpus_size
    again, _ = load_artifact_registry(repo_root)
    assert again == digest


def test_a_missing_registry_fails_closed(tmp_path):
    with pytest.raises(AssimilationError, match="does not exist"):
        load_artifact_registry(tmp_path)


def test_an_unreadable_registry_fails_closed(tmp_path):
    target = tmp_path / ARTIFACT_REGISTRY_PATH
    target.parent.mkdir(parents=True)
    target.write_text("{ not json", encoding="utf-8")
    with pytest.raises(AssimilationError, match="could not be read"):
        load_artifact_registry(tmp_path)


def test_a_registry_declaring_no_artifact_list_fails_closed(tmp_path):
    target = tmp_path / ARTIFACT_REGISTRY_PATH
    target.parent.mkdir(parents=True)
    target.write_text(json.dumps({"count": 0}), encoding="utf-8")
    with pytest.raises(AssimilationError, match="declares no artifact list"):
        load_artifact_registry(tmp_path)


# --- open-world registration ----------------------------------------------------


def test_native_statuses_are_admitted_by_registration_not_by_amending_the_law(
    assimilation_report,
):
    """Article 17: an unknown category is admitted by registration, never by amendment."""
    assert set(assimilation_report.registered_lifecycle_terms) == {
        "active",
        "certified",
        "complete",
        "final",
        "frozen",
        "under-review",
    }
    # None of these appear in the law's own declared stages.
    declared = build_vocabulary_registry().require(LIFECYCLE_STAGE).term_ids()
    for status in assimilation_report.registered_lifecycle_terms:
        assert status not in declared


def test_the_repositorys_own_categories_and_programmes_get_their_own_vocabularies(
    assimilated_universe, assimilation_report
):
    vocabularies = assimilated_universe.vocabularies()
    assert NATIVE_CATEGORY_VOCABULARY in vocabularies.vocabulary_ids()
    assert NATIVE_PROGRAM_VOCABULARY in vocabularies.vocabulary_ids()
    # The claim is that the repository's OWN categories and programmes get vocabularies of
    # their own — a containment relation, which is what is asserted here. The former literals
    # (80 / 77) measured one day's corpus and broke on the next: adding four artifacts moved
    # them to 81 / 78 and failed a suite where nothing was wrong. Containment proves the
    # property for any corpus, and the non-emptiness assertions keep it from passing vacuously.
    category_terms = set(vocabularies.require(NATIVE_CATEGORY_VOCABULARY).term_ids())
    program_terms = set(vocabularies.require(NATIVE_PROGRAM_VOCABULARY).term_ids())
    assert set(assimilation_report.registered_categories) <= category_terms
    assert set(assimilation_report.registered_programs) <= program_terms
    assert assimilation_report.registered_categories
    assert assimilation_report.registered_programs


def test_registration_is_idempotent_over_the_same_records(repo_root):
    _, records = load_artifact_registry(repo_root)
    vocabularies = build_vocabulary_registry()
    first, categories, programs = register_native_vocabularies(vocabularies, records)
    second, categories_again, programs_again = register_native_vocabularies(vocabularies, records)
    assert first and not second  # nothing left to add the second time
    assert categories == categories_again
    assert programs == programs_again


@pytest.mark.parametrize(
    ("status", "expected"),
    [("ACTIVE", "active"), ("UNDER_REVIEW", "under-review"), ("", "draft"), (None, "draft")],
)
def test_native_status_maps_onto_a_term_id(status, expected):
    assert native_lifecycle(status) == expected


def test_native_term_normalises_and_never_returns_empty():
    assert native_term("SVC") == "svc"
    assert native_term("UNDER_SCORE") == "under-score"
    assert native_term("  ") == "unclassified"


# --- the mapping ----------------------------------------------------------------


def test_every_artifact_becomes_exactly_one_object(assimilation_report, corpus_size):
    assert assimilation_report.artifacts_read == corpus_size
    assert assimilation_report.objects_minted == corpus_size


def test_assimilation_is_invertible_over_the_whole_corpus(assimilation_report):
    assert assimilation_report.invertible
    assert assimilation_report.lossless
    assert assimilation_report.losses == ()
    require_lossless(assimilation_report)


def test_every_object_reconstructs_its_source_record_exactly(assimilated_universe, repo_root):
    _, records = load_artifact_registry(repo_root)
    by_id = {record["universal_id"]: record for record in records}
    assimilated = [
        obj
        for obj in assimilated_universe.objects()
        if obj.identity.namespace == ASSIMILATION_NAMESPACE
    ]
    assert len(assimilated) == len(records)
    for obj in assimilated:
        original = by_id[obj.identity.local_name]
        assert content_hash(reconstruct_artifact(obj)) == content_hash(original)


def test_the_native_record_is_stored_verbatim(repo_root):
    _, records = load_artifact_registry(repo_root)
    record = records[0]
    obj = assimilate_artifact(
        record,
        known_ids=frozenset({record["universal_id"]}),
        law_urn=urn_for("ucos", "UCKP-LAW-0001"),
        source=ARTIFACT_REGISTRY_PATH,
        source_digest="d",
    )
    assert obj.metadata.get(NATIVE_RECORD_KEY) == canonical_json(record)


def test_assimilated_objects_take_engineering_authority_not_constitutional(
    assimilated_universe,
):
    """Assimilation moves an artifact under the law; it does not promote it."""
    for obj in assimilated_universe.objects():
        if obj.identity.namespace == ASSIMILATION_NAMESPACE:
            assert obj.authority.tier == ASSIMILATED_TIER
            assert obj.taxonomy.kind == ASSIMILATED_KIND
            assert obj.taxonomy.category == ASSIMILATED_CATEGORY


def test_the_one_parentless_artifact_derives_from_the_root_law(assimilated_universe):
    root_book = assimilated_universe.registry.require(artifact_urn("UCOS-BOOK-000000"))
    assert root_book.authority.derives_from == assimilated_universe.root_id()


def test_every_assimilated_authority_chain_terminates_at_the_law(assimilated_universe):
    graph = assimilated_universe.graph()
    root = assimilated_universe.root_id()
    for obj in assimilated_universe.objects():
        if obj.identity.namespace == ASSIMILATION_NAMESPACE:
            assert graph.authority_chain(obj.ucko_id)[-1] == root


def test_the_repository_path_survives_only_as_a_non_authoritative_binding(
    assimilated_universe,
):
    """Article 4 / UCKP-INV-10, at the point where the repository actually appears."""
    obj = assimilated_universe.registry.require(artifact_urn("UCOS-BOOK-000000"))
    kinds = {binding.persistence_kind for binding in obj.persistence_bindings}
    assert kinds == {"git", "filesystem"}
    assert all(not binding.authoritative for binding in obj.persistence_bindings)
    assert all(not binding.authoritative for binding in obj.projection_bindings)
    assert obj.evidence[0].locator.endswith(".md")


def test_the_source_content_hash_is_preserved_as_evidence(assimilated_universe, repo_root):
    _, records = load_artifact_registry(repo_root)
    declared = {r["universal_id"]: r["content_hash"] for r in records}
    obj = assimilated_universe.registry.require(artifact_urn("UCOS-BOOK-000000"))
    assert obj.evidence[0].digest == declared["UCOS-BOOK-000000"]


def test_provenance_names_both_the_artifact_and_the_registry_it_came_through(
    assimilated_universe,
):
    obj = assimilated_universe.registry.require(artifact_urn("UCOS-BOOK-000000"))
    actions = [step.action for step in obj.provenance]
    assert "declared" in actions and "assimilated" in actions
    assert any(step.source == ARTIFACT_REGISTRY_PATH for step in obj.provenance)


def test_semantic_definitions_are_unique_even_though_names_collide(repo_root):
    """490 artifacts share a name and every description is empty."""
    _, records = load_artifact_registry(repo_root)
    definitions = {semantic_definition(record) for record in records}
    assert len(definitions) == len(records)


def test_shared_names_are_reported_rather_than_absorbed(assimilation_report, repo_root):
    """The property is REPORTING, and the count is a fact about a corpus that keeps growing.

    This assertion used to pin the literal 21. The corpus reached 23 and the test failed for a
    reason unrelated to anything it names — the report was working exactly as intended. A test
    that goes red whenever the repository grows teaches its readers to bump the number, and a
    number people bump on sight is not an assertion.

    So the population is DERIVED from the same registry the report reads, and the two must
    agree exactly. That is strictly stronger than the literal: it fails if the report drops a
    collision (absorption, the defect this test exists to catch), it fails if the report invents
    one, and it cannot go stale.
    """
    _, records = load_artifact_registry(repo_root)
    counts = Counter(str(record.get("name", "")).strip() for record in records)
    expected = {name for name, total in counts.items() if total > 1}

    reported = assimilation_report.shared_semantic_names
    assert reported, "no shared name was reported at all, so this test would hold vacuously"
    assert len(reported) == len(expected), (
        f"the report names {len(reported)} shared semantic names and the registry carries "
        f"{len(expected)}; a name that collides and is not reported has been absorbed"
    )

    # Every entry carries its multiplicity, which is what makes a collision READABLE rather
    # than merely counted — absorbing a name and reporting the survivor would satisfy a bare
    # count and lose the fact.
    for entry in reported:
        assert re.search(r" x\d+$", entry), f"{entry!r} reports no multiplicity"
    assert max(counts.values()) > 1
    assert any(entry.endswith(f" x{max(counts.values())}") for entry in reported)


def test_unresolvable_traceability_is_reported_and_never_turned_into_an_edge(
    assimilated_universe, assimilation_report
):
    """A link to a non-existent object is the dangling relationship Article 7 forbids."""
    assert assimilation_report.unresolvable_traceability
    assert assimilated_universe.graph().dangling() == ()


def test_unresolvable_links_are_still_preserved_in_the_native_record(
    assimilated_universe, assimilation_report, repo_root
):
    """Not edged is not the same as lost."""
    _, records = load_artifact_registry(repo_root)
    unresolved_targets = {
        entry.rsplit("-> ", 1)[1] for entry in assimilation_report.unresolvable_traceability
    }
    assert unresolved_targets
    recovered: set[str] = set()
    for obj in assimilated_universe.objects():
        if obj.identity.namespace != ASSIMILATION_NAMESPACE:
            continue
        traceability = reconstruct_artifact(obj).get("traceability") or {}
        for targets in traceability.values():
            recovered.update(str(target) for target in targets)
    assert unresolved_targets <= recovered


def test_an_artifact_with_no_identity_is_refused():
    with pytest.raises(AssimilationError, match="no universal_id"):
        assimilate_artifact(
            {"name": "x"},
            known_ids=frozenset(),
            law_urn="urn:x",
            source="s",
            source_digest="d",
        )


def test_reconstruction_refuses_an_object_carrying_no_native_record(minimal_root):
    with pytest.raises(AssimilationError, match="carries no native record"):
        reconstruct_artifact(minimal_root)


def test_reconstruction_refuses_an_undecodable_native_record(minimal_root):
    broken = dataclasses.replace(
        minimal_root, metadata=MetadataSet.of({NATIVE_RECORD_KEY: "{ not json"})
    )
    with pytest.raises(AssimilationError, match="not decodable"):
        reconstruct_artifact(broken)


def test_reconstruction_refuses_a_native_record_that_is_not_a_mapping(minimal_root):
    broken = dataclasses.replace(
        minimal_root, metadata=MetadataSet.of({NATIVE_RECORD_KEY: "[1,2,3]"})
    )
    with pytest.raises(AssimilationError, match="not a mapping"):
        reconstruct_artifact(broken)


def test_the_invertibility_check_detects_a_dropped_field(repo_root):
    """The test that proves the losslessness test can fail."""
    _, records = load_artifact_registry(repo_root)
    record = dict(records[0])
    obj = assimilate_artifact(
        record,
        known_ids=frozenset({record["universal_id"]}),
        law_urn=urn_for("ucos", "UCKP-LAW-0001"),
        source=ARTIFACT_REGISTRY_PATH,
        source_digest="d",
    )
    lossy = dataclasses.replace(
        obj,
        metadata=MetadataSet.of(
            {
                **obj.metadata.as_dict(),
                NATIVE_RECORD_KEY: canonical_json({"universal_id": record["universal_id"]}),
            }
        ),
    )
    losses = verify_invertible((lossy,), (record,))
    assert losses
    assert "does not reconstruct" in losses[0]


def test_the_invertibility_check_detects_a_count_mismatch(repo_root):
    _, records = load_artifact_registry(repo_root)
    losses = verify_invertible((), records[:2])
    assert any("were minted" in loss for loss in losses)


def test_the_invertibility_check_detects_an_object_with_no_source(repo_root, minimal_root):
    losses = verify_invertible((minimal_root,), ())
    assert any("corresponds to no source artifact" in loss for loss in losses)


def test_require_lossless_refuses_a_lossy_report():
    report = AssimilationReport(
        source="s",
        source_digest="d",
        artifacts_read=1,
        objects_minted=1,
        invertible=False,
        losses=("something went missing",),
    )
    assert not report.lossless
    with pytest.raises(AssimilationError, match="not lossless"):
        require_lossless(report)


def test_the_report_serializes_and_summarizes(assimilation_report, corpus_size):
    record = assimilation_report.to_dict()
    assert record["counts"]["artifacts_read"] == corpus_size
    assert record["lossless"] is True
    assert "invertible=True" in assimilation_report.summary()


# --- the assimilated universe ---------------------------------------------------


def test_the_assimilated_universe_holds_the_constitution_and_the_corpus(
    assimilated_universe,
    constitution_object_count,
    corpus_size,
    uga_projection_size,
):
    assert (
        len(assimilated_universe.objects())
        == constitution_object_count + corpus_size + uga_projection_size
    )
    assert len(assimilated_universe.discovery.providers_found) == 4
    assert "engine.uckp.assimilation" in assimilated_universe.registry.providers()


def test_the_assimilated_universe_still_has_exactly_one_root(assimilated_universe):
    assert assimilated_universe.root_id() == urn_for("ucos", "UCKP-LAW-0001")


def test_the_assimilated_universe_is_coherent(assimilated_universe):
    assimilated_universe.require_coherent()
    graph = assimilated_universe.graph()
    assert graph.dangling() == ()
    assert graph.orphans(assimilated_universe.root_id()) == ()


def test_the_assimilated_universe_satisfies_all_seventeen_invariants(assimilated_universe):
    report = validate_universe(assimilated_universe)
    assert report.verdict == CERTIFIED, [item.to_dict() for item in report.blocking_failures()]
    assert report.satisfied_count() == 17
    assert report.all_stop_conditions_met()


def test_assimilation_is_not_a_discovery_provider():
    """Discovery must not become hostage to the presence of a working tree.

    A module that merely *documents* that it is not a provider is still a provider:
    the walk looks for the attribute, not for the intention. So the name must be
    absent from the module namespace.
    """
    from engine.uckp import assimilation

    assert not hasattr(assimilation, "ucko_objects")
    assert not hasattr(assimilation, "UCKO_OBJECTS")


def test_discovery_finds_exactly_the_declarative_providers():
    from engine.uckp.registry import UniversalKnowledgeRegistry

    registry = UniversalKnowledgeRegistry(vocabularies=build_vocabulary_registry())
    report = registry.discover("engine.uckp")
    # engine.uckp.uga_projection (existence_resolution's declared UGA projection,
    # PHASE-UCF-005-PROVIDER-INTEGRATION-DETERMINATION.md) joined the three native
    # providers as of this test's update — an intentional extension through the
    # existing ucko_objects() protocol, not a regression this lock-down should hide.
    assert report.providers_found == (
        "engine.uckp.alignment",
        "engine.uckp.capabilities",
        "engine.uckp.constitution",
        "engine.uckp.uga_projection",
    )


def test_assimilating_twice_against_one_registry_is_permitted(repo_root):
    from engine.uckp.assimilation import assimilate

    vocabularies = build_vocabulary_registry()
    _, first = assimilate(source_root=repo_root, vocabularies=vocabularies)
    _, second = assimilate(source_root=repo_root, vocabularies=vocabularies)
    assert first.lossless and second.lossless
    assert first.registered_categories == second.registered_categories


def test_a_conflicting_native_vocabulary_under_an_existing_id_fails_closed(repo_root):
    from engine.uckp.vocabulary import Term, Vocabulary

    _, records = load_artifact_registry(repo_root)
    vocabularies = build_vocabulary_registry()
    vocabularies.register(
        Vocabulary(
            vocabulary_id=NATIVE_CATEGORY_VOCABULARY,
            purpose="a rival set of terms",
            terms=(Term(term_id="something-else", definition="not the real categories"),),
        )
    )
    with pytest.raises(AssimilationError, match="already registered under this id"):
        register_native_vocabularies(vocabularies, records)


# --- the residual paths: an absent term, a lost record, an unresolvable dependency --


def test_an_absent_native_category_maps_to_the_unclassified_term():
    """``str(None)`` is ``"none"``, so absence has to be tested before stringifying."""
    assert native_term(None) == "unclassified"
    assert native_term("  ") == "unclassified"
    assert native_term("Meta_Model") == "meta-model"


def test_invertibility_names_an_object_whose_native_record_was_lost(minimal_root):
    """The reconstruction failure must be reported per object, not abort the measurement."""
    record = {"universal_id": minimal_root.local_name, "name": "the source artifact"}
    losses = verify_invertible((minimal_root,), (record,))
    assert any("carries no native record" in loss for loss in losses)
    with pytest.raises(AssimilationError, match="carries no native record"):
        reconstruct_artifact(minimal_root)


def _write_registry(tmp_path, artifacts: list[dict]) -> None:
    target = tmp_path / ARTIFACT_REGISTRY_PATH
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(
        json.dumps({"count": len(artifacts), "artifacts": artifacts}), encoding="utf-8"
    )


def test_a_dependency_on_an_artifact_the_registry_does_not_contain_is_named_not_dropped(
    tmp_path, vocabularies
):
    """Article 19: nothing the source declared may vanish silently, including a broken link."""
    from engine.uckp.assimilation import assimilate

    _write_registry(
        tmp_path,
        [
            {
                "universal_id": "UCOS-PROBE-000001",
                "name": "a probe artifact",
                "category": "meta_model",
                "status": "active",
                "path": "00-MASTER/UCOS-PROBE-000001/probe.json",
                "content_hash": "0" * 64,
                "dependencies": ["UCOS-ABSENT-999999"],
            }
        ],
    )
    objects, report = assimilate(source_root=tmp_path, vocabularies=vocabularies)
    assert len(objects) == 1
    assert report.unresolvable_dependencies == (
        "UCOS-PROBE-000001 -depends-on-> UCOS-ABSENT-999999",
    )
    assert report.invertible is True
    assert report.losses == ()
    require_lossless(report)
