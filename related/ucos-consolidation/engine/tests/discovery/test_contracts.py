"""Tests for engine.discovery.contracts (EPIC-003)."""

from __future__ import annotations

import pytest

from engine.discovery.contracts import (
    DISCOVERY_CONTRACT,
    DISCOVERY_DIMENSIONS,
    CoverageReport,
    DimensionCoverage,
    DimensionResult,
    DiscoveredItem,
    DiscoveryKind,
    DiscoveryReport,
    build_coverage_report,
    canonical_json,
    content_hash,
)
from engine.discovery.errors import DiscoveryDimensionError


def test_canonical_json_is_sorted_and_compact():
    assert canonical_json({"b": 1, "a": 2}) == '{"a":2,"b":1}'


def test_content_hash_is_stable_and_order_independent():
    assert content_hash({"a": 1, "b": 2}) == content_hash({"b": 2, "a": 1})
    assert len(content_hash({"x": 1})) == 64


def test_discovery_dimensions_count_and_order():
    assert len(DISCOVERY_DIMENSIONS) == 8
    assert DISCOVERY_DIMENSIONS[0] is DiscoveryKind.NAMESPACE
    assert DISCOVERY_DIMENSIONS[-1] is DiscoveryKind.CAPABILITY


def test_discovery_kind_coerce():
    assert DiscoveryKind.coerce("namespace") is DiscoveryKind.NAMESPACE
    assert DiscoveryKind.coerce(DiscoveryKind.DOCUMENT) is DiscoveryKind.DOCUMENT
    with pytest.raises(DiscoveryDimensionError):
        DiscoveryKind.coerce("not-a-dimension")


def test_discovered_item_to_dict():
    item = DiscoveredItem(
        kind=DiscoveryKind.DOCUMENT,
        item_id="UDDOC-X",
        name="X",
        source="artifacts.json",
        attributes={"a": 1},
        references=("Y",),
    )
    assert item.to_dict() == {
        "kind": "document",
        "item_id": "UDDOC-X",
        "name": "X",
        "source": "artifacts.json",
        "attributes": {"a": 1},
        "references": ["Y"],
    }


def test_dimension_coverage_percent_and_complete():
    full = DimensionCoverage(DiscoveryKind.DOCUMENT, discovered=3, total=3)
    assert full.complete and full.percent == 100.0
    empty = DimensionCoverage(DiscoveryKind.DOCUMENT, discovered=0, total=0)
    assert empty.complete and empty.percent == 100.0
    partial = DimensionCoverage(DiscoveryKind.DEPENDENCY, discovered=1, total=4)
    assert not partial.complete and partial.percent == 25.0


def _result(kind, items=(), discovered=0, total=0, gaps=()):
    return DimensionResult(
        kind=kind,
        items=tuple(items),
        coverage=DimensionCoverage(kind, discovered=discovered, total=total),
        gaps=tuple(gaps),
    )


def test_dimension_result_helpers():
    item = DiscoveredItem(DiscoveryKind.DOCUMENT, "UDDOC-X", "X", "artifacts.json")
    result = _result(DiscoveryKind.DOCUMENT, items=[item], discovered=1, total=1)
    assert result.count() == 1
    assert result.item_ids() == ("UDDOC-X",)
    assert result.complete
    assert result.to_dict()["dimension"] == "document"


def test_coverage_report_aggregation():
    results = [
        _result(DiscoveryKind.DOCUMENT, discovered=3, total=3),
        _result(DiscoveryKind.DEPENDENCY, discovered=1, total=2),
    ]
    report = build_coverage_report(results)
    assert isinstance(report, CoverageReport)
    assert not report.complete
    assert report.incomplete_dimensions() == ("dependency",)
    assert report.total_discovered == 4
    assert report.total_scope == 5
    assert report.percent == 80.0
    assert set(report.by_dimension()) == {"document", "dependency"}


def test_coverage_report_empty_is_complete():
    report = build_coverage_report([])
    assert report.complete
    assert report.percent == 100.0


def _report():
    results = (
        _result(DiscoveryKind.DOCUMENT, discovered=3, total=3),
        _result(DiscoveryKind.DEPENDENCY, discovered=1, total=2, gaps=("UCOS-GHOST",)),
    )
    return DiscoveryReport(engine_id="E", substrate={"artifacts": 3}, results=results)


def test_discovery_report_views():
    report = _report()
    assert report.counts() == {"document": 0, "dependency": 0}
    assert report.total_items() == 0
    assert not report.complete
    assert report.result("document").kind is DiscoveryKind.DOCUMENT
    assert set(report.by_dimension()) == {"document", "dependency"}
    assert report.coverage().incomplete_dimensions() == ("dependency",)


def test_discovery_report_result_missing_raises():
    report = _report()
    with pytest.raises(DiscoveryDimensionError):
        report.result(DiscoveryKind.NAMESPACE)


def test_discovery_report_content_hash_deterministic():
    assert _report().content_sha256() == _report().content_sha256()
    assert _report().to_dict()["content_sha256"] == _report().content_sha256()


def test_discovery_contract_identity():
    assert DISCOVERY_CONTRACT.name == "discovery.universal"
    assert str(DISCOVERY_CONTRACT.version) == "1.0.0"
