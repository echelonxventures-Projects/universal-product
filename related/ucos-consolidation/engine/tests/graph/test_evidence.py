"""Unit tests for engine.graph.evidence — operational evidence artifacts."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from engine.graph.evidence import (
    EVIDENCE_VERSION,
    EvidenceWriteError,
    _assert_writable,
    build_evidence,
    write_evidence,
)


def test_build_evidence_is_operational(kg):
    evidence = build_evidence(kg)
    assert evidence["evidence_version"] == EVIDENCE_VERSION
    assert evidence["operational"] is True
    assert len(evidence["projections"]) == 10
    assert evidence["validation"]["is_valid"] is True
    assert evidence["certification_verdict"] == "CERTIFIED"
    # the worked exemplar demonstrates a real traversal
    ex = evidence["exemplars"]
    assert ex["subject"]
    assert ex["blast_radius"] >= 1


def test_write_evidence_to_tmp(kg, tmp_path):
    evidence = build_evidence(kg)
    out = tmp_path / "nested" / "evidence.json"
    written = write_evidence(evidence, out)
    assert written.is_file()
    reloaded = json.loads(written.read_text())
    assert reloaded["operational"] is True


def test_write_evidence_refuses_frozen_corpus(kg):
    evidence = build_evidence(kg)
    repo_root = (
        __import__("pathlib")
        .Path(__import__("engine.graph.evidence", fromlist=["__file__"]).__file__)
        .resolve()
        .parents[2]
    )
    frozen_target = repo_root / "00-BOOK" / "DATA" / "should-not-write.json"
    with pytest.raises(EvidenceWriteError):
        write_evidence(evidence, frozen_target)
    assert not frozen_target.exists()


def test_the_impact_section_is_omitted_when_no_artifact_has_a_blast_radius(kg):
    """A SUBJECT IS THE ARTIFACT WHOSE CHANGE REACHES THE MOST, and a graph where nothing
    reaches anything has none. Emitting the four impact fields anyway would report a blast
    radius of zero for the empty string — a measurement about a node that does not exist —
    so the section is omitted and ``subject`` is empty, which is the honest answer.
    """

    real_impact = kg.impact()

    class _NoImpact:
        # An empty projection graph, taken from the real one rather than constructed,
        # so nothing here needs to know how a KnowledgeGraph is built.
        graph = real_impact.graph.subgraph(node_ids=[])

        @staticmethod
        def blast_radius(_node_id: str) -> int:
            return 0

        @staticmethod
        def impact_of(_node_id: str) -> tuple[str, ...]:
            return ()

        def __getattr__(self, name: str):
            return getattr(real_impact, name)

    class _Isolated:
        def __init__(self, real) -> None:
            self._real = real

        @staticmethod
        def impact():
            return _NoImpact()

        def __getattr__(self, name: str):
            return getattr(self._real, name)

    exemplars = build_evidence(_Isolated(kg))["exemplars"]

    assert exemplars["subject"] == ""
    assert "blast_radius" not in exemplars
    assert "impacted_sample" not in exemplars
    assert "dependency_acyclic" in exemplars


def test_writing_evidence_inside_the_repository_but_outside_the_freeze_is_allowed():
    """THE GUARD HAS TWO ANSWERS AND ONLY THE REFUSAL HAD A TEST.

    Every other evidence test writes under ``tmp_path``, which takes the "outside the repo"
    early return — so the permitted in-repository case, which is what a real invocation
    writing into the runtime directory takes, was never exercised. A guard that refused every
    in-repository path would look correct from a suite that only ever writes outside it.
    """

    repo_root = Path(__file__).resolve().parents[3]
    _assert_writable(repo_root / ".runtime" / "graph" / "evidence.json")

    with pytest.raises(EvidenceWriteError, match="frozen corpus"):
        _assert_writable(repo_root / "00-BOOK" / "evidence.json")
