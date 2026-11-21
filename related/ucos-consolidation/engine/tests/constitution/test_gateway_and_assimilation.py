"""UCOS-CMG/RTAG — every stage of the mutation pipeline is driven into its refusal.

The pipeline's value is entirely in what it stops, so a test suite that only shows a
lawful mutation applying would prove nothing. Each of the seven stages is failed here in
isolation, and the refusal is asserted to name *that* stage — a mutation refused at
``proposal`` when it should have been refused at ``registration`` would mean the pipeline
is not actually checking what it claims to.
"""

from __future__ import annotations

import pytest

from engine.constitution import assimilation, catalog, gateway, metadata, state
from engine.constitution import assimilation as assimilation_gate
from engine.constitution import replay as replay_engine
from engine.constitution.errors import ConstitutionalError, DuplicateTruth, MutationRefused
from engine.constitution.metadata import Population
from engine.tests.constitution.conftest import declare, population


def _mutation(*records: metadata.ConstitutionalMetadata, **kwargs: str) -> gateway.Mutation:
    return gateway.Mutation(
        records=records,
        authority=kwargs.get("authority", "ext:UCOS-AUTHORITY-TEST"),
        reason=kwargs.get("reason", "test"),
    )


# --------------------------------------------------------------------------- assimilation


def test_creation_is_permitted_only_where_nothing_canonical_exists(lawful: Population) -> None:
    verdict = assimilation.require_creatable(
        assimilation.Proposal(subject="fresh", owner="ext:o", outputs=("fresh-thing",)), lawful
    )
    assert verdict.creatable
    assert verdict.status == "CREATE"
    assert set(verdict.gap()) == {s.name for s in assimilation.SEARCHES}


@pytest.mark.parametrize(
    ("proposal", "search"),
    [
        (assimilation.Proposal(subject="root"), "artifact"),
        (assimilation.Proposal(subject="new", outputs=("root-output",)), "capability"),
    ],
)
def test_each_canonical_search_refuses_creation(
    lawful: Population, proposal: assimilation.Proposal, search: str
) -> None:
    verdict = assimilation.assimilate(proposal, lawful)
    assert not verdict.creatable
    assert search in {i.search for i in verdict.incumbents}
    assert "root" in verdict.reuse_targets
    with pytest.raises(DuplicateTruth) as excinfo:
        assimilation.require_creatable(proposal, lawful)
    assert excinfo.value.detail["clause"] == "CEL-08"


def test_the_owner_search_refuses_duplication_but_not_growth() -> None:
    """A nucleus owning many capabilities is expected; owning one twice is not."""
    pop = population(declare("held", canonical_owner=("ext:owner",), outputs=("thing",)))
    growth = assimilation.Proposal(subject="new", owner="ext:owner", outputs=("other-thing",))
    duplicate = assimilation.Proposal(subject="new", owner="ext:owner", outputs=("thing",))
    assert assimilation.assimilate(growth, pop).creatable
    assert not assimilation.assimilate(duplicate, pop).creatable


def test_duplicate_capabilities_are_measurable_across_a_population() -> None:
    pop = population(
        declare("a", outputs=("shared",)),
        declare("b", outputs=("shared",)),
    )
    assert assimilation.duplicate_capabilities(pop) == {"shared": ("a", "b")}


def test_a_proposal_can_be_read_out_of_a_declaration() -> None:
    record = declare("x", outputs=("out",), inputs=("in",))
    proposal = assimilation.proposal_for(record)
    assert proposal.subject == "x"
    assert proposal.outputs == ("out",)


# --------------------------------------------------------------------------- gateway


def test_the_pipeline_order_is_derived_from_the_declared_chain() -> None:
    assert gateway.pipeline_order() == (
        "proposal",
        "evidence",
        "validation",
        "verification",
        "certification",
        "registration",
        "truth_update",
    )


def test_a_lawful_mutation_applies_and_yields_a_committed_seal(lawful: Population) -> None:
    grown, record = gateway.apply(lawful, _mutation(declare("newcomer", dependencies=("root",))))
    assert record.applied
    assert record.status == "APPLIED"
    assert record.chain_is_intact()
    assert len(record.outcomes) == len(gateway.PIPELINE)
    assert record.seal is not None and record.seal.committed
    assert record.replay is not None and record.replay.fixed_point
    assert "newcomer" in grown
    assert "newcomer" not in lawful  # the base population is untouched


def test_an_amendment_supersedes_rather_than_duplicating(lawful: Population) -> None:
    """The artifact search must not make correcting a subject impossible."""
    amended = declare("leaf", dependencies=("root",), constraints=("amended",))
    grown, record = gateway.apply(lawful, _mutation(amended))
    assert record.applied
    assert grown.get("leaf").entries("constraints") == ("amended",)
    assert len(grown) == len(lawful)


def _unmintable() -> metadata.ConstitutionalMetadata:
    """A record that is completely declared but carries an identifier nobody could mint."""
    good = declare("registered")
    return metadata.ConstitutionalMetadata(
        subject="registered", universal_id="not-an-id", facets=good.facets
    )


@pytest.mark.parametrize(
    ("record_factory", "stage"),
    [
        (lambda: metadata.ConstitutionalMetadata.declare("bare", universal_id=""), "proposal"),
        (lambda: declare("dup", outputs=("root-output",)), "evidence"),
        (lambda: declare("dangling", dependencies=("ghost",)), "validation"),
        (lambda: declare("selfie", certifications=("selfie",)), "validation"),
        (_unmintable, "verification"),
    ],
)
def test_each_stage_refuses_what_it_owns(lawful: Population, record_factory, stage: str) -> None:
    record = gateway.propose(lawful, _mutation(record_factory()))
    assert not record.applied
    assert record.refused_at == stage
    with pytest.raises(MutationRefused) as excinfo:
        gateway.apply(lawful, _mutation(record_factory()))
    assert excinfo.value.detail["refused_at"] == stage
    assert excinfo.value.detail["clause"] == "CEL-04"


def test_the_pipeline_stops_at_the_first_refusal(lawful: Population) -> None:
    """A stage after a failed one would be judging a state that will never exist."""
    record = gateway.propose(lawful, _mutation(declare("dangling", dependencies=("ghost",))))
    assert [o.name for o in record.outcomes] == ["proposal", "evidence", "validation"]
    assert record.chain_is_intact()


def test_the_registration_stage_is_a_second_defence(lawful: Population) -> None:
    """Reachable only directly — and that is the point.

    ``verification`` proves identity as one of its nine obligations, so a malformed
    identifier never survives to ``registration`` through the pipeline. That does not make
    the stage redundant: it is the same second-defence discipline as
    :mod:`engine.nucleus.ownership`, which measures a population that arrived by some path
    the constructor never saw. A stage whose refusal branch has never executed is a stage
    nobody has checked, so it is forced here.
    """
    stage = next(s for s in gateway.PIPELINE if s.name == "registration")
    base = lawful

    unmintable = _unmintable()
    satisfied, detail = stage.run(
        gateway.Context(
            base=base,
            candidate=base.with_records([unmintable]),
            mutation=_mutation(unmintable),
        )
    )
    assert not satisfied
    assert "identity authority could mint" in detail

    unregistered = declare("unregistered")
    stripped = metadata.ConstitutionalMetadata(
        subject="unregistered",
        universal_id=unregistered.universal_id,
        facets={**dict(unregistered.facets), "registrations": ()},
    )
    satisfied, detail = stage.run(
        gateway.Context(
            base=base,
            candidate=base.with_records([stripped]),
            mutation=_mutation(stripped),
        )
    )
    assert not satisfied
    assert "names no registry" in detail


def test_a_mutation_with_no_authority_is_refused(lawful: Population) -> None:
    record = gateway.propose(lawful, gateway.Mutation(records=(declare("x"),), authority=""))
    assert record.refused_at == "proposal"
    assert "authority" in record.outcomes[0].detail


def test_an_empty_mutation_is_refused(lawful: Population) -> None:
    record = gateway.propose(lawful, gateway.Mutation(records=(), authority="ext:a"))
    assert record.refused_at == "proposal"


def test_a_refused_mutation_leaves_repository_truth_untouched(lawful: Population) -> None:
    before = lawful.digest()
    record = gateway.propose(lawful, _mutation(declare("selfie", certifications=("selfie",))))
    assert not record.applied
    assert record.population.digest() == before
    assert record.population is lawful


def test_the_journal_is_tamper_evident(lawful: Population) -> None:
    record = gateway.propose(lawful, _mutation(declare("newcomer")))
    assert record.chain_is_intact()
    forged = gateway.MutationRecord(
        gateway_id=record.gateway_id,
        mutation=record.mutation,
        outcomes=(
            gateway.StageOutcome(
                name=record.outcomes[0].name,
                satisfied=record.outcomes[0].satisfied,
                statement=record.outcomes[0].statement,
                detail="edited after the fact",
                prev_hash=record.outcomes[0].prev_hash,
                entry_hash=record.outcomes[0].entry_hash,
            ),
        ),
        order=record.order,
        applied=record.applied,
        population=record.population,
    )
    assert not forged.chain_is_intact()


def test_the_gateway_is_the_only_producer_of_a_clean_seal_over_a_new_state() -> None:
    """A hand-assembled population has no seal, so it can do none of the guarded acts."""

    base = catalog.build_population()
    smuggled = base.with_records([declare("smuggled")])
    seal = state.commit(base)
    with pytest.raises(Exception) as excinfo:
        state.guard(seal, smuggled, act="register")
    assert "moved since it was sealed" in str(excinfo.value)


# ---------------------------------------------------------------------------------------
# The later stages as second defences, driven directly
#
# The same discipline `test_the_registration_stage_is_a_second_defence` already states, and
# for the same reason: `verification` proves nine obligations and `validation` proves the
# graph, so a state that would fail `evidence`'s duplicate check, `verification`'s authority
# report, `certification`'s planner or `truth_update`'s convergence is refused earlier and
# never reaches them through the pipeline. That does not make those branches redundant — it
# makes them the branches nobody has checked, which is exactly what this suite refuses to
# allow for the stages before them.
# ---------------------------------------------------------------------------------------


def _stage(name: str) -> gateway.Stage:
    return next(s for s in gateway.PIPELINE if s.name == name)


def _context(base: Population, *records: metadata.ConstitutionalMetadata) -> gateway.Context:
    return gateway.Context(
        base=base,
        candidate=base.with_records(records),
        mutation=_mutation(*records),
    )


def test_the_evidence_stage_measures_duplicate_capability_across_the_whole_state(
    lawful: Population,
) -> None:
    """TWO SUBJECTS, ONE OUTPUT, and neither of them new.

    The creation search catches a NEW subject duplicating existing truth; this check is the
    other half — the resulting STATE holding two producers of one capability, which can
    arise from amending two existing subjects into collision without creating anything. The
    refusal names the output and every subject producing it, because a reader cannot resolve
    a duplication they cannot locate.
    """
    collide_a = declare("root", outputs=("shared-output",))
    collide_b = declare("middle", dependencies=("root",), outputs=("shared-output",))
    satisfied, detail = _stage("evidence").run(_context(lawful, collide_a, collide_b))

    assert not satisfied
    assert "duplicate capabilities" in detail
    assert "shared-output" in detail
    assert "root" in detail and "middle" in detail


def test_the_verification_stage_reports_an_authority_breach_before_it_proves_legality(
    lawful: Population,
) -> None:
    """A self-attesting subject is an authority breach, and the report is consulted FIRST.

    Proving each record's legality one at a time would report the breach as that record's
    private failure; the authority graph measures the whole state, so a circular attestation
    between two subjects is named as what it is. Ordering the report first is what makes the
    detail say "authority breaches" rather than "unproven".
    """
    circular_a = declare("root", certifications=("middle",))
    circular_b = declare("middle", dependencies=("root",), certifications=("root",))
    satisfied, detail = _stage("verification").run(_context(lawful, circular_a, circular_b))

    assert not satisfied
    assert detail.startswith("authority breaches:")


def test_the_certification_stage_certifies_the_state_and_not_the_diff(
    lawful: Population,
) -> None:
    """CERTIFYING ONLY THE MUTATED SUBJECTS WOULD CERTIFY A CHANGE THAT BREAKS SOMETHING IT
    NEVER MENTIONED, which is why the unit of certification is the resulting state.

    The refusal is reached by amending one subject into a shape the planner cannot place,
    and the message carries the planner's own refusals rather than a summary of them.
    """
    unplaceable = declare("root", dependencies=("middle",))
    satisfied, detail = _stage("certification").run(_context(lawful, unplaceable))

    assert not satisfied
    assert detail.startswith("the resulting state is not executable:")


def test_the_truth_update_stage_refuses_a_state_that_does_not_settle(
    lawful: Population, monkeypatch: pytest.MonkeyPatch
) -> None:
    """CEL-06 is a claim about a FIXED POINT, so the stage's refusal is what makes it one.

    Convergence is a property of the whole replay model, and this repository's declarations
    settle — which is the correct outcome and also why this branch never ran. The replay
    record is therefore supplied directly: what is under test is that the stage reads
    ``fixed_point``, refuses when it is false, and names the divergent acts a reader would
    otherwise have to re-derive.
    """

    class _Divergent:
        fixed_point = False
        converged_at = None

        @staticmethod
        def divergent_acts() -> tuple[str, ...]:
            return ("attestation", "registration")

    monkeypatch.setattr(replay_engine, "converge", lambda _population: _Divergent())
    satisfied, detail = _stage("truth_update").run(_context(lawful, declare("settled")))

    assert not satisfied
    assert "did not settle" in detail
    assert "attestation" in detail and "registration" in detail


def test_a_stage_that_cannot_be_evaluated_is_a_failed_stage_and_not_a_crash(
    lawful: Population, monkeypatch: pytest.MonkeyPatch
) -> None:
    """AN EXCEPTION OUT OF A STAGE IS STILL A VERDICT.

    Letting it escape would abandon the run with the mutation seal still open and no record
    of which stage was being evaluated — the state engine would be left dirty by the very
    mechanism that exists to keep it clean. The exception's text is carried into the detail
    so the failure is diagnosable from the record rather than from a traceback nobody kept.
    """

    def explode(*_args, **_kwargs):
        raise RuntimeError("the search index is unavailable")

    monkeypatch.setattr(assimilation_gate, "duplicate_capabilities", explode)
    record = gateway.propose(lawful, _mutation(declare("fresh")))

    assert not record.applied
    assert record.refused_at == "evidence"
    failed = next(o for o in record.outcomes if o.name == "evidence")
    assert "stage could not be evaluated" in failed.detail
    assert "the search index is unavailable" in failed.detail
    assert record.chain_is_intact(), "the journal must still be readable after a fault"


def test_a_record_hashes_its_own_content_so_the_journal_can_be_compared(
    lawful: Population,
) -> None:
    """The record's digest is what an external gate compares against a sealed expectation.
    Two proposals of one mutation over one state must hash alike, or every such comparison
    is a coin toss; two different mutations must not, or the comparison proves nothing."""
    first = gateway.propose(lawful, _mutation(declare("fresh")))
    second = gateway.propose(lawful, _mutation(declare("fresh")))
    other = gateway.propose(lawful, _mutation(declare("different")))

    assert first.digest() == second.digest()
    assert len(first.digest()) == 64
    assert first.digest() != other.digest()


def test_a_mutation_separates_what_it_creates_from_what_it_amends(lawful: Population) -> None:
    """The two halves are asked separately because they are governed separately: a creation
    faces the assimilation searches and an amendment faces supersession. A mutation that
    could not tell them apart would put an amendment through the duplicate-truth gate and
    refuse every correction as a duplicate of the thing it corrects."""
    fresh = declare("fresh")
    amended = declare("root", constraints=("deterministic", "idempotent"))
    mutation = _mutation(fresh, amended)

    assert [r.subject for r in mutation.creates(lawful)] == ["fresh"]
    assert [r.subject for r in mutation.amends(lawful)] == ["root"]
    assert len(mutation.creates(lawful)) + len(mutation.amends(lawful)) == len(mutation.records)


def test_a_pipeline_declaring_a_cycle_has_no_order_and_says_so() -> None:
    """The gateway derives its own run order through the same authority every other consumer
    uses, so it is subject to CEL-02 rather than being the one place a sequence is hardcoded.
    The cost of that is a pipeline that could declare a cycle, and the refusal is what keeps
    a cyclic declaration from silently yielding a partial order that runs some stages."""

    cyclic = (
        gateway.Stage(name="a", statement="a", depends_on=("b",), run=lambda _c: (True, "")),
        gateway.Stage(name="b", statement="b", depends_on=("a",), run=lambda _c: (True, "")),
    )
    with pytest.raises(ConstitutionalError) as excinfo:
        gateway.pipeline_order(cyclic)
    assert "declares a cycle" in str(excinfo.value)
    assert set(excinfo.value.detail["unresolved"]) == {"a", "b"}


def test_every_search_looks_past_the_proposal_s_own_incumbent_declaration() -> None:
    """AMENDING A SUBJECT MUST NOT READ AS DUPLICATING IT.

    A proposal for a subject the population already declares is a supersession, and the
    incumbent it would replace matches every search perfectly — same outputs, same owner,
    same inputs. Exactly ONE search is supposed to notice: ``artifact``, whose whole job is
    to say that a subject with this key already exists. ``capability``, ``owner`` and
    ``knowledge`` skip it, and without that skip the same fact would be reported four times
    over — the gateway would read three duplications that do not exist, and every reader of
    the verdict would be told to extend three subjects that are all the one being amended.
    """
    incumbent = declare(
        "held",
        canonical_owner=("ext:owner",),
        outputs=("thing",),
        inputs=("material",),
    )
    pop = population(incumbent)

    amendment = assimilation.proposal_for(incumbent)
    verdict = assimilation.assimilate(amendment, pop)
    assert {i.search for i in verdict.incumbents} == {"artifact"}
    assert [i.subject for i in verdict.incumbents] == ["held"]

    # And the searches still see a DIFFERENT subject occupying the same ground.
    rival = assimilation.Proposal(
        subject="rival", owner="ext:owner", outputs=("thing",), inputs=("material",)
    )
    kinds = {i.search for i in assimilation.assimilate(rival, pop).incumbents}
    assert {"capability", "owner", "knowledge"} <= kinds


def test_the_knowledge_search_ignores_a_subject_owned_by_somebody_else() -> None:
    """Two owners assimilating the same input is not duplication — it is two subsystems
    reading the same material, which is ordinary. The search narrows to one owner's ground
    on purpose, and the skip is what keeps it from reporting every reader of a shared input.
    """
    theirs = declare(
        "theirs",
        canonical_owner=("ext:other-owner",),
        outputs=("thing",),
        inputs=("material",),
    )
    pop = population(theirs)
    mine = assimilation.Proposal(
        subject="mine", owner="ext:owner", outputs=("thing",), inputs=("material",)
    )
    kinds = {i.search for i in assimilation.assimilate(mine, pop).incumbents}

    assert "capability" in kinds, "a shared output is still one canonical owner's"
    assert "owner" not in kinds
    assert "knowledge" not in kinds
