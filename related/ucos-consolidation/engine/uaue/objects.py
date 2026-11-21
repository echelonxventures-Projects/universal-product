"""UAUE — the evolution object model (UAUE-000001, Epoch 3).

One type carries the mandated fields: :class:`EvolutionObject`. Every phase of the loop
produces exactly one, and the mandate is enforced in exactly one place —
:meth:`EvolutionObject.derive` — rather than eleven times over in eleven phase modules. A
field mandate implemented per phase would be eleven mandates that could disagree.

The phase artifacts (:class:`EvolutionUnderstanding`, :class:`EvolutionPlan`, …) carry what is
*specific* to their phase. Each one projects into an :class:`EvolutionObject` so the chain is
uniform, which is what lets validation, verification, certification and history be written
once against the object rather than once per phase.

**Identity is derived, never minted.** :func:`derive_identity` applies the rule the declaration
declares — a prefix, a width, and a digest of the declared input fields — using the digest
owner the declaration names. No identifier literal appears in this module, no serial is
consumed, and no registry is written. Because identity is derived from meaning rather than
from arrival order, the same candidate observed twice yields the same identity and the history
does not fork.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field, replace
from typing import Any

from engine.uaue.model import EvolutionAuthorityError, IdentityRule
from engine.uckp.canonical import content_hash

#: A context is carried as an ordered tuple of pairs rather than as a mapping: it must be
#: hashable, canonically ordered and immutable, because it is a digest input.
Context = tuple[tuple[str, str], ...]


def as_context(values: Mapping[str, object] | Sequence[tuple[str, str]]) -> Context:
    """A context in canonical form: pairs sorted by key, values rendered as text."""
    items = values.items() if isinstance(values, Mapping) else values
    return tuple(sorted((str(key), str(value)) for key, value in items))


def derive_identity(rule: IdentityRule, inputs: Mapping[str, str]) -> str:
    """The identity of an evolution object, derived through the declared rule.

    Every field the rule names must be present and non-empty. An object whose identity inputs
    are incomplete is anonymous, and the declaration's anonymity rule says anonymous evolution
    is refused rather than reported — so this raises rather than returning a short digest.
    """
    missing = [name for name in rule.inputs if not str(inputs.get(name, "")).strip()]
    if missing:
        raise EvolutionAuthorityError(
            "an evolution object cannot be identified from empty identity inputs",
            missing=missing,
            rule=rule.anonymity_rule,
        )
    payload = [str(inputs[name]) for name in rule.inputs]
    return f"{rule.prefix}{content_hash(payload)[: rule.width]}"


def identity_inputs(rule: IdentityRule, obj: EvolutionObject) -> dict[str, str]:
    """The declared identity inputs, read off an object by the names the declaration uses.

    Generic on purpose. A hand-written mapping would restate the declared input list in code —
    in three modules, since derivation, validation and verification all need it — and a
    declaration that changed its inputs would then silently keep hashing the old ones. Reading
    the object's attributes by declared name means the input set has exactly one definition, and
    an input the object model does not carry is a refusal rather than an empty string.
    """
    missing = [name for name in rule.inputs if not hasattr(obj, name)]
    if missing:
        raise EvolutionAuthorityError(
            "the declaration names an identity input the object model does not carry",
            inputs=missing,
        )
    return {name: str(getattr(obj, name)) for name in rule.inputs}


@dataclass(frozen=True, slots=True)
class EvolutionCandidate:
    """An evolution opportunity, as one located owner measured it.

    Produced only by :mod:`engine.uaue.discovery`, only from an artifact another owner
    published, and never without evidence. ``source`` and ``owner`` are what make a candidate
    attributable: a candidate this engine invented would have no source to name.
    """

    evolution_id: str
    subject_identity: str
    candidate_class: str
    source: str
    owner: str
    reason: str
    previous_state: str
    target_state: str
    context: Context
    evidence: tuple[str, ...]
    dependencies: tuple[str, ...]
    severity: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "evolution_id": self.evolution_id,
            "subject_identity": self.subject_identity,
            "candidate_class": self.candidate_class,
            "source": self.source,
            "owner": self.owner,
            "reason": self.reason,
            "previous_state": self.previous_state,
            "target_state": self.target_state,
            "context": [list(pair) for pair in self.context],
            "evidence": list(self.evidence),
            "dependencies": list(self.dependencies),
            "severity": self.severity,
        }

    def digest(self) -> str:
        return content_hash(self.to_dict())

    @classmethod
    def from_object(cls, obj: EvolutionObject, *, severity: str = "") -> EvolutionCandidate:
        """The candidate view of an object already in the chain.

        Later phases derive their own object from the candidate's fields, and an object already
        carries every one of them. Reconstructing the view here means a phase function takes
        one argument instead of two that must agree — two arguments that must agree are two
        arguments that can disagree, and the disagreement would silently fork the identity.
        """
        source = dict(obj.context)
        return cls(
            evolution_id=obj.evolution_id,
            subject_identity=obj.subject_identity,
            candidate_class=obj.candidate_class,
            source=source.get("source", ""),
            owner=source.get("owner", ""),
            reason=obj.reason,
            previous_state=obj.previous_state,
            target_state=obj.target_state,
            context=obj.context,
            evidence=obj.evidence,
            dependencies=obj.dependencies,
            severity=severity or source.get("risk", ""),
        )


@dataclass(frozen=True, slots=True)
class EvolutionObject:
    """One evolution object: one phase's answer for one candidate, carrying every field.

    Constructed only through :meth:`derive`, which is the single place the identity rule and
    the field mandate are applied.
    """

    evolution_id: str
    object_kind: str
    phase: str
    lifecycle_state: str
    subject_identity: str
    candidate_class: str
    previous_state: str
    target_state: str
    reason: str
    context: Context
    dependencies: tuple[str, ...]
    evidence: tuple[str, ...]
    plan: str
    execution_record: str
    validation_result: str
    verification_result: str
    certification_result: str
    authority: str

    @classmethod
    def derive(
        cls,
        *,
        rule: IdentityRule,
        candidate: EvolutionCandidate,
        object_kind: str,
        phase: str,
        lifecycle_state: str,
        dependencies: Sequence[str],
        evidence: Sequence[str],
        authority: str,
        plan: str = "",
        execution_record: str = "",
        validation_result: str = "",
        verification_result: str = "",
        certification_result: str = "",
        previous_state: str = "",
        target_state: str = "",
        reason: str = "",
        context: Context | None = None,
    ) -> EvolutionObject:
        """Derive one phase's object from a candidate.

        The identity is computed from the object itself, through the declared input names, so two
        phases over one candidate have distinct identities while the same candidate rediscovered
        yields the identical identity. Evidence is required: an object with no evidence is refused
        here, which is why no later phase has to check for one.
        """
        if not tuple(evidence):
            raise EvolutionAuthorityError(
                "an evolution object must carry at least one resolving evidence path",
                phase=phase,
                object_kind=object_kind,
                subject=candidate.subject_identity,
            )
        provisional = cls(
            evolution_id="",
            object_kind=object_kind,
            phase=phase,
            lifecycle_state=lifecycle_state,
            subject_identity=candidate.subject_identity,
            candidate_class=candidate.candidate_class,
            previous_state=previous_state or candidate.previous_state,
            target_state=target_state or candidate.target_state,
            reason=reason or candidate.reason,
            context=context if context is not None else candidate.context,
            dependencies=tuple(dependencies),
            evidence=tuple(evidence),
            plan=plan,
            execution_record=execution_record,
            validation_result=validation_result,
            verification_result=verification_result,
            certification_result=certification_result,
            authority=authority,
        )
        return replace(
            provisional,
            evolution_id=derive_identity(rule, identity_inputs(rule, provisional)),
        )

    def field_value(self, name: str) -> object:
        """One mandated field by its declared name, for the completeness measurement."""
        if not hasattr(self, name):
            raise EvolutionAuthorityError(
                "the declaration mandates a field the object model does not carry", field=name
            )
        return getattr(self, name)

    def with_results(
        self,
        *,
        plan: str = "",
        execution_record: str = "",
        validation_result: str = "",
        verification_result: str = "",
        certification_result: str = "",
    ) -> EvolutionObject:
        """A copy carrying the chain's plan, execution record and later verdicts.

        Returns a new object rather than mutating: an evolution object that could be edited after
        it was identified would have an identity that no longer described it.

        **The identity is unchanged, by design.** The declared identity inputs are the candidate
        class, the subject, the reason, the authority and the object kind — deliberately not the
        plan and not any verdict. That is what makes this operation lawful: the same evolution
        judged twice is the same evolution, so attaching a verdict cannot fork the history. It is
        also what makes the field mandate satisfiable at all, since a phase-one object cannot know
        a verdict that phase seven will reach, and would otherwise be permanently incomplete.
        """
        return EvolutionObject(
            evolution_id=self.evolution_id,
            object_kind=self.object_kind,
            phase=self.phase,
            lifecycle_state=self.lifecycle_state,
            subject_identity=self.subject_identity,
            candidate_class=self.candidate_class,
            previous_state=self.previous_state,
            target_state=self.target_state,
            reason=self.reason,
            context=self.context,
            dependencies=self.dependencies,
            evidence=self.evidence,
            plan=plan or self.plan,
            execution_record=execution_record or self.execution_record,
            validation_result=validation_result or self.validation_result,
            verification_result=verification_result or self.verification_result,
            certification_result=certification_result or self.certification_result,
            authority=self.authority,
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "evolution_id": self.evolution_id,
            "object_kind": self.object_kind,
            "phase": self.phase,
            "lifecycle_state": self.lifecycle_state,
            "subject_identity": self.subject_identity,
            "candidate_class": self.candidate_class,
            "previous_state": self.previous_state,
            "target_state": self.target_state,
            "reason": self.reason,
            "context": [list(pair) for pair in self.context],
            "dependencies": list(self.dependencies),
            "evidence": list(self.evidence),
            "plan": self.plan,
            "execution_record": self.execution_record,
            "validation_result": self.validation_result,
            "verification_result": self.verification_result,
            "certification_result": self.certification_result,
            "authority": self.authority,
        }

    def digest(self) -> str:
        return content_hash(self.to_dict())


def phase_object(
    authority: Any,
    previous: EvolutionObject,
    *,
    ordinal: int,
    evidence: Sequence[str] | None = None,
    plan: str = "",
    execution_record: str = "",
    validation_result: str = "",
    verification_result: str = "",
    certification_result: str = "",
    note: Mapping[str, str] | None = None,
) -> EvolutionObject:
    """Derive the object of the phase at ``ordinal``, continuing from ``previous``.

    The single construction path for the phases whose artifact is a verdict rather than a
    document (validation, verification, certification, learning, state transition). Every one of
    them needs the same five things — the phase, its object kind, its lifecycle state, its
    dependencies and its authority — all of which come from the authority, so deriving them here
    once removes five near-identical copies and the chance that one of them drifts.
    """
    phase = authority.phase_by_ordinal(ordinal)
    kind = authority.object_kind_of(phase.identifier)
    return EvolutionObject.derive(
        rule=authority.identity,
        candidate=EvolutionCandidate.from_object(previous),
        object_kind=kind.identifier,
        phase=phase.identifier,
        lifecycle_state=authority.stage_of(phase.identifier),
        dependencies=authority.dependencies_of(phase.identifier),
        evidence=tuple(evidence) if evidence is not None else previous.evidence,
        authority=phase.authority,
        plan=plan or previous.plan,
        execution_record=execution_record or previous.execution_record,
        validation_result=validation_result or previous.validation_result,
        verification_result=verification_result or previous.verification_result,
        certification_result=certification_result or previous.certification_result,
        context=as_context({**dict(previous.context), **dict(note or {})}),
    )


@dataclass(frozen=True, slots=True)
class EvolutionUnderstanding:
    """Why to evolve, what changes, what depends on it, what can break, what evidences it."""

    obj: EvolutionObject
    why: str
    current_state: str
    target_state: str
    impact: tuple[str, ...]
    dependencies: tuple[str, ...]
    risk: str
    validation_requirement: tuple[str, ...]
    certification_requirement: tuple[str, ...]
    breaks: tuple[str, ...]

    def to_dict(self) -> dict[str, Any]:
        return {
            "object": self.obj.to_dict(),
            "why": self.why,
            "current_state": self.current_state,
            "target_state": self.target_state,
            "impact": list(self.impact),
            "dependencies": list(self.dependencies),
            "risk": self.risk,
            "validation_requirement": list(self.validation_requirement),
            "certification_requirement": list(self.certification_requirement),
            "breaks": list(self.breaks),
        }


@dataclass(frozen=True, slots=True)
class PlanStep:
    """One step of a plan, and the located owner that discharges it."""

    phase: str
    duty: str
    owner: str
    gate: str
    authority: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "phase": self.phase,
            "duty": self.duty,
            "owner": self.owner,
            "gate": self.gate,
            "authority": self.authority,
        }


@dataclass(frozen=True, slots=True)
class EvolutionPlan:
    """Objectives, steps, dependencies, risk controls, criteria and rollback."""

    obj: EvolutionObject
    understanding: EvolutionUnderstanding
    objectives: tuple[str, ...]
    steps: tuple[PlanStep, ...]
    dependencies: tuple[str, ...]
    risk: str
    risk_controls: tuple[str, ...]
    validation_criteria: tuple[str, ...]
    verification_criteria: tuple[str, ...]
    certification_criteria: tuple[str, ...]
    rollback_strategy: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "object": self.obj.to_dict(),
            "objectives": list(self.objectives),
            "steps": [step.to_dict() for step in self.steps],
            "dependencies": list(self.dependencies),
            "risk": self.risk,
            "risk_controls": list(self.risk_controls),
            "validation_criteria": list(self.validation_criteria),
            "verification_criteria": list(self.verification_criteria),
            "certification_criteria": list(self.certification_criteria),
            "rollback_strategy": self.rollback_strategy,
        }

    def digest(self) -> str:
        return content_hash(self.to_dict())


@dataclass(frozen=True, slots=True)
class EvolutionSimulation:
    """Impact prediction, dependency resolution and risk evaluation, before execution."""

    obj: EvolutionObject
    plan: EvolutionPlan
    expected_impact: tuple[str, ...]
    dependency_effects: tuple[str, ...]
    unresolved_dependencies: tuple[str, ...]
    potential_failures: tuple[str, ...]
    validation_ready: bool
    fixed_point: bool
    first_digest: str
    second_digest: str
    replay_owner: str

    @property
    def executable(self) -> bool:
        """Whether execution may be authorised at all.

        A simulation that did not reach a fixed point, or that left a dependency unresolved,
        or that found the validation criteria unmeasurable, has not evaluated the plan — and
        the controlled-execution rule forbids executing an unevaluated plan.
        """
        return self.fixed_point and not self.unresolved_dependencies and self.validation_ready

    def to_dict(self) -> dict[str, Any]:
        return {
            "object": self.obj.to_dict(),
            "expected_impact": list(self.expected_impact),
            "dependency_effects": list(self.dependency_effects),
            "unresolved_dependencies": list(self.unresolved_dependencies),
            "potential_failures": list(self.potential_failures),
            "validation_ready": self.validation_ready,
            "fixed_point": self.fixed_point,
            "first_digest": self.first_digest,
            "second_digest": self.second_digest,
            "replay_owner": self.replay_owner,
            "executable": self.executable,
        }


@dataclass(frozen=True, slots=True)
class EvolutionExecution:
    """The authorisation of an execution — never the assertion that a mutation happened.

    ``authorised`` says the single declared mutation path resolves, its symbols are bound and
    its gate is wired. This engine performs no mutation, which is why no bypass can originate
    here: there is no code path from this object to repository state.
    """

    obj: EvolutionObject
    plan: EvolutionPlan
    simulation: EvolutionSimulation
    mutation_path: str
    mutation_symbols: tuple[str, ...]
    gate: str
    gate_wired: bool
    path_resolves: bool
    authority: str
    authorised: bool
    refusals: tuple[str, ...]
    mutation_performed: bool = False

    def to_dict(self) -> dict[str, Any]:
        return {
            "object": self.obj.to_dict(),
            "mutation_path": self.mutation_path,
            "mutation_symbols": list(self.mutation_symbols),
            "gate": self.gate,
            "gate_wired": self.gate_wired,
            "path_resolves": self.path_resolves,
            "authority": self.authority,
            "authorised": self.authorised,
            "refusals": list(self.refusals),
            "mutation_performed": self.mutation_performed,
        }

    def digest(self) -> str:
        return content_hash(self.to_dict())


@dataclass(frozen=True, slots=True)
class EvolutionObservation:
    """Expected result, actual result and deviation, attributed to the measuring owner.

    No verdict word is emitted. Delta classification against declared orderings is owned by
    the control plane, which ``engine`` may not import, so the classification is *attributed*
    to :attr:`classification_owner` rather than restated here under a word this engine
    invented. What is recorded is the falsifiable part: two digests and their difference.
    """

    obj: EvolutionObject
    execution: EvolutionExecution
    expected: Context
    actual: Context
    deviation: tuple[str, ...]
    evidence: tuple[str, ...]
    measured_by: str
    classification_owner: str

    @property
    def matches(self) -> bool:
        return not self.deviation

    def to_dict(self) -> dict[str, Any]:
        return {
            "object": self.obj.to_dict(),
            "expected": [list(pair) for pair in self.expected],
            "actual": [list(pair) for pair in self.actual],
            "deviation": list(self.deviation),
            "evidence": list(self.evidence),
            "measured_by": self.measured_by,
            "classification_owner": self.classification_owner,
            "matches": self.matches,
        }


@dataclass(frozen=True, slots=True)
class CriterionOutcome:
    """One declared criterion, measured, with the owner that governs the dimension."""

    identifier: str
    subject: str
    obligation: str
    satisfied: bool
    blocking: bool
    detail: str
    owner: str = ""
    gate: str = ""
    gate_wired: bool = True

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.identifier,
            "subject": self.subject,
            "obligation": self.obligation,
            "satisfied": self.satisfied,
            "blocking": self.blocking,
            "detail": self.detail,
            "owner": self.owner,
            "gate": self.gate,
            "gate_wired": self.gate_wired,
        }


@dataclass(frozen=True, slots=True)
class Verdict:
    """The aggregate of a set of measured criteria.

    ``passed`` is false when any *blocking* criterion is unsatisfied. A non-blocking failure
    is recorded and does not gate, which is the declaration's own distinction and not a
    leniency introduced here.
    """

    subject: str
    outcomes: tuple[CriterionOutcome, ...]

    @property
    def failures(self) -> tuple[CriterionOutcome, ...]:
        return tuple(entry for entry in self.outcomes if not entry.satisfied)

    @property
    def blocking_failures(self) -> tuple[CriterionOutcome, ...]:
        return tuple(entry for entry in self.failures if entry.blocking)

    @property
    def passed(self) -> bool:
        return not self.blocking_failures

    @property
    def summary(self) -> str:
        satisfied = len(self.outcomes) - len(self.failures)
        state = "SATISFIED" if self.passed else "REFUSED"
        return f"{state} {satisfied}/{len(self.outcomes)} {self.subject}"

    def to_dict(self) -> dict[str, Any]:
        return {
            "subject": self.subject,
            "passed": self.passed,
            "summary": self.summary,
            "outcomes": [entry.to_dict() for entry in self.outcomes],
        }

    def digest(self) -> str:
        return content_hash(self.to_dict())


@dataclass(frozen=True, slots=True)
class EvolutionChain:
    """Every object produced for one candidate, in phase order, with its phase artifacts.

    The chain is the unit validation, verification, certification and history operate on. It
    is assembled by the phase modules in order and is never partially valid: a chain missing a
    mandated object fails the completeness dimension rather than being silently short.
    """

    candidate: EvolutionCandidate
    objects: tuple[EvolutionObject, ...]
    understanding: EvolutionUnderstanding | None = None
    plan: EvolutionPlan | None = None
    simulation: EvolutionSimulation | None = None
    execution: EvolutionExecution | None = None
    observation: EvolutionObservation | None = None
    validation: Verdict | None = None
    verification: Verdict | None = None
    certification: Verdict | None = None
    findings: tuple[str, ...] = field(default_factory=tuple)

    @property
    def evolution_id(self) -> str:
        """The chain's identity: its candidate's, which every phase object descends from."""
        return self.candidate.evolution_id

    @property
    def subject_identity(self) -> str:
        return self.candidate.subject_identity

    def object_for(self, phase: str) -> EvolutionObject | None:
        for entry in self.objects:
            if entry.phase == phase:
                return entry
        return None

    def kinds(self) -> tuple[str, ...]:
        return tuple(entry.object_kind for entry in self.objects)

    def with_objects(self, objects: Sequence[EvolutionObject]) -> EvolutionChain:
        return EvolutionChain(
            candidate=self.candidate,
            objects=tuple(objects),
            understanding=self.understanding,
            plan=self.plan,
            simulation=self.simulation,
            execution=self.execution,
            observation=self.observation,
            validation=self.validation,
            verification=self.verification,
            certification=self.certification,
            findings=self.findings,
        )

    def with_verdicts(
        self,
        *,
        validation: Verdict | None = None,
        verification: Verdict | None = None,
        certification: Verdict | None = None,
    ) -> EvolutionChain:
        """The chain carrying measured verdicts, with its objects untouched."""
        return EvolutionChain(
            candidate=self.candidate,
            objects=self.objects,
            understanding=self.understanding,
            plan=self.plan,
            simulation=self.simulation,
            execution=self.execution,
            observation=self.observation,
            validation=validation if validation is not None else self.validation,
            verification=verification if verification is not None else self.verification,
            certification=certification if certification is not None else self.certification,
            findings=self.findings,
        )

    def sealed(self) -> EvolutionChain:
        """Every object carrying the chain's plan, execution record and measured verdicts.

        The declared field mandate applies to *every* evolution object, including the ones
        produced before the plan existed and before any verdict was reached. Sealing is how that
        mandate becomes satisfiable without backdating: the plan and the verdicts are attached to
        every object in the chain at the end of the traversal, and because none of them is an
        identity input, not one identity changes. A chain that has not been sealed is therefore
        incomplete by construction rather than by accident, which is what makes the completeness
        dimension a real measurement instead of a formality.

        Sealing is idempotent in its effect on identity and converges in its effect on verdicts:
        sealing a sealed chain attaches the same values, so a caller may settle the interdependence
        between "completeness requires a verdict" and "the verdict measures completeness" by
        measuring, sealing, and measuring once more.
        """
        plan = self.plan.obj.plan if self.plan is not None else ""
        execution_record = self.execution.obj.execution_record if self.execution is not None else ""
        validation = self.validation.summary if self.validation is not None else ""
        verification = self.verification.summary if self.verification is not None else ""
        certification = self.certification.summary if self.certification is not None else ""
        return self.with_objects(
            tuple(
                entry.with_results(
                    plan=plan,
                    execution_record=execution_record,
                    validation_result=validation,
                    verification_result=verification,
                    certification_result=certification,
                )
                for entry in self.objects
            )
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "evolution_id": self.evolution_id,
            "candidate": self.candidate.to_dict(),
            "objects": [entry.to_dict() for entry in self.objects],
            "understanding": self.understanding.to_dict() if self.understanding else None,
            "plan": self.plan.to_dict() if self.plan else None,
            "simulation": self.simulation.to_dict() if self.simulation else None,
            "execution": self.execution.to_dict() if self.execution else None,
            "observation": self.observation.to_dict() if self.observation else None,
            "validation": self.validation.to_dict() if self.validation else None,
            "verification": self.verification.to_dict() if self.verification else None,
            "certification": self.certification.to_dict() if self.certification else None,
            "findings": list(self.findings),
        }

    def digest(self) -> str:
        return content_hash(self.to_dict())


__all__ = [
    "Context",
    "CriterionOutcome",
    "EvolutionCandidate",
    "EvolutionChain",
    "EvolutionExecution",
    "EvolutionObject",
    "EvolutionObservation",
    "EvolutionPlan",
    "EvolutionSimulation",
    "EvolutionUnderstanding",
    "PlanStep",
    "Verdict",
    "as_context",
    "derive_identity",
    "identity_inputs",
    "phase_object",
]
