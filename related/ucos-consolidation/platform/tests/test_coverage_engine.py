"""ZG-P-02 — coverage engine tests (compute/verify/reconcile/fingerprint/report)."""

from __future__ import annotations

import itertools
from platform.coverage.engine import (
    CoverageEngine,
    CoverageReconciliation,
    CoverageVerification,
)
from platform.coverage.errors import CoverageEngineError
from platform.coverage.evidence import EvidenceBundle, EvidenceSource
from platform.coverage.graph import CoverageGraph
from platform.coverage.registry import CoverageRegistry
from platform.tests._coverage_helpers import (
    K,
    complete_source,
    duplicate_source,
    edge,
    node,
    orphan_code_source,
    orphan_universe_source,
)

import pytest


class _NonDeterministicSource(EvidenceSource):
    """Returns a different bundle on each collect() — to exercise fail-closed paths."""

    def __init__(self):
        self._counter = itertools.count()

    def collect(self) -> EvidenceBundle:
        i = next(self._counter)
        return EvidenceBundle.create(
            [node(K.UNIVERSE, f"UNI-{i}"), node(K.PHASE, "IMP-1")],
            [edge(K.UNIVERSE, f"UNI-{i}", K.PHASE, "IMP-1")],
        )


def test_engine_requires_source_and_valid_registry():
    with pytest.raises(CoverageEngineError):
        CoverageEngine(object())  # type: ignore[arg-type]
    with pytest.raises(CoverageEngineError):
        CoverageEngine(complete_source(), registry=object())  # type: ignore[arg-type]


def test_compute_builds_graph_and_records():
    eng = CoverageEngine(complete_source())
    g = eng.compute()
    assert isinstance(g, CoverageGraph)
    assert eng.registry.node_count == len(g)
    assert eng.registry.edge_count == len(g.edges())


def test_fingerprint_matches_graph():
    eng = CoverageEngine(complete_source())
    assert eng.fingerprint() == CoverageGraph(complete_source().collect()).fingerprint()


def test_verify_clean_graph_ok():
    eng = CoverageEngine(complete_source())
    eng.compute()
    v = eng.verify()
    assert isinstance(v, CoverageVerification)
    assert v.ok
    assert v.violations == ()
    assert v.to_dict()["ok"] is True


def test_verify_flags_orphan_universe():
    eng = CoverageEngine(orphan_universe_source())
    eng.compute()
    v = eng.verify()
    assert not v.ok
    assert v.orphan_universe_count == 1
    assert any(s.startswith("orphan-universe") for s in v.violations)


def test_verify_flags_orphan_code():
    eng = CoverageEngine(orphan_code_source())
    eng.compute()
    v = eng.verify()
    assert not v.ok
    assert v.orphan_code_count >= 1
    assert any(s.startswith("orphan-code") for s in v.violations)


def test_verify_flags_duplicate_coverage():
    eng = CoverageEngine(duplicate_source())
    eng.compute()
    v = eng.verify()
    assert v.duplicate_count >= 1
    assert any(s.startswith("duplicate-coverage") for s in v.violations)


def test_verify_flags_nondeterminism():
    eng = CoverageEngine(_NonDeterministicSource())
    v = eng.verify()
    assert "coverage-fingerprint-nondeterministic" in v.violations


def test_reconcile_matches_after_compute():
    eng = CoverageEngine(complete_source())
    eng.compute()
    r = eng.reconcile()
    assert isinstance(r, CoverageReconciliation)
    assert r.reconciled
    assert r.to_dict()["reconciled"] is True


def test_reconcile_detects_divergence_before_compute():
    eng = CoverageEngine(complete_source())
    # registry empty; recompute non-empty ⇒ additions ⇒ not reconciled.
    r = eng.reconcile()
    assert not r.reconciled
    assert r.added_nodes
    assert r.added_edges
    assert r.recorded_fingerprint != r.recomputed_fingerprint


def test_report_shape():
    eng = CoverageEngine(complete_source())
    rep = eng.report()
    assert rep["universe_coverage_percentage"] == 100.0
    assert set(rep["by_kind"]) == {k.value for k in K}
    assert rep["gaps"] == []
    assert rep["orphans"] == []
    assert rep["node_count"] > 0


def test_verification_and_reconciliation_ids_are_content_addressed():
    v = CoverageVerification.create(
        fingerprint="fp",
        violations=(),
        orphan_code_count=0,
        orphan_universe_count=0,
        duplicate_count=0,
    )
    assert v.verification_id.startswith("UCOS-COVV-")
    r = CoverageReconciliation.create(
        added_nodes=(),
        removed_nodes=("x",),
        added_edges=(),
        removed_edges=(),
        recorded_fingerprint="a",
        recomputed_fingerprint="b",
    )
    assert r.reconciliation_id.startswith("UCOS-COVR-")
    assert not r.reconciled


def test_engine_accepts_supplied_registry():
    reg = CoverageRegistry()
    eng = CoverageEngine(complete_source(), registry=reg)
    eng.compute()
    assert reg.node_count > 0
