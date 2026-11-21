"""EPIC-RTE-002 — Execution Lifecycle (Runtime Execution Platform).

Realises **Execution Lifecycle**: the closed, deterministic transition model that
governs how a composed Universe moves between the :mod:`~engine.runtime.execution.state`
states during a modelled execution. The lifecycle is a *rule structure only* — it
decides which transitions are legal; it performs none of them and executes nothing
(RUNTIME-013 ORL-15).

The model is intentionally small and total, so every path is decidable and every
illegal transition fails loudly and auditably:

    pending   → ready | skipped
    ready     → running | skipped
    running   → completed | failed
    failed    → ready | rolled_back        (recovery retry / reversal)
    completed → rolled_back                (reversal, IP-08)
    skipped   → (terminal)
    rolled_back → (terminal)

Because the transition table is fixed data (no wall-clock, no ambient state), the
lifecycle is fully deterministic (ORL-20).
"""

from __future__ import annotations

from engine.runtime.execution.errors import ExecutionLifecycleError
from engine.runtime.execution.state import (
    COMPLETED,
    FAILED,
    PENDING,
    READY,
    ROLLED_BACK,
    RUNNING,
    SKIPPED,
    require_state,
)

#: The canonical, closed lifecycle transition table (``from → allowed to-states``).
LIFECYCLE_TRANSITIONS: dict[str, tuple[str, ...]] = {
    PENDING: (READY, SKIPPED),
    READY: (RUNNING, SKIPPED),
    RUNNING: (COMPLETED, FAILED),
    FAILED: (READY, ROLLED_BACK),
    COMPLETED: (ROLLED_BACK,),
    SKIPPED: (),
    ROLLED_BACK: (),
}


def allowed_transitions(state: str) -> tuple[str, ...]:
    """Return the states legally reachable in one step from ``state``."""
    return LIFECYCLE_TRANSITIONS[require_state(state)]


def can_transition(source: str, target: str) -> bool:
    """True iff ``source → target`` is a legal single lifecycle transition."""
    return require_state(target) in LIFECYCLE_TRANSITIONS[require_state(source)]


def require_transition(source: str, target: str) -> str:
    """Return ``target`` if ``source → target`` is legal, else raise.

    Raises:
        ExecutionLifecycleError: if the transition is not in :data:`LIFECYCLE_TRANSITIONS`.
    """
    if not can_transition(source, target):
        raise ExecutionLifecycleError(
            "illegal execution lifecycle transition",
            source=source,
            target=target,
            allowed=list(LIFECYCLE_TRANSITIONS[source]),
        )
    return target


__all__ = [
    "LIFECYCLE_TRANSITIONS",
    "allowed_transitions",
    "can_transition",
    "require_transition",
]
