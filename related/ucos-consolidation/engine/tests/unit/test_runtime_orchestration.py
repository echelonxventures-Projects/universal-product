"""TASK-000042 — Runtime Orchestration unit tests (EPIC-006).

Exercises the top-level orchestration entry point that composes existing Universes
into a coordinated, deterministic, disclosed orchestration record (RUNTIME-013).
"""

from __future__ import annotations

import json

import pytest

from engine.runtime.composition import Universe, compose
from engine.runtime.orchestration import (
    ORCHESTRATION_FORMAT,
    RuntimeOrchestration,
    orchestrate,
    orchestration_of,
)


@pytest.fixture
def universes(make_runtime_unit):
    a = Universe.of(make_runtime_unit("A"), context_id="ctx1")
    b = Universe.of(make_runtime_unit("B"), context_id="ctx1", depends_on=["A"])
    return a, b


def test_orchestrate_produces_orchestration(universes):
    a, b = universes
    orchestration = orchestrate([b, a], coordination="conditional")
    assert isinstance(orchestration, RuntimeOrchestration)
    assert orchestration.orchestration_id.startswith("UCOS-ORCHESTRATION-")
    assert orchestration.coordination == "conditional"
    assert orchestration.universe_ids() == ("A", "B")
    assert orchestration.plan.coordination == "conditional"


def test_orchestration_embeds_composition_and_disclosure(universes):
    a, b = universes
    orchestration = orchestrate([a, b])
    descriptor = orchestration.descriptor
    assert descriptor["orchestration_descriptor_format"] == ORCHESTRATION_FORMAT
    assert descriptor["composition_id"] == orchestration.composition_id
    assert descriptor["universe_count"] == 2
    assert descriptor["composition"]["composition_id"] == orchestration.composition_id
    assert orchestration.disclosure["gate"] == "EC-1"


def test_orchestrate_is_deterministic(universes):
    a, b = universes
    first = orchestrate([a, b], coordination="sequential")
    second = orchestrate([b, a], coordination="sequential")
    assert first.orchestration_id == second.orchestration_id
    assert json.dumps(first.to_dict(), sort_keys=True) == json.dumps(
        second.to_dict(), sort_keys=True
    )


def test_orchestration_of_wraps_composition(universes):
    a, b = universes
    composition = compose([a, b], coordination="concurrent")
    orchestration = orchestration_of(composition)
    assert orchestration.composition is composition
    assert orchestration.composition_id == composition.composition_id
    assert orchestration.coordination == "concurrent"


def test_orchestration_id_tracks_coordination(universes):
    a, b = universes
    seq = orchestrate([a, b], coordination="sequential")
    con = orchestrate([a, b], coordination="concurrent")
    assert seq.orchestration_id != con.orchestration_id
