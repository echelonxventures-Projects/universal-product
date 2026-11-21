"""EPIC-RTE-002 — Execution Replay Validation unit tests."""

from __future__ import annotations

import pytest

from engine.runtime.execution.coordinator import coordinate
from engine.runtime.execution.errors import ReplayValidationError
from engine.runtime.execution.replay_validation import (
    REPLAY_VALIDATION_FORMAT,
    compare_runs,
    require_replay,
    validate_replay,
)
from engine.runtime.execution.state import FAILED


def test_validate_replay_is_valid(composition):
    result = validate_replay(composition, coordinate(composition, outcomes={"A": FAILED}))
    assert result.valid
    assert result.identical_id
    assert result.identical_descriptor
    assert result.mismatches == ()


def test_require_replay_passes(composition):
    assert require_replay(composition, coordinate(composition)).valid


def test_validation_to_dict(composition):
    blob = validate_replay(composition, coordinate(composition)).to_dict()
    assert blob["replay_validation_format"] == REPLAY_VALIDATION_FORMAT
    assert blob["valid"] is True


def test_compare_runs_detects_mismatch(composition):
    clean = coordinate(composition)
    failed = coordinate(composition, outcomes={"A": FAILED})
    result = compare_runs(clean, failed)
    assert not result.valid
    assert not result.identical_id
    assert not result.identical_descriptor
    assert "run_id" in result.mismatches
    # differing descriptor fields are reported
    assert "states" in result.mismatches


def test_require_replay_raises_on_divergence(composition, monkeypatch):
    clean = coordinate(composition)
    # Force the replay to diverge so the determinism gate fails loudly.
    monkeypatch.setattr(
        "engine.runtime.execution.replay_validation.replay",
        lambda comp, run: coordinate(comp, outcomes={"A": FAILED}),
    )
    with pytest.raises(ReplayValidationError) as exc:
        require_replay(composition, clean)
    assert exc.value.code == "RT-EXEC-REPLAYVAL-001"
