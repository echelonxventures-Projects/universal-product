"""EPIC-007 (Terminal T7) — Execution Lifecycle (Universal Runtime Platform).

The closed, deterministic transition model that governs how a governed execution moves
through the runtime plane — realizing the ``PRS-003`` Runtime Lifecycle service
(start / place / run / settle / compensate). The lifecycle is a *rule structure only*:
it decides which transitions are legal; it performs none of them and runs nothing live.

Because the transition table is fixed data (no wall-clock, no ambient state), the
lifecycle is fully deterministic — identical inputs decide identically. The model is
intentionally small and total so every path is decidable and every illegal transition
fails loudly and auditably:

    pending    → scheduled | cancelled
    scheduled  → placed | cancelled
    placed     → running | cancelled
    running    → succeeded | failed
    succeeded  → compensated                  (governed reversal)
    failed     → scheduled | compensated      (governed retry / saga compensation)
    compensated → (terminal)
    cancelled   → (terminal)
"""

from __future__ import annotations

from platform.runtime_platform.errors import RuntimeLifecycleError

#: The recorded lifecycle vocabulary format.
LIFECYCLE_FORMAT = "ucos-runtime-execution-lifecycle/1.0.0"

# --- the eight canonical execution states ----------------------------------------
PENDING = "pending"
SCHEDULED = "scheduled"
PLACED = "placed"
RUNNING = "running"
SUCCEEDED = "succeeded"
FAILED = "failed"
COMPENSATED = "compensated"
CANCELLED = "cancelled"

#: Every recognized execution state, in canonical order.
EXECUTION_STATES: tuple[str, ...] = (
    PENDING,
    SCHEDULED,
    PLACED,
    RUNNING,
    SUCCEEDED,
    FAILED,
    COMPENSATED,
    CANCELLED,
)

#: The states from which no further transition is legal.
TERMINAL_STATES: frozenset[str] = frozenset({COMPENSATED, CANCELLED})

#: The states that represent a settled (run-complete) execution outcome.
SETTLED_STATES: frozenset[str] = frozenset({SUCCEEDED, FAILED, COMPENSATED, CANCELLED})

#: The canonical, closed lifecycle transition table (``from → allowed to-states``).
LIFECYCLE_TRANSITIONS: dict[str, tuple[str, ...]] = {
    PENDING: (SCHEDULED, CANCELLED),
    SCHEDULED: (PLACED, CANCELLED),
    PLACED: (RUNNING, CANCELLED),
    RUNNING: (SUCCEEDED, FAILED),
    SUCCEEDED: (COMPENSATED,),
    FAILED: (SCHEDULED, COMPENSATED),
    COMPENSATED: (),
    CANCELLED: (),
}


def require_state(state: str) -> str:
    """Return ``state`` if it is a recognized execution state, else raise."""
    if state not in LIFECYCLE_TRANSITIONS:
        raise RuntimeLifecycleError("unknown execution state", state=state)
    return state


def allowed_transitions(state: str) -> tuple[str, ...]:
    """Return the states legally reachable in one step from ``state``."""
    return LIFECYCLE_TRANSITIONS[require_state(state)]


def is_terminal(state: str) -> bool:
    """True iff ``state`` admits no further transition."""
    return require_state(state) in TERMINAL_STATES


def is_settled(state: str) -> bool:
    """True iff ``state`` is a settled (run-complete) outcome."""
    return require_state(state) in SETTLED_STATES


def can_transition(source: str, target: str) -> bool:
    """True iff ``source → target`` is a legal single lifecycle transition."""
    return require_state(target) in LIFECYCLE_TRANSITIONS[require_state(source)]


def require_transition(source: str, target: str) -> str:
    """Return ``target`` if ``source → target`` is legal, else raise (fail-closed)."""
    if not can_transition(source, target):
        raise RuntimeLifecycleError(
            "illegal execution lifecycle transition",
            source=source,
            target=target,
            allowed=list(LIFECYCLE_TRANSITIONS[source]),
        )
    return target


def validate_trajectory(trajectory: tuple[str, ...]) -> tuple[str, ...]:
    """Return ``trajectory`` if every consecutive pair is a legal transition, else raise.

    A trajectory must begin at :data:`PENDING` and every step must obey
    :data:`LIFECYCLE_TRANSITIONS`. An empty trajectory is rejected (fail-closed).
    """
    if not trajectory:
        raise RuntimeLifecycleError("empty execution trajectory")
    if trajectory[0] != PENDING:
        raise RuntimeLifecycleError(
            "execution trajectory must begin at pending", start=trajectory[0]
        )
    for source, target in zip(trajectory, trajectory[1:], strict=False):
        require_transition(source, target)
    return trajectory


__all__ = [
    "LIFECYCLE_FORMAT",
    "PENDING",
    "SCHEDULED",
    "PLACED",
    "RUNNING",
    "SUCCEEDED",
    "FAILED",
    "COMPENSATED",
    "CANCELLED",
    "EXECUTION_STATES",
    "TERMINAL_STATES",
    "SETTLED_STATES",
    "LIFECYCLE_TRANSITIONS",
    "require_state",
    "allowed_transitions",
    "is_terminal",
    "is_settled",
    "can_transition",
    "require_transition",
    "validate_trajectory",
]
