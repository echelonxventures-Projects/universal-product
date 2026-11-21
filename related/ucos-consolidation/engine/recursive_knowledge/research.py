"""URKE-000001 Part 07 — research. Any unresolved subject can become one, and it is recursive.

Research is a profile, not a class. Opening research on something does not move or alter it: a new
subject is admitted and linked back with the declared derivation relation, so the original keeps its
own state and history. That is what lets research be recursive without special handling — research
on research is the same call with a different target.

The nine declared research facets are required payload keys. A research subject that carried a
question and nothing else would read as an investigation while recording none of what makes one
auditable: what it depends on, what bounds it, what blocks it, and how confident anybody is.
"""

from __future__ import annotations

from engine.recursive_knowledge.ledger import KnowledgeLedger, relate
from engine.recursive_knowledge.model import Evidence, GovernedEntity, Lineage
from engine.recursive_knowledge.subjects import SubjectError

#: The role research is admitted under. A code symbol the declaration binds to a profile.
INVESTIGATION_ROLE = "investigation"


def open_research(
    ledger: KnowledgeLedger,
    *,
    natural_key: str,
    question: str,
    owner: str,
    origin: str,
    domain: str | None = None,
    derived_from: str = "",
    hypotheses: tuple[str, ...] = (),
    dependencies: tuple[str, ...] = (),
    limitations: tuple[str, ...] = (),
    blockers: tuple[str, ...] = (),
    context: str | None = None,
) -> GovernedEntity:
    """Admit a research subject carrying every declared facet, and link it to what it came from."""
    declaration = ledger.declaration
    if not question.strip():
        raise SubjectError("a research subject must state its question")
    entity = ledger.subject(
        natural_key=natural_key,
        profile=declaration.profile_for(INVESTIGATION_ROLE),
        domain=domain or declaration.residual_domain,
        owner=owner,
        origin=origin,
        context=context,
        title=question,
        payload={
            "blockers": list(blockers) or ["no blocker stated"],
            "confidence": declaration.qualifier(_confidence_qualifier(declaration)).initial,
            "dependencies": list(dependencies) or ["no dependency stated"],
            "experiments": ["no experiment yet"],
            "history": [f"opened from {origin}"],
            "hypotheses": list(hypotheses) or ["no hypothesis yet"],
            "limitations": list(limitations)
            or ["what this investigation cannot settle has not been stated"],
            "outcomes": ["no outcome yet"],
            "questions": [question],
        },
        evidence=(Evidence(source=origin, statement=question, independent=False),),
        lineage=Lineage(derived_from=(derived_from,) if derived_from else (), presented_by=origin),
    )
    admitted = ledger.admit(entity)
    if derived_from and ledger.has(derived_from):
        relate(
            ledger,
            source=admitted.identity,
            target=derived_from,
            relation=_derivation_relation(declaration),
            basis=f"research opened on an unresolved subject: {question}",
            owner=owner,
            origin=declaration.artifact_id,
        )
    return admitted


def _confidence_qualifier(declaration) -> str:  # noqa: ANN001 - declaration type is obvious here
    """The declared qualifier that records how well supported a claim is held to be."""
    return declaration.confidence_qualifier


def _derivation_relation(declaration) -> str:  # noqa: ANN001
    """The declared relation for derivation, found by its inverse rather than written as a "
    "literal."""
    for spec in declaration.relations:
        if spec.inverse == "produced":
            return spec.relation
    raise SubjectError("no declared relation carries the produced inverse")


def research_for(ledger: KnowledgeLedger, identity: str) -> tuple[GovernedEntity, ...]:
    """Every research subject derived from this one. Empty means nothing is investigating it."""
    return tuple(
        item
        for item in ledger.of_profile(ledger.declaration.profile_for(INVESTIGATION_ROLE))
        if identity in item.lineage.derived_from
    )


__all__ = ["INVESTIGATION_ROLE", "open_research", "research_for"]
