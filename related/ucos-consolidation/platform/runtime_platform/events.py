"""EPIC-007 (Terminal T7) — Runtime Event Bus (Universal Runtime Platform).

The runtime plane's **Event Bus** — realizing the ``PRS-013`` Event Publication and
``PRS-015`` Event Delivery services. It is a thin, governed façade over the certified
Platform Foundation :class:`~platform.foundation.events.EventBus` (a deterministic,
synchronous, append-only, in-process, wall-clock-free bus): it **adds no second event
substrate** and re-implements no delivery, ordering, or deduplication logic. It layers
on the runtime plane's governed **event category vocabulary** and typed publish helpers,
so every emitted event is one of a fixed set of governed runtime signals (mirroring the
ratified ``PEV-001..003`` / ``PEV-026..027`` execution & workflow event categories).

Publishing an unknown category fails closed. Because the underlying bus assigns a
monotonic ``sequence`` and content-addresses each event, the recorded event log is fully
reproducible.
"""

from __future__ import annotations

from collections.abc import Mapping
from platform.foundation.events import EventBus, EventHandler, PlatformEvent
from platform.runtime_platform.errors import RuntimeEventError
from typing import Any

#: The stable event source attributed to the runtime plane.
RUNTIME_EVENT_SOURCE = "platform.runtime_platform.runtime"

# --- the governed runtime event categories (fixed vocabulary) --------------------
EXECUTION_SCHEDULED = "runtime.execution.scheduled"  # PEV-001
WORKLOAD_PLACED = "runtime.execution.placed"  # PEV-002
EXECUTION_STARTED = "runtime.execution.started"
EXECUTION_SUCCEEDED = "runtime.execution.succeeded"
EXECUTION_FAILED = "runtime.execution.failed"
EXECUTION_COMPENSATED = "runtime.execution.compensated"
EXECUTION_REGISTERED = "runtime.execution.registered"  # PRS-022
LIFECYCLE_CHANGED = "runtime.execution.lifecycle.changed"  # PEV-003
WORKFLOW_RESOLVED = "runtime.workflow.resolved"  # PEV-026
WORKFLOW_STEP_COMPLETED = "runtime.workflow.step.completed"  # PEV-027
WORKFLOW_COMPLETED = "runtime.workflow.completed"
WORKFLOW_COMPENSATED = "runtime.workflow.compensated"
CAPACITY_CHANGED = "runtime.capacity.changed"  # PEV-004

#: Every governed runtime event category, in canonical order.
RUNTIME_EVENT_CATEGORIES: tuple[str, ...] = (
    EXECUTION_SCHEDULED,
    WORKLOAD_PLACED,
    EXECUTION_STARTED,
    EXECUTION_SUCCEEDED,
    EXECUTION_FAILED,
    EXECUTION_COMPENSATED,
    EXECUTION_REGISTERED,
    LIFECYCLE_CHANGED,
    WORKFLOW_RESOLVED,
    WORKFLOW_STEP_COMPLETED,
    WORKFLOW_COMPLETED,
    WORKFLOW_COMPENSATED,
    CAPACITY_CHANGED,
)

_CATEGORY_SET: frozenset[str] = frozenset(RUNTIME_EVENT_CATEGORIES)


def require_category(category: str) -> str:
    """Return ``category`` if it is a governed runtime event category, else raise."""
    if category not in _CATEGORY_SET:
        raise RuntimeEventError("unknown runtime event category", category=category)
    return category


class RuntimeEventBus:
    """A governed, deterministic runtime event bus over the Foundation event bus.

    It owns no event storage of its own — the Foundation :class:`EventBus` is the single
    append-only substrate. This façade validates the event category against the fixed
    runtime vocabulary and stamps the canonical runtime source, so every runtime signal
    is governed and reproducible.
    """

    __slots__ = ("_bus",)

    def __init__(self, bus: EventBus | None = None) -> None:
        if bus is not None and not isinstance(bus, EventBus):
            raise RuntimeEventError("RuntimeEventBus requires a Foundation EventBus when supplied")
        self._bus = bus if bus is not None else EventBus()

    @property
    def bus(self) -> EventBus:
        """The underlying Foundation event bus (the single append-only substrate)."""
        return self._bus

    def subscribe(self, handler: EventHandler, *, category: str | None = None) -> None:
        """Register a handler, optionally filtered to one governed runtime category."""
        event_type = require_category(category) if category is not None else None
        self._bus.subscribe(handler, event_type=event_type)

    def publish(
        self,
        category: str,
        subject: str,
        *,
        payload: Mapping[str, Any] | None = None,
    ) -> PlatformEvent:
        """Publish a governed runtime event (fail-closed on an unknown category)."""
        return self._bus.publish(
            require_category(category),
            RUNTIME_EVENT_SOURCE,
            subject,
            payload=payload,
        )

    @property
    def events(self) -> tuple[PlatformEvent, ...]:
        """An immutable snapshot of the append-only event log (in order)."""
        return self._bus.events

    def events_of(self, category: str) -> tuple[PlatformEvent, ...]:
        """Every recorded event of a governed runtime category, in order."""
        return self._bus.events_of(require_category(category))

    def __len__(self) -> int:
        return len(self._bus)

    def to_dict(self) -> dict[str, Any]:
        return {
            "runtime_event_categories": list(RUNTIME_EVENT_CATEGORIES),
            "event_count": len(self._bus),
        }


__all__ = [
    "RUNTIME_EVENT_SOURCE",
    "EXECUTION_SCHEDULED",
    "WORKLOAD_PLACED",
    "EXECUTION_STARTED",
    "EXECUTION_SUCCEEDED",
    "EXECUTION_FAILED",
    "EXECUTION_COMPENSATED",
    "EXECUTION_REGISTERED",
    "LIFECYCLE_CHANGED",
    "WORKFLOW_RESOLVED",
    "WORKFLOW_STEP_COMPLETED",
    "WORKFLOW_COMPLETED",
    "WORKFLOW_COMPENSATED",
    "CAPACITY_CHANGED",
    "RUNTIME_EVENT_CATEGORIES",
    "require_category",
    "RuntimeEventBus",
]
