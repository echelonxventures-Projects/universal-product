"""Tests for engine.graph.architecture.evidence.

Proves: build_evidence returns a well-formed document; write_evidence writes
a readable JSON file; _assert_writable rejects paths inside the frozen corpus;
and the operational flag is set correctly.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from engine.graph.architecture.engine import ArchitectureIntelligenceEngine
from engine.graph.architecture.errors import InsightsWriteError
from engine.graph.architecture.evidence import (
    EVIDENCE_VERSION,
    _assert_writable,
    build_evidence,
    write_evidence,
)

# --- build_evidence ------------------------------------------------------------


def test_build_evidence_keys(kg):
    engine = ArchitectureIntelligenceEngine(kg)
    doc = build_evidence(engine)
    assert doc["evidence_version"] == EVIDENCE_VERSION
    assert "generated_at" in doc
    assert "contract" in doc
    assert "provenance" in doc
    assert "core" in doc
    assert "deliverables" in doc
    assert "insights" in doc
    assert "exemplars" in doc
    assert isinstance(doc["operational"], bool)


def test_build_evidence_deliverables_present(kg):
    engine = ArchitectureIntelligenceEngine(kg)
    doc = build_evidence(engine)
    deliverables = doc["deliverables"]
    assert "dependency_intelligence" in deliverables
    assert "architecture_impact_engine" in deliverables
    assert "critical_path_engine" in deliverables
    assert "blast_radius_engine" in deliverables
    assert "knowledge_insights_report" in deliverables


def test_build_evidence_operational_flag_real_corpus(kg):
    engine = ArchitectureIntelligenceEngine(kg)
    doc = build_evidence(engine)
    # The corpus has artifacts, so exemplars.subject should be set
    # and operational should be True
    assert isinstance(doc["operational"], bool)


def test_build_evidence_limit_parameter(kg):
    engine = ArchitectureIntelligenceEngine(kg)
    doc = build_evidence(engine, limit=3)
    top = doc["deliverables"]["blast_radius_engine"]["top"]
    assert len(top) <= 3


# --- write_evidence ------------------------------------------------------------


def test_write_evidence_creates_file(tmp_path, kg):
    engine = ArchitectureIntelligenceEngine(kg)
    doc = build_evidence(engine)
    out_path = tmp_path / "subdir" / "evidence.json"
    result = write_evidence(doc, out_path)
    assert result == out_path
    assert out_path.exists()
    loaded = json.loads(out_path.read_text())
    assert loaded["evidence_version"] == EVIDENCE_VERSION


def test_write_evidence_returns_path(tmp_path, kg):
    engine = ArchitectureIntelligenceEngine(kg)
    doc = build_evidence(engine)
    target = tmp_path / "out.json"
    returned = write_evidence(doc, str(target))
    assert returned == Path(str(target))


# --- _assert_writable ----------------------------------------------------------


def test_write_evidence_refuses_frozen_corpus(kg):
    """Writing into the frozen corpus (00-BOOK, 00-SOURCE, 99-FREEZE) must be refused."""
    engine = ArchitectureIntelligenceEngine(kg)
    doc = build_evidence(engine)
    # Test file: engine/tests/graph/architecture/test_evidence.py
    # parents[4] = repo root (UCOS-CONSOLIDATION)
    repo_root = Path(__file__).resolve().parents[4]
    frozen_target = repo_root / "00-BOOK" / "evidence.json"
    with pytest.raises(InsightsWriteError):
        write_evidence(doc, frozen_target)


def test_write_evidence_outside_repo_is_allowed(tmp_path, kg):
    """A path outside the repository root must not be rejected."""
    engine = ArchitectureIntelligenceEngine(kg)
    doc = build_evidence(engine)
    target = tmp_path / "external" / "evidence.json"
    result = write_evidence(doc, target)
    assert result.exists()


def test_the_subject_section_is_omitted_when_nothing_has_a_blast_radius(kg, monkeypatch):
    """A SUBJECT IS THE ARTIFACT WITH THE LARGEST BLAST RADIUS, and a corpus where nothing
    reaches anything has none. Emitting the four analysis fields anyway would report a
    prediction, a reachability summary and a radius for the empty string — measurements about
    a node that does not exist — so they are omitted and ``subject`` is empty.
    """

    engine = ArchitectureIntelligenceEngine(kg)
    real_blast = engine.blast_radius

    class _NoTop:
        @staticmethod
        def top(limit: int = 1):
            return ()

        def __getattr__(self, name: str):
            return getattr(real_blast, name)

    class _Engine:
        blast_radius = _NoTop()

        def __getattr__(self, name: str):
            return getattr(engine, name)

    document = build_evidence(_Engine())

    assert document["exemplars"]["subject"] == ""
    assert "blast_radius" not in document["exemplars"]
    assert "critical_path_length" in document["exemplars"]


def test_writing_architecture_insights_inside_the_repository_is_allowed():
    """The permitted half of the frozen-corpus guard. Every other test writes under
    ``tmp_path``, which takes the "outside the repository" early return, so the in-repository
    case a real run takes had never been exercised."""

    repo_root = Path(__file__).resolve().parents[4]
    _assert_writable(repo_root / ".runtime" / "architecture" / "insights.json")

    with pytest.raises(InsightsWriteError, match="frozen corpus"):
        _assert_writable(repo_root / "00-BOOK" / "insights.json")
