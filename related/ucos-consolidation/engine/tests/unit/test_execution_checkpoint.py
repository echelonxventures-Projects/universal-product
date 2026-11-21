"""EPIC-RTE-002 — Execution Checkpointing unit tests."""

from __future__ import annotations

import pytest

from engine.runtime.execution.checkpoint import CHECKPOINT_FORMAT, Checkpoint, checkpoint
from engine.runtime.execution.coordinator import coordinate
from engine.runtime.execution.errors import CheckpointError
from engine.runtime.execution.state import COMPLETED, PENDING


def test_full_checkpoint_captures_all(composition):
    run = coordinate(composition)
    cp = checkpoint(run)
    assert cp.through_stage == 2  # concurrent diamond max stage
    assert {s.status for s in cp.states} == {COMPLETED}
    assert cp.sequence == len(run.audit)
    assert cp.checkpoint_id.startswith("UCOS-EXEC-CKPT-")


def test_partial_checkpoint_resets_later_stages(composition):
    run = coordinate(composition)
    cp = checkpoint(run, through_stage=0)
    by_id = {s.universe_id: s.status for s in cp.states}
    assert by_id["A"] == COMPLETED
    assert by_id["B"] == PENDING
    assert by_id["C"] == PENDING
    assert by_id["D"] == PENDING
    # only A's 3 transitions counted
    assert cp.sequence == 3


def test_reset_sentinel_retains_nothing(composition):
    run = coordinate(composition)
    cp = checkpoint(run, through_stage=-1)
    assert {s.status for s in cp.states} == {PENDING}
    assert cp.sequence == 0


def test_below_sentinel_raises(composition):
    run = coordinate(composition)
    with pytest.raises(CheckpointError) as exc:
        checkpoint(run, through_stage=-2)
    assert exc.value.code == "RT-EXEC-CKPT-001"


def test_state_map(composition):
    cp = checkpoint(coordinate(composition))
    assert set(cp.state_map()) == {"A", "B", "C", "D"}


def test_to_dict_and_from_dict_round_trip(composition):
    cp = checkpoint(coordinate(composition), through_stage=1)
    blob = cp.to_dict()
    assert blob["checkpoint_format"] == CHECKPOINT_FORMAT
    assert Checkpoint.from_dict(blob) == cp


def test_from_dict_malformed_raises():
    with pytest.raises(CheckpointError):
        Checkpoint.from_dict({"checkpoint_id": "x"})  # missing required keys


def test_checkpoint_is_deterministic(composition):
    run = coordinate(composition)
    assert checkpoint(run).checkpoint_id == checkpoint(run).checkpoint_id
