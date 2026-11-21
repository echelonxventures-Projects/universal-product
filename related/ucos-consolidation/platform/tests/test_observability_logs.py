"""EC2-TASK-000180 — Platform structured log buffer tests."""

from __future__ import annotations

from platform.observability.contracts import Severity
from platform.observability.errors import LogError
from platform.observability.logs import LogBuffer, LogEntry

import pytest

from engine.foundation.obs.context import reset_correlation_id, set_correlation_id


def test_buffer_is_append_only_and_ordered():
    buf = LogBuffer(emit_to_ec1=False)
    e0 = buf.info("src", "first")
    e1 = buf.warning("src", "second")
    assert e0.sequence == 0 and e1.sequence == 1
    assert buf.entries == (e0, e1)
    assert len(buf) == 2


def test_entry_is_content_addressed_and_deterministic():
    a = LogEntry.create(Severity.INFO, "s", "m", 0, fields={"k": 1})
    b = LogEntry.create(Severity.INFO, "s", "m", 0, fields={"k": 1})
    assert a.entry_id == b.entry_id
    assert a.entry_id.startswith("UCOS-LOG-")


def test_entry_validation_is_fail_closed():
    with pytest.raises(LogError):
        LogEntry.create(Severity.INFO, "", "m", 0)
    with pytest.raises(LogError):
        LogEntry.create(Severity.INFO, "s", "", 0)
    with pytest.raises(LogError):
        LogEntry.create(Severity.INFO, "s", "m", -1)
    with pytest.raises(LogError):
        LogEntry.create("info", "s", "m", 0)  # type: ignore[arg-type]


def test_severity_filter():
    buf = LogBuffer(emit_to_ec1=False)
    buf.debug("s", "d")
    buf.info("s", "i")
    buf.error("s", "e")
    buf.critical("s", "c")
    at_warn = buf.at_least(Severity.WARNING)
    assert [e.severity for e in at_warn] == [Severity.ERROR, Severity.CRITICAL]


def test_all_severity_helpers_record():
    buf = LogBuffer(emit_to_ec1=False)
    buf.debug("s", "d")
    buf.info("s", "i")
    buf.warning("s", "w")
    buf.error("s", "e")
    buf.critical("s", "c")
    assert len(buf) == 5


def test_buffer_binds_correlation_id():
    buf = LogBuffer(emit_to_ec1=False)
    token = set_correlation_id("corr-xyz")
    try:
        entry = buf.info("s", "m")
    finally:
        reset_correlation_id(token)
    assert entry.correlation_id == "corr-xyz"


def test_buffer_fingerprint_is_deterministic():
    a = LogBuffer(emit_to_ec1=False)
    b = LogBuffer(emit_to_ec1=False)
    for buf in (a, b):
        buf.info("s", "m", k="v")
        buf.error("s", "boom")
    assert a.fingerprint() == b.fingerprint()
    assert a.to_dict()["entry_count"] == 2


def test_emit_to_ec1_reuses_logger():
    # emit path must not raise; it delegates to the reused EC-1 structured logger.
    buf = LogBuffer(emit_to_ec1=True)
    entry = buf.info("src", "emitted", detail="value")
    assert entry.entry_id.startswith("UCOS-LOG-")
