"""ZG-P-02 — coverage reconciliation tests (registry vs fresh recompute)."""

from __future__ import annotations

from platform.coverage.engine import CoverageEngine
from platform.tests._coverage_helpers import complete_source, gapped_source


def test_reconciled_when_registry_matches_recompute():
    eng = CoverageEngine(complete_source())
    eng.compute()
    r = eng.reconcile()
    assert r.reconciled
    assert r.added_nodes == ()
    assert r.removed_nodes == ()
    assert r.added_edges == ()
    assert r.removed_edges == ()
    assert r.recorded_fingerprint == r.recomputed_fingerprint


def test_divergence_reported_as_additions_when_registry_empty():
    eng = CoverageEngine(gapped_source())
    r = eng.reconcile()
    assert not r.reconciled
    assert len(r.added_nodes) > 0
    assert len(r.added_edges) > 0
    assert r.removed_nodes == ()
    assert r.removed_edges == ()


def test_reconciliation_is_deterministic():
    eng = CoverageEngine(complete_source())
    eng.compute()
    a = eng.reconcile()
    b = eng.reconcile()
    assert a.reconciliation_id == b.reconciliation_id
