"""URKE-000001 Part 01 — the governed entity as inert values. No I/O, no clock, no vocabulary.

Everything in this module is a frozen value. Nothing here decides anything: a governed entity
carries what was recorded about it and the histories that were appended to it, and it carries no
verdict, no permission and no truth flag. Disposition belongs to UCON-000001 and is reached through
:mod:`engine.recursive_knowledge.bridge`; this module could not express an admission if it wanted
to, which is the point.

Two design decisions are load-bearing.

**Histories are tuples, not fields.** A contradiction does not have a ``resolution`` — it has a
:class:`ResolutionStep` sequence, and the earlier steps stay. A verification is not a boolean — it
is a :class:`VerificationEvent` sequence, and a later refutation does not erase the earlier
support. Had these been scalar fields, "this was resolved" and "this was resolved three times in
three incompatible ways" would be the same observable state, and the second is the one worth
knowing about.

**Required attributes are read, never assumed.** :data:`ATTRIBUTE_READERS` maps an attribute name
to the function that reads it off an entity, and the declaration says which attributes each entity
class requires. :func:`missing_attributes` is therefore a join between data and code rather than a
hand-written checklist, and law URKE-L-03 and URKE-L-05 refuse the declaration if it names an
attribute nothing here can read, or if this module can read an attribute no entity class requires.

Stdlib only, plus two in-repo primitives that already have owners: the kernel mints identity and
UCKP Layer Zero owns the canonical digest. Neither is reimplemented here.
"""

from __future__ import annotations

from collections.abc import Callable, Iterable, Mapping
from dataclasses import dataclass, field
from types import MappingProxyType
from typing import Any

from engine.construct.model import Evidence, Lineage
from engine.kernel.identity import mint
from engine.uckp.canonical import content_hash

#: Digest length for a derived record identifier. Long enough that two records in one ledger do
#: not collide, short enough to read in a rendered trace.
_RECORD_DIGEST = 16


class RecursiveKnowledgeError(RuntimeError):
    """The entity, record or declaration is unusable. A fault, never a knowledge state.

    Raised for a malformed *record* — an entity missing a required attribute, a transition to a
    state nothing declares, a closure claimed with no criterion. It is never raised because
    something is unknown, contradictory, undecidable or unresolved: those are states, and a state
    is an answer rather than an error. The gate maps this to FAULT (exit 2), which is neither a
    pass nor a refusal.
    """


def knowledge_id(entity_class: str, natural_key: str, *, namespace: str, key_domain: str) -> str:
    """Return the deterministic identifier for ``(entity_class, namespace, natural_key)``.

    Pure and total: no clock, no counter, no path, no I/O, and no natural key it refuses. The key
    is folded through the canonical digest first, so a question phrased with punctuation, spaces or
    in a non-Latin script yields an identifier rather than a refusal — which matters here more than
    in most places, because the natural key of an unknown is usually a sentence somebody wrote once.

    ``namespace`` and ``key_domain`` are parameters rather than constants because they are declared
    data. A module-level default would be this capability quietly owning an identity decision the
    declaration is supposed to own.
    """
    if not isinstance(entity_class, str) or not entity_class.strip():
        raise RecursiveKnowledgeError("an entity class is required to mint an identity")
    if not isinstance(natural_key, str) or not natural_key.strip():
        raise RecursiveKnowledgeError("a natural key is required to mint an identity")
    if not namespace.strip() or not key_domain.strip():
        raise RecursiveKnowledgeError(
            "the declaration must supply an identity namespace and a key domain"
        )
    folded = content_hash([key_domain, natural_key.strip()])
    return mint(entity_class.strip(), namespace, folded)


def _frozen(value: Mapping[str, Any] | None) -> Mapping[str, Any]:
    return MappingProxyType(dict(value or {}))


def _texts(value: Any) -> tuple[str, ...]:
    if value is None:
        return ()
    if isinstance(value, str):
        return (value,)
    return tuple(str(item) for item in value)


# --- histories ----------------------------------------------------------------------------


@dataclass(frozen=True, slots=True)
class StateTransition:
    """One recorded movement between knowledge states.

    ``basis`` is required. A transition with no basis would let a subject be moved from unknown to
    verified by an act nobody has to account for, and the whole lifecycle would then be decorative.
    """

    from_state: str
    to_state: str
    basis: str
    actor: str
    sequence: int
    record_id: str = field(default="", compare=False)

    def __post_init__(self) -> None:
        if not self.basis.strip():
            raise RecursiveKnowledgeError(
                f"a state transition to {self.to_state!r} must name its basis"
            )
        if not self.actor.strip():
            raise RecursiveKnowledgeError(
                f"a state transition to {self.to_state!r} must name its actor"
            )
        object.__setattr__(
            self,
            "record_id",
            content_hash([self.from_state, self.to_state, self.basis, self.actor, self.sequence])[
                :_RECORD_DIGEST
            ],
        )

    def as_dict(self) -> dict[str, Any]:
        return {
            "actor": self.actor,
            "basis": self.basis,
            "from_state": self.from_state,
            "record_id": self.record_id,
            "sequence": self.sequence,
            "to_state": self.to_state,
        }


@dataclass(frozen=True, slots=True)
class Position:
    """One side of a contradiction: who holds it, what they claim, and on what basis.

    A contradiction is stored as positions rather than as a left/right pair so that a third
    position does not require a schema change, and so that neither side occupies a structurally
    privileged field.
    """

    holder: str
    claim: str
    basis: str
    evidence: tuple[Evidence, ...] = ()
    position_id: str = field(default="", compare=False)

    def __post_init__(self) -> None:
        if not self.holder.strip():
            raise RecursiveKnowledgeError("a competing position must name its holder")
        if not self.claim.strip():
            raise RecursiveKnowledgeError("a competing position must state its claim")
        object.__setattr__(self, "evidence", tuple(self.evidence))
        object.__setattr__(
            self,
            "position_id",
            content_hash([self.holder, self.claim, self.basis])[:_RECORD_DIGEST],
        )

    def as_dict(self) -> dict[str, Any]:
        return {
            "basis": self.basis,
            "claim_text": self.claim,
            "evidence": [item.as_dict() for item in self.evidence],
            "holder": self.holder,
            "position_id": self.position_id,
        }


@dataclass(frozen=True, slots=True)
class ResolutionStep:
    """One recorded act in the resolution of a contradiction. Appended, never replaced."""

    action: str
    actor: str
    outcome: str
    basis: str
    sequence: int
    step_id: str = field(default="", compare=False)

    def __post_init__(self) -> None:
        for label, value in (("action", self.action), ("actor", self.actor), ("basis", self.basis)):
            if not str(value).strip():
                raise RecursiveKnowledgeError(f"a resolution step must name its {label}")
        object.__setattr__(
            self,
            "step_id",
            content_hash([self.action, self.actor, self.outcome, self.basis, self.sequence])[
                :_RECORD_DIGEST
            ],
        )

    def as_dict(self) -> dict[str, Any]:
        return {
            "action": self.action,
            "actor": self.actor,
            "basis": self.basis,
            "outcome": self.outcome,
            "sequence": self.sequence,
            "step_id": self.step_id,
        }


@dataclass(frozen=True, slots=True)
class VerificationEvent:
    """One verification performed against an entity, with what it assumed and what it could not do.

    ``assumptions`` and ``limitations`` are both required and both must be non-empty. A
    verification that declares it assumed nothing and could not fail has not been examined, and
    recording it would add a row that reads as assurance while measuring nothing. UCON-000001
    applies the same refusal to verifiers; this is the same principle applied to events.
    """

    verifier: str
    verdict: str
    assumptions: tuple[str, ...]
    limitations: tuple[str, ...]
    basis: str
    sequence: int
    event_id: str = field(default="", compare=False)

    def __post_init__(self) -> None:
        object.__setattr__(self, "assumptions", _texts(self.assumptions))
        object.__setattr__(self, "limitations", _texts(self.limitations))
        if not self.verifier.strip():
            raise RecursiveKnowledgeError("a verification event must name its verifier")
        if not self.verdict.strip():
            raise RecursiveKnowledgeError("a verification event must record its verdict")
        if not self.basis.strip():
            raise RecursiveKnowledgeError("a verification event must name its basis")
        if not self.assumptions:
            raise RecursiveKnowledgeError(
                f"the verification by {self.verifier!r} declares no assumptions, so nothing about "
                "it has been examined"
            )
        if not self.limitations:
            raise RecursiveKnowledgeError(
                f"the verification by {self.verifier!r} declares no limitations, so it claims to "
                "be unable to be wrong"
            )
        object.__setattr__(
            self,
            "event_id",
            content_hash(
                [
                    self.verifier,
                    self.verdict,
                    list(self.assumptions),
                    list(self.limitations),
                    self.basis,
                    self.sequence,
                ]
            )[:_RECORD_DIGEST],
        )

    def as_dict(self) -> dict[str, Any]:
        return {
            "assumptions": list(self.assumptions),
            "basis": self.basis,
            "event_id": self.event_id,
            "limitations": list(self.limitations),
            "sequence": self.sequence,
            "verdict": self.verdict,
            "verifier": self.verifier,
        }


@dataclass(frozen=True, slots=True)
class ReviewPoint:
    """When a gap must be looked at again, counted in ledger sequence rather than in elapsed time.

    Sequence rather than a clock, because the same committed bytes must measure identically twice
    and a wall-clock comparison cannot do that. The consequence — that a review can be surfaced as
    due because work advanced past it and not because time passed — is a real limitation and it is
    disclosed in the declaration rather than papered over here.
    """

    cadence: int
    due_at_sequence: int
    criteria: str
    review_id: str = field(default="", compare=False)

    def __post_init__(self) -> None:
        if self.cadence < 1:
            raise RecursiveKnowledgeError("a review cadence must be at least one ledger step")
        if not self.criteria.strip():
            raise RecursiveKnowledgeError("a review point must say what the review is to consider")
        object.__setattr__(
            self,
            "review_id",
            content_hash([self.cadence, self.due_at_sequence, self.criteria])[:_RECORD_DIGEST],
        )

    def due(self, at_sequence: int) -> bool:
        """True when the ledger has advanced to or past this review point."""
        return at_sequence >= self.due_at_sequence

    def as_dict(self) -> dict[str, Any]:
        return {
            "cadence": self.cadence,
            "criteria": self.criteria,
            "due_at_sequence": self.due_at_sequence,
            "review_id": self.review_id,
        }


@dataclass(frozen=True, slots=True)
class ClosureCriterion:
    """One condition that must hold before a gap may be closed.

    ``satisfied`` may only become true together with a ``basis``: :meth:`satisfy` is the single
    constructor for the satisfied form and it requires one. Closure is therefore always traceable
    to something, and a gap cannot be closed by flipping a flag.
    """

    statement: str
    satisfied: bool = False
    basis: str = ""
    criterion_id: str = field(default="", compare=False)

    def __post_init__(self) -> None:
        if not self.statement.strip():
            raise RecursiveKnowledgeError("a closure criterion must state a condition")
        if self.satisfied and not self.basis.strip():
            raise RecursiveKnowledgeError(
                f"the criterion {self.statement!r} is recorded satisfied with no basis"
            )
        object.__setattr__(self, "criterion_id", content_hash([self.statement])[:_RECORD_DIGEST])

    def satisfy(self, basis: str) -> ClosureCriterion:
        """Return the satisfied form of this criterion, which requires a basis."""
        return ClosureCriterion(statement=self.statement, satisfied=True, basis=basis)

    def as_dict(self) -> dict[str, Any]:
        return {
            "basis": self.basis,
            "criterion_id": self.criterion_id,
            "satisfied": self.satisfied,
            "statement": self.statement,
        }


# --- the governed entity ------------------------------------------------------------------


@dataclass(frozen=True, slots=True)
class GovernedEntity:
    """One identified thing under governed lifecycle, with every history it has accumulated.

    One type for every entity class rather than a class hierarchy, because the required-attribute
    set is declared data: a subclass per class would put the requirement in code, and adding an
    entity class would then be a code change instead of an admission. What a research object needs
    and what a contradiction needs differ, and the difference lives in the declaration where
    URKE-L-03 and URKE-L-05 can measure it.

    The attributes that look unused for a given class are not defaults standing in for facts — an
    entity class that does not require ``severity`` simply never reads it, and one that does
    requires it to be present at admission or the admission is refused.
    """

    identity: str
    entity_class: str
    natural_key: str
    state: str
    owner: str
    origin: str
    governance: str
    sequence: int
    title: str = ""
    classification: str = ""
    severity: str = ""
    resolution_path: str = ""
    resolution_status: str = ""
    lineage: Lineage = field(default_factory=Lineage)
    evidence: tuple[Evidence, ...] = ()
    payload: Mapping[str, Any] = field(default_factory=dict)
    affected_entities: tuple[str, ...] = ()
    affected: Mapping[str, tuple[str, ...]] = field(default_factory=dict)
    context: str = ""
    evolution_metadata: Mapping[str, str] = field(default_factory=dict)
    source: str = ""
    target: str = ""
    relation: str = ""
    basis: str = ""
    axes: Mapping[str, str] = field(default_factory=dict)
    candidate_resolutions: tuple[str, ...] = ()
    competing_positions: tuple[Position, ...] = ()
    resolution_history: tuple[ResolutionStep, ...] = ()
    verification_history: tuple[VerificationEvent, ...] = ()
    state_history: tuple[StateTransition, ...] = ()
    review_schedule: tuple[ReviewPoint, ...] = ()
    closure_criteria: tuple[ClosureCriterion, ...] = ()
    superseded_by: str = ""

    def __post_init__(self) -> None:
        object.__setattr__(self, "payload", _frozen(self.payload))
        object.__setattr__(self, "evidence", tuple(self.evidence))
        object.__setattr__(self, "affected_entities", _texts(self.affected_entities))
        object.__setattr__(
            self,
            "affected",
            MappingProxyType({str(k): _texts(v) for k, v in dict(self.affected or {}).items()}),
        )
        object.__setattr__(
            self,
            "axes",
            MappingProxyType({str(k): str(v) for k, v in dict(self.axes or {}).items()}),
        )
        object.__setattr__(
            self,
            "evolution_metadata",
            MappingProxyType(
                {str(k): str(v) for k, v in dict(self.evolution_metadata or {}).items()}
            ),
        )
        object.__setattr__(self, "candidate_resolutions", _texts(self.candidate_resolutions))
        object.__setattr__(self, "competing_positions", tuple(self.competing_positions))
        object.__setattr__(self, "resolution_history", tuple(self.resolution_history))
        object.__setattr__(self, "verification_history", tuple(self.verification_history))
        object.__setattr__(self, "state_history", tuple(self.state_history))
        object.__setattr__(self, "review_schedule", tuple(self.review_schedule))
        object.__setattr__(self, "closure_criteria", tuple(self.closure_criteria))
        object.__setattr__(self, "title", self.title or self.natural_key)

    @property
    def active(self) -> bool:
        """False once something later has been recorded as replacing this entity."""
        return not self.superseded_by

    @property
    def closure_satisfied(self) -> bool:
        """True when every declared closure criterion is recorded satisfied.

        An entity with no criteria answers False. "Nothing was required" and "everything required
        was done" must not be the same answer, or a gap admitted without criteria would close for
        free.
        """
        return bool(self.closure_criteria) and all(
            criterion.satisfied for criterion in self.closure_criteria
        )

    def content_digest(self) -> str:
        """A digest over the whole entity, histories included, excluding its derived identity."""
        return content_hash(
            {
                "affected": {k: list(v) for k, v in sorted(self.affected.items())},
                "affected_entities": list(self.affected_entities),
                "axes": dict(sorted(self.axes.items())),
                "basis": self.basis,
                "context": self.context,
                "evolution_metadata": dict(sorted(self.evolution_metadata.items())),
                "relation": self.relation,
                "source": self.source,
                "target": self.target,
                "candidate_resolutions": list(self.candidate_resolutions),
                "classification": self.classification,
                "closure_criteria": [item.as_dict() for item in self.closure_criteria],
                "competing_positions": [item.as_dict() for item in self.competing_positions],
                "entity_class": self.entity_class,
                "evidence": [item.as_dict() for item in self.evidence],
                "governance": self.governance,
                "lineage": self.lineage.as_dict(),
                "natural_key": self.natural_key,
                "origin": self.origin,
                "owner": self.owner,
                "payload": dict(self.payload),
                "resolution_history": [item.as_dict() for item in self.resolution_history],
                "resolution_path": self.resolution_path,
                "resolution_status": self.resolution_status,
                "review_schedule": [item.as_dict() for item in self.review_schedule],
                "severity": self.severity,
                "state": self.state,
                "state_history": [item.as_dict() for item in self.state_history],
                "superseded_by": self.superseded_by,
                "title": self.title,
                "verification_history": [item.as_dict() for item in self.verification_history],
            }
        )

    def as_dict(self) -> dict[str, Any]:
        return {
            "active": self.active,
            "affected": {k: list(v) for k, v in sorted(self.affected.items())},
            "affected_entities": list(self.affected_entities),
            "axes": dict(sorted(self.axes.items())),
            "basis": self.basis,
            "context": self.context,
            "evolution_metadata": dict(sorted(self.evolution_metadata.items())),
            "relation": self.relation,
            "source": self.source,
            "target": self.target,
            "candidate_resolutions": list(self.candidate_resolutions),
            "classification": self.classification,
            "closure_criteria": [item.as_dict() for item in self.closure_criteria],
            "closure_satisfied": self.closure_satisfied,
            "competing_positions": [item.as_dict() for item in self.competing_positions],
            "content_digest": self.content_digest(),
            "entity_class": self.entity_class,
            "evidence": [item.as_dict() for item in self.evidence],
            "governance": self.governance,
            "identity": self.identity,
            "lineage": self.lineage.as_dict(),
            "natural_key": self.natural_key,
            "origin": self.origin,
            "owner": self.owner,
            "payload": dict(self.payload),
            "resolution_history": [item.as_dict() for item in self.resolution_history],
            "resolution_path": self.resolution_path,
            "resolution_status": self.resolution_status,
            "review_schedule": [item.as_dict() for item in self.review_schedule],
            "sequence": self.sequence,
            "severity": self.severity,
            "state": self.state,
            "state_history": [item.as_dict() for item in self.state_history],
            "superseded_by": self.superseded_by,
            "title": self.title,
            "verification_history": [item.as_dict() for item in self.verification_history],
        }


# --- the attribute join -------------------------------------------------------------------

#: Every attribute an entity class may require, mapped to the function that reads it. Bound in both
#: directions at load time: a required attribute nothing here reads is an unenforceable requirement,
#: and a reader no class requires is dead code wearing enforcement's costume.
ATTRIBUTE_READERS: Mapping[str, Callable[[GovernedEntity], Any]] = MappingProxyType(
    {
        "affected": lambda entity: entity.affected,
        "affected_entities": lambda entity: entity.affected_entities,
        "axes": lambda entity: entity.axes,
        "basis": lambda entity: entity.basis,
        "context": lambda entity: entity.context,
        "evolution_metadata": lambda entity: entity.evolution_metadata,
        "relation": lambda entity: entity.relation,
        "source": lambda entity: entity.source,
        "target": lambda entity: entity.target,
        "candidate_resolutions": lambda entity: entity.candidate_resolutions,
        "classification": lambda entity: entity.classification,
        "closure_criteria": lambda entity: entity.closure_criteria,
        "competing_positions": lambda entity: entity.competing_positions,
        "entity_class": lambda entity: entity.entity_class,
        "evidence": lambda entity: entity.evidence,
        "governance": lambda entity: entity.governance,
        "identity": lambda entity: entity.identity,
        "lineage": lambda entity: entity.lineage.presented_by or entity.lineage.derived_from,
        "natural_key": lambda entity: entity.natural_key,
        "origin": lambda entity: entity.origin,
        "owner": lambda entity: entity.owner,
        "payload": lambda entity: entity.payload,
        "resolution_history": lambda entity: entity.resolution_history,
        "resolution_path": lambda entity: entity.resolution_path,
        "resolution_status": lambda entity: entity.resolution_status,
        "review_schedule": lambda entity: entity.review_schedule,
        "severity": lambda entity: entity.severity,
        "state": lambda entity: entity.state,
        "state_history": lambda entity: entity.state_history,
        "title": lambda entity: entity.title,
        "verification_history": lambda entity: entity.verification_history,
    }
)


def available_attributes() -> frozenset[str]:
    """The attribute names this module can read — the set the declaration is bound against."""
    return frozenset(ATTRIBUTE_READERS)


def missing_attributes(entity: GovernedEntity, required: Iterable[str]) -> tuple[str, ...]:
    """Return the required attributes this entity does not carry, in declared order.

    "Does not carry" means empty, not absent: every attribute exists on the type, so the question
    is always whether a value was recorded. An unknown owner is recorded with the declared
    unassigned token rather than an empty string, precisely so that "nobody owns this" is a fact a
    detector can find instead of a blank that reads as an oversight.
    """
    absent: list[str] = []
    for attribute in required:
        reader = ATTRIBUTE_READERS.get(attribute)
        if reader is None:
            raise RecursiveKnowledgeError(
                f"the declaration requires attribute {attribute!r}, which nothing can read"
            )
        value = reader(entity)
        if isinstance(value, str):
            if not value.strip():
                absent.append(attribute)
        elif not value:
            absent.append(attribute)
    return tuple(absent)


__all__ = [
    "ATTRIBUTE_READERS",
    "ClosureCriterion",
    "Evidence",
    "GovernedEntity",
    "Lineage",
    "Position",
    "RecursiveKnowledgeError",
    "ResolutionStep",
    "ReviewPoint",
    "StateTransition",
    "VerificationEvent",
    "available_attributes",
    "knowledge_id",
    "missing_attributes",
]
