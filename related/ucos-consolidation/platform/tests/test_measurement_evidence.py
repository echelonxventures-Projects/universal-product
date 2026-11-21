"""UCOS-EPIC-004 — Measurement evidence tests (UCOS-UMA-001)."""

from __future__ import annotations

from platform.measurement.errors import MeasurementEvidenceError
from platform.measurement.evidence import MeasurementEvidence
from platform.measurement.service import build_measurement_service
from platform.tests._measurement_helpers import complete_source, gapped_source

import pytest


def test_evidence_requires_truth_fingerprint():
    with pytest.raises(MeasurementEvidenceError):
        MeasurementEvidence.create(
            truth_fingerprint="",
            enumeration_fingerprint="e",
            metrics_fingerprint="m",
            coverage_fingerprint="c",
            gaps_fingerprint="g",
            registry_fingerprint="r",
            artifact_count=0,
            relationship_count=0,
            volume_count=0,
            traceability_percentage=0.0,
            fully_traced_count=0,
            gap_count=0,
            structural_gap_count=0,
            health_status="healthy",
        )


def test_service_evidence_is_deterministic_and_complete():
    svc = build_measurement_service(complete_source())
    ev = svc.evidence(strict=True)
    assert ev.evidence_id.startswith("UCOS-UMAV-")
    assert ev.artifact_count == 2
    assert ev.relationship_count == 1
    assert ev.volume_count == 1
    assert ev.traceability_percentage == 100.0
    assert ev.fully_traced_count == 2
    assert ev.gap_count == 0
    assert ev.structural_gap_count == 0
    assert ev.health_status == "healthy"
    # deterministic across recompute.
    recomputed = build_measurement_service(complete_source()).evidence(strict=True)
    assert recomputed.fingerprint() == ev.fingerprint()
    assert ev.to_dict()["evidence_id"] == ev.evidence_id


def test_gapped_evidence_reports_gaps():
    ev = build_measurement_service(gapped_source()).evidence(strict=True)
    assert ev.gap_count == 7
    assert ev.structural_gap_count == 4
    assert ev.health_status == "unhealthy"
