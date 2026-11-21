"""Deterministic proof of the UGA -> UCKP existence projection (`existence_resolution`).

Six properties, each required by PHASE-UCF-005-PROVIDER-INTEGRATION-DETERMINATION.md:
identity preservation, ownership mapping, lifecycle mapping, facet evaluation, zero
duplicate objects, and zero canonical contamination.
"""

from __future__ import annotations

import json

import pytest

from engine.uckp.alignment import REPOSITORY_NAMESPACE
from engine.uckp.registry import UniversalKnowledgeRegistry
from engine.uckp.uga_projection import (
    _CATEGORY_MAP,
    _LIFECYCLE_MAP,
    _UGA_REGISTRY_PATH,
    UnrecognisedUGAValueError,
    _project_one,
    ucko_objects,
)


@pytest.fixture(scope="module")
def uga_entries() -> tuple[dict, ...]:
    with _UGA_REGISTRY_PATH.open(encoding="utf-8") as handle:
        return tuple(json.load(handle)["entries"])


@pytest.fixture(scope="module")
def projected() -> tuple:
    return ucko_objects()


# --- identity preservation ---------------------------------------------------------


def test_every_urn_carries_the_uga_universal_id_verbatim(uga_entries, projected) -> None:
    by_local_name = {obj.identity.local_name: obj for obj in projected}
    for entry in uga_entries:
        assert entry["universal_id"] in by_local_name
        obj = by_local_name[entry["universal_id"]]
        assert obj.identity.namespace == REPOSITORY_NAMESPACE
        assert obj.identity.urn == f"urn:ucos:ucko:{REPOSITORY_NAMESPACE}:{entry['universal_id']}"


def test_identity_is_injective_no_two_entries_derive_one_urn(projected) -> None:
    urns = [obj.identity.urn for obj in projected]
    assert len(urns) == len(set(urns))


def test_minting_is_pure_same_entry_same_identity_every_call() -> None:
    first = ucko_objects()
    second = ucko_objects()
    assert [o.identity.urn for o in first] == [o.identity.urn for o in second]
    assert [o.identity.uuid for o in first] == [o.identity.uuid for o in second]


# --- ownership mapping ---------------------------------------------------------------


def test_ownership_is_carried_through_unmodified(uga_entries, projected) -> None:
    by_local_name = {obj.identity.local_name: obj for obj in projected}
    for entry in uga_entries:
        assert by_local_name[entry["universal_id"]].ownership.owner == entry["owner"]


# --- lifecycle mapping -----------------------------------------------------------------


def test_lifecycle_map_is_total_over_every_value_uga_actually_emits(uga_entries) -> None:
    observed = {entry["lifecycle"] for entry in uga_entries}
    assert observed <= set(_LIFECYCLE_MAP)


def test_lifecycle_mapping_is_applied_consistently(uga_entries, projected) -> None:
    by_local_name = {obj.identity.local_name: obj for obj in projected}
    for entry in uga_entries:
        expected = _LIFECYCLE_MAP[entry["lifecycle"]]
        assert by_local_name[entry["universal_id"]].lifecycle == expected


def test_unmapped_lifecycle_fails_closed_rather_than_guessing() -> None:
    bad_entry = {
        "universal_id": "UCOS-TEST-000001",
        "path": "does/not/matter",
        "object_class": "DATA_OBJECT",
        "lifecycle": "NOT-A-REAL-VALUE",
        "owner": "nobody",
    }
    with pytest.raises(UnrecognisedUGAValueError):
        _project_one(bad_entry)


def test_unmapped_object_class_fails_closed_rather_than_guessing() -> None:
    bad_entry = {
        "universal_id": "UCOS-TEST-000002",
        "path": "does/not/matter",
        "object_class": "NOT-A-REAL-CLASS",
        "lifecycle": "AUTHORED",
        "owner": "nobody",
    }
    with pytest.raises(UnrecognisedUGAValueError):
        _project_one(bad_entry)


def test_category_map_is_total_over_every_object_class_uga_actually_emits(uga_entries) -> None:
    observed = {entry["object_class"] for entry in uga_entries}
    assert observed <= set(_CATEGORY_MAP)


# --- facet evaluation (Article 6, require_complete) -----------------------------------


def test_every_projected_object_answers_all_thirty_three_facets(projected) -> None:
    incomplete = [obj.ucko_id for obj in projected if obj.missing_facets()]
    assert incomplete == []


def test_require_complete_raises_for_none_of_them(projected) -> None:
    for obj in projected:
        obj.require_complete()  # raises FacetError on failure; must not raise


def test_certification_validation_verification_are_present_but_honestly_unattested(
    projected,
) -> None:
    sample = projected[0]
    unattested = {facet.value for facet in sample.unattested_facets()}
    assert unattested == {"certification", "validation", "verification"}


# --- zero duplicate objects -------------------------------------------------------------


def test_registry_admits_every_projected_object_with_zero_refusals() -> None:
    registry = UniversalKnowledgeRegistry()
    report = registry.discover()
    assert "engine.uckp.uga_projection" in report.providers_found
    assert not report.failures


def test_projection_count_matches_the_uga_registry_exactly(uga_entries, projected) -> None:
    assert len(projected) == len(uga_entries)


# --- zero canonical contamination -------------------------------------------------------


def test_reading_the_uga_registry_does_not_mutate_it(uga_entries) -> None:
    ucko_objects()
    with _UGA_REGISTRY_PATH.open(encoding="utf-8") as handle:
        after = tuple(json.load(handle)["entries"])
    assert after == uga_entries


def test_projection_writes_no_file_anywhere(tmp_path, monkeypatch) -> None:
    import os

    before = {
        os.path.join(root, name)
        for root, _dirs, files in os.walk(".")
        if ".git" not in root
        for name in files
    }
    ucko_objects()
    after = {
        os.path.join(root, name)
        for root, _dirs, files in os.walk(".")
        if ".git" not in root
        for name in files
    }
    assert before == after
