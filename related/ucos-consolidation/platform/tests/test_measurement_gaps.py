"""UCOS-EPIC-004 — Gap Engine tests (UCOS-UMA-001)."""

from __future__ import annotations

from platform.measurement.contracts import MeasurementKind
from platform.measurement.errors import GapMeasurementError
from platform.measurement.gaps import (
    DANGLING_EDGE,
    INCOMPLETE_TRACEABILITY,
    ISOLATED_ARTIFACT,
    UNASSIGNED_OWNER,
    UNKNOWN_PARENT,
    UNKNOWN_VOLUME,
    VOLUME_COUNT_MISMATCH,
    Gap,
    GapEngine,
    GapReport,
)
from platform.tests._measurement_helpers import complete_snapshot, gapped_snapshot

import pytest


def test_complete_population_has_no_gaps():
    report = GapEngine(complete_snapshot()).detect()
    assert report.total == 0
    assert report.clean is True
    assert report.structural_count == 0
    assert report.completeness_count == 0


def test_gapped_population_detects_every_gap_type():
    report = GapEngine(gapped_snapshot()).detect()
    assert report.clean is False
    assert {g.gap_type for g in report.gaps} == {
        UNKNOWN_VOLUME,
        UNKNOWN_PARENT,
        DANGLING_EDGE,
        VOLUME_COUNT_MISMATCH,
        INCOMPLETE_TRACEABILITY,
        UNASSIGNED_OWNER,
        ISOLATED_ARTIFACT,
    }
    assert report.structural_count == 4
    assert report.completeness_count == 3
    assert report.total == 7
    assert len(report) == 7
    assert len(report.of_type(DANGLING_EDGE)) == 1
    assert report.of_type(DANGLING_EDGE)[0].subject == "UCOS-DANGLING"
    assert report.report_id.startswith("UCOS-UMAGR-")


def test_gap_band_classification():
    structural = Gap.create(UNKNOWN_VOLUME, "UCOS-A003")
    completeness = Gap.create(UNASSIGNED_OWNER, "UCOS-A003")
    assert structural.structural is True
    assert completeness.structural is False
    assert structural.to_dict()["band"] == "structural"
    assert structural.gap_id.startswith("UCOS-UMAG-")


def test_gap_validation_fails_closed():
    with pytest.raises(GapMeasurementError):
        Gap.create("not-a-gap-type", "UCOS-A001")
    with pytest.raises(GapMeasurementError):
        Gap.create(UNKNOWN_VOLUME, "  ")


def test_engine_requires_snapshot():
    with pytest.raises(GapMeasurementError):
        GapEngine(object())  # type: ignore[arg-type]


def test_deterministic_and_as_measurement():
    a = GapEngine(gapped_snapshot()).detect()
    b = GapEngine(gapped_snapshot()).detect()
    assert a.fingerprint() == b.fingerprint()
    assert a.by_type == b.by_type
    m = a.as_measurement()
    assert m.kind is MeasurementKind.GAP
    assert m.subject == "registry.gaps"
    assert isinstance(a, GapReport)
