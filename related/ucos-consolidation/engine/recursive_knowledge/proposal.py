"""URKE-000001 Part 11 — the architectural change proposal, and the test that comes before it.

Architecture is a governed subject: it may evolve, and it may not evolve silently. The order matters
and it is enforced here rather than recommended anywhere.

:func:`representability` runs first and is a computation, not a judgement. Given a condition, it
either returns the composition that expresses it — in which case the answer is a data extension and
no proposal is warranted — or it returns the reason no composition does. "Architecture evolves by
evidence, not by anticipation" is that function being called before :func:`propose` is.

:func:`propose` refuses a proposal missing any declared requirement. A proposal that could be
recorded incomplete would be an architectural mutation with a paper trail that reads as governance.
"""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from engine.recursive_knowledge.composition import CompositionError, express
from engine.recursive_knowledge.declaration import Declaration
from engine.recursive_knowledge.ledger import KnowledgeLedger
from engine.recursive_knowledge.model import (
    Evidence,
    GovernedEntity,
    Lineage,
    RecursiveKnowledgeError,
)

#: The role a proposal is admitted under. A code symbol the declaration binds to a profile.
PROPOSAL_ROLE = "change_proposal"


class ProposalError(RecursiveKnowledgeError):
    """The proposal is incomplete, or representability was not measured. A fault."""


def representability(
    declaration: Declaration,
    *,
    state: str,
    domain: str,
    axes: Mapping[str, str] | None = None,
    qualifiers: Mapping[str, str] | None = None,
) -> dict[str, Any]:
    """Measure whether the existing primitives express a condition. Step two of the default rule.

    Returns ``representable`` with either the composition or the reason. It never raises for an
    unrepresentable condition, because "we cannot express this" is the finding, not an error.
    """
    try:
        expression = express(
            declaration, state=state, domain=domain, axes=axes, qualifiers=qualifiers
        )
    except (CompositionError, RecursiveKnowledgeError) as exc:
        return {
            "expression": None,
            "reason": str(exc),
            "representable": False,
            "verdict": "an architectural change proposal is warranted",
        }
    return {
        "expression": dict(expression),
        "reason": "",
        "representable": True,
        "verdict": "extend data only; no architectural change is warranted",
    }


def propose(
    ledger: KnowledgeLedger,
    *,
    construct: str,
    unrepresentable_because: str,
    capability_gained: str,
    complexity_added: str,
    tradeoff_justification: str,
    impact: str,
    verification: str,
    validation: str,
    governance_decision: str,
    owner: str,
) -> GovernedEntity:
    """Admit a proposal to change the foundation. Refuses one missing any declared requirement."""
    declaration = ledger.declaration
    offered = {
        "capability_gained": capability_gained,
        "complexity_added": complexity_added,
        "construct": construct,
        "governance_decision": governance_decision,
        "impact": impact,
        "tradeoff_justification": tradeoff_justification,
        "unrepresentable_because": unrepresentable_because,
        "validation": validation,
        "verification": verification,
    }
    absent = sorted(key for key, value in offered.items() if not str(value).strip())
    if absent:
        raise ProposalError(
            "an architectural change proposal is incomplete without "
            + ", ".join(absent)
            + "; the burden of proof sits on the change"
        )
    entity = ledger.subject(
        natural_key=f"proposal/{construct}",
        profile=declaration.profile_for(PROPOSAL_ROLE),
        domain=declaration.residual_domain,
        owner=owner,
        origin="architecture_evolution",
        title=f"proposed architectural change: {construct}",
        payload=offered,
        evidence=(Evidence(source="architecture_evolution", statement=unrepresentable_because),),
        lineage=Lineage(presented_by=owner),
        resolution_path=tradeoff_justification,
    )
    return ledger.admit(entity)


def proposals(ledger: KnowledgeLedger) -> tuple[GovernedEntity, ...]:
    """Every recorded architectural change proposal. Empty means the foundation has not been "
    "asked."""
    return ledger.of_profile(ledger.declaration.profile_for(PROPOSAL_ROLE))


__all__ = ["PROPOSAL_ROLE", "ProposalError", "proposals", "propose", "representability"]
