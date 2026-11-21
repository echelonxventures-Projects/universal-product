"""Fixtures for the Universal Discovery Engine tests (EPIC-003).

Two self-contained registry substrates are written to ``tmp_path`` so discovery is
exercised without touching the read-only certified corpus (DP-03):

    * ``clean_engine`` — a fully consistent substrate: every dimension is completely
      covered (universal discovery succeeds).
    * ``gapped_engine`` — a substrate seeded with exactly one referential gap in each
      gap-capable dimension (namespace, component, dependency, evidence, capability),
      so coverage shortfalls are provably detected and attributed.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from engine.discovery.engine import UniversalDiscoveryEngine
from engine.registry.source import ARTIFACTS_FILE, RELATIONSHIPS_FILE, VOLUMES_FILE

_TRACE_EMPTY = {
    "requirement": [],
    "architecture": [],
    "design": [],
    "implementation": [],
    "source_code": [],
    "unit_test": [],
    "integration_test": [],
    "functional_test": [],
    "security_test": [],
    "certification": [],
    "deployment": [],
    "production": [],
    "operations": [],
}


def artifact(uid, **overrides):
    """Build an artifact record with sensible, gap-free defaults."""
    base = {
        "universal_id": uid,
        "native_id": None,
        "name": f"Artifact {uid}",
        "description": "",
        "category": "REG",
        "volume": "VOL-000",
        "page_start": 1,
        "page_end": 1,
        "status": "ACTIVE",
        "version": "1.0.0",
        "parent": None,
        "dependencies": [],
        "program": "UKB",
        "owner": "UCOS-PROGRAM-CUSTODIAN",
        "tags": ["UKB", "REG"],
        "path": f"00-BOOK/{uid}.md",
        "return_link": "00-BOOK/UCOS-BOOK-000000-UNIVERSAL-MASTER-KNOWLEDGE-BOOK.md",
        "content_hash": f"hash-{uid}",
        "traceability": dict(_TRACE_EMPTY),
    }
    base.update(overrides)
    return base


def edge(edge_id, src, dst, edge_type, inverse_of=None, note="structural:chain"):
    return {
        "edge_id": edge_id,
        "from": src,
        "to": dst,
        "type": edge_type,
        "inverse_of": inverse_of,
        "note": note,
    }


def volume(vid, serial, name, category, artifact_count, page_start=1, page_end=10):
    return {
        "volume_id": vid,
        "serial": serial,
        "name": name,
        "description": f"Volume {name}.",
        "category": category,
        "status": "ACTIVE",
        "artifact_count": artifact_count,
        "page_range_start": page_start,
        "page_range_end": page_end,
        "index_path": f"00-BOOK/REGISTRIES/VOLUME-REGISTRY.md#{vid.lower()}",
    }


def _write_substrate(directory: Path, artifacts, relationships, volumes) -> Path:
    (directory / ARTIFACTS_FILE).write_text(
        json.dumps({"count": len(artifacts), "artifacts": artifacts}),
        encoding="utf-8",
    )
    (directory / RELATIONSHIPS_FILE).write_text(
        json.dumps({"count": len(relationships), "relationships": relationships}),
        encoding="utf-8",
    )
    (directory / VOLUMES_FILE).write_text(
        json.dumps({"count": len(volumes), "volumes": volumes}),
        encoding="utf-8",
    )
    return directory


@pytest.fixture
def clean_artifacts():
    return [
        artifact("UCOS-BOOK-000000", name="Root Book", category="BOOK", volume="VOL-000"),
        artifact(
            "UCOS-REG-000001",
            native_id="REG-001",
            name="Alpha",
            category="REG",
            volume="VOL-000",
            parent="UCOS-BOOK-000000",
            program="UKB",
        ),
        artifact(
            "UCOS-ENG-000001",
            native_id="ENG-001",
            name="Beta",
            category="ENG",
            volume="VOL-003",
            parent="UCOS-BOOK-000000",
            program="ENG",
            status="FROZEN",
            dependencies=["UCOS-REG-000001"],
        ),
    ]


@pytest.fixture
def clean_relationships():
    return [
        edge("UEDGE-000000001", "UCOS-REG-000001", "UCOS-BOOK-000000", "Parent"),
        edge("UEDGE-000000002", "UCOS-BOOK-000000", "UCOS-REG-000001", "Child"),
        edge("UEDGE-000000003", "UCOS-ENG-000001", "UCOS-REG-000001", "Depends-On"),
    ]


@pytest.fixture
def clean_volumes():
    return [
        volume("VOL-000", 0, "MASTER INDEX", "IDX", artifact_count=2),
        volume("VOL-003", 3, "ARCHITECTURE", "ARCH", artifact_count=1),
    ]


@pytest.fixture
def clean_data_dir(tmp_path, clean_artifacts, clean_relationships, clean_volumes) -> Path:
    return _write_substrate(tmp_path, clean_artifacts, clean_relationships, clean_volumes)


@pytest.fixture
def clean_engine(clean_data_dir) -> UniversalDiscoveryEngine:
    return UniversalDiscoveryEngine.open(clean_data_dir)


@pytest.fixture
def gapped_data_dir(tmp_path, clean_artifacts, clean_relationships, clean_volumes) -> Path:
    artifacts = [
        *clean_artifacts,
        # namespace gap: references a volume absent from the volume registry.
        artifact("UCOS-GAP-VOL", volume="VOL-999", category="GAP", program="GAPPROG"),
        # component gap: names a parent that resolves to no artifact.
        artifact("UCOS-GAP-PARENT", parent="UCOS-MISSING"),
        # dependency gap: declares a dependency on an unknown artifact.
        artifact("UCOS-GAP-DEP", dependencies=["UCOS-GHOST"]),
        # evidence gap: carries no content hash.
        artifact("UCOS-GAP-EVID", content_hash=None),
        # capability gap: a program whose only artifact is unrealised (PLANNED).
        artifact("UCOS-GAP-CAP", program="PLANPROG", status="PLANNED"),
    ]
    return _write_substrate(tmp_path, artifacts, clean_relationships, clean_volumes)


@pytest.fixture
def gapped_engine(gapped_data_dir) -> UniversalDiscoveryEngine:
    return UniversalDiscoveryEngine.open(gapped_data_dir)
