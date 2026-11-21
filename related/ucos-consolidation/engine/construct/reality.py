"""UCON-000001 Part 03 — reality status, and the conjunction that keeps it honest.

This module answers *what does the evidence support?* It does not answer, and cannot answer,
*is this construct admitted?* — and that is enforced structurally rather than promised. This
module does not import :mod:`engine.construct.disposition`, that module does not import this
one, and law UCON-L-11 parses both files to confirm neither ever will. Two modules that
cannot see each other cannot derive one answer from the other, which is a stronger guarantee
than a rule saying they must not.

The one place the two facts meet is :func:`permitted_acts`, and they meet as a **conjunction**:

    an act is permitted iff the active disposition permits it AND the active reality state
    permits it.

That single line is the operational form of *admission does not imply truth*. ADMIT permits
``certify``; HYPOTHETICAL does not; so an admitted hypothetical construct cannot be certified,
and no amount of admission changes that. The conjunction reads both from the DECLARATION — it
consults the declared permission sets, never the disposition engine — so this module still has
no dependency on how a disposition came to be assigned.

Assessment never downgrades a claim to make it fit. A presentation claiming VERIFIED on one
piece of evidence is recorded as VERIFIED with ``floor_met`` false, because the interesting
fact is that the claim was made above its floor. Silently rewriting it to OBSERVED would
destroy the only evidence that somebody over-claimed.

No state is terminal. VERIFIED names CONTRADICTED among its successors, because falsification
must stay reachable from the strongest state; a framework in which VERIFIED were terminal
would be asserting that some verification can never be overturned. Law UCON-L-10 measures it.
"""

from __future__ import annotations

from collections.abc import Iterable

from engine.construct.declaration import Declaration, DeclarationError
from engine.construct.model import Construct, ConstructError, Presentation, RealityAssessment


class RealityError(ConstructError):
    """An assessment or transition the declaration does not permit."""


def assess(
    declaration: Declaration,
    presentation: Presentation,
    *,
    sequence: int = 0,
    status: str | None = None,
) -> RealityAssessment:
    """Assess ``presentation`` into a reality state, without consulting any disposition.

    The state is the one the presenter claimed, or the declared initial state when the
    presenter claimed none — and *which* state that is comes from the declaration, because
    "what do we hold when we know nothing" is exactly the kind of assumption that must not be
    a default buried in code.
    """
    claimed = (status or presentation.reality_status or "").strip()
    resolved = claimed or declaration.initial_reality_state
    try:
        spec = declaration.reality(resolved)
    except DeclarationError as exc:
        raise RealityError(
            f"{presentation.identity}: claims undeclared reality state {resolved!r}"
        ) from exc
    evidence_count = presentation.evidence_count
    independent = presentation.independent_sources
    return RealityAssessment(
        identity=presentation.identity,
        status=spec.identifier,
        evidence_count=evidence_count,
        independent_sources=independent,
        assessed_from=tuple(item.evidence_id for item in presentation.evidence),
        sequence=sequence,
        floor_met=(
            evidence_count >= spec.evidence_floor and independent >= spec.independent_sources_floor
        ),
    )


def transition(
    declaration: Declaration,
    current: RealityAssessment,
    to_status: str,
    *,
    sequence: int,
    evidence_count: int | None = None,
    independent_sources: int | None = None,
    assessed_from: Iterable[str] | None = None,
) -> RealityAssessment:
    """The successor assessment, or raise when the declaration forbids the transition.

    Refusing an undeclared transition is what makes the state graph a graph rather than a
    suggestion. The refusal names both endpoints and the successors that were available, so
    the caller learns what the declaration actually allows instead of only that it said no.
    """
    spec = declaration.reality(current.status)
    if to_status not in spec.successors:
        raise RealityError(
            f"{current.identity}: {current.status} -> {to_status} is not a declared "
            f"transition; declared successors are {', '.join(spec.successors) or 'none'}"
        )
    target = declaration.reality(to_status)
    count = current.evidence_count if evidence_count is None else evidence_count
    sources = current.independent_sources if independent_sources is None else independent_sources
    origin = (
        tuple(current.assessed_from)
        if assessed_from is None
        else tuple(str(item) for item in assessed_from)
    )
    return RealityAssessment(
        identity=current.identity,
        status=target.identifier,
        evidence_count=count,
        independent_sources=sources,
        assessed_from=origin,
        sequence=sequence,
        floor_met=(count >= target.evidence_floor and sources >= target.independent_sources_floor),
    )


def reachable_from(declaration: Declaration, start: str) -> frozenset[str]:
    """Every reality state reachable from ``start`` by declared transitions.

    Used by law UCON-L-10 to measure that no state is stranded: a state nothing can reach is a
    state the framework declares and can never occupy, which is a closure disguised as a
    vocabulary member.
    """
    declaration.reality(start)
    seen: set[str] = {start}
    frontier = [start]
    while frontier:
        current = frontier.pop()
        for successor in declaration.reality(current).successors:
            if successor not in seen:
                seen.add(successor)
                frontier.append(successor)
    return frozenset(seen)


def permitted_acts(declaration: Declaration, construct: Construct) -> frozenset[str]:
    """The acts the construct may take: disposition permissions INTERSECT reality permissions.

    This intersection is the whole enforcement of *admission does not imply truth*. Both sets
    are read from the declaration, so this function has no dependency on the disposition
    engine — only on what the declaration says each name permits.
    """
    disposition = declaration.disposition(construct.disposition.disposition)
    reality = declaration.reality(construct.reality.status)
    return frozenset(disposition.permits & reality.permits)


def permits(declaration: Declaration, construct: Construct, act: str) -> bool:
    """True iff ``act`` is permitted by both the active disposition and the active state.

    An act the declaration does not declare is refused rather than defaulted: an undeclared
    act silently permitted would be an operational capability nobody governs.
    """
    if act not in declaration.operational_acts:
        return False
    return act in permitted_acts(declaration, construct)


def refusal(declaration: Declaration, construct: Construct, act: str) -> str:
    """Why ``act`` is refused, naming which side refused it. Empty when it is permitted."""
    if act not in declaration.operational_acts:
        return f"{act!r} is not a declared operational act"
    disposition = declaration.disposition(construct.disposition.disposition)
    reality = declaration.reality(construct.reality.status)
    blockers = []
    if act not in disposition.permits:
        blockers.append(f"disposition {disposition.identifier} does not permit it")
    if act not in reality.permits:
        blockers.append(f"reality state {reality.identifier} does not permit it")
    return "; ".join(blockers)


__all__ = [
    "RealityError",
    "assess",
    "permits",
    "permitted_acts",
    "reachable_from",
    "refusal",
    "transition",
]
