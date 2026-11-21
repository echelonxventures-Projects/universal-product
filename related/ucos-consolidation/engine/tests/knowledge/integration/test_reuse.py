"""Tests for engine.knowledge.integration.reuse — Deliverable 5."""

from __future__ import annotations

import pytest

from engine.knowledge.capability import (
    KNOWLEDGE_ONCE_PRINCIPLE,
    CapabilityRecord,
    assimilate_capabilities,
    is_capability,
)
from engine.knowledge.integration.contracts import Disposition
from engine.knowledge.integration.reuse import ReuseEngine
from engine.knowledge.model import KnowledgeKind
from engine.knowledge.store import KnowledgeBase

from .conftest import make_cko, make_intent


def test_reuse_on_semantic_twin(base):
    engine = ReuseEngine(base)
    # identical substance to COMP-A, same owner -> reuse
    intent = make_intent("NEW", statement="the alpha component substance", owner="TEAM-A")
    assessment = engine.assess(intent)
    assert assessment.disposition is Disposition.REUSE
    assert "COMP-A" in assessment.targets
    assert not assessment.requires_creation
    assert assessment.candidates[0].to_dict()["relation"] == "semantic"


def test_extend_on_same_kind_universe(base):
    engine = ReuseEngine(base)
    intent = make_intent(
        "NEW", title="alpha component v2", statement="alpha component substance improved"
    )
    assessment = engine.assess(intent)
    assert assessment.disposition is Disposition.EXTEND
    assert assessment.targets == ("COMP-A",)
    assert "COMP-A" in assessment.to_dict()["targets"]


def test_compose_on_existing_components(base):
    engine = ReuseEngine(base)
    intent = make_intent(
        "NEW",
        title="Zeta",
        statement="orchestrating flows via bindings",
        dependencies=("COMP-A", "COMP-B"),
    )
    assessment = engine.assess(intent)
    assert assessment.disposition is Disposition.COMPOSE
    assert assessment.targets == ("COMP-A", "COMP-B")


def test_create_when_nothing_reusable():
    engine = ReuseEngine(KnowledgeBase([]))
    assessment = engine.assess(make_intent("NEW"))
    assert assessment.disposition is Disposition.CREATE
    assert assessment.requires_creation
    assert assessment.reasons


def test_compose_needs_two_active_components():
    # only one resolvable component -> not compose (falls through to create)
    base = KnowledgeBase([make_cko("ONLY-A")])
    engine = ReuseEngine(base)
    intent = make_intent(
        "NEW", title="Zeta", statement="orchestrating flows", dependencies=("ONLY-A", "MISSING")
    )
    assert engine.assess(intent).disposition is Disposition.CREATE


# -- capability awareness (Repository Self-Awareness) --------------------------
#
# The engine used to be structurally blind to the repository's own implementation:
# capability facts are a different *kind* of knowledge than the intent proposing a
# capability, so neither the semantic-hash path nor the same-kind/same-universe path
# could ever match one. Every implemented capability was answered CREATE.


def _capability_base(*records) -> KnowledgeBase:
    """A base holding the founding principle plus projected capability facts."""
    return assimilate_capabilities(
        KnowledgeBase([make_cko(KNOWLEDGE_ONCE_PRINCIPLE)]),
        [CapabilityRecord.from_dict(record) for record in records],
    ).base


def _capability_record(**overrides) -> dict[str, object]:
    record: dict[str, object] = {
        "unique_id": "RC-01",
        "canonical_name": "engine.knowledge.ukip",
        "canonical_location": "engine/knowledge/ukip",
        "category": "engine",
        "authority": "EC-1 CERTIFIED",
        "reuse": "REUSE_AS_IS/COMPOSE",
        "replacement_prohibited": True,
        "implementation_status": "CERTIFIED",
        "description": "Knowledge intelligence platform.",
        "evidence_present": True,
        "summary": (
            "Admits provenance chains, classification rules and a knowledge registry from "
            "an unbounded number of providers, recording hash chained provenance for every "
            "registered knowledge record."
        ),
        "symbols": ["KnowledgeRegistry", "ProvenanceLedger", "provenance", "classification"],
    }
    record.update(overrides)
    return record


def test_an_implemented_capability_is_found_and_creation_is_refused():
    base = _capability_base(_capability_record())
    intent = make_intent(
        "NEW",
        title="Universal Knowledge Provenance",
        statement="Record a hash chained provenance chain for every knowledge record.",
    )
    assessment = ReuseEngine(base).assess(intent)
    assert assessment.disposition is Disposition.REUSE
    assert not assessment.requires_creation
    assert assessment.candidates
    assert assessment.candidates[0].relation == "implemented-capability"
    assert any("replacement" in reason for reason in assessment.reasons)


def test_capability_awareness_ignores_kind_and_universe():
    """The whole point: a capability fact never shares an intent's kind or universe."""
    base = _capability_base(_capability_record())
    capability = next(obj for obj in base.objects() if is_capability(obj))
    intent = make_intent(
        "NEW",
        kind=KnowledgeKind.PATTERN,
        universe="SOMETHING-ELSE",
        title="Universal Knowledge Provenance",
        statement="Record a hash chained provenance chain for every knowledge record.",
    )
    assert capability.kind is not intent.kind
    assert capability.universe != intent.universe
    assert ReuseEngine(base).assess(intent).disposition is Disposition.REUSE


def test_a_replaceable_capability_yields_extend_not_reuse():
    base = _capability_base(_capability_record(replacement_prohibited=False))
    intent = make_intent(
        "NEW",
        title="Universal Knowledge Provenance",
        statement="Record a hash chained provenance chain for every knowledge record.",
    )
    assessment = ReuseEngine(base).assess(intent)
    assert assessment.disposition is Disposition.EXTEND
    assert any("extension is permitted" in reason for reason in assessment.reasons)


def test_verification_packages_are_never_offered_as_reuse_targets():
    """You do not implement provenance by reusing the provenance tests."""
    base = _capability_base(
        _capability_record(canonical_location="engine/tests/knowledge/ukip", unique_id="RC-02")
    )
    intent = make_intent(
        "NEW",
        title="Universal Knowledge Provenance",
        statement="Record a hash chained provenance chain for every knowledge record.",
    )
    assessment = ReuseEngine(base).assess(intent)
    assert not [c for c in assessment.candidates if c.relation == "implemented-capability"]


def test_an_unbuilt_capability_is_never_offered_as_a_reuse_target():
    base = _capability_base(_capability_record(implementation_status="PLANNED"))
    intent = make_intent(
        "NEW",
        title="Universal Knowledge Provenance",
        statement="Record a hash chained provenance chain for every knowledge record.",
    )
    assessment = ReuseEngine(base).assess(intent)
    assert not [c for c in assessment.candidates if c.relation == "implemented-capability"]


def test_an_on_topic_intent_outranks_an_off_topic_one():
    """Discrimination is a property of the ranking, measurable without a threshold.

    Asserting a bare CREATE for an off-topic intent would only hold on a corpus large
    enough for inverse document frequency to discriminate; the invariant that holds at
    every corpus size is that the on-topic intent scores strictly higher.
    """
    base = _capability_base(
        _capability_record(),
        _capability_record(
            unique_id="RC-02",
            canonical_name="platform.security",
            canonical_location="platform/security",
            category="platform",
            summary="Authorises subjects, enforces policy and audits access decisions.",
            symbols=["Authoriser", "PolicyDecision", "audit"],
        ),
    )
    engine = ReuseEngine(base)

    def best(title: str, statement: str) -> int:
        candidates = [
            c
            for c in engine.assess(make_intent("NEW", title=title, statement=statement)).candidates
            if c.relation in {"implemented-capability", "nearest-capability"}
        ]
        return candidates[0].score if candidates else 0

    on_topic = best(
        "Universal Knowledge Provenance",
        "Record a hash chained provenance chain for every registered knowledge record.",
    )
    off_topic = best(
        "Bake a chocolate cake",
        "Cream butter and sugar then fold in flour cocoa and eggs and bake.",
    )
    assert on_topic > off_topic


def test_create_carries_the_nearest_capabilities_as_evidence():
    """A CREATE verdict must be auditable, not a bare 'nothing found'."""
    base = _capability_base(_capability_record())
    intent = make_intent(
        "NEW",
        title="Knowledge registry telemetry sampling",
        statement="Sample telemetry counters emitted while registering knowledge.",
    )
    assessment = ReuseEngine(base).assess(intent)
    if assessment.disposition is Disposition.CREATE:
        assert any("confidence floor" in reason for reason in assessment.reasons)
        assert [c for c in assessment.candidates if c.relation == "nearest-capability"]


def test_semantic_reuse_still_takes_precedence_over_capability_matching(base):
    intent = make_intent("NEW", statement="the alpha component substance", owner="TEAM-A")
    assessment = ReuseEngine(base).assess(intent)
    assert assessment.disposition is Disposition.REUSE
    assert assessment.candidates[0].relation == "semantic"


def test_a_base_without_capabilities_behaves_exactly_as_before(base):
    """Capability awareness must not perturb a base that records no capabilities."""
    intent = make_intent(
        "NEW", title="alpha component v2", statement="alpha component substance improved"
    )
    assessment = ReuseEngine(base).assess(intent)
    assert assessment.disposition is Disposition.EXTEND
    assert assessment.targets == ("COMP-A",)


def test_candidate_ordering_is_deterministic():
    base = _capability_base(
        _capability_record(),
        _capability_record(
            unique_id="RC-02",
            canonical_name="engine.knowledge",
            canonical_location="engine/knowledge",
        ),
    )
    intent = make_intent(
        "NEW",
        title="Universal Knowledge Provenance",
        statement="Record a hash chained provenance chain for every knowledge record.",
    )
    engine = ReuseEngine(base)
    first = [c.cko_id for c in engine.assess(intent).candidates]
    second = [c.cko_id for c in ReuseEngine(base).assess(intent).candidates]
    assert first == second


def test_similarity_is_zero_when_nothing_is_shared_and_when_a_vector_has_no_length():
    """TWO ZEROS FOR TWO DIFFERENT REASONS, and both are short-circuits.

    No shared term means the cosine's numerator is zero, and computing the norms first
    would be arithmetic over vocabularies that cannot agree — the answer is decided before
    the division. A zero norm is the arithmetic guard: it happens when every term a
    document carries appears in EVERY document, so its inverse document frequency is zero
    and the vector has no length. Dividing there is a ZeroDivisionError, and the honest
    answer is that a term shared by everything distinguishes nothing.
    """
    engine = ReuseEngine(KnowledgeBase([]))

    assert engine._similarity(frozenset({"alpha"}), frozenset({"beta"}), {}) == 0.0

    ubiquitous = {"shared": 0.0}
    assert engine._similarity(frozenset({"shared"}), frozenset({"shared"}), ubiquitous) == 0.0

    real = {"alpha": 1.0, "beta": 1.0}
    assert engine._similarity(
        frozenset({"alpha", "beta"}), frozenset({"alpha", "beta"}), real
    ) == pytest.approx(1.0)


def test_a_capability_never_proposes_itself_as_its_own_reuse_candidate():
    """The intent's own id is skipped, and the reason is that it would always win.

    An intent scored against the capability recorded under its own id compares a document
    with itself, which is a perfect match — so without the skip every MODIFY of an existing
    capability would be told to reuse the thing it is modifying, and the strongest candidate
    on every such assessment would be the subject of the assessment.
    """
    base = _capability_base(
        _capability_record(),
        _capability_record(
            unique_id="RC-02",
            canonical_name="engine.knowledge.other",
            canonical_location="engine/knowledge/other",
        ),
    )
    engine = ReuseEngine(base)
    projected = [obj.cko_id for obj in base.objects() if is_capability(obj)]
    assert len(projected) == 2

    intent = make_intent(
        projected[0],
        title="Universal Knowledge Provenance",
        statement="Record a hash chained provenance chain for every knowledge record.",
    )
    named = {c.cko_id for c in engine._capability_candidates(intent)}
    assert projected[0] not in named, "the intent was offered itself for reuse"
    assert projected[1] in named


def test_a_capability_sharing_no_vocabulary_with_the_intent_is_not_ranked_at_all():
    """A zero score is not a weak candidate — it is not a candidate.

    Keeping it would put every capability in the repository on every ranked list, ordered
    by a number that says nothing, and the caller adjudicating those candidates would be
    reading a list whose tail is noise. Only capabilities that actually share vocabulary
    with the intent are scored in.
    """
    base = _capability_base(
        _capability_record(),
        _capability_record(
            unique_id="RC-02",
            canonical_name="platform.palette.chooser",
            canonical_location="platform/palette/chooser",
            description="Colour palette selection.",
            summary="Chooses colour palettes for diagrams and charts.",
            symbols=["PaletteChooser"],
        ),
    )
    engine = ReuseEngine(base)
    # THE INTENT USES ONLY DISTINCTIVE VOCABULARY, and that is what makes the test work.
    # Every projected capability fact shares a large boilerplate ("canonical", "owner",
    # "implemented", ...), and the inverse-document-frequency weighting is smoothed, so a
    # single boilerplate word in common is enough to score ABOVE zero. Only an intent whose
    # terms are absent from a document entirely reaches the exclusion.
    intent = make_intent("NEW", title="Provenance", statement="Hash chained provenance.")
    named = {c.cko_id for c in engine._capability_candidates(intent)}
    projected = {obj.cko_id: obj for obj in base.objects() if is_capability(obj)}
    unrelated = next(
        cko_id
        for cko_id, obj in projected.items()
        if "palette" in (obj.statement + obj.title).lower()
    )
    assert unrelated not in named, "a capability sharing no vocabulary was ranked anyway"
    assert named, "every capability was excluded, so the exclusion proves nothing"
