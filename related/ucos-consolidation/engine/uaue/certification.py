"""UAUE — AUE-P-09, the evolution certification engine (UAUE-000001, Epoch 3).

**No certificate is issued here.** The universal certification pipeline is the sole issuer of
certificates in this repository, and it issues them for artifacts from validation, measurement
and repository-truth inputs. This module does not call it, does not imitate it, and does not
produce anything a reader could mistake for a certificate.

What it produces is the set of eight declared *proofs* that make an evolution transaction
certifiable — was authorised, was understood, was planned, was executed correctly, has evidence,
has validation, has verification, has history. These are the proofs that are specific to an
evolution transaction and could not be expressed as a certification rule over a static object:
the pipeline cannot ask "did this chain produce an understanding object", because the pipeline
has no concept of a chain.

A proof is satisfied only when the thing it names actually exists in the chain. In particular
"has validation" and "has verification" require a *measured* verdict, not a present field: a
chain carrying the word "PASS" with nothing behind it fails, which is the difference between
certifying an evolution and certifying a string.
"""

from __future__ import annotations

from engine.uaue.model import EvolutionAuthority, EvolutionAuthorityError
from engine.uaue.objects import (
    CriterionOutcome,
    EvolutionChain,
    EvolutionObject,
    Verdict,
    phase_object,
)

_CERTIFICATION_ORDINAL = 9


def _was_authorized(authority: EvolutionAuthority, chain: EvolutionChain) -> tuple[bool, str]:
    gates = {phase.identifier: phase.gate.command for phase in authority.phases}
    unauthorised = [
        obj.object_kind
        for obj in chain.objects
        if not obj.authority or not gates.get(obj.phase, "")
    ]
    if unauthorised:
        return False, f"objects with no named authority or gate: {sorted(set(unauthorised))}"
    return True, f"all {len(chain.objects)} objects resolve under a named authority and gate"


def _was_understood(chain: EvolutionChain) -> tuple[bool, str]:
    understanding = chain.understanding
    if understanding is None:
        return False, "the chain produced no understanding object"
    answers = {
        "why": understanding.why,
        "what changes": understanding.target_state,
        "what depends": understanding.dependencies,
        "what breaks": understanding.breaks,
        "what evidence": understanding.obj.evidence,
    }
    unanswered = sorted(name for name, value in answers.items() if not value)
    if unanswered:
        return False, f"understanding leaves questions unanswered: {unanswered}"
    return True, "understanding answers why, what, what depends, what breaks and what evidence"


def _was_planned(chain: EvolutionChain) -> tuple[bool, str]:
    if chain.plan is None:
        return False, "the chain produced no plan object"
    unplanned = [obj.object_kind for obj in chain.objects if not obj.plan]
    # The objects of the phases that precede planning cannot carry a plan that did not yet
    # exist, so the obligation is measured over the planning phase and everything after it.
    planning_ordinal = min((obj.phase for obj in chain.objects if obj.plan), default="", key=str)
    if unplanned and planning_ordinal == "":
        return False, "no object carries the plan"
    downstream_unplanned = [
        obj.object_kind for obj in chain.objects if not obj.plan and obj.phase >= planning_ordinal
    ]
    if downstream_unplanned:
        return False, f"downstream objects not carrying the plan: {downstream_unplanned}"
    return True, f"plan present and carried by every object from {planning_ordinal} onward"


def _was_executed_correctly(chain: EvolutionChain) -> tuple[bool, str]:
    execution = chain.execution
    if execution is None:
        return False, "the chain produced no execution object"
    if execution.mutation_performed:
        return False, "the execution object claims a mutation, which this register never performs"
    if not execution.authorised:
        return False, f"execution was not authorised: {'; '.join(execution.refusals)}"
    if not execution.path_resolves or not execution.gate_wired:
        return False, "the authorised mutation path or its gate does not resolve"
    return True, (
        f"execution bound to the single authorised path {execution.mutation_path} "
        f"behind {execution.gate}, with no mutation performed here"
    )


def _has_evidence(chain: EvolutionChain) -> tuple[bool, str]:
    empty = [obj.object_kind for obj in chain.objects if not obj.evidence]
    if empty:
        return False, f"objects carrying an empty evidence set: {sorted(set(empty))}"
    return True, f"no object of {len(chain.objects)} carries an empty evidence set"


def _has_validation(chain: EvolutionChain) -> tuple[bool, str]:
    if chain.validation is None or not chain.validation.outcomes:
        return False, "the chain carries no measured validation verdict"
    if not chain.validation.passed:
        failures = [entry.identifier for entry in chain.validation.blocking_failures]
        return False, f"validation refused: {failures}"
    return True, chain.validation.summary


def _has_verification(chain: EvolutionChain) -> tuple[bool, str]:
    if chain.verification is None or not chain.verification.outcomes:
        return False, "the chain carries no measured verification verdict"
    if not chain.verification.passed:
        failures = [entry.identifier for entry in chain.verification.blocking_failures]
        return False, f"verification refused: {failures}"
    return True, chain.verification.summary


def _has_history(authority: EvolutionAuthority, chain: EvolutionChain) -> tuple[bool, str]:
    """Every object appears in the history projection, and the projection rehydrates.

    Measured by actually projecting and rehydrating, through the ledger that owns the append
    rules — so this proof fails if the history cannot be read back under the same rules that
    wrote it, rather than passing because a file exists.
    """
    from engine.uaue.history import project_history, rehydrate_history

    try:
        document = project_history(chain, authority)
        rehydrated = rehydrate_history(document)
    except Exception as error:  # noqa: BLE001 — an unrehydratable history is a failed proof
        return False, f"the history projection does not rehydrate: {error}"
    recorded = {record.subject for record in rehydrated.records()}
    missing = [obj.evolution_id for obj in chain.objects if obj.evolution_id not in recorded]
    if missing:
        return False, f"{len(missing)} objects are absent from the history projection"
    return True, (
        f"{len(rehydrated)} records projected and rehydrated under "
        f"{authority.history.ledger_home}"
    )


def certify_evolution(
    chain: EvolutionChain,
    authority: EvolutionAuthority,
) -> Verdict:
    """Measure the eight declared certification proofs over one chain.

    Args:
        chain: the chain to judge. It must already carry its validation and verification
            verdicts; a chain judged before it was validated fails those proofs by construction.
        authority: the rehydrated authority, whose ``certifications`` block is the proof list.

    Returns:
        A :class:`~engine.uaue.objects.Verdict`. Certification standing can never exceed the
        standing of the owners the declaration binds, so a passing verdict here means the proofs
        hold — not that a certificate was issued.
    """
    phase = next(entry for entry in authority.phases if entry.ordinal == _CERTIFICATION_ORDINAL)
    owner = phase.owners[0].home if phase.owners else ""

    outcomes: list[CriterionOutcome] = []
    for criterion in authority.certifications:
        proof = criterion.subject.strip().lower()
        if proof == "was authorized":
            satisfied, detail = _was_authorized(authority, chain)
        elif proof == "was understood":
            satisfied, detail = _was_understood(chain)
        elif proof == "was planned":
            satisfied, detail = _was_planned(chain)
        elif proof == "was executed correctly":
            satisfied, detail = _was_executed_correctly(chain)
        elif proof == "has evidence":
            satisfied, detail = _has_evidence(chain)
        elif proof == "has validation":
            satisfied, detail = _has_validation(chain)
        elif proof == "has verification":
            satisfied, detail = _has_verification(chain)
        elif proof == "has history":
            satisfied, detail = _has_history(authority, chain)
        else:
            satisfied, detail = (
                False,
                "the declaration adds a certification proof this engine cannot measure",
            )
        outcomes.append(
            CriterionOutcome(
                identifier=criterion.identifier,
                subject=criterion.subject,
                obligation=criterion.obligation,
                satisfied=satisfied,
                blocking=criterion.blocking,
                detail=detail,
                owner=owner,
            )
        )
    return Verdict(subject=f"certification of {chain.evolution_id}", outcomes=tuple(outcomes))


def certification_object(
    chain: EvolutionChain, verdict: Verdict, authority: EvolutionAuthority
) -> EvolutionObject:
    """The certification phase's own object, carrying the measured proofs' verdict."""
    previous = chain.objects[-1] if chain.objects else None
    if previous is None:
        raise EvolutionAuthorityError(
            "a chain with no prior object cannot be certified", subject=chain.subject_identity
        )
    return phase_object(
        authority,
        previous,
        ordinal=_CERTIFICATION_ORDINAL,
        certification_result=verdict.summary,
        note={"certified_by": authority.phase_by_ordinal(_CERTIFICATION_ORDINAL).identifier},
    )


__all__ = ["certification_object", "certify_evolution"]
