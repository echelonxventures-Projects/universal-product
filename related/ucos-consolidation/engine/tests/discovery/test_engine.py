"""Tests for engine.discovery.engine — the UniversalDiscoveryEngine facade."""

from __future__ import annotations

import pytest

from engine.discovery.contracts import DISCOVERY_CONTRACT, DiscoveryKind
from engine.discovery.engine import DISCOVERY_ENGINE_ID, UniversalDiscoveryEngine
from engine.discovery.errors import DiscoveryDimensionError
from engine.foundation.contracts.contract import ContractRegistry


def test_discover_all_dimensions_clean(clean_engine):
    report = clean_engine.discover()
    assert report.engine_id == DISCOVERY_ENGINE_ID
    assert len(report.results) == 8
    # dimensions emitted in canonical order regardless of internal iteration
    assert tuple(r.kind for r in report.results) == tuple(DiscoveryKind)
    assert report.complete
    assert report.substrate == {"artifacts": 3, "relationships": 3, "volumes": 2}


def test_discover_is_deterministic(clean_engine, clean_data_dir):
    first = clean_engine.discover()
    second = UniversalDiscoveryEngine.open(clean_data_dir).discover()
    assert first.content_sha256() == second.content_sha256()
    assert first.to_dict() == second.to_dict()


def test_discover_gapped_is_incomplete(gapped_engine):
    report = gapped_engine.discover()
    assert not report.complete
    incomplete = set(report.coverage().incomplete_dimensions())
    assert incomplete == {"namespace", "component", "dependency", "evidence", "capability"}
    # complete dimensions remain complete
    assert report.result("document").complete
    assert report.result("registry").complete
    assert report.result("ontology").complete


def test_discover_subset(clean_engine):
    report = clean_engine.discover(dimensions=["dependency", "namespace"])
    # subset honoured, but still in canonical order (namespace before dependency)
    assert tuple(r.kind for r in report.results) == (
        DiscoveryKind.NAMESPACE,
        DiscoveryKind.DEPENDENCY,
    )


def test_discover_subset_deduplicates(clean_engine):
    report = clean_engine.discover(dimensions=["document", "document"])
    assert len(report.results) == 1
    assert report.results[0].kind is DiscoveryKind.DOCUMENT


def test_discover_dimension_dispatch(clean_engine):
    for kind in DiscoveryKind:
        result = clean_engine.discover_dimension(kind)
        assert result.kind is kind


def test_discover_dimension_unknown_raises(clean_engine):
    with pytest.raises(DiscoveryDimensionError):
        clean_engine.discover_dimension("bogus")


def test_per_dimension_methods(clean_engine):
    assert clean_engine.namespaces().kind is DiscoveryKind.NAMESPACE
    assert clean_engine.documents().kind is DiscoveryKind.DOCUMENT
    assert clean_engine.registries().kind is DiscoveryKind.REGISTRY
    assert clean_engine.components().kind is DiscoveryKind.COMPONENT
    assert clean_engine.dependencies().kind is DiscoveryKind.DEPENDENCY
    assert clean_engine.evidence().kind is DiscoveryKind.EVIDENCE
    assert clean_engine.ontology().kind is DiscoveryKind.ONTOLOGY
    assert clean_engine.capabilities().kind is DiscoveryKind.CAPABILITY


def test_contract_registration(clean_engine):
    registry = ContractRegistry()
    clean_engine.register_contract(registry)
    assert registry.get("discovery.universal") is DISCOVERY_CONTRACT
    assert clean_engine.contract is DISCOVERY_CONTRACT


def test_registry_property(clean_engine):
    assert clean_engine.registry.summary() == {
        "artifacts": 3,
        "relationships": 3,
        "volumes": 2,
    }
