"""EPIC-RTE-002 — Execution State (Runtime Execution Platform).

Realises **Execution State**: the deterministic, JSON-serialisable record of where
each composed Universe stands in a modelled execution, plus the aggregate run
status. State is a **recorded structure only** (RUNTIME-013 ORL-15): it describes a
modelled execution over an existing composition and drives no live process.

Following the established runtime convention (``COORDINATION_CLASSES`` in
:mod:`engine.runtime.planner`), states are plain, sorted string constants rather
than an enum, so every state is JSON-native and a state record round-trips without
custom encoding. The set is closed and validated at the boundary (a foreign state
is refused via :class:`~engine.runtime.execution.errors.ExecutionLifecycleError`).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from engine.runtime.execution.errors import ExecutionLifecycleError

# --------------------------------------------------------------------------- #
# Per-universe execution states                                               #
# --------------------------------------------------------------------------- #

#: A universe that has not yet been considered for execution.
PENDING = "pending"
#: A universe whose dependencies are all satisfied and may proceed.
READY = "ready"
#: A universe currently modelled as executing.
RUNNING = "running"
#: A universe that completed successfully.
COMPLETED = "completed"
#: A universe whose modelled execution failed.
FAILED = "failed"
#: A universe deliberately or transitively skipped (e.g. a blocked dependent).
SKIPPED = "skipped"
#: A previously completed universe whose effect has been reversed (IP-08).
ROLLED_BACK = "rolled_back"

#: The closed, sorted set of recognised per-universe execution states.
EXECUTION_STATES: tuple[str, ...] = (
    COMPLETED,
    FAILED,
    PENDING,
    READY,
    ROLLED_BACK,
    RUNNING,
    SKIPPED,
)

#: States from which no further transition occurs within a single execution pass.
TERMINAL_STATES: tuple[str, ...] = (COMPLETED, FAILED, ROLLED_BACK, SKIPPED)

# --------------------------------------------------------------------------- #
# Aggregate run status                                                        #
# --------------------------------------------------------------------------- #

#: Every universe completed successfully.
SUCCEEDED = "succeeded"
#: At least one universe failed.
RUN_FAILED = "failed"
#: No failure, but at least one universe was skipped (a partial execution).
PARTIAL = "partial"
#: Every completed universe was subsequently rolled back (IP-08).
ROLLED_BACK_RUN = "rolled_back"

#: The closed, sorted set of recognised aggregate run statuses.
RUN_STATUSES: tuple[str, ...] = (PARTIAL, ROLLED_BACK_RUN, RUN_FAILED, SUCCEEDED)


def is_terminal(state: str) -> bool:
    """True iff ``state`` is a terminal per-universe state."""
    return state in TERMINAL_STATES


def require_state(state: str) -> str:
    """Return ``state`` if recognised, else raise :class:`ExecutionLifecycleError`."""
    if state not in EXECUTION_STATES:
        raise ExecutionLifecycleError(
            "unknown execution state", state=state, allowed=list(EXECUTION_STATES)
        )
    return state


@dataclass(frozen=True, slots=True)
class UniverseExecutionState:
    """The recorded execution state of a single composed Universe.

    A pure value: ``universe_id`` and ``context_id`` bind it to the composition,
    ``stage`` is its scheduled coordination stage, ``status`` is one of
    :data:`EXECUTION_STATES`, and ``outcome`` carries the (non-secret) modelled
    result detail. It confers no authority and executes nothing (ORL-15/ORL-22).
    """

    universe_id: str
    context_id: str
    stage: int
    status: str
    depends_on: tuple[str, ...] = field(default_factory=tuple)
    outcome: str = ""

    def __post_init__(self) -> None:
        require_state(self.status)

    @property
    def terminal(self) -> bool:
        """True iff this universe has reached a terminal state."""
        return is_terminal(self.status)

    def with_status(self, status: str, *, outcome: str = "") -> UniverseExecutionState:
        """Return a copy in ``status`` (the transition legality is enforced elsewhere)."""
        return UniverseExecutionState(
            universe_id=self.universe_id,
            context_id=self.context_id,
            stage=self.stage,
            status=require_state(status),
            depends_on=self.depends_on,
            outcome=outcome,
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "universe_id": self.universe_id,
            "context_id": self.context_id,
            "stage": self.stage,
            "status": self.status,
            "depends_on": list(self.depends_on),
            "outcome": self.outcome,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> UniverseExecutionState:
        """Reconstruct a state record from its :meth:`to_dict` form (persistence)."""
        return cls(
            universe_id=str(data["universe_id"]),
            context_id=str(data["context_id"]),
            stage=int(data["stage"]),
            status=require_state(str(data["status"])),
            depends_on=tuple(data.get("depends_on", ())),
            outcome=str(data.get("outcome", "")),
        )


def derive_run_status(states: tuple[UniverseExecutionState, ...]) -> str:
    """Deterministically reduce per-universe states to an aggregate run status.

    Precedence (auditable and stable): any ``failed`` → ``failed``; else every
    universe ``rolled_back`` → ``rolled_back``; else any ``skipped`` → ``partial``;
    else ``succeeded``. An empty run is ``succeeded`` (vacuously complete).
    """
    statuses = {state.status for state in states}
    if FAILED in statuses:
        return RUN_FAILED
    if states and statuses == {ROLLED_BACK}:
        return ROLLED_BACK_RUN
    if SKIPPED in statuses:
        return PARTIAL
    return SUCCEEDED


__all__ = [
    "PENDING",
    "READY",
    "RUNNING",
    "COMPLETED",
    "FAILED",
    "SKIPPED",
    "ROLLED_BACK",
    "EXECUTION_STATES",
    "TERMINAL_STATES",
    "SUCCEEDED",
    "RUN_FAILED",
    "PARTIAL",
    "ROLLED_BACK_RUN",
    "RUN_STATUSES",
    "is_terminal",
    "require_state",
    "derive_run_status",
    "UniverseExecutionState",
]
