"""Tests for engine.knowledge.integration.pipeline — the constitutional execution path."""

from __future__ import annotations

import pytest

from engine.knowledge.integration import composition as composition_module
from engine.knowledge.integration import pipeline as pipeline_module
from engine.knowledge.integration.composition import CompositionResult
from engine.knowledge.integration.contracts import Disposition, Operation, SequenceStage
from engine.knowledge.integration.errors import IntegrationError
from engine.knowledge.integration.pipeline import ConstitutionalPipeline, Outcome, StageStatus
from engine.knowledge.model import KnowledgeAuthority, KnowledgeKind, Lifecycle
from engine.knowledge.store import KnowledgeBase
from engine.knowledge.validation import KnowledgeValidationReport, Verdict

from .conftest import make_cko, make_intent


def test_create_novel(empty_base):
    decision = ConstitutionalPipeline(empty_base).execute(make_intent("N-1"))
    assert decision.outcome is Outcome.CREATED
    assert decision.accepted
    assert decision.artifact["cko_id"] == "N-1"
    # every sequence stage is recorded
    recorded = {s.stage for s in decision.stages}
    assert recorded == set(SequenceStage)
    assert decision.stage(SequenceStage.CREATE).status is StageStatus.DONE
    assert decision.to_dict()["outcome"] == "created"


def test_modify_existing_evolves_in_place():
    base = KnowledgeBase([make_cko("M", owner="TEAM-A")])
    intent = make_intent(
        "M", owner="TEAM-A", operation=Operation.MODIFY, statement="revised distinct wording now"
    )
    decision = ConstitutionalPipeline(base).execute(intent)
    assert decision.outcome is Outcome.MODIFIED
    assert decision.accepted
    assert decision.stage(SequenceStage.CREATE).status is StageStatus.SKIPPED
    assert any("evolves the existing" in r for r in decision.reasons)


def test_modify_missing_blocked():
    decision = ConstitutionalPipeline(KnowledgeBase([])).execute(
        make_intent("MISSING", operation=Operation.MODIFY)
    )
    assert decision.outcome is Outcome.BLOCKED
    assert not decision.accepted


def test_create_duplicate_identity_blocked(base):
    decision = ConstitutionalPipeline(base).execute(make_intent("COMP-A"))
    assert decision.outcome is Outcome.BLOCKED


def test_reuse_pure_semantic_twin():
    base = KnowledgeBase([make_cko("TW", statement="reusable substance", owner="TEAM-A")])
    intent = make_intent("NEW", statement="reusable substance", owner="TEAM-A")
    decision = ConstitutionalPipeline(base).execute(intent)
    assert decision.outcome is Outcome.REUSED
    assert decision.artifact["cko_id"] == "TW"


def test_foreign_owner_twin_blocked():
    base = KnowledgeBase([make_cko("TW", statement="reusable substance", owner="OTHER")])
    intent = make_intent("NEW", statement="reusable substance", owner="TEAM-A")
    decision = ConstitutionalPipeline(base).execute(intent)
    assert decision.outcome is Outcome.BLOCKED
    assert "overlapping-ownership" in decision.reasons


def test_extend(base):
    intent = make_intent(
        "NEW", title="alpha component v2", statement="alpha component substance improved"
    )
    decision = ConstitutionalPipeline(base).execute(intent)
    assert decision.outcome is Outcome.EXTENDED
    assert decision.stage(SequenceStage.EXTEND).status is StageStatus.DONE


def test_compose(base):
    intent = make_intent(
        "NEW",
        title="Zeta",
        statement="orchestrating flows via bindings",
        dependencies=("COMP-A", "COMP-B"),
    )
    decision = ConstitutionalPipeline(base).execute(intent)
    assert decision.outcome is Outcome.COMPOSED
    assert decision.stage(SequenceStage.COMPOSE).status is StageStatus.DONE


def test_governance_kind_grounds_in_evolve():
    principle = make_cko(
        "P",
        universe="GOV",
        kind=KnowledgeKind.PRINCIPLE,
        authority=KnowledgeAuthority.CONSTITUTIONAL,
        lifecycle=Lifecycle.RATIFIED,
    )
    intent = make_intent(
        "POL-1",
        universe="GOV",
        kind=KnowledgeKind.POLICY,
        statement="a distinct governance policy body",
        dependencies=("P",),
        knowledge_links=("P",),
    )
    decision = ConstitutionalPipeline(KnowledgeBase([principle])).execute(intent)
    assert decision.accepted
    evolve = decision.stage(SequenceStage.EVOLVE)
    assert "governance" in evolve.detail
    assert evolve.detail["governance"]["grounded"] is True


def test_require_raises_on_block_and_returns_on_accept(empty_base):
    pipe = ConstitutionalPipeline(empty_base)
    assert pipe.require(make_intent("OK-1")).accepted
    with pytest.raises(IntegrationError):
        pipe.require(make_intent("MISSING", operation=Operation.MODIFY))


def test_asking_for_a_stage_the_decision_never_reached_answers_none(empty_base):
    """``stage()`` is how a caller reads one step's outcome, and a BLOCKED decision stops
    part-way — so the honest answer for a stage that never ran is ``None``, not a fabricated
    record. Every accepted decision records all eight stages, which is why the falling-off-
    the-end arm had never run."""
    blocked = ConstitutionalPipeline(empty_base).execute(
        make_intent("MISSING", operation=Operation.MODIFY)
    )
    assert not blocked.accepted
    recorded = {s.stage for s in blocked.stages}
    missing = next(stage for stage in SequenceStage if stage not in recorded)
    assert blocked.stage(missing) is None
    assert blocked.stage(next(iter(recorded))) is not None


def test_the_pipeline_exposes_the_base_it_decided_against(empty_base):
    """The base is what every stage's verdict was computed over, so a caller reading a
    decision needs the same one to reproduce it. Reaching for the store instead would let a
    later save be mistaken for the state the decision was made against."""
    pipeline = ConstitutionalPipeline(empty_base)
    assert pipeline.base is empty_base


def test_a_composition_that_fails_validation_blocks_and_records_where(base):
    """VALIDATE IS FAIL-CLOSED, and its refusal arm was unexecuted because every fixture
    composes into a base that validates.

    A composition that produces knowledge the validator rejects must stop at VALIDATE and
    say so — returning the artifact anyway would hand the caller an object the canonical
    layer has already refused, and the stage record is what tells them which gate said no.
    """

    refusing = KnowledgeValidationReport(verdict=Verdict.NOT_VALID)
    original = pipeline_module.validate_base
    try:
        pipeline_module.validate_base = lambda _base: refusing
        decision = ConstitutionalPipeline(base).execute(
            make_intent(
                "NEW",
                title="Zeta",
                statement="orchestrating flows via bindings",
                dependencies=("COMP-A", "COMP-B"),
            )
        )
    finally:
        pipeline_module.validate_base = original

    assert decision.outcome is Outcome.BLOCKED
    assert not decision.accepted
    assert decision.stage(SequenceStage.VALIDATE).status is StageStatus.BLOCKED


def test_a_composition_that_proves_insufficient_at_materialisation_falls_back_to_create(base):
    """The disposition and the composition are TWO decisions, taken at two moments.

    The reuse engine decides COMPOSE from lexical evidence; the composer then tries to
    actually build the object and can find the components insufficient. Trusting the earlier
    decision would mean returning ``None`` as the artifact — or raising, in a pipeline whose
    whole contract is that it produces a decision rather than an exception. Falling back to
    CREATE is the answer the evidence supports: nothing was composed, so something is being
    authored, and the stage record says COMPOSE was not what happened.
    """

    intent = make_intent(
        "NEW",
        title="Zeta",
        statement="orchestrating flows via bindings",
        dependencies=("COMP-A", "COMP-B"),
    )
    composed = ConstitutionalPipeline(base).execute(intent)
    assert composed.outcome is Outcome.COMPOSED, "the fixture no longer reaches COMPOSE"

    original = composition_module.AutonomousComposer.compose

    def insufficient(self, proposed):
        return CompositionResult(
            intent_id=proposed.intent_id,
            sufficient=False,
            disposition=Disposition.COMPOSE,
            components=(),
            reasons=("the components could not be materialised",),
        )

    try:
        composition_module.AutonomousComposer.compose = insufficient
        decision = ConstitutionalPipeline(base).execute(intent)
    finally:
        composition_module.AutonomousComposer.compose = original

    assert decision.outcome is Outcome.CREATED
    assert decision.accepted
    assert decision.artifact["cko_id"] == "NEW"
    assert decision.stage(SequenceStage.COMPOSE).status is StageStatus.SKIPPED
