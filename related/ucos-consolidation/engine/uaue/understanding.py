"""UAUE — AUE-P-02, the evolution understanding engine (UAUE-000001, Epoch 3).

Understanding answers five questions about one candidate: why evolve, what changes, what
depends on it, what it can break, and what evidence supports each answer. Every answer is
composed from what a located owner already measured or from what the declaration already
mandates. None is authored here.

That constraint is the point. The temptation in this phase is to *explain* a candidate — to
infer a domain impact from a subject name. An inferred impact would be this register's own
opinion presented as measurement, and it would be unfalsifiable. So:

* **why** is the discovering owner's own words, carried unchanged.
* **what changes** is the measured previous state and the declared target state.
* **what depends on it** is the mandated dependency derivation: the phase's owner homes plus
  the phases it depends on.
* **what can break** is the set of blocking zero-tolerance invariants — the things an evolution
  is not permitted to break, named from the declaration rather than guessed per subject.
* **evidence** is the declared evidence of this phase that resolves, plus the candidate's own.

Meaning, relationship kind and authority tier remain the knowledge model's to define
(``engine/knowledge/model.py``); this phase composes, it does not classify.
"""

from __future__ import annotations

from engine.uaue.authority import dependencies_of
from engine.uaue.model import EvolutionAuthority, EvolutionAuthorityError
from engine.uaue.objects import (
    EvolutionCandidate,
    EvolutionObject,
    EvolutionUnderstanding,
    as_context,
)
from engine.uaue.resolution import Substrate

_UNDERSTANDING_ORDINAL = 2


def understand_evolution(
    candidate: EvolutionCandidate,
    authority: EvolutionAuthority,
    substrate: Substrate | None = None,
) -> EvolutionUnderstanding:
    """Understand one candidate.

    Args:
        candidate: the candidate discovery produced. Its subject and reason are carried
            unchanged, so one chain always describes one subject.
        authority: the rehydrated authority, which supplies the phase, its owners, its
            evidence and the criteria this understanding must be judged against later.
        substrate: the tree used to decide which declared evidence resolves.

    Returns:
        An :class:`~engine.uaue.objects.EvolutionUnderstanding`.

    Raises:
        EvolutionAuthorityError: the candidate carries no evidence that resolves. Understanding
            an unevidenced candidate would produce an explanation with nothing under it.
    """
    substrate = substrate if substrate is not None else Substrate()
    phase = next(entry for entry in authority.phases if entry.ordinal == _UNDERSTANDING_ORDINAL)
    kind = authority.object_kind_of(phase.identifier)

    # The candidate's own evidence must resolve. The phase's declared evidence supports the
    # *phase*; it cannot stand in for the artifact that produced the candidate, or a candidate
    # attributable to nothing would inherit this register's own evidence and look measured.
    attributable = tuple(path for path in candidate.evidence if substrate.resolves(path))
    if not attributable:
        raise EvolutionAuthorityError(
            "a candidate with no resolving evidence cannot be understood",
            subject=candidate.subject_identity,
            candidate=candidate.evolution_id,
            declared=list(candidate.evidence),
        )
    evidence = tuple(dict.fromkeys((*attributable, *phase.resolving_evidence)))

    dependencies = dependencies_of(authority, phase.identifier)
    impact = (
        f"{candidate.previous_state} becomes: {candidate.target_state}",
        *(
            f"impact is bounded by what {phase.authority} measured in {path}"
            for path in phase.resolving_evidence
        ),
    )
    breaks = tuple(
        f"{entry.identifier}: {entry.invariant}" for entry in authority.mandatory if entry.blocking
    )
    validation_requirement = tuple(
        f"{entry.identifier}: {entry.obligation}"
        for entry in authority.validations
        if entry.blocking
    )
    certification_requirement = tuple(
        f"{entry.identifier}: {entry.obligation}" for entry in authority.certifications
    )

    # Risk follows the plan contract: the severity the discovering owner recorded, defaulting
    # to the candidate class where the source declared no severity. Never a severity invented
    # here, because a severity nobody measured would rank a candidate on this engine's opinion.
    risk = candidate.severity or candidate.candidate_class

    obj = EvolutionObject.derive(
        rule=authority.identity,
        candidate=candidate,
        object_kind=kind.identifier,
        phase=phase.identifier,
        lifecycle_state=authority.stage_of(phase.identifier),
        dependencies=dependencies,
        evidence=evidence,
        authority=phase.authority,
        context=as_context(
            {
                **dict(candidate.context),
                "understood_by": phase.identifier,
                "risk": risk,
            }
        ),
    )
    return EvolutionUnderstanding(
        obj=obj,
        why=candidate.reason,
        current_state=candidate.previous_state,
        target_state=candidate.target_state,
        impact=impact,
        dependencies=dependencies,
        risk=risk,
        validation_requirement=validation_requirement,
        certification_requirement=certification_requirement,
        breaks=breaks,
    )


__all__ = ["understand_evolution"]
