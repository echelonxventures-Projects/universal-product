"""ZG-P-02 — append-only content-addressed coverage registry tests."""

from __future__ import annotations

from platform.coverage.errors import CoverageRegistryError
from platform.coverage.graph import CoverageGraph
from platform.coverage.registry import CoverageRegistry
from platform.tests._coverage_helpers import (
    K,
    complete_source,
    duplicate_source,
    edge,
    node,
)

import pytest


def test_ingest_records_all_and_is_idempotent():
    reg = CoverageRegistry()
    bundle = complete_source().collect()
    reg.ingest(bundle)
    n0, e0 = reg.node_count, reg.edge_count
    reg.ingest(bundle)  # idempotent
    assert (reg.node_count, reg.edge_count) == (n0, e0)
    assert len(reg) == n0 + e0


def test_record_node_conflict_fails_closed():
    reg = CoverageRegistry()
    reg.record_node(node(K.UNIVERSE, "UNI-1", authority="a"))
    # same id, different content.
    with pytest.raises(CoverageRegistryError):
        reg.record_node(node(K.UNIVERSE, "UNI-1", authority="b"))


def test_record_edge_conflict_is_impossible_by_content_addressing():
    reg = CoverageRegistry()
    e = edge(K.UNIVERSE, "UNI-1", K.PHASE, "IMP-1", authority="a")
    reg.record_edge(e)
    reg.record_edge(e)  # idempotent
    assert reg.edge_count == 1


def test_record_type_errors():
    reg = CoverageRegistry()
    with pytest.raises(CoverageRegistryError):
        reg.record_node(object())  # type: ignore[arg-type]
    with pytest.raises(CoverageRegistryError):
        reg.record_edge(object())  # type: ignore[arg-type]
    with pytest.raises(CoverageRegistryError):
        reg.ingest(object())  # type: ignore[arg-type]


def test_duplicate_edge_refs_surface_multi_authority():
    reg = CoverageRegistry()
    reg.ingest(duplicate_source().collect())
    dupes = reg.duplicate_edge_refs()
    assert any("IMP-005" in d and "IDENTITY" in d for d in dupes)


def test_no_duplicates_on_clean_graph():
    reg = CoverageRegistry()
    reg.ingest(complete_source().collect())
    assert reg.duplicate_edge_refs() == ()


def test_accessors_bundle_and_graph_roundtrip():
    reg = CoverageRegistry()
    src_bundle = complete_source().collect()
    reg.ingest(src_bundle)
    assert reg.has_node(reg.nodes()[0].node_id)
    assert reg.has_edge(reg.edges()[0].edge_id)
    assert reg.fingerprint()
    rebuilt = reg.as_bundle()
    assert rebuilt.fingerprint() == src_bundle.fingerprint()
    g = reg.graph()
    assert isinstance(g, CoverageGraph)
    assert g.fingerprint() == CoverageGraph(src_bundle).fingerprint()
    assert reg.to_dict()["node_count"] == reg.node_count
