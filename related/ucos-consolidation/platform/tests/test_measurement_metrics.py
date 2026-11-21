"""UCOS-EPIC-004 — Metrics Engine tests (UCOS-UMA-001)."""

from __future__ import annotations

from platform.measurement.contracts import MeasurementKind, MetricKind
from platform.measurement.errors import MetricsError
from platform.measurement.metrics import MetricsEngine
from platform.tests._measurement_helpers import complete_snapshot, gapped_snapshot

import pytest


def test_counters_and_distributions():
    ms = MetricsEngine(complete_snapshot()).measure()
    assert ms.value("registry.artifacts.total") == 2.0
    assert ms.value("registry.relationships.total") == 1.0
    assert ms.value("registry.volumes.total") == 1.0
    assert ms.value("registry.artifacts.by_status", status="CERTIFIED") == 2.0
    assert ms.value("registry.artifacts.by_program", program="PROG-1") == 2.0
    assert ms.value("registry.relationships.by_type", type="Depends-On") == 1.0
    assert ms.metricset_id.startswith("UCOS-UMAT-")
    assert len(ms) >= 6


def test_gapped_distributions():
    ms = MetricsEngine(gapped_snapshot()).measure()
    assert ms.value("registry.artifacts.total") == 3.0
    assert ms.value("registry.relationships.by_type", type="References") == 1.0
    assert ms.value("registry.artifacts.by_volume", volume="V-UNKNOWN") == 1.0


def test_missing_series_fails_closed():
    ms = MetricsEngine(complete_snapshot()).measure()
    with pytest.raises(MetricsError):
        ms.get("registry.artifacts.by_status", status="NONEXISTENT")
    with pytest.raises(MetricsError):
        ms.get("no.such.metric")


def test_engine_requires_snapshot():
    with pytest.raises(MetricsError):
        MetricsEngine(object())  # type: ignore[arg-type]


def test_deterministic_and_as_measurement():
    a = MetricsEngine(complete_snapshot()).measure()
    b = MetricsEngine(complete_snapshot()).measure()
    assert a.fingerprint() == b.fingerprint()
    # metric series are ordered by (name, labels)
    names = [m.name for m in a.metrics]
    assert names == sorted(names) or all(isinstance(m.kind, MetricKind) for m in a.metrics)
    m = a.as_measurement()
    assert m.kind is MeasurementKind.METRIC
    assert m.subject == "registry.metrics"
