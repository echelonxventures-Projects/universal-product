"""EPIC-RTE-002 — Execution Recovery (Runtime Execution Platform).

Realises **Execution Recovery**: establishing the last **consistent** point of a
run from which execution can be safely resumed. The recovery point is the highest
scheduled stage ``S`` such that *every* universe at a stage ``≤ S`` completed
successfully; universes beyond it are re-derived on continuation. Recovery reuses
:func:`~engine.runtime.execution.checkpoint.checkpoint` verbatim to materialise the
resume point and :func:`~engine.runtime.execution.continuation.continue_execution`
to resume — it adds no execution logic and executes nothing (RUNTIME-013 ORL-15).

If no stage completed cleanly (a failure or skip at stage 0), the recovery point is
the empty reset checkpoint (sentinel stage ``-1``): a full, safe restart. Recovery
is deterministic (ORL-20).
"""

from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING

from engine.foundation.obs.logging import get_logger
from engine.foundation.obs.telemetry import trace
from engine.runtime.execution.checkpoint import Checkpoint, checkpoint
from engine.runtime.execution.continuation import continue_execution
from engine.runtime.execution.state import COMPLETED

if TYPE_CHECKING:  # pragma: no cover - typing only, avoids an import cycle
    from engine.runtime.composition import RuntimeComposition
    from engine.runtime.execution.coordinator import ExecutionRun

_logger = get_logger("runtime.execution.recovery")


def recovery_stage(run: ExecutionRun) -> int:
    """The highest stage whose every universe (and all earlier) completed.

    Returns ``-1`` when even stage 0 did not complete cleanly (full restart).
    """
    by_stage: dict[int, list[str]] = {}
    for state in run.states:
        by_stage.setdefault(state.stage, []).append(state.status)

    boundary = -1
    for stage in sorted(by_stage):
        if all(status == COMPLETED for status in by_stage[stage]):
            boundary = stage
        else:
            break
    return boundary


def recover(run: ExecutionRun) -> Checkpoint:
    """Establish the last consistent :class:`Checkpoint` of ``run`` (deterministic)."""
    with trace("runtime.execution.recover", run=run.run_id):
        boundary = recovery_stage(run)
        point = checkpoint(run, through_stage=boundary)
    _logger.info(
        "runtime.execution.recovered",
        run=run.run_id,
        checkpoint_id=point.checkpoint_id,
        recovery_stage=boundary,
    )
    return point


def recover_and_continue(
    composition: RuntimeComposition,
    run: ExecutionRun,
    *,
    outcomes: Mapping[str, str] | None = None,
    subject: str = "engineering",
) -> ExecutionRun:
    """Recover ``run`` to its last consistent point and resume it (deterministic)."""
    point = recover(run)
    return continue_execution(composition, point, outcomes=outcomes, subject=subject)


__all__ = ["recovery_stage", "recover", "recover_and_continue"]
