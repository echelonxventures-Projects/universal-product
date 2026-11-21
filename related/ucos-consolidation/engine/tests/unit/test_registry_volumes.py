"""Tests for TASK-000014 volume repository & integrity views (EPIC-002)."""

from __future__ import annotations

import pytest

from engine.registry.artifacts import ArtifactRepository
from engine.registry.errors import VolumeNotFoundError
from engine.registry.graph import RelationshipGraph
from engine.registry.models import Artifact, Relationship, Volume
from engine.registry.volumes import VolumeRepository, check_integrity


@pytest.fixture
def volumes(source) -> VolumeRepository:
    return VolumeRepository.from_source(source)


def test_count_len_iter_all(volumes):
    assert volumes.count() == 2
    assert len(volumes) == 2
    assert len(list(iter(volumes))) == 2
    assert len(volumes.all()) == 2


def test_get_find_exists(volumes):
    assert volumes.get("VOL-000").name == "MASTER INDEX"
    assert volumes.find("VOL-003").category == "ARCH"
    assert volumes.find("VOL-999") is None
    assert volumes.exists("VOL-000")
    assert not volumes.exists("VOL-999")


def test_get_missing_raises(volumes):
    with pytest.raises(VolumeNotFoundError):
        volumes.get("VOL-999")


def test_by_category_and_ids(volumes):
    assert {v.volume_id for v in volumes.by_category("arch")} == {"VOL-003"}
    assert volumes.ids() == ("VOL-000", "VOL-003")


def test_integrity_consistent(source):
    artifacts = ArtifactRepository.from_source(source)
    graph = RelationshipGraph.from_source(source)
    vols = VolumeRepository.from_source(source)
    report = check_integrity(artifacts, graph, vols)
    assert report.is_consistent
    assert report.dangling_edge_endpoints == ()
    assert report.unknown_artifact_volumes == ()
    assert report.unknown_parents == ()
    assert report.volume_count_mismatches == ()


def _art(uid, **kw):
    base = {
        "universal_id": uid,
        "name": uid,
        "volume": "VOL-000",
        "page_start": 1,
        "page_end": 1,
        "status": "ACTIVE",
        "version": "1.0.0",
        "path": "p",
    }
    base.update(kw)
    return Artifact.from_dict(base)


def test_integrity_detects_all_anomalies():
    artifacts = ArtifactRepository(
        [
            _art("UCOS-A-000001", volume="VOL-000", parent="UCOS-MISSING-000001"),
            _art("UCOS-B-000001", volume="VOL-404"),
        ]
    )
    graph = RelationshipGraph(
        [
            Relationship.from_dict(
                {
                    "edge_id": "UEDGE-1",
                    "from": "UCOS-A-000001",
                    "to": "UCOS-GHOST-000001",
                    "type": "Depends-On",
                }
            )
        ]
    )
    volumes = VolumeRepository(
        [
            Volume.from_dict(
                {
                    "volume_id": "VOL-000",
                    "serial": 0,
                    "name": "V",
                    "category": "IDX",
                    "status": "ACTIVE",
                    "artifact_count": 5,
                }
            )
        ]
    )
    report = check_integrity(artifacts, graph, volumes)
    assert not report.is_consistent
    assert "UCOS-GHOST-000001" in report.dangling_edge_endpoints
    assert "VOL-404" in report.unknown_artifact_volumes
    assert "UCOS-MISSING-000001" in report.unknown_parents
    assert "VOL-000" in report.volume_count_mismatches


def test_real_corpus_volumes_load(real_data_dir):
    from engine.registry.source import RegistrySource

    vols = VolumeRepository.from_source(RegistrySource(real_data_dir))
    assert vols.count() > 0
    assert vols.exists("VOL-000")
