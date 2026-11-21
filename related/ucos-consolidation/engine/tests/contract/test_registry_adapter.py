"""Tests for TASK-000015 unified Registry Adapter facade (EPIC-002).

Exercises the Foundation-contract-compliant read-only facade, including lazy
loading, contract publication (AR-03/PL-05), and telemetry (PL-02).
"""

from __future__ import annotations

import pytest

from engine.foundation.contracts.contract import ContractRegistry, Version
from engine.foundation.obs.telemetry import metrics_snapshot, reset_metrics
from engine.registry.adapter import REGISTRY_READ_CONTRACT, RegistryAdapter
from engine.registry.errors import ArtifactNotFoundError, VolumeNotFoundError


@pytest.fixture
def adapter(data_dir) -> RegistryAdapter:
    return RegistryAdapter.open(data_dir)


def test_open_and_source(adapter, data_dir):
    assert adapter.source.data_dir == data_dir.resolve()


def test_contract_identity():
    assert REGISTRY_READ_CONTRACT.name == "registry.read"
    assert REGISTRY_READ_CONTRACT.version == Version(1, 0, 0)


def test_register_contract_into_foundation_registry(adapter):
    registry = ContractRegistry()
    adapter.register_contract(registry)
    served = registry.check_compatibility("registry.read", "1.0.0")
    assert served is REGISTRY_READ_CONTRACT
    assert adapter.contract is REGISTRY_READ_CONTRACT


def test_lazy_load_is_memoised(adapter):
    first = adapter.artifacts
    assert adapter.artifacts is first
    g1 = adapter.graph
    assert adapter.graph is g1
    v1 = adapter.volumes
    assert adapter.volumes is v1


def test_summary_and_load_all(adapter):
    adapter.load_all()
    assert adapter.summary() == {"artifacts": 3, "relationships": 4, "volumes": 2}


def test_convenience_lookups(adapter):
    assert adapter.artifact("UCOS-REG-000001").name == "Alpha"
    assert adapter.volume("VOL-000").serial == 0
    assert len(adapter.artifacts_in_volume("VOL-000")) == 2


def test_artifacts_in_volume_unknown_volume(adapter):
    with pytest.raises(VolumeNotFoundError):
        adapter.artifacts_in_volume("VOL-999")


def test_missing_artifact(adapter):
    with pytest.raises(ArtifactNotFoundError):
        adapter.artifact("UCOS-XXX-999999")


def test_integrity_report(adapter):
    report = adapter.integrity()
    assert report.is_consistent


def test_loading_emits_telemetry(adapter):
    reset_metrics()
    adapter.load_all()
    snapshot = metrics_snapshot()
    # PL-02: each load runs inside a Foundation `trace` span, which records a
    # span.count counter and a span.duration_ms histogram. (metrics_snapshot
    # collapses series by metric name, so we assert presence, not per-span keys.)
    assert "span.count" in snapshot["counters"]
    assert "span.duration_ms" in snapshot["histograms"]
    reset_metrics()


def test_default_open_uses_real_corpus(real_data_dir):
    # Constructing without an explicit source targets the real read-only corpus.
    adapter = RegistryAdapter()
    assert adapter.source.is_within_frozen_corpus() is True
    assert adapter.summary()["artifacts"] > 0
