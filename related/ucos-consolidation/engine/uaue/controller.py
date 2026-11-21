"""UAUE — the autonomous evolution controller (UAUE-000001, Epoch 4).

The exit criterion AUE-EXIT-12 states the whole obligation of this module: *the controller
traverses every phase for every candidate with no phase-specific or subject-specific branch*. It
is not a position of the loop and claims none — the eleven declared positions each have an owner
already, and a twelfth would be this module legislating itself into the cycle it conducts.

Epoch 3 built eleven deterministic functions. Each one answers its own question well and none of
them knows the loop exists: understanding does not know that planning follows it, and validation
does not know that its own verdict is a field its subject must carry. Something has to carry a
candidate from the first to the last, decide when a precondition is unmet, and settle the one
interdependence the declaration writes into itself. That is this module, and it is the only thing
this module does.

**It conducts; it does not decide.** Not one measurement is taken here. Discovery, understanding,
planning, evaluation, authorisation, measurement, validation, verification, certification and the
history projection are all owned by the modules of Epoch 3, and every one of them is called, none
is reimplemented. A controller that re-measured anything would be a second opinion on a subject
that already has an owner, which is the failure this programme exists to detect.

**It knows nothing about its subject.** There is no branch on a subject, a class, a source, an
owner, a domain or a model of reality anywhere in the traversal: the loop is driven by declared
position, the artifacts are produced by the phase modules, and the verdicts are measured against
the declared criteria. That is why the declared unknown probe traverses the identical code path as
a candidate read from a sealed artifact, and why a candidate class introduced tomorrow needs no
change here. The positions below are the same positions each phase module already declares
privately; they are the loop's shape, not a fact about anything it carries.

**It performs no mutation.** The authorisation phase reports whether the single declared mutation
path resolves behind its gate. This module records that report, records that no mutation was
performed, and refuses the run if the two are ever confused — an authorisation is not an effect,
and a conductor that treated it as one would be the second mutation path the declaration forbids.

**It fails closed and it fails attributably.** A candidate that cannot be identified or evidenced
is refused at admission, before a run exists, because there would be nothing to attribute a
refusal to. Everything after admission halts the traversal at the position whose precondition is
unmet and names the reason on the run, because at that point there *is* an identified run to
attribute it to, and a silent short chain is indistinguishable from a complete one.
"""

from __future__ import annotations

from collections.abc import Callable, Iterable, Sequence
from dataclasses import dataclass, field
from typing import Any

from engine.uaue.authority import load_evolution_authority
from engine.uaue.certification import certification_object, certify_evolution
from engine.uaue.discovery import DiscoveryReport, discover_evolution_candidates
from engine.uaue.execution import execute_evolution
from engine.uaue.history import (
    learning_object,
    project_history,
    state_transition_object,
)
from engine.uaue.model import EvolutionAuthority, EvolutionAuthorityError
from engine.uaue.objects import (
    EvolutionCandidate,
    EvolutionChain,
    EvolutionExecution,
    EvolutionObject,
    EvolutionObservation,
    EvolutionPlan,
    EvolutionSimulation,
    EvolutionUnderstanding,
    Verdict,
)
from engine.uaue.observation import observe_evolution
from engine.uaue.planning import create_evolution_plan
from engine.uaue.resolution import DeclarationReader, Substrate
from engine.uaue.simulation import simulate_evolution
from engine.uaue.understanding import understand_evolution
from engine.uaue.validation import validate_evolution, validation_object
from engine.uaue.verification import verification_object, verify_evolution
from engine.uckp.canonical import content_hash

#: The declared positions of the loop, in declared order. Positions rather than identifiers, for
#: the reason every phase module of Epoch 3 already uses positions: an identifier written here
#: would be this module holding a copy of a name the declaration owns, and a renamed phase would
#: then silently stop being conducted. The authority resolves each position to its phase, its
#: object kind, its lifecycle state, its owners, its gate and its dependencies.
(
    _ADMIT,
    _COMPREHEND,
    _COMPOSE,
    _EVALUATE,
    _AUTHORISE,
    _MEASURE,
    _VALIDATE,
    _VERIFY,
    _CERTIFY,
    _ASSIMILATE,
    _TRANSITION,
) = range(1, 12)

#: The deterministic ceiling on settlement rounds. The settlement below is idempotent once the
#: verdicts stop changing, so a stable state is normally reached in three rounds; the ceiling
#: exists so that a declaration whose criteria could never settle terminates with an unsettled
#: verdict instead of spinning. A bound that is never reached is still the reason there is no
#: unbounded loop.
MAX_SETTLEMENT_ROUNDS = 8


class EvolutionRefused(EvolutionAuthorityError):
    """A candidate cannot be admitted, so no run may be started for it.

    Raised only at admission. After admission a refusal is *recorded on the run* rather than
    raised, because an identified run can carry its own refusal and a caller can then read why a
    traversal stopped; an unidentifiable candidate has nothing to carry one.
    """

    code = "UAUE-CONTROLLER-001"


@dataclass(frozen=True, slots=True)
class EvolutionContext:
    """Everything one traversal is conducted against. Passed in; never read from anywhere else.

    There is no module-level state in this file and no default context is cached, so two runs
    cannot influence each other and a caller can conduct a traversal against a substrate of its
    own choosing without disturbing anyone else's.

    The policies are the declared criteria a run must satisfy to be considered settled. They are
    *derived* from the authority by :meth:`resolve` — the blocking criteria of the declaration's own
    validation, verification and certification blocks — and never authored. A policy this class
    invented would be a second criteria authority, and a policy that could waive one would make the
    verdict the caller's rather than the declaration's.
    """

    authority: EvolutionAuthority
    substrate: Substrate
    observer: str
    evidence_source: DeclarationReader
    execution_permissions: tuple[str, ...]
    validation_policy: tuple[str, ...]
    certification_policy: tuple[str, ...]
    verification_policy: tuple[str, ...]
    max_settlement_rounds: int = MAX_SETTLEMENT_ROUNDS

    @classmethod
    def resolve(
        cls,
        authority: EvolutionAuthority | None = None,
        substrate: Substrate | None = None,
        reader: DeclarationReader | None = None,
        *,
        max_settlement_rounds: int = MAX_SETTLEMENT_ROUNDS,
    ) -> EvolutionContext:
        """A context derived entirely from repository truth.

        Args:
            authority: the rehydrated authority. Rehydrated from the canonical declaration when
                omitted, against ``substrate`` so the two cannot describe different trees.
            substrate: the tree every declared home, evidence path and gate is measured against.
            reader: the declaration candidates and their evidence are read through.
            max_settlement_rounds: the deterministic ceiling on settlement rounds.

        Raises:
            EvolutionRefused: the ceiling is not positive, so nothing could ever be settled, or
                the declared execution position names no owner, so no execution could ever be
                authorised through a located owner.
        """
        if max_settlement_rounds < 1:
            raise EvolutionRefused(
                "a settlement ceiling below one round would leave every verdict unmeasured",
                max_settlement_rounds=max_settlement_rounds,
            )
        substrate = substrate if substrate is not None else Substrate()
        reader = reader if reader is not None else DeclarationReader.canonical()
        authority = (
            authority if authority is not None else load_evolution_authority(reader, substrate)
        )
        executor = authority.phase_by_ordinal(_AUTHORISE)
        permissions = tuple(owner.home for owner in executor.owners)
        if not permissions:
            raise EvolutionRefused(
                "the declared execution position names no owner, "
                "so no execution could be authorised through a located owner",
                phase=executor.identifier,
            )
        measurer = authority.phase_by_ordinal(_MEASURE)
        return cls(
            authority=authority,
            substrate=substrate,
            observer=measurer.owners[0].home if measurer.owners else "",
            evidence_source=reader,
            execution_permissions=permissions,
            validation_policy=tuple(
                entry.identifier for entry in authority.validations if entry.blocking
            ),
            verification_policy=tuple(
                entry.identifier for entry in authority.verifications if entry.blocking
            ),
            certification_policy=tuple(
                entry.identifier for entry in authority.certifications if entry.blocking
            ),
            max_settlement_rounds=max_settlement_rounds,
        )

    def permits(self, path: str) -> bool:
        """Whether this context permits an execution to be authorised through ``path``."""
        return bool(path) and path in self.execution_permissions

    def to_document(self) -> dict[str, Any]:
        """The context as a canonical document — the input to :meth:`digest`.

        Neither the substrate root nor the declaration's own path appears, for the reason
        :meth:`EvolutionAuthority.digest` excludes its source: the same declaration read from a
        file and from a document in memory must settle to one digest, or a replay measurement
        would only be proving that the tree was read from the same directory twice.
        """
        return {
            "authority": self.authority.digest(),
            "observer": self.observer,
            "execution_permissions": list(self.execution_permissions),
            "validation_policy": list(self.validation_policy),
            "verification_policy": list(self.verification_policy),
            "certification_policy": list(self.certification_policy),
            "max_settlement_rounds": self.max_settlement_rounds,
        }

    def digest(self) -> str:
        return content_hash(self.to_document())


@dataclass(frozen=True, slots=True)
class StageResult:
    """What one declared position of the loop produced for one candidate, and what it refused.

    Carried per position rather than aggregated, so a halted traversal names the position that
    halted it. ``refusals`` empty is the only thing that means the position was discharged.
    """

    ordinal: int
    phase: str
    object_kind: str
    lifecycle_state: str
    evolution_id: str
    digest: str
    evidence: tuple[str, ...]
    refusals: tuple[str, ...] = ()

    @property
    def discharged(self) -> bool:
        return not self.refusals

    def to_dict(self) -> dict[str, Any]:
        return {
            "ordinal": self.ordinal,
            "phase": self.phase,
            "object_kind": self.object_kind,
            "lifecycle_state": self.lifecycle_state,
            "evolution_id": self.evolution_id,
            "digest": self.digest,
            "evidence": list(self.evidence),
            "refusals": list(self.refusals),
        }


@dataclass(frozen=True, slots=True)
class EvolutionSettlement:
    """The result of settling a chain to a fixed point.

    ``rounds`` and ``digests`` are both carried because determinism is claimed about both: two
    settlements of one chain must take the same number of rounds and pass through the same
    intermediate states, not merely arrive at the same place. The digests are state digests — see
    :func:`_state_digest` for why the chain's own digest is not the quantity that can settle.
    """

    chain: EvolutionChain
    rounds: int
    digests: tuple[str, ...]
    converged: bool
    ceiling: int

    @property
    def digest(self) -> str:
        return self.digests[-1] if self.digests else ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "rounds": self.rounds,
            "digests": list(self.digests),
            "converged": self.converged,
            "ceiling": self.ceiling,
            "digest": self.digest,
        }


def _settle_once(chain: EvolutionChain, context: EvolutionContext) -> EvolutionChain:
    """One settlement round: measure, seal, measure the proofs, seal again.

    The order is forced by the declaration and is not a preference. Completeness is a mandated
    field measurement, and three of the mandated fields are verdicts, so a chain cannot be
    complete until it has been judged; but the proofs require a *measured* verdict, so they
    cannot be judged until the chain carries one. Sealing between the two measurements is what
    turns that circularity into a convergence instead of a contradiction — and sealing changes no
    identity, because no verdict is an identity input.
    """
    authority = context.authority
    substrate = context.substrate
    settled = chain.with_verdicts(
        validation=validate_evolution(chain, authority, substrate),
        verification=verify_evolution(chain, authority, substrate),
    ).sealed()
    return settled.with_verdicts(certification=certify_evolution(settled, authority)).sealed()


def _state_digest(chain: EvolutionChain) -> str:
    """The digest of the state a settlement must stabilise: the objects and their verdicts.

    Deliberately **not** :meth:`EvolutionChain.digest`, and the reason is a real property of the
    declaration rather than a convenience. One declared validation dimension reports the chain's
    own digest as its evidence, so the chain document contains a value derived from the chain
    document: each round would quote the previous round's address, and the sequence could never
    repeat a value no matter how many rounds were allowed. A fixed point over that quantity does
    not exist, so measuring it would guarantee the answer "did not settle" for a chain that had in
    fact settled.

    What must settle is the interdependence the declaration actually writes: every object's
    mandated fields, three of which are verdicts, and the verdict each object was judged under.
    That is what is digested here. The verdict *details* are evidence for a verdict, not part of
    the state being resolved — and one of them is the self-reference above.
    """
    return content_hash(
        {
            "objects": [obj.to_dict() for obj in chain.objects],
            "validation": chain.validation.summary if chain.validation else "",
            "verification": chain.verification.summary if chain.verification else "",
            "certification": chain.certification.summary if chain.certification else "",
            "passed": [
                verdict.passed if verdict else None
                for verdict in (chain.validation, chain.verification, chain.certification)
            ],
        }
    )


def resolve_evolution_state(
    chain: EvolutionChain,
    context: EvolutionContext,
    *,
    max_rounds: int | None = None,
) -> EvolutionSettlement:
    """Settle a chain's interdependent state to a fixed point, or to the declared ceiling.

    Three declared dependencies run in a cycle and none of them can be resolved first:
    completeness requires every mandated field, and three mandated fields are verdicts;
    certification requires a measured validation and verification verdict; and the readiness the
    evaluation phase reports is itself a validation question. Resolving them means iterating
    until the state stops changing.

    Args:
        chain: the chain to settle. Every declared position must already have produced its
            object; settling a short chain would settle a chain that is incomplete by
            construction, which is a refusal the caller has already recorded.
        context: the context to settle against, which supplies the ceiling.
        max_rounds: overrides the context's ceiling. A caller lowering it is asking whether the
            state settles *within* that many rounds, which is how the bound itself is measured.

    Returns:
        An :class:`EvolutionSettlement`. ``converged`` is true when a round reproduced the
        previous round's digest exactly. It is false when the ceiling was reached first, and the
        chain is then returned in its last measured state rather than discarded, because an
        unsettled state is a finding and hiding it would make it look settled.

    Raises:
        EvolutionRefused: the ceiling is not positive.
    """
    ceiling = context.max_settlement_rounds if max_rounds is None else max_rounds
    if ceiling < 1:
        raise EvolutionRefused(
            "a settlement ceiling below one round would leave every verdict unmeasured",
            ceiling=ceiling,
        )
    digests: list[str] = []
    current = chain
    converged = False
    while len(digests) < ceiling:
        current = _settle_once(current, context)
        digest = _state_digest(current)
        previous = digests[-1] if digests else ""
        digests.append(digest)
        if digest == previous:
            converged = True
            break
    return EvolutionSettlement(
        chain=current,
        rounds=len(digests),
        digests=tuple(digests),
        converged=converged,
        ceiling=ceiling,
    )


@dataclass(frozen=True, slots=True)
class EvolutionRun:
    """One conducted traversal of the loop for one candidate.

    The run is the controller's whole output and it is inert: it carries what each position
    produced, what was refused, the settled verdicts and the history projection, and it holds no
    reference to anything mutable. ``mutation_performed`` is carried beside
    ``execution_authorized`` deliberately — the declaration requires the two to be distinguishable
    by a reader, and a record that carried only the first could be misread as an effect.
    """

    run_id: str
    candidate_identity: str
    lifecycle_state: str
    stage_results: tuple[StageResult, ...]
    evidence: tuple[str, ...]
    validation: Verdict | None
    verification: Verdict | None
    certification: Verdict | None
    history: dict[str, Any]
    chain: EvolutionChain
    settlement: EvolutionSettlement | None
    execution_authorized: bool
    mutation_performed: bool
    refusals: tuple[str, ...]
    subject_identity: str
    candidate_class: str

    @property
    def halted(self) -> bool:
        """Whether the traversal stopped before every declared position was discharged."""
        return any(not entry.discharged for entry in self.stage_results)

    @property
    def halted_at(self) -> str:
        for entry in self.stage_results:
            if not entry.discharged:
                return entry.phase
        return ""

    @property
    def certified(self) -> bool:
        """Whether every declared obligation the policies name was satisfied.

        Deliberately conjunctive and deliberately unforgiving: a halted traversal, an unsettled
        state, a missing verdict, an unauthorised execution and an unmet blocking criterion all
        produce the same answer, because a run that is certified on any of them would be a
        certificate over something nobody measured.
        """
        return not self.refusals and self.settlement is not None and self.settlement.converged

    def verdict(self) -> str:
        state = "CERTIFIED" if self.certified else "REFUSED"
        return f"{state} {self.run_id[:12]} {self.candidate_identity}"

    def to_document(self) -> dict[str, Any]:
        return {
            "run_id": self.run_id,
            "candidate_identity": self.candidate_identity,
            "subject_identity": self.subject_identity,
            "candidate_class": self.candidate_class,
            "lifecycle_state": self.lifecycle_state,
            "stage_results": [entry.to_dict() for entry in self.stage_results],
            "evidence": list(self.evidence),
            "validation": self.validation.to_dict() if self.validation else None,
            "verification": self.verification.to_dict() if self.verification else None,
            "certification": self.certification.to_dict() if self.certification else None,
            "settlement": self.settlement.to_dict() if self.settlement else None,
            "execution_authorized": self.execution_authorized,
            "mutation_performed": self.mutation_performed,
            "refusals": list(self.refusals),
            "certified": self.certified,
            "chain": self.chain.to_dict(),
            "history": self.history,
        }

    def digest(self) -> str:
        """The content-addressed digest of the run — the subject of the replay measurement."""
        return content_hash(self.to_document())

    def to_dict(self) -> dict[str, Any]:
        return {**self.to_document(), "digest": self.digest()}


@dataclass(slots=True)
class _Traversal:
    """The mutable state of one traversal in progress. Private, local, and never shared."""

    context: EvolutionContext
    candidate: EvolutionCandidate
    objects: list[EvolutionObject] = field(default_factory=list)
    stages: list[StageResult] = field(default_factory=list)
    refusals: list[str] = field(default_factory=list)
    understanding: EvolutionUnderstanding | None = None
    plan: EvolutionPlan | None = None
    simulation: EvolutionSimulation | None = None
    execution: EvolutionExecution | None = None
    observation: EvolutionObservation | None = None
    validation: Verdict | None = None
    verification: Verdict | None = None
    certification: Verdict | None = None
    halted: bool = False

    @property
    def authority(self) -> EvolutionAuthority:
        return self.context.authority

    @property
    def substrate(self) -> Substrate:
        return self.context.substrate

    def record(self, ordinal: int, obj: EvolutionObject, refusals: Sequence[str] = ()) -> None:
        """Record what one position produced, and any reason it did not discharge."""
        self.objects.append(obj)
        self.stages.append(
            StageResult(
                ordinal=ordinal,
                phase=obj.phase,
                object_kind=obj.object_kind,
                lifecycle_state=obj.lifecycle_state,
                evolution_id=obj.evolution_id,
                digest=obj.digest(),
                evidence=obj.evidence,
                refusals=tuple(refusals),
            )
        )
        if refusals:
            self.refusals.extend(refusals)
            self.halted = True

    def halt(self, ordinal: int, refusals: Sequence[str]) -> None:
        """Record a position that produced nothing at all, and stop the traversal.

        A position with no object still gets a stage result, because a traversal that simply
        stopped listing positions would be indistinguishable from one that never reached them.
        """
        phase = self.authority.phase_by_ordinal(ordinal)
        self.stages.append(
            StageResult(
                ordinal=ordinal,
                phase=phase.identifier,
                object_kind="",
                lifecycle_state="",
                evolution_id="",
                digest="",
                evidence=(),
                refusals=tuple(refusals),
            )
        )
        self.refusals.extend(refusals)
        self.halted = True

    def chain(self) -> EvolutionChain:
        return EvolutionChain(
            candidate=self.candidate,
            objects=tuple(self.objects),
            understanding=self.understanding,
            plan=self.plan,
            simulation=self.simulation,
            execution=self.execution,
            observation=self.observation,
            validation=self.validation,
            verification=self.verification,
            certification=self.certification,
        )


def _admitted_object(traversal: _Traversal) -> None:
    """The head of the chain: the object of the position that admits the candidate.

    Derived here because there is no prior object for :func:`~engine.uaue.objects.phase_object` to
    continue from — this is the only position of the loop with no predecessor. Everything else
    about it, including its evidence, comes from the candidate the discovering owner produced.
    """
    authority = traversal.authority
    phase = authority.phase_by_ordinal(_ADMIT)
    traversal.record(
        _ADMIT,
        EvolutionObject.derive(
            rule=authority.identity,
            candidate=traversal.candidate,
            object_kind=authority.object_kind_of(phase.identifier).identifier,
            phase=phase.identifier,
            lifecycle_state=authority.stage_of(phase.identifier),
            dependencies=authority.dependencies_of(phase.identifier),
            evidence=traversal.candidate.evidence,
            authority=phase.authority,
        ),
    )


def _comprehend(traversal: _Traversal) -> None:
    understanding = understand_evolution(
        traversal.candidate, traversal.authority, traversal.substrate
    )
    traversal.understanding = understanding
    traversal.record(_COMPREHEND, understanding.obj)


def _compose(traversal: _Traversal) -> None:
    if traversal.understanding is None:  # pragma: no cover — the order forbids it
        traversal.halt(_COMPOSE, ("nothing was understood, so nothing can be composed",))
        return
    plan = create_evolution_plan(traversal.understanding, traversal.authority)
    traversal.plan = plan
    traversal.record(_COMPOSE, plan.obj)


def _evaluate(traversal: _Traversal) -> None:
    """Evaluate the composed plan. Reports; does not refuse.

    The evaluation yields a report — expected impact, dependency effects, potential
    failures, readiness and whether replay over the candidate state settles. Whether that report
    is *sufficient* to authorise anything is the authorisation position's question, and asking it
    twice is how two answers to one question come to exist. So every condition this position could
    have refused on is carried on the report and refused once, below.
    """
    if traversal.plan is None:  # pragma: no cover — the order forbids it
        traversal.halt(_EVALUATE, ("nothing was composed, so nothing can be evaluated",))
        return
    simulation = simulate_evolution(traversal.plan, traversal.authority, traversal.substrate)
    traversal.simulation = simulation
    traversal.record(_EVALUATE, simulation.obj)


def _authorise(traversal: _Traversal) -> None:
    """Authorise the evaluated plan through the single declared path. Never perform it.

    This is the one position where the loop can stop for a reason the subject brought with it, and
    every such reason is named here rather than spread across the positions that noticed it: a plan
    whose evaluation left a dependency unresolved, that did not settle, or whose criteria are not
    measurable has an unknown effect, and an execution with an unknown effect is exactly what
    "controlled execution" excludes. A path this context does not permit is refused too — a
    permission nobody granted is not a permission. The position's own seven preconditions are
    measured by its owner and carried through here rather than restated.
    """
    simulation = traversal.simulation
    if simulation is None:  # pragma: no cover — the order forbids it
        traversal.halt(_AUTHORISE, ("nothing was evaluated, so nothing can be authorised",))
        return
    if not simulation.executable:
        reasons = [
            f"a declared dependency does not resolve: {name}"
            for name in simulation.unresolved_dependencies
        ]
        if not simulation.fixed_point:
            reasons.append("the evaluation did not settle over the candidate state")
        if not simulation.validation_ready:
            reasons.append("the declared criteria are not measurable, so readiness is unproven")
        traversal.halt(
            _AUTHORISE,
            tuple(f"the evaluation did not authorise an execution: {reason}" for reason in reasons),
        )
        return
    execution = execute_evolution(simulation, traversal.authority, traversal.substrate)
    traversal.execution = execution
    refusals = list(execution.refusals)
    if not traversal.context.permits(execution.mutation_path):
        refusals.append(
            "this context grants no permission over the declared execution path: "
            f"{execution.mutation_path or '<none declared>'}"
        )
    if execution.mutation_performed:
        refusals.append(
            "the authorisation record claims a mutation was performed, "
            "which this controller never does and never permits"
        )
    traversal.record(_AUTHORISE, execution.obj, refusals)


def _measure(traversal: _Traversal) -> None:
    if traversal.execution is None:  # pragma: no cover — the order forbids it
        traversal.halt(_MEASURE, ("nothing was authorised, so nothing can be measured",))
        return
    observation = observe_evolution(traversal.execution, traversal.authority, traversal.substrate)
    traversal.observation = observation
    traversal.record(_MEASURE, observation.obj)


def _validate(traversal: _Traversal) -> None:
    chain = traversal.chain()
    verdict = validate_evolution(chain, traversal.authority, traversal.substrate)
    traversal.validation = verdict
    traversal.record(_VALIDATE, validation_object(chain, verdict, traversal.authority))


def _verify(traversal: _Traversal) -> None:
    chain = traversal.chain()
    verdict = verify_evolution(chain, traversal.authority, traversal.substrate)
    traversal.verification = verdict
    traversal.record(_VERIFY, verification_object(chain, verdict, traversal.authority))


def _certify(traversal: _Traversal) -> None:
    chain = traversal.chain()
    verdict = certify_evolution(chain, traversal.authority)
    traversal.certification = verdict
    traversal.record(_CERTIFY, certification_object(chain, verdict, traversal.authority))


def _assimilate(traversal: _Traversal) -> None:
    traversal.record(_ASSIMILATE, learning_object(traversal.chain(), traversal.authority))


def _transition(traversal: _Traversal) -> None:
    traversal.record(_TRANSITION, state_transition_object(traversal.chain(), traversal.authority))


#: The loop, as a sequence of declared positions and the owner that discharges each. A table
#: rather than eleven inline calls, so the traversal is one loop with no branch in it: the shape
#: of a run is therefore the same for every candidate by construction rather than by inspection.
_LOOP: tuple[tuple[int, Callable[[_Traversal], None]], ...] = (
    (_ADMIT, _admitted_object),
    (_COMPREHEND, _comprehend),
    (_COMPOSE, _compose),
    (_EVALUATE, _evaluate),
    (_AUTHORISE, _authorise),
    (_MEASURE, _measure),
    (_VALIDATE, _validate),
    (_VERIFY, _verify),
    (_CERTIFY, _certify),
    (_ASSIMILATE, _assimilate),
    (_TRANSITION, _transition),
)


class EvolutionController:
    """The single orchestration authority over one traversal of the loop.

    Holds a context and nothing else: no cache, no ledger, no registry and no accumulated state
    between runs. Two controllers over one context conduct identical runs, and one controller
    conducting the same candidate twice produces two runs with one digest — which is the property
    the replay measurement rests on and would be impossible if anything were remembered here.
    """

    __slots__ = ("_context",)

    def __init__(self, context: EvolutionContext) -> None:
        self._context = context

    @classmethod
    def canonical(
        cls, substrate: Substrate | None = None, reader: DeclarationReader | None = None
    ) -> EvolutionController:
        """A controller over the canonical declaration and the tree this package lives in."""
        return cls(EvolutionContext.resolve(substrate=substrate, reader=reader))

    @property
    def context(self) -> EvolutionContext:
        return self._context

    @property
    def authority(self) -> EvolutionAuthority:
        return self._context.authority

    def discover(self) -> DiscoveryReport:
        """Every candidate the declared sources yield. Delegated in full to their owner."""
        return discover_evolution_candidates(
            self._context.authority, self._context.substrate, self._context.evidence_source
        )

    def admit(self, candidate: EvolutionCandidate) -> None:
        """Measure that a candidate may enter the loop at all.

        Raises:
            EvolutionRefused: the candidate is anonymous, names no subject, or carries no evidence
                that resolves. Each is a refusal rather than a recorded finding because a run
                identity is derived from the candidate's own identity: there would be no run to
                attribute the finding to, and a run identified by an empty string would collide
                with every other unidentifiable candidate.
        """
        if not candidate.evolution_id:
            raise EvolutionRefused(
                "an anonymous candidate cannot enter the loop",
                subject=candidate.subject_identity,
            )
        if not candidate.subject_identity.strip():
            raise EvolutionRefused(
                "a candidate naming no subject cannot enter the loop",
                candidate=candidate.evolution_id,
            )
        resolving = tuple(
            path for path in candidate.evidence if self._context.substrate.resolves(path)
        )
        if not resolving:
            raise EvolutionRefused(
                "a candidate with no resolving evidence cannot enter the loop",
                candidate=candidate.evolution_id,
                subject=candidate.subject_identity,
                declared=list(candidate.evidence),
            )

    def run(self, candidate: EvolutionCandidate, *, cycle: int = 0) -> EvolutionRun:
        """Conduct one candidate through every declared position of the loop.

        Args:
            candidate: the candidate to conduct. Any candidate: nothing about its class, source,
                owner or subject changes what happens to it.
            cycle: the ledger cycle this traversal occupies in the history projection. One
                traversal is one cycle.

        Returns:
            An :class:`EvolutionRun`. A refused traversal returns a run whose ``refusals`` name
            every unmet obligation and whose ``certified`` is false; it does not raise, because a
            refusal a caller cannot read is a refusal that will be mistaken for an absence.

        Raises:
            EvolutionRefused: the candidate could not be admitted.
        """
        self.admit(candidate)
        context = self._context
        traversal = _Traversal(context=context, candidate=candidate)

        for ordinal, discharge in _LOOP:
            if traversal.halted:
                break
            try:
                discharge(traversal)
            except EvolutionAuthorityError as error:
                # An owner refused. Recorded against the position that called it rather than
                # raised, so the run still names which obligation stopped it and under whose
                # authority — an exception escaping here would lose both.
                traversal.halt(ordinal, (f"{error}",))

        settlement: EvolutionSettlement | None = None
        chain = traversal.chain()
        if not traversal.halted:
            settlement = resolve_evolution_state(chain, context)
            chain = settlement.chain
            if not settlement.converged:
                traversal.refusals.append(
                    "the evolution state did not settle within the declared ceiling of "
                    f"{settlement.ceiling} rounds"
                )

        refusals = list(traversal.refusals)
        refusals.extend(_policy_refusals(chain, context))
        execution = chain.execution
        authorised = execution is not None and execution.authorised
        performed = execution.mutation_performed if execution is not None else False
        if performed:
            refusals.append("a mutation was recorded, which this controller never performs")

        history: dict[str, Any] = {}
        if not traversal.halted:
            try:
                history = project_history(chain, context.authority)
            except EvolutionAuthorityError as error:
                refusals.append(f"the history could not be projected: {error}")

        return EvolutionRun(
            run_id=_run_identity(candidate, context, cycle),
            candidate_identity=candidate.evolution_id,
            subject_identity=candidate.subject_identity,
            candidate_class=candidate.candidate_class,
            lifecycle_state=(traversal.objects[-1].lifecycle_state if traversal.objects else ""),
            stage_results=tuple(traversal.stages),
            evidence=tuple(
                dict.fromkeys(
                    path
                    for obj in chain.objects
                    for path in obj.evidence
                    if context.substrate.resolves(path)
                )
            ),
            validation=chain.validation,
            verification=chain.verification,
            certification=chain.certification,
            history=history,
            chain=chain,
            settlement=settlement,
            execution_authorized=authorised,
            mutation_performed=performed,
            refusals=tuple(refusals),
        )

    def run_all(
        self, candidates: Iterable[EvolutionCandidate] | None = None
    ) -> tuple[EvolutionRun, ...]:
        """Conduct every candidate, one ledger cycle each, in the order they were discovered.

        Order is the discovering owners' declared order and is never sorted by class, severity or
        subject: a controller that chose what to conduct first would be deciding which evolution
        matters, which is a judgement no owner delegated to it.
        """
        subjects = (
            tuple(candidates) if candidates is not None else tuple(self.discover().candidates)
        )
        return tuple(self.run(candidate, cycle=cycle) for cycle, candidate in enumerate(subjects))

    def project_history(self, runs: Sequence[EvolutionRun]) -> dict[str, Any]:
        """The canonical history projection over every complete run, one cycle per run.

        Delegated to the projection owner, which appends through the canonical append-only ledger,
        so the ordering and cycle rules are enforced by their owner rather than re-checked here.
        Halted runs are excluded: a chain that never reached a position has no object to record at
        that position, and the ledger would refuse a skipped stage — correctly.
        """
        complete = [run.chain for run in runs if not run.halted]
        return project_history(complete, self._context.authority)


def _policy_refusals(chain: EvolutionChain, context: EvolutionContext) -> tuple[str, ...]:
    """Every declared obligation the context's policies name that the chain did not satisfy.

    Measured against the *declared* criterion identifiers, so a criterion the declaration adds is
    enforced without a change here, and a criterion the declaration removes stops being enforced
    without a stale check outliving it.
    """
    refusals: list[str] = []
    for name, verdict, policy in (
        ("validation", chain.validation, context.validation_policy),
        ("verification", chain.verification, context.verification_policy),
        ("certification", chain.certification, context.certification_policy),
    ):
        if verdict is None or not verdict.outcomes:
            refusals.append(f"the run carries no measured {name} verdict")
            continue
        satisfied = {entry.identifier for entry in verdict.outcomes if entry.satisfied}
        unmet = [entry for entry in policy if entry not in satisfied]
        if unmet:
            refusals.append(f"{name} refused: {', '.join(unmet)}")
    return tuple(refusals)


def _run_identity(candidate: EvolutionCandidate, context: EvolutionContext, cycle: int) -> str:
    """The run's identity: a content address over what the run is a function of.

    A digest and not a minted identifier. Minting one would be a second identity system, and this
    programme derives identity rather than allocating it — so the run identity is the digest of
    the candidate that entered, the authority it was conducted under, the context it was conducted
    in and the cycle it occupies. Two runs of one candidate under one authority and one context
    therefore share an identity, which is what makes them comparable at all.
    """
    return content_hash(
        [candidate.evolution_id, context.authority.digest(), context.digest(), str(cycle)]
    )


__all__ = [
    "MAX_SETTLEMENT_ROUNDS",
    "EvolutionContext",
    "EvolutionController",
    "EvolutionRefused",
    "EvolutionRun",
    "EvolutionSettlement",
    "StageResult",
    "resolve_evolution_state",
]
