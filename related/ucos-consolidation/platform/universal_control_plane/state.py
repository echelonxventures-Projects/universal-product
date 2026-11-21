"""UCOS-CTRL-000001 — Universal State Engine.

The StateEngine governs lifecycle transitions for every control-plane object.
Permitted transitions are registered at construction time; no transition is
assumed. The engine is deterministic: given the same current state and event
token it always returns the same next state, and it never consults the clock.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from platform.universal_control_plane.errors import StateTransitionError
from platform.universal_control_plane.ontology import (
    DEFAULT_LIFECYCLE,
    LIFECYCLE_ACTIVE,
    LIFECYCLE_ARCHIVED,
    LIFECYCLE_CANCELLED,
    LIFECYCLE_COMPLETE,
    LIFECYCLE_DRAFT,
    LIFECYCLE_PAUSED,
)
from typing import Any


@dataclass(frozen=True)
class Transition:
    """A permitted lifecycle transition."""

    from_state: str
    event: str
    to_state: str

    def to_dict(self) -> dict[str, str]:
        return {"from_state": self.from_state, "event": self.event, "to_state": self.to_state}


@dataclass
class StateEngine:
    """Registry-driven lifecycle state machine.

    Transitions are data, not code: register them via :meth:`register_transition`.
    The engine ships with a default table covering the six standard lifecycle states;
    callers extend or replace it for domain-specific state models.
    """

    _transitions: dict[tuple[str, str], str] = field(default_factory=dict)
    _states: set[str] = field(default_factory=set)

    def __post_init__(self) -> None:
        self._seed_defaults()

    def _seed_defaults(self) -> None:
        for s in DEFAULT_LIFECYCLE:
            self._states.add(s)
        default_table = [
            (LIFECYCLE_DRAFT, "ACTIVATE", LIFECYCLE_ACTIVE),
            (LIFECYCLE_DRAFT, "CANCEL", LIFECYCLE_CANCELLED),
            (LIFECYCLE_ACTIVE, "PAUSE", LIFECYCLE_PAUSED),
            (LIFECYCLE_ACTIVE, "COMPLETE", LIFECYCLE_COMPLETE),
            (LIFECYCLE_ACTIVE, "CANCEL", LIFECYCLE_CANCELLED),
            (LIFECYCLE_PAUSED, "RESUME", LIFECYCLE_ACTIVE),
            (LIFECYCLE_PAUSED, "CANCEL", LIFECYCLE_CANCELLED),
            (LIFECYCLE_COMPLETE, "ARCHIVE", LIFECYCLE_ARCHIVED),
            (LIFECYCLE_CANCELLED, "ARCHIVE", LIFECYCLE_ARCHIVED),
        ]
        for from_s, event, to_s in default_table:
            self._transitions[(from_s, event)] = to_s

    # ------------------------------------------------------------------
    # Registration
    # ------------------------------------------------------------------

    def register_state(self, state: str) -> None:
        """Add a new lifecycle state token."""
        if not state or not state.strip():
            raise ValueError("state token must be a non-empty string")
        self._states.add(state.strip())

    def register_transition(self, from_state: str, event: str, to_state: str) -> None:
        """Register a permitted transition. Overwrites any prior binding."""
        for s in (from_state, to_state):
            if s not in self._states:
                self._states.add(s)
        self._transitions[(from_state, event)] = to_state

    # ------------------------------------------------------------------
    # Runtime
    # ------------------------------------------------------------------

    def transition(self, current_state: str, event: str) -> str:
        """Return the next state for *current_state* + *event*, or raise."""
        key = (current_state, event)
        if key not in self._transitions:
            raise StateTransitionError(
                f"no transition registered for state={current_state!r} event={event!r}"
            )
        return self._transitions[key]

    def can_transition(self, current_state: str, event: str) -> bool:
        """Return True iff the transition is registered."""
        return (current_state, event) in self._transitions

    def permitted_events(self, current_state: str) -> list[str]:
        """All events that may be fired from *current_state*."""
        return sorted(event for (from_s, event) in self._transitions if from_s == current_state)

    # ------------------------------------------------------------------
    # Inspection
    # ------------------------------------------------------------------

    @property
    def states(self) -> frozenset[str]:
        return frozenset(self._states)

    def transitions(self) -> list[Transition]:
        return sorted(
            [Transition(fs, ev, ts) for (fs, ev), ts in self._transitions.items()],
            key=lambda t: (t.from_state, t.event),
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "states": sorted(self._states),
            "transitions": [t.to_dict() for t in self.transitions()],
        }
