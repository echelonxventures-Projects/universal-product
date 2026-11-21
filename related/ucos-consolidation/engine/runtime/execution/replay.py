"""EPIC-RTE-002 — Execution Replay (Runtime Execution Platform).

Realises **Execution Replay**: the deterministic re-derivation of an
:class:`~engine.runtime.execution.coordinator.ExecutionRun` from its source
composition. Because coordination is a pure function of the composition and the
modelled outcomes, replay reconstructs the requested outcomes from the original
run's recorded states and re-runs the coordinator verbatim — no execution logic is
duplicated. A faithful replay reproduces the original run byte-for-byte (validated
by :mod:`~engine.runtime.execution.replay_validation`). Replay records; it executes
nothing (RUNTIME-013 ORL-15/ORL-20).
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from engine.foundation.obs.logging import get_logger
from engine.foundation.obs.telemetry import trace
from engine.runtime.execution.coordinator import ExecutionRun, coordinate
from engine.runtime.execution.errors import ReplayError
from engine.runtime.execution.state import FAILED, SKIPPED

if TYPE_CHECKING:  # pragma: no cover - typing only, avoids an import cycle
    from engine.runtime.composition import RuntimeComposition

_logger = get_logger("runtime.execution.replay")

#: The outcome marker the coordinator records for an operator-requested skip.
_OPERATOR_SKIP = "operator-skipped"


def requested_outcomes(run: ExecutionRun) -> dict[str, str]:
    """Reconstruct the modelled outcomes a caller must have requested for ``run``.

    Only *requested* outcomes are recovered: a completed universe used the default,
    a blocked skip was derived automatically, so neither is emitted. A failure and
    an operator-requested skip are recovered explicitly.
    """
    outcomes: dict[str, str] = {}
    for state in run.states:
        if state.status == FAILED:
            outcomes[state.universe_id] = FAILED
        elif state.status == SKIPPED and state.outcome == _OPERATOR_SKIP:
            outcomes[state.universe_id] = SKIPPED
        # completed → default; blocked skip → derived; rolled_back → post-run
    return outcomes


def replay(composition: RuntimeComposition, run: ExecutionRun) -> ExecutionRun:
    """Deterministically replay ``run`` against ``composition``.

    Raises:
        ReplayError: if the run does not belong to ``composition``.
    """
    if run.composition_id != composition.composition_id:
        raise ReplayError(
            "run does not belong to this composition",
            run_composition=run.composition_id,
            composition_id=composition.composition_id,
        )
    with trace("runtime.execution.replay", run=run.run_id):
        replayed = coordinate(composition, outcomes=requested_outcomes(run))
    _logger.info(
        "runtime.execution.replayed",
        original_run=run.run_id,
        replayed_run=replayed.run_id,
    )
    return replayed


__all__ = ["requested_outcomes", "replay"]
