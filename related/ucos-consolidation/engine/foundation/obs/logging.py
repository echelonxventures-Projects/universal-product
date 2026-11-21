"""TASK-000006 — Structured logging.

Deterministic, single-line JSON logs on ``stderr`` with:
    * the active correlation id (TASK-000007) attached to every record;
    * automatic redaction of secret-typed fields and :class:`SecretRef` values
      (SEC-04 — no secrets in logs);
    * default-on configuration (PL-02) — the first ``get_logger`` call configures
      the logging tree idempotently.
"""

from __future__ import annotations

import io
import json
import logging
import re
import threading
from collections.abc import Mapping
from datetime import UTC, datetime
from typing import Any

from engine.foundation.config.config import SecretRef
from engine.foundation.obs import context

_ROOT = "ucos.ec1"
_lock = threading.Lock()
_configured = False

_SECRET_KEY_PATTERN = re.compile(
    r"(password|passwd|secret|token|api[_-]?key|apikey|credential|"
    r"private[_-]?key|access[_-]?key)",
    re.IGNORECASE,
)
_REDACTED = "***"


def _json_default(value: Any) -> str:
    return str(value)


def _redact(value: Any) -> Any:
    if isinstance(value, SecretRef):
        return _REDACTED
    if isinstance(value, Mapping):
        return {
            key: (_REDACTED if _SECRET_KEY_PATTERN.search(str(key)) else _redact(item))
            for key, item in value.items()
        }
    if isinstance(value, list | tuple):
        return [_redact(item) for item in value]
    return value


class _JsonFormatter(logging.Formatter):
    """Render a log record as one deterministic JSON object."""

    def format(self, record: logging.LogRecord) -> str:
        payload: dict[str, Any] = {
            "timestamp": datetime.fromtimestamp(record.created, tz=UTC).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        cid = context.correlation_id()
        if cid is not None:
            payload["correlation_id"] = cid
        fields = getattr(record, "fields", None)
        if fields:
            payload["fields"] = _redact(fields)
        if record.exc_info:
            payload["exception"] = self.formatException(record.exc_info)
        return json.dumps(payload, default=_json_default, sort_keys=True)


class StructuredLogger:
    """Thin wrapper that forwards structured ``**fields`` as one record extra."""

    __slots__ = ("_logger",)

    def __init__(self, logger: logging.Logger) -> None:
        self._logger = logger

    def _emit(self, level: int, message: str, exc_info: bool, fields: dict[str, Any]) -> None:
        extra = {"fields": fields} if fields else {}
        self._logger.log(level, message, exc_info=exc_info, extra=extra)

    def debug(self, message: str, **fields: Any) -> None:
        self._emit(logging.DEBUG, message, False, fields)

    def info(self, message: str, **fields: Any) -> None:
        self._emit(logging.INFO, message, False, fields)

    def warning(self, message: str, **fields: Any) -> None:
        self._emit(logging.WARNING, message, False, fields)

    def error(self, message: str, **fields: Any) -> None:
        self._emit(logging.ERROR, message, False, fields)

    def critical(self, message: str, **fields: Any) -> None:
        self._emit(logging.CRITICAL, message, False, fields)

    def exception(self, message: str, **fields: Any) -> None:
        """Log at ERROR level including the active exception traceback."""
        self._emit(logging.ERROR, message, True, fields)


def configure_logging(
    level: str | int = "INFO",
    *,
    stream: io.TextIOBase | None = None,
    force: bool = False,
) -> None:
    """Configure the ``ucos.ec1`` logging tree (idempotent unless ``force``)."""
    global _configured
    with _lock:
        if _configured and not force:
            return
        logger = logging.getLogger(_ROOT)
        for handler in list(logger.handlers):
            logger.removeHandler(handler)
        handler = logging.StreamHandler(stream)
        handler.setFormatter(_JsonFormatter())
        logger.addHandler(handler)
        logger.setLevel(level)
        logger.propagate = False
        _configured = True


def get_logger(name: str) -> StructuredLogger:
    """Return a :class:`StructuredLogger` for ``ucos.ec1.<name>`` (default-on)."""
    if not _configured:
        configure_logging()
    return StructuredLogger(logging.getLogger(f"{_ROOT}.{name}"))


__all__ = ["StructuredLogger", "configure_logging", "get_logger"]
