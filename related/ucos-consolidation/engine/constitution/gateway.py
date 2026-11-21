"""UCOS-CMG-EXEC-000001 — the Constitutional Mutation Gateway (Requirement 004).

Every mutation of repository truth executes one sequence: proposal, evidence, validation,
verification, certification, registration, truth update. A mutation that does not
discharge every stage does not apply — not partially, not provisionally, not pending a
follow-up.

How "direct mutation shall be impossible" is actually enforced
--------------------------------------------------------------
Python cannot stop a caller from constructing a
:class:`~engine.constitution.metadata.Population` by hand, and a docstring asking them not
to would be exactly the trust-based operation this package exists to remove. So the
enforcement is placed where it can be real: **the gateway is the only producer of a clean
:class:`~engine.constitution.state.StateSeal`.**

:mod:`engine.constitution.state` refuses to verify, certify, register, measure or govern
under a seal that is dirty or that does not match the state being acted on. A population
assembled outside this pipeline therefore exists, and can be read, and can be printed —
and can do none of the five things that would let it become repository truth. The bypass
path is not blocked by a rule; it is blocked by there being nothing at the end of it.

The stages are data
-------------------
:data:`PIPELINE` is a tuple of ``(name, statement, function)``. The order is derived from
the declared chain by the single ordering authority, exactly as the lifecycle's is, so the
pipeline cannot be silently re-sequenced by editing a call site — and an eighth stage is
one appended entry. Each stage is journalled into a hash chain, so a record of a mutation
is tamper-evident rather than merely detailed.
"""

from __future__ import annotations

from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass, field
from typing import Any

from engine.constitution import assimilation as assimilation_gate
from engine.constitution import authority as authority_graph
from engine.constitution import dependency as dependency_graph
from engine.constitution import legality as legality_engine
from engine.constitution import planner as execution_planner
from engine.constitution import replay as replay_engine
from engine.constitution import state as state_engine
from engine.constitution.errors import ConstitutionalError, MutationRefused
from engine.constitution.metadata import ConstitutionalMetadata, Population
from engine.foundation.composition.ordering import DEFAULT_STRATEGY, derive_order, unresolved_keys
from engine.registry.universal.identity import is_well_formed
from engine.uckp.canonical import content_hash

#: The identity of the mutation gateway this module realises.
GATEWAY_ID = "UCOS-CMG-EXEC-000001"

#: Versioned so stages can be *appended* without any prior mutation record changing.
GATEWAY_VERSION = "1.0.0"


@dataclass(frozen=True, slots=True)
class Mutation:
    """A proposed change to repository truth, before it has earned the right to apply."""

    records: tuple[ConstitutionalMetadata, ...]
    authority: str = ""
    reason: str = ""

    def creates(self, population: Population) -> tuple[ConstitutionalMetadata, ...]:
        """The records introducing a subject the population has never declared."""
        return tuple(record for record in self.records if record.subject not in population)

    def amends(self, population: Population) -> tuple[ConstitutionalMetadata, ...]:
        """The records superseding a subject the population already declares."""
        return tuple(record for record in self.records if record.subject in population)

    def to_dict(self) -> dict[str, Any]:
        return {
            "authority": self.authority,
            "reason": self.reason,
            "subjects": [record.subject for record in self.records],
            "records": [record.to_dict() for record in self.records],
        }

    def digest(self) -> str:
        return content_hash(self.to_dict())


@dataclass(frozen=True, slots=True)
class Context:
    """What a stage may read: the committed state, the candidate state, the mutation."""

    base: Population
    candidate: Population
    mutation: Mutation


#: A stage function: given the context, return ``(satisfied, detail)``. Pure — a stage
#: reads no clock, no filesystem and no network, so a mutation record replays identically.
StageFunction = Callable[[Context], "tuple[bool, str]"]


@dataclass(frozen=True, slots=True)
class Stage:
    """One stage of the mutation pipeline."""

    name: str
    statement: str
    run: StageFunction
    depends_on: tuple[str, ...] = ()

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "statement": self.statement,
            "depends_on": list(self.depends_on),
        }


# --------------------------------------------------------------------------- #
# The seven stages                                                             #
# --------------------------------------------------------------------------- #


def _proposal(context: Context) -> tuple[bool, str]:
    """The mutation is well-formed and every record carries complete metadata."""
    if not context.mutation.records:
        return False, "a mutation must carry at least one record"
    if not context.mutation.authority.strip():
        return False, "a mutation must name the authority it acts under"
    incomplete = sorted(
        record.subject for record in context.mutation.records if not record.complete
    )
    if incomplete:
        return False, f"records with incomplete metadata: {', '.join(incomplete)}"
    return True, f"{len(context.mutation.records)} record(s) proposed"


def _evidence(context: Context) -> tuple[bool, str]:
    """Nothing being created duplicates canonical truth (CEL-08, at the point of entry).

    Run over creations only. An amendment *should* find its own subject already declared —
    that is what makes it an amendment — so putting it through the artifact search would
    make supersession impossible and force every correction to be a new subject, which is
    the duplication this gate exists to prevent.
    """
    for record in context.mutation.creates(context.base):
        verdict = assimilation_gate.assimilate(assimilation_gate.proposal_for(record), context.base)
        if not verdict.creatable:
            return False, (
                f"{record.subject} duplicates canonical truth; "
                f"extend {', '.join(verdict.reuse_targets)} instead"
            )
    duplicates = assimilation_gate.duplicate_capabilities(context.candidate)
    if duplicates:
        rendered = "; ".join(
            f"{output} produced by {', '.join(subjects)}" for output, subjects in duplicates.items()
        )
        return False, f"the resulting state would hold duplicate capabilities: {rendered}"
    return True, "no canonical truth is duplicated"


def _validation(context: Context) -> tuple[bool, str]:
    """The resulting graph resolves and is acyclic."""
    graph = dependency_graph.build(context.candidate)
    unknown = graph.unknown_referents()
    if unknown:
        rendered = ", ".join(f"{e.source}→{e.target} ({e.relation})" for e in unknown)
        return False, f"declarations name subjects that do not exist: {rendered}"
    for relation in graph.relations:
        if cycles := graph.cycles(relation):
            return False, f"cycle in {relation!r} among: {', '.join(cycles)}"
    return True, "the resulting graph resolves and is acyclic"


def _verification(context: Context) -> tuple[bool, str]:
    """Every mutated subject proves legality, and no subject attests to itself."""
    graph = dependency_graph.build(context.candidate)
    authority_report = authority_graph.analyse(context.candidate, graph)
    if not authority_report.passed:
        rendered = "; ".join(f.detail for f in authority_report.findings)
        return False, f"authority breaches: {rendered}"
    for record in context.mutation.records:
        verdict = legality_engine.prove(
            context.candidate.get(record.subject), graph, context.candidate
        )
        if not verdict.legal:
            return False, f"{record.subject} unproven: {', '.join(verdict.unproven)}"
    return True, f"{len(context.mutation.records)} record(s) proved legality"


def _certification(context: Context) -> tuple[bool, str]:
    """The resulting state yields an executable plan — the whole state, not only the diff.

    Certifying only the mutated subjects would certify a change that breaks something it
    never mentioned. The unit of certification is therefore the state a mutation produces.
    """
    derived = execution_planner.plan(context.candidate)
    if not derived.executable:
        return False, f"the resulting state is not executable: {'; '.join(derived.refusals)}"
    return True, f"plan of {len(derived.order)} subject(s) certified"


def _registration(context: Context) -> tuple[bool, str]:
    """Every mutated record is identified and registered."""
    for record in context.mutation.records:
        if not is_well_formed(record.universal_id):
            return False, (
                f"{record.subject} carries no identifier the identity authority could mint"
            )
        if not record.entries("registrations"):
            return False, f"{record.subject} names no registry"
    return True, f"{len(context.mutation.records)} record(s) registered"


def _truth_update(context: Context) -> tuple[bool, str]:
    """The resulting state settles to a deterministic fixed point (CEL-06)."""
    record = replay_engine.converge(context.candidate)
    if not record.fixed_point:
        return False, (
            "the resulting state did not settle; divergent acts: "
            f"{', '.join(record.divergent_acts()) or 'unknown'}"
        )
    return True, f"fixed point at round {record.converged_at}"


#: The pipeline (DATA — extend by appending). Each stage declares the one before it, and
#: the run order is *derived* from those declarations rather than from this tuple's order.
PIPELINE: tuple[Stage, ...] = (
    Stage("proposal", "the mutation is well-formed and completely declared", _proposal),
    Stage(
        "evidence",
        "nothing being created duplicates canonical truth",
        _evidence,
        depends_on=("proposal",),
    ),
    Stage(
        "validation",
        "the resulting graph resolves and is acyclic",
        _validation,
        depends_on=("evidence",),
    ),
    Stage(
        "verification",
        "every mutated subject proves legality under an independent authority",
        _verification,
        depends_on=("validation",),
    ),
    Stage(
        "certification",
        "the resulting state yields an executable plan",
        _certification,
        depends_on=("verification",),
    ),
    Stage(
        "registration",
        "every mutated record is identified and registered",
        _registration,
        depends_on=("certification",),
    ),
    Stage(
        "truth_update",
        "the resulting state settles to a deterministic fixed point",
        _truth_update,
        depends_on=("registration",),
    ),
)


def pipeline_order(
    stages: Sequence[Stage] = PIPELINE, *, strategy: str = DEFAULT_STRATEGY
) -> tuple[str, ...]:
    """The derived run order of the pipeline.

    Derived, not read off :data:`PIPELINE`, and through the same ordering authority every
    other consumer uses — so the gateway is subject to CEL-02 like everything else rather
    than being the one place a sequence is hardcoded.
    """
    graph = {stage.name: stage.depends_on for stage in stages}
    ordering = derive_order(graph, strategy=strategy)
    if unresolved := unresolved_keys(graph, ordering):
        raise ConstitutionalError(
            "the mutation pipeline declares a cycle; no order exists",
            gateway_id=GATEWAY_ID,
            unresolved=unresolved,
        )
    return tuple(name for _wave, name in ordering)


@dataclass(frozen=True, slots=True)
class StageOutcome:
    """The journalled record of one stage having run."""

    name: str
    satisfied: bool
    statement: str
    detail: str
    prev_hash: str = ""
    entry_hash: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "satisfied": self.satisfied,
            "statement": self.statement,
            "detail": self.detail,
            "prev_hash": self.prev_hash,
            "entry_hash": self.entry_hash,
        }


def _entry_hash(outcome: StageOutcome, prev_hash: str) -> str:
    """The hash-chained digest of one stage entry (tamper-evident journal)."""
    return content_hash(
        {
            "name": outcome.name,
            "satisfied": outcome.satisfied,
            "detail": outcome.detail,
            "prev_hash": prev_hash,
        }
    )


@dataclass(frozen=True, slots=True)
class MutationRecord:
    """The complete, replayable record of one mutation attempt."""

    gateway_id: str
    mutation: Mutation
    outcomes: tuple[StageOutcome, ...]
    order: tuple[str, ...]
    applied: bool
    population: Population
    seal: state_engine.StateSeal | None = None
    replay: replay_engine.ReplayRecord | None = None
    scope: Mapping[str, Any] = field(default_factory=dict)

    @property
    def refused_at(self) -> str:
        """The stage that refused the mutation, or the empty string when it applied."""
        for outcome in self.outcomes:
            if not outcome.satisfied:
                return outcome.name
        return ""

    @property
    def status(self) -> str:
        return "APPLIED" if self.applied else "REFUSED"

    @property
    def chain_head(self) -> str:
        return self.outcomes[-1].entry_hash if self.outcomes else ""

    def chain_is_intact(self) -> bool:
        """True iff every journal entry's digest reproduces from its own content."""
        previous = ""
        for outcome in self.outcomes:
            if outcome.prev_hash != previous or outcome.entry_hash != _entry_hash(
                outcome, previous
            ):
                return False
            previous = outcome.entry_hash
        return True

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema": "ucos-constitutional-mutation",
            "version": GATEWAY_VERSION,
            "gateway_id": self.gateway_id,
            "status": self.status,
            "applied": self.applied,
            "refused_at": self.refused_at,
            "order": list(self.order),
            "mutation": self.mutation.to_dict(),
            "outcomes": [o.to_dict() for o in self.outcomes],
            "chain_head": self.chain_head,
            "chain_intact": self.chain_is_intact(),
            "population_digest": self.population.digest(),
            "seal": self.seal.to_dict() if self.seal else None,
            "replay": self.replay.to_dict() if self.replay else None,
            "scope": {k: self.scope[k] for k in sorted(self.scope)},
        }

    def digest(self) -> str:
        return content_hash(self.to_dict())


def propose(
    population: Population,
    mutation: Mutation,
    *,
    stages: Sequence[Stage] = PIPELINE,
    strategy: str = DEFAULT_STRATEGY,
) -> MutationRecord:
    """Run ``mutation`` through the whole pipeline and return the record.

    The candidate state is built once, up front, and every stage judges *that* — so a
    stage cannot see a state a later stage will not. Stages run under an open mutation
    seal, which is why no stage can certify or register the half-built state it is
    examining: :mod:`engine.constitution.state` refuses a dirty seal.

    The pipeline stops at the first refusal. A stage after a failed one would be judging a
    state that was never going to exist, and recording its verdict as though it counted is
    how a partial mutation acquires the appearance of progress.

    Returns the record whether or not it applied; :func:`apply` is the fail-closed form.
    """
    order = pipeline_order(stages, strategy=strategy)
    by_name = {stage.name: stage for stage in stages}
    candidate = population.with_records(mutation.records)
    context = Context(base=population, candidate=candidate, mutation=mutation)

    outcomes: list[StageOutcome] = []
    previous = ""
    satisfied_all = True
    with state_engine.mutating(population):
        for name in order:
            stage = by_name[name]
            try:
                satisfied, detail = stage.run(context)
            except Exception as exc:  # noqa: BLE001 - an unevaluable stage is a failed stage
                satisfied, detail = False, f"stage could not be evaluated: {exc}"
            outcome = StageOutcome(
                name=stage.name,
                satisfied=bool(satisfied),
                statement=stage.statement,
                detail=str(detail),
                prev_hash=previous,
            )
            entry = _entry_hash(outcome, previous)
            outcomes.append(
                StageOutcome(
                    name=outcome.name,
                    satisfied=outcome.satisfied,
                    statement=outcome.statement,
                    detail=outcome.detail,
                    prev_hash=previous,
                    entry_hash=entry,
                )
            )
            previous = entry
            if not outcome.satisfied:
                satisfied_all = False
                break

    if not satisfied_all:
        # The base population is returned unchanged. A refused mutation leaves no trace in
        # repository truth — only in this record, which is where a refusal belongs.
        return MutationRecord(
            gateway_id=GATEWAY_ID,
            mutation=mutation,
            outcomes=tuple(outcomes),
            order=order,
            applied=False,
            population=population,
            scope={"base_digest": population.digest()},
        )

    settled = replay_engine.require_fixed_point(candidate)
    seal = state_engine.commit(
        candidate,
        gateway_id=GATEWAY_ID,
        mutation_digest=mutation.digest(),
        replay_digest=settled.digest(),
    )
    return MutationRecord(
        gateway_id=GATEWAY_ID,
        mutation=mutation,
        outcomes=tuple(outcomes),
        order=order,
        applied=True,
        population=candidate,
        seal=seal,
        replay=settled,
        scope={"base_digest": population.digest(), "result_digest": candidate.digest()},
    )


def apply(
    population: Population,
    mutation: Mutation,
    *,
    stages: Sequence[Stage] = PIPELINE,
    strategy: str = DEFAULT_STRATEGY,
) -> tuple[Population, MutationRecord]:
    """Apply ``mutation``, or refuse it — the fail-closed entry point.

    Returns the new population and the record that earned it. The returned population is
    the only one in this package carrying a clean seal, and so the only one that may
    subsequently be verified, certified, registered, measured or governed.

    Raises:
        MutationRefused: a stage did not discharge; the stage and its detail are named.
    """
    record = propose(population, mutation, stages=stages, strategy=strategy)
    if not record.applied:
        raise MutationRefused(
            "mutation refused: the gateway pipeline did not complete",
            gateway_id=GATEWAY_ID,
            clause="CEL-04",
            refused_at=record.refused_at,
            outcomes=[o.to_dict() for o in record.outcomes if not o.satisfied],
        )
    return record.population, record


def to_document() -> dict[str, Any]:
    """The pipeline as a deterministic, machine-readable document."""
    return {
        "schema": "ucos-constitutional-mutation-gateway",
        "version": GATEWAY_VERSION,
        "gateway_id": GATEWAY_ID,
        "stages": [s.to_dict() for s in PIPELINE],
        "order": list(pipeline_order()),
        "direct_mutation": "impossible: no other producer of a clean state seal exists",
        "closed_set": False,
    }


def digest() -> str:
    return content_hash(to_document())


__all__ = [
    "GATEWAY_ID",
    "GATEWAY_VERSION",
    "PIPELINE",
    "Context",
    "Mutation",
    "MutationRecord",
    "Stage",
    "StageFunction",
    "StageOutcome",
    "apply",
    "digest",
    "pipeline_order",
    "propose",
    "to_document",
]
