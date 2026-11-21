"""TASK-000007 — Observability: metrics + traces.

Dependency-free, default-on telemetry (PL-02). Provides:
    * an in-memory metric registry (counters, gauges, histograms);
    * a :func:`trace` span context manager that times a unit of work, binds a
      correlation id for the duration if none exists, records span metrics, and
      emits structured span logs (TASK-000006).

Correlation helpers are re-exported from :mod:`engine.foundation.obs.context`.
"""

from __future__ import annotations

import threading
import time
import uuid
from collections.abc import Iterator
from contextlib import contextmanager
from typing import Any

from engine.foundation.obs import context
from engine.foundation.obs.context import (
    correlation_id,
    new_correlation_id,
    reset_correlation_id,
    set_correlation_id,
)
from engine.foundation.obs.logging import get_logger

_logger = get_logger("telemetry")
_lock = threading.Lock()

_counters: dict[tuple[str, tuple[tuple[str, str], ...]], float] = {}
_gauges: dict[tuple[str, tuple[tuple[str, str], ...]], float] = {}
_histograms: dict[tuple[str, tuple[tuple[str, str], ...]], list[float]] = {}


def _key(name: str, labels: dict[str, Any]) -> tuple[str, tuple[tuple[str, str], ...]]:
    return name, tuple(sorted((str(k), str(v)) for k, v in labels.items()))


def metric_counter(name: str, value: float = 1.0, **labels: Any) -> None:
    """Increment a monotonic counter."""
    key = _key(name, labels)
    with _lock:
        _counters[key] = _counters.get(key, 0.0) + value


def metric_gauge(name: str, value: float, **labels: Any) -> None:
    """Set a gauge to ``value``."""
    key = _key(name, labels)
    with _lock:
        _gauges[key] = value


def metric_histogram(name: str, value: float, **labels: Any) -> None:
    """Record a sample into a histogram series."""
    key = _key(name, labels)
    with _lock:
        _histograms.setdefault(key, []).append(value)


def metrics_snapshot() -> dict[str, dict[str, Any]]:
    """Return a copy of all recorded metrics (for tests and evidence export)."""
    with _lock:
        return {
            "counters": {
                name: dict(labels) | {"value": value} for (name, labels), value in _counters.items()
            },
            "gauges": {
                name: dict(labels) | {"value": value} for (name, labels), value in _gauges.items()
            },
            "histograms": {
                name: {**dict(labels), "count": len(samples), "sum": sum(samples)}
                for (name, labels), samples in _histograms.items()
            },
        }


def reset_metrics() -> None:
    """Clear all metric state (test isolation)."""
    with _lock:
        _counters.clear()
        _gauges.clear()
        _histograms.clear()


@contextmanager
def trace(name: str, **attributes: Any) -> Iterator[str]:
    """Time a span. Binds a correlation id for its duration if none is set.

    Yields the active correlation id. On exit, span duration and outcome are
    recorded to metrics and emitted as a structured log line.
    """
    token = None
    if context.correlation_id() is None:
        token = context.set_correlation_id(uuid.uuid4().hex)
    cid = context.correlation_id()
    assert cid is not None  # noqa: S101 — invariant: a correlation id is always bound here
    start = time.perf_counter()
    _logger.debug(f"span.start:{name}", span=name, **attributes)
    try:
        yield cid
    except Exception as exc:
        duration_ms = (time.perf_counter() - start) * 1000.0
        metric_histogram("span.duration_ms", duration_ms, span=name, outcome="error")
        metric_counter("span.count", 1.0, span=name, outcome="error")
        _logger.error(
            f"span.error:{name}",
            span=name,
            duration_ms=round(duration_ms, 3),
            error=type(exc).__name__,
        )
        raise
    else:
        duration_ms = (time.perf_counter() - start) * 1000.0
        metric_histogram("span.duration_ms", duration_ms, span=name, outcome="ok")
        metric_counter("span.count", 1.0, span=name, outcome="ok")
        _logger.debug(f"span.end:{name}", span=name, duration_ms=round(duration_ms, 3))
    finally:
        if token is not None:
            reset_correlation_id(token)


__all__ = [
    "correlation_id",
    "set_correlation_id",
    "new_correlation_id",
    "reset_correlation_id",
    "metric_counter",
    "metric_gauge",
    "metric_histogram",
    "metrics_snapshot",
    "reset_metrics",
    "trace",
]
