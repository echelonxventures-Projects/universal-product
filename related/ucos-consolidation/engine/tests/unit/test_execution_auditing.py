"""EPIC-RTE-002 — Execution Auditing unit tests."""

from __future__ import annotations

from engine.runtime.execution.auditing import (
    AUDIT_LOG_FORMAT,
    AUTHORIZE,
    TRANSITION,
    AuditEvent,
    AuditLog,
)


def test_empty_log_has_zero_sequence():
    log = AuditLog()
    assert log.sequence == 0
    assert len(log) == 0
    assert log.events == ()


def test_append_is_forward_only_and_immutable():
    log = AuditLog()
    log2 = log.append(
        event=TRANSITION,
        universe_id="A",
        stage=0,
        source_state="pending",
        target_state="ready",
    )
    # original is unchanged
    assert len(log) == 0
    assert len(log2) == 1
    assert log2.events[0].sequence == 0
    log3 = log2.append(
        event=TRANSITION,
        universe_id="A",
        stage=0,
        source_state="ready",
        target_state="running",
        detail="d",
    )
    assert [e.sequence for e in log3.events] == [0, 1]
    assert log3.events[1].detail == "d"


def test_for_universe_and_transitions_filters():
    log = (
        AuditLog()
        .append(
            event=TRANSITION,
            universe_id="A",
            stage=0,
            source_state="pending",
            target_state="ready",
        )
        .append(event=AUTHORIZE, universe_id="B", stage=1, source_state="", target_state="")
    )
    assert len(log.for_universe("A")) == 1
    assert len(log.for_universe("B")) == 1
    assert len(log.transitions()) == 1


def test_event_to_dict_and_from_dict_round_trip():
    event = AuditEvent(
        sequence=3,
        event=TRANSITION,
        universe_id="A",
        stage=2,
        source_state="running",
        target_state="completed",
        detail="outcome:completed",
    )
    blob = event.to_dict()
    assert AuditEvent.from_dict(blob) == event


def test_event_from_dict_defaults_detail():
    event = AuditEvent.from_dict(
        {
            "sequence": 0,
            "event": TRANSITION,
            "universe_id": "A",
            "stage": 0,
            "source_state": "pending",
            "target_state": "ready",
        }
    )
    assert event.detail == ""


def test_log_to_dict_and_from_dict_round_trip():
    log = AuditLog().append(
        event=TRANSITION, universe_id="A", stage=0, source_state="pending", target_state="ready"
    )
    blob = log.to_dict()
    assert blob["audit_log_format"] == AUDIT_LOG_FORMAT
    assert blob["event_count"] == 1
    assert AuditLog.from_dict(blob) == log
