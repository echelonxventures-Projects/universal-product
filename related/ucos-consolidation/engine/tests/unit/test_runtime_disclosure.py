"""TASK-000036/000037 — Provisional-state disclosure unit tests (DE-05 / C-05)."""

from __future__ import annotations

import dataclasses

import pytest

from engine.runtime.assembly import assemble
from engine.runtime.disclosure import (
    DISCLOSURE_GATE,
    DISCLOSURE_ID,
    build_disclosure,
    disclosure_present,
    inject_provisional_state,
    require_disclosure,
)
from engine.runtime.errors import DisclosureError


def test_build_disclosure_is_deterministic():
    assert build_disclosure() == build_disclosure()
    disclosure = build_disclosure()
    assert disclosure["disclosure_id"] == DISCLOSURE_ID
    assert disclosure["gate"] == DISCLOSURE_GATE
    assert disclosure["gate_open"] is True
    assert disclosure["asserts_constitutional_finality"] is False
    assert disclosure["authority"] == "ENGINEERING-EXECUTION-ONLY"


def test_disclosure_present_validation():
    assert disclosure_present(build_disclosure()) is True
    assert disclosure_present(None) is False
    assert disclosure_present({}) is False
    assert disclosure_present({"disclosure_id": "OTHER"}) is False


def test_require_disclosure_raises_when_absent():
    with pytest.raises(DisclosureError):
        require_disclosure(None)
    assert require_disclosure(build_disclosure())["gate"] == DISCLOSURE_GATE


def test_assemble_auto_injects_disclosure(published_package, runtime_signer):
    unit = assemble(published_package, verify_with=runtime_signer)
    assert disclosure_present(unit.disclosure)
    assert unit.descriptor["provisional_state_disclosure"]["disclosure_id"] == DISCLOSURE_ID


def test_inject_is_idempotent(published_package, runtime_signer):
    unit = assemble(published_package, verify_with=runtime_signer)
    reinjected = inject_provisional_state(unit)
    assert reinjected.disclosure == unit.disclosure
    assert (
        reinjected.descriptor["provisional_state_disclosure"]
        == unit.descriptor["provisional_state_disclosure"]
    )


def test_inject_on_bare_unit(published_package, runtime_signer):
    unit = assemble(published_package, verify_with=runtime_signer)
    bare = dataclasses.replace(unit, disclosure=None)
    restored = inject_provisional_state(bare)
    assert disclosure_present(restored.disclosure)
