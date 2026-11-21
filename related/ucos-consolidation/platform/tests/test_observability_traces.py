"""EC2-TASK-000181 — Platform trace recorder tests."""

from __future__ import annotations

from platform.observability.errors import TraceError
from platform.observability.traces import SpanRecord, TraceRecorder

import pytest


def test_span_records_ok_outcome():
    rec = TraceRecorder()
    with rec.span("compile", stage="parse") as cid:
        assert cid is not None
    assert len(rec) == 1
    assert rec.spans[0].outcome == "ok"
    assert rec.spans[0].name == "compile"


def test_span_records_error_and_reraises():
    rec = TraceRecorder()
    with pytest.raises(ValueError):
        with rec.span("failing"):
            raise ValueError("boom")
    assert len(rec) == 1
    assert rec.spans[0].outcome == "error"


def test_spans_are_ordered_and_named_queryable():
    rec = TraceRecorder()
    with rec.span("a"):
        pass
    with rec.span("b"):
        pass
    with rec.span("a"):
        pass
    assert [s.sequence for s in rec.spans] == [0, 1, 2]
    assert len(rec.spans_named("a")) == 2


def test_span_record_is_content_addressed_without_walltime():
    a = SpanRecord.create("s", 0, "ok", attributes={"k": "v"})
    b = SpanRecord.create("s", 0, "ok", attributes={"k": "v"})
    assert a.span_id == b.span_id
    assert a.span_id.startswith("UCOS-SPAN-")


def test_span_record_validation():
    with pytest.raises(TraceError):
        SpanRecord.create("", 0, "ok")
    with pytest.raises(TraceError):
        SpanRecord.create("s", -1, "ok")
    with pytest.raises(TraceError):
        SpanRecord.create("s", 0, "unknown")


def test_recorder_fingerprint_deterministic():
    a = TraceRecorder()
    b = TraceRecorder()
    for rec in (a, b):
        with rec.span("x", n="1"):
            pass
    assert a.fingerprint() == b.fingerprint()
    assert a.to_dict()["span_count"] == 1
