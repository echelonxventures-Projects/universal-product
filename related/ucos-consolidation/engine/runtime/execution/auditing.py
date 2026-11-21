"""EPIC-RTE-002 — Execution Auditing (Runtime Execution Platform).

Realises **Execution Auditing**: an append-only, ordered, deterministic record of
every lifecycle transition and platform decision taken during a modelled
execution. Auditing reuses the Foundation error/observability discipline
(non-secret, structured, machine-consumable — PL-02, IP-12) and is a *record
structure only*: it captures what the platform decided, it decides nothing.

An :class:`AuditLog` is immutable and forward-only (ORL-07): :meth:`AuditLog.append`
returns a **new** log with a monotonically increasing ``sequence``, so an audit
trail can never be silently mutated. Sequence numbers are assigned in emission
order within a single execution pass, so identical inputs yield an identical,
byte-comparable trail (ORL-20).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

#: Event kinds the platform records.
TRANSITION = "transition"
AUTHORIZE = "authorize"
CHECKPOINT = "checkpoint"
ROLLBACK = "rollback"

#: The recorded audit-log format.
AUDIT_LOG_FORMAT = "ucos-execution-audit/1.0.0"


@dataclass(frozen=True, slots=True)
class AuditEvent:
    """One recorded, ordered execution event (a decision, not an action)."""

    sequence: int
    event: str
    universe_id: str
    stage: int
    source_state: str
    target_state: str
    detail: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "sequence": self.sequence,
            "event": self.event,
            "universe_id": self.universe_id,
            "stage": self.stage,
            "source_state": self.source_state,
            "target_state": self.target_state,
            "detail": self.detail,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> AuditEvent:
        return cls(
            sequence=int(data["sequence"]),
            event=str(data["event"]),
            universe_id=str(data["universe_id"]),
            stage=int(data["stage"]),
            source_state=str(data["source_state"]),
            target_state=str(data["target_state"]),
            detail=str(data.get("detail", "")),
        )


@dataclass(frozen=True, slots=True)
class AuditLog:
    """An immutable, append-only, ordered sequence of :class:`AuditEvent`."""

    events: tuple[AuditEvent, ...] = field(default_factory=tuple)

    @property
    def sequence(self) -> int:
        """The next sequence number (== the number of recorded events)."""
        return len(self.events)

    def append(
        self,
        *,
        event: str,
        universe_id: str,
        stage: int,
        source_state: str,
        target_state: str,
        detail: str = "",
    ) -> AuditLog:
        """Return a new log with one appended event (forward-only, ORL-07)."""
        entry = AuditEvent(
            sequence=self.sequence,
            event=event,
            universe_id=universe_id,
            stage=stage,
            source_state=source_state,
            target_state=target_state,
            detail=detail,
        )
        return AuditLog(events=(*self.events, entry))

    def for_universe(self, universe_id: str) -> tuple[AuditEvent, ...]:
        """Every recorded event for ``universe_id`` (in sequence order)."""
        return tuple(e for e in self.events if e.universe_id == universe_id)

    def transitions(self) -> tuple[AuditEvent, ...]:
        """Every recorded lifecycle-transition event (in sequence order)."""
        return tuple(e for e in self.events if e.event == TRANSITION)

    def __len__(self) -> int:
        return len(self.events)

    def to_dict(self) -> dict[str, Any]:
        return {
            "audit_log_format": AUDIT_LOG_FORMAT,
            "event_count": len(self.events),
            "events": [e.to_dict() for e in self.events],
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> AuditLog:
        return cls(events=tuple(AuditEvent.from_dict(e) for e in data.get("events", ())))


__all__ = [
    "TRANSITION",
    "AUTHORIZE",
    "CHECKPOINT",
    "ROLLBACK",
    "AUDIT_LOG_FORMAT",
    "AuditEvent",
    "AuditLog",
]
