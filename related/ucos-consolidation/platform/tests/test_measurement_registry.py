"""UCOS-EPIC-004 — Measurement Registry tests (UCOS-UMA-001)."""

from __future__ import annotations

from platform.measurement.contracts import Measurement, MeasurementKind
from platform.measurement.errors import MeasurementRegistryError
from platform.measurement.registry import MeasurementRegistry

import pytest


def _m(subject: str, payload: dict) -> Measurement:
    return Measurement.create(MeasurementKind.METRIC, subject, payload=payload)


def test_record_is_idempotent_by_id():
    reg = MeasurementRegistry()
    m = _m("s", {"a": 1})
    assert reg.record(m) is m
    assert reg.record(m) is m  # idempotent
    assert reg.count == 1
    assert len(reg) == 1
    assert reg.has(m.measurement_id) is True
    assert reg.get(m.measurement_id) is m
    assert m.measurement_id in reg


def test_conflicting_duplicate_is_refused():
    reg = MeasurementRegistry()
    # Two records forced to share an id but carry different content (fail-closed).
    a = Measurement(MeasurementKind.GAP, "s", "one", {"x": 1}, measurement_id="UCOS-UMAM-DUP")
    b = Measurement(MeasurementKind.GAP, "s", "two", {"x": 2}, measurement_id="UCOS-UMAM-DUP")
    reg.record(a)
    with pytest.raises(MeasurementRegistryError):
        reg.record(b)


def test_record_all_and_kind_views():
    reg = MeasurementRegistry()
    reg.record_all(
        [
            Measurement.create(MeasurementKind.GAP, "g", payload={"n": 1}),
            Measurement.create(MeasurementKind.COVERAGE, "c", payload={"n": 2}),
            Measurement.create(MeasurementKind.METRIC, "m", payload={"n": 3}),
        ]
    )
    assert reg.count == 3
    assert len(reg.of_kind(MeasurementKind.GAP)) == 1
    assert reg.counts_by_kind() == {"coverage": 1, "gap": 1, "metric": 1}
    assert len(reg.all()) == 3


def test_bad_inputs_fail_closed():
    reg = MeasurementRegistry()
    with pytest.raises(MeasurementRegistryError):
        reg.record(object())  # type: ignore[arg-type]
    with pytest.raises(MeasurementRegistryError):
        reg.get("UCOS-UMAM-NONE")
    with pytest.raises(MeasurementRegistryError):
        reg.of_kind("gap")  # type: ignore[arg-type]


def test_fingerprint_is_deterministic():
    reg1 = MeasurementRegistry()
    reg2 = MeasurementRegistry()
    for reg in (reg1, reg2):
        reg.record(_m("s", {"a": 1}))
    assert reg1.fingerprint() == reg2.fingerprint()
    assert reg1.to_dict()["count"] == 1
