"""EPIC-RTE-002 — Execution Continuation (Runtime Execution Platform).

Realises **Execution Continuation**: resuming a modelled execution from a
:class:`~engine.runtime.execution.checkpoint.Checkpoint`. Continuation reuses the
:func:`~engine.runtime.execution.coordinator.coordinate` fold verbatim (seeding it
with the checkpoint) — it adds no execution logic. This is the platform's
**resumability** guarantee: continuing from any checkpoint reproduces the same
final per-universe state as an uninterrupted run with the same modelled outcomes
(RUNTIME-013 ORL-20). It executes nothing (ORL-15).
"""

from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING

from engine.foundation.obs.logging import get_logger
from engine.runtime.execution.coordinator import ExecutionRun, coordinate
from engine.runtime.execution.errors import ContinuationError

if TYPE_CHECKING:  # pragma: no cover - typing only, avoids an import cycle
    from engine.runtime.composition import RuntimeComposition
    from engine.runtime.execution.checkpoint import Checkpoint

_logger = get_logger("runtime.execution.continuation")


def continue_execution(
    composition: RuntimeComposition,
    checkpoint: Checkpoint,
    *,
    outcomes: Mapping[str, str] | None = None,
    subject: str = "engineering",
) -> ExecutionRun:
    """Resume ``composition`` from ``checkpoint`` (deterministic, resumable).

    Args:
        composition: the composition whose execution is being resumed. Its identity
            must match the checkpoint's.
        checkpoint: the resume point produced by
            :func:`~engine.runtime.execution.checkpoint.checkpoint`.
        outcomes: the same modelled outcomes used originally (so pending universes
            resolve identically).
        subject: the engineering subject authorising the resumed execution.

    Raises:
        ContinuationError: if the checkpoint does not belong to ``composition``.
    """
    if checkpoint.composition_id != composition.composition_id:
        raise ContinuationError(
            "checkpoint does not belong to this composition",
            checkpoint_composition=checkpoint.composition_id,
            composition_id=composition.composition_id,
        )
    run = coordinate(composition, outcomes=outcomes, subject=subject, resume=checkpoint)
    _logger.info(
        "runtime.execution.continued",
        run_id=run.run_id,
        checkpoint_id=checkpoint.checkpoint_id,
        status=run.status,
    )
    return run


def verify_continuation(original: ExecutionRun, resumed: ExecutionRun) -> bool:
    """Return True iff ``resumed`` reproduced ``original``'s final per-universe states.

    Raises:
        ContinuationError: if any universe's final status diverges (a broken resume).
    """
    original_map = {s.universe_id: s.status for s in original.states}
    resumed_map = {s.universe_id: s.status for s in resumed.states}
    if original_map != resumed_map:
        divergent = sorted(
            uid
            for uid in original_map.keys() | resumed_map.keys()
            if original_map.get(uid) != resumed_map.get(uid)
        )
        raise ContinuationError(
            "resumed execution diverged from the original run",
            divergent=divergent,
        )
    return True


__all__ = ["continue_execution", "verify_continuation"]
