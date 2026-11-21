"""Tests for TASK-000012 artifact repository (EPIC-002)."""

from __future__ import annotations

import pytest

from engine.registry.artifacts import ArtifactRepository
from engine.registry.errors import ArtifactNotFoundError, RegistryValidationError
from engine.registry.models import Artifact, LifecycleStatus


@pytest.fixture
def repo(source) -> ArtifactRepository:
    return ArtifactRepository.from_source(source)


def test_count_and_len(repo):
    assert repo.count() == 3
    assert len(repo) == 3
    assert len(list(iter(repo))) == 3
    assert len(repo.all()) == 3


def test_get_and_find_and_exists(repo):
    art = repo.get("UCOS-REG-000001")
    assert art.name == "Alpha"
    assert repo.find("UCOS-REG-000001") is art
    assert repo.find("nope") is None
    assert repo.exists("UCOS-REG-000001")
    assert not repo.exists("nope")


def test_get_missing_raises(repo):
    with pytest.raises(ArtifactNotFoundError):
        repo.get("UCOS-XXX-999999")


def test_by_native_id(repo):
    assert repo.by_native_id("ENG-001").universal_id == "UCOS-ENG-000001"
    assert repo.by_native_id("missing") is None


def test_by_category_case_insensitive(repo):
    assert {a.universal_id for a in repo.by_category("reg")} == {"UCOS-REG-000001"}


def test_by_program(repo):
    assert {a.universal_id for a in repo.by_program("eng")} == {"UCOS-ENG-000001"}


def test_by_volume(repo):
    assert len(repo.by_volume("VOL-000")) == 2
    assert len(repo.by_volume("VOL-003")) == 1


def test_by_status_enum_and_str(repo):
    assert {a.universal_id for a in repo.by_status(LifecycleStatus.FROZEN)} == {"UCOS-ENG-000001"}
    assert {a.universal_id for a in repo.by_status("ACTIVE")} == {
        "UCOS-BOOK-000000",
        "UCOS-REG-000001",
    }


def test_children_of(repo):
    kids = {a.universal_id for a in repo.children_of("UCOS-BOOK-000000")}
    assert kids == {"UCOS-REG-000001", "UCOS-ENG-000001"}


def test_filter_multi_criteria(repo):
    result = repo.filter(volume="VOL-000", status="ACTIVE")
    assert {a.universal_id for a in result} == {"UCOS-BOOK-000000", "UCOS-REG-000001"}


def test_filter_status_accepts_enum(repo):
    result = repo.filter(status=LifecycleStatus.FROZEN)
    assert {a.universal_id for a in result} == {"UCOS-ENG-000001"}


def test_filter_by_category(repo):
    result = repo.filter(category="ENG")
    assert {a.universal_id for a in result} == {"UCOS-ENG-000001"}


def test_filter_owner_and_parent(repo):
    result = repo.filter(parent="UCOS-BOOK-000000", program="ENG")
    assert {a.universal_id for a in result} == {"UCOS-ENG-000001"}
    assert repo.filter(owner="UCOS-PROGRAM-CUSTODIAN")  # non-empty


def test_filter_unknown_criteria(repo):
    with pytest.raises(RegistryValidationError):
        repo.filter(banana="yellow")


def test_categories_and_programs(repo):
    assert repo.categories() == ("BOOK", "ENG", "REG")
    assert repo.programs() == ("ENG", "UKB")


def test_status_counts(repo):
    counts = repo.status_counts()
    assert counts == {"ACTIVE": 2, "FROZEN": 1}


def test_duplicate_universal_id_rejected():
    dup = Artifact.from_dict(
        {
            "universal_id": "UCOS-A-000001",
            "name": "x",
            "volume": "VOL-000",
            "page_start": 1,
            "page_end": 1,
            "status": "ACTIVE",
            "version": "1.0.0",
            "path": "p",
        }
    )
    with pytest.raises(RegistryValidationError):
        ArtifactRepository([dup, dup])


def test_real_corpus_loads(real_data_dir):
    from engine.registry.source import RegistrySource

    repo = ArtifactRepository.from_source(RegistrySource(real_data_dir))
    assert repo.count() > 0
    root = repo.get("UCOS-BOOK-000000")
    assert root.parent is None
