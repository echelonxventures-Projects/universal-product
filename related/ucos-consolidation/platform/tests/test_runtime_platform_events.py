"""EPIC-007 (T7) — Runtime event bus tests."""

from __future__ import annotations

from platform.foundation.events import EventBus
from platform.runtime_platform.errors import RuntimeEventError
from platform.runtime_platform.events import (
    EXECUTION_SCHEDULED,
    EXECUTION_SUCCEEDED,
    RUNTIME_EVENT_CATEGORIES,
    RUNTIME_EVENT_SOURCE,
    RuntimeEventBus,
    require_category,
)

import pytest


def test_require_category_accepts_known_rejects_unknown():
    assert require_category(EXECUTION_SCHEDULED) == EXECUTION_SCHEDULED
    with pytest.raises(RuntimeEventError):
        require_category("nope")


def test_publish_stamps_source_and_appends():
    bus = RuntimeEventBus()
    event = bus.publish(EXECUTION_SCHEDULED, "subj", payload={"k": 1})
    assert event.source == RUNTIME_EVENT_SOURCE
    assert event.event_type == EXECUTION_SCHEDULED
    assert len(bus) == 1
    assert bus.events[0] is event


def test_publish_unknown_category_fails_closed():
    bus = RuntimeEventBus()
    with pytest.raises(RuntimeEventError):
        bus.publish("bad.category", "subj")


def test_subscribe_filtered_and_events_of():
    bus = RuntimeEventBus()
    seen = []
    bus.subscribe(seen.append, category=EXECUTION_SUCCEEDED)
    bus.publish(EXECUTION_SCHEDULED, "s")
    bus.publish(EXECUTION_SUCCEEDED, "s")
    assert [e.event_type for e in seen] == [EXECUTION_SUCCEEDED]
    assert len(bus.events_of(EXECUTION_SUCCEEDED)) == 1


def test_subscribe_unknown_category_fails_closed():
    bus = RuntimeEventBus()
    with pytest.raises(RuntimeEventError):
        bus.subscribe(lambda e: None, category="bad")


def test_wraps_supplied_foundation_bus():
    foundation = EventBus()
    bus = RuntimeEventBus(foundation)
    assert bus.bus is foundation
    bus.publish(EXECUTION_SCHEDULED, "s")
    assert len(foundation) == 1


def test_rejects_non_bus():
    with pytest.raises(RuntimeEventError):
        RuntimeEventBus("not-a-bus")  # type: ignore[arg-type]


def test_to_dict_lists_categories():
    bus = RuntimeEventBus()
    d = bus.to_dict()
    assert d["runtime_event_categories"] == list(RUNTIME_EVENT_CATEGORIES)
    assert d["event_count"] == 0
