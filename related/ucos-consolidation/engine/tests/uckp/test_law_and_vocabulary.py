"""The root law as executable data, and the open vocabularies that keep it extensible."""

from __future__ import annotations

import pytest

from engine.civilization.generation import GENERATION_STRATA
from engine.graph.architecture.layers import LAYER_ORDER, UNCLASSIFIED
from engine.uckp.assimilation import verify_vocabulary_alignment
from engine.uckp.canonical import content_hash
from engine.uckp.errors import AssimilationError, LawViolation
from engine.uckp.law import (
    GOVERNED_CATEGORIES,
    LAW_ID,
    NON_AUTHORITATIVE_CATEGORIES,
    ROOT_LAW,
    SUPREMACY_CLAUSE,
    Article,
    Invariant,
    RootLaw,
    StopCondition,
)
from engine.uckp.vocabulary import (
    ARCHITECTURE_LAYER,
    AUTHORITY_TIER,
    CIVILIZATION_STRATUM,
    DEFAULT_VOCABULARIES,
    DISCOVERY_DIMENSION,
    FACET_VOCABULARY,
    KNOWLEDGE_KIND,
    LIFECYCLE_STAGE,
    PROJECTION_KIND,
    RELATION_TYPE,
    UKIP_FACET,
    Term,
    Vocabulary,
    VocabularyRegistry,
    build_vocabulary_registry,
)

# --- the law --------------------------------------------------------------------


def test_the_law_declares_twenty_articles_seventeen_invariants_thirteen_stops():
    assert len(ROOT_LAW.articles) == 20
    assert len(ROOT_LAW.invariants) == 17
    assert len(ROOT_LAW.stop_conditions) == 13
    assert ROOT_LAW.law_id == LAW_ID == "UCKP-LAW-0001"


def test_the_law_is_internally_coherent():
    ROOT_LAW.require_coherent()


def test_every_invariant_is_enforced_by_at_least_one_article():
    """An invariant no clause demands has no constitutional basis."""
    enforced = {i for article in ROOT_LAW.articles for i in article.enforces}
    assert set(ROOT_LAW.invariant_ids()) == enforced


def test_every_article_enforcement_reference_resolves():
    declared = set(ROOT_LAW.invariant_ids())
    for article in ROOT_LAW.articles:
        assert set(article.enforces) <= declared


def test_every_stop_condition_names_only_declared_invariants():
    declared = set(ROOT_LAW.invariant_ids())
    for condition in ROOT_LAW.stop_conditions:
        assert set(condition.invariants) <= declared


def test_article_one_is_the_supremacy_clause():
    assert ROOT_LAW.article("UCKP-ART-01").clause == SUPREMACY_CLAUSE
    assert ROOT_LAW.supremacy == SUPREMACY_CLAUSE


def test_lookup_by_id_and_refusal_of_unknown_ids():
    assert ROOT_LAW.invariant("UCKP-INV-01").name == "knowledge-once"
    with pytest.raises(LawViolation):
        ROOT_LAW.article("UCKP-ART-99")
    with pytest.raises(LawViolation):
        ROOT_LAW.invariant("UCKP-INV-99")


def test_articles_enforcing_is_derived_from_the_articles():
    enforcing = ROOT_LAW.articles_enforcing("UCKP-INV-03")
    assert enforcing
    assert all("UCKP-INV-03" in article.enforces for article in enforcing)


def test_the_law_digest_is_deterministic_and_covers_every_clause():
    assert ROOT_LAW.digest() == ROOT_LAW.digest()
    assert ROOT_LAW.digest() == content_hash(ROOT_LAW.to_dict())


def test_governed_and_non_authoritative_categories_are_disjoint():
    """Nothing may both require a canonical home and be forbidden from holding one."""
    assert not set(GOVERNED_CATEGORIES) & set(NON_AUTHORITATIVE_CATEGORIES)


def test_governs_and_is_non_authoritative_are_case_insensitive():
    assert ROOT_LAW.governs("Law")
    assert ROOT_LAW.governs(" knowledge ")
    assert not ROOT_LAW.governs("repository")
    assert ROOT_LAW.is_non_authoritative("REPOSITORY")
    assert ROOT_LAW.is_non_authoritative("markdown")


def test_the_repository_and_the_document_are_declared_non_authoritative():
    for name in ("repository", "document", "file", "folder", "source-code", "schema", "database"):
        assert ROOT_LAW.is_non_authoritative(name)


def test_a_law_with_a_duplicate_article_is_refused():
    duplicate = ROOT_LAW.articles[0]
    broken = RootLaw(
        law_id="X",
        version="1",
        supremacy="s",
        articles=(duplicate, duplicate),
        invariants=ROOT_LAW.invariants,
        stop_conditions=(),
        governed_categories=(),
        non_authoritative_categories=(),
    )
    with pytest.raises(LawViolation, match="declared twice"):
        broken.require_coherent()


def test_a_law_enforcing_an_undeclared_invariant_is_refused():
    broken = RootLaw(
        law_id="X",
        version="1",
        supremacy="s",
        articles=(Article("A-1", "t", "c", enforces=("NOPE",)),),
        invariants=(Invariant("NOPE-OTHER", "n", "s"),),
        stop_conditions=(),
        governed_categories=(),
        non_authoritative_categories=(),
    )
    with pytest.raises(LawViolation, match="undeclared invariant"):
        broken.require_coherent()


def test_a_law_with_an_invariant_no_article_enforces_is_refused():
    broken = RootLaw(
        law_id="X",
        version="1",
        supremacy="s",
        articles=(Article("A-1", "t", "c", enforces=("I-1",)),),
        invariants=(Invariant("I-1", "n", "s"), Invariant("I-2", "n2", "s2")),
        stop_conditions=(),
        governed_categories=(),
        non_authoritative_categories=(),
    )
    with pytest.raises(LawViolation, match="enforced by no article"):
        broken.require_coherent()


def test_a_stop_condition_naming_an_undeclared_invariant_is_refused():
    broken = RootLaw(
        law_id="X",
        version="1",
        supremacy="s",
        articles=(Article("A-1", "t", "c", enforces=("I-1",)),),
        invariants=(Invariant("I-1", "n", "s"),),
        stop_conditions=(StopCondition("S-1", "s", ("NOPE",)),),
        governed_categories=(),
        non_authoritative_categories=(),
    )
    with pytest.raises(LawViolation, match="undeclared invariant"):
        broken.require_coherent()


def test_a_duplicate_invariant_declaration_is_refused():
    invariant = ROOT_LAW.invariants[0]
    broken = RootLaw(
        law_id="X",
        version="1",
        supremacy="s",
        articles=(Article("A-1", "t", "c", enforces=(invariant.invariant_id,)),),
        invariants=(invariant, invariant),
        stop_conditions=(),
        governed_categories=(),
        non_authoritative_categories=(),
    )
    with pytest.raises(LawViolation, match="invariant declared twice"):
        broken.require_coherent()


def test_law_values_serialize_completely():
    record = ROOT_LAW.to_dict()
    assert len(record["articles"]) == 20
    assert len(record["invariants"]) == 17
    assert len(record["stop_conditions"]) == 13
    assert record["supremacy"] == SUPREMACY_CLAUSE


def test_every_invariant_is_blocking():
    """A non-blocking constitutional invariant would be an invariant with no force."""
    assert all(invariant.blocking for invariant in ROOT_LAW.invariants)


# --- vocabularies ---------------------------------------------------------------


def test_the_default_registry_declares_the_thirteen_vocabularies():
    registry = build_vocabulary_registry()
    assert len(registry.vocabulary_ids()) == 13
    assert DEFAULT_VOCABULARIES.vocabulary_ids() == registry.vocabulary_ids()


def test_a_vocabulary_admits_an_unknown_future_term_by_registration():
    """Article 17: extension is registration, never amendment."""
    registry = build_vocabulary_registry()
    before = registry.require(KNOWLEDGE_KIND)
    assert not before.has("uckp.probe.future")
    registry.extend(KNOWLEDGE_KIND, Term(term_id="uckp.probe.future", definition="something new"))
    assert registry.require(KNOWLEDGE_KIND).has("uckp.probe.future")


def test_extension_derives_a_new_vocabulary_and_leaves_the_original_untouched():
    declared = build_vocabulary_registry().require(AUTHORITY_TIER)
    widened = declared.extended_with(Term(term_id="planetary", definition="new tier"))
    assert widened.has("planetary")
    assert not declared.has("planetary")


def test_registering_a_wholly_new_vocabulary_is_permitted():
    registry = build_vocabulary_registry()
    registry.register(
        Vocabulary(
            vocabulary_id="test.new-dimension",
            purpose="a dimension the law never enumerated",
            terms=(Term(term_id="alpha", definition="first"),),
        )
    )
    assert "test.new-dimension" in registry.vocabulary_ids()
    assert registry.require_term("test.new-dimension", "alpha").term_id == "alpha"


def test_the_registry_reports_itself_extensible():
    assert build_vocabulary_registry().is_extensible()


def test_requiring_an_unknown_term_fails_closed():
    registry = build_vocabulary_registry()
    with pytest.raises(LawViolation, match="not registered in this vocabulary"):
        registry.require_term(KNOWLEDGE_KIND, "no-such-kind")


def test_requiring_an_unknown_vocabulary_fails_closed():
    registry = build_vocabulary_registry()
    with pytest.raises(LawViolation, match="no such vocabulary"):
        registry.require("no.such.vocabulary")
    assert registry.get("no.such.vocabulary") is None


def test_lifecycle_declares_lawful_successors():
    lifecycle = build_vocabulary_registry().require(LIFECYCLE_STAGE)
    assert lifecycle.has("draft")
    assert lifecycle.can_transition("draft", "review")
    assert not lifecycle.can_transition("draft", "no-such-stage")


def test_vocabulary_digest_is_deterministic_and_changes_on_extension():
    declared = build_vocabulary_registry().require(RELATION_TYPE)
    assert declared.digest() == declared.digest()
    widened = declared.extended_with(Term(term_id="orbits", definition="new relation"))
    assert widened.digest() != declared.digest()


def test_registry_digest_covers_every_vocabulary():
    registry = build_vocabulary_registry()
    before = registry.digest()
    registry.extend(RELATION_TYPE, Term(term_id="orbits", definition="new relation"))
    assert registry.digest() != before


def test_registry_document_names_every_vocabulary_and_its_purpose():
    document = build_vocabulary_registry().to_document()
    assert document["vocabularies"]
    for entry in document["vocabularies"]:
        assert entry["purpose"]


def test_term_lookup_returns_none_for_a_stranger_and_the_term_otherwise():
    vocabulary = build_vocabulary_registry().require(KNOWLEDGE_KIND)
    assert vocabulary.get("no-such") is None
    assert vocabulary.get("law").term_id == "law"
    assert "law" in vocabulary.term_ids()


def test_a_registered_vocabulary_is_returned_by_register():
    registry = VocabularyRegistry()
    vocabulary = Vocabulary("v", "p", (Term("t", "d"),))
    assert registry.register(vocabulary) is vocabulary


# --- vocabularies: the refusals that make "append-only" mean something ------------


def test_a_vocabulary_refuses_to_declare_the_same_term_twice():
    """Two definitions of one term is two meanings for one digest."""
    with pytest.raises(LawViolation, match="term declared twice"):
        Vocabulary(
            "test.duplicated",
            "a vocabulary that says the same thing twice",
            (Term("colour", "the first meaning"), Term("colour", "the second meaning")),
        )


def test_registering_the_identical_term_again_returns_the_same_vocabulary():
    """Idempotent, because re-registration is not a change and must not look like one."""
    term = Term("teal", "a blue-green")
    vocabulary = Vocabulary("test.colours", "colours", (term,))
    assert vocabulary.extended_with(term) is vocabulary
    assert vocabulary.extended_with(Term("teal", "a blue-green")) is vocabulary


def test_redefining_a_registered_term_is_refused():
    """A term whose meaning changed retroactively invalidates every digest under it."""
    vocabulary = Vocabulary("test.colours", "colours", (Term("teal", "a blue-green"),))
    with pytest.raises(LawViolation, match="may not be redefined"):
        vocabulary.extended_with(Term("teal", "actually a shade of grey"))


def test_the_registry_refuses_a_second_vocabulary_under_one_identity():
    registry = VocabularyRegistry((Vocabulary("test.one", "the first"),))
    with pytest.raises(LawViolation, match="vocabulary already registered"):
        registry.register(Vocabulary("test.one", "a rival under the same id"))


def test_the_registry_reports_itself_closed_when_a_vocabulary_swallows_an_extension():
    """The extensibility check must have a reachable False, or it proves nothing."""

    class Swallowing(Vocabulary):
        """Accepts the extension and returns a vocabulary without it."""

        def extended_with(self, term: Term) -> Vocabulary:
            return self

    registry = VocabularyRegistry((Swallowing("test.closed", "closed in practice"),))
    assert registry.is_extensible() is False
    assert build_vocabulary_registry().is_extensible() is True


# --- the five engine structural vocabularies (CEP-MOD-002 M-1…M-5) ---------------


@pytest.mark.parametrize(
    ("vocabulary_id", "size"),
    [
        (CIVILIZATION_STRATUM, 9),
        (ARCHITECTURE_LAYER, 14),
        (PROJECTION_KIND, 13),
        (UKIP_FACET, 6),
        (DISCOVERY_DIMENSION, 8),
    ],
)
def test_each_engine_vocabulary_is_registered_and_admits_a_stranger(vocabulary_id, size):
    """INV-14 could not reach these term sets while they lived only in engine code."""
    registry = build_vocabulary_registry()
    vocabulary = registry.require(vocabulary_id)
    assert len(vocabulary.term_ids()) == size
    assert all(vocabulary.get(term_id).definition for term_id in vocabulary.term_ids())
    registry.extend(vocabulary_id, Term("uckp.probe.future", "an unregistered future member"))
    assert registry.require(vocabulary_id).has("uckp.probe.future")


def test_every_projection_matches_the_vocabulary_that_owns_it():
    """Nine closed term sets, nine registered owners, zero divergences. Fails closed."""
    verify_vocabulary_alignment()


def test_the_ukip_facets_and_the_uckp_facets_are_not_the_same_vocabulary():
    """Two facet sets name two different decisions; merging them would fork meaning."""
    registry = build_vocabulary_registry()
    ukip = set(registry.require(UKIP_FACET).term_ids())
    uckp = set(registry.require(FACET_VOCABULARY).term_ids())
    assert ukip != uckp
    assert UKIP_FACET != FACET_VOCABULARY


def test_the_stratum_lineage_is_the_generation_chain_read_forwards():
    """GENERATION_STRATA records a predecessor; the vocabulary records the successor."""
    strata = build_vocabulary_registry().require(CIVILIZATION_STRATUM)
    for key, _name, predecessor, _definition in GENERATION_STRATA:
        if predecessor is not None:
            assert strata.can_transition(predecessor, key)
    assert strata.require("SolutionStratum").successors == ()


def test_the_layer_rank_is_the_stack_depth_the_engine_measures():
    """A layer's depth is its index in LAYER_ORDER, so Term.rank must be that index."""
    layers = build_vocabulary_registry().require(ARCHITECTURE_LAYER)
    for term_id in layers.term_ids():
        assert layers.require(term_id).rank == LAYER_ORDER.index(term_id)


def test_the_unclassified_fallback_is_not_a_layer():
    """It is what a category gets when it has no position in the stack, not a position."""
    assert UNCLASSIFIED not in build_vocabulary_registry().require(ARCHITECTURE_LAYER).term_ids()


def test_alignment_fails_closed_when_a_vocabulary_gains_a_term_the_engine_lacks():
    """The guard's whole purpose: registration without projection is a live divergence."""
    registry = build_vocabulary_registry()
    registry.extend(DISCOVERY_DIMENSION, Term("prophecy", "a dimension nobody discovers yet"))
    with pytest.raises(AssimilationError, match="vocabulary alignment failed") as raised:
        verify_vocabulary_alignment(registry)
    assert "'prophecy'" in str(raised.value.context["divergences"])


def test_alignment_fails_closed_when_the_engine_declares_an_unregistered_term():
    """The other direction: a term set may not outrun the registry that owns it."""
    seeded = build_vocabulary_registry()
    declared = seeded.require(UKIP_FACET)
    registry = VocabularyRegistry(
        Vocabulary(
            UKIP_FACET, declared.purpose, tuple(t for t in declared.terms if t.term_id != "version")
        )
        if vocabulary_id == UKIP_FACET
        else seeded.require(vocabulary_id)
        for vocabulary_id in seeded.vocabulary_ids()
    )
    with pytest.raises(AssimilationError, match="vocabulary alignment failed") as raised:
        verify_vocabulary_alignment(registry)
    assert "'version'" in str(raised.value.context["divergences"])
