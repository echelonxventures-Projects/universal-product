"""URKE-000001 Part 06 — the profiles that carry a history: gaps, contradictions, lessons.

Three profiles need more than the universal attribute set, and this module is where their extra
requirements are assembled. None of them is a class: a gap and a contradiction are subjects whose
classification names a profile, and the profile is data.

Two deliberate decisions are worth naming.

A contradiction is admitted with its resolution history and verification history already non-empty,
because the recording *is* an act in the resolution history and the detection *is* a measurement
with assumptions and limits. The alternative — permitting empty histories at admission — would have
meant either a profile that cannot enforce them or a first entry that is fabricated later.

A gap cannot be admitted without closure criteria. A gap with no criteria could be closed for free,
and "closed" would come to mean "stopped being looked at".
"""

from __future__ import annotations

from dataclasses import replace
from typing import Any

from engine.recursive_knowledge.declaration import Declaration, DisclosedGap
from engine.recursive_knowledge.ledger import KnowledgeLedger, LedgerError, relate
from engine.recursive_knowledge.model import (
    ClosureCriterion,
    Evidence,
    GovernedEntity,
    Lineage,
    Position,
    RecursiveKnowledgeError,
    ResolutionStep,
    ReviewPoint,
    VerificationEvent,
)

#: Roles this module addresses profiles through. Code symbols, bound in the declaration.
DISCLOSURE_ROLE = "disclosure"
CONFLICT_ROLE = "conflict"
LESSON_ROLE = "lesson"


class SubjectError(RecursiveKnowledgeError):
    """The subject cannot be assembled as its profile requires. A fault, never a state."""


# --- gaps ---------------------------------------------------------------------------------


def record_gap(
    ledger: KnowledgeLedger,
    *,
    natural_key: str,
    classification: str,
    severity: str,
    owner: str,
    origin: str,
    finding: str,
    resolution_path: str,
    criteria: tuple[str, ...],
    domain: str | None = None,
    cadence: int | None = None,
    context: str | None = None,
    qualifiers: dict[str, str] | None = None,
) -> GovernedEntity:
    """Admit a gap: identity, class, severity, owner, evidence, resolution path, review, criteria.

    ``qualifiers`` is how a caller says what kind of not-knowing this is — unstated, residual,
    blocked on science that does not exist. It is passed through to the composition rather than
    interpreted here, because a gap module that interpreted qualifiers would be a second classifier.
    """
    declaration = ledger.declaration
    declaration.gap_class(classification)
    declaration.severity(severity)
    if not criteria:
        raise SubjectError(
            f"the gap {natural_key!r} declares no closure criterion, so it could be closed without "
            "anything having been done"
        )
    if not resolution_path.strip():
        raise SubjectError(f"the gap {natural_key!r} names no resolution path")
    interval = cadence or declaration.default_review_cadence
    if interval < declaration.minimum_review_cadence:
        raise SubjectError(
            f"a review cadence of {interval} is below the declared minimum "
            f"{declaration.minimum_review_cadence}"
        )
    entity = ledger.subject(
        natural_key=natural_key,
        profile=declaration.profile_for(DISCLOSURE_ROLE),
        domain=domain or declaration.residual_domain,
        owner=owner,
        origin=origin,
        context=context,
        title=finding,
        payload={"classification": classification, "finding": finding},
        qualifiers=qualifiers,
        evidence=(Evidence(source=origin, statement=finding),),
        severity=severity,
        resolution_path=resolution_path,
        review_schedule=(
            ReviewPoint(
                cadence=interval,
                due_at_sequence=ledger.review_clock() + interval,
                criteria=resolution_path,
            ),
        ),
        closure_criteria=tuple(ClosureCriterion(statement=item) for item in criteria),
    )
    admitted = ledger.admit(entity)
    return replace(admitted, classification=admitted.classification)


def admit_disclosed_gap(ledger: KnowledgeLedger, gap: DisclosedGap) -> GovernedEntity:
    """Admit a gap the declaration discloses about itself. Self-application, not documentation."""
    declaration = ledger.declaration
    return record_gap(
        ledger,
        natural_key=gap.gap_id,
        classification=gap.classification,
        severity=gap.severity,
        owner=gap.referred_to
        if gap.referred_to in {spec.identifier for spec in declaration.ownership_roles}
        else declaration.unassigned_owner,
        origin=gap.source,
        finding=gap.finding,
        resolution_path=gap.remediation,
        criteria=(declaration.closure_criterion_template,),
        cadence=declaration.disclosure_review_cadence,
    )


def satisfy(
    ledger: KnowledgeLedger, identity: str, *, criterion: str, basis: str
) -> GovernedEntity:
    """Record one closure criterion satisfied, with a basis. Appends; replaces no history."""
    entity = ledger.get(identity)
    if not basis.strip():
        raise SubjectError("a satisfied criterion must name its basis")
    found = False
    updated = []
    for item in entity.closure_criteria:
        if item.statement == criterion and not item.satisfied:
            updated.append(item.satisfy(basis))
            found = True
        else:
            updated.append(item)
    if not found:
        raise SubjectError(f"{criterion!r} is not an unsatisfied closure criterion of {identity!r}")
    return ledger.amend(replace(entity, closure_criteria=tuple(updated)), event="criterion")


def close_gap(ledger: KnowledgeLedger, identity: str, *, basis: str, actor: str) -> GovernedEntity:
    """Move a gap to a settled state. Refuses unless every declared criterion is satisfied."""
    from engine.recursive_knowledge.states import transition

    entity = ledger.get(identity)
    if not entity.closure_satisfied:
        outstanding = [item.statement for item in entity.closure_criteria if not item.satisfied]
        raise SubjectError(
            f"{identity!r} cannot be closed: "
            + (
                f"{len(outstanding)} criterion(s) remain unsatisfied"
                if outstanding
                else "it declares no closure criterion"
            )
        )
    settled = ledger.declaration.settled_states[0]
    moved = transition(
        ledger.declaration,
        entity,
        settled,
        basis=basis,
        actor=actor,
        sequence=len(ledger.journal),
    )
    return ledger.amend(moved, event="closed")


def overdue(ledger: KnowledgeLedger) -> tuple[GovernedEntity, ...]:
    """Every unsettled gap whose review point the ledger has advanced past."""
    from engine.recursive_knowledge.states import settled as is_settled

    at = ledger.review_clock()
    role = ledger.declaration.profile_for(DISCLOSURE_ROLE)
    return tuple(
        item
        for item in ledger.of_profile(role)
        if not is_settled(ledger.declaration, item.state)
        and any(point.due(at) for point in item.review_schedule)
    )


# --- contradictions -----------------------------------------------------------------------


def record_contradiction(
    ledger: KnowledgeLedger,
    *,
    natural_key: str,
    classification: str,
    resolution_status: str,
    positions: tuple[Position, ...],
    affected: dict[str, tuple[str, ...]],
    candidate_resolutions: tuple[str, ...],
    owner: str,
    origin: str,
    detector: str,
    domain: str | None = None,
    context: str | None = None,
) -> GovernedEntity:
    """Admit a contradiction with every attribute its profile requires, histories included."""
    declaration = ledger.declaration
    declaration.contradiction_class(classification)
    declaration.resolution_state(resolution_status)
    if len(positions) < declaration.minimum_positions:
        raise SubjectError(
            f"a contradiction needs at least {declaration.minimum_positions} competing positions "
            f"and"
            f"{len(positions)} were offered; fewer is a disagreement with one side"
        )
    if not candidate_resolutions:
        raise SubjectError(
            f"the contradiction {natural_key!r} offers no candidate resolution, so nothing records "
            "what could settle it"
        )
    declared_dimensions = set(declaration.affected_dimensions)
    unknown = sorted(set(affected) - declared_dimensions)
    if unknown:
        raise SubjectError(
            "a contradiction records what it affects along declared dimensions; "
            f"{', '.join(unknown)} is not one"
        )
    if not affected:
        raise SubjectError(f"the contradiction {natural_key!r} records nothing it affects")
    touched = tuple(sorted({item for values in affected.values() for item in values}))
    if not touched:
        raise SubjectError(f"the contradiction {natural_key!r} names no affected subject")
    sequence = len(ledger.journal)
    entity = ledger.subject(
        natural_key=natural_key,
        profile=declaration.profile_for(CONFLICT_ROLE),
        domain=domain or declaration.residual_domain,
        owner=owner,
        origin=origin,
        context=context,
        title=f"{classification}: {natural_key}",
        payload={"classification": classification},
        evidence=tuple(item for position in positions for item in position.evidence)
        or (Evidence(source=detector, statement=f"detected by {detector}"),),
        lineage=Lineage(derived_from=touched, presented_by=detector),
        competing_positions=positions,
        candidate_resolutions=candidate_resolutions,
        affected=affected,
        affected_entities=touched,
        resolution_status=resolution_status,
        resolution_history=(
            ResolutionStep(
                action="admission-of-the-conflict",
                actor=detector,
                outcome=resolution_status,
                basis=origin,
                sequence=sequence,
            ),
        ),
        verification_history=(
            VerificationEvent(
                verifier=detector,
                verdict="detected",
                assumptions=("the positions are stated as their holders meant them",),
                limitations=(
                    "detection establishes that the positions conflict, not which one is right",
                ),
                basis=origin,
                sequence=sequence,
            ),
        ),
    )
    return ledger.admit(entity)


def add_resolution(
    ledger: KnowledgeLedger, identity: str, *, action: str, actor: str, outcome: str, basis: str
) -> GovernedEntity:
    """Append a resolution step. Earlier steps are retained byte-for-byte."""
    entity = ledger.get(identity)
    step = ResolutionStep(
        action=action,
        actor=actor,
        outcome=outcome,
        basis=basis,
        sequence=len(ledger.journal),
    )
    return ledger.amend(
        replace(entity, resolution_history=entity.resolution_history + (step,)), event="resolution"
    )


def add_verification(
    ledger: KnowledgeLedger,
    identity: str,
    *,
    verifier: str,
    verdict: str,
    assumptions: tuple[str, ...],
    limitations: tuple[str, ...],
    basis: str,
) -> GovernedEntity:
    """Append a verification event. Refuses one declaring no assumptions or no limitations."""
    entity = ledger.get(identity)
    event = VerificationEvent(
        verifier=verifier,
        verdict=verdict,
        assumptions=assumptions,
        limitations=limitations,
        basis=basis,
        sequence=len(ledger.journal),
    )
    return ledger.amend(
        replace(entity, verification_history=entity.verification_history + (event,)),
        event="verification",
    )


def generate_consequences(
    ledger: KnowledgeLedger, identity: str, *, owner: str
) -> tuple[GovernedEntity, ...]:
    """Admit every declared consequence of a contradiction as a related subject.

    Nothing unresolved becomes invisible: each consequence is a subject in its own right, linked
    back with the declared relation, so a contradiction that generated research and a contradiction
    that generated nothing are different observable states.
    """
    from engine.recursive_knowledge.research import open_research

    declaration = ledger.declaration
    source = ledger.get(identity)
    produced: list[GovernedEntity] = []
    for consequence in declaration.contradiction_generates:
        subject = open_research(
            ledger,
            natural_key=f"{source.natural_key}/{consequence}",
            question=f"what does {consequence} establish about {source.natural_key}?",
            owner=owner,
            origin=source.identity,
            domain=str(source.payload.get("domain") or declaration.residual_domain),
        )
        relate(
            ledger,
            source=subject.identity,
            target=identity,
            relation=_generated_relation(declaration),
            basis=f"generated as the {consequence} consequence of a recorded contradiction",
            owner=owner,
            origin=declaration.artifact_id,
        )
        produced.append(subject)
    return tuple(produced)


def _generated_relation(declaration: Declaration) -> str:
    """The declared relation for a consequence. Found by inverse, never written as a literal."""
    for spec in declaration.relations:
        if spec.inverse == "generated":
            return spec.relation
    raise SubjectError("no declared relation carries the generated inverse")


# --- learning -----------------------------------------------------------------------------


def start_lesson(
    ledger: KnowledgeLedger, *, natural_key: str, owner: str, origin: str, domain: str | None = None
) -> GovernedEntity:
    """Admit a candidate lesson at the first declared stage of the pipeline."""
    declaration = ledger.declaration
    first = declaration.learning_stages[0].identifier
    entity = ledger.subject(
        natural_key=natural_key,
        profile=declaration.profile_for(LESSON_ROLE),
        domain=domain or declaration.residual_domain,
        owner=owner,
        origin=origin,
        payload={"stage": first},
        evidence=(Evidence(source=origin, statement=f"observed: {natural_key}"),),
        lineage=Lineage(presented_by=origin),
    )
    return ledger.admit(entity)


def advance(ledger: KnowledgeLedger, identity: str, *, to_stage: str, basis: str) -> GovernedEntity:
    """Advance a lesson exactly one declared stage. Any skip is refused.

    The pipeline is ordered and this is the only way through it, which is what makes the bypass law
    measurable: there is one door, and it only opens onto the next room.
    """
    declaration = ledger.declaration
    stages = [spec.identifier for spec in declaration.learning_stages]
    if to_stage not in stages:
        raise SubjectError(f"{to_stage!r} is not a declared learning stage")
    entity = ledger.get(identity)
    current = str(entity.payload.get("stage") or "")
    if current not in stages:
        raise SubjectError(f"{identity!r} rests at {current!r}, which is not a declared stage")
    if stages.index(to_stage) != stages.index(current) + 1:
        position = stages.index(current) + 1
        following = stages[position] if position < len(stages) else "no further stage"
        raise SubjectError(
            f"the pipeline permits no move from {current!r} to {to_stage!r}; "
            f"the next stage is {following!r}"
        )
    if not basis.strip():
        raise SubjectError("a pipeline advance must name its basis")
    payload = dict(entity.payload)
    payload["stage"] = to_stage
    return ledger.amend(replace(entity, payload=payload), event="advanced")


def reverse_lesson(
    ledger: KnowledgeLedger, identity: str, *, by: str, basis: str
) -> GovernedEntity:
    """Reverse a lesson by supersession, never by deletion. The declared reversal operator."""
    return ledger.supersede(identity, by=by, basis=basis)


def payload_of(entity: GovernedEntity) -> dict[str, Any]:
    return dict(entity.payload)


__all__ = [
    "CONFLICT_ROLE",
    "DISCLOSURE_ROLE",
    "LESSON_ROLE",
    "LedgerError",
    "SubjectError",
    "add_resolution",
    "add_verification",
    "admit_disclosed_gap",
    "advance",
    "close_gap",
    "generate_consequences",
    "overdue",
    "payload_of",
    "record_contradiction",
    "record_gap",
    "reverse_lesson",
    "satisfy",
    "start_lesson",
]
