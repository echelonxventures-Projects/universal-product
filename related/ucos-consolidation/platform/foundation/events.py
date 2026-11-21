"""EC2-TASK-000060 — Platform Event Model (EC2-EPIC-001).

The immutable event vocabulary plus a deterministic, in-process, append-only event
bus that every future EC-2 epic uses to publish and observe state transitions
(request submitted, generation completed, certification issued, deploy applied, …).

Design (IMP-007 §5 determinism; PC-14 events; PC-16 audit):
    * :class:`PlatformEvent` is immutable and **carries no wall-clock** — ordering is
      established by a monotonic ``sequence`` assigned by the bus on publish, so the
      event log is reproducible. Its ``event_id`` is a content hash of the event
      core (type, source, subject, payload, sequence).
    * :class:`EventBus` is synchronous and append-only: publishing appends to an
      ordered log and dispatches to subscribers in deterministic order; subscribers
      never mutate the log. The bus binds the active correlation id (reusing the EC-1
      observability context) when present.

The bus is a foundation primitive — an in-memory, dependency-free substrate. It is
**not** an external message broker or a running service (those belong to later
operational epics).
"""

from __future__ import annotations

from collections.abc import Callable, Mapping
from dataclasses import dataclass, field
from platform.foundation.contracts import content_hash
from platform.foundation.errors import EventError
from typing import Any

from engine.foundation.obs.context import correlation_id

#: An event handler receives the recorded event and returns nothing.
EventHandler = Callable[["PlatformEvent"], None]


@dataclass(frozen=True, slots=True)
class PlatformEvent:
    """An immutable, content-addressed platform event (no wall-clock)."""

    event_type: str
    source: str
    subject: str
    sequence: int
    payload: Mapping[str, Any] = field(default_factory=dict)
    correlation_id: str | None = None
    event_id: str = ""

    @classmethod
    def create(
        cls,
        event_type: str,
        source: str,
        subject: str,
        sequence: int,
        *,
        payload: Mapping[str, Any] | None = None,
        correlation_id: str | None = None,
    ) -> PlatformEvent:
        """Build an event with a deterministic, content-addressed ``event_id``."""
        if not isinstance(event_type, str) or not event_type:
            raise EventError("event_type is required")
        if not isinstance(source, str) or not source:
            raise EventError("event source is required", event_type=event_type)
        if sequence < 0:
            raise EventError("event sequence must be non-negative", event_type=event_type)
        data = dict(payload or {})
        core = {
            "event_type": event_type,
            "source": source,
            "subject": subject,
            "sequence": sequence,
            "payload": data,
        }
        return cls(
            event_type=event_type,
            source=source,
            subject=subject,
            sequence=sequence,
            payload=data,
            correlation_id=correlation_id,
            event_id=f"UCOS-EVT-{content_hash(core)[:16]}",
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "event_id": self.event_id,
            "event_type": self.event_type,
            "source": self.source,
            "subject": self.subject,
            "sequence": self.sequence,
            "payload": dict(self.payload),
            "correlation_id": self.correlation_id,
        }


class EventBus:
    """A deterministic, synchronous, append-only in-process event bus."""

    __slots__ = ("_log", "_subscribers")

    def __init__(self) -> None:
        self._log: list[PlatformEvent] = []
        # name -> (event_type filter or None, handler); ordered by insertion.
        self._subscribers: list[tuple[str | None, EventHandler]] = []

    def subscribe(self, handler: EventHandler, *, event_type: str | None = None) -> None:
        """Register a handler, optionally filtered to a single ``event_type``."""
        if not callable(handler):
            raise EventError("event handler must be callable")
        self._subscribers.append((event_type, handler))

    def publish(
        self,
        event_type: str,
        source: str,
        subject: str,
        *,
        payload: Mapping[str, Any] | None = None,
    ) -> PlatformEvent:
        """Append an event to the log and dispatch it to matching subscribers."""
        sequence = len(self._log)
        event = PlatformEvent.create(
            event_type,
            source,
            subject,
            sequence,
            payload=payload,
            correlation_id=correlation_id(),
        )
        self._log.append(event)
        for filter_type, handler in self._subscribers:
            if filter_type is None or filter_type == event_type:
                handler(event)
        return event

    @property
    def events(self) -> tuple[PlatformEvent, ...]:
        """An immutable snapshot of the append-only event log (in order)."""
        return tuple(self._log)

    def __len__(self) -> int:
        return len(self._log)

    def events_of(self, event_type: str) -> tuple[PlatformEvent, ...]:
        """Every recorded event of ``event_type`` in order."""
        return tuple(e for e in self._log if e.event_type == event_type)

    def to_dict(self) -> dict[str, Any]:
        return {"event_count": len(self._log), "events": [e.to_dict() for e in self._log]}


__all__ = ["EventHandler", "PlatformEvent", "EventBus"]
