"""Tests for engine.knowledge.capability — Repository Self-Awareness (Part 04/09).

Everything is built in memory or under ``tmp_path``; nothing touches the certified
corpus or the real capability catalogue (DP-03).
"""

from __future__ import annotations

import json

import pytest

from engine.knowledge.capability import (
    CAPABILITY_ID_PREFIX,
    CAPABILITY_TAG,
    CAPABILITY_UNIVERSE,
    REPLACEMENT_PROHIBITED_TAG,
    VERIFICATION_TAG,
    CapabilityRecord,
    assimilate_capabilities,
    capability_id,
    capability_objects,
    coverage,
    is_capability,
    is_reuse_candidate,
    is_verification,
    load_catalog,
    replacement_prohibited,
)
from engine.knowledge.errors import KnowledgeSourceError, KnowledgeValidationError
from engine.knowledge.model import KnowledgeKind, Lifecycle
from engine.knowledge.store import KnowledgeBase

from .conftest import make_cko


def _record(**overrides) -> dict[str, object]:
    """A well-formed catalogue record; override any field."""
    record: dict[str, object] = {
        "unique_id": "RC-01",
        "canonical_name": "engine.knowledge.ukip",
        "canonical_location": "engine/knowledge/ukip",
        "category": "engine",
        "authority": "EC-1 CERTIFIED",
        "reuse": "REUSE_AS_IS/COMPOSE",
        "replacement_prohibited": True,
        "implementation_status": "CERTIFIED",
        "description": "Universal Knowledge Intelligence Platform.",
        "evidence_present": True,
        "summary": "Admits knowledge from an unbounded number of providers.",
        "symbols": ["KnowledgeRegistry", "ProvenanceLedger"],
    }
    record.update(overrides)
    return record


# -- identity ------------------------------------------------------------------


def test_capability_id_is_derived_from_location_not_from_order():
    first = capability_id("engine/knowledge/ukip")
    assert first.startswith(f"{CAPABILITY_ID_PREFIX}-")
    assert first == capability_id("engine/knowledge/ukip")
    assert first != capability_id("engine/knowledge/integration")


@pytest.mark.parametrize("location", ["", "   "])
def test_capability_id_refuses_an_empty_location(location):
    with pytest.raises(KnowledgeValidationError):
        capability_id(location)


# -- record parsing ------------------------------------------------------------


def test_record_round_trips_and_projects_a_sealed_object():
    record = CapabilityRecord.from_dict(_record())
    obj = record.to_object()
    assert obj.cko_id == record.cko_id
    assert obj.kind is KnowledgeKind.FACT
    assert obj.universe == CAPABILITY_UNIVERSE
    assert obj.lifecycle is Lifecycle.OPERATIONAL
    assert obj.owner == "UCOS-ENGINE-AUTHORITY"
    assert obj.documentation_links == ("engine/knowledge/ukip",)
    assert obj.content_sha256 == obj.sealed().content_sha256
    assert is_capability(obj) and replacement_prohibited(obj)


def test_statement_carries_both_purpose_and_symbol_surface():
    statement = CapabilityRecord.from_dict(_record()).statement()
    assert "unbounded number of providers" in statement
    assert "KnowledgeRegistry" in statement
    assert "engine/knowledge/ukip" in statement


def test_rationale_is_present_so_the_validation_gate_passes():
    assert CapabilityRecord.from_dict(_record()).rationale().strip()


def test_summary_is_preferred_over_the_truncated_description():
    with_summary = CapabilityRecord.from_dict(_record()).statement()
    without = CapabilityRecord.from_dict(_record(summary="")).statement()
    assert "unbounded number of providers" in with_summary
    assert "Universal Knowledge Intelligence Platform." in without


def test_missing_required_keys_fail_loudly():
    broken = _record()
    del broken["category"]
    with pytest.raises(KnowledgeValidationError):
        CapabilityRecord.from_dict(broken)


def test_empty_location_fails_loudly():
    with pytest.raises(KnowledgeValidationError):
        CapabilityRecord.from_dict(_record(canonical_location="  "))


def test_non_mapping_record_fails_loudly():
    with pytest.raises(KnowledgeValidationError):
        CapabilityRecord.from_dict(["not", "a", "mapping"])  # type: ignore[arg-type]


# -- lifecycle mapping ---------------------------------------------------------


@pytest.mark.parametrize(
    ("status", "lifecycle", "implemented"),
    [
        ("CERTIFIED", Lifecycle.OPERATIONAL, True),
        ("IMPLEMENTED", Lifecycle.IMPLEMENTED, True),
        ("PLANNED", Lifecycle.APPROVED, False),
        ("INDETERMINATE", Lifecycle.DRAFT, False),
        ("SOMETHING-NEW", Lifecycle.DRAFT, False),
    ],
)
def test_status_maps_to_lifecycle_and_only_built_things_are_reusable(
    status, lifecycle, implemented
):
    record = CapabilityRecord.from_dict(_record(implementation_status=status))
    assert record.lifecycle is lifecycle
    assert record.is_implemented is implemented


def test_an_unplanned_capability_is_never_offered_for_reuse():
    obj = CapabilityRecord.from_dict(_record(implementation_status="PLANNED")).to_object()
    assert not is_reuse_candidate(obj)


# -- verification packages -----------------------------------------------------


@pytest.mark.parametrize(
    "location",
    ["engine/tests", "engine/tests/knowledge", "platform/tests", "engine/test_helpers"],
)
def test_verification_packages_are_tagged_and_excluded_from_reuse(location):
    record = CapabilityRecord.from_dict(_record(canonical_location=location))
    assert record.is_verification
    obj = record.to_object()
    assert VERIFICATION_TAG in obj.tags
    assert is_verification(obj)
    assert is_capability(obj)
    assert not is_reuse_candidate(obj)


def test_a_real_capability_is_a_reuse_candidate():
    assert is_reuse_candidate(CapabilityRecord.from_dict(_record()).to_object())


def test_a_non_capability_object_is_not_a_capability():
    # Uses the founding seed principle rather than a synthetic id: any string matching
    # the UCKO family grammar (`UCKO-[A-Z]+-\d{3,4}`) is harvested from source by
    # `closure_engine.py` and would enter the concept universe as a phantom concept.
    assert not is_capability(make_cko("UCKO-PRIN-0001"))
    assert not is_reuse_candidate(make_cko("UCKO-PRIN-0001"))


def test_replacement_permitted_capability_carries_no_prohibition_tag():
    obj = CapabilityRecord.from_dict(_record(replacement_prohibited=False)).to_object()
    assert REPLACEMENT_PROHIBITED_TAG not in obj.tags
    assert not replacement_prohibited(obj)


def test_tags_include_the_capability_marker_and_location_vocabulary():
    tags = CapabilityRecord.from_dict(_record()).tags()
    assert CAPABILITY_TAG in tags
    assert "ukip" in tags and "knowledge" in tags
    assert tags == tuple(sorted(tags))


# -- catalogue loading ---------------------------------------------------------


def _write_catalog(tmp_path, records):
    path = tmp_path / "catalog.json"
    path.write_text(json.dumps({"capabilities": records}), encoding="utf-8")
    return path


def test_load_catalog_sorts_by_location(tmp_path):
    path = _write_catalog(
        tmp_path,
        [_record(canonical_location="b/two"), _record(canonical_location="a/one")],
    )
    records = load_catalog(path)
    assert [r.canonical_location for r in records] == ["a/one", "b/two"]


def test_load_catalog_refuses_a_duplicate_capability(tmp_path):
    path = _write_catalog(tmp_path, [_record(), _record()])
    with pytest.raises(KnowledgeValidationError):
        load_catalog(path)


def test_load_catalog_fails_closed_on_absent_file(tmp_path):
    with pytest.raises(KnowledgeSourceError):
        load_catalog(tmp_path / "missing.json")


def test_load_catalog_fails_closed_on_invalid_json(tmp_path):
    path = tmp_path / "bad.json"
    path.write_text("{not json", encoding="utf-8")
    with pytest.raises(KnowledgeSourceError):
        load_catalog(path)


def test_load_catalog_fails_closed_on_non_object_root(tmp_path):
    path = tmp_path / "root.json"
    path.write_text("[]", encoding="utf-8")
    with pytest.raises(KnowledgeSourceError):
        load_catalog(path)


def test_load_catalog_fails_closed_when_the_array_is_missing(tmp_path):
    path = tmp_path / "shape.json"
    path.write_text(json.dumps({"items": []}), encoding="utf-8")
    with pytest.raises(KnowledgeSourceError):
        load_catalog(path)


# -- projection + assimilation -------------------------------------------------


def test_capability_objects_are_ordered_by_id():
    records = [
        CapabilityRecord.from_dict(_record(canonical_location=f"engine/p{i}")) for i in range(4)
    ]
    ids = [obj.cko_id for obj in capability_objects(records)]
    assert ids == sorted(ids)


def test_assimilation_creates_what_is_missing_and_preserves_other_knowledge():
    base = KnowledgeBase([make_cko("UCKO-PRIN-0001")])
    records = [CapabilityRecord.from_dict(_record())]
    result = assimilate_capabilities(base, records)
    assert result.counts() == {
        "created": 1,
        "updated": 0,
        "unchanged": 0,
        "retired": 0,
        "capabilities": 1,
    }
    assert result.changed
    assert result.base.get_object("UCKO-PRIN-0001") is not None
    assert result.base.get_object(records[0].cko_id) is not None


def test_reassimilation_is_a_no_op_knowledge_once():
    base = KnowledgeBase([make_cko("UCKO-PRIN-0001")])
    records = [CapabilityRecord.from_dict(_record())]
    once = assimilate_capabilities(base, records)
    twice = assimilate_capabilities(once.base, records)
    assert twice.counts()["unchanged"] == 1
    assert twice.counts()["created"] == 0
    assert not twice.changed
    assert once.base.objects() == twice.base.objects()


def test_drifted_substance_is_updated_not_duplicated():
    base = KnowledgeBase([make_cko("UCKO-PRIN-0001")])
    records = [CapabilityRecord.from_dict(_record())]
    once = assimilate_capabilities(base, records)
    drifted = [CapabilityRecord.from_dict(_record(implementation_status="IMPLEMENTED"))]
    twice = assimilate_capabilities(once.base, drifted)
    assert twice.counts()["updated"] == 1
    assert twice.counts()["created"] == 0
    assert len(twice.base.objects()) == len(once.base.objects())


def test_a_vanished_capability_is_retired_so_it_cannot_be_a_false_reuse_target():
    base = KnowledgeBase([make_cko("UCKO-PRIN-0001")])
    once = assimilate_capabilities(base, [CapabilityRecord.from_dict(_record())])
    gone = assimilate_capabilities(once.base, [])
    assert gone.retired == (CapabilityRecord.from_dict(_record()).cko_id,)
    assert gone.changed
    assert gone.base.get_object("UCKO-PRIN-0001") is not None


def test_assimilation_report_serialises():
    result = assimilate_capabilities(KnowledgeBase(), [CapabilityRecord.from_dict(_record())])
    payload = result.to_dict()
    assert payload["counts"]["created"] == 1
    assert payload["created"] == [CapabilityRecord.from_dict(_record()).cko_id]


# -- coverage ------------------------------------------------------------------


def test_coverage_reports_the_blindness_before_and_closure_after():
    records = [CapabilityRecord.from_dict(_record())]
    empty = coverage(records, KnowledgeBase())
    assert empty["discovered"] == 1
    assert empty["recorded"] == 0
    assert empty["uncovered"] == 1
    assert empty["coverage_pct"] == 0.0
    assert empty["uncovered_locations"] == ["engine/knowledge/ukip"]

    closed = coverage(records, assimilate_capabilities(KnowledgeBase(), records).base)
    assert closed["recorded"] == 1
    assert closed["uncovered"] == 0
    assert closed["reusable"] == 1
    assert closed["coverage_pct"] == 100.0


def test_coverage_of_an_empty_catalogue_does_not_divide_by_zero():
    assert coverage([], KnowledgeBase())["coverage_pct"] == 0.0


def test_planned_capabilities_are_recorded_but_not_counted_reusable():
    records = [CapabilityRecord.from_dict(_record(implementation_status="PLANNED"))]
    report = coverage(records, assimilate_capabilities(KnowledgeBase(), records).base)
    assert report["recorded"] == 1
    assert report["reusable"] == 0
