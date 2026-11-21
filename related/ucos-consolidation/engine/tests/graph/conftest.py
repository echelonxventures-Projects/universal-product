"""Fixtures for the Universal Knowledge Graph tests (UCOS-EPIC-002).

A single, internally-consistent registry substrate is written to ``tmp_path`` so
every projection has real content to exercise, without touching the read-only
certified corpus (DP-03). The substrate includes artifacts, relationships,
volumes, plus the auxiliary evidence/certification/twin documents the
Evidence/Validation/Certification projections consume.

A separate ``real_data_dir`` fixture points at the actual ``00-BOOK/DATA`` for
read-only integration checks (skipped when the corpus is unavailable).
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from engine.graph.adapter import KnowledgeGraphAdapter
from engine.graph.engine import build_core_graph
from engine.registry.adapter import RegistryAdapter
from engine.registry.source import (
    ARTIFACTS_FILE,
    RELATIONSHIPS_FILE,
    VOLUMES_FILE,
    RegistrySource,
    default_data_dir,
)

_TRACE_STAGES = (
    "requirement",
    "architecture",
    "design",
    "implementation",
    "source_code",
    "unit_test",
    "integration_test",
    "functional_test",
    "security_test",
    "certification",
    "deployment",
    "production",
    "operations",
)


def _trace(**stages):
    base = {stage: [] for stage in _TRACE_STAGES}
    base.update({k: list(v) for k, v in stages.items()})
    return base


def _artifact(
    uid,
    category,
    volume,
    *,
    status="ACTIVE",
    version="1.0.0",
    program="UKB",
    parent="UCOS-BOOK-000000",
    traceability=None,
    name=None,
):
    return {
        "universal_id": uid,
        "native_id": uid.replace("UCOS-", ""),
        "name": name or f"Artifact {uid}",
        "description": "",
        "category": category,
        "volume": volume,
        "page_start": 1,
        "page_end": 1,
        "status": status,
        "version": version,
        "parent": parent,
        "dependencies": [],
        "program": program,
        "owner": "UCOS-PROGRAM-CUSTODIAN",
        "tags": [program, category],
        "path": f"00-BOOK/{uid}.md",
        "return_link": "00-BOOK/UCOS-BOOK-000000.md",
        "content_hash": None,
        "traceability": traceability or _trace(),
    }


def _edge(edge_id, src, dst, edge_type, inverse_of=None, note="structural:test"):
    return {
        "edge_id": edge_id,
        "from": src,
        "to": dst,
        "type": edge_type,
        "inverse_of": inverse_of,
        "note": note,
    }


def _volume(vid, serial, name, category, count):
    return {
        "volume_id": vid,
        "serial": serial,
        "name": name,
        "description": f"Volume {name}.",
        "category": category,
        "status": "ACTIVE",
        "artifact_count": count,
        "page_range_start": 1,
        "page_range_end": 100,
        "index_path": f"00-BOOK/REGISTRIES/VOLUME-REGISTRY.md#{vid.lower()}",
    }


@pytest.fixture
def sample_artifacts():
    return [
        _artifact("UCOS-BOOK-000000", "BOOK", "VOL-000", parent=None, name="Root Book"),
        _artifact(
            "UCOS-CON-000001",
            "CON",
            "VOL-002",
            status="FROZEN",
            program="UKB",
            name="Constitution",
        ),
        _artifact(
            "UCOS-ARCH-000001",
            "ARCH",
            "VOL-003",
            program="ARCH",
            name="Architecture",
            traceability=_trace(requirement=["UCOS-CON-000001"], architecture=["UCOS-ARCH-000001"]),
        ),
        _artifact("UCOS-REG-000001", "REG", "VOL-000", status="CERTIFIED", name="Registry"),
        _artifact(
            "UCOS-IMP-000001",
            "IMP",
            "VOL-006",
            program="IMP",
            name="Implementation",
            traceability=_trace(
                requirement=["UCOS-CON-000001"], implementation=["UCOS-ENG-000001"]
            ),
        ),
        _artifact("UCOS-SVC-000001", "SVC", "VOL-006", program="SERVICE", name="Service"),
        _artifact("UCOS-ENG-000001", "ENG", "VOL-006", program="ENG", name="Engine A"),
    ]


@pytest.fixture
def sample_relationships():
    edges = []
    n = 0

    def add(src, dst, etype, inv=None):
        nonlocal n
        n += 1
        edges.append(_edge(f"UEDGE-{n:09d}", src, dst, etype, inverse_of=inv))

    # structural hierarchy
    for child in (
        "UCOS-CON-000001",
        "UCOS-ARCH-000001",
        "UCOS-REG-000001",
        "UCOS-IMP-000001",
        "UCOS-SVC-000001",
        "UCOS-ENG-000001",
    ):
        add(child, "UCOS-BOOK-000000", "Parent")
        add("UCOS-BOOK-000000", child, "Child")
    # dependency chain (acyclic): IMP -> ARCH -> CON ; SVC -> REG
    add("UCOS-IMP-000001", "UCOS-ARCH-000001", "Depends-On")
    add("UCOS-ARCH-000001", "UCOS-CON-000001", "Depends-On")
    add("UCOS-SVC-000001", "UCOS-REG-000001", "Depends-On")
    # required-by (inverse of depends-on)
    add("UCOS-CON-000001", "UCOS-ARCH-000001", "Required-By")
    # capability provision
    add("UCOS-SVC-000001", "UCOS-REG-000001", "Consumes")
    add("UCOS-REG-000001", "UCOS-SVC-000001", "Consumed-By")
    # traceability families
    add("UCOS-IMP-000001", "UCOS-ARCH-000001", "Implements")
    add("UCOS-ARCH-000001", "UCOS-IMP-000001", "Implemented-By")
    add("UCOS-IMP-000001", "UCOS-CON-000001", "Traces-To")
    add("UCOS-CON-000001", "UCOS-IMP-000001", "Traced-From")
    add("UCOS-ARCH-000001", "UCOS-CON-000001", "Authorized-By")
    add("UCOS-CON-000001", "UCOS-ARCH-000001", "Authorizes")
    return edges


@pytest.fixture
def sample_volumes():
    return [
        _volume("VOL-000", 0, "MASTER INDEX", "IDX", 2),
        _volume("VOL-002", 2, "CONSTITUTION", "CON", 1),
        _volume("VOL-003", 3, "ARCHITECTURE", "ARCH", 1),
        _volume("VOL-006", 6, "IMPLEMENTATION", "IMP", 3),
    ]


@pytest.fixture
def sample_signals():
    def sig(sid, subject, dimension, state, source, result="pass", coverage=90.0):
        return {
            "signal_id": sid,
            "subject_universal_id": subject,
            "subject_native_id": None,
            "dimension": dimension,
            "state": state,
            "source": source,
            "as_of": "2026-07-15T08:00:00Z",
            "evidence": f"ref://{sid}",
            "metrics": {"result": result, "coverage": coverage},
            "connector": source.lower(),
            "ingest_run": "URUN-000000001",
        }

    return [
        sig("USIG-000000001", "UCOS-IMP-000001", "build", "IMPLEMENTED", "GITHUB_ACTIONS"),
        sig("USIG-000000002", "UCOS-IMP-000001", "unit_testing", "IMPLEMENTED", "GITHUB_ACTIONS"),
        sig("USIG-000000003", "UCOS-SVC-000001", "security", "BLOCKED", "TRIVY", result="fail"),
        sig("USIG-000000004", "UCOS-ARCH-000001", "implementation", "IMPLEMENTED", "GIT"),
        # a signal whose subject is absent from the graph (tolerated / finding)
        sig("USIG-000000005", "UCOS-GHOST-999999", "quality", "BLOCKED", "SONARQUBE"),
    ]


@pytest.fixture
def sample_certification():
    return {
        "generated_at": "2026-07-15T00:00:00+00:00",
        "generator_version": "test",
        "standard": "UCOS-CERT",
        "verdict": "CERTIFIED",
        "domains_total": 2,
        "domains_passed": 2,
        "domains": {
            "identity": {"pass": True, "checks": [{"name": "unique ids", "pass": True}]},
            "knowledge_graph": {
                "pass": True,
                "checks": [{"name": "edges resolve", "pass": True}],
            },
        },
        "scope": "test",
    }


@pytest.fixture
def sample_twin():
    return {
        "generated_at": "2026-07-15T00:00:00+00:00",
        "dimensions": {
            "build": {"status": "IMPLEMENTED", "signal_source": "GITHUB_ACTIONS"},
            "unit_testing": {"status": "IMPLEMENTED", "signal_source": "GITHUB_ACTIONS"},
            "security": {"status": "BLOCKED", "signal_source": "TRIVY"},
        },
        "subjects": [],
    }


@pytest.fixture
def graph_data_dir(
    tmp_path,
    sample_artifacts,
    sample_relationships,
    sample_volumes,
    sample_signals,
    sample_certification,
    sample_twin,
) -> Path:
    (tmp_path / ARTIFACTS_FILE).write_text(
        json.dumps(
            {
                "generated_at": "2026-07-16T00:00:00+00:00",
                "generator_version": "test-1.0",
                "count": len(sample_artifacts),
                "artifacts": sample_artifacts,
            }
        ),
        encoding="utf-8",
    )
    (tmp_path / RELATIONSHIPS_FILE).write_text(
        json.dumps({"count": len(sample_relationships), "relationships": sample_relationships}),
        encoding="utf-8",
    )
    (tmp_path / VOLUMES_FILE).write_text(
        json.dumps({"count": len(sample_volumes), "volumes": sample_volumes}),
        encoding="utf-8",
    )
    (tmp_path / "signals.json").write_text(
        json.dumps({"signals": sample_signals}), encoding="utf-8"
    )
    (tmp_path / "certification.json").write_text(json.dumps(sample_certification), encoding="utf-8")
    (tmp_path / "twin.json").write_text(json.dumps(sample_twin), encoding="utf-8")
    return tmp_path


@pytest.fixture
def minimal_data_dir(tmp_path, sample_artifacts, sample_relationships, sample_volumes) -> Path:
    """A substrate WITHOUT the optional signals/certification/twin documents."""
    (tmp_path / ARTIFACTS_FILE).write_text(
        json.dumps({"count": len(sample_artifacts), "artifacts": sample_artifacts}),
        encoding="utf-8",
    )
    (tmp_path / RELATIONSHIPS_FILE).write_text(
        json.dumps({"count": len(sample_relationships), "relationships": sample_relationships}),
        encoding="utf-8",
    )
    (tmp_path / VOLUMES_FILE).write_text(
        json.dumps({"count": len(sample_volumes), "volumes": sample_volumes}),
        encoding="utf-8",
    )
    return tmp_path


@pytest.fixture
def registry(graph_data_dir) -> RegistryAdapter:
    return RegistryAdapter.open(graph_data_dir)


@pytest.fixture
def core(registry):
    return build_core_graph(registry)


@pytest.fixture
def kg(graph_data_dir) -> KnowledgeGraphAdapter:
    return KnowledgeGraphAdapter.open(graph_data_dir)


@pytest.fixture
def real_data_dir() -> Path:
    path = default_data_dir()
    if not path.is_dir():
        pytest.skip("00-BOOK/DATA registry substrate not present")
    return path


@pytest.fixture
def real_source(real_data_dir) -> RegistrySource:
    return RegistrySource(real_data_dir)
