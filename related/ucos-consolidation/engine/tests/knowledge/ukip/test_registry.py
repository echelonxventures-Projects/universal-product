"""UKIP Part 06 — the Knowledge Registry: the Knowledge Once Principle under N providers.

The registry's central claim is that adding providers never adds records. It holds because the
key *is* the content digest, so the second provider to supply a piece of knowledge lands on the
same home the first one made and is recorded as corroboration — evidence that the knowledge is
real, not a duplicate to be reported.

Two properties carry that claim and both are proven here rather than asserted. First,
**nothing is discarded**: a displaced canonical source becomes a corroboration, because a
provider whose contribution was dropped would look like a fresh duplicate on the next run.
Second, **the canonical role follows declared authority**: an authoritative provider takes the
home whenever it arrives, and among equals the first arrival keeps it.

Order-independence is therefore a claim about the registry's *contents*, and the tests below
say exactly that much: the record set, the source set and the provider set do not depend on the
sequence the providers ran in. The provenance chain does, and must — it is the account of what
happened, and a chain that hid the sequence would be one nobody could replay.
"""

from __future__ import annotations

import pytest

from engine.knowledge.model import (
    KnowledgeAuthority,
    KnowledgeKind,
    Lifecycle,
    RelationType,
)
from engine.knowledge.ukip.classification import KnowledgeClassifier
from engine.knowledge.ukip.contracts import ProviderKind, RelationDeclaration
from engine.knowledge.ukip.errors import DuplicateHomeError, RegistrationError
from engine.knowledge.ukip.provenance import Stage
from engine.knowledge.ukip.registry import (
    REGISTRY_ACTOR,
    REGISTRY_SCHEMA,
    REGISTRY_VERSION,
    Admission,
    AdmissionOutcome,
    KnowledgeRegistry,
    RegisteredKnowledge,
)

from .conftest import make_source, make_unclassified, make_unit, unit_from

STATEMENT = "Every canonical object shall be homed exactly once."


def registered(key: str = "a", **overrides) -> RegisteredKnowledge:
    """A sealed record built from a fully classified unit."""
    return RegisteredKnowledge.from_unit(make_unit(key, **overrides))


def submit(registry: KnowledgeRegistry, unit, **kwargs) -> Admission:
    """Classify and submit a unit the way the assimilator does."""
    classification = KnowledgeClassifier().classify(unit)
    return registry.submit(classification.apply(unit), classification, **kwargs)


# ---------------------------------------------------------------------------
# AdmissionOutcome / Admission
# ---------------------------------------------------------------------------


def test_only_a_rejection_leaves_the_knowledge_out_of_the_registry():
    assert AdmissionOutcome.REGISTERED.admitted
    assert AdmissionOutcome.CORROBORATED.admitted
    assert not AdmissionOutcome.REJECTED.admitted


def test_only_the_first_arrival_created_the_canonical_home():
    made = Admission(AdmissionOutcome.REGISTERED, "K-1", "p", "k")
    joined = Admission(AdmissionOutcome.CORROBORATED, "K-1", "q", "k")
    assert made.created_home
    assert not joined.created_home


def test_an_admission_projects_every_field_it_records():
    admission = Admission(AdmissionOutcome.REGISTERED, "K-1", "p", "k", "home established")
    assert admission.to_dict() == {
        "outcome": "registered",
        "knowledge_id": "K-1",
        "provider_id": "p",
        "unit_key": "k",
        "reason": "home established",
    }


# ---------------------------------------------------------------------------
# RegisteredKnowledge — construction and sealing
# ---------------------------------------------------------------------------


def test_only_a_fully_classified_unit_may_be_registered():
    """Registering unclassified knowledge would home something nobody has placed."""
    with pytest.raises(RegistrationError) as exc:
        RegisteredKnowledge.from_unit(make_unclassified("raw-1"))
    assert "fully classified" in str(exc.value)


def test_a_record_is_sealed_over_its_own_content():
    record = registered()
    assert record.record_sha256
    assert record.verify_integrity()


def test_a_mutated_record_no_longer_verifies():
    """Post-registration mutation is detectable, which is what makes the seal worth having."""
    from dataclasses import replace

    tampered = replace(registered(), statement="Something else entirely.")
    assert not tampered.verify_integrity()


def test_an_unsealed_record_does_not_verify():
    from dataclasses import replace

    assert not replace(registered(), record_sha256="").verify_integrity()


def test_the_seal_covers_the_provenance_chain():
    """A record whose provenance was swapped is a different record."""
    record = registered()
    moved = record.with_provenance(
        record.provenance.append(Stage.REGISTERED, actor="other", action="register")
    )
    assert moved.record_sha256 != record.record_sha256
    assert moved.verify_integrity()


def test_a_record_carries_its_classification_rules_when_one_was_supplied():
    unit = make_unclassified("raw-1", statement=STATEMENT)
    classification = KnowledgeClassifier().classify(unit)
    record = RegisteredKnowledge.from_unit(classification.apply(unit), classification)
    assert record.classification_rules == classification.rule_ids()


# ---------------------------------------------------------------------------
# RegisteredKnowledge — corroboration
# ---------------------------------------------------------------------------


def test_a_unit_expressing_different_knowledge_cannot_corroborate():
    """Corroboration is agreement about the same substance, never about the same name."""
    record = registered("a", statement=STATEMENT)
    other = make_unit("a", statement="A completely different assertion entirely.")
    with pytest.raises(RegistrationError) as exc:
        record.corroborated_by(other, prefer_canonical=False)
    assert "does not express the registered knowledge" in str(exc.value)


def test_a_source_already_cited_corroborates_nothing_new():
    """The same provider saying the same thing twice is one piece of evidence, not two."""
    unit = make_unit("a", statement=STATEMENT)
    record = RegisteredKnowledge.from_unit(unit)
    assert record.corroborated_by(unit, prefer_canonical=False) is record


def test_a_second_provider_becomes_a_corroboration():
    first = unit_from("alpha", "a", STATEMENT)
    second = unit_from("beta", "a", STATEMENT)
    record = RegisteredKnowledge.from_unit(first).corroborated_by(second, prefer_canonical=False)
    assert record.canonical_source == first.source
    assert [s.citation for s in record.corroborations] == [second.source.citation]
    assert record.provider_ids == ("alpha", "beta")
    assert record.is_multi_sourced
    assert record.corroboration_count == 1
    assert record.verify_integrity()


def test_a_preferred_provider_takes_the_canonical_role_and_nothing_is_discarded():
    """The displaced source stays: a dropped contribution would look new on the next run."""
    first = unit_from("alpha", "a", STATEMENT)
    second = unit_from("beta", "a", STATEMENT)
    record = RegisteredKnowledge.from_unit(first).corroborated_by(second, prefer_canonical=True)
    assert record.canonical_source == second.source
    assert first.source.citation in [s.citation for s in record.corroborations]
    assert record.provider_ids == ("alpha", "beta")


def test_corroborating_sources_are_ordered_by_citation_not_by_arrival():
    """Ordering by citation is what makes the record independent of provider run order."""
    home = unit_from("mid", "a", STATEMENT)
    late = unit_from("aaa", "a", STATEMENT)
    early = unit_from("zzz", "a", STATEMENT)
    record = RegisteredKnowledge.from_unit(home)
    forward = record.corroborated_by(late, prefer_canonical=False).corroborated_by(
        early, prefer_canonical=False
    )
    backward = record.corroborated_by(early, prefer_canonical=False).corroborated_by(
        late, prefer_canonical=False
    )
    assert forward.corroborations == backward.corroborations
    assert forward.record_sha256 == backward.record_sha256


def test_corroboration_merges_the_relations_the_second_provider_declared():
    """A provider that knows one more edge contributes it; it does not overwrite the record."""
    first = unit_from(
        "alpha", "a", STATEMENT, relations=(RelationDeclaration(RelationType.DEPENDS_ON, "b"),)
    )
    second = unit_from(
        "beta", "a", STATEMENT, relations=(RelationDeclaration(RelationType.REFERENCES, "c"),)
    )
    record = RegisteredKnowledge.from_unit(first).corroborated_by(second, prefer_canonical=False)
    assert {(r.relation, r.target) for r in record.relations} == {
        (RelationType.DEPENDS_ON, "b"),
        (RelationType.REFERENCES, "c"),
    }


# ---------------------------------------------------------------------------
# RegisteredKnowledge — relations
# ---------------------------------------------------------------------------


def test_merging_relations_deduplicates_and_orders_them():
    record = registered("a", relations=(RelationDeclaration(RelationType.DEPENDS_ON, "z"),))
    merged = record.merge_relations(
        (
            RelationDeclaration(RelationType.DEPENDS_ON, "z"),  # already held
            RelationDeclaration(RelationType.DEPENDS_ON, "a"),
        )
    )
    assert [r.target for r in merged.relations] == ["a", "z"]
    assert merged.verify_integrity()


def test_merging_relations_that_add_nothing_returns_the_same_record():
    """No change means no reseal — a record must not churn its identity for nothing."""
    record = registered("a", relations=(RelationDeclaration(RelationType.DEPENDS_ON, "z"),))
    assert record.merge_relations((RelationDeclaration(RelationType.DEPENDS_ON, "z"),)) is record
    assert record.merge_relations(()) is record


def test_relations_resolve_provider_local_targets_to_canonical_identifiers():
    record = registered("a", relations=(RelationDeclaration(RelationType.DEPENDS_ON, "peer-key"),))
    resolved = record.resolved_relations({"peer-key": "UCKO-PEER-0001"})
    assert [r.target for r in resolved] == ["UCKO-PEER-0001"]


def test_an_unresolvable_target_is_kept_verbatim_rather_than_dropped():
    record = registered("a", relations=(RelationDeclaration(RelationType.DEPENDS_ON, "unknown"),))
    assert [r.target for r in record.resolved_relations({})] == ["unknown"]


def test_a_preserved_target_survives_the_projection_unrewritten():
    """A link into an artifact UKIP does not own must not be rewritten to a knowledge id."""
    record = registered("a", relations=(RelationDeclaration(RelationType.DEPENDS_ON, "UDEC-0001"),))
    resolved = record.resolved_relations(
        {"UDEC-0001": "UCKO-WRONG-0001"}, preserve=frozenset({"UDEC-0001"})
    )
    assert [r.target for r in resolved] == ["UDEC-0001"]


def test_resolution_collapses_two_relations_that_resolve_to_one_edge():
    record = registered(
        "a",
        relations=(
            RelationDeclaration(RelationType.DEPENDS_ON, "alias-1"),
            RelationDeclaration(RelationType.DEPENDS_ON, "alias-2"),
        ),
    )
    resolved = record.resolved_relations({"alias-1": "UCKO-X-0001", "alias-2": "UCKO-X-0001"})
    assert [r.target for r in resolved] == ["UCKO-X-0001"]


# ---------------------------------------------------------------------------
# RegisteredKnowledge — projection
# ---------------------------------------------------------------------------


def test_searchable_text_carries_the_record_without_copying_the_content():
    record = registered("a", statement=STATEMENT, tags=("truth", "ownership"))
    text = record.searchable_text()
    assert record.knowledge_id in text
    assert STATEMENT in text
    assert "ownership" in text


@pytest.mark.parametrize(
    ("relation", "field"),
    (
        (RelationType.DEPENDS_ON, "dependencies"),
        (RelationType.CONFLICTS_WITH, "conflicts_with"),
        (RelationType.SUPERSEDES, "supersedes"),
        (RelationType.REFERENCES, "knowledge_links"),
    ),
)
def test_each_relation_kind_projects_onto_the_field_ukda_already_owns(relation, field):
    """The registry projects into UKDA's object model; it never invents a second one."""
    record = registered("a", relations=(RelationDeclaration(relation, "UCKO-TARGET-0001"),))
    obj = record.to_canonical_object()
    assert getattr(obj, field) == ("UCKO-TARGET-0001",)


def test_a_reference_to_a_decision_becomes_a_decision_link():
    record = registered("a", relations=(RelationDeclaration(RelationType.DEPENDS_ON, "UDEC-1"),))
    obj = record.to_canonical_object(decision_ids=frozenset({"UDEC-1"}))
    assert obj.decision_links == ("UDEC-1",)
    assert obj.dependencies == ()


def test_a_record_read_out_of_a_decision_links_back_to_that_decision():
    """What documents the knowledge is precisely the record it was read out of."""
    unit = make_unit(
        "a",
        source=make_source(
            provider_id="decisions", kind=ProviderKind.DECISION_LOG, locator="UDEC-1"
        ),
    )
    obj = RegisteredKnowledge.from_unit(unit).to_canonical_object(
        decision_ids=frozenset({"UDEC-1"})
    )
    assert obj.decision_links == ("UDEC-1",)


def test_the_projection_cites_every_provider_so_attribution_survives_it():
    first = unit_from("alpha", "a", STATEMENT)
    second = unit_from("beta", "a", STATEMENT)
    record = RegisteredKnowledge.from_unit(first).corroborated_by(second, prefer_canonical=False)
    obj = record.to_canonical_object()
    assert set(obj.evidence) == {first.source.citation, second.source.citation}


def test_the_projection_may_be_homed_under_a_supplied_identifier():
    obj = registered("a").to_canonical_object(cko_id="UCKO-EXPLICIT-0001")
    assert obj.cko_id == "UCKO-EXPLICIT-0001"


def test_the_record_projection_carries_its_seal_providers_and_provenance():
    record = registered("a")
    payload = record.to_dict()
    assert payload["record_sha256"] == record.record_sha256
    assert payload["provider_ids"] == list(record.provider_ids)
    assert payload["provenance"]["seal"] == record.provenance.seal


# ---------------------------------------------------------------------------
# KnowledgeRegistry — homing
# ---------------------------------------------------------------------------


def test_a_registry_installs_the_records_it_is_constructed_with():
    registry = KnowledgeRegistry([registered("a"), registered("b")])
    assert len(registry) == 2
    assert registry.knowledge_ids() == tuple(sorted(registry.knowledge_ids()))


def test_two_different_records_may_not_claim_one_canonical_home():
    from dataclasses import replace

    first = registered("a", statement=STATEMENT)
    impostor = replace(first, knowledge_sha256="d" * 64).sealed()
    registry = KnowledgeRegistry([first])
    with pytest.raises(DuplicateHomeError) as exc:
        registry.register(impostor)
    assert "same canonical home" in str(exc.value)


def test_identical_knowledge_may_not_be_homed_under_two_identifiers():
    """The invariant the whole keying scheme exists to make true."""
    from dataclasses import replace

    first = registered("a", statement=STATEMENT)
    aliased = replace(first, knowledge_id="UCKO-ALIAS-0001").sealed()
    registry = KnowledgeRegistry([first])
    with pytest.raises(DuplicateHomeError) as exc:
        registry.register(aliased)
    assert "already homed under another identifier" in str(exc.value)


def test_reinstalling_the_identical_record_is_accepted():
    record = registered("a")
    registry = KnowledgeRegistry([record])
    assert registry.register(record) is registry
    assert len(registry) == 1


def test_the_duplicate_home_invariant_holds_over_a_populated_registry():
    registry = KnowledgeRegistry([registered("a"), registered("b"), registered("c")])
    assert registry.duplicate_homes() == ()
    assert registry.unsealed() == ()


# ---------------------------------------------------------------------------
# KnowledgeRegistry — admission
# ---------------------------------------------------------------------------


def test_the_first_unit_establishes_the_canonical_home():
    registry = KnowledgeRegistry()
    admission = submit(registry, make_unclassified("a", statement=STATEMENT))
    assert admission.outcome is AdmissionOutcome.REGISTERED
    assert admission.created_home
    assert len(registry) == 1
    record = registry.require(admission.knowledge_id)
    assert record.provenance.has_stage(Stage.REGISTERED)
    assert record.provenance.has_stage(Stage.CLASSIFIED)


def test_n_providers_of_the_same_knowledge_never_produce_n_records():
    """The Knowledge Once Principle, stated as the count it promises."""
    registry = KnowledgeRegistry()
    outcomes = [
        submit(registry, unit_from(f"provider-{index}", "a", STATEMENT)).outcome
        for index in range(5)
    ]
    assert outcomes[0] is AdmissionOutcome.REGISTERED
    assert all(outcome is AdmissionOutcome.CORROBORATED for outcome in outcomes[1:])
    assert len(registry) == 1
    record = registry.records()[0]
    assert len(record.provider_ids) == 5
    assert record.provenance.has_stage(Stage.CORROBORATED)


def test_no_provider_contribution_is_lost_to_the_order_the_providers_ran_in():
    """Nothing is discarded: the full source set is the same set whichever way it arrived."""
    units = [unit_from(f"provider-{index}", "a", STATEMENT) for index in range(4)]
    forward, backward = KnowledgeRegistry(), KnowledgeRegistry()
    for unit in units:
        submit(forward, unit)
    for unit in reversed(units):
        submit(backward, unit)
    first, second = forward.records()[0], backward.records()[0]
    assert first.knowledge_id == second.knowledge_id
    assert first.knowledge_sha256 == second.knowledge_sha256
    assert first.provider_ids == second.provider_ids
    assert {s.citation for s in first.sources} == {s.citation for s in second.sources}


def test_the_canonical_role_follows_declared_authority_not_arrival_order():
    """Among equals the first arrival keeps the home; a declared authority takes it regardless."""
    ordinary = [unit_from(f"provider-{index}", "a", STATEMENT) for index in range(3)]
    authority = unit_from("canon", "a", STATEMENT)

    early, late = KnowledgeRegistry(), KnowledgeRegistry()
    submit(early, authority, authoritative=True)
    for unit in ordinary:
        submit(early, unit)
    for unit in ordinary:
        submit(late, unit)
    submit(late, authority, authoritative=True)

    assert early.records()[0].canonical_source.provider_id == "canon"
    assert late.records()[0].canonical_source.provider_id == "canon"
    # The displaced sources survive in both, and as the same set.
    assert early.records()[0].provider_ids == late.records()[0].provider_ids


def test_the_provenance_chain_records_history_and_therefore_reflects_arrival_order():
    """Provenance is a record of what happened, so it is the one part order may show in.

    This is not a wrinkle in the order-independence claim; it is the boundary of it. The
    registry's *contents* are order-independent, and the chain is the honest account of how
    they came to be — a chain that hid the sequence would be a chain nobody could replay.
    """
    units = [unit_from(f"provider-{index}", "a", STATEMENT) for index in range(3)]
    forward, backward = KnowledgeRegistry(), KnowledgeRegistry()
    for unit in units:
        submit(forward, unit)
    for unit in reversed(units):
        submit(backward, unit)

    def corroborators(registry):
        steps = registry.records()[0].provenance.steps
        return [s.detail for s in steps if s.stage is Stage.CORROBORATED]

    assert corroborators(forward) == [f"provider:provider-{i}" for i in (1, 2)]
    assert corroborators(backward) == [f"provider:provider-{i}" for i in (1, 0)]
    assert forward.records()[0].provenance.verify()
    assert backward.records()[0].provenance.verify()


def test_an_authoritative_provider_displaces_the_canonical_source():
    registry = KnowledgeRegistry()
    submit(registry, unit_from("documents", "a", STATEMENT))
    submit(registry, unit_from("canon", "a", STATEMENT), authoritative=True)
    record = registry.records()[0]
    assert record.canonical_source.provider_id == "canon"
    assert "documents" in record.provider_ids


def test_a_non_authoritative_provider_never_displaces_the_canonical_source():
    registry = KnowledgeRegistry()
    submit(registry, unit_from("first", "a", STATEMENT))
    submit(registry, unit_from("second", "a", STATEMENT), authoritative=False, priority=9999)
    assert registry.records()[0].canonical_source.provider_id == "first"


@pytest.mark.parametrize("kind", (ProviderKind.CANONICAL_STORE, ProviderKind.DECISION_LOG))
def test_an_authoritative_provider_cannot_displace_a_canonical_store(kind):
    """The canonical store already is the authority; nothing outranks it."""
    registry = KnowledgeRegistry()
    submit(
        registry,
        make_unit("a", statement=STATEMENT, source=make_source("store", "store/a", kind=kind)),
    )
    submit(registry, unit_from("challenger", "a", STATEMENT), authoritative=True)
    record = registry.records()[0]
    assert record.canonical_source.provider_id == "store"
    assert "challenger" in record.provider_ids


def test_a_negative_priority_authoritative_provider_does_not_displace():
    registry = KnowledgeRegistry()
    submit(registry, unit_from("first", "a", STATEMENT))
    submit(registry, unit_from("second", "a", STATEMENT), authoritative=True, priority=-1)
    assert registry.records()[0].canonical_source.provider_id == "first"


def test_the_admission_log_records_every_submission_in_order():
    registry = KnowledgeRegistry()
    submit(registry, unit_from("alpha", "a", STATEMENT))
    submit(registry, unit_from("beta", "a", STATEMENT))
    log = registry.admissions()
    assert [item.outcome for item in log] == [
        AdmissionOutcome.REGISTERED,
        AdmissionOutcome.CORROBORATED,
    ]
    assert [item.provider_id for item in log] == ["alpha", "beta"]
    assert all(item.reason for item in log)


def test_the_registry_records_the_actor_it_performed_the_step_as():
    registry = KnowledgeRegistry()
    submit(registry, make_unclassified("a", statement=STATEMENT))
    steps = registry.records()[0].provenance.steps
    assert any(step.actor == REGISTRY_ACTOR for step in steps)


def test_an_already_classified_chain_is_not_classified_a_second_time():
    """A stage recorded twice would make the chain claim work that never happened."""
    registry = KnowledgeRegistry()
    unit = make_unit("a", statement=STATEMENT)
    classification = KnowledgeClassifier().classify(unit)
    registry.submit(unit, classification)
    steps = registry.records()[0].provenance.steps
    assert sum(1 for step in steps if step.stage is Stage.CLASSIFIED) <= 1


# ---------------------------------------------------------------------------
# KnowledgeRegistry — lookups
# ---------------------------------------------------------------------------


def test_membership_iteration_and_length_read_the_same_population():
    registry = KnowledgeRegistry([registered("a"), registered("b")])
    ids = registry.knowledge_ids()
    assert len(registry) == len(ids) == 2
    assert all(knowledge_id in registry for knowledge_id in ids)
    assert "UCKO-NOBODY-0001" not in registry
    assert tuple(record.knowledge_id for record in registry) == ids


def test_get_reports_an_unregistered_identifier_as_absent():
    assert KnowledgeRegistry().get("UCKO-NOBODY-0001") is None


def test_require_refuses_an_unregistered_identifier():
    with pytest.raises(RegistrationError) as exc:
        KnowledgeRegistry().require("UCKO-NOBODY-0001")
    assert "not registered" in str(exc.value)


def test_a_record_is_reachable_by_its_content_digest():
    record = registered("a", statement=STATEMENT)
    registry = KnowledgeRegistry([record])
    assert registry.by_content_hash(record.knowledge_sha256) is record
    assert registry.by_content_hash("0" * 64) is None


def test_resolution_accepts_a_canonical_id_a_provider_local_key_or_a_digest():
    registry = KnowledgeRegistry()
    admission = submit(registry, unit_from("alpha", "a", STATEMENT))
    record = registry.require(admission.knowledge_id)
    assert registry.resolve(record.knowledge_id) is record
    assert registry.resolve("alpha:a") is record
    assert registry.resolve(record.knowledge_sha256) is record
    assert registry.resolve("nothing-like-this") is None


def test_the_reference_map_accepts_a_bare_key_while_it_stays_unambiguous():
    """A provider may cite a peer by its own key without knowing the platform."""
    registry = KnowledgeRegistry()
    admission = submit(registry, unit_from("alpha", "only-here", STATEMENT))
    mapping = registry.reference_map()
    assert mapping["alpha:only-here"] == admission.knowledge_id
    assert mapping["only-here"] == admission.knowledge_id
    assert mapping[admission.knowledge_id] == admission.knowledge_id


def test_a_bare_key_two_providers_use_for_different_knowledge_is_withdrawn():
    """Withdrawn rather than resolved by guess: an ambiguous citation is not a reference."""
    registry = KnowledgeRegistry()
    first = submit(registry, unit_from("alpha", "shared", "The first distinct assertion here."))
    second = submit(registry, unit_from("beta", "shared", "A second and different assertion."))
    assert first.knowledge_id != second.knowledge_id
    mapping = registry.reference_map()
    assert "shared" not in mapping
    assert mapping["alpha:shared"] == first.knowledge_id
    assert mapping["beta:shared"] == second.knowledge_id


def test_a_bare_key_two_providers_use_for_the_same_knowledge_stays_resolvable():
    """Two providers agreeing about one thing is not an ambiguity."""
    registry = KnowledgeRegistry()
    admission = submit(registry, unit_from("alpha", "shared", STATEMENT))
    submit(registry, unit_from("beta", "shared", STATEMENT))
    assert registry.reference_map()["shared"] == admission.knowledge_id


def test_a_third_provider_cannot_revive_a_withdrawn_bare_key():
    registry = KnowledgeRegistry()
    submit(registry, unit_from("alpha", "shared", "The first distinct assertion here."))
    submit(registry, unit_from("beta", "shared", "A second and different assertion."))
    submit(registry, unit_from("gamma", "shared", "The first distinct assertion here."))
    assert "shared" not in registry.reference_map()


# ---------------------------------------------------------------------------
# KnowledgeRegistry — classification queries
# ---------------------------------------------------------------------------


def test_every_classification_query_selects_only_matching_records():
    matching = registered(
        "a",
        kind=KnowledgeKind.PRINCIPLE,
        authority=KnowledgeAuthority.CONSTITUTIONAL,
        lifecycle=Lifecycle.OPERATIONAL,
        universe="ALPHA",
        owner="OWNER-A",
    )
    other = registered(
        "b",
        kind=KnowledgeKind.FACT,
        authority=KnowledgeAuthority.ADVISORY,
        lifecycle=Lifecycle.DEPRECATED,
        universe="BETA",
        owner="OWNER-B",
    )
    registry = KnowledgeRegistry([matching, other])
    assert registry.by_kind(KnowledgeKind.PRINCIPLE) == (matching,)
    assert registry.by_authority(KnowledgeAuthority.CONSTITUTIONAL) == (matching,)
    assert registry.by_lifecycle(Lifecycle.OPERATIONAL) == (matching,)
    assert registry.by_universe("ALPHA") == (matching,)
    assert registry.by_owner("OWNER-A") == (matching,)
    assert registry.by_kind(KnowledgeKind.EXCEPTION) == ()


def test_by_provider_finds_a_provider_that_only_corroborated():
    """Corroboration is contribution: a provider that agreed still supplied the knowledge."""
    registry = KnowledgeRegistry()
    submit(registry, unit_from("alpha", "a", STATEMENT))
    submit(registry, unit_from("beta", "a", STATEMENT))
    assert len(registry.by_provider("beta")) == 1
    assert registry.by_provider("nobody") == ()


def test_active_and_multi_sourced_select_what_they_name():
    registry = KnowledgeRegistry()
    submit(registry, unit_from("alpha", "a", STATEMENT))
    submit(registry, unit_from("beta", "a", STATEMENT))
    submit(registry, unit_from("alpha", "b", "A second and distinct canonical assertion."))
    assert len(registry.multi_sourced()) == 1
    assert len(registry.active()) == len(registry.records())
    assert registry.provider_ids() == ("alpha", "beta")


# ---------------------------------------------------------------------------
# KnowledgeRegistry — integrity and projection
# ---------------------------------------------------------------------------


def test_the_seal_is_deterministic_and_moves_when_the_population_does():
    registry = KnowledgeRegistry([registered("a")])
    first = registry.seal()
    assert first == KnowledgeRegistry([registered("a")]).seal()
    registry.register(registered("b"))
    assert registry.seal() != first


def test_the_counts_describe_the_registry_they_are_taken_over():
    registry = KnowledgeRegistry()
    submit(registry, unit_from("alpha", "a", STATEMENT))
    submit(registry, unit_from("beta", "a", STATEMENT))
    counts = registry.counts()
    assert counts == {
        "records": 1,
        "providers": 2,
        "corroborated": 1,
        "active": 1,
        "relations": 0,
    }


def test_the_registry_envelope_is_deterministic_and_carries_no_wall_clock():
    registry = KnowledgeRegistry([registered("a"), registered("b")])
    document = registry.to_document()
    assert document["schema"] == REGISTRY_SCHEMA
    assert document["version"] == REGISTRY_VERSION
    assert document["seal"] == registry.seal()
    assert [item["knowledge_id"] for item in document["records"]] == list(registry.knowledge_ids())
    assert document == KnowledgeRegistry([registered("a"), registered("b")]).to_document()


def test_the_projection_resolves_relations_through_the_reference_map():
    """The bridge into UKDA: provider-local edges become canonical ones on the way out."""
    registry = KnowledgeRegistry()
    target = submit(registry, unit_from("alpha", "target", "The knowledge being depended upon."))
    submit(
        registry,
        unit_from(
            "alpha",
            "source",
            "The knowledge that depends on another.",
            relations=(RelationDeclaration(RelationType.DEPENDS_ON, "alpha:target"),),
        ),
    )
    base = registry.to_knowledge_base()
    depending = next(obj for obj in base.objects() if obj.dependencies)
    assert depending.dependencies == (target.knowledge_id,)


def test_the_projection_carries_decision_records_through_unchanged(seed_base):
    """UKIP does not own the decision record shape and will not synthesise one."""
    decision = seed_base.decisions()[0]
    registry = KnowledgeRegistry()
    submit(
        registry,
        unit_from(
            "alpha",
            "a",
            STATEMENT,
            relations=(RelationDeclaration(RelationType.DEPENDS_ON, decision.decision_id),),
        ),
    )
    base = registry.to_knowledge_base([decision])
    assert base.decisions() == (decision,)
    obj = base.objects()[0]
    assert obj.decision_links == (decision.decision_id,)
    assert obj.dependencies == ()
