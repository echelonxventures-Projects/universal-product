"""UCOS-CEP/DPE/ARE — order is derived, dirty state is unmeasurable, replay settles.

The planner tests are mostly about what the planner *refuses to accept*: there is no
argument through which an order can arrive, and a plan over an illegal population is not
executable however well-formed its graph. The state tests force each of the two ways a
seal can be invalid. The replay tests force divergence, which is the branch a correct
system never takes and therefore the one most likely to be wrong.
"""

from __future__ import annotations

import dataclasses

import pytest

from engine.constitution import planner, replay, state
from engine.constitution.errors import (
    DirtyStateViolation,
    IllegalExecution,
    ManualSequencing,
    ReplayDivergence,
)
from engine.constitution.metadata import Population
from engine.tests.constitution.conftest import declare, population

# --------------------------------------------------------------------------- planner


def test_the_order_is_derived_and_respects_dependencies(lawful: Population) -> None:
    derived = planner.require_executable(lawful)
    assert derived.executable
    assert derived.order.index("root") < derived.order.index("middle")
    assert derived.order.index("middle") < derived.order.index("leaf")
    assert derived.position("root") == 0


@pytest.mark.parametrize(
    "forbidden",
    [{"order": ["a"]}, {"sequence": ["a"]}, {"first": "a"}, {"priority": 1}, {"after": "b"}],
)
def test_no_argument_admits_a_caller_supplied_order(
    lawful: Population, forbidden: dict[str, object]
) -> None:
    """CEL-02 is enforced by there being no parameter, not by asking callers not to."""
    with pytest.raises(ManualSequencing) as excinfo:
        planner.plan(lawful, **forbidden)
    assert excinfo.value.detail["supplied"] == sorted(forbidden)
    assert excinfo.value.detail["clause"] == "CEL-02"


def test_all_six_closures_are_calculated(lawful: Population) -> None:
    derived = planner.plan(lawful)
    closures = derived.closures("leaf")
    assert set(closures) == set(planner.CLOSURES)
    assert closures["dependency"] == ("middle", "root")
    assert closures["certification"] == ("root",)
    with pytest.raises(ManualSequencing):
        derived.closure("leaf", "invented")


def test_certification_relations_do_not_constrain_execution_order() -> None:
    """A certifier that depends on what it certifies is lawful, not a cycle."""
    pop = population(
        declare("engine", certifications=("auditor",)),
        declare("auditor", dependencies=("engine",)),
    )
    derived = planner.plan(pop)
    assert derived.executable
    assert derived.order.index("engine") < derived.order.index("auditor")


def test_a_cycle_in_an_unordered_relation_is_still_refused() -> None:
    """Ordering cannot see it, so the plan measures it directly."""
    pop = population(
        declare("a", governance_rules=("b",)),
        declare("b", governance_rules=("a",)),
    )
    derived = planner.plan(pop)
    assert not derived.executable
    assert "governance_rules" in derived.cyclic_relations
    assert any("cycle in governance_rules" in reason for reason in derived.refusals)


def test_an_illegal_population_yields_a_plan_that_refuses_to_execute() -> None:
    pop = population(declare("x", certifications=()))
    derived = planner.plan(pop)
    assert not derived.executable
    assert derived.status == "REFUSED"
    with pytest.raises(IllegalExecution) as excinfo:
        planner.require_executable(pop)
    assert "x" in excinfo.value.detail["illegal"]


def test_parallel_waves_expresses_the_declared_concurrency(lawful: Population) -> None:
    sequential = planner.plan(lawful, strategy="dependency-order")
    concurrent = planner.plan(lawful, strategy="parallel-waves")
    assert set(sequential.order) == set(concurrent.order)
    assert len(concurrent.waves) <= len(sequential.waves)


def test_a_plan_is_deterministic(lawful: Population) -> None:
    assert planner.plan(lawful).digest() == planner.plan(lawful).digest()


# --------------------------------------------------------------------------- state


def test_a_committed_seal_admits_every_guarded_act(lawful: Population) -> None:
    seal = state.commit(lawful, source="test")
    for act in state.GUARDED_ACTS:
        assert state.guard(seal, lawful, act=act) is seal


def test_a_seal_taken_during_a_mutation_is_born_dirty(lawful: Population) -> None:
    with state.mutating(lawful) as open_seal:
        assert open_seal.dirty
        for act in state.GUARDED_ACTS:
            with pytest.raises(DirtyStateViolation) as excinfo:
                state.guard(open_seal, lawful, act=act)
            assert excinfo.value.detail["clause"] == "CEL-07"


def test_a_stale_seal_is_refused_even_though_it_was_clean(lawful: Population) -> None:
    """Measure, mutate, then certify against the measurement — the subtle failure."""
    seal = state.commit(lawful)
    moved = lawful.with_records([declare("newcomer")])
    assert not seal.matches(moved)
    with pytest.raises(DirtyStateViolation) as excinfo:
        state.guard(seal, moved, act="certify")
    assert excinfo.value.detail["sealed_digest"] == seal.digest


def test_an_unguarded_act_is_admitted_but_can_be_guarded_explicitly(lawful: Population) -> None:
    with state.mutating(lawful) as open_seal:
        assert state.guard(open_seal, lawful, act="describe") is open_seal
        with pytest.raises(DirtyStateViolation):
            state.require_committed(open_seal, lawful, act="describe")


def test_a_seal_carries_no_clock(lawful: Population) -> None:
    """Freshness is digest equality; two seals of one state must be identical."""
    assert state.commit(lawful).seal_digest() == state.commit(lawful).seal_digest()


# --------------------------------------------------------------------------- replay


def test_a_pure_system_settles_at_round_two(lawful: Population) -> None:
    record = replay.require_fixed_point(lawful)
    assert record.fixed_point
    assert record.converged_at == 2
    assert record.divergent_acts() == ()
    assert record.status == "FIXED-POINT"


def test_divergence_is_refused_and_names_the_offending_act(lawful: Population) -> None:
    counter = iter(range(100))

    unstable = (
        *replay.REPLAY_ACTS,
        replay.Act("wobbly", "reads something it must not", lambda _pop: str(next(counter))),
    )
    record = replay.converge(lawful, acts=unstable)
    assert not record.fixed_point
    assert record.divergent_acts() == ("wobbly",)
    assert record.final_digest == ""

    counter2 = iter(range(100))
    unstable2 = (
        *replay.REPLAY_ACTS,
        replay.Act("wobbly", "reads something it must not", lambda _pop: str(next(counter2))),
    )
    with pytest.raises(ReplayDivergence) as excinfo:
        replay.require_fixed_point(lawful, acts=unstable2)
    assert excinfo.value.detail["divergent_acts"] == ["wobbly"]
    assert excinfo.value.detail["clause"] == "CEL-06"


def test_a_stable_failure_is_still_a_fixed_point(lawful: Population) -> None:
    """A deterministic failure reproduces; only an *unstable* one is divergence."""

    def always_raises(_pop: Population) -> str:
        raise RuntimeError("deterministic failure")

    acts = (replay.Act("broken", "fails the same way every time", always_raises),)
    record = replay.converge(lawful, acts=acts)
    assert record.fixed_point


def test_a_fixed_point_cannot_be_observed_in_one_round(lawful: Population) -> None:
    with pytest.raises(ReplayDivergence):
        replay.converge(lawful, max_rounds=1)


def test_asking_for_the_position_of_a_subject_the_plan_did_not_place_returns_minus_one(
    lawful: Population,
) -> None:
    """``-1`` and not an exception, because "not placed" is an ordinary answer.

    A caller comparing two subjects' positions is asking about the derived order, and a
    subject the plan could not place has no position in it. Raising would make every such
    comparison need a guard; returning ``0`` would put an unplaceable subject first.
    """
    plan = planner.plan(lawful)

    for subject in lawful.subjects():
        assert plan.position(subject) >= 0
    assert plan.position("never-declared") == -1
    positions = [plan.position(s) for s in lawful.subjects()]
    assert sorted(positions) == list(range(len(positions)))


def test_a_replay_with_a_single_round_names_no_divergent_act() -> None:
    """Divergence is a comparison BETWEEN two rounds, so one round can carry no verdict
    about it. Returning an empty tuple is the honest answer; comparing a round with itself
    would report perfect convergence for a replay that has not yet replayed anything."""
    settled = replay.converge(population(declare("root")))
    assert settled.fixed_point
    assert settled.divergent_acts() == ()

    one_round = dataclasses.replace(settled, rounds=settled.rounds[:1])
    assert len(one_round.rounds) == 1
    assert one_round.divergent_acts() == ()


def test_an_opened_seal_is_the_same_state_marked_dirty(lawful: Population) -> None:
    """``opened`` is what a mutation gateway holds while it works, and it must not re-derive
    the digest: the seal has to keep pointing at the state it was taken over, or the gateway
    would be holding a seal for a state that does not exist yet. Only ``committed`` moves."""
    committed = state.commit(lawful, source="test")
    assert committed.committed
    assert not committed.dirty

    opened = committed.opened()
    assert opened.dirty
    assert not opened.committed
    assert opened.digest == committed.digest
    assert opened.matches(lawful)
