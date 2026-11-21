"""URKE-000001 Part 10 — evolution. One mechanism, no special case, and it leaves a record.

:func:`evolve` is the single entry point for every declared subject. It resolves the operator from
the declared table and calls it; there is no branch keyed on which subject is changing, and the law
that measures this parses the module to confirm none has appeared. A special case for one subject is
how a special case for each one begins.

Every step is a subject in the same ledger as everything else, carrying the subject, the operator,
the digest before and the digest after. Evolution of the framework is therefore recorded by the
framework, which is what makes it traceable rather than described — and what makes tampering with
the record detectable through the same chain check as anything else.
"""

from __future__ import annotations

from collections.abc import Callable, Mapping
from types import MappingProxyType
from typing import Any

from engine.recursive_knowledge.ledger import KnowledgeLedger
from engine.recursive_knowledge.model import (
    Evidence,
    GovernedEntity,
    Lineage,
    RecursiveKnowledgeError,
)

#: The role an evolution step is admitted under. A code symbol the declaration binds to a profile.
CHANGE_ROLE = "change_record"


class EvolutionError(RecursiveKnowledgeError):
    """The evolution step cannot be recorded as declared. A fault, never a refusal to evolve."""


def _step(
    ledger: KnowledgeLedger,
    *,
    subject: str,
    operator: str,
    before: str,
    after: str,
    basis: str,
    owner: str,
) -> GovernedEntity:
    declaration = ledger.declaration
    entity = ledger.subject(
        natural_key=f"{subject}/{operator}/{after[:16]}",
        profile=declaration.profile_for(CHANGE_ROLE),
        domain=declaration.residual_domain,
        owner=owner,
        origin=declaration.evolution_entry_point,
        title=f"{operator} {subject}",
        payload={"after": after, "before": before, "operator": operator, "subject": subject},
        evidence=(Evidence(source=declaration.evolution_entry_point, statement=basis),),
        lineage=Lineage(presented_by=owner),
    )
    return ledger.admit(entity)


def operator_extend(ledger: KnowledgeLedger, **step: Any) -> GovernedEntity:
    """Add a member. Narrowing is not expressible through this operator, by construction."""
    return _step(ledger, **step)


def operator_refine(ledger: KnowledgeLedger, **step: Any) -> GovernedEntity:
    """Change a definition or a binding without removing a member. The declared replacement path."""
    return _step(ledger, **step)


def operator_supersede(ledger: KnowledgeLedger, **step: Any) -> GovernedEntity:
    """Replace a member with a named later one, retaining the earlier. The declared recovery "
    "path."""
    return _step(ledger, **step)


def operator_bind(ledger: KnowledgeLedger, **step: Any) -> GovernedEntity:
    """Attach a locally held vocabulary to the authority that owns it, closing a binding gap."""
    return _step(ledger, **step)


#: Every declared operator, mapped to its implementation. Bound both ways at load time.
OPERATORS: Mapping[str, Callable[..., GovernedEntity]] = MappingProxyType(
    {
        "operator_bind": operator_bind,
        "operator_extend": operator_extend,
        "operator_refine": operator_refine,
        "operator_supersede": operator_supersede,
    }
)


def available_operators() -> frozenset[str]:
    return frozenset(OPERATORS)


def evolve(
    ledger: KnowledgeLedger,
    *,
    subject: str,
    operator: str,
    before: str,
    after: str,
    basis: str,
    owner: str,
) -> GovernedEntity:
    """The one entry point. Refuses a subject the declaration does not declare evolvable this "
    "way."""
    declaration = ledger.declaration
    spec = next(
        (item for item in declaration.evolution_subjects if item.identifier == subject), None
    )
    if spec is None:
        raise EvolutionError(f"{subject!r} is not a declared evolution subject")
    if operator not in spec.operators:
        raise EvolutionError(
            f"the declaration does not permit {operator!r} on {subject!r}; permitted operators are "
            f"{', '.join(spec.operators)}"
        )
    implementation = next(
        (item.implementation for item in declaration.operators if item.identifier == operator), ""
    )
    function = OPERATORS.get(implementation)
    if function is None:
        raise EvolutionError(
            f"operator {operator!r} names {implementation!r}, which is not implemented"
        )
    if not basis.strip():
        raise EvolutionError("an evolution step must name its basis")
    if before == after:
        raise EvolutionError(
            f"the step on {subject!r} records the same digest before and after, so it records no "
            f"change"
        )
    return function(
        ledger,
        subject=subject,
        operator=operator,
        before=before,
        after=after,
        basis=basis,
        owner=owner,
    )


def trace(ledger: KnowledgeLedger, subject: str) -> tuple[GovernedEntity, ...]:
    """Every recorded step against one subject, in ledger order. The reconstructible history."""
    role = ledger.declaration.profile_for(CHANGE_ROLE)
    return tuple(
        sorted(
            (item for item in ledger.of_profile(role) if item.payload.get("subject") == subject),
            key=lambda item: item.sequence,
        )
    )


__all__ = [
    "CHANGE_ROLE",
    "OPERATORS",
    "EvolutionError",
    "available_operators",
    "evolve",
    "operator_bind",
    "operator_extend",
    "operator_refine",
    "operator_supersede",
    "trace",
]
