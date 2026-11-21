"""EC2-TASK-000181 — Platform Traces (EC2-EPIC-013).

A deterministic span/trace recorder for governed platform actions. It **reuses** the
certified EC-1 span discipline (:func:`engine.foundation.obs.telemetry.trace`)
additively — the reused context manager performs the real timing, correlation-id
binding, and span metrics on the EC-1 substrate — while this module records an
immutable, content-addressed :class:`SpanRecord` for reproducible trace evidence.

Design (PL-02 observability; IP-03 traceability; IMP-007 §5 determinism):
    * :class:`SpanRecord` is immutable and content-addressed over
      ``(name, sequence, outcome, attributes)``. **Wall-clock duration is not part
      of the identity** (it is timing telemetry, recorded on the EC-1 substrate), so
      trace evidence is reproducible across runs.
    * :class:`TraceRecorder.span` is an append-only context manager that opens a
      reused EC-1 span, captures the bound correlation id, and records the outcome
      (``ok`` / ``error``) fail-closed even when the wrapped block raises.
"""

from __future__ import annotations

from collections.abc import Iterator, Mapping
from contextlib import contextmanager
from dataclasses import dataclass, field
from platform.foundation.contracts import content_hash
from platform.observability.errors import TraceError
from typing import Any

from engine.foundation.obs.telemetry import trace as _ec1_trace


@dataclass(frozen=True, slots=True)
class SpanRecord:
    """An immutable, content-addressed record of a completed span (no wall-clock id)."""

    name: str
    sequence: int
    outcome: str
    attributes: Mapping[str, Any] = field(default_factory=dict)
    correlation_id: str | None = None
    span_id: str = ""

    @classmethod
    def create(
        cls,
        name: str,
        sequence: int,
        outcome: str,
        *,
        attributes: Mapping[str, Any] | None = None,
        correlation_id: str | None = None,
    ) -> SpanRecord:
        """Build a span record with a deterministic, content-addressed ``span_id``."""
        if not isinstance(name, str) or not name:
            raise TraceError("span name is required")
        if sequence < 0:
            raise TraceError("span sequence must be non-negative", name=name)
        if outcome not in ("ok", "error"):
            raise TraceError("span outcome must be 'ok' or 'error'", name=name)
        attrs = dict(attributes or {})
        core = {"name": name, "sequence": sequence, "outcome": outcome, "attributes": attrs}
        return cls(
            name=name,
            sequence=sequence,
            outcome=outcome,
            attributes=attrs,
            correlation_id=correlation_id,
            span_id=f"UCOS-SPAN-{content_hash(core)[:16]}",
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "span_id": self.span_id,
            "name": self.name,
            "sequence": self.sequence,
            "outcome": self.outcome,
            "attributes": dict(self.attributes),
            "correlation_id": self.correlation_id,
        }


class TraceRecorder:
    """A deterministic, append-only span recorder (reuses EC-1 telemetry spans)."""

    __slots__ = ("_spans",)

    def __init__(self) -> None:
        self._spans: list[SpanRecord] = []

    @contextmanager
    def span(self, name: str, **attributes: Any) -> Iterator[str]:
        """Open a reused EC-1 span; record its outcome fail-closed on exit.

        Yields the active correlation id. Records an ``error`` outcome and re-raises
        if the wrapped block raises, otherwise records ``ok``.
        """
        sequence = len(self._spans)
        outcome = "ok"
        cid: str | None = None
        try:
            with _ec1_trace(name, **attributes) as correlation:
                cid = correlation
                yield correlation
        except Exception:
            outcome = "error"
            self._spans.append(
                SpanRecord.create(
                    name, sequence, outcome, attributes=attributes, correlation_id=cid
                )
            )
            raise
        else:
            self._spans.append(
                SpanRecord.create(
                    name, sequence, outcome, attributes=attributes, correlation_id=cid
                )
            )

    @property
    def spans(self) -> tuple[SpanRecord, ...]:
        """An immutable snapshot of the append-only span log (in order)."""
        return tuple(self._spans)

    def __len__(self) -> int:
        return len(self._spans)

    def spans_named(self, name: str) -> tuple[SpanRecord, ...]:
        return tuple(s for s in self._spans if s.name == name)

    def to_dict(self) -> dict[str, Any]:
        return {"span_count": len(self._spans), "spans": [s.to_dict() for s in self._spans]}

    def fingerprint(self) -> str:
        """A deterministic content hash over the content-addressed span identities.

        Computed from the ``span_id`` values (whose cores exclude the volatile,
        runtime-generated ``correlation_id``) so trace evidence is reproducible
        regardless of ambient correlation context.
        """
        return content_hash(
            {"span_count": len(self._spans), "spans": [s.span_id for s in self._spans]}
        )


__all__ = ["SpanRecord", "TraceRecorder"]
