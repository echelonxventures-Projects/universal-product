"""ZG-P-02 — coverage service composition tests."""

from __future__ import annotations

from platform.coverage.errors import CoverageError
from platform.coverage.graph import CoverageGraph
from platform.coverage.service import (
    CoverageEvidence,
    CoverageService,
    build_coverage_service,
)
from platform.observability.contracts import HealthStatus
from platform.observability.health import HealthRegistry
from platform.tests._coverage_helpers import complete_source, gapped_source

import pytest


def test_build_requires_source():
    with pytest.raises(CoverageError):
        build_coverage_service(object())  # type: ignore[arg-type]


def test_service_requires_engine_and_valid_registry():
    with pytest.raises(CoverageError):
        CoverageService(object())  # type: ignore[arg-type]


def test_service_operations_mirror_engine():
    svc = build_coverage_service(complete_source())
    assert isinstance(svc.compute(), CoverageGraph)
    assert svc.verify().ok
    assert svc.reconcile() is not None
    assert svc.fingerprint()
    assert svc.report()["universe_coverage_percentage"] == 100.0
    assert svc.registry.node_count > 0
    assert svc.engine is not None


def test_health_report_and_status():
    svc = build_coverage_service(complete_source())
    endpoint = svc.health_report(strict=True)
    assert endpoint["healthy"] is True
    assert svc.health_status(strict=True) is HealthStatus.HEALTHY
    # gapped: degraded baseline, unhealthy strict.
    gsvc = build_coverage_service(gapped_source())
    assert gsvc.health_status(strict=False) is HealthStatus.DEGRADED
    assert gsvc.health_status(strict=True) is HealthStatus.UNHEALTHY


def test_certify_and_evidence():
    svc = build_coverage_service(complete_source())
    cert = svc.certify(strict=True)
    assert cert.certified
    ev = svc.evidence(strict=True)
    assert isinstance(ev, CoverageEvidence)
    assert ev.universe_percentage == 100.0
    assert ev.gap_count == 0
    assert ev.orphan_count == 0
    assert ev.certification_status == "CERTIFIED"
    assert ev.evidence_id.startswith("UCOS-COVE-EV-")
    # deterministic evidence.
    assert svc.evidence(strict=True).fingerprint() == ev.fingerprint()
    assert ev.to_dict()["node_count"] == ev.node_count


def test_to_dict_cites_governance_and_contracts():
    svc = build_coverage_service(complete_source())
    d = svc.to_dict()
    assert "GOV-002" in d["governance_authorities"]
    assert "MIP-ZG-001" in d["governance_authorities"]
    assert len(d["contracts"]) == 5
    assert "coverage-fingerprint-mismatch" in d["health_checks"]


def test_service_accepts_supplied_health_registry():
    from platform.coverage.engine import CoverageEngine
    from platform.coverage.health import coverage_health_checks

    hr = HealthRegistry()
    for c in coverage_health_checks():
        hr.register(c)
    svc = CoverageService(CoverageEngine(complete_source()), health_registry=hr)
    assert svc.health_status(strict=True) is HealthStatus.HEALTHY


def test_service_rejects_bad_health_registry():
    from platform.coverage.engine import CoverageEngine

    with pytest.raises(CoverageError):
        CoverageService(CoverageEngine(complete_source()), health_registry=object())  # type: ignore[arg-type]
