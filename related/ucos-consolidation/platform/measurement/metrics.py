"""UCOS-EPIC-004 — Metrics Engine (UCOS-UMA-001).

Computes the quantitative metric series over the Registry population — counters for the
population sizes and gauges for every distribution (artifacts by status/program/category/
volume, relationships by type). Every metric is a pure function of the
:class:`~platform.measurement.source.TruthSnapshot`; recompute over identical Truth is
byte-identical (IMP-007 §5). The engine reuses the certified Observability
:class:`~platform.observability.contracts.MetricKind` vocabulary and authors no Truth.
"""

from __future__ import annotations

from dataclasses import dataclass
from platform.foundation.contracts import content_hash
from platform.measurement.contracts import Measurement, MeasurementKind, Metric, MetricKind
from platform.measurement.errors import MetricsError
from platform.measurement.source import TruthSnapshot
from typing import Any


@dataclass(frozen=True, slots=True)
class MetricSet:
    """An immutable, content-addressed set of metric series over Registry Truth."""

    metrics: tuple[Metric, ...]
    metricset_id: str = ""

    @classmethod
    def create(cls, metrics: tuple[Metric, ...]) -> MetricSet:
        ordered = tuple(sorted(metrics, key=lambda m: (m.name, m.labels)))
        core = {"metrics": [m.to_dict() for m in ordered]}
        return cls(metrics=ordered, metricset_id=f"UCOS-UMAT-{content_hash(core)[:16]}")

    def __len__(self) -> int:
        return len(self.metrics)

    def get(self, name: str, **labels: str) -> Metric:
        """Return the metric series with ``name`` and exactly ``labels`` (fail-closed)."""
        wanted = tuple(sorted(labels.items()))
        for metric in self.metrics:
            if metric.name == name and metric.labels == wanted:
                return metric
        raise MetricsError("no such metric series", name=name, labels=str(wanted))

    def value(self, name: str, **labels: str) -> float:
        """Convenience accessor for a single metric's value."""
        return self.get(name, **labels).value

    def to_dict(self) -> dict[str, Any]:
        return {
            "metricset_id": self.metricset_id,
            "metric_count": len(self.metrics),
            "metrics": [m.to_dict() for m in self.metrics],
        }

    def fingerprint(self) -> str:
        return content_hash(self.to_dict())

    def as_measurement(self) -> Measurement:
        """Wrap the metric set as a recordable :class:`Measurement`."""
        return Measurement.create(
            MeasurementKind.METRIC,
            "registry.metrics",
            summary=f"{len(self.metrics)} metric series over the Registry population",
            payload=self.to_dict(),
        )


def _counts(values: object) -> dict[str, int]:
    """Deterministic value→count map over an iterable of string keys."""
    counts: dict[str, int] = {}
    for value in values:  # type: ignore[union-attr]
        key = str(value)
        counts[key] = counts.get(key, 0) + 1
    return counts


class MetricsEngine:
    """Deterministically computes quantitative metrics from a Truth snapshot."""

    __slots__ = ("_snapshot",)

    def __init__(self, snapshot: TruthSnapshot) -> None:
        if not isinstance(snapshot, TruthSnapshot):
            raise MetricsError("MetricsEngine requires a TruthSnapshot")
        self._snapshot = snapshot

    def measure(self) -> MetricSet:
        """Compute the full metric set (counters + distribution gauges)."""
        arts = self._snapshot.artifacts
        rels = self._snapshot.relationships
        vols = self._snapshot.volumes
        metrics: list[Metric] = [
            Metric.create("registry.artifacts.total", MetricKind.COUNTER, len(arts)),
            Metric.create("registry.relationships.total", MetricKind.COUNTER, len(rels)),
            Metric.create("registry.volumes.total", MetricKind.COUNTER, len(vols)),
        ]

        for status, count in _counts(a.status.value for a in arts).items():
            metrics.append(
                Metric.create(
                    "registry.artifacts.by_status",
                    MetricKind.GAUGE,
                    count,
                    labels={"status": status},
                )
            )
        for program, count in _counts(a.program for a in arts if a.program).items():
            metrics.append(
                Metric.create(
                    "registry.artifacts.by_program",
                    MetricKind.GAUGE,
                    count,
                    labels={"program": program},
                )
            )
        for category, count in _counts(a.category for a in arts if a.category).items():
            metrics.append(
                Metric.create(
                    "registry.artifacts.by_category",
                    MetricKind.GAUGE,
                    count,
                    labels={"category": category},
                )
            )
        for volume, count in _counts(a.volume for a in arts if a.volume).items():
            metrics.append(
                Metric.create(
                    "registry.artifacts.by_volume",
                    MetricKind.GAUGE,
                    count,
                    labels={"volume": volume},
                )
            )
        for rel_type, count in _counts(r.type for r in rels).items():
            metrics.append(
                Metric.create(
                    "registry.relationships.by_type",
                    MetricKind.GAUGE,
                    count,
                    labels={"type": rel_type},
                )
            )
        return MetricSet.create(tuple(metrics))


__all__ = ["MetricSet", "MetricsEngine"]
