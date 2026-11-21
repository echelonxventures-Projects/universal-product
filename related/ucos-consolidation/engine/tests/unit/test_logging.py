"""Tests for TASK-000006 structured logging."""

from __future__ import annotations

import io
import json

import pytest

from engine.foundation.config.config import SecretRef
from engine.foundation.obs import context
from engine.foundation.obs.logging import configure_logging, get_logger


@pytest.fixture()
def log_buffer():
    buffer = io.StringIO()
    configure_logging(level="DEBUG", stream=buffer, force=True)
    yield buffer
    # restore default configuration for other tests
    configure_logging(force=True)


def _last_record(buffer: io.StringIO) -> dict:
    lines = [line for line in buffer.getvalue().splitlines() if line.strip()]
    return json.loads(lines[-1])


def test_basic_json_record(log_buffer):
    get_logger("test").info("hello", user="alice")
    record = _last_record(log_buffer)
    assert record["message"] == "hello"
    assert record["level"] == "INFO"
    assert record["logger"] == "ucos.ec1.test"
    assert record["fields"]["user"] == "alice"
    assert "timestamp" in record


def test_correlation_id_attached(log_buffer):
    token = context.set_correlation_id("corr-123")
    try:
        get_logger("test").warning("with-cid")
    finally:
        context.reset_correlation_id(token)
    record = _last_record(log_buffer)
    assert record["correlation_id"] == "corr-123"


def test_secret_key_field_redacted(log_buffer):
    get_logger("test").info("login", password="plaintext", token="abc", user="bob")
    record = _last_record(log_buffer)
    assert record["fields"]["password"] == "***"
    assert record["fields"]["token"] == "***"
    assert record["fields"]["user"] == "bob"
    assert "plaintext" not in log_buffer.getvalue()


def test_secret_ref_value_redacted(log_buffer):
    get_logger("test").info("cfg", db=SecretRef("env://DB"))
    record = _last_record(log_buffer)
    assert record["fields"]["db"] == "***"


def test_nested_and_sequence_redaction(log_buffer):
    get_logger("test").info(
        "nested",
        payload={"api_key": "leak", "safe": [1, {"secret": "leak2"}]},
    )
    record = _last_record(log_buffer)
    assert record["fields"]["payload"]["api_key"] == "***"
    assert record["fields"]["payload"]["safe"][1]["secret"] == "***"
    assert "leak" not in log_buffer.getvalue()


def test_exception_logging(log_buffer):
    log = get_logger("test")
    try:
        raise ValueError("boom")
    except ValueError:
        log.exception("failed", op="x")
    record = _last_record(log_buffer)
    assert record["level"] == "ERROR"
    assert "ValueError: boom" in record["exception"]


def test_deterministic_sorted_keys(log_buffer):
    get_logger("test").info("z", b=1, a=2)
    line = [line_ for line_ in log_buffer.getvalue().splitlines() if line_.strip()][-1]
    # sort_keys=True => top-level keys are ordered
    assert line.index('"level"') < line.index('"message"')


def test_critical_level(log_buffer):
    get_logger("test").critical("boom", code=500)
    record = _last_record(log_buffer)
    assert record["level"] == "CRITICAL"
    assert record["message"] == "boom"
    assert record["fields"]["code"] == 500


def test_non_serializable_field_is_stringified(log_buffer):
    class Widget:
        def __str__(self) -> str:
            return "widget-repr"

    get_logger("test").info("obj", widget=Widget())
    record = _last_record(log_buffer)
    # json.dumps falls back to _json_default (str) for otherwise-unserialisable values
    assert record["fields"]["widget"] == "widget-repr"


def test_configure_logging_is_idempotent_without_force(log_buffer):
    # The tree is already configured (by the fixture); a second call without
    # force must return early and leave the existing handler untouched.
    other = io.StringIO()
    configure_logging(stream=other)
    get_logger("test").info("still-original")
    assert other.getvalue() == ""
    assert "still-original" in log_buffer.getvalue()
