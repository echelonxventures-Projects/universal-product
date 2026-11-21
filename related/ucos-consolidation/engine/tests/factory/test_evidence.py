"""TASK-000045 — Generation evidence tests (TASK-000043)."""

from __future__ import annotations

from engine.factory.classifier import resolve_blueprint_class
from engine.factory.contracts import FactoryRequest
from engine.factory.evidence import (
    EVIDENCE_FORMAT,
    GenerationEvidence,
    build_generation_evidence,
)


def _classification():
    return resolve_blueprint_class({"family": "BP-DATA"})


def test_build_evidence_full():
    disclosure = {
        "disclosure_id": "EC-1-PROVISIONAL-STATE",
        "gate": "EC-1",
        "asserts_constitutional_finality": False,
    }
    evidence = build_generation_evidence(
        blueprint_id="BP-DATA-0001",
        blueprint_version="1.0.0",
        classification=_classification(),
        compiler_artifact={"artifact_id": "UCOS-CMP-BP-DATA-0001-abc", "package_sha256": "aa"},
        runtime_artifact={"runtime_id": "UCOS-RUN-BP-DATA-0001-def", "image_reference": "img"},
        dependency_closure=[{"blueprint_id": "BP-DATA-0001", "role": "root"}],
        disclosure=disclosure,
    )
    assert isinstance(evidence, GenerationEvidence)
    d = evidence.to_dict()
    assert d["evidence_format"] == EVIDENCE_FORMAT
    assert d["blueprint"] == {"blueprint_id": "BP-DATA-0001", "version": "1.0.0"}
    assert d["classification"]["blueprint_class"] == "BP-DATA"
    assert d["compiler_artifact"]["artifact_id"] == "UCOS-CMP-BP-DATA-0001-abc"
    assert d["runtime_artifact"]["runtime_id"] == "UCOS-RUN-BP-DATA-0001-def"
    assert d["dependency_closure"] == [{"blueprint_id": "BP-DATA-0001", "role": "root"}]
    assert d["disclosure_state"] == {
        "present": True,
        "disclosure_id": "EC-1-PROVISIONAL-STATE",
        "gate": "EC-1",
        "asserts_constitutional_finality": False,
    }
    assert d["gap"] is None


def test_build_evidence_gap():
    evidence = build_generation_evidence(
        blueprint_id="BP-API-0001",
        blueprint_version="1.0.0",
        classification=resolve_blueprint_class({"family": "BP-API"}),
        compiler_artifact=None,
        runtime_artifact=None,
        dependency_closure=(),
        disclosure=None,
        gap={"stage": "parse", "code": "CMP-PARSE-001"},
    )
    d = evidence.to_dict()
    assert d["compiler_artifact"] is None
    assert d["runtime_artifact"] is None
    assert d["dependency_closure"] == []
    assert d["disclosure_state"] == {
        "present": False,
        "disclosure_id": None,
        "gate": None,
        "asserts_constitutional_finality": None,
    }
    assert d["gap"] == {"stage": "parse", "code": "CMP-PARSE-001"}


def test_evidence_is_deterministic():
    kwargs = dict(
        blueprint_id="BP-DATA-0001",
        blueprint_version="1.0.0",
        classification=_classification(),
        compiler_artifact={"artifact_id": "x", "package_sha256": "y"},
        runtime_artifact={"runtime_id": "r", "image_reference": "i"},
        dependency_closure=[{"blueprint_id": "BP-DATA-0001", "role": "root"}],
        disclosure={"disclosure_id": "EC-1-PROVISIONAL-STATE", "gate": "EC-1"},
    )
    first = build_generation_evidence(**kwargs).to_dict()
    second = build_generation_evidence(**kwargs).to_dict()
    assert first == second


def test_evidence_from_real_generation(orchestrator):
    result = orchestrator.generate(FactoryRequest("BP-DATA-0001"))
    evidence = result.evidence
    assert evidence["evidence_format"] == EVIDENCE_FORMAT
    assert evidence["dependency_closure"][0]["role"] == "root"
