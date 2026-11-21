"""EPIC-RTE-002 — Execution Checkpointing (Runtime Execution Platform).

Realises **Execution Checkpointing**: a deterministic, self-contained capture of a
modelled execution's progress up to a chosen stage boundary, sufficient to **resume
the execution** later (see :mod:`~engine.runtime.execution.continuation`). A
checkpoint is a *record structure only* — it stores what was decided; it decides
nothing and executes nothing (RUNTIME-013 ORL-15).

A :class:`Checkpoint` is intentionally self-describing and composition-free: it
carries the per-universe :class:`~engine.runtime.execution.state.UniverseExecutionState`
records (universes at or before the boundary keep their terminal status; later
universes are reset to ``pending``) plus the audit sequence reached. Because it
holds no ambient state and every collection is sorted, identical runs and
boundaries yield a byte-identical checkpoint (ORL-20), and it can be persisted and
restored verbatim (:mod:`~engine.runtime.execution.persistence`).
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

from engine.foundation.obs.logging import get_logger
from engine.foundation.obs.telemetry import trace
from engine.runtime.execution.errors import CheckpointError
from engine.runtime.execution.state import PENDING, UniverseExecutionState

if TYPE_CHECKING:  # pragma: no cover - typing only, avoids an import cycle
    from engine.runtime.execution.coordinator import ExecutionRun

_logger = get_logger("runtime.execution.checkpoint")

#: The recorded checkpoint format.
CHECKPOINT_FORMAT = "ucos-execution-checkpoint/1.0.0"


@dataclass(frozen=True, slots=True)
class Checkpoint:
    """A deterministic, resumable capture of execution progress (ORL-07/ORL-20)."""

    checkpoint_id: str
    run_id: str
    composition_id: str
    coordination: str
    through_stage: int
    states: tuple[UniverseExecutionState, ...]
    sequence: int

    def state_map(self) -> dict[str, UniverseExecutionState]:
        """A ``universe_id → state`` map for seeding a resumed execution."""
        return {state.universe_id: state for state in self.states}

    def to_dict(self) -> dict[str, Any]:
        return {
            "checkpoint_format": CHECKPOINT_FORMAT,
            "checkpoint_id": self.checkpoint_id,
            "run_id": self.run_id,
            "composition_id": self.composition_id,
            "coordination": self.coordination,
            "through_stage": self.through_stage,
            "sequence": self.sequence,
            "states": [state.to_dict() for state in self.states],
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Checkpoint:
        """Reconstruct a checkpoint from its :meth:`to_dict` form (persistence)."""
        try:
            return cls(
                checkpoint_id=str(data["checkpoint_id"]),
                run_id=str(data["run_id"]),
                composition_id=str(data["composition_id"]),
                coordination=str(data["coordination"]),
                through_stage=int(data["through_stage"]),
                states=tuple(UniverseExecutionState.from_dict(s) for s in data["states"]),
                sequence=int(data["sequence"]),
            )
        except (KeyError, TypeError, ValueError) as exc:
            raise CheckpointError("checkpoint record is malformed", detail=str(exc)) from exc


def checkpoint(run: ExecutionRun, *, through_stage: int | None = None) -> Checkpoint:
    """Capture ``run`` as a resumable :class:`Checkpoint` up to ``through_stage``.

    Args:
        run: the execution run to checkpoint.
        through_stage: the inclusive stage boundary to capture. Universes at a later
            stage are reset to ``pending`` so a resume re-derives them. Defaults to
            the run's final stage (a full checkpoint of the whole run). The sentinel
            ``-1`` retains nothing (a full reset — the empty resume point used by
            recovery when no stage completed cleanly).

    Raises:
        CheckpointError: if ``through_stage`` is below the ``-1`` reset sentinel.
    """
    max_stage = max((state.stage for state in run.states), default=0)
    boundary = max_stage if through_stage is None else through_stage
    if boundary < -1:
        raise CheckpointError(
            "checkpoint stage boundary is below the reset sentinel", through_stage=boundary
        )

    with trace("runtime.execution.checkpoint", run=run.run_id, through_stage=boundary):
        captured: list[UniverseExecutionState] = []
        sequence = 0
        for state in run.states:
            if state.stage <= boundary:
                captured.append(state)
                sequence += len(run.audit.for_universe(state.universe_id))
            else:
                captured.append(state.with_status(PENDING))
        captured.sort(key=lambda s: s.universe_id)
        states = tuple(captured)
        cp = Checkpoint(
            checkpoint_id=_checkpoint_id(run.run_id, boundary, states),
            run_id=run.run_id,
            composition_id=run.composition_id,
            coordination=run.coordination,
            through_stage=boundary,
            states=states,
            sequence=sequence,
        )
    _logger.info(
        "runtime.execution.checkpointed",
        checkpoint_id=cp.checkpoint_id,
        run=run.run_id,
        through_stage=boundary,
    )
    return cp


def _checkpoint_id(
    run_id: str, through_stage: int, states: tuple[UniverseExecutionState, ...]
) -> str:
    state_part = "|".join(f"{s.universe_id}:{s.status}" for s in states)
    payload = f"{run_id}||through={through_stage}||states={state_part}"
    digest = hashlib.sha256(payload.encode()).hexdigest()
    return f"UCOS-EXEC-CKPT-{digest[:16]}"


__all__ = ["CHECKPOINT_FORMAT", "Checkpoint", "checkpoint"]
