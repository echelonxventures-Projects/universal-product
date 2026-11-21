"""Tests for TASK-000011 registry domain models (EPIC-002)."""

from __future__ import annotations

import pytest

from engine.registry.errors import RegistryValidationError
from engine.registry.models import (
    TRACE_STAGES,
    Artifact,
    LifecycleStatus,
    Relationship,
    Traceability,
    Volume,
)


def _min_artifact(**overrides):
    record = {
        "universal_id": "UCOS-REG-000001",
        "name": "Alpha",
        "volume": "VOL-000",
        "page_start": 1,
        "page_end": 2,
        "status": "ACTIVE",
        "version": "1.0.0",
        "path": "00-BOOK/x.md",
    }
    record.update(overrides)
    return record


# -- LifecycleStatus ----------------------------------------------------------


def test_lifecycle_coerce_ok():
    assert LifecycleStatus.coerce("FROZEN", context="x") is LifecycleStatus.FROZEN


def test_lifecycle_coerce_invalid():
    with pytest.raises(RegistryValidationError):
        LifecycleStatus.coerce("MOON", context="x")


# -- Artifact -----------------------------------------------------------------


def test_artifact_minimal_defaults():
    art = Artifact.from_dict(_min_artifact())
    assert art.universal_id == "UCOS-REG-000001"
    assert art.status is LifecycleStatus.ACTIVE
    assert art.owner == "UNASSIGNED"
    assert art.dependencies == ()
    assert art.traceability.references() == ()


def test_artifact_full_record():
    art = Artifact.from_dict(
        _min_artifact(
            native_id="REG-001",
            description="desc",
            category="REG",
            parent="UCOS-BOOK-000000",
            dependencies=["UCOS-BOOK-000000"],
            program="UKB",
            owner="OWNER",
            tags=["a", "b"],
            content_hash="abc",
            traceability={"architecture": ["UCOS-BOOK-000000"], "requirement": ["EC-1"]},
        )
    )
    assert art.native_id == "REG-001"
    assert art.dependencies == ("UCOS-BOOK-000000",)
    assert art.tags == ("a", "b")
    assert art.traceability.stage("architecture") == ("UCOS-BOOK-000000",)
    assert set(art.traceability.references()) == {"UCOS-BOOK-000000", "EC-1"}


def test_artifact_not_a_mapping():
    with pytest.raises(RegistryValidationError):
        Artifact.from_dict(["not", "a", "map"])  # type: ignore[arg-type]


def test_artifact_missing_required():
    record = _min_artifact()
    del record["name"]
    with pytest.raises(RegistryValidationError):
        Artifact.from_dict(record)


def test_artifact_bad_native_id_type():
    with pytest.raises(RegistryValidationError):
        Artifact.from_dict(_min_artifact(native_id=123))


def test_artifact_bad_page_type():
    with pytest.raises(RegistryValidationError):
        Artifact.from_dict(_min_artifact(page_start="one"))


def test_artifact_bool_is_not_int():
    with pytest.raises(RegistryValidationError):
        Artifact.from_dict(_min_artifact(page_start=True))


def test_artifact_bad_dependencies_type():
    with pytest.raises(RegistryValidationError):
        Artifact.from_dict(_min_artifact(dependencies=[1, 2]))


def test_artifact_empty_string_field_rejected():
    with pytest.raises(RegistryValidationError):
        Artifact.from_dict(_min_artifact(name=""))


# -- Traceability -------------------------------------------------------------


def test_traceability_from_none_yields_empty_stages():
    trace = Traceability.from_dict(None, at="x")
    assert set(trace.stages) == set(TRACE_STAGES)
    assert all(v == () for v in trace.stages.values())


def test_traceability_not_a_mapping():
    with pytest.raises(RegistryValidationError):
        Traceability.from_dict([], at="x")


def test_traceability_unknown_stage():
    trace = Traceability.from_dict({}, at="x")
    with pytest.raises(RegistryValidationError):
        trace.stage("nonsense")


def test_traceability_bad_stage_value():
    with pytest.raises(RegistryValidationError):
        Traceability.from_dict({"architecture": "not-a-list"}, at="x")


# -- Relationship -------------------------------------------------------------


def test_relationship_ok():
    edge = Relationship.from_dict(
        {
            "edge_id": "UEDGE-000000001",
            "from": "UCOS-A-000001",
            "to": "UCOS-B-000001",
            "type": "Depends-On",
            "inverse_of": None,
            "note": "n",
        }
    )
    assert edge.source == "UCOS-A-000001"
    assert edge.target == "UCOS-B-000001"
    assert edge.type == "Depends-On"
    assert edge.note == "n"


def test_relationship_not_a_mapping():
    with pytest.raises(RegistryValidationError):
        Relationship.from_dict("x")  # type: ignore[arg-type]


def test_relationship_missing_target():
    with pytest.raises(RegistryValidationError):
        Relationship.from_dict({"edge_id": "UEDGE-1", "from": "A", "type": "Uses"})


def test_relationship_bad_inverse_type():
    with pytest.raises(RegistryValidationError):
        Relationship.from_dict(
            {"edge_id": "UEDGE-1", "from": "A", "to": "B", "type": "Uses", "inverse_of": 3}
        )


# -- Volume -------------------------------------------------------------------


def test_volume_ok():
    vol = Volume.from_dict(
        {
            "volume_id": "VOL-000",
            "serial": 0,
            "name": "IDX",
            "category": "IDX",
            "status": "ACTIVE",
            "artifact_count": 4,
            "page_range_start": 1,
            "page_range_end": 9,
        }
    )
    assert vol.serial == 0
    assert vol.page_range_end == 9


def test_volume_nullable_pages():
    vol = Volume.from_dict(
        {
            "volume_id": "VOL-001",
            "serial": 1,
            "name": "V",
            "category": "VSN",
            "status": "PLANNED",
            "page_range_start": None,
            "page_range_end": None,
        }
    )
    assert vol.page_range_start is None
    assert vol.artifact_count == 0


def test_volume_not_a_mapping():
    with pytest.raises(RegistryValidationError):
        Volume.from_dict(42)  # type: ignore[arg-type]


def test_volume_bad_page_type():
    with pytest.raises(RegistryValidationError):
        Volume.from_dict(
            {
                "volume_id": "VOL-000",
                "serial": 0,
                "name": "V",
                "category": "IDX",
                "status": "ACTIVE",
                "page_range_start": "x",
            }
        )
