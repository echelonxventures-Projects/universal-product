"""Tests for engine.discovery.evidence — coverage report + evidence bundle."""

from __future__ import annotations

import json

from engine.discovery.evidence import (
    DISCOVERY_COVERAGE_FORMAT,
    DISCOVERY_EVIDENCE_FORMAT,
    build_coverage_document,
    build_discovery_evidence,
    emit_evidence,
)


def test_build_discovery_evidence_clean(clean_engine):
    report = clean_engine.discover()
    evidence = build_discovery_evidence(report)
    assert evidence.engine_id == report.engine_id
    assert evidence.complete is True
    assert evidence.coverage_percent == 100.0
    assert evidence.gaps == {}
    assert evidence.report_sha256 == report.content_sha256()
    assert len(evidence.record_sha256) == 64
    doc = evidence.to_dict()
    assert doc["evidence_format"] == DISCOVERY_EVIDENCE_FORMAT


def test_build_discovery_evidence_records_gaps(gapped_engine):
    report = gapped_engine.discover()
    evidence = build_discovery_evidence(report)
    assert evidence.complete is False
    assert set(evidence.gaps) == {
        "namespace",
        "component",
        "dependency",
        "evidence",
        "capability",
    }
    assert evidence.gaps["dependency"] == ["UCOS-GHOST"]


def test_coverage_document_shape(clean_engine):
    report = clean_engine.discover()
    doc = build_coverage_document(report)
    assert doc["schema"] == DISCOVERY_COVERAGE_FORMAT
    assert doc["coverage"]["complete"] is True
    assert doc["report_sha256"] == report.content_sha256()
    assert doc["substrate"] == {"artifacts": 3, "relationships": 3, "volumes": 2}


def test_emit_evidence_writes_bundle(clean_engine, tmp_path):
    report = clean_engine.discover()
    out = tmp_path / "evidence"
    written = emit_evidence(report, out)
    # coverage report + evidence record + one file per dimension (8)
    assert "discovery-coverage-report.json" in written
    assert "discovery-evidence-record.json" in written
    assert "discovery-namespace.json" in written
    assert len(written) == 2 + 8
    for path in written.values():
        assert (out / path.split("/")[-1]).is_file()


def test_emit_evidence_is_deterministic(clean_engine, tmp_path):
    report = clean_engine.discover()
    first = tmp_path / "a"
    second = tmp_path / "b"
    emit_evidence(report, first)
    emit_evidence(report, second)
    for name in ("discovery-coverage-report.json", "discovery-evidence-record.json"):
        assert (first / name).read_text() == (second / name).read_text()


def test_emitted_files_are_sorted_json(clean_engine, tmp_path):
    report = clean_engine.discover()
    out = tmp_path / "evidence"
    emit_evidence(report, out)
    content = (out / "discovery-coverage-report.json").read_text()
    # sorted keys => a re-dump with sort_keys is identical (modulo trailing newline)
    parsed = json.loads(content)
    assert content.rstrip("\n") == json.dumps(parsed, sort_keys=True, indent=2, ensure_ascii=False)
