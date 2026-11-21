"""Shared deterministic fixtures for the Universal Measurement Engine tests (UCOS-EPIC-004).

Not a test module — provides builders for well-formed and gapped Registry Truth
populations (built from the certified Registry model objects) so the pure measurement
engines/registry/health/evidence core is exercised deterministically without coupling to
the live corpus.
"""

from __future__ import annotations

from platform.measurement.source import InMemoryTruthSource, TruthSnapshot

from engine.registry.models import (
    TRACE_STAGES,
    Artifact,
    Relationship,
    Volume,
)


def _full_trace(uid: str) -> dict[str, list[str]]:
    """A traceability map with every one of the 13 stages populated."""
    return {stage: [f"{uid}-{stage}"] for stage in TRACE_STAGES}


def artifact(
    uid: str,
    *,
    volume: str = "V-001",
    program: str = "PROG-1",
    category: str = "CAT-A",
    owner: str = "ORG-CORE",
    status: str = "CERTIFIED",
    parent: str | None = None,
    traceability: dict[str, list[str]] | None = None,
) -> Artifact:
    record: dict[str, object] = {
        "universal_id": uid,
        "name": f"Artifact {uid}",
        "volume": volume,
        "page_start": 1,
        "page_end": 2,
        "status": status,
        "version": "1.0.0",
        "path": f"path/{uid}.md",
        "program": program,
        "category": category,
        "owner": owner,
        "traceability": _full_trace(uid) if traceability is None else traceability,
    }
    if parent is not None:
        record["parent"] = parent
    return Artifact.from_dict(record)


def relationship(
    edge_id: str, source: str, target: str, rel_type: str = "Depends-On"
) -> Relationship:
    return Relationship.from_dict(
        {"edge_id": edge_id, "from": source, "to": target, "type": rel_type}
    )


def volume(
    volume_id: str,
    *,
    serial: int = 1,
    category: str = "CAT-A",
    status: str = "ACTIVE",
    artifact_count: int = 0,
) -> Volume:
    return Volume.from_dict(
        {
            "volume_id": volume_id,
            "serial": serial,
            "name": f"Volume {volume_id}",
            "category": category,
            "status": status,
            "artifact_count": artifact_count,
        }
    )


def complete_snapshot() -> TruthSnapshot:
    """Two fully-traced, owned, connected artifacts in a correctly-counted volume.

    No structural gaps, no completeness gaps: coverage is 100% and every artifact
    participates in a relationship.
    """
    arts = [
        artifact("UCOS-A001", volume="V-001"),
        artifact("UCOS-A002", volume="V-001"),
    ]
    rels = [relationship("EDGE-1", "UCOS-A001", "UCOS-A002")]
    vols = [volume("V-001", artifact_count=2)]
    return TruthSnapshot.create(arts, rels, vols)


def complete_source() -> InMemoryTruthSource:
    snap = complete_snapshot()
    return InMemoryTruthSource(snap.artifacts, snap.relationships, snap.volumes)


def gapped_snapshot() -> TruthSnapshot:
    """A population exhibiting every gap type the engine detects.

    Adds to the complete population: an artifact in an unknown volume, with an unknown
    parent, incomplete traceability, no owner, and no relationships (isolated); a
    dangling relationship endpoint; and a volume whose declared count is wrong.
    """
    arts = [
        artifact("UCOS-A001", volume="V-001"),
        artifact("UCOS-A002", volume="V-001"),
        artifact(
            "UCOS-A003",
            volume="V-UNKNOWN",
            parent="UCOS-GHOST-PARENT",
            owner="UNASSIGNED",
            traceability={"requirement": ["UCOS-A003-requirement"]},
        ),
    ]
    rels = [
        relationship("EDGE-1", "UCOS-A001", "UCOS-A002"),
        relationship("EDGE-2", "UCOS-A001", "UCOS-DANGLING", "References"),
    ]
    vols = [
        volume("V-001", artifact_count=2),
        volume("V-002", serial=2, artifact_count=9),  # declared 9, placed 0 -> mismatch
    ]
    return TruthSnapshot.create(arts, rels, vols)


def gapped_source() -> InMemoryTruthSource:
    snap = gapped_snapshot()
    return InMemoryTruthSource(snap.artifacts, snap.relationships, snap.volumes)


def empty_source() -> InMemoryTruthSource:
    """A degenerate empty population (no artifacts, relationships, or volumes)."""
    return InMemoryTruthSource([], [], [])


__all__ = [
    "artifact",
    "relationship",
    "volume",
    "complete_snapshot",
    "complete_source",
    "gapped_snapshot",
    "gapped_source",
    "empty_source",
]
