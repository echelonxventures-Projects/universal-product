"""UCOS-EPIC-004 — Coverage Engine (traceability) tests (UCOS-UMA-001)."""

from __future__ import annotations

from platform.measurement.contracts import MeasurementKind
from platform.measurement.coverage import CoverageEngine
from platform.measurement.errors import CoverageMeasurementError
from platform.tests._measurement_helpers import (
    complete_snapshot,
    empty_source,
    gapped_snapshot,
)

import pytest


def test_complete_traceability_is_fully_covered():
    cov = CoverageEngine(complete_snapshot()).measure()
    assert cov.artifact_total == 2
    assert cov.overall_percentage == 100.0
    assert cov.fully_traced_count == 2
    assert cov.fully_traced_percentage == 100.0
    assert cov.stage_percentage("requirement") == 100.0
    assert cov.coverage_id.startswith("UCOS-UMAC-")


def test_gapped_traceability_is_partial():
    cov = CoverageEngine(gapped_snapshot()).measure()
    assert cov.artifact_total == 3
    assert cov.fully_traced_count == 2  # only A1, A2 are fully traced
    # requirement stage is populated for all 3; other stages for only 2/3.
    assert cov.stage_percentage("requirement") == 100.0
    assert cov.stage_percentage("operations") == pytest.approx(66.6667, abs=1e-3)
    assert 0.0 < cov.overall_percentage < 100.0


def test_empty_population_is_zero_not_error():
    cov = CoverageEngine(empty_source().snapshot()).measure()
    assert cov.artifact_total == 0
    assert cov.overall_percentage == 0.0
    assert cov.fully_traced_percentage == 0.0
    assert cov.stage_percentage("design") == 0.0


def test_unknown_stage_fails_closed():
    cov = CoverageEngine(complete_snapshot()).measure()
    with pytest.raises(CoverageMeasurementError):
        cov.stage_percentage("not-a-stage")


def test_engine_requires_snapshot():
    with pytest.raises(CoverageMeasurementError):
        CoverageEngine(object())  # type: ignore[arg-type]


def test_deterministic_and_as_measurement():
    a = CoverageEngine(complete_snapshot()).measure()
    b = CoverageEngine(complete_snapshot()).measure()
    assert a.fingerprint() == b.fingerprint()
    m = a.as_measurement()
    assert m.kind is MeasurementKind.COVERAGE
    assert m.subject == "registry.traceability"
