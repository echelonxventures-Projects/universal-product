"""EPIC-RTE-002 — Execution Continuation unit tests."""

from __future__ import annotations

import dataclasses

import pytest

from engine.runtime.execution.checkpoint import checkpoint
from engine.runtime.execution.continuation import continue_execution, verify_continuation
from engine.runtime.execution.coordinator import coordinate
from engine.runtime.execution.errors import ContinuationError
from engine.runtime.execution.state import FAILED


def test_continue_reproduces_final_states(composition):
    original = coordinate(composition)
    cp = checkpoint(original, through_stage=0)
    resumed = continue_execution(composition, cp)
    assert verify_continuation(original, resumed)


def test_continue_from_reset_reproduces_full_run(composition):
    original = coordinate(composition)
    cp = checkpoint(original, through_stage=-1)
    resumed = continue_execution(composition, cp)
    assert verify_continuation(original, resumed)


def test_continue_with_outcomes(composition):
    original = coordinate(composition, outcomes={"A": FAILED})
    cp = checkpoint(original, through_stage=-1)
    resumed = continue_execution(composition, cp, outcomes={"A": FAILED})
    assert verify_continuation(original, resumed)


def test_continue_rejects_foreign_checkpoint(composition):
    original = coordinate(composition)
    cp = checkpoint(original)
    foreign = dataclasses.replace(cp, composition_id="UCOS-COMPOSITION-other")
    with pytest.raises(ContinuationError) as exc:
        continue_execution(composition, foreign)
    assert exc.value.code == "RT-EXEC-CONT-001"


def test_verify_continuation_detects_divergence(composition):
    original = coordinate(composition)
    diverged = coordinate(composition, outcomes={"A": FAILED})
    with pytest.raises(ContinuationError) as exc:
        verify_continuation(original, diverged)
    assert "A" in exc.value.context["divergent"]
