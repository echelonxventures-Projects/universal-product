"""UCOS-EPIC-004 — Measurement health tests (UCOS-UMA-001)."""

from __future__ import annotations

from platform.measurement.coverage import CoverageEngine
from platform.measurement.gaps import GapEngine
from platform.measurement.health import (
    DETERMINISM_CHECK,
    MeasurementHealth,
    measurement_health_checks,
)
from platform.measurement.registry import MeasurementRegistry
from platform.measurement.service import build_measurement_service
from platform.observability.contracts import HealthStatus
from platform.tests._measurement_helpers import (
    complete_snapshot,
    complete_source,
    gapped_snapshot,
)

import pytest


def test_five_checks_registered():
    assert len(measurement_health_checks()) == 5


def test_complete_population_is_healthy():
    health = MeasurementHealth(
        gap_report=GapEngine(complete_snapshot()).detect(),
        coverage=CoverageEngine(complete_snapshot()).measure(),
        registry=MeasurementRegistry(),
        deterministic=True,
    )
    assert health.integrity_ok is True
    assert health.healthy(strict=True) is True
    probe = health.probe(strict=True)
    assert all(s is HealthStatus.HEALTHY for s in probe.values())


def test_gapped_population_degrades_then_fails_strict():
    health = MeasurementHealth(
        gap_report=GapEngine(gapped_snapshot()).detect(),
        coverage=CoverageEngine(gapped_snapshot()).measure(),
        registry=MeasurementRegistry(),
        deterministic=True,
    )
    # integrity intact (engine determinism + registry consistency), quality gaps present.
    assert health.integrity_ok is True
    non_strict = health.probe(strict=False)
    strict = health.probe(strict=True)
    assert non_strict["structural-truth-gaps"] is HealthStatus.DEGRADED
    assert strict["structural-truth-gaps"] is HealthStatus.UNHEALTHY
    assert health.structural_gap_count() == 4
    assert health.traceability_gap_count() == 1
    assert health.ownership_gap_count() == 1


def test_non_determinism_is_unhealthy():
    health = MeasurementHealth(
        gap_report=GapEngine(complete_snapshot()).detect(),
        coverage=CoverageEngine(complete_snapshot()).measure(),
        registry=MeasurementRegistry(),
        deterministic=False,
    )
    assert health.probe()[DETERMINISM_CHECK] is HealthStatus.UNHEALTHY
    assert health.integrity_ok is False


def test_registry_consistency_check():
    reg = MeasurementRegistry()
    svc = build_measurement_service(complete_source())
    run = svc.measure()
    reg.record_all(run.measurements())
    health = MeasurementHealth(
        gap_report=run.gaps, coverage=run.coverage, registry=reg, deterministic=True
    )
    assert health.registry_consistent() is True


def test_bad_inputs_fail_closed():
    with pytest.raises(TypeError):
        MeasurementHealth(
            gap_report=object(),  # type: ignore[arg-type]
            coverage=CoverageEngine(complete_snapshot()).measure(),
            registry=MeasurementRegistry(),
            deterministic=True,
        )
    with pytest.raises(TypeError):
        MeasurementHealth(
            gap_report=GapEngine(complete_snapshot()).detect(),
            coverage=object(),  # type: ignore[arg-type]
            registry=MeasurementRegistry(),
            deterministic=True,
        )
    with pytest.raises(TypeError):
        MeasurementHealth(
            gap_report=GapEngine(complete_snapshot()).detect(),
            coverage=CoverageEngine(complete_snapshot()).measure(),
            registry=object(),  # type: ignore[arg-type]
            deterministic=True,
        )
