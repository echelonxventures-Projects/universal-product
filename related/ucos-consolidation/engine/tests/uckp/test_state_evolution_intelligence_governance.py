"""Articles 12, 14, 15, 16: immutable states, endless evolution, self-reasoning, governance."""

from __future__ import annotations

import dataclasses

import pytest

from engine.uckp.errors import (
    EvolutionError,
    GovernanceError,
    LawViolation,
    StateImmutabilityError,
)
from engine.uckp.evolution import (
    CYCLE_LENGTH,
    EVOLUTION_CYCLE,
    EVOLUTION_STAGE,
    EvolutionLedger,
    EvolutionRecord,
    EvolutionStage,
    evolution_stage_vocabulary,
    is_terminal,
    next_stage,
)
from engine.uckp.governance import (
    ANSWERED,
    PERMITTED,
    REFUSED,
    VERDICTS,
    GovernanceDecision,
    GovernanceEngine,
    build_rules,
    inputs_digest_of,
    normalise_arguments,
    rule_for_article,
)
from engine.uckp.intelligence import (
    ReasoningKind,
    build_intelligence,
    reasoning_kinds,
)
from engine.uckp.law import ROOT_LAW
from engine.uckp.state import (
    DELTA_REGISTERS,
    GENESIS_PARENT,
    ConstitutionalDelta,
    ConstitutionalState,
    ConstitutionalTimeline,
    Proof,
)
from engine.uckp.universe import _contribute_evolution_stage_vocabulary
from engine.uckp.vocabulary import Term, Vocabulary, build_vocabulary_registry

# --- constitutional state -------------------------------------------------------


def _genesis(digest: str = "d0") -> ConstitutionalState:
    return ConstitutionalState.genesis(knowledge_digest=digest, knowledge_ids=("urn:a",))


def test_genesis_has_no_parent_and_records_everything_as_added():
    state = _genesis()
    assert state.is_genesis
    assert state.parent_state_id == GENESIS_PARENT
    assert state.sequence == 0
    assert state.knowledge_delta.added == ("urn:a",)
    assert state.verify_integrity()
    assert state.proofs_hold()


def test_a_transition_creates_a_successor_and_never_touches_the_parent():
    """Article 12: no previous state ever changes."""
    genesis = _genesis()
    before = genesis.state_id
    successor = genesis.transition(knowledge_digest="d1")
    assert genesis.state_id == before
    assert successor.parent_state_id == genesis.state_id
    assert successor.sequence == 1
    assert successor.verify_integrity()


def test_a_state_carries_all_five_delta_registers():
    state = _genesis()
    assert {delta.register for delta in state.deltas()} == set(DELTA_REGISTERS)


def test_a_state_carries_replay_validation_and_verification_proofs():
    state = _genesis()
    assert {proof.kind for proof in state.proofs()} == {"replay", "validation", "verification"}
    assert state.proofs_hold()


def test_an_edited_state_fails_its_own_integrity_check():
    state = _genesis()
    tampered = dataclasses.replace(state, knowledge_digest="tampered")
    assert not tampered.verify_integrity()
    with pytest.raises(StateImmutabilityError, match="altered after sealing"):
        tampered.require_immutable()


def test_the_timeline_refuses_a_first_state_that_is_not_genesis():
    genesis = _genesis()
    successor = genesis.transition(knowledge_digest="d1")
    with pytest.raises(StateImmutabilityError, match="first state must be genesis"):
        ConstitutionalTimeline((successor,))


def test_the_timeline_refuses_a_state_that_does_not_reference_the_head():
    genesis = _genesis()
    timeline = ConstitutionalTimeline((genesis,))
    stranger = _genesis("other").transition(knowledge_digest="d9")
    with pytest.raises(StateImmutabilityError, match="reference the current head"):
        timeline.append(stranger)


def test_the_timeline_refuses_a_sequence_that_skips():
    genesis = _genesis()
    timeline = ConstitutionalTimeline((genesis,))
    skipped = dataclasses.replace(genesis.transition(knowledge_digest="d1"), sequence=5).sealed()
    with pytest.raises(StateImmutabilityError, match="increase by exactly one"):
        timeline.append(skipped)


def test_the_timeline_refuses_the_same_state_twice():
    genesis = _genesis()
    timeline = ConstitutionalTimeline((genesis,))
    successor = genesis.transition(knowledge_digest="d1")
    timeline.append(successor)
    with pytest.raises(StateImmutabilityError):
        timeline.append(successor)


def test_the_timeline_exposes_no_way_to_modify_or_remove_a_state():
    """Append-only is a property of the interface, not a convention."""
    timeline = ConstitutionalTimeline((_genesis(),))
    for forbidden in ("remove", "delete", "pop", "truncate", "rewrite", "update", "insert"):
        assert not hasattr(timeline, forbidden)


def test_the_timeline_replays_identically_and_verifies(universe):
    timeline = universe.timeline
    assert timeline.states()
    assert timeline.verify()
    assert timeline.replays_identically()
    assert timeline.proofs_complete()
    assert timeline.audit_complete()
    assert timeline.replay() == timeline.state_ids()


def test_the_timeline_resolves_states_and_lineage(universe):
    timeline = universe.timeline
    head = timeline.require_head()
    assert timeline.head() is head
    assert timeline.get(head.state_id) is head
    assert timeline.get("no-such-state") is None
    assert timeline.lineage(head.state_id)[0] == timeline.state_ids()[0]
    assert timeline.fingerprint() == timeline.fingerprint()
    assert timeline.to_document()["counts"]["states"] == len(timeline.states())


def test_an_empty_timeline_has_no_head():
    timeline = ConstitutionalTimeline()
    assert timeline.head() is None
    with pytest.raises(StateImmutabilityError):
        timeline.require_head()


def test_a_delta_and_a_proof_serialize():
    delta = ConstitutionalDelta("knowledge", added=("a",), removed=("b",), changed=("c",))
    assert delta.to_dict()["register"] == "knowledge"
    proof = Proof("replay", "p", "i", "o")
    assert proof.to_dict()["kind"] == "replay"
    assert proof.as_replay_proof().holds("o")


# --- evolution ------------------------------------------------------------------


def test_the_cycle_has_fifteen_stages_and_no_terminal_one():
    """Article 14: evolution appends, never rewrites, never terminates."""
    assert CYCLE_LENGTH == 15
    assert len(EVOLUTION_CYCLE) == 15
    for stage in EVOLUTION_CYCLE:
        assert not is_terminal(stage)
        assert next_stage(stage) in EVOLUTION_CYCLE


def test_the_final_stage_wraps_to_the_first():
    assert next_stage(EVOLUTION_CYCLE[-1]) is EVOLUTION_CYCLE[0]


def test_the_stage_vocabulary_is_derived_from_the_cycle():
    """The vocabulary is a projection of the cycle, not a second list of stages."""
    vocabulary = evolution_stage_vocabulary()
    assert vocabulary.vocabulary_id == EVOLUTION_STAGE
    assert vocabulary.term_ids() == tuple(sorted(stage.value for stage in EVOLUTION_CYCLE))
    for index, stage in enumerate(EVOLUTION_CYCLE):
        term = vocabulary.require(stage.value)
        assert term.rank == index
        assert term.successors == (next_stage(stage).value,)


def test_the_stage_vocabulary_admits_an_unknown_future_stage():
    """INV-14 over the stage set: the enum refuses a stranger, the vocabulary admits one.

    This is the property the closed enumeration cannot have on its own. ``coerce`` refuses
    a sixteenth stage, so without the vocabulary the cycle would be fixed at the fifteen
    stages that were known when it was written.
    """
    with pytest.raises(EvolutionError, match="unknown evolution stage"):
        EvolutionStage.coerce("ascend")

    vocabulary = evolution_stage_vocabulary()
    widened = vocabulary.extended_with(Term("ascend", "an unknown future stage"))
    assert widened.has("ascend")
    assert not vocabulary.has("ascend"), "extension must derive a new vocabulary, not mutate"
    assert len(widened.term_ids()) == CYCLE_LENGTH + 1


def test_the_universe_publishes_the_stage_vocabulary(universe):
    """Registering it is what brings the stage set under the INV-14 probe."""
    vocabularies = universe.vocabularies()
    assert EVOLUTION_STAGE in vocabularies.vocabulary_ids()
    assert vocabularies.require(EVOLUTION_STAGE).digest() == evolution_stage_vocabulary().digest()
    assert vocabularies.is_extensible()


def test_contributing_the_stage_vocabulary_twice_reuses_the_identical_one():
    registry = build_vocabulary_registry()
    _contribute_evolution_stage_vocabulary(registry)
    _contribute_evolution_stage_vocabulary(registry)
    assert registry.require(EVOLUTION_STAGE).digest() == evolution_stage_vocabulary().digest()


def test_a_competing_stage_vocabulary_under_the_same_id_fails_closed():
    registry = build_vocabulary_registry()
    registry.register(Vocabulary(EVOLUTION_STAGE, "a competing stage set", (Term("only", "x"),)))
    with pytest.raises(LawViolation, match="different evolution stage vocabulary"):
        _contribute_evolution_stage_vocabulary(registry)


def test_the_ledger_refuses_a_start_that_is_not_the_first_stage_of_cycle_zero():
    ledger = EvolutionLedger()
    with pytest.raises(EvolutionError, match="must begin at the first stage"):
        ledger.append(
            EvolutionRecord(cycle=0, stage=EVOLUTION_CYCLE[3], subject="s", outcome="o", digest="d")
        )


def test_the_ledger_refuses_a_skipped_stage():
    ledger = EvolutionLedger()
    ledger.append(
        EvolutionRecord(cycle=0, stage=EVOLUTION_CYCLE[0], subject="s", outcome="o", digest="d")
    )
    with pytest.raises(EvolutionError, match="may not be skipped or reordered"):
        ledger.append(
            EvolutionRecord(cycle=0, stage=EVOLUTION_CYCLE[5], subject="s", outcome="o", digest="d")
        )


def test_the_ledger_refuses_a_cycle_that_advances_early():
    ledger = EvolutionLedger()
    ledger.append(
        EvolutionRecord(cycle=0, stage=EVOLUTION_CYCLE[0], subject="s", outcome="o", digest="d")
    )
    with pytest.raises(EvolutionError, match="cycle must advance"):
        ledger.append(
            EvolutionRecord(cycle=1, stage=EVOLUTION_CYCLE[1], subject="s", outcome="o", digest="d")
        )


def test_the_ledger_exposes_no_way_to_rewrite_history():
    ledger = EvolutionLedger()
    for forbidden in ("remove", "delete", "truncate", "rewrite", "update", "pop"):
        assert not hasattr(ledger, forbidden)


def test_the_universe_ledger_has_wrapped_so_non_termination_is_shown_not_asserted(universe):
    ledger = universe.evolution
    assert not ledger.is_terminated()
    assert ledger.cycles() >= 2
    assert len(ledger.records()) == CYCLE_LENGTH + 1
    assert ledger.current_stage() is EVOLUTION_CYCLE[0]
    assert ledger.completed_cycles() >= 1


def test_the_ledger_reports_stage_records_and_a_fingerprint(universe):
    ledger = universe.evolution
    assert ledger.stage_records(EVOLUTION_CYCLE[0])
    assert ledger.stage_records("observe")
    assert ledger.fingerprint() == ledger.fingerprint()
    assert ledger.expected_stage() in EVOLUTION_CYCLE
    assert ledger.to_document()["counts"]
    assert isinstance(ledger.findings(), tuple)


def test_a_record_round_trips():
    record = EvolutionRecord(
        cycle=0,
        stage=EvolutionStage.OBSERVE,
        subject="s",
        outcome="o",
        digest="d",
        findings=("f",),
    )
    assert EvolutionRecord.from_dict(record.to_dict()) == record


def test_stage_coercion_accepts_a_name_and_a_member():
    assert EvolutionStage.coerce("observe") is EvolutionStage.OBSERVE
    assert EvolutionStage.coerce(EvolutionStage.LEARN) is EvolutionStage.LEARN


# --- intelligence ---------------------------------------------------------------


def test_thirteen_modes_of_reasoning_exist_and_all_run(universe):
    intelligence = universe.intelligence()
    assert len(reasoning_kinds()) == 13
    results = intelligence.reason_all()
    assert len(results) == 13


def test_every_declared_reasoning_kind_has_a_reasoner(universe):
    intelligence = universe.intelligence()
    assert set(intelligence.reasoners()) == set(ReasoningKind)


def test_reasoning_is_deterministic(universe):
    intelligence = build_intelligence(universe.registry)
    first = intelligence.reason("dependency")
    second = intelligence.reason("dependency")
    assert first.to_dict() == second.to_dict()


@pytest.mark.parametrize("kind", sorted(reasoning_kinds()))
def test_each_reasoning_kind_returns_a_result_naming_its_kind(universe, kind):
    result = universe.intelligence().reason(kind)
    assert result.kind.value == kind
    assert isinstance(result.findings, tuple)


def test_reasoning_refuses_an_unknown_kind(universe):
    from engine.uckp.errors import UCKPValidationError

    with pytest.raises(UCKPValidationError, match="unknown reasoning kind"):
        universe.intelligence().reason("no-such-reasoning")


def test_the_intelligence_report_aggregates_every_reasoner(universe):
    report = universe.intelligence().report()
    assert len(report["results"]) == 13
    assert report["counts"]
    assert report["graph_fingerprint"]


def test_the_universe_reasons_about_itself_and_finds_no_violation(universe):
    """Article 15: knowledge reasons about itself — and this universe comes out clean."""
    for result in universe.intelligence().reason_all():
        violations = [
            finding for finding in result.findings if finding.to_dict()["severity"] == "violation"
        ]
        assert violations == [], f"{result.kind.value}: {[v.to_dict() for v in violations[:3]]}"
    assert universe.intelligence().report()["clean"] is True


def test_no_two_objects_state_the_identical_definition(universe):
    """Article 3 seen from the graph: one clause, one home."""
    redundancy = universe.intelligence().reason("redundancy")
    assert redundancy.findings == ()


def test_nothing_claims_to_be_operational_without_an_attested_validation(universe):
    consistency = universe.intelligence().reason("consistency")
    assert consistency.findings == ()


def test_wording_similarity_is_reported_as_an_observation_not_a_breach(universe):
    """A token-overlap score cannot establish a breach, and identical contracts imply it.

    Ten persistence adapters and ten execution adapters exist precisely because
    Articles 9 and 10 demand one identical contract across many technologies, so their
    descriptions necessarily overlap heavily. Grading that as a violation would make
    the constitution's own requirement generate constitutional violations.
    """
    semantic = universe.intelligence().reason("semantic")
    severities = {finding.to_dict()["severity"] for finding in semantic.findings}
    assert "violation" not in severities
    assert semantic.observations["near_duplicates"] > 0
    assert semantic.to_dict()["clean"] is True


def test_identical_meaning_under_two_identities_is_still_a_violation(minimal_registry):
    """The heuristic was downgraded; the fact was not."""
    import dataclasses as _dc

    root = minimal_registry.require(minimal_registry.require_single_root())
    twin = _dc.replace(
        root, identity=root.identity.__class__.mint("test", "TWIN"), replay=None
    ).create_from_self()
    # Bypass registry admission to construct the state the reasoner must detect.
    minimal_registry._objects[twin.ucko_id] = twin  # noqa: SLF001
    minimal_registry._by_semantics.setdefault(twin.semantic_digest(), root.ucko_id)  # noqa: SLF001
    findings = build_intelligence(minimal_registry).reason("semantic").findings
    assert any(finding.to_dict()["severity"] == "violation" for finding in findings)


# --- governance -----------------------------------------------------------------


def test_one_rule_is_derived_per_article_and_never_enumerated():
    rules = build_rules()
    assert len(rules) == len(ROOT_LAW.articles)
    assert [rule.article_id for rule in rules] == list(ROOT_LAW.article_ids())
    for rule in rules:
        assert rule.statement == ROOT_LAW.article(rule.article_id).clause


def test_rule_lookup_by_article_and_refusal_of_a_stranger():
    assert rule_for_article("UCKP-ART-01").rule_id == "UCKP-RULE-01"
    assert rule_for_article(ROOT_LAW.articles[0]).rule_id == "UCKP-RULE-01"
    with pytest.raises(GovernanceError, match="no rule derives"):
        rule_for_article("UCKP-ART-99")


def test_the_verdict_vocabulary_is_closed(universe):
    for decision in universe.governance.decisions():
        assert decision.verdict in VERDICTS


def test_every_governance_question_is_answerable(universe):
    governance = universe.governance
    assert set(governance.questions()) == {
        "is-lawful",
        "is-projection-authoritative",
        "may-create",
        "may-transition",
        "what-authority",
        "who-owns",
    }


def test_an_unknown_question_is_refused(universe):
    with pytest.raises(GovernanceError, match="no such governance question"):
        universe.governance.decide("what-colour-is-it")


def test_every_recorded_decision_replays_from_itself(universe):
    """Article 16: replayability is a property of the decision, not of the caller."""
    governance = universe.governance
    assert governance.decisions()
    assert governance.replays_identically()
    for decision in governance.decisions():
        assert governance.replay(decision)


def test_a_decision_carries_the_arguments_it_depended_on(minimal_registry):
    governance = GovernanceEngine(minimal_registry)
    root = minimal_registry.require_single_root()
    decision = governance.decide("may-transition", subject=root, target="implemented")
    assert decision.arguments == (("target", "implemented"),)
    # Replay needs nothing but the decision.
    assert governance.replay(decision)


def test_an_argument_bearing_decision_would_not_replay_without_its_inputs(minimal_registry):
    """The defect this design exists to prevent: silent verdict drift on replay."""
    governance = GovernanceEngine(minimal_registry)
    root = minimal_registry.require_single_root()
    subject = minimal_registry.require(root)
    refused = governance.decide(
        "may-create",
        subject=root,
        concept=subject.semantic_identity.concept,
        definition=subject.semantic_identity.definition,
    )
    assert refused.verdict == REFUSED
    assert governance.replay(refused)
    # Forgetting the arguments changes the answer, which is why they are recorded.
    forgotten = dataclasses.replace(
        refused, arguments=(), inputs_digest=inputs_digest_of(refused.question, refused.subject, ())
    ).sealed()
    assert not governance.replay(forgotten)


def test_a_decision_is_deterministic_and_content_addressed(universe):
    for decision in universe.governance.decisions():
        assert decision.deterministic()
        assert decision.decision_id == decision.derived_decision_id()


def test_a_decision_whose_digest_contradicts_its_arguments_is_refused():
    with pytest.raises(GovernanceError, match="do not hash to the recorded inputs digest"):
        GovernanceDecision(
            question="is-lawful",
            subject="urn:x",
            verdict=PERMITTED,
            rule_id="UCKP-RULE-06",
            article_id="UCKP-ART-06",
            rationale="r",
            inputs_digest="not-the-real-digest",
            universe_seal="s",
            arguments=(("a", "b"),),
        )


def test_a_verdict_outside_the_closed_set_is_refused():
    with pytest.raises(GovernanceError, match="not machine-verifiable"):
        GovernanceDecision(
            question="is-lawful",
            subject="urn:x",
            verdict="maybe",
            rule_id="UCKP-RULE-06",
            article_id="UCKP-ART-06",
            rationale="r",
            inputs_digest=inputs_digest_of("is-lawful", "urn:x", ()),
            universe_seal="s",
        )


def test_a_decision_explains_itself_in_a_sentence(universe):
    for decision in universe.governance.decisions():
        explanation = decision.explain()
        assert decision.verdict in explanation
        assert decision.rule_id in explanation


def test_a_decision_produces_an_audit_entry(universe):
    audit = universe.governance.audit()
    assert len(audit) == len(universe.governance.decisions())
    for entry in audit:
        assert entry.actor and entry.action and entry.subject


def test_reuse_before_create_refuses_a_second_home_for_existing_knowledge(minimal_registry):
    governance = GovernanceEngine(minimal_registry)
    root = minimal_registry.require(minimal_registry.require_single_root())
    refused = governance.decide(
        "may-create",
        subject="anything",
        concept=root.semantic_identity.concept,
        definition=root.semantic_identity.definition,
    )
    assert refused.verdict == REFUSED
    assert any("canonical home" in finding for finding in refused.findings)


def test_creating_genuinely_new_knowledge_is_permitted(minimal_registry):
    governance = GovernanceEngine(minimal_registry)
    permitted = governance.decide(
        "may-create", subject="new", concept="unheard of", definition="nothing carries this"
    )
    assert permitted.verdict == PERMITTED


def test_a_projection_is_never_authoritative_and_the_question_admits_no_exception(
    minimal_registry,
):
    governance = GovernanceEngine(minimal_registry)
    for subject in ("repository", "markdown", "some-future-technology"):
        assert governance.decide("is-projection-authoritative", subject=subject).verdict == REFUSED


def test_asking_about_a_nonexistent_subject_is_refused_not_answered(minimal_registry):
    governance = GovernanceEngine(minimal_registry)
    for question in ("who-owns", "what-authority", "is-lawful", "may-transition"):
        assert governance.decide(question, subject="urn:ucos:ucko:test:GHOST").verdict == REFUSED


def test_who_owns_and_what_authority_are_answered_for_a_real_subject(minimal_registry):
    governance = GovernanceEngine(minimal_registry)
    root = minimal_registry.require_single_root()
    assert governance.decide("who-owns", subject=root).verdict == ANSWERED
    authority = governance.decide("what-authority", subject=root)
    assert authority.verdict == ANSWERED
    assert authority.findings


def test_a_lawful_object_is_lawful_and_a_broken_one_is_not(minimal_registry):
    governance = GovernanceEngine(minimal_registry)
    root = minimal_registry.require_single_root()
    assert governance.decide("is-lawful", subject=root).verdict == PERMITTED


def test_normalise_arguments_is_ordered_and_stringly_typed():
    assert normalise_arguments({"b": 2, "a": 1}) == (("a", "1"), ("b", "2"))


def test_the_governance_document_records_rules_decisions_and_replay(universe):
    document = universe.governance.to_document()
    assert document["counts"]["rules"] == 20
    assert document["replays_identically"] is True
    assert document["audit"]


# --- deltas and proofs: decoding what a prior era wrote --------------------------


def test_a_delta_that_records_no_change_reports_itself_empty():
    assert ConstitutionalDelta("knowledge").empty is True
    assert ConstitutionalDelta("knowledge", added=("urn:a",)).empty is False


def test_a_delta_is_derived_from_two_identity_sets_without_regard_to_order():
    delta = ConstitutionalDelta.between("knowledge", ["urn:b", "urn:a"], ["urn:a", "urn:c"])
    assert delta.added == ("urn:c",)
    assert delta.removed == ("urn:b",)
    assert ConstitutionalDelta.between("knowledge", (), ()).empty


def test_a_delta_and_a_proof_decode_an_absent_record_to_their_empty_form():
    """A record from a prior era may omit a register; that is missing, not malformed."""
    assert ConstitutionalDelta.from_dict(None) == ConstitutionalDelta("")
    assert Proof.from_dict(None).verdict == "holds"
    assert Proof.from_dict(None).kind == ""


# --- states: decoding, and the refusals that keep a timeline append-only ----------


def test_a_state_record_that_is_not_a_mapping_is_refused():
    with pytest.raises(StateImmutabilityError, match="must be a mapping"):
        ConstitutionalState.from_dict("a state, allegedly")


def test_a_sealed_state_round_trips_through_its_record_and_is_verified_on_the_way_in():
    original = _genesis("d-round-trip")
    restored = ConstitutionalState.from_dict(original.to_dict())
    assert restored.state_id == original.state_id
    assert restored.verify_integrity()
    assert restored.proofs_hold()


def test_a_record_carrying_no_identity_is_sealed_on_decoding():
    """An unsealed record is completed, never trusted: the identity is re-derived."""
    record = _genesis("d-unsealed").to_dict()
    record["state_id"] = ""
    restored = ConstitutionalState.from_dict(record)
    assert restored.state_id == restored.derived_state_id()
    assert restored.verify_integrity()


def test_a_record_whose_identity_does_not_match_its_content_is_refused():
    record = _genesis("d-tampered").to_dict()
    record["knowledge_digest"] = "a different universe"
    with pytest.raises(StateImmutabilityError):
        ConstitutionalState.from_dict(record)


def test_appending_a_state_whose_identity_is_already_in_the_timeline_is_refused():
    """The last guard: parent and sequence can be made to line up, identity cannot.

    Reached with a double, because the parent/sequence checks in front of it make this
    condition unconstructible from real states — which is exactly why the guard needs a
    test rather than trust.
    """
    from engine.tests.uckp.doubles import Proxy

    genesis = _genesis("d-twice")
    timeline = ConstitutionalTimeline((genesis,))
    impostor = Proxy(
        genesis,
        parent_state_id=genesis.state_id,
        sequence=genesis.sequence + 1,
        state_id=genesis.state_id,
    )
    with pytest.raises(StateImmutabilityError, match="already in the timeline"):
        timeline.append(impostor)
    assert len(timeline) == 1


def test_the_timeline_refuses_its_own_verification_when_a_state_was_altered():
    """``verify`` needs a reachable False, or a corrupt timeline would verify."""
    from engine.tests.uckp.doubles import Proxy

    genesis = _genesis("d-altered")
    timeline = ConstitutionalTimeline((genesis,))
    tampered = ConstitutionalTimeline()
    tampered._states.append(Proxy(genesis, verify_integrity=lambda: False))
    assert timeline.verify() is True
    assert tampered.verify() is False


def test_the_timeline_refuses_a_history_that_does_not_begin_at_genesis():
    from engine.tests.uckp.doubles import Proxy

    genesis = _genesis("d-headless")
    successor = genesis.transition(
        knowledge_digest="d-headless-2",
        knowledge_delta=ConstitutionalDelta("knowledge"),
    )
    headless = ConstitutionalTimeline()
    headless._states.append(successor)
    assert headless.verify() is False

    broken_link = ConstitutionalTimeline()
    broken_link._states.extend(
        (genesis, Proxy(successor, parent_state_id="a state that never existed"))
    )
    assert broken_link.verify() is False


# --- evolution: coercion, construction, and the stage that is always defined -------


def test_an_unknown_evolution_stage_is_refused():
    with pytest.raises(EvolutionError, match="unknown evolution stage"):
        EvolutionStage.coerce("ascend")


def test_a_ledger_admits_the_records_it_is_constructed_with_and_reports_its_length():
    records = tuple(
        EvolutionRecord(cycle=0, stage=stage, subject="s", outcome="appended", digest="d")
        for stage in EVOLUTION_CYCLE[:3]
    )
    ledger = EvolutionLedger(records)
    assert len(ledger) == 3
    assert ledger.records() == records


def test_an_empty_ledger_still_names_the_stage_it_will_accept_next():
    """Article 14: the next stage is always defined, including before anything happened."""
    assert EvolutionLedger().expected_stage() is EVOLUTION_CYCLE[0]
    assert EvolutionLedger().current_stage() is None


# --- governance: the verdict surface, and an object that is not lawful -------------


def test_a_decision_says_whether_it_permitted_what_was_asked(universe):
    engine = GovernanceEngine(universe.registry)
    permitted = engine.decide("what-authority", subject=universe.root_id())
    assert permitted.permitted is (permitted.verdict == PERMITTED)
    refused = engine.decide("is-lawful", subject="urn:ucos:ucko:test:ABSENT")
    assert refused.verdict == REFUSED
    assert refused.permitted is False


def test_is_lawful_reports_a_broken_seal_and_a_broken_replay_proof(universe):
    """The lawfulness question must be able to answer "no" on a real object."""
    from engine.tests.uckp.doubles import Proxy

    intact = universe.registry.require(universe.root_id())
    broken = dataclasses.replace(intact, lifecycle="operational")  # seal not recomputed
    assert broken.verify_integrity() is False

    engine = GovernanceEngine(Proxy(universe.registry, get=lambda ucko_id: broken))
    decision = engine.decide("is-lawful", subject=broken.ucko_id)
    assert decision.verdict == REFUSED
    assert "seal does not match content" in decision.findings
    assert "replay proof does not hold" in decision.findings


# --- intelligence: the reasoners, in front of what they claim to detect -----------
#
# The registry refuses an object with a broken seal or an unanswered facet, so a
# reasoner that reports those conditions can never meet one through registration.
# ``RegistryView`` puts the reasoner in front of the condition without weakening the
# admission rules that make it unreachable in production.


def _reason(kind: str, *objects, vocabularies):
    from engine.tests.uckp.doubles import RegistryView

    view = RegistryView(objects, vocabularies=vocabularies)
    return build_intelligence(view).reason(kind)


def _statements(result) -> str:
    return "\n".join(finding.statement for finding in result.findings)


def test_coercing_a_reasoning_kind_that_is_already_one_returns_it():
    assert ReasoningKind.coerce(ReasoningKind.GAP) is ReasoningKind.GAP


def test_wording_similarity_is_zero_when_a_definition_carries_no_long_words(
    mint_object, vocabularies
):
    """The overlap score must not divide by an empty vocabulary of tokens."""
    from engine.uckp.identity import urn_for

    root = urn_for("test", "ROOT")
    left = mint_object("SHORT-LEFT", derives_from=root, concept="aa", definition="bb cc")
    right = mint_object("SHORT-RIGHT", derives_from=root, concept="dd", definition="ee ff")
    result = _reason("semantic", left, right, vocabularies=vocabularies)
    assert result.observations["near_duplicates"] == 0.0
    assert result.findings == ()


def test_dependency_reasoning_reports_a_dependency_and_an_edge_that_resolve_to_nothing(
    mint_object, vocabularies
):
    from engine.uckp.identity import urn_for

    ghost = urn_for("test", "GHOST")
    stray = mint_object(
        "DEPENDS-ON-A-GHOST",
        derives_from=urn_for("test", "DEPENDS-ON-A-GHOST"),
        dependencies=(ghost,),
    )
    result = _reason("dependency", stray, vocabularies=vocabularies)
    statements = _statements(result)
    assert f"depends on {ghost}, which does not exist" in statements
    assert "cannot be executed" in statements
    assert all(finding.severity == "violation" for finding in result.findings)


def test_constitutional_reasoning_reports_a_category_the_law_does_not_govern(
    mint_object, vocabularies
):
    """ "document" is declared non-authoritative, so it is not a home for authority."""
    from engine.uckp.identity import urn_for

    misfiled = mint_object(
        "A-DOCUMENT", derives_from=urn_for("test", "A-DOCUMENT"), category="document"
    )
    result = _reason("constitutional", misfiled, vocabularies=vocabularies)
    statements = _statements(result)
    assert "is not a governed category" in statements
    assert "may only ever be a projection" in statements


def test_authority_reasoning_reports_two_roots_and_a_parent_that_does_not_exist(
    mint_object, vocabularies
):
    from engine.uckp.identity import urn_for

    first = mint_object("ROOT-ONE", derives_from=urn_for("test", "ROOT-ONE"))
    second = mint_object("ROOT-TWO", derives_from=urn_for("test", "ROOT-TWO"))
    orphan = mint_object("CHILD-OF-NOBODY", derives_from=urn_for("test", "GHOST-PARENT"))
    result = _reason("authority", first, second, orphan, vocabularies=vocabularies)
    statements = _statements(result)
    assert "declares 3 constitutional roots, not one" not in statements
    assert "declares 2 constitutional roots, not one" in statements
    assert "derives authority from" in statements
    assert result.observations["roots"] == 2.0


def test_authority_reasoning_reports_a_child_that_outranks_its_own_parent(
    mint_object, vocabularies
):
    """Authority flows downward; a constitutional child of an advisory parent inverts it."""
    from engine.uckp.identity import urn_for

    parent_urn = urn_for("test", "ADVISORY-PARENT")
    parent = mint_object("ADVISORY-PARENT", derives_from=parent_urn, authority_tier="advisory")
    child = mint_object(
        "CONSTITUTIONAL-CHILD", derives_from=parent_urn, authority_tier="constitutional"
    )
    result = _reason("authority", parent, child, vocabularies=vocabularies)
    assert "outranks the authority it derives from" in _statements(result)


def test_authority_reasoning_reports_a_cycle(mint_object, vocabularies):
    from engine.uckp.identity import urn_for

    left = mint_object("LEFT", derives_from=urn_for("test", "RIGHT"))
    right = mint_object("RIGHT", derives_from=urn_for("test", "LEFT"))
    result = _reason("authority", left, right, vocabularies=vocabularies)
    assert "authority cycle" in _statements(result)


def test_governance_reasoning_reports_an_object_naming_no_governance_authority(
    mint_object, vocabularies
):
    from engine.tests.uckp.doubles import Proxy
    from engine.uckp.identity import urn_for

    obj = mint_object("UNGOVERNED", derives_from=urn_for("test", "UNGOVERNED"))
    ungoverned = dataclasses.replace(
        obj, governance_context=Proxy(obj.governance_context, value="")
    )
    result = _reason("governance", ungoverned, vocabularies=vocabularies)
    assert "names no governance authority" in _statements(result)
    assert result.observations["ungoverned"] == 1.0


def test_evolution_reasoning_reports_an_object_with_no_temporal_history(mint_object, vocabularies):
    from engine.uckp.identity import urn_for

    obj = mint_object("TIMELESS", derives_from=urn_for("test", "TIMELESS"))
    result = _reason(
        "evolution", dataclasses.replace(obj, temporal_history=()), vocabularies=vocabularies
    )
    assert "records no temporal history" in _statements(result)
    assert result.observations["without_temporal_history"] == 1.0


def test_consistency_reasoning_reports_an_operational_object_that_was_never_validated(
    mint_object, vocabularies
):
    from engine.uckp.identity import urn_for

    live = mint_object(
        "IN-SERVICE", derives_from=urn_for("test", "IN-SERVICE"), lifecycle="operational"
    )
    result = _reason("consistency", live, vocabularies=vocabularies)
    assert "is operational but was never validated" in _statements(result)


def test_consistency_reasoning_reports_a_broken_seal_and_a_broken_replay_proof(
    mint_object, vocabularies
):
    from engine.uckp.identity import urn_for

    obj = mint_object("TAMPERED", derives_from=urn_for("test", "TAMPERED"))
    tampered = dataclasses.replace(obj, lifecycle="draft")  # seal and proof not recomputed
    result = _reason("consistency", tampered, vocabularies=vocabularies)
    statements = _statements(result)
    assert "seal does not match content" in statements
    assert "replay proof does not hold" in statements


def test_gap_reasoning_reports_an_unanswered_facet(mint_object, vocabularies):
    from engine.uckp.identity import urn_for

    obj = mint_object("SILENT", derives_from=urn_for("test", "SILENT"))
    result = _reason("gap", dataclasses.replace(obj, replay=None), vocabularies=vocabularies)
    assert "facet replay is absent" in _statements(result)


def test_redundancy_reasoning_reports_one_definition_stated_twice(mint_object, vocabularies):
    """Whitespace and case are not meaning, so restating a clause is still restating it."""
    from engine.uckp.identity import urn_for

    root = urn_for("test", "ROOT")
    left = mint_object("FIRST-COPY", derives_from=root, definition="The identical clause")
    right = mint_object("SECOND-COPY", derives_from=root, definition="the  identical   clause")
    assert left.semantic_digest() != right.semantic_digest()
    result = _reason("redundancy", left, right, vocabularies=vocabularies)
    assert "the identical definition is stated by" in _statements(result)
    assert result.observations["repeated_definitions"] == 1.0


def test_optimization_reasoning_reports_an_object_that_points_at_nothing(minimal_root, universe):
    """An ownership edge names a person, so it is not participation in the graph."""
    from engine.tests.uckp.doubles import RegistryView

    view = RegistryView((minimal_root,), vocabularies=universe.vocabularies())
    result = build_intelligence(view).reason("optimization")
    assert result.observations["isolated_objects"] == 1.0
    assert "participates in nothing" in _statements(result)
    assert all(finding.severity == "observation" for finding in result.findings)


def test_future_reasoning_reports_a_declared_future_binding(mint_object, vocabularies):
    from engine.uckp.identity import urn_for
    from engine.uckp.values import Relationship

    root = urn_for("test", "FORWARD-LOOKING")
    forward = mint_object(
        "FORWARD-LOOKING",
        derives_from=root,
        relationships=(Relationship("references", urn_for("test", "NOT-YET"), "future"),),
    )
    result = _reason("future", forward, vocabularies=vocabularies)
    assert "declares an intended future binding" in _statements(result)
    assert result.observations["future_bindings"] == 1.0


def test_future_reasoning_reports_a_vocabulary_that_refuses_the_future(minimal_root):
    from engine.tests.uckp.doubles import RegistryView
    from engine.uckp.vocabulary import VocabularyRegistry

    class Swallowing(Vocabulary):
        def extended_with(self, term: Term) -> Vocabulary:
            return self

    closed = VocabularyRegistry((Swallowing("test.closed", "closed in practice"),))
    result = build_intelligence(RegistryView((minimal_root,), vocabularies=closed)).reason("future")
    assert "refuses an unknown future member" in _statements(result)
    assert result.observations["vocabularies_extensible"] == 0.0
    assert result.clean is False


def test_the_lineage_of_a_state_the_timeline_does_not_hold_is_empty():
    timeline = ConstitutionalTimeline((_genesis("d-lineage"),))
    assert timeline.lineage("a state that was never appended") == ()
    assert len(timeline.lineage(timeline.head().state_id)) == 1
