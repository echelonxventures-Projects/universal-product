"""ZG-P-02 — coverage graph model tests (status, gaps, orphans, fail-closed)."""

from __future__ import annotations

from platform.coverage.contracts import CoverageNode, CoverageNodeKind, CoverageStatus
from platform.coverage.errors import CoverageGraphError
from platform.coverage.evidence import EvidenceBundle, InMemoryEvidenceSource
from platform.coverage.graph import CoverageGraph
from platform.tests._coverage_helpers import (
    K,
    complete_source,
    edge,
    gapped_source,
    node,
    orphan_code_source,
    orphan_universe_source,
    partial_source,
)

import pytest


def _graph(source) -> CoverageGraph:
    return CoverageGraph(source.collect())


def test_complete_graph_all_covered():
    g = _graph(complete_source())
    assert g.coverage_percentage(K.UNIVERSE) == 100.0
    assert not g.gaps()
    assert not g.orphans()
    for n in g.nodes():
        assert g.status_of(n.node_id) is CoverageStatus.COVERED
    assert len(g.covered()) == len(g)


def test_gapped_graph_reports_uncovered_universe():
    g = _graph(gapped_source())
    uncovered_universes = [
        n.ref
        for n in g.nodes_of_kind(K.UNIVERSE)
        if g.status_of(n.node_id) is CoverageStatus.UNCOVERED
    ]
    assert "UNI-099" in uncovered_universes
    assert g.coverage_percentage(K.UNIVERSE) < 100.0
    assert any(n.ref == "UNI-099" for n in g.gaps())
    assert not g.orphans()


def test_partial_status_propagates():
    g = _graph(partial_source())
    epic = next(n for n in g.nodes_of_kind(K.EPIC))
    assert g.status_of(epic.node_id) is CoverageStatus.PARTIAL
    # universes above a partial epic are partial (a gap), never falsely covered.
    assert any(n.kind is K.UNIVERSE for n in g.gaps())


def test_orphan_universe_detected():
    g = _graph(orphan_universe_source())
    assert len(g.orphan_universes()) == 1
    assert g.orphans()[0].kind is K.UNIVERSE
    assert g.coverage_percentage(K.UNIVERSE) == 0.0


def test_orphan_code_detected():
    g = _graph(orphan_code_source())
    orphan_kinds = {n.kind for n in g.orphan_code()}
    assert K.EPIC in orphan_kinds
    assert K.MODULE in orphan_kinds
    assert K.RUNTIME_ASSET in orphan_kinds


def test_dangling_source_fails_closed():
    # An edge whose SOURCE node is not declared.
    bundle = EvidenceBundle.create(
        [node(K.PHASE, "IMP-1")],
        [edge(K.UNIVERSE, "UNI-404", K.PHASE, "IMP-1")],
    )
    with pytest.raises(CoverageGraphError):
        CoverageGraph(bundle)


def test_dangling_target_fails_closed():
    bundle = EvidenceBundle.create(
        [node(K.UNIVERSE, "UNI-1")],
        [edge(K.UNIVERSE, "UNI-1", K.PHASE, "IMP-404")],
    )
    with pytest.raises(CoverageGraphError):
        CoverageGraph(bundle)


def test_graph_requires_bundle():
    with pytest.raises(CoverageGraphError):
        CoverageGraph(object())  # type: ignore[arg-type]


def test_accessors_and_unknown_node():
    g = _graph(complete_source())
    nid = g.node_ids[0]
    assert nid in g
    assert isinstance(g.get(nid), CoverageNode)
    assert g.status_of(nid) in set(CoverageStatus)
    # children/parents accessors return sorted tuples.
    uni = next(n for n in g.nodes_of_kind(K.UNIVERSE))
    assert g.children_of(uni.node_id)
    assert g.parents_of(uni.node_id) == ()
    with pytest.raises(CoverageGraphError):
        g.get("UCOS-COVN-does-not-exist")
    with pytest.raises(CoverageGraphError):
        g.status_of("UCOS-COVN-does-not-exist")
    assert g.children_of("missing") == ()
    assert g.parents_of("missing") == ()


def test_percentage_zero_when_kind_absent():
    # A graph with only universes → runtime kind population empty → 0.0.
    g = CoverageGraph(InMemoryEvidenceSource([node(K.UNIVERSE, "UNI-1")], []).collect())
    assert g.coverage_percentage(CoverageNodeKind.RUNTIME_ASSET) == 0.0


def test_to_dict_and_fingerprint_stable():
    g1 = _graph(complete_source())
    g2 = _graph(complete_source())
    assert g1.fingerprint() == g2.fingerprint()
    d = g1.to_dict()
    assert d["node_count"] == len(g1)
    assert all("status" in n for n in d["nodes"])
