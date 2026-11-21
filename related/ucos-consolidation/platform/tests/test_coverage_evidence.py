"""ZG-P-02 — evidence bundle + source tests."""

from __future__ import annotations

from platform.coverage.errors import CoverageEvidenceError
from platform.coverage.evidence import (
    EvidenceBundle,
    EvidenceSource,
    InMemoryEvidenceSource,
)
from platform.tests._coverage_helpers import K, complete_source, edge, node

import pytest


def test_bundle_dedupes_and_orders():
    n1 = node(K.UNIVERSE, "UNI-001")
    n1b = node(K.UNIVERSE, "UNI-001")  # identical → dedup
    e1 = edge(K.UNIVERSE, "UNI-001", K.PHASE, "IMP-1")
    e1b = edge(K.UNIVERSE, "UNI-001", K.PHASE, "IMP-1")  # identical → dedup
    bundle = EvidenceBundle.create([n1, n1b, node(K.PHASE, "IMP-1")], [e1, e1b])
    assert len(bundle.nodes) == 2
    assert len(bundle.edges) == 1
    # deterministic ordering by id.
    assert list(bundle.nodes) == sorted(bundle.nodes, key=lambda n: n.node_id)


def test_bundle_conflicting_node_fails_closed():
    a = node(K.UNIVERSE, "UNI-001", authority="one")
    b = node(K.UNIVERSE, "UNI-001", authority="two")  # same id, different fingerprint
    with pytest.raises(CoverageEvidenceError):
        EvidenceBundle.create([a, b], [])


def test_bundle_rejects_non_node_and_non_edge():
    with pytest.raises(CoverageEvidenceError):
        EvidenceBundle.create([object()], [])  # type: ignore[list-item]
    with pytest.raises(CoverageEvidenceError):
        EvidenceBundle.create([], [object()])  # type: ignore[list-item]


def test_bundle_fingerprint_and_to_dict():
    b1 = complete_source().collect()
    b2 = complete_source().collect()
    assert b1.fingerprint() == b2.fingerprint()
    d = b1.to_dict()
    assert d["node_count"] == len(b1.nodes)
    assert d["edge_count"] == len(b1.edges)


def test_inmemory_source_is_stable():
    src = complete_source()
    assert src.collect().fingerprint() == src.collect().fingerprint()


def test_evidence_source_is_abstract():
    with pytest.raises(TypeError):
        EvidenceSource()  # type: ignore[abstract]


def test_inmemory_source_type():
    assert isinstance(complete_source(), InMemoryEvidenceSource)
