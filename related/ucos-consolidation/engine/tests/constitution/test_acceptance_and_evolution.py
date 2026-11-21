"""UCOS-CEL-ENFORCE/UACE — the enforcement layer measures, and the cycle elevates.

The most important test in this file is
:func:`test_every_declared_invariant_has_a_measurement`. It is the one that keeps the rest
honest: if the law grows a clause that nothing counts, the system is back to *containing*
a rule rather than enforcing it, and that is the exact condition this package was built to
remove. It must fail loudly rather than pass quietly.

The second is :func:`test_the_system_satisfies_its_own_constitution`, which runs the whole
apparatus over the apparatus. It is a real proof of coherence, and it is not a proof that
the code does what it declares — that is what every other test here is for.
"""

from __future__ import annotations

import pytest

from engine.constitution import acceptance, catalog, evolution, gateway, law
from engine.constitution import stages as stage_faculties
from engine.constitution.errors import AcceptanceFailure, ConstitutionalError
from engine.constitution.metadata import Population
from engine.nucleus import lifecycle as nucleus_lifecycle
from engine.tests.constitution.conftest import declare, population

# --------------------------------------------------------------------------- enforcement


def test_every_declared_invariant_has_a_measurement() -> None:
    """A rule nobody counts is a preference. The law may not outgrow its enforcement."""
    assert acceptance.unmeasured_invariants() == ()
    assert set(acceptance.MEASUREMENTS) == {i.invariant_id for i in law.EXECUTION_INVARIANTS}


def test_a_lawful_population_satisfies_every_invariant_and_criterion(lawful: Population) -> None:
    report = acceptance.gate(lawful)
    assert report.passed
    assert report.status == "PASS"
    assert len(report.criteria) == len(law.ACCEPTANCE_CRITERIA)
    assert all(measured.satisfied for measured in report.measured)


@pytest.mark.parametrize(
    ("factory", "invariant"),
    [
        (lambda: population(declare("a", governance_rules=())), "CEL-INV-01"),
        (lambda: population(declare("a", dependencies=("ghost",))), "CEL-INV-02"),
        (
            lambda: population(
                declare("a", dependencies=("b",)), declare("b", dependencies=("a",))
            ),
            "CEL-INV-03",
        ),
        (
            lambda: population(declare("a", authorities=("b",)), declare("b", authorities=("a",))),
            "CEL-INV-04",
        ),
        (
            lambda: population(
                declare("a", certifications=("b",)), declare("b", certifications=("a",))
            ),
            "CEL-INV-05",
        ),
        (
            lambda: population(
                declare("a", canonical_owner=("b",)), declare("b", canonical_owner=("a",))
            ),
            "CEL-INV-06",
        ),
        (lambda: population(declare("a", certifications=("a",))), "CEL-INV-07"),
        (
            lambda: population(declare("a", outputs=("x",)), declare("b", outputs=("x",))),
            "CEL-INV-10",
        ),
        (lambda: population(declare("a", canonical_owner=("ext:x", "ext:y"))), "CEL-INV-11"),
    ],
)
def test_each_invariant_counts_its_own_violation(factory, invariant: str) -> None:
    report = acceptance.enforce(factory())
    measured = report.measurement(invariant)
    assert measured.count > 0, f"{invariant} did not count its violation"
    assert not measured.satisfied
    assert invariant in report.blocking_failures
    with pytest.raises(AcceptanceFailure) as excinfo:
        acceptance.gate(factory())
    assert invariant in excinfo.value.detail["blocking_failures"]


def test_an_unmeasured_invariant_is_blocking_not_satisfied(
    lawful: Population, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The enforcement layer fails closed on its own incompleteness.

    Simulates the law growing an invariant that :data:`acceptance.MEASUREMENTS` has no
    entry for. The layer must report it unmeasured *and* blocking — silently passing a
    rule it cannot count would put the repository back to containing rules rather than
    enforcing them, which is the whole defect this package removes.
    """
    extra = law.Invariant("CEL-INV-99", "invented", "nothing counts this", "CEL-01")
    monkeypatch.setattr(acceptance, "EXECUTION_INVARIANTS", (*law.EXECUTION_INVARIANTS, extra))
    report = acceptance.enforce(lawful)
    measured = report.measurement("CEL-INV-99")
    assert not measured.measured
    assert not measured.satisfied
    assert "CEL-INV-99" in report.blocking_failures
    with pytest.raises(AcceptanceFailure):
        acceptance.gate(lawful)


def test_an_unknown_measurement_lookup_fails_closed(lawful: Population) -> None:
    with pytest.raises(AcceptanceFailure):
        acceptance.enforce(lawful).measurement("CEL-INV-404")


def test_one_view_is_shared_by_every_measurement(lawful: Population) -> None:
    """Twelve independently derived views could disagree; one cannot."""
    view = acceptance.View.of(lawful)
    assert view.plan.graph.digest() == view.graph.digest()
    assert view.legality.passed and view.authority.passed


# --------------------------------------------------------------------------- evolution


def test_the_phase_order_is_derived(lawful: Population) -> None:
    assert evolution.phase_order()[0] == "discover"
    assert evolution.phase_order()[-1] == "elevate"
    assert len(evolution.phase_order()) == len(evolution.PHASES)


def test_a_measuring_cycle_completes_and_elevates(lawful: Population) -> None:
    record = evolution.require_elevation(lawful, evolution.Goal("measure", authority="ext:a"))
    assert record.complete
    assert record.status == "ELEVATED"
    assert record.capability > 0
    assert record.next_input() is lawful


def test_a_mutating_cycle_carries_the_mutation_through(lawful: Population) -> None:
    goal = evolution.Goal(
        "add a subject",
        authority="ext:a",
        mutation=gateway.Mutation(
            records=(declare("added", dependencies=("root",)),), authority="ext:a"
        ),
    )
    record = evolution.require_elevation(lawful, goal)
    assert "added" in record.population
    assert record.seal is not None and record.seal.committed
    assert record.outcome("mutate").satisfied


@pytest.mark.parametrize(
    ("factory", "phase"),
    [
        (lambda: population(declare("a", dependencies=("ghost",))), "discover"),
        (
            lambda: population(declare("a", outputs=("x",)), declare("b", outputs=("x",))),
            "assimilate",
        ),
        (lambda: population(declare("a", certifications=("a",))), "govern"),
        (lambda: population(declare("a", governance_rules=())), "verify"),
    ],
)
def test_the_cycle_stops_at_the_phase_that_refuses(factory, phase: str) -> None:
    record = evolution.run(factory(), evolution.Goal("try", authority="ext:a"))
    assert not record.complete
    assert record.refused_at == phase
    assert record.status == "REFUSED"
    with pytest.raises(ConstitutionalError) as excinfo:
        evolution.require_elevation(factory(), evolution.Goal("try", authority="ext:a"))
    assert excinfo.value.detail["refused_at"] == phase


def test_a_refused_cycle_reports_only_the_phases_it_reached() -> None:
    record = evolution.run(
        population(declare("a", dependencies=("ghost",))), evolution.Goal("try", authority="ext:a")
    )
    assert [o.name for o in record.outcomes] == ["discover"]
    with pytest.raises(ConstitutionalError):
        record.outcome("elevate")


def test_a_mutation_refused_by_the_gateway_refuses_the_cycle(lawful: Population) -> None:
    goal = evolution.Goal(
        "smuggle",
        authority="ext:a",
        mutation=gateway.Mutation(
            records=(declare("selfie", certifications=("selfie",)),), authority="ext:a"
        ),
    )
    record = evolution.run(lawful, goal)
    assert record.refused_at == "mutate"
    assert record.population is lawful


def test_cycles_converge_when_the_state_stops_changing(lawful: Population) -> None:
    records = evolution.converge_cycles(lawful, evolution.Goal("measure", authority="ext:a"))
    assert len(records) == 1
    assert records[0].complete


def test_the_capability_reading_is_derived_from_measurements(lawful: Population) -> None:
    healthy = evolution.capability_reading(lawful)
    degraded = evolution.capability_reading(population(declare("a", governance_rules=())))
    assert healthy > degraded


# --------------------------------------------------------------------------- composition


def test_the_engine_discharges_ucl_000001_rather_than_copying_it(lawful: Population) -> None:
    """The declared lifecycle keeps its stages and gains an implementation."""
    execution = nucleus_lifecycle.execute(
        "repository",
        stage_function=evolution.lifecycle_stage_function(lawful),
        context={"frame": "test"},
    )
    assert len(execution.outcomes) == len(nucleus_lifecycle.STAGES)
    assert execution.complete
    assert execution.chain_is_intact()
    satisfied = [
        o for o in execution.outcomes if o.status is nucleus_lifecycle.StageStatus.SATISFIED
    ]
    unclaimed = [
        o for o in execution.outcomes if o.status is nucleus_lifecycle.StageStatus.NOT_APPLICABLE
    ]
    # This assertion was once the reverse: it required *some* stage to be unclaimed,
    # because the engine carried one verdict per stage group and had a faculty for only
    # seven of sixteen. engine.constitution.stages now supplies one faculty per declared
    # stage, so nothing is unclaimed — and the honest assertion is the stronger one.
    assert len(satisfied) == len(
        execution.outcomes
    ), "every declared stage must be discharged by a measurement"
    assert unclaimed == [], "a stage with no faculty would be silently unmeasured"


def test_a_failing_population_fails_the_lifecycle_stages_it_owns() -> None:
    broken = population(declare("a", dependencies=("ghost",)))
    execution = nucleus_lifecycle.execute(
        "repository", stage_function=evolution.lifecycle_stage_function(broken)
    )
    assert execution.failures
    assert not execution.complete


# --------------------------------------------------------------------------- self-proof


def test_the_system_satisfies_its_own_constitution() -> None:
    """The engines that enforce CEL-09 are not exempt from CEL-09."""
    system = catalog.build_population()
    assert len(system) == len(catalog.DECLARATIONS)
    report = acceptance.gate(system)
    assert report.passed
    record = evolution.require_elevation(
        system, evolution.Goal("prove self-coherence", authority=catalog.DETERMINATION)
    )
    assert record.complete
    assert record.outcome("certify").satisfied


def test_the_system_declares_no_subject_it_does_not_implement() -> None:
    """A declaration naming an engine that does not exist would be a comfortable lie."""
    for subject, engine_id in catalog.engine_index().items():
        assert engine_id.startswith("UCOS-"), subject


def test_the_whole_system_is_deterministic() -> None:
    system = catalog.build_population()
    assert acceptance.enforce(system).digest() == acceptance.enforce(system).digest()
    first = evolution.run(system, evolution.Goal("replay me", authority="ext:a"))
    second = evolution.run(system, evolution.Goal("replay me", authority="ext:a"))
    assert first.digest() == second.digest()


def test_a_cycle_declaring_a_cycle_among_its_phases_has_no_order() -> None:
    """The evolution engine derives its own phase order through CEL-02 rather than reading
    it off ``PHASES``, which is what makes it subject to the ordering law like everything
    else. The cost is that its declaration could be cyclic, and the refusal is what stops a
    cyclic declaration from yielding a partial order that quietly runs some phases."""
    cyclic = (
        evolution.Phase(
            name="a", statement="a", depends_on=("b",), run=lambda c: (True, "", {}, c)
        ),
        evolution.Phase(
            name="b", statement="b", depends_on=("a",), run=lambda c: (True, "", {}, c)
        ),
    )
    with pytest.raises(ConstitutionalError) as excinfo:
        evolution.phase_order(cyclic)
    assert "declares a cycle" in str(excinfo.value)
    assert set(excinfo.value.detail["unresolved"]) == {"a", "b"}


def test_a_phase_that_cannot_be_evaluated_is_a_failed_phase_and_not_a_crash(
    lawful: Population,
) -> None:
    """AN EXCEPTION OUT OF A PHASE IS STILL A VERDICT — the same discipline the mutation
    pipeline keeps for its stages. Letting it escape would abandon the cycle with no record
    of which phase was being evaluated, and the record is the only thing a later reader has.
    """

    def explode(_cycle):
        raise RuntimeError("the observation surface is unavailable")

    phases = tuple(
        evolution.Phase(
            name=phase.name,
            statement=phase.statement,
            run=explode if phase.name == evolution.PHASES[0].name else phase.run,
            depends_on=phase.depends_on,
        )
        for phase in evolution.PHASES
    )
    record = evolution.run(lawful, evolution.Goal("measure only"), phases=phases)

    assert not record.complete
    failed = next(o for o in record.outcomes if not o.satisfied)
    assert "phase could not be evaluated" in failed.detail
    assert "the observation surface is unavailable" in failed.detail


def test_converging_runs_again_only_while_the_population_keeps_moving(
    lawful: Population,
) -> None:
    """THE STOPPING CONDITION IS A FIXED POINT, NOT A COUNT.

    A cycle that leaves the population digest unchanged has found a fixed point of the
    repository's own constitution, and running again would produce the same record — so the
    loop stops. It also stops on an incomplete cycle, because re-running a refused cycle
    would re-refuse it. The ``current = record.population`` line is the only way the loop
    ever continues, and it had never run: every fixture settles on its first cycle, which is
    the correct outcome and also why the continuation was dead.
    """
    goal = evolution.Goal("measure only")

    settled = evolution.converge_cycles(lawful, goal)
    assert len(settled) == 1, "the fixture no longer settles on its first cycle"

    calls: list[int] = []

    class _Record:
        def __init__(self, population):
            self.complete = True
            self.population = population

    def advancing(population, _goal, **_kwargs):
        calls.append(len(calls))
        if len(calls) < 3:
            return _Record(population.with_records([declare(f"grown{len(calls)}")]))
        return _Record(population)

    original = evolution.run
    try:
        evolution.run = advancing
        records = evolution.converge_cycles(lawful, goal, max_cycles=10)
    finally:
        evolution.run = original

    assert len(records) == 3, "the loop did not continue while the population was moving"
    assert records[-1].population.digest() == records[-2].population.digest()

    # AND THE BOUND IS REAL. A population that never stops moving would loop forever, so
    # `max_cycles` is what makes convergence terminate on a repository that does not
    # converge — the answer is then "these cycles ran and it had not settled", which is a
    # result a reader can act on rather than a hang.
    calls.clear()
    never_settles = 0

    def always_moving(population, _goal, **_kwargs):
        nonlocal never_settles
        never_settles += 1
        return _Record(population.with_records([declare(f"more{never_settles}")]))

    try:
        evolution.run = always_moving
        bounded = evolution.converge_cycles(lawful, goal, max_cycles=2)
    finally:
        evolution.run = original

    assert len(bounded) == 2, "the bound did not stop a population that never settles"
    assert bounded[-1].population.digest() != bounded[-2].population.digest()


def test_a_stage_with_no_registered_faculty_is_unclaimed_rather_than_satisfied(
    lawful: Population,
) -> None:
    """NOT_APPLICABLE, never SATISFIED. A stage nobody measures is honestly unclaimed;
    reporting it satisfied would let a lifecycle stage be discharged by the ABSENCE of a
    measurement, which is the same defect as a declaration asserting itself."""
    stage_function = evolution.lifecycle_stage_function(lawful)
    unregistered = nucleus_lifecycle.Stage(
        stage_id="no-such-stage", name="unclaimed", ordinal=999, group="none"
    )
    status, _evidence_id, detail = stage_function("root", unregistered)

    assert status is nucleus_lifecycle.StageStatus.NOT_APPLICABLE
    assert detail["reason"] == "no faculty for this stage"
    assert detail["subject"] == "root"


def test_a_faculty_that_raises_fails_its_stage_and_names_the_error(
    lawful: Population, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The same "an exception is still a verdict" discipline, at the composition point where
    this engine's faculties are handed to UCL-000001. A raising faculty must fail its own
    stage rather than abort the lifecycle run, and the error type and text are carried into
    the evidence so the failure is diagnosable from the record."""

    stage_id = next(iter(stage_faculties.FACULTIES))

    def explode(_context):
        raise RuntimeError("the manifest is unreadable")

    monkeypatch.setitem(stage_faculties.FACULTIES, stage_id, explode)
    stage_function = evolution.lifecycle_stage_function(lawful)
    declared = nucleus_lifecycle.Stage(stage_id=stage_id, name="declared", ordinal=1, group="any")
    status, evidence_id, detail = stage_function("root", declared)

    assert status is nucleus_lifecycle.StageStatus.FAILED
    assert evidence_id.endswith(":unevaluable")
    assert "RuntimeError" in detail["error"]
    assert "the manifest is unreadable" in detail["error"]
