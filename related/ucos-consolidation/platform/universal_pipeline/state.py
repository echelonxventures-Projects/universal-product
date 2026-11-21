"""UAPF-000001 — the Universal State Engine (execution-unit lifecycle).

The lifecycle of an execution unit is **Repository Truth**, not a UAPF invention. The
states, the legal transition table and the illegal transitions transcribed below are the
ones ``06-IMPLEMENTATION-STATE-MACHINE.md`` already legislates; this module is the
executable projection of that document and adds no state, no edge and no authority of
its own. If the document changes, this table changes with it — and
:func:`state_machine` renders the table so a gate can compare the projection against
the source instead of trusting it.

Why a table and not code
------------------------
:data:`_LEGAL_TRANSITIONS` is declared data, and every decision this module makes is a
lookup in it. There is no ``if state == "READY"`` anywhere, so the §4 illegal
transitions are rejected *because they are absent from the table* rather than because
someone remembered to forbid them — which is why the list of illegal transitions needs
no code at all and cannot fall out of step with the legal one.

Forward-only, with one located exception
----------------------------------------
Transitions are forward-only (AIF-L17, ``08-LIFECYCLE-FRAMEWORK.md`` LR-5). The single
exception located in Repository Truth is the bounded ``FAILED → READY`` retry edge
(``05-BATCH-GENERATION-RULES.md`` R1), so the machine is acyclic apart from that one
loop and the loop is capped: :func:`require_retry_budget` enforces the cap, and
exhaustion routes to ``ARCHIVED`` with an escalation rather than being dropped silently.

``ARCHIVED`` is absolutely terminal — it has no outbound edge, so no recorded unit can
ever leave it. Determinism: every function here is a pure lookup, so the same pair of
states always yields the same verdict.
"""

from __future__ import annotations

from platform.universal_pipeline.errors import PipelineStateError
from typing import Any

#: The ten execution-unit states, in the order ``06-IMPLEMENTATION-STATE-MACHINE.md``
#: §1 declares them.
EXECUTION_UNIT_STATES: tuple[str, ...] = (
    "SPECIFIED",
    "READY",
    "EXECUTING",
    "IMPLEMENTED",
    "VALIDATED",
    "CERTIFIED",
    "FAILED",
    "BLOCKED",
    "SUPERSEDED",
    "ARCHIVED",
)

#: The state every unit enters at admission (§1: design-complete, unrealized).
INITIAL_STATE = "SPECIFIED"

#: The state a unit must hold to be certified complete (§2 ``VALIDATED → CERTIFIED``).
CERTIFIED_STATE = "CERTIFIED"

#: States §6 calls terminal: a unit in one of these has left every active queue.
TERMINAL_STATES: frozenset[str] = frozenset({"SUPERSEDED", "ARCHIVED"})

#: The default retry cap. ``05-BATCH-GENERATION-RULES.md`` §9 and
#: ``09-EXECUTION-GOVERNANCE.md`` make ``MAX_RETRY`` a *fixed operational parameter* set
#: by the operator, explicitly **not** a per-run manual choice — so it is a default
#: carried here and overridable per platform, never a per-unit decision.
DEFAULT_MAX_RETRY = 3

#: The legal transition table, transcribed from §2. ``any active → SUPERSEDED`` (the
#: final §2 row) is expanded onto every non-terminal state rather than special-cased in
#: code, so canonical replacement needs no branch.
_LEGAL_TRANSITIONS: dict[str, frozenset[str]] = {
    "SPECIFIED": frozenset({"READY", "BLOCKED", "ARCHIVED", "SUPERSEDED"}),
    "READY": frozenset({"EXECUTING", "BLOCKED", "SUPERSEDED"}),
    "EXECUTING": frozenset({"IMPLEMENTED", "FAILED", "SUPERSEDED"}),
    "IMPLEMENTED": frozenset({"VALIDATED", "FAILED", "SUPERSEDED"}),
    "VALIDATED": frozenset({"CERTIFIED", "FAILED", "SUPERSEDED"}),
    "CERTIFIED": frozenset({"ARCHIVED", "SUPERSEDED"}),
    "FAILED": frozenset({"READY", "BLOCKED", "ARCHIVED", "SUPERSEDED"}),
    "BLOCKED": frozenset({"READY", "SUPERSEDED"}),
    "SUPERSEDED": frozenset({"ARCHIVED"}),
    "ARCHIVED": frozenset(),
}

#: The gate code ``06-IMPLEMENTATION-STATE-MACHINE.md`` §4 requires an illegal
#: transition to be logged under. Carried on the raised error so the rejection is
#: recognizable by the code Repository Truth names, not by message text.
ILLEGAL_TRANSITION_CODE = "GATE:ILLEGAL-TRANSITION"

#: The four conditions ``09-EXECUTION-GOVERNANCE.md`` reserves to a human decision.
#: Everything else continues automatically, so autonomy has exactly one exit and it
#: names its reason (see :class:`~platform.universal_pipeline.errors.PipelineExceptionEscalation`).
ESCALATION_REASONS: tuple[str, ...] = (
    "conflicting-canonical-authority",
    "constitutional-ambiguity",
    "explicit-human-decision-required",
    "missing-external-authority",
)


def require_state(state: str) -> None:
    """Fail closed unless ``state`` is one of the ten declared states.

    Raises:
        PipelineStateError: naming the unknown state.
    """
    if state not in _LEGAL_TRANSITIONS:
        raise PipelineStateError(
            "unknown execution-unit state",
            state=state,
            declared=len(EXECUTION_UNIT_STATES),
        )


def legal_transitions(state: str) -> tuple[str, ...]:
    """The states ``state`` may legally advance to, sorted (deterministic).

    Empty exactly for ``ARCHIVED``, which is absolutely terminal.
    """
    require_state(state)
    return tuple(sorted(_LEGAL_TRANSITIONS[state]))


def is_legal_transition(from_state: str, to_state: str) -> bool:
    """True iff ``from_state → to_state`` appears in the §2 legal table."""
    require_state(from_state)
    require_state(to_state)
    return to_state in _LEGAL_TRANSITIONS[from_state]


def require_unit_transition(from_state: str, to_state: str) -> None:
    """Fail closed unless ``from_state → to_state`` is legal.

    The single guard every UAPF state change passes through: a unit's state is only ever
    advanced here, so an illegal transition is impossible to record rather than merely
    discouraged (§4).

    Raises:
        PipelineStateError: carrying :data:`ILLEGAL_TRANSITION_CODE`, the offending pair
            and the transitions that *were* legal — enough to diagnose without reading
            the table.
    """
    if not is_legal_transition(from_state, to_state):
        raise PipelineStateError(
            "illegal execution-unit state transition",
            gate=ILLEGAL_TRANSITION_CODE,
            from_state=from_state,
            to_state=to_state,
            legal=list(legal_transitions(from_state)),
        )


def is_terminal(state: str) -> bool:
    """True iff ``state`` is one of the terminal states §6 declares."""
    require_state(state)
    return state in TERMINAL_STATES


def is_active(state: str) -> bool:
    """True iff ``state`` is non-terminal — i.e. the unit is still in play."""
    return not is_terminal(state)


def require_retry_budget(attempt: int, *, max_retry: int = DEFAULT_MAX_RETRY) -> None:
    """Fail closed when the bounded ``FAILED → READY`` retry budget is exhausted (R1).

    ``attempt`` is the number of attempts already made. Exhaustion is an error rather
    than a silent stop because R1 requires an exhausted member to be escalated to
    governance and never dropped: the raised error *is* the escalation signal, and the
    caller routes the unit to ``ARCHIVED``.

    Raises:
        PipelineStateError: if ``attempt`` is negative, ``max_retry`` is negative, or
            ``attempt`` has reached ``max_retry``.
    """
    if attempt < 0:
        raise PipelineStateError("attempt count must be non-negative", attempt=attempt)
    if max_retry < 0:
        raise PipelineStateError("max_retry must be non-negative", max_retry=max_retry)
    if attempt >= max_retry:
        raise PipelineStateError(
            "retry budget exhausted (escalate to governance; never dropped)",
            attempt=attempt,
            max_retry=max_retry,
        )


def require_escalation_reason(reason: str) -> None:
    """Fail closed unless ``reason`` is one of the four declared escalation reasons.

    Raises:
        PipelineStateError: naming the rejected reason and the declared set.
    """
    if reason not in ESCALATION_REASONS:
        raise PipelineStateError(
            "unknown escalation reason (autonomy halts only for a declared reason)",
            reason=reason,
            declared=list(ESCALATION_REASONS),
        )


def state_machine() -> dict[str, Any]:
    """The declared machine as a deterministic, serializable mapping (evidence).

    Rendered from the table itself, so a gate comparing this against
    ``06-IMPLEMENTATION-STATE-MACHINE.md`` compares the *projection actually in force*
    rather than a restatement of it.
    """
    return {
        "authority": "06-IMPLEMENTATION-STATE-MACHINE.md",
        "initial_state": INITIAL_STATE,
        "state_count": len(EXECUTION_UNIT_STATES),
        "states": list(EXECUTION_UNIT_STATES),
        "terminal_states": sorted(TERMINAL_STATES),
        "default_max_retry": DEFAULT_MAX_RETRY,
        "escalation_reasons": list(ESCALATION_REASONS),
        "transitions": [
            {"from": state, "to": list(legal_transitions(state))} for state in EXECUTION_UNIT_STATES
        ],
        "transition_count": sum(len(targets) for targets in _LEGAL_TRANSITIONS.values()),
    }


__all__ = [
    "CERTIFIED_STATE",
    "DEFAULT_MAX_RETRY",
    "ESCALATION_REASONS",
    "EXECUTION_UNIT_STATES",
    "ILLEGAL_TRANSITION_CODE",
    "INITIAL_STATE",
    "TERMINAL_STATES",
    "is_active",
    "is_legal_transition",
    "is_terminal",
    "legal_transitions",
    "require_escalation_reason",
    "require_retry_budget",
    "require_state",
    "require_unit_transition",
    "state_machine",
]
