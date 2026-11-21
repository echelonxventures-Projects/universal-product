"""EC2-TASK-000180 — Platform Structured Logs (EC2-EPIC-013).

An append-only, deterministic structured-log buffer that captures platform log
entries as content-addressed evidence, and **reuses** the certified EC-1 structured
logging discipline (:func:`engine.foundation.obs.logging.get_logger`) additively —
every captured entry is also emitted through the EC-1 logger (single-line JSON on
stderr, secret-redacted, correlation-id-bound) without modifying it.

Design (PL-02 observability; SEC-04 no secrets; IMP-007 §5 determinism):
    * :class:`LogEntry` is immutable and **carries no wall-clock** — ordering is a
      monotonic ``sequence`` assigned by the buffer on append. Its ``entry_id`` is a
      content hash of the entry core (severity, source, message, fields, sequence).
    * Secret-typed fields are redacted at the EC-1 layer on emit; the buffer itself
      stores only the caller-provided structured fields (callers pass references,
      never secret values — SEC-04).
    * :class:`LogBuffer` is append-only; snapshots and fingerprints are pure
      functions of the recorded entries.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field
from platform.foundation.contracts import content_hash
from platform.observability.contracts import Severity
from platform.observability.errors import LogError
from typing import Any

from engine.foundation.obs.context import correlation_id
from engine.foundation.obs.logging import get_logger

_ec1_logger = get_logger("platform.observability")


@dataclass(frozen=True, slots=True)
class LogEntry:
    """An immutable, content-addressed structured log entry (no wall-clock)."""

    severity: Severity
    source: str
    message: str
    sequence: int
    fields: Mapping[str, Any] = field(default_factory=dict)
    correlation_id: str | None = None
    entry_id: str = ""

    @classmethod
    def create(
        cls,
        severity: Severity,
        source: str,
        message: str,
        sequence: int,
        *,
        fields: Mapping[str, Any] | None = None,
        correlation_id: str | None = None,
    ) -> LogEntry:
        """Build a log entry with a deterministic, content-addressed ``entry_id``."""
        if not isinstance(severity, Severity):
            raise LogError("log severity must be a Severity")
        if not isinstance(source, str) or not source:
            raise LogError("log source is required")
        if not isinstance(message, str) or not message:
            raise LogError("log message is required", source=source)
        if sequence < 0:
            raise LogError("log sequence must be non-negative", source=source)
        data = dict(fields or {})
        core = {
            "severity": severity.value,
            "source": source,
            "message": message,
            "sequence": sequence,
            "fields": data,
        }
        return cls(
            severity=severity,
            source=source,
            message=message,
            sequence=sequence,
            fields=data,
            correlation_id=correlation_id,
            entry_id=f"UCOS-LOG-{content_hash(core)[:16]}",
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "entry_id": self.entry_id,
            "severity": self.severity.value,
            "source": self.source,
            "message": self.message,
            "sequence": self.sequence,
            "fields": dict(self.fields),
            "correlation_id": self.correlation_id,
        }


class LogBuffer:
    """A deterministic, append-only structured-log buffer (reuses EC-1 logging)."""

    __slots__ = ("_entries", "_emit")

    #: Maps observability severities to the EC-1 structured logger methods.
    _EMIT_METHODS = {
        Severity.DEBUG: "debug",
        Severity.INFO: "info",
        Severity.WARNING: "warning",
        Severity.ERROR: "error",
        Severity.CRITICAL: "critical",
    }

    def __init__(self, *, emit_to_ec1: bool = True) -> None:
        self._entries: list[LogEntry] = []
        self._emit = emit_to_ec1

    def record(
        self,
        severity: Severity,
        source: str,
        message: str,
        **fields: Any,
    ) -> LogEntry:
        """Append a structured log entry and emit it through the EC-1 logger."""
        entry = LogEntry.create(
            severity,
            source,
            message,
            len(self._entries),
            fields=fields,
            correlation_id=correlation_id(),
        )
        self._entries.append(entry)
        if self._emit:
            method = getattr(_ec1_logger, self._EMIT_METHODS[severity])
            method(message, source=source, **fields)
        return entry

    def debug(self, source: str, message: str, **fields: Any) -> LogEntry:
        return self.record(Severity.DEBUG, source, message, **fields)

    def info(self, source: str, message: str, **fields: Any) -> LogEntry:
        return self.record(Severity.INFO, source, message, **fields)

    def warning(self, source: str, message: str, **fields: Any) -> LogEntry:
        return self.record(Severity.WARNING, source, message, **fields)

    def error(self, source: str, message: str, **fields: Any) -> LogEntry:
        return self.record(Severity.ERROR, source, message, **fields)

    def critical(self, source: str, message: str, **fields: Any) -> LogEntry:
        return self.record(Severity.CRITICAL, source, message, **fields)

    @property
    def entries(self) -> tuple[LogEntry, ...]:
        """An immutable snapshot of the append-only log (in order)."""
        return tuple(self._entries)

    def __len__(self) -> int:
        return len(self._entries)

    def at_least(self, severity: Severity) -> tuple[LogEntry, ...]:
        """Every entry at ``severity`` or more severe, in order."""
        return tuple(e for e in self._entries if e.severity.at_least(severity))

    def to_dict(self) -> dict[str, Any]:
        return {"entry_count": len(self._entries), "entries": [e.to_dict() for e in self._entries]}

    def fingerprint(self) -> str:
        """A deterministic content hash over the content-addressed entry identities.

        Computed from the ``entry_id`` values (whose cores exclude the volatile,
        runtime ``correlation_id``) so log evidence is reproducible regardless of
        ambient correlation context.
        """
        return content_hash(
            {"entry_count": len(self._entries), "entries": [e.entry_id for e in self._entries]}
        )


__all__ = ["LogEntry", "LogBuffer"]
