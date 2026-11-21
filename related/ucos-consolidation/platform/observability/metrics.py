"""EC2-TASK-000179 — Platform Metrics (EC2-EPIC-013).

A deterministic, in-memory metric registry providing the three metric kinds
(counter, gauge, histogram) with labels. It is the platform-side, content-addressed
source of truth for metric evidence and **reuses** the certified EC-1 telemetry
discipline additively — every record is also emitted through
:mod:`engine.foundation.obs.telemetry` so the platform inherits the EC-1
observability substrate without modifying it.

Design (IMP-007 §5 determinism; PC-12 monitoring):
    * :class:`MetricSample` is immutable and content-addressed over
      ``(name, kind, labels)`` — its ``sample_id`` identifies the series, not a
      single observation, so a snapshot is stable and comparable across runs.
    * :class:`MetricRegistry` is deterministic: counters accumulate, gauges are
      last-writer, histograms retain ordered samples; :meth:`MetricRegistry.snapshot`
      and :meth:`MetricRegistry.fingerprint` are pure functions of the recorded
      series in sorted order (no wall-clock).

This module records **no** wall-clock time and **no** secret material (SEC-04).
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field
from platform.foundation.contracts import content_hash
from platform.observability.contracts import MetricKind
from platform.observability.errors import MetricError
from typing import Any

from engine.foundation.obs import telemetry as _ec1_telemetry


def _label_tuple(labels: Mapping[str, Any] | None) -> tuple[tuple[str, str], ...]:
    """Return labels as a deterministic, sorted tuple of ``(str, str)`` pairs."""
    if not labels:
        return ()
    return tuple(sorted((str(k), str(v)) for k, v in labels.items()))


@dataclass(frozen=True, slots=True)
class MetricSample:
    """An immutable, content-addressed metric series identity + accumulated value."""

    name: str
    kind: MetricKind
    value: float
    labels: tuple[tuple[str, str], ...] = ()
    count: int = 0
    sample_id: str = ""

    @classmethod
    def create(
        cls,
        name: str,
        kind: MetricKind,
        value: float,
        *,
        labels: Mapping[str, Any] | None = None,
        count: int = 0,
    ) -> MetricSample:
        """Build a sample with a deterministic, content-addressed ``sample_id``."""
        if not isinstance(name, str) or not name:
            raise MetricError("metric name is required")
        if not isinstance(kind, MetricKind):
            raise MetricError("metric kind must be a MetricKind", name=name)
        label_tuple = _label_tuple(labels)
        core = {"name": name, "kind": kind.value, "labels": [list(p) for p in label_tuple]}
        return cls(
            name=name,
            kind=kind,
            value=float(value),
            labels=label_tuple,
            count=count,
            sample_id=f"UCOS-MTRC-{content_hash(core)[:16]}",
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "sample_id": self.sample_id,
            "name": self.name,
            "kind": self.kind.value,
            "value": self.value,
            "labels": {k: v for k, v in self.labels},
            "count": self.count,
        }


@dataclass(frozen=True, slots=True)
class _Series:
    name: str
    kind: MetricKind
    labels: tuple[tuple[str, str], ...]
    value: float = 0.0
    samples: tuple[float, ...] = field(default_factory=tuple)


class MetricRegistry:
    """A deterministic, additive registry of platform metrics (reuses EC-1 telemetry)."""

    __slots__ = ("_series", "_mirror")

    def __init__(self, *, mirror_to_ec1: bool = True) -> None:
        self._series: dict[tuple[str, tuple[tuple[str, str], ...]], _Series] = {}
        self._mirror = mirror_to_ec1

    def counter(self, name: str, value: float = 1.0, **labels: Any) -> None:
        """Increment a monotonic counter (reused EC-1 counter emitted additively)."""
        if value < 0:
            raise MetricError("counter increments must be non-negative", name=name)
        key = (name, _label_tuple(labels))
        series = self._series.get(key)
        if series is None or series.kind is not MetricKind.COUNTER:
            if series is not None:
                raise MetricError("metric kind conflict", name=name, kind=series.kind.value)
            series = _Series(name, MetricKind.COUNTER, key[1])
        self._series[key] = _Series(name, MetricKind.COUNTER, key[1], value=series.value + value)
        if self._mirror:
            _ec1_telemetry.metric_counter(name, value, **labels)

    def gauge(self, name: str, value: float, **labels: Any) -> None:
        """Set a gauge to ``value`` (last-writer-wins)."""
        key = (name, _label_tuple(labels))
        existing = self._series.get(key)
        if existing is not None and existing.kind is not MetricKind.GAUGE:
            raise MetricError("metric kind conflict", name=name, kind=existing.kind.value)
        self._series[key] = _Series(name, MetricKind.GAUGE, key[1], value=float(value))
        if self._mirror:
            _ec1_telemetry.metric_gauge(name, value, **labels)

    def histogram(self, name: str, value: float, **labels: Any) -> None:
        """Record a sample into a histogram series (ordered retention)."""
        key = (name, _label_tuple(labels))
        existing = self._series.get(key)
        if existing is not None and existing.kind is not MetricKind.HISTOGRAM:
            raise MetricError("metric kind conflict", name=name, kind=existing.kind.value)
        samples = (existing.samples if existing else ()) + (float(value),)
        self._series[key] = _Series(
            name, MetricKind.HISTOGRAM, key[1], value=sum(samples), samples=samples
        )
        if self._mirror:
            _ec1_telemetry.metric_histogram(name, value, **labels)

    def __len__(self) -> int:
        return len(self._series)

    def total_count(self) -> int:
        """The total number of recorded observations across all series."""
        total = 0
        for series in self._series.values():
            if series.kind is MetricKind.HISTOGRAM:
                total += len(series.samples)
            else:
                total += 1
        return total

    def samples(self) -> tuple[MetricSample, ...]:
        """Every series as a :class:`MetricSample` in deterministic sorted order."""
        out: list[MetricSample] = []
        for _key, series in sorted(self._series.items()):
            count = len(series.samples) if series.kind is MetricKind.HISTOGRAM else 0
            out.append(
                MetricSample.create(
                    series.name,
                    series.kind,
                    series.value,
                    labels={k: v for k, v in series.labels},
                    count=count,
                )
            )
        return tuple(out)

    def value_of(self, name: str, **labels: Any) -> float:
        """Return the accumulated value of one series (raises if absent)."""
        key = (name, _label_tuple(labels))
        series = self._series.get(key)
        if series is None:
            raise MetricError("no such metric series", name=name)
        return series.value

    def snapshot(self) -> dict[str, Any]:
        """A deterministic, serializable snapshot of all series (sorted)."""
        return {"metric_count": len(self._series), "series": [s.to_dict() for s in self.samples()]}

    def fingerprint(self) -> str:
        """A deterministic content hash proving reproducible metric state."""
        return content_hash(self.snapshot())


__all__ = ["MetricSample", "MetricRegistry"]
