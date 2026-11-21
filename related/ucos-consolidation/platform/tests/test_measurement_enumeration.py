"""UCOS-EPIC-004 — Enumeration Engine tests (UCOS-UMA-001)."""

from __future__ import annotations

from platform.measurement.contracts import MeasurementKind
from platform.measurement.enumeration import EnumerationEngine
from platform.measurement.errors import EnumerationError
from platform.tests._measurement_helpers import complete_snapshot, gapped_snapshot

import pytest


def test_enumerates_population_dimensions():
    enum = EnumerationEngine(complete_snapshot()).enumerate()
    assert enum.dimension("programs") == ("PROG-1",)
    assert enum.dimension("statuses") == ("CERTIFIED",)
    assert enum.dimension("volumes") == ("V-001",)
    assert enum.dimension("relationship_types") == ("Depends-On",)
    assert len(enum.dimension("trace_stages")) == 13
    assert enum.counts["artifacts"] == 2
    assert enum.counts["relationships"] == 1
    assert enum.counts["distinct_programs"] == 1
    assert enum.enumeration_id.startswith("UCOS-UMAE-")


def test_gapped_population_discovers_extra_values():
    enum = EnumerationEngine(gapped_snapshot()).enumerate()
    assert "UNASSIGNED" in enum.dimension("owners")
    assert "ORG-CORE" in enum.dimension("owners")
    assert set(enum.dimension("relationship_types")) == {"Depends-On", "References"}


def test_unknown_dimension_fails_closed():
    enum = EnumerationEngine(complete_snapshot()).enumerate()
    with pytest.raises(EnumerationError):
        enum.dimension("nonexistent")


def test_engine_requires_snapshot():
    with pytest.raises(EnumerationError):
        EnumerationEngine(object())  # type: ignore[arg-type]


def test_deterministic_and_as_measurement():
    a = EnumerationEngine(complete_snapshot()).enumerate()
    b = EnumerationEngine(complete_snapshot()).enumerate()
    assert a.fingerprint() == b.fingerprint()
    m = a.as_measurement()
    assert m.kind is MeasurementKind.ENUMERATION
    assert m.subject == "registry.population"
    assert a.to_dict()["enumeration_id"] == a.enumeration_id
