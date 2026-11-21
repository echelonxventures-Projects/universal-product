"""EC2-TASK-000131 — Artifact Explorer health + evidence tests (EC2-EPIC-009).

Covers the read-only referential-integrity health probe over the consumed EC2-EPIC-007
ledgers (registry / dispatch / provenance) and the deterministic runtime evidence record.
"""

from __future__ import annotations

from platform.artifact_explorer.evidence import ExplorerEvidence
from platform.artifact_explorer.health import (
    DISPATCH_CHECK,
    PROVENANCE_CHECK,
    REGISTRY_CHECK,
    ExplorerHealth,
    artifact_explorer_health_checks,
)
from platform.generation.dispatch import DispatchLedger, DispatchRecord
from platform.generation.provenance import ProvenanceLedger, RequestProvenance
from platform.generation.registry import GenerationRequestRegistry
from platform.observability.contracts import HealthStatus
from platform.tests.artifact_explorer_helpers import (
    dispatch_for,
    make_request,
    provenance_for,
)

import pytest


def test_health_checks_are_all_critical():
    checks = artifact_explorer_health_checks()
    names = {c.name for c in checks}
    assert names == {REGISTRY_CHECK, PROVENANCE_CHECK, DISPATCH_CHECK}
    assert all(c.critical for c in checks)


def test_health_rejects_invalid_components():
    reg = GenerationRequestRegistry()
    disp = DispatchLedger()
    prov = ProvenanceLedger()
    with pytest.raises(TypeError):
        ExplorerHealth("nope", disp, prov)  # type: ignore[arg-type]
    with pytest.raises(TypeError):
        ExplorerHealth(reg, "nope", prov)  # type: ignore[arg-type]
    with pytest.raises(TypeError):
        ExplorerHealth(reg, disp, "nope")  # type: ignore[arg-type]


def test_health_healthy_when_references_resolve():
    reg = GenerationRequestRegistry()
    disp = DispatchLedger()
    prov = ProvenanceLedger()
    req = make_request(reg)
    dispatch_for(disp, req)
    provenance_for(prov, req)
    health = ExplorerHealth(reg, disp, prov)
    assert health.healthy is True
    assert health.orphaned_dispatches() == ()
    assert health.orphaned_provenance() == ()
    probe = health.probe()
    assert probe[REGISTRY_CHECK] is HealthStatus.HEALTHY
    assert probe[DISPATCH_CHECK] is HealthStatus.HEALTHY
    assert probe[PROVENANCE_CHECK] is HealthStatus.HEALTHY


def test_health_unhealthy_on_orphaned_dispatch():
    reg = GenerationRequestRegistry()
    disp = DispatchLedger()
    prov = ProvenanceLedger()
    # A dispatch that references a request never registered in the explorer's registry.
    disp.record(
        DispatchRecord.create(
            request_ref="UCOS-GREQ-orphan",
            blueprint_ref="UCOS-BLPR-1",
            family=make_request(GenerationRequestRegistry()).family,
            content_hash="c0ffee",
            tick=5,
        )
    )
    health = ExplorerHealth(reg, disp, prov)
    assert health.orphaned_dispatches() == ("UCOS-GREQ-orphan",)
    assert health.healthy is False
    assert health.probe()[DISPATCH_CHECK] is HealthStatus.UNHEALTHY


def test_health_unhealthy_on_orphaned_provenance():
    reg = GenerationRequestRegistry()
    disp = DispatchLedger()
    prov = ProvenanceLedger()
    prov.record(
        RequestProvenance.create(
            request_ref="UCOS-GREQ-orphan",
            blueprint_ref="UCOS-BLPR-1",
            family=make_request(GenerationRequestRegistry()).family,
            generation_reference="GEN-DATA-001",
            generation_artifact_id="BP-DATA-0001",
            blueprint_provenance_ref="UCOS-BPRV-xyz",
            implementation_target="platform/generation",
            content_hash="c0ffee",
            dependency_chain=("EPIC-006",),
        )
    )
    health = ExplorerHealth(reg, disp, prov)
    assert health.orphaned_provenance() == ("UCOS-GREQ-orphan",)
    assert health.probe()[PROVENANCE_CHECK] is HealthStatus.UNHEALTHY


def test_evidence_is_deterministic():
    a = ExplorerEvidence.create(
        registry_fingerprint="r",
        dispatch_fingerprint="d",
        provenance_fingerprint="p",
        artifact_count=1,
        dispatched_count=1,
        provenance_count=1,
        traceable_count=1,
        lookup_count=2,
        search_count=3,
        lineage_count=4,
        provenance_navigation_count=5,
        trace_count=6,
        access_evaluation_count=7,
        health_status="healthy",
    )
    b = ExplorerEvidence.create(
        registry_fingerprint="r",
        dispatch_fingerprint="d",
        provenance_fingerprint="p",
        artifact_count=1,
        dispatched_count=1,
        provenance_count=1,
        traceable_count=1,
        lookup_count=2,
        search_count=3,
        lineage_count=4,
        provenance_navigation_count=5,
        trace_count=6,
        access_evaluation_count=7,
        health_status="healthy",
    )
    assert a.evidence_id == b.evidence_id
    assert a.evidence_id.startswith("UCOS-AXEV-")
    assert a.to_dict()["health_status"] == "healthy"
    assert a.fingerprint() == b.fingerprint()
