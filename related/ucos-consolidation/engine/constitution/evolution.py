"""UCOS-UACE-000001 — the Universal Autonomous Constitutional Evolution Engine (Req 011).

Everything else in this package is a faculty. This module is the loop that exercises them
in the one order it is lawful to exercise them in, and it is where the directive's
lifecycle — receive goal, discover, assimilate, plan, verify, certify, register, replay,
elevate, begin again — becomes a single call that either produces a certified, settled,
elevated state or refuses and says which faculty refused.

Its relationship to the 45-stage lifecycle
------------------------------------------
It does not replace it and does not copy it. ``UCL-000001``
(:mod:`engine.nucleus.lifecycle`) remains the one lifecycle authority, and its stage set
remains a checked projection of the manifest that owns it. A second stage list here — even
a longer, more detailed one — would be a second lifecycle truth, which CEL-08 forbids as
plainly as it forbids a duplicate capability.

So the relationship is composition. This engine supplies the *closure, legality, ordering,
mutation and convergence machinery* the lifecycle's stages were always meant to be
discharged by, and :func:`lifecycle_stage_function` hands that machinery to
:func:`engine.nucleus.lifecycle.execute` as its stage function — the extension point that
module already declares. The lifecycle keeps its 45 stages and gains an implementation;
this engine keeps its faculties and gains a lifecycle. Neither grows a copy of the other.

Elevation is measured, not asserted
-----------------------------------
CEL-11 requires a cycle to leave the repository more capable than it found it. That needs
a number, so :func:`capability_reading` computes one from the state — subjects that proved
legality, invariants that measured clean, criteria that held — and the reading is checked
for regression by :func:`engine.nucleus.evolution.state_must_grow`, the repository's
existing rule for "increase", rather than by a second definition of the word.
"""

from __future__ import annotations

from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass, field
from typing import Any

from engine.constitution import acceptance as enforcement_layer
from engine.constitution import assimilation as assimilation_gate
from engine.constitution import authority as authority_graph
from engine.constitution import dependency as dependency_graph
from engine.constitution import gateway as mutation_gateway
from engine.constitution import legality as legality_engine
from engine.constitution import planner as execution_planner
from engine.constitution import replay as replay_engine
from engine.constitution import state as state_engine
from engine.constitution.errors import ConstitutionalError
from engine.constitution.law import EXECUTION_INVARIANTS, LAW_ID
from engine.constitution.metadata import Population
from engine.foundation.composition.ordering import DEFAULT_STRATEGY, derive_order, unresolved_keys
from engine.nucleus import lifecycle as nucleus_lifecycle
from engine.nucleus.evolution import Evolution, state_must_grow
from engine.uckp.canonical import content_hash

#: The identity of the evolution engine this module realises.
ENGINE_ID = "UCOS-UACE-000001"

#: Versioned so phases can be *appended* without any prior cycle record changing meaning.
EVOLUTION_VERSION = "1.0.0"


@dataclass(frozen=True, slots=True)
class Goal:
    """What a cycle was asked to achieve, and the authority that asked.

    A cycle with no goal is a measurement; a cycle with a goal is an evolution. Both are
    lawful, which is why ``mutation`` is optional — a repository that runs the cycle and
    changes nothing has still proven it is still correct, and that is a result worth
    having.
    """

    statement: str
    authority: str = ""
    mutation: mutation_gateway.Mutation | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "statement": self.statement,
            "authority": self.authority,
            "mutation": self.mutation.to_dict() if self.mutation else None,
        }


@dataclass(frozen=True, slots=True)
class PhaseOutcome:
    """The record of one phase of one cycle."""

    name: str
    satisfied: bool
    statement: str
    detail: str
    evidence_digest: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "satisfied": self.satisfied,
            "statement": self.statement,
            "detail": self.detail,
            "evidence_digest": self.evidence_digest,
        }


@dataclass(frozen=True, slots=True)
class CycleState:
    """The state one cycle carries between phases."""

    population: Population
    goal: Goal
    seal: state_engine.StateSeal | None = None
    mutation_record: mutation_gateway.MutationRecord | None = None
    replay_record: replay_engine.ReplayRecord | None = None
    acceptance: enforcement_layer.AcceptanceReport | None = None
    plan: execution_planner.ExecutionPlan | None = None


#: A phase: given the state, return ``(satisfied, detail, evidence, next_state)``.
PhaseFunction = Callable[[CycleState], "tuple[bool, str, Any, CycleState]"]


@dataclass(frozen=True, slots=True)
class Phase:
    """One phase of the constitutional evolution cycle."""

    name: str
    statement: str
    run: PhaseFunction
    depends_on: tuple[str, ...] = ()

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "statement": self.statement,
            "depends_on": list(self.depends_on),
        }


# --------------------------------------------------------------------------- #
# The phases                                                                   #
# --------------------------------------------------------------------------- #


def _discover(cycle: CycleState) -> tuple[bool, str, Any, CycleState]:
    """Repository truth discovery: derive the whole constitutional graph."""
    graph = dependency_graph.build(cycle.population)
    unknown = graph.unknown_referents()
    if unknown:
        return (
            False,
            f"{len(unknown)} declared referent(s) name subjects that do not exist",
            graph.to_dict(),
            cycle,
        )
    detail = f"{len(graph.subjects)} subject(s), {len(graph.edges)} edge(s)"
    return True, detail, graph.to_dict(), cycle


def _assimilate(cycle: CycleState) -> tuple[bool, str, Any, CycleState]:
    """Reuse before create: no capability is produced by two subjects."""
    duplicates = assimilation_gate.duplicate_capabilities(cycle.population)
    if duplicates:
        rendered = "; ".join(f"{k}: {', '.join(v)}" for k, v in duplicates.items())
        return False, f"duplicate canonical truth: {rendered}", {"duplicates": duplicates}, cycle
    return True, "no duplicate canonical truth", {"duplicates": {}}, cycle


def _govern(cycle: CycleState) -> tuple[bool, str, Any, CycleState]:
    """Authority closure: nothing derives its own permission to exist."""
    graph = dependency_graph.build(cycle.population)
    report = authority_graph.analyse(cycle.population, graph)
    detail = (
        "authority closes"
        if report.passed
        else f"{len(report.findings)} breach(es): {'; '.join(f.detail for f in report.findings)}"
    )
    return report.passed, detail, report.to_dict(), cycle


def _verify(cycle: CycleState) -> tuple[bool, str, Any, CycleState]:
    """Legality: every subject proves all nine obligations."""
    graph = dependency_graph.build(cycle.population)
    report = legality_engine.assess(cycle.population, graph)
    detail = (
        f"{len(report.legal_subjects)} subject(s) proved legality"
        if report.passed
        else f"{len(report.illegal)} illegal subject(s): "
        f"{', '.join(v.subject for v in report.illegal)}"
    )
    return report.passed, detail, report.to_dict(), cycle


def _plan(cycle: CycleState) -> tuple[bool, str, Any, CycleState]:
    """Topological ordering: the legal execution order is derived."""
    derived = execution_planner.plan(cycle.population)
    detail = (
        f"{len(derived.order)} subject(s) in {len(derived.waves)} wave(s)"
        if derived.executable
        else "; ".join(derived.refusals)
    )
    return (
        derived.executable,
        detail,
        derived.to_dict(),
        CycleState(
            population=cycle.population,
            goal=cycle.goal,
            seal=cycle.seal,
            mutation_record=cycle.mutation_record,
            replay_record=cycle.replay_record,
            acceptance=cycle.acceptance,
            plan=derived,
        ),
    )


def _mutate(cycle: CycleState) -> tuple[bool, str, Any, CycleState]:
    """Every change to repository truth passes the gateway, or the cycle does not change it."""
    if cycle.goal.mutation is None:
        return True, "no mutation proposed; the cycle measures rather than changes", {}, cycle
    record = mutation_gateway.propose(cycle.population, cycle.goal.mutation)
    if not record.applied:
        return (
            False,
            f"mutation refused at {record.refused_at}: "
            f"{next((o.detail for o in record.outcomes if not o.satisfied), '')}",
            record.to_dict(),
            cycle,
        )
    return (
        True,
        f"{len(cycle.goal.mutation.records)} record(s) applied",
        record.to_dict(),
        CycleState(
            population=record.population,
            goal=cycle.goal,
            seal=record.seal,
            mutation_record=record,
            replay_record=record.replay,
            acceptance=cycle.acceptance,
            plan=cycle.plan,
        ),
    )


def _converge(cycle: CycleState) -> tuple[bool, str, Any, CycleState]:
    """Replay to a deterministic fixed point; nothing is certified before it settles."""
    record = replay_engine.converge(cycle.population)
    detail = (
        f"fixed point at round {record.converged_at}"
        if record.fixed_point
        else f"divergent acts: {', '.join(record.divergent_acts()) or 'unknown'}"
    )
    return (
        record.fixed_point,
        detail,
        record.to_dict(),
        CycleState(
            population=cycle.population,
            goal=cycle.goal,
            seal=cycle.seal,
            mutation_record=cycle.mutation_record,
            replay_record=record,
            acceptance=cycle.acceptance,
            plan=cycle.plan,
        ),
    )


def _certify(cycle: CycleState) -> tuple[bool, str, Any, CycleState]:
    """The enforcement layer measures every invariant and resolves every criterion.

    Runs against a committed seal. If the cycle mutated, the seal came from the gateway
    after convergence; if it did not, one is taken here over an unchanged state. Either
    way the certification reads state that is not moving, which is CEL-07.
    """
    seal = cycle.seal or state_engine.commit(cycle.population, engine_id=ENGINE_ID)
    state_engine.guard(seal, cycle.population, act="certify")
    report = enforcement_layer.enforce(cycle.population)
    detail = (
        f"{len(report.criteria)} criteria hold"
        if report.passed
        else f"failures: {', '.join(report.blocking_failures)}"
    )
    return (
        report.passed,
        detail,
        report.to_dict(),
        CycleState(
            population=cycle.population,
            goal=cycle.goal,
            seal=seal,
            mutation_record=cycle.mutation_record,
            replay_record=cycle.replay_record,
            acceptance=report,
            plan=cycle.plan,
        ),
    )


def _elevate(cycle: CycleState) -> tuple[bool, str, Any, CycleState]:
    """The capability reading did not regress — CEL-11, measured rather than asserted."""
    reading = capability_reading(cycle.population, acceptance=cycle.acceptance)
    evolution = Evolution(
        subject_id=f"UCOS-CYCLE-{content_hash(cycle.goal.statement)[:12]}",
        subject_key="repository",
        generation=1,
        change=cycle.goal.statement or "constitutional cycle",
        state={"capability": reading},
        authority=cycle.goal.authority or ENGINE_ID,
    )
    grew, why = state_must_grow(evolution)
    return grew, why or f"capability reading {reading}", {"capability": reading}, cycle


#: The cycle's phases (DATA — extend by appending). Order is *derived* from the declared
#: chain by the single ordering authority, so the cycle is subject to CEL-02 like
#: everything else rather than being the one place a sequence is written down.
PHASES: tuple[Phase, ...] = (
    Phase("discover", "repository truth is discovered from the declarations", _discover),
    Phase(
        "assimilate",
        "reuse precedes creation; no capability has two owners",
        _assimilate,
        depends_on=("discover",),
    ),
    Phase(
        "govern",
        "authority closes; nothing derives its own permission to exist",
        _govern,
        depends_on=("assimilate",),
    ),
    Phase(
        "verify",
        "every subject proves every legality obligation",
        _verify,
        depends_on=("govern",),
    ),
    Phase(
        "plan",
        "the legal execution order is derived, never declared",
        _plan,
        depends_on=("verify",),
    ),
    Phase(
        "mutate",
        "every change passes the mutation gateway",
        _mutate,
        depends_on=("plan",),
    ),
    Phase(
        "converge",
        "replay reaches a deterministic fixed point",
        _converge,
        depends_on=("mutate",),
    ),
    Phase(
        "certify",
        "every invariant is measured and every acceptance criterion resolved",
        _certify,
        depends_on=("converge",),
    ),
    Phase(
        "elevate",
        "the capability reading did not regress",
        _elevate,
        depends_on=("certify",),
    ),
)


def phase_order(
    phases: Sequence[Phase] = PHASES, *, strategy: str = DEFAULT_STRATEGY
) -> tuple[str, ...]:
    """The derived run order of the cycle's phases."""
    graph = {phase.name: phase.depends_on for phase in phases}
    ordering = derive_order(graph, strategy=strategy)
    if unresolved := unresolved_keys(graph, ordering):
        raise ConstitutionalError(
            "the evolution cycle declares a cycle among its phases; no order exists",
            engine_id=ENGINE_ID,
            unresolved=unresolved,
        )
    return tuple(name for _wave, name in ordering)


def capability_reading(
    population: Population,
    *,
    acceptance: enforcement_layer.AcceptanceReport | None = None,
) -> int:
    """A whole-number reading of the repository's constitutional capability.

    Counted, not judged: subjects that carry complete metadata, subjects that proved
    legality, and invariants that measured clean. Every term is something this package
    already measures, so the reading cannot drift from the reports it summarises, and a
    cycle cannot raise it except by making one of those three things more true.
    """
    report = acceptance or enforcement_layer.enforce(population)
    complete = sum(1 for record in population if record.complete)
    legal = len(report.measurement("CEL-INV-08").subjects)
    clean = sum(1 for measured in report.measured if measured.satisfied)
    return complete + (len(population) - legal) + clean


@dataclass(frozen=True, slots=True)
class CycleRecord:
    """The complete, replayable record of one constitutional evolution cycle."""

    engine_id: str
    law_id: str
    goal: Goal
    outcomes: tuple[PhaseOutcome, ...]
    order: tuple[str, ...]
    population: Population
    seal: state_engine.StateSeal | None = None
    acceptance: enforcement_layer.AcceptanceReport | None = None
    plan: execution_planner.ExecutionPlan | None = None
    replay: replay_engine.ReplayRecord | None = None
    capability: int = 0
    scope: Mapping[str, Any] = field(default_factory=dict)

    @property
    def refused_at(self) -> str:
        for outcome in self.outcomes:
            if not outcome.satisfied:
                return outcome.name
        return ""

    @property
    def complete(self) -> bool:
        """True iff every declared phase ran and none refused."""
        return len(self.outcomes) == len(PHASES) and not self.refused_at

    @property
    def status(self) -> str:
        return "ELEVATED" if self.complete else "REFUSED"

    def outcome(self, name: str) -> PhaseOutcome:
        for item in self.outcomes:
            if item.name == name:
                return item
        raise ConstitutionalError(
            "this cycle did not reach that phase",
            engine_id=self.engine_id,
            phase=name,
            reached=[o.name for o in self.outcomes],
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema": "ucos-constitutional-evolution-cycle",
            "version": EVOLUTION_VERSION,
            "engine_id": self.engine_id,
            "law_id": self.law_id,
            "status": self.status,
            "refused_at": self.refused_at,
            "goal": self.goal.to_dict(),
            "order": list(self.order),
            "phases": [o.to_dict() for o in self.outcomes],
            "capability": self.capability,
            "population_digest": self.population.digest(),
            "seal": self.seal.to_dict() if self.seal else None,
            "acceptance_digest": self.acceptance.digest() if self.acceptance else "",
            "plan_digest": self.plan.digest() if self.plan else "",
            "replay_digest": self.replay.digest() if self.replay else "",
            "scope": {k: self.scope[k] for k in sorted(self.scope)},
        }

    def digest(self) -> str:
        return content_hash(self.to_dict())

    def next_input(self) -> Population:
        """The state the next cycle begins from — CEL-11's "input to the next cycle"."""
        return self.population


def run(
    population: Population,
    goal: Goal,
    *,
    phases: Sequence[Phase] = PHASES,
    strategy: str = DEFAULT_STRATEGY,
) -> CycleRecord:
    """Run one whole constitutional evolution cycle over ``population``.

    Stops at the first refusal, for the same reason the gateway does: a phase that runs
    after a failed one is judging a state that was never going to exist. The record names
    the phase that refused, which is the actionable half of a failure.

    Returns the record whether or not the cycle completed; :func:`require_elevation` is
    the fail-closed form.
    """
    order = phase_order(phases, strategy=strategy)
    by_name = {phase.name: phase for phase in phases}
    cycle = CycleState(population=population, goal=goal)
    outcomes: list[PhaseOutcome] = []

    for name in order:
        phase = by_name[name]
        try:
            satisfied, detail, evidence, cycle = phase.run(cycle)
        except Exception as exc:  # noqa: BLE001 - an unevaluable phase is a failed phase
            satisfied, detail, evidence = False, f"phase could not be evaluated: {exc}", {}
        outcomes.append(
            PhaseOutcome(
                name=phase.name,
                satisfied=bool(satisfied),
                statement=phase.statement,
                detail=str(detail),
                evidence_digest=content_hash(evidence) if evidence else "",
            )
        )
        if not satisfied:
            break

    return CycleRecord(
        engine_id=ENGINE_ID,
        law_id=LAW_ID,
        goal=goal,
        outcomes=tuple(outcomes),
        order=order,
        population=cycle.population,
        seal=cycle.seal,
        acceptance=cycle.acceptance,
        plan=cycle.plan,
        replay=cycle.replay_record,
        capability=capability_reading(cycle.population, acceptance=cycle.acceptance),
        scope={
            "entry_digest": population.digest(),
            "exit_digest": cycle.population.digest(),
            "phase_count": len(phases),
        },
    )


def require_elevation(
    population: Population,
    goal: Goal,
    *,
    phases: Sequence[Phase] = PHASES,
    strategy: str = DEFAULT_STRATEGY,
) -> CycleRecord:
    """Run the cycle and refuse unless it completed and elevated.

    Raises:
        ConstitutionalError: a phase refused; the phase and its detail are named.
    """
    record = run(population, goal, phases=phases, strategy=strategy)
    if not record.complete:
        raise ConstitutionalError(
            "the constitutional evolution cycle did not complete",
            engine_id=ENGINE_ID,
            refused_at=record.refused_at,
            detail=next((o.detail for o in record.outcomes if not o.satisfied), ""),
            phases=[o.to_dict() for o in record.outcomes],
        )
    return record


def converge_cycles(
    population: Population,
    goal: Goal,
    *,
    max_cycles: int = 4,
) -> tuple[CycleRecord, ...]:
    """Run cycles until the state stops changing — "begin next elevated cycle", bounded.

    Each cycle's output is the next cycle's input, which is CEL-11's loop. It terminates
    when a cycle leaves the population digest unchanged: at that point the repository is a
    fixed point of its own constitution, and running again would produce the same record.
    """
    records: list[CycleRecord] = []
    current = population
    for _ in range(max(1, max_cycles)):
        record = run(current, goal)
        records.append(record)
        if not record.complete or record.population.digest() == current.digest():
            break
        current = record.population
    return tuple(records)


def lifecycle_stage_function(
    population: Population,
) -> nucleus_lifecycle.StageFunction:
    """Hand this engine's faculties to ``UCL-000001`` as its stage function.

    The composition point named in this module's docstring. The 45 stages stay where they
    are declared; what changes is that a stage is now discharged by a measurement rather
    than by the declaration asserting itself.

    Discharge is **per stage**, not per group. An earlier form of this function carried one
    verdict for a whole stage group, which meant a stage could read as satisfied because a
    sibling was — a group of eight sharing one measurement is one measurement, not eight.
    :mod:`engine.constitution.stages` supplies one faculty per declared stage, and each
    returns the digest of what it actually measured.

    A stage with no registered faculty is reported ``NOT_APPLICABLE`` — honestly unclaimed
    rather than silently satisfied, the same discipline
    :func:`engine.nucleus.lifecycle.satisfied_by_declaration` keeps.
    """
    from engine.constitution import stages as stage_faculties

    context = stage_faculties.Context(population=population)

    def stage_function(
        subject: str, stage: nucleus_lifecycle.Stage
    ) -> tuple[nucleus_lifecycle.StageStatus, str, Mapping[str, Any]]:
        registered = stage_faculties.FACULTIES.get(stage.stage_id)
        if registered is None:
            return (
                nucleus_lifecycle.StageStatus.NOT_APPLICABLE,
                f"{ENGINE_ID}:{stage.stage_id}",
                {"subject": subject, "group": stage.group, "reason": "no faculty for this stage"},
            )
        try:
            measurement = registered(context)
        except Exception as exc:  # noqa: BLE001 - an unevaluable faculty is a failed stage
            return (
                nucleus_lifecycle.StageStatus.FAILED,
                f"{stage_faculties.EVIDENCE_PREFIX}:unevaluable",
                {"subject": subject, "group": stage.group, "error": f"{type(exc).__name__}: {exc}"},
            )
        return (
            nucleus_lifecycle.StageStatus.SATISFIED
            if measurement.satisfied
            else nucleus_lifecycle.StageStatus.FAILED,
            measurement.digest(),
            {"subject": subject, "group": stage.group, "detail": measurement.detail},
        )

    return stage_function


def to_document() -> dict[str, Any]:
    """The cycle model as a deterministic, machine-readable document."""
    return {
        "schema": "ucos-constitutional-evolution-engine",
        "version": EVOLUTION_VERSION,
        "engine_id": ENGINE_ID,
        "law_id": LAW_ID,
        "phases": [p.to_dict() for p in PHASES],
        "order": list(phase_order()),
        "lifecycle_authority": nucleus_lifecycle.LIFECYCLE_ID,
        "lifecycle_stage_count": len(nucleus_lifecycle.STAGES),
        "invariant_count": len(EXECUTION_INVARIANTS),
        "closed_set": False,
    }


def digest() -> str:
    return content_hash(to_document())


__all__ = [
    "ENGINE_ID",
    "EVOLUTION_VERSION",
    "PHASES",
    "CycleRecord",
    "CycleState",
    "Goal",
    "Phase",
    "PhaseFunction",
    "PhaseOutcome",
    "capability_reading",
    "converge_cycles",
    "digest",
    "lifecycle_stage_function",
    "phase_order",
    "require_elevation",
    "run",
    "to_document",
]
