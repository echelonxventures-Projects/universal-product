"""EC2-TASK-000060 — Platform event model tests."""

from __future__ import annotations

from platform.foundation.errors import EventError
from platform.foundation.events import EventBus, PlatformEvent

import pytest

from engine.foundation.obs.context import reset_correlation_id, set_correlation_id


def test_event_is_content_addressed_and_deterministic():
    a = PlatformEvent.create("t", "src", "subj", 0, payload={"k": 1})
    b = PlatformEvent.create("t", "src", "subj", 0, payload={"k": 1})
    assert a.event_id == b.event_id
    assert a.event_id.startswith("UCOS-EVT-")


def test_event_validation():
    with pytest.raises(EventError):
        PlatformEvent.create("", "src", "subj", 0)
    with pytest.raises(EventError):
        PlatformEvent.create("t", "", "subj", 0)
    with pytest.raises(EventError):
        PlatformEvent.create("t", "src", "subj", -1)


def test_bus_append_only_and_ordered():
    bus = EventBus()
    e0 = bus.publish("a", "src", "s0")
    e1 = bus.publish("b", "src", "s1")
    assert e0.sequence == 0 and e1.sequence == 1
    assert len(bus) == 2
    assert bus.events == (e0, e1)


def test_bus_dispatch_and_filter():
    bus = EventBus()
    seen_all = []
    seen_a = []
    bus.subscribe(seen_all.append)
    bus.subscribe(seen_a.append, event_type="a")
    bus.publish("a", "src", "s")
    bus.publish("b", "src", "s")
    assert [e.event_type for e in seen_all] == ["a", "b"]
    assert [e.event_type for e in seen_a] == ["a"]
    assert len(bus.events_of("a")) == 1


def test_bus_rejects_non_callable_handler():
    bus = EventBus()
    with pytest.raises(EventError):
        bus.subscribe("not-callable")  # type: ignore[arg-type]


def test_bus_binds_correlation_id():
    bus = EventBus()
    token = set_correlation_id("corr-123")
    try:
        event = bus.publish("t", "src", "s")
    finally:
        reset_correlation_id(token)
    assert event.correlation_id == "corr-123"


def test_bus_to_dict():
    bus = EventBus()
    bus.publish("t", "src", "s", payload={"x": 1})
    d = bus.to_dict()
    assert d["event_count"] == 1
    assert d["events"][0]["payload"] == {"x": 1}
