"""UCOS-EPIC-004 — measurement vocabulary & contract tests (UCOS-UMA-001)."""

from __future__ import annotations

from platform.measurement.contracts import (
    GOVERNANCE_AUTHORITIES,
    MEASUREMENT_CONTRACTS,
    UMA_ID,
    Measurement,
    MeasurementKind,
    Metric,
    MetricKind,
    measurement_contract_names,
)
from platform.measurement.errors import MeasurementContractError

import pytest


def test_uma_identity_and_contract_surface():
    assert UMA_ID == "UCOS-UMA-001"
    assert len(MEASUREMENT_CONTRACTS) == 7
    assert len(measurement_contract_names()) == 7
    assert "DP-03" in GOVERNANCE_AUTHORITIES
    assert "UCOS-EPIC-004" in GOVERNANCE_AUTHORITIES


def test_metric_identity_is_series_not_value():
    a = Metric.create("m", MetricKind.GAUGE, 1, labels={"k": "v"})
    b = Metric.create("m", MetricKind.GAUGE, 999, labels={"k": "v"})
    # The id is a pure function of (name, kind, labels) — value-independent.
    assert a.metric_id == b.metric_id
    assert a.metric_id.startswith("UCOS-UMAX-")
    assert a.fingerprint() != b.fingerprint()  # fingerprint includes value
    assert a.to_dict()["value"] == 1.0


def test_metric_validation():
    with pytest.raises(MeasurementContractError):
        Metric.create("", MetricKind.GAUGE, 1)
    with pytest.raises(MeasurementContractError):
        Metric.create("m", object(), 1)  # type: ignore[arg-type]
    with pytest.raises(MeasurementContractError):
        Metric.create("m", MetricKind.GAUGE, "x")  # type: ignore[arg-type]
    with pytest.raises(MeasurementContractError):
        Metric.create("m", MetricKind.GAUGE, True)  # bool is not numeric here
    with pytest.raises(MeasurementContractError):
        Metric.create("m", MetricKind.GAUGE, 1, labels={"k": 5})  # type: ignore[dict-item]


def test_measurement_identity_and_idempotence():
    m1 = Measurement.create(MeasurementKind.METRIC, "s", summary="x", payload={"a": 1})
    m2 = Measurement.create(MeasurementKind.METRIC, "s", summary="y", payload={"a": 1})
    # summary is not part of identity; payload + kind + subject are.
    assert m1.measurement_id == m2.measurement_id
    assert m1.measurement_id.startswith("UCOS-UMAM-")
    assert m1.to_dict()["kind"] == "metric"


def test_measurement_validation():
    with pytest.raises(MeasurementContractError):
        Measurement.create(object(), "s")  # type: ignore[arg-type]
    with pytest.raises(MeasurementContractError):
        Measurement.create(MeasurementKind.GAP, "  ")
    with pytest.raises(MeasurementContractError):
        Measurement.create(MeasurementKind.GAP, "s", payload={"bad": object()})
    with pytest.raises(MeasurementContractError):
        Measurement.create(MeasurementKind.GAP, "s", payload=["not", "a", "map"])  # type: ignore[arg-type]


def test_measurement_ids_are_disjoint_from_truth_ids():
    """A measurement id can never collide with a Registry universal id (UCOS-*)."""
    m = Measurement.create(MeasurementKind.ENUMERATION, "registry.population")
    assert m.measurement_id.startswith("UCOS-UMA")
    assert not m.measurement_id.startswith("UCOS-A")  # not a truth artifact id shape
