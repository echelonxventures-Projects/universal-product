"""EPIC-VAL-002 — Repository Acceptance contracts tests."""

from __future__ import annotations

import pytest

from engine.acceptance.contracts import (
    AcceptanceFinding,
    AcceptanceRecord,
    AcceptanceStatus,
    CoverageDimension,
    CoverageProfile,
    DependencyRecord,
    GateSeverity,
    GateStatus,
    IntegrationRecord,
    RepositoryHealth,
    RepositoryInventory,
    RepositorySubject,
    ReuseRecord,
    UnitRecord,
    canonical_json,
    content_hash,
)
from engine.acceptance.errors import (
    AcceptanceIntegrityError,
    RepositorySubjectError,
)
from engine.runtime.disclosure import build_disclosure


def test_canonical_json_is_sorted_and_compact():
    assert canonical_json({"b": 1, "a": 2}) == '{"a":2,"b":1}'


def test_content_hash_is_deterministic():
    assert content_hash({"a": 1}) == content_hash({"a": 1})
    assert content_hash({"a": 1}) != content_hash({"a": 2})


# --- coverage ---------------------------------------------------------------
def test_coverage_dimension_complete_and_percent():
    full = CoverageDimension("statements", 10, 10)
    assert full.complete is True
    assert full.percent == 100.0
    partial = CoverageDimension("branches", 3, 4)
    assert partial.complete is False
    assert partial.percent == 75.0
    assert full.to_dict()["complete"] is True


def test_coverage_dimension_zero_total_is_vacuously_complete():
    empty = CoverageDimension("functions", 0, 0)
    assert empty.complete is True
    assert empty.percent == 100.0


def test_coverage_profile_missing_and_incomplete():
    profile = CoverageProfile(dimensions=(CoverageDimension("statements", 1, 2),))
    assert "statements" in profile.incomplete_dimensions()
    assert set(profile.missing_dimensions()) == set(CoverageProfile.REQUIRED) - {"statements"}
    assert profile.complete is False
    assert profile.by_name()["statements"].covered == 1


def test_coverage_profile_complete_when_all_required_full():
    profile = CoverageProfile(
        dimensions=tuple(CoverageDimension(n, 1, 1) for n in CoverageProfile.REQUIRED)
    )
    assert profile.complete is True
    assert profile.missing_dimensions() == ()
    assert profile.incomplete_dimensions() == ()
    assert profile.to_dict()["complete"] is True


# --- unit / dependency / reuse / integration --------------------------------
def test_unit_missing_trace_stages():
    unit = UnitRecord("U", owner="o", traceability=("requirement", "design"))
    assert "implementation" in unit.missing_trace_stages()
    assert unit.to_dict()["unit_id"] == "U"


def test_dependency_to_dict():
    assert DependencyRecord("D", resolved=True, pinned=True).to_dict()["pinned"] is True


def test_reuse_unjustified_duplicate():
    assert ReuseRecord("c").is_unjustified_duplicate is True
    assert ReuseRecord("c", reused=True).is_unjustified_duplicate is False
    assert ReuseRecord("c", justified=True).is_unjustified_duplicate is False
    assert ReuseRecord("c", reused=True).to_dict()["reused"] is True


def test_integration_to_dict():
    assert IntegrationRecord("p", satisfied=True).to_dict()["satisfied"] is True


# --- inventory --------------------------------------------------------------
def test_inventory_missing_extras_overlaps():
    inv = RepositoryInventory(
        expected=("A", "B", "C"),
        present=("A", "B", "X"),
        responsibilities={"r": ("A", "B"), "s": ("A",)},
    )
    assert inv.missing() == ("C",)
    assert inv.extras() == ("X",)
    assert inv.overlaps() == ("r",)
    assert inv.to_dict()["missing"] == ["C"]


def test_inventory_duplicates_by_id_and_by_content():
    inv = RepositoryInventory(
        present=("A", "A", "B"),
        content_hashes={"B": "h", "C": "h", "D": "z"},
    )
    dups = inv.duplicates()
    assert "A" in dups  # duplicate id
    assert "B" in dups and "C" in dups  # shared content hash
    assert "D" not in dups


def test_inventory_clean_has_no_defects():
    inv = RepositoryInventory(expected=("A",), present=("A",), content_hashes={"A": "h"})
    assert inv.duplicates() == ()
    assert inv.missing() == ()
    assert inv.extras() == ()
    assert inv.overlaps() == ()


# --- health / finding -------------------------------------------------------
def test_health_healthy_flag():
    assert RepositoryHealth().healthy is True
    assert RepositoryHealth(critical_issues=("x",)).healthy is False
    assert RepositoryHealth(warnings=("w",)).to_dict()["healthy"] is True


def test_finding_properties():
    passed = AcceptanceFinding("g", GateSeverity.BLOCKING, GateStatus.PASS)
    assert passed.passed is True
    assert passed.is_blocking_failure is False
    blocking = AcceptanceFinding("g", GateSeverity.BLOCKING, GateStatus.FAIL)
    assert blocking.is_blocking_failure is True
    advisory = AcceptanceFinding("g", GateSeverity.ADVISORY, GateStatus.FAIL)
    assert advisory.is_blocking_failure is False
    assert blocking.to_dict()["status"] == "fail"


# --- subject assimilation ---------------------------------------------------
def test_from_mapping_assimilates_full_subject(acceptable_facts):
    subject = RepositorySubject.from_mapping(acceptable_facts)
    assert subject.repository_id == "UCOS-REPO-0001"
    assert subject.epic_id == "EPIC-VAL-002"
    assert len(subject.units) == 2
    assert subject.units[0].owner == "UCOS-PROGRAM-CUSTODIAN"
    assert subject.coverage.complete is True
    assert subject.inventory.responsibilities["persist"] == ("UNIT-A",)
    assert subject.health.warnings == ("stale-branch",)
    # round-trips deterministically
    assert subject.digest() == RepositorySubject.from_mapping(acceptable_facts).digest()
    assert subject.to_dict()["epic_id"] == "EPIC-VAL-002"


def test_from_mapping_rejects_non_mapping():
    with pytest.raises(RepositorySubjectError):
        RepositorySubject.from_mapping([])  # type: ignore[arg-type]


def test_from_mapping_requires_identity():
    with pytest.raises(RepositorySubjectError):
        RepositorySubject.from_mapping({"epic_id": "E"})
    with pytest.raises(RepositorySubjectError):
        RepositorySubject.from_mapping({"repository_id": "R"})


def test_from_mapping_tolerates_sparse_and_scalar_fields():
    subject = RepositorySubject.from_mapping(
        {
            "repository_id": "R",
            "epic_id": "E",
            "discovered_repositories": "not-a-list",  # scalar -> empty tuple
            "units": [{"unit_id": "U"}],  # owner falsey -> None
            "inventory": "not-a-mapping",  # -> empty inventory
            "health": None,  # -> empty health
            "coverage": None,  # -> empty profile
        }
    )
    assert subject.discovered_repositories == ()
    assert subject.units[0].owner is None
    assert subject.inventory.expected == ()
    assert subject.health.critical_issues == ()
    assert subject.coverage.dimensions == ()


def test_from_mapping_handles_missing_inventory_submaps():
    subject = RepositorySubject.from_mapping(
        {
            "repository_id": "R",
            "epic_id": "E",
            "inventory": {"expected": ["A"], "present": ["A"]},
        }
    )
    assert subject.inventory.content_hashes == {}
    assert subject.inventory.responsibilities == {}


# --- acceptance record ------------------------------------------------------
def _record(status=AcceptanceStatus.ACCEPTED):
    return AcceptanceRecord.create(
        repository_id="R",
        epic_id="EPIC-VAL-002",
        status=status,
        evidence_ref="deadbeef",
        gates=(AcceptanceFinding("g", GateSeverity.BLOCKING, GateStatus.PASS),),
        disclosure=build_disclosure(),
    )


def test_record_is_content_addressed_and_reproducible():
    a = _record()
    b = _record()
    assert a.acceptance_id == b.acceptance_id
    assert a.content_sha256 == b.content_sha256
    assert a.acceptance_id.startswith("UCOS-ACCEPT-EPIC-VAL-002-")
    assert a.accepted is True
    assert a.verify_integrity() is True
    a.require_integrity()  # does not raise
    assert a.to_dict()["accepted"] is True


def test_record_rejected_status():
    rejected = _record(AcceptanceStatus.REJECTED)
    assert rejected.accepted is False


def test_record_integrity_detects_mutation():
    import dataclasses

    tampered = dataclasses.replace(_record(), evidence_ref="tampered")
    assert tampered.verify_integrity() is False
    with pytest.raises(AcceptanceIntegrityError):
        tampered.require_integrity()
