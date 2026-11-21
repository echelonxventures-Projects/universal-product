"""Integration tests: universal discovery over the real, read-only 00-BOOK corpus.

These exercise the engine end to end against the certified substrate (read-only,
DP-03). They skip automatically when the corpus is not present. They assert
structure and determinism — never exact counts — so they remain valid as the
corpus grows.
"""

from __future__ import annotations

from engine.discovery.contracts import DiscoveryKind
from engine.discovery.engine import UniversalDiscoveryEngine
from engine.discovery.evidence import build_discovery_evidence


def test_real_corpus_discovers_all_dimensions(real_data_dir):
    report = UniversalDiscoveryEngine.open(real_data_dir).discover()
    assert len(report.results) == 8
    assert tuple(r.kind for r in report.results) == tuple(DiscoveryKind)
    # every dimension surfaced at least one grounded item
    assert all(r.count() > 0 for r in report.results)
    # documents/components are one-per-artifact; the corpus is non-trivial
    assert report.result("document").count() > 100


def test_real_corpus_discovery_is_deterministic(real_data_dir):
    first = UniversalDiscoveryEngine.open(real_data_dir).discover()
    second = UniversalDiscoveryEngine.open(real_data_dir).discover()
    assert first.content_sha256() == second.content_sha256()


def test_real_corpus_evidence_record(real_data_dir):
    report = UniversalDiscoveryEngine.open(real_data_dir).discover()
    evidence = build_discovery_evidence(report)
    assert evidence.report_sha256 == report.content_sha256()
    assert evidence.substrate["artifacts"] > 0
    # coverage is a real completeness measure over the corpus (0..100)
    assert 0.0 <= evidence.coverage_percent <= 100.0
