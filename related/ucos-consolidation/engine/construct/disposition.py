"""UCON-000001 Part 04 — the disposition engine. A total function, or it is not an engine.

Every presented construct receives exactly one disposition. Not "usually", not "when a rule
matches": *always*, and the totality is structural rather than hoped for. The rule set is
ordered, first-match-wins, and the declaration's last rule must be the catch-all — checked at
load by :meth:`Declaration.validate`, so a rule set that could miss cannot be loaded at all.
:func:`dispose` therefore has no code path that returns nothing, and no code path that raises
because a construct was unwelcome.

The catch-all disposition is ESCALATE and law UCON-L-03 refuses any other. This is the single
most consequential line in the capability. A catch-all of REJECT would discard precisely the
constructs the rule set failed to anticipate — the unforeseen, the future-originated, the
currently unrepresentable — and it would do so while reporting a clean, total, fully-covered
run. ESCALATE says the honest thing instead: no declared rule decided this, so an authority
must, and here is the construct, recorded, waiting.

This module reads no reality module and no registry. It is given a :class:`Context` — a
read-only view of the four facts about the surrounding state that any rule may need — and is
otherwise a pure function of the declaration and the presentation. That is what makes the
whole engine testable by construction and what lets law UCON-L-11 prove that reality status is
not derived from admission: this file does not import :mod:`engine.construct.reality`, and it
never will, because the reality status it needs arrives as a plain string on the presentation.

Operators are code and rules are data, and the boundary between them is measured. Law
UCON-L-04 refuses in both directions: a rule naming an operator :data:`OPERATORS` does not
implement is manual governance, and an operator :data:`OPERATORS` implements that no rule
claims is dead code that looks like enforcement. Adding a *rule* is a declaration edit; adding
an *operator* is a code change plus a rule that uses it, and there is no third option that
lets either drift.
"""

from __future__ import annotations

from collections.abc import Callable, Mapping
from dataclasses import dataclass, field
from typing import Any

from engine.construct.declaration import Clause, Declaration, Rule
from engine.construct.model import ConstructError, DispositionRecord, Presentation


class DispositionError(ConstructError):
    """A rule could not be evaluated. A fault, never a disposition.

    Reserved for a malformed clause — a declared operator missing its declared argument. It is
    never raised because a construct is unknown or unwelcome: those are dispositions.
    """


@dataclass(frozen=True, slots=True)
class Context:
    """The surrounding state a rule may consult. Read-only, and deliberately tiny.

    Five facts, no more. A context that could reach the whole registry would let a rule depend
    on anything, and then "why did this construct get this disposition" would be answerable only
    by re-running the engine against the exact same world.

    ``reality_status`` is the RESOLVED state — the one the assessment settled on, which for a
    presentation that claimed nothing is the declared initial state rather than an empty string.
    It arrives here as a plain string precisely so that this module never imports
    :mod:`engine.construct.reality`. Note the direction: a declared rule may consult reality to
    decide a disposition, because operational behaviour is *required* to depend on status. What
    is forbidden is the reverse — deriving reality from admission — and that is what law
    UCON-L-11 measures.
    """

    registered_kinds: frozenset[str] = frozenset()
    registered_identities: frozenset[str] = frozenset()
    contradicted: frozenset[str] = frozenset()
    research_states: Mapping[str, str] = field(default_factory=dict)
    reality_status: str = ""


# --- the operators ---------------------------------------------------------------------------
#
# One function per declared operator name. Each is a pure predicate over
# (presentation, context, arguments). A missing declared argument is a FAULT, because a clause
# that cannot be evaluated must not quietly evaluate to False — a silently false clause is a
# rule that stops firing without anybody being told.


def _argument(arguments: Mapping[str, Any], name: str, operator: str) -> Any:
    if name not in arguments:
        raise DispositionError(f"operator {operator!r} requires argument {name!r}")
    return arguments[name]


def _always(presentation: Presentation, context: Context, arguments: Mapping[str, Any]) -> bool:
    """The catch-all predicate. True for every construct, by definition."""
    return True


def _escalation_requested(
    presentation: Presentation, context: Context, arguments: Mapping[str, Any]
) -> bool:
    return presentation.escalation_requested


def _declared_undecidable(
    presentation: Presentation, context: Context, arguments: Mapping[str, Any]
) -> bool:
    return presentation.declared_undecidable


def _has_contradiction(
    presentation: Presentation, context: Context, arguments: Mapping[str, Any]
) -> bool:
    return presentation.identity in context.contradicted


def _kind_unregistered(
    presentation: Presentation, context: Context, arguments: Mapping[str, Any]
) -> bool:
    return presentation.kind not in context.registered_kinds


def _kind_in(presentation: Presentation, context: Context, arguments: Mapping[str, Any]) -> bool:
    kinds = _argument(arguments, "kinds", "kind_in")
    return presentation.kind in {str(k) for k in kinds}


def _research_state_in(
    presentation: Presentation, context: Context, arguments: Mapping[str, Any]
) -> bool:
    states = {str(s) for s in _argument(arguments, "states", "research_state_in")}
    declared = presentation.payload.get("research_state")
    if isinstance(declared, str) and declared:
        return declared in states
    return context.research_states.get(presentation.identity, "") in states


def _has_unresolved_dependency(
    presentation: Presentation, context: Context, arguments: Mapping[str, Any]
) -> bool:
    return any(
        dependency not in context.registered_identities for dependency in presentation.dependencies
    )


def _attribute_equals(
    presentation: Presentation, context: Context, arguments: Mapping[str, Any]
) -> bool:
    field_name = str(_argument(arguments, "field", "attribute_equals"))
    expected = _argument(arguments, "value", "attribute_equals")
    return presentation.payload.get(field_name) == expected


def _reality_status_in(
    presentation: Presentation, context: Context, arguments: Mapping[str, Any]
) -> bool:
    """Read the RESOLVED status, falling back to what the presenter claimed.

    The resolved value is used because the raw field is empty whenever the presenter claimed
    nothing, and an empty string matches no declared state — so reading the raw field would make
    this operator silently stop firing for exactly the constructs that established least. That
    is a rule that quietly went dark, which is worse than a rule that never existed.
    """
    states = {str(s) for s in _argument(arguments, "states", "reality_status_in")}
    return (context.reality_status or presentation.reality_status) in states


def _evidence_count_below(
    presentation: Presentation, context: Context, arguments: Mapping[str, Any]
) -> bool:
    return presentation.evidence_count < int(_argument(arguments, "count", "evidence_count_below"))


def _evidence_present(
    presentation: Presentation, context: Context, arguments: Mapping[str, Any]
) -> bool:
    return presentation.evidence_count > 0


#: The implemented operator set. Two-way bound to the declared rules by law UCON-L-04: nothing
#: here may go unclaimed, and nothing claimed may be absent here.
OPERATORS: Mapping[str, Callable[[Presentation, Context, Mapping[str, Any]], bool]] = {
    "always": _always,
    "attribute_equals": _attribute_equals,
    "declared_undecidable": _declared_undecidable,
    "escalation_requested": _escalation_requested,
    "evidence_count_below": _evidence_count_below,
    "evidence_present": _evidence_present,
    "has_contradiction": _has_contradiction,
    "has_unresolved_dependency": _has_unresolved_dependency,
    "kind_in": _kind_in,
    "kind_unregistered": _kind_unregistered,
    "reality_status_in": _reality_status_in,
    "research_state_in": _research_state_in,
}


def available_operators() -> frozenset[str]:
    """The operator names this module implements — the registry law UCON-L-04 reads."""
    return frozenset(OPERATORS)


# --- evaluation ------------------------------------------------------------------------------


def evaluate_clause(clause: Clause, presentation: Presentation, context: Context) -> bool:
    """Evaluate one clause. An unimplemented operator is a fault, never a false clause."""
    operator = OPERATORS.get(clause.operator)
    if operator is None:
        raise DispositionError(
            f"operator {clause.operator!r} is declared by a rule but not implemented"
        )
    return operator(presentation, context, clause.arguments)


def matches(rule: Rule, presentation: Presentation, context: Context) -> bool:
    """True iff every clause of ``rule`` holds. Clauses conjoin; rules are the disjunction."""
    return all(evaluate_clause(clause, presentation, context) for clause in rule.when)


def select_rule(declaration: Declaration, presentation: Presentation, context: Context) -> Rule:
    """The first rule that matches. Total: the declaration's last rule matches everything.

    The fallback at the end is not a defensive default — it is unreachable, and it is written
    as a fault rather than as ``declaration.catch_all`` so that if the load-time totality check
    were ever weakened, the failure would be loud here instead of silently selecting a rule
    that had stopped being last.
    """
    for rule in declaration.rules:
        if matches(rule, presentation, context):
            return rule
    raise DispositionError(
        f"{presentation.identity}: no rule matched, which means the declared catch-all is "
        "not total — the rule set was loaded in a state Declaration.validate should have refused"
    )


def dispose(
    declaration: Declaration,
    presentation: Presentation,
    *,
    context: Context | None = None,
    sequence: int = 0,
) -> DispositionRecord:
    """Assign exactly one disposition to ``presentation``, traceably.

    Returns a record naming the rule that decided it and the rationale that rule declares, so
    the answer to "why" is in the record and needs no replay. The record also pins the
    presentation's content digest, so a disposition that outlived a change to its subject is
    detectable rather than merely stale.
    """
    resolved = context if context is not None else Context()
    rule = select_rule(declaration, presentation, resolved)
    declaration.disposition(rule.disposition)
    return DispositionRecord(
        identity=presentation.identity,
        disposition=rule.disposition,
        rule_id=rule.rule_id,
        rationale=rule.rationale,
        sequence=sequence,
        inputs_digest=presentation.content_digest(),
    )


def trace(
    declaration: Declaration, presentation: Presentation, *, context: Context | None = None
) -> tuple[dict[str, Any], ...]:
    """Every rule, in order, with whether it matched and which clause first failed.

    The audit trail behind a disposition: not only which rule won, but which rules were
    consulted and rejected. A disposition whose reason cannot be reconstructed is a disposition
    nobody can contest.
    """
    resolved = context if context is not None else Context()
    rows: list[dict[str, Any]] = []
    decided = False
    for rule in declaration.rules:
        clauses = []
        matched = True
        for clause in rule.when:
            holds = evaluate_clause(clause, presentation, resolved)
            clauses.append({"holds": holds, "operator": clause.operator})
            matched = matched and holds
        rows.append(
            {
                "clauses": clauses,
                "consulted": not decided,
                "disposition": rule.disposition,
                "matched": matched,
                "rule_id": rule.rule_id,
                "selected": matched and not decided,
            }
        )
        decided = decided or matched
    return tuple(rows)


__all__ = [
    "OPERATORS",
    "Context",
    "DispositionError",
    "available_operators",
    "dispose",
    "evaluate_clause",
    "matches",
    "select_rule",
    "trace",
]
