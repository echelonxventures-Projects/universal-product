"""UCOS-EPIC-004 — Truth source tests (UCOS-UMA-001)."""

from __future__ import annotations

from platform.measurement.errors import TruthSourceError
from platform.measurement.source import (
    InMemoryTruthSource,
    RegistryTruthSource,
    TruthSnapshot,
)
from platform.tests._measurement_helpers import artifact, complete_snapshot, relationship, volume

import pytest


def test_snapshot_is_ordered_and_deterministic():
    snap = complete_snapshot()
    assert [a.universal_id for a in snap.artifacts] == ["UCOS-A001", "UCOS-A002"]
    assert snap.artifact_count == 2
    assert snap.relationship_count == 1
    assert snap.volume_count == 1
    assert snap.artifact_ids() == frozenset({"UCOS-A001", "UCOS-A002"})
    assert snap.volume_ids() == frozenset({"V-001"})
    assert snap.fingerprint() == complete_snapshot().fingerprint()


def test_snapshot_type_checks_fail_closed():
    with pytest.raises(TruthSourceError):
        TruthSnapshot.create([object()], [], [])  # type: ignore[list-item]
    with pytest.raises(TruthSourceError):
        TruthSnapshot.create([], [object()], [])  # type: ignore[list-item]
    with pytest.raises(TruthSourceError):
        TruthSnapshot.create([], [], [object()])  # type: ignore[list-item]


def test_snapshot_ordering_normalizes_unsorted_input():
    a2 = artifact("UCOS-A002")
    a1 = artifact("UCOS-A001")
    snap = TruthSnapshot.create(
        [a2, a1],
        [relationship("E", "UCOS-A001", "UCOS-A002")],
        [volume("V-001", artifact_count=2)],
    )
    assert [a.universal_id for a in snap.artifacts] == ["UCOS-A001", "UCOS-A002"]


def test_in_memory_source_returns_stable_snapshot():
    snap = complete_snapshot()
    src = InMemoryTruthSource(snap.artifacts, snap.relationships, snap.volumes)
    assert src.snapshot().fingerprint() == src.snapshot().fingerprint()


def test_snapshot_exposes_no_mutation_surface():
    """Measurement consumes Truth: the snapshot offers only read views."""
    snap = complete_snapshot()
    assert not hasattr(snap, "add_artifact")
    assert not hasattr(snap, "record")
    with pytest.raises((AttributeError, TypeError)):
        snap.artifacts = ()  # frozen dataclass: assignment is refused  # type: ignore[misc]


def test_registry_truth_source_requires_adapter():
    with pytest.raises(TruthSourceError):
        RegistryTruthSource(object())  # type: ignore[arg-type]


def test_registry_truth_source_projects_live_registry():
    """RegistryTruthSource reads the certified corpus read-only and exposes its adapter."""
    from engine.registry.adapter import RegistryAdapter

    adapter = RegistryAdapter.open()
    src = RegistryTruthSource(adapter)
    assert src.adapter is adapter
    snap = src.snapshot()
    assert snap.artifact_count > 0
    # a pure projection: re-reading yields the same fingerprint.
    assert snap.fingerprint() == src.snapshot().fingerprint()
