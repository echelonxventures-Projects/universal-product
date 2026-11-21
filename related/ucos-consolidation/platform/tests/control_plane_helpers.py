"""Shared substrate builder for the Universal Control Plane suites.

Every control-plane test that needs a *repository* gets this one instead of the
real 1,220-artifact registry. That is not only a speed decision: a hermetic
substrate is what proves the engine's central claim — that it hardcodes no path
and no identifier — because a control plane that only works against the packaged
substrate would pass its own tests while being unable to describe anything else.

The locators below are deliberately real repository shapes, so the declared truth
policy classifies them for real: ``engine/…`` and ``platform/…`` are canonical
and may own; ``99-FREEZE/…`` is historical and may not; ``00-MASTER/…`` is
operational memory and may not. That mix is what makes the fixture produce both
governed and not-governed subjects rather than a uniformly green population.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

#: Registered artifacts spanning every declared artifact class and both a truth
#: class that may own and three that may not.
FIXTURE_ARTIFACTS: tuple[dict[str, Any], ...] = (
    {
        "universal_id": "UCOS-REG-000001",
        "native_id": "REG-1",
        "name": "Fixture Registry Index",
        "description": "the registration record of the fixture substrate",
        "category": "REG",
        "volume": "VOL-000",
        "status": "ACTIVE",
        "version": "1.0.0",
        "parent": None,
        "dependencies": [],
        "program": "UKB",
        "owner": "FIXTURE-CUSTODIAN",
        "tags": ["REG"],
        "path": "00-BOOK/REGISTRIES/index.md",
        "content_hash": "a" * 64,
        "traceability": {"architecture": ["UCOS-ARCH-000001"]},
        "page_start": 1,
        "page_end": 2,
    },
    {
        "universal_id": "UCOS-GOV-000001",
        "native_id": "GOV-1",
        "name": "Fixture Governance Record",
        "description": "a governance artifact in a canonical home",
        "category": "GOV",
        "volume": "VOL-001",
        "status": "ACTIVE",
        "version": "2.1.0",
        "parent": None,
        "dependencies": ["UCOS-REG-000001"],
        "program": "GOV",
        "owner": "FIXTURE-CUSTODIAN",
        "tags": ["GOV"],
        "path": "engine/governance/pipeline.py",
        "content_hash": "b" * 64,
        "traceability": {"implementation": ["UCOS-IMP-000001"]},
        "page_start": 3,
        "page_end": 4,
    },
    {
        "universal_id": "UCOS-CERTIF-000001",
        "native_id": "CERT-1",
        "name": "Fixture Certification",
        "description": "a certification artifact frozen into historical state",
        "category": "CERTIF",
        "volume": "VOL-001",
        "status": "CERTIFIED",
        "version": "1.0.0",
        "parent": None,
        "dependencies": [],
        "program": "CERTIF",
        "owner": "FIXTURE-CUSTODIAN",
        "tags": ["CERTIF"],
        "path": "99-FREEZE/certificate.md",
        "content_hash": "c" * 64,
        "traceability": {"certification": ["UCOS-CERT-000001"]},
        "page_start": 5,
        "page_end": 6,
    },
    {
        "universal_id": "UCOS-EES-000001",
        "native_id": "EES-1",
        "name": "Fixture Evidence",
        "description": "an evidence artifact held in operational memory",
        "category": "EES",
        "volume": "VOL-002",
        "status": "ACTIVE",
        "version": "0.9.0",
        "parent": None,
        "dependencies": ["UCOS-GOV-000001"],
        "program": "EES",
        "owner": "FIXTURE-CUSTODIAN",
        "tags": ["EES"],
        "path": "00-MASTER/EVIDENCE/measure.md",
        "content_hash": "d" * 64,
        "traceability": {},
        "page_start": 7,
        "page_end": 8,
    },
    {
        "universal_id": "UCOS-FINALD-000001",
        "native_id": "DET-1",
        "name": "Fixture Determination",
        "description": "a determination artifact with no declared owner",
        "category": "FINALD",
        "volume": "VOL-002",
        "status": "COMPLETE",
        "version": "1.0.0",
        "parent": None,
        "dependencies": [],
        "program": "DET",
        "owner": "",
        "tags": ["FINALD"],
        "path": "platform/universal_control_plane/truth.py",
        "content_hash": "e" * 64,
        "traceability": {"architecture": ["UCOS-ARCH-000002"]},
        "page_start": 9,
        "page_end": 10,
    },
)

#: Relationship edges: one forward per admitted type, plus an inverse the truth
#: engine must ignore and a self-edge it must drop.
FIXTURE_RELATIONSHIPS: tuple[dict[str, Any], ...] = (
    {
        "edge_id": "UEDGE-000000001",
        "from": "UCOS-GOV-000001",
        "to": "UCOS-REG-000001",
        "type": "Depends-On",
        "inverse_of": None,
        "note": "structural",
    },
    {
        "edge_id": "UEDGE-000000002",
        "from": "UCOS-REG-000001",
        "to": "UCOS-GOV-000001",
        "type": "Required-By",
        "inverse_of": "UEDGE-000000001",
        "note": "inverse",
    },
    {
        "edge_id": "UEDGE-000000003",
        "from": "UCOS-EES-000001",
        "to": "UCOS-GOV-000001",
        "type": "Consumes",
        "inverse_of": None,
        "note": "",
    },
    {
        "edge_id": "UEDGE-000000004",
        "from": "UCOS-FINALD-000001",
        "to": "UCOS-FINALD-000001",
        "type": "Depends-On",
        "inverse_of": None,
        "note": "self-edge",
    },
)

FIXTURE_CAPABILITIES: tuple[dict[str, Any], ...] = (
    {
        "canonical_name": "engine.governance",
        "canonical_location": "engine/governance",
        "category": "engine",
        "authority": "EC-1 CERTIFIED",
        "description": "Repository Governance Pipeline.",
        "reuse": "REUSE/EXTEND",
        "replacement_prohibited": True,
        "implementation_status": "IMPLEMENTED",
    },
    {
        "canonical_name": "platform.universal_control_plane",
        "canonical_location": "platform/universal_control_plane",
        "category": "platform",
        "authority": "ENGINEERING-EXECUTION-ONLY",
        "description": "The Universal Control Plane.",
        "reuse": "REUSE/EXTEND",
        "replacement_prohibited": False,
        "implementation_status": "IMPLEMENTED",
    },
)

FIXTURE_CHANGE_LEDGER: dict[str, Any] = {
    "generated_at": "2026-01-01T00:00:00+00:00",
    "generator_version": "fixture/1.0.0",
    "counts": {"change_events": 3, "versioned_artifacts": 2},
    "change_event_histogram": {"Created": 2, "Version-Incremented": 1},
    "change_events": [
        {
            "change_id": "UCHG-000000001",
            "subject": "UCOS-REG-000001",
            "kind": "Created",
            "at": "2026-01-01T00:00:00+00:00",
            "snapshot_seq": 1,
            "from": None,
            "to": "ACTIVE",
        },
        {
            "change_id": "UCHG-000000002",
            "subject": "UCOS-GOV-000001",
            "kind": "Created",
            "at": "2026-01-01T00:00:00+00:00",
            "snapshot_seq": 1,
            "from": None,
            "to": "DRAFT",
        },
        {
            "change_id": "UCHG-000000003",
            "subject": "UCOS-GOV-000001",
            "kind": "Version-Incremented",
            "at": "2026-01-02T00:00:00+00:00",
            "snapshot_seq": 2,
            "from": "DRAFT",
            "to": "ACTIVE",
        },
    ],
    "version_records": {
        "UCOS-REG-000001": {
            "current_version": "1.0.0",
            "first_version": "1.0.0",
            "version_depth": 1,
            "content_baseline": "a" * 64,
            "history": [{"version": "1.0.0", "content_hash": "a" * 64, "snapshot_seq": 1}],
        },
        "UCOS-GOV-000001": {
            "current_version": "2.1.0",
            "first_version": "2.0.0",
            "version_depth": 2,
            "content_baseline": "b" * 64,
            "history": [
                {"version": "2.0.0", "content_hash": "0" * 64, "snapshot_seq": 1},
                {"version": "2.1.0", "content_hash": "b" * 64, "snapshot_seq": 2},
            ],
        },
    },
    "lineage": {
        "UCOS-REG-000001": {"predecessors": [], "successors": [], "origin": "UCOS-REG-000001"},
        "UCOS-GOV-000001": {"predecessors": [], "successors": [], "origin": "UCOS-GOV-000001"},
    },
}

FIXTURE_CERTIFICATION: dict[str, Any] = {
    "generated_at": "2026-01-01T00:00:00+00:00",
    "standard": "Fixture Certification",
    "verdict": "CERTIFIED",
    "domains_total": 1,
    "domains_passed": 1,
    "domains": {"identity": {"pass": True, "checks": [{"name": "unique ids", "pass": True}]}},
    "scope": {"artifacts": 5, "edges": 4},
}

FIXTURE_VOLUMES: tuple[dict[str, Any], ...] = (
    {
        "volume_id": "VOL-000",
        "serial": 0,
        "name": "MASTER INDEX",
        "description": "",
        "category": "IDX",
        "status": "ACTIVE",
        "artifact_count": 1,
        "page_range_start": 1,
        "page_range_end": 2,
        "index_path": "00-BOOK/REGISTRIES/index.md",
    },
)


def _write(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=1), encoding="utf-8")


def build_substrate(
    root: Path,
    *,
    artifacts: tuple[dict[str, Any], ...] | None = None,
    relationships: tuple[dict[str, Any], ...] | None = None,
    capabilities: tuple[dict[str, Any], ...] | None = None,
    capability_catalog: bool = True,
) -> tuple[Path, Path]:
    """Write a complete fixture substrate under *root*.

    Returns ``(repository_root, data_dir)`` — the two arguments every
    control-plane entry point takes, and the two things it must never assume.
    """
    data_dir = root / "00-BOOK" / "DATA"
    _write(
        data_dir / "artifacts.json",
        {
            "generated_at": "2026-01-01T00:00:00+00:00",
            "count": len(artifacts or FIXTURE_ARTIFACTS),
            "artifacts": list(artifacts or FIXTURE_ARTIFACTS),
        },
    )
    _write(
        data_dir / "relationships.json",
        {
            "generated_at": "2026-01-01T00:00:00+00:00",
            "count": len(relationships or FIXTURE_RELATIONSHIPS),
            "relationships": list(relationships or FIXTURE_RELATIONSHIPS),
        },
    )
    _write(
        data_dir / "volumes.json",
        {
            "generated_at": "2026-01-01T00:00:00+00:00",
            "count": len(FIXTURE_VOLUMES),
            "volumes": list(FIXTURE_VOLUMES),
        },
    )
    _write(data_dir / "certification.json", FIXTURE_CERTIFICATION)
    _write(data_dir / "change-ledger.json", FIXTURE_CHANGE_LEDGER)
    if capability_catalog:
        _write(
            root / "intelligence" / "UCOS-RIE-CAPABILITY-CATALOG.json",
            {
                "artifact_id": "UCOS-RIE-CAPABILITY-CATALOG",
                "count": len(capabilities or FIXTURE_CAPABILITIES),
                "capabilities": list(capabilities or FIXTURE_CAPABILITIES),
            },
        )
    return root, data_dir


def discover_plane(root: Path, **kwargs: Any):
    """Discover a control plane over a fixture substrate built beneath *root*."""
    from platform.universal_control_plane.discovery import ControlPlane

    repository_root, data_dir = build_substrate(root)
    return ControlPlane.discover(
        data_dir=data_dir,
        repository_root=repository_root,
        journal_root=kwargs.pop("journal_root", root / "runtime"),
        **kwargs,
    )


__all__ = [
    "FIXTURE_ARTIFACTS",
    "FIXTURE_CAPABILITIES",
    "FIXTURE_CERTIFICATION",
    "FIXTURE_CHANGE_LEDGER",
    "FIXTURE_RELATIONSHIPS",
    "FIXTURE_VOLUMES",
    "build_substrate",
    "discover_plane",
]
