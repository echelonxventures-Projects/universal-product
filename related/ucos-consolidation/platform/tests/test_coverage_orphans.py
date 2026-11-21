"""ZG-P-02 — orphan analysis tests (no orphan code, no orphan universe on real repo)."""

from __future__ import annotations

from platform.coverage.bootstrap import bootstrap_coverage
from platform.coverage.engine import CoverageEngine
from platform.tests._coverage_helpers import (
    complete_source,
    orphan_code_source,
    orphan_universe_source,
)


def test_complete_graph_has_no_orphans():
    g = CoverageEngine(complete_source()).compute()
    assert g.orphans() == ()
    assert g.orphan_code() == ()
    assert g.orphan_universes() == ()


def test_orphan_universe_isolated():
    g = CoverageEngine(orphan_universe_source()).compute()
    assert len(g.orphan_universes()) == 1
    assert g.orphan_code() == ()


def test_orphan_code_isolated():
    g = CoverageEngine(orphan_code_source()).compute()
    assert g.orphan_universes() == ()
    assert len(g.orphan_code()) >= 1


def test_real_repository_has_no_orphans_and_no_duplicates():
    """Success criteria: no orphan code, no orphan universes, no duplicate records."""
    svc = bootstrap_coverage()
    graph = svc.compute()
    assert graph.orphan_code() == ()
    assert graph.orphan_universes() == ()
    assert svc.registry.duplicate_edge_refs() == ()
    v = svc.verify()
    assert v.orphan_code_count == 0
    assert v.orphan_universe_count == 0
    assert v.duplicate_count == 0
    assert v.ok
