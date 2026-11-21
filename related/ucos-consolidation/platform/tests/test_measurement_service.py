"""UCOS-EPIC-004 — Measurement service composition tests (UCOS-UMA-001)."""

from __future__ import annotations

from platform.measurement.contracts import UMA_ID, MeasurementKind
from platform.measurement.errors import MeasurementError
from platform.measurement.health import measurement_health_checks
from platform.measurement.registry import MeasurementRegistry
from platform.measurement.service import (
    MeasurementService,
    build_measurement_service,
)
from platform.observability.contracts import HealthStatus
from platform.observability.health import HealthRegistry
from platform.tests._measurement_helpers import complete_source, gapped_source

import pytest


def test_build_requires_source():
    with pytest.raises(MeasurementError):
        build_measurement_service(object())  # type: ignore[arg-type]


def test_service_rejects_bad_dependencies():
    with pytest.raises(MeasurementError):
        MeasurementService(object())  # type: ignore[arg-type]
    with pytest.raises(MeasurementError):
        MeasurementService(complete_source(), registry=object())  # type: ignore[arg-type]
    with pytest.raises(MeasurementError):
        MeasurementService(complete_source(), health_registry=object())  # type: ignore[arg-type]


def test_operations_and_measure_records_registry():
    svc = build_measurement_service(complete_source())
    assert svc.uma_id == UMA_ID
    run = svc.measure()
    assert run.run_id.startswith("UCOS-UMAR-")
    # exactly the four kind-level measurements are recorded.
    assert svc.registry.count == 4
    kinds = {m.kind for m in svc.registry.all()}
    assert kinds == set(MeasurementKind)
    # re-measure is idempotent (same Truth -> same measurement ids).
    svc.measure()
    assert svc.registry.count == 4


def test_report_shape():
    rep = build_measurement_service(complete_source()).report()
    assert rep["uma_id"] == UMA_ID
    assert rep["counts"]["artifacts"] == 2
    assert rep["traceability"]["overall_percentage"] == 100.0
    assert rep["gaps"]["total"] == 0
    assert rep["metric_count"] >= 6


def test_health_status_complete_vs_gapped():
    assert (
        build_measurement_service(complete_source()).health_status(strict=True)
        is HealthStatus.HEALTHY
    )
    gsvc = build_measurement_service(gapped_source())
    assert gsvc.health_status(strict=False) is HealthStatus.DEGRADED
    assert gsvc.health_status(strict=True) is HealthStatus.UNHEALTHY
    endpoint = build_measurement_service(complete_source()).health_report(strict=True)
    assert endpoint["healthy"] is True


def test_to_dict_cites_governance_and_contracts():
    d = build_measurement_service(complete_source()).to_dict()
    assert d["instrument"] == UMA_ID
    assert "DP-03" in d["governance_authorities"]
    assert len(d["contracts"]) == 7
    assert "measurement-determinism" in d["health_checks"]


def test_service_accepts_supplied_registry_and_health_registry():
    reg = MeasurementRegistry()
    hr = HealthRegistry()
    for c in measurement_health_checks():
        hr.register(c)
    svc = MeasurementService(complete_source(), registry=reg, health_registry=hr)
    svc.measure()
    assert reg.count == 4
    assert svc.health_status(strict=True) is HealthStatus.HEALTHY


def test_measurement_never_creates_truth():
    """Every recorded measurement lives in the UCOS-UMA* namespace, disjoint from Truth."""
    svc = build_measurement_service(complete_source())
    svc.measure()
    truth_ids = {"UCOS-A001", "UCOS-A002"}
    for m in svc.registry.all():
        assert m.measurement_id.startswith("UCOS-UMA")
        assert m.measurement_id not in truth_ids
    # fingerprint of a fresh run is stable (pure function of Truth).
    assert svc.fingerprint() == svc.fingerprint()
