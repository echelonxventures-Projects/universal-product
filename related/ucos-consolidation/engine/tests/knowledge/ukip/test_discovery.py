"""UKIP Part 09 — discovery as a duplication-prevention mechanism, exercised as one.

WHY THIS MODULE EXISTS. Discovery's whole claim is that knowledge which cannot be found
gets re-authored, so every addressing mode and the three discover-before-create verdicts
are load-bearing. None of them had a test: the REUSE verdict that refuses a second
authoring, the exact content-digest match that makes it decisive, and
:meth:`DiscoveryAnswer.require_create_allowed` — the fail-closed call a caller makes
before authoring — were all reachable only by reading them.
"""

from __future__ import annotations

import pytest

from engine.knowledge.model import KnowledgeAuthority, KnowledgeKind, Lifecycle, RelationType
from engine.knowledge.ukip.contracts import RelationDeclaration
from engine.knowledge.ukip.discovery import (
    SEMANTIC_EXTEND_THRESHOLD,
    SEMANTIC_REUSE_THRESHOLD,
    CoverageReport,
    DiscoveryAnswer,
    DiscoveryHit,
    KnowledgeDiscovery,
    ReuseCandidate,
    Verdict,
    build_discovery,
    tokenize,
)
from engine.knowledge.ukip.errors import DiscoveryBypassError
from engine.knowledge.ukip.registry import KnowledgeRegistry

from .conftest import make_unit, register, unit_from


@pytest.fixture
def discovery(simple_registry: KnowledgeRegistry) -> KnowledgeDiscovery:
    return build_discovery(simple_registry)


def _id_of(discovery: KnowledgeDiscovery, title: str) -> str:
    for record in discovery.registry.records():
        if record.title == title:
            return record.knowledge_id
    raise AssertionError(f"no record titled {title!r}")


# -- tokenisation ---------------------------------------------------------------------


def test_tokenisation_is_lowercase_alphanumeric_and_shared_by_every_path():
    assert tokenize("Alpha-Beta, GAMMA 42!") == ("alpha", "beta", "gamma", "42")
    assert tokenize("") == ()
    assert tokenize("   ---   ") == ()


def test_the_terms_a_record_matches_on_are_the_terms_search_uses(discovery):
    identifier = _id_of(discovery, "Title a")
    assert "alpha" in discovery.terms_of(identifier)
    assert discovery.terms_of("UKID-ABSENT") == ()


# -- addressing -----------------------------------------------------------------------


def test_a_record_answers_to_every_address_anyone_might_hold(discovery):
    identifier = _id_of(discovery, "Title a")
    record = discovery.locate(identifier)
    assert record is not None
    assert discovery.locate(record.knowledge_sha256) is record
    addresses = discovery.addresses_of(identifier)
    # id, digest, provider-local `provider:key` and the bare key while it is unambiguous
    assert set(addresses) == {
        identifier,
        record.knowledge_sha256,
        "test-provider:a",
        "a",
    }
    assert all(discovery.locate(address) is record for address in addresses)


def test_an_address_nothing_answers_to_resolves_to_nothing(discovery):
    assert discovery.locate("nothing-resolves-to-this") is None
    assert discovery.addresses_of("UKID-ABSENT") == ()


def test_discoverability_is_the_conjunction_of_identifier_digest_and_search(discovery):
    identifier = _id_of(discovery, "Title a")
    assert discovery.is_discoverable(identifier) is True
    assert discovery.is_discoverable("UKID-ABSENT") is False


# -- classification and provider cuts -------------------------------------------------


def test_every_classification_cut_is_delegated_to_the_registry(discovery):
    assert len(discovery.by_kind(KnowledgeKind.FACT)) == 3
    assert discovery.by_kind(KnowledgeKind.PRINCIPLE) == ()
    assert len(discovery.by_authority(KnowledgeAuthority.ENGINEERING)) == 3
    assert len(discovery.by_lifecycle(Lifecycle.OPERATIONAL)) == 3
    assert len(discovery.by_universe("TEST")) == 3
    assert discovery.by_universe("OTHER") == ()
    assert len(discovery.by_owner("TEST-OWNER")) == 3
    assert len(discovery.by_provider("test-provider")) == 3
    assert discovery.by_provider("nobody") == ()


# -- ranked search --------------------------------------------------------------------


def test_a_query_with_no_terms_returns_nothing_rather_than_everything(discovery):
    assert discovery.search("") == ()
    assert discovery.search("   ") == ()


def test_search_returns_only_records_that_matched_a_term(discovery):
    hits = discovery.search("Alpha")
    assert [h.title for h in hits] == ["Title a"]
    assert hits[0].matched == ("alpha",)
    assert discovery.search("nonexistentterm") == ()


def test_search_ranks_corroborated_and_more_authoritative_knowledge_higher():
    solo = make_unit("solo", statement="Shared discovery vocabulary statement one.")
    left = unit_from("alpha", "pair", "Shared discovery vocabulary statement two.")
    right = unit_from("beta", "pair", "Shared discovery vocabulary statement two.")
    discovery = build_discovery(register((solo, left, right)))
    hits = discovery.search("shared discovery vocabulary statement")
    assert len(hits) == 2
    assert hits[0].provider_ids == ("alpha", "beta")
    assert hits[0].score > hits[1].score


def test_search_is_deterministic_and_honours_its_limit(discovery):
    assert discovery.search("statement") == discovery.search("statement")
    assert len(discovery.search("statement", limit=1)) == 1


def test_a_hit_serialises_the_fields_a_caller_ranks_on(discovery):
    payload = discovery.search("Alpha")[0].to_dict()
    assert set(payload) == {
        "knowledge_id",
        "title",
        "kind",
        "authority",
        "score",
        "matched",
        "provider_ids",
    }
    assert payload["matched"] == ["alpha"]


# -- relationship neighbourhood -------------------------------------------------------


def test_the_neighbourhood_resolves_declared_relations_to_canonical_identifiers(discovery):
    a, b = _id_of(discovery, "Title a"), _id_of(discovery, "Title b")
    assert discovery.related(b) == (a,)
    assert discovery.related(a) == ()


def test_the_neighbourhood_of_an_unknown_record_is_empty(discovery):
    assert discovery.related("UKID-ABSENT") == ()


def test_a_relation_to_knowledge_the_registry_does_not_hold_is_not_a_neighbour():
    dangling = make_unit(
        "d",
        statement="Delta knowledge statement.",
        relations=(RelationDeclaration(RelationType.DEPENDS_ON, "nowhere"),),
    )
    discovery = build_discovery(register((dangling,)))
    assert discovery.related(discovery.registry.knowledge_ids()[0]) == ()


# -- discover before create -----------------------------------------------------------


def test_unrelated_knowledge_may_be_created(discovery):
    answer = discovery.discover_before_create(
        "Entirely unrelated subject matter concerning orbital mechanics.",
        title="Orbital mechanics",
    )
    assert answer.verdict is Verdict.CREATE
    assert answer.may_create is True
    assert answer.must_reuse is False
    assert answer.candidates == ()
    assert answer.best is None
    assert answer.searched == 3
    answer.require_create_allowed()


def test_an_exact_content_digest_match_is_decisive_and_demands_reuse(discovery):
    record = discovery.registry.records()[0]
    answer = discovery.discover_before_create(
        record.statement,
        title=record.title,
        rationale=record.rationale,
        kind=record.kind,
    )
    assert answer.verdict is Verdict.REUSE
    assert answer.must_reuse is True
    best = answer.best
    assert best is not None
    assert best.exact is True
    assert best.overlap == 1.0
    assert best.knowledge_id == record.knowledge_id


def test_creation_after_a_reuse_verdict_is_refused_and_names_what_to_reuse(discovery):
    record = discovery.registry.records()[0]
    answer = discovery.discover_before_create(
        record.statement, title=record.title, rationale=record.rationale, kind=record.kind
    )
    with pytest.raises(DiscoveryBypassError):
        answer.require_create_allowed()


def test_a_reuse_verdict_with_no_candidate_still_refuses_creation():
    """The guard reads ``best`` for the message, never for the decision — a REUSE verdict
    refuses even when no candidate survived trimming."""
    answer = DiscoveryAnswer(verdict=Verdict.REUSE, query="q")
    assert answer.best is None
    with pytest.raises(DiscoveryBypassError):
        answer.require_create_allowed()


def test_high_term_overlap_without_a_digest_match_also_demands_reuse():
    existing = make_unit(
        "e",
        title="Deterministic canonical ordering",
        statement="Deterministic canonical ordering keeps every emitted artifact stable.",
        rationale="Stability is what makes a digest comparable across runs.",
    )
    discovery = build_discovery(register((existing,)))
    answer = discovery.discover_before_create(
        "Deterministic canonical ordering keeps every emitted artifact stable.",
        title="Deterministic canonical ordering",
        rationale="Stability is what makes a digest comparable across runs.",
    )
    assert answer.verdict is Verdict.REUSE
    assert answer.best is not None
    assert answer.best.exact is False
    assert answer.best.overlap >= SEMANTIC_REUSE_THRESHOLD
    assert answer.best.reason == "semantically equivalent to existing knowledge"


def test_moderate_overlap_asks_for_extension_rather_than_a_second_authoring():
    existing = make_unit(
        "f",
        title="Canonical ordering",
        statement="Canonical ordering keeps emitted artifacts stable across runs.",
        rationale="",
    )
    discovery = build_discovery(register((existing,)))
    answer = discovery.discover_before_create(
        "Canonical ordering keeps emitted artifacts stable across runs, plus retention.",
        title="Canonical ordering",
    )
    assert answer.verdict is Verdict.EXTEND
    assert answer.may_create is False
    assert answer.must_reuse is False
    assert answer.best is not None
    assert SEMANTIC_EXTEND_THRESHOLD <= answer.best.overlap < SEMANTIC_REUSE_THRESHOLD
    assert answer.best.reason == "closely related; extend or link instead of duplicating"
    answer.require_create_allowed()


def test_the_exact_home_is_never_also_offered_as_an_overlap_candidate(discovery):
    record = discovery.registry.records()[0]
    answer = discovery.discover_before_create(
        record.statement, title=record.title, rationale=record.rationale, kind=record.kind
    )
    identifiers = [c.knowledge_id for c in answer.candidates]
    assert identifiers.count(record.knowledge_id) == 1


def test_screening_a_provider_unit_asks_the_same_question_before_submission(discovery):
    record = discovery.registry.records()[0]
    unit = make_unit(
        "screen",
        title=record.title,
        statement=record.statement,
        rationale=record.rationale,
        kind=record.kind,
    )
    assert discovery.screen_unit(unit).verdict is Verdict.REUSE


def test_an_answer_serialises_its_verdict_and_its_candidates(discovery):
    record = discovery.registry.records()[0]
    payload = discovery.discover_before_create(
        record.statement, title=record.title, rationale=record.rationale, kind=record.kind
    ).to_dict()
    assert payload["verdict"] == "reuse"
    assert payload["searched"] == 3
    assert payload["candidates"][0]["exact"] is True
    assert set(payload["candidates"][0]) == {
        "knowledge_id",
        "title",
        "overlap",
        "exact",
        "reason",
    }


def test_overlap_of_an_empty_side_is_zero_rather_than_undefined(discovery):
    assert discovery._overlap((), ("a",)) == 0.0
    assert discovery._overlap(("a",), ()) == 0.0
    assert discovery._overlap(("a", "b"), ("b", "c")) == pytest.approx(1 / 3)


def test_a_reuse_candidate_rounds_its_overlap_for_serialisation():
    candidate = ReuseCandidate("UKID-1", "T", overlap=1 / 3, exact=False, reason="r")
    assert candidate.to_dict()["overlap"] == 0.3333


# -- coverage -------------------------------------------------------------------------


def test_coverage_is_a_deterministic_discoverability_snapshot(discovery):
    report = discovery.coverage()
    assert report.total_records == 3
    assert report.total_providers == 1
    assert report.by_kind == {"fact": 3}
    assert report.by_authority == {"engineering": 3}
    assert report.by_lifecycle == {"operational": 3}
    assert report.by_universe == {"TEST": 3}
    assert report.by_provider == {"test-provider": 3}
    assert report.undiscoverable == ()
    assert report.is_fully_discoverable is True
    assert len(report.single_sourced) == 3
    assert discovery.coverage() == report


def test_coverage_serialises_every_field_it_reports(discovery):
    payload = discovery.coverage().to_dict()
    assert set(payload) == {
        "total_records",
        "total_providers",
        "by_kind",
        "by_authority",
        "by_lifecycle",
        "by_universe",
        "by_provider",
        "undiscoverable",
        "single_sourced",
        "fully_discoverable",
    }
    assert payload["fully_discoverable"] is True


def test_a_record_that_search_cannot_find_is_reported_as_undiscoverable():
    """Not fully discoverable is a REPORT, not a crash: the snapshot names the record
    rather than refusing to produce a snapshot at all."""
    report = CoverageReport(
        total_records=1,
        total_providers=1,
        by_kind={},
        by_authority={},
        by_lifecycle={},
        by_universe={},
        by_provider={},
        undiscoverable=("UKID-LOST",),
    )
    assert report.is_fully_discoverable is False
    assert report.to_dict()["undiscoverable"] == ["UKID-LOST"]


def test_corroborated_knowledge_is_not_counted_as_single_sourced():
    left = unit_from("alpha", "pair", "One statement two providers agree on.")
    right = unit_from("beta", "pair", "One statement two providers agree on.")
    report = build_discovery(register((left, right))).coverage()
    assert report.total_providers == 2
    assert report.single_sourced == ()
    assert report.by_provider == {"alpha": 1, "beta": 1}


def test_a_hit_and_a_candidate_are_value_objects(discovery):
    hit = DiscoveryHit("UKID-1", "T", "fact", "engineering", 3)
    assert hit.matched == () and hit.provider_ids == ()
    assert hit == DiscoveryHit("UKID-1", "T", "fact", "engineering", 3)
