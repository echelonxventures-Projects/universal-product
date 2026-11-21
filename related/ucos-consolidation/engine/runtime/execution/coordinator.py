"""EPIC-RTE-002 — Execution Coordinator (Runtime Execution Platform).

Realises the **Execution Coordinator**: the heart of the platform. It composes the
scheduler, lifecycle, authorization, isolation, federation, and auditing
capabilities into a single, **pure, deterministic fold** over a composition's
recorded schedule, producing an :class:`ExecutionRun` — the complete, auditable
record of a modelled execution.

The coordinator **executes nothing** (RUNTIME-013 ORL-15/ORL-23): it models each
Universe's progression through the lifecycle and records the outcome. Modelled
outcomes are supplied explicitly (``outcomes``) so the fold is a pure function of
its inputs; unspecified universes are modelled as completing successfully. A
universe whose dependency did not complete is deterministically **skipped**
(blocked propagation), so failure containment is decidable and stable.

Determinism (ORL-20): universes are processed in the schedule's recorded order,
lifecycle transitions are validated against the fixed transition table, no
wall-clock or ambient state is embedded, and the ``run_id`` is a SHA-256 over the
composition identity, coordination, sorted modelled outcomes, and any resume point.
Identical inputs therefore yield a byte-identical run. Passing ``resume`` seeds the
fold from a :class:`~engine.runtime.execution.checkpoint.Checkpoint`, which makes
every execution **resumable** while preserving the same final per-universe state.
"""

from __future__ import annotations

import hashlib
from collections.abc import Mapping
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

from engine.foundation.obs.logging import get_logger
from engine.foundation.obs.telemetry import trace
from engine.runtime.execution.auditing import TRANSITION, AuditLog
from engine.runtime.execution.authorization import authorize, require_authorization
from engine.runtime.execution.errors import ExecutionScheduleError
from engine.runtime.execution.federation import assert_federated, federate
from engine.runtime.execution.isolation import isolate
from engine.runtime.execution.lifecycle import require_transition
from engine.runtime.execution.scheduler import ExecutionSchedule, schedule
from engine.runtime.execution.state import (
    COMPLETED,
    FAILED,
    PENDING,
    READY,
    RUNNING,
    SKIPPED,
    UniverseExecutionState,
    derive_run_status,
)

if TYPE_CHECKING:  # pragma: no cover - typing only, avoids an import cycle
    from engine.runtime.composition import RuntimeComposition
    from engine.runtime.execution.checkpoint import Checkpoint

_logger = get_logger("runtime.execution.coordinator")

#: The recorded execution-run format.
EXECUTION_RUN_FORMAT = "ucos-execution-run/1.0.0"

#: The modelled outcomes a caller may request per universe.
REQUESTABLE_OUTCOMES: tuple[str, ...] = (COMPLETED, FAILED, SKIPPED)


@dataclass(frozen=True, slots=True)
class ExecutionRun:
    """The complete, deterministic, auditable record of a modelled execution.

    A *record structure only*: it carries the source composition, the schedule, the
    final per-universe states, the append-only audit log, the aggregate status, and
    the EC-1 provisional-state disclosure. It deploys and executes nothing.
    """

    run_id: str
    composition: RuntimeComposition
    coordination: str
    authorization_id: str
    schedule: ExecutionSchedule
    states: tuple[UniverseExecutionState, ...]
    audit: AuditLog
    status: str
    disclosure: dict[str, Any]
    descriptor: dict[str, Any]

    @property
    def composition_id(self) -> str:
        return self.composition.composition_id

    def state_of(self, universe_id: str) -> UniverseExecutionState:
        """The final state of ``universe_id`` (raises if not a member)."""
        for state in self.states:
            if state.universe_id == universe_id:
                return state
        raise ExecutionScheduleError(
            "universe is not part of the execution run", universe_id=universe_id
        )

    def state_map(self) -> dict[str, UniverseExecutionState]:
        return {state.universe_id: state for state in self.states}

    def universes_in(self, status: str) -> tuple[str, ...]:
        """Every universe id whose final state is ``status`` (sorted)."""
        return tuple(sorted(s.universe_id for s in self.states if s.status == status))

    def to_dict(self) -> dict[str, Any]:
        return dict(self.descriptor)


def coordinate(
    composition: RuntimeComposition,
    *,
    outcomes: Mapping[str, str] | None = None,
    subject: str = "engineering",
    resume: Checkpoint | None = None,
) -> ExecutionRun:
    """Coordinate a modelled execution of ``composition`` (pure, deterministic).

    Args:
        composition: the composition to execute.
        outcomes: optional ``universe_id → modelled outcome`` map; each value must
            be one of :data:`REQUESTABLE_OUTCOMES`. Unspecified universes complete.
        subject: the non-secret engineering subject authorising the execution.
        resume: an optional checkpoint to resume from (seeds the fold).

    Raises:
        ExecutionAuthorizationError: if the composition is not authorised.
        ExecutionScheduleError: if ``outcomes`` names an unknown universe or an
            unrecognised outcome.
        ExecutionIsolationError, ExecutionFederationError: on any residual isolation
            or federation leak (defensive re-checks).
    """
    requested = _validate_outcomes(composition, outcomes)

    with trace(
        "runtime.execution.coordinate",
        composition=composition.composition_id,
        resumed=resume is not None,
    ):
        authorization = require_authorization(authorize(composition, subject=subject))
        isolation = isolate(composition)
        federation = federate(composition)
        assert_federated(composition, isolation, federation)

        execution_schedule = schedule(composition)
        stage_map = execution_schedule.stage_map()

        states = _seed_states(composition, stage_map, resume)
        audit = AuditLog()

        for universe_id in execution_schedule.order:
            current = states[universe_id]
            if current.terminal:
                continue
            states[universe_id], audit = _advance(
                current, requested.get(universe_id, COMPLETED), states, audit
            )

        final_states = tuple(sorted(states.values(), key=lambda s: s.universe_id))
        status = derive_run_status(final_states)
        run_id = _run_id(composition.composition_id, composition.coordination, requested, resume)
        descriptor = build_run_descriptor(
            run_id=run_id,
            composition=composition,
            authorization_id=authorization.authorization_id,
            execution_schedule=execution_schedule,
            states=final_states,
            audit=audit,
            status=status,
        )
        run = ExecutionRun(
            run_id=run_id,
            composition=composition,
            coordination=composition.coordination,
            authorization_id=authorization.authorization_id,
            schedule=execution_schedule,
            states=final_states,
            audit=audit,
            status=status,
            disclosure=composition.disclosure,
            descriptor=descriptor,
        )

    _logger.info(
        "runtime.execution.coordinated",
        run_id=run_id,
        composition_id=composition.composition_id,
        status=status,
        transitions=len(audit),
    )
    return run


# --------------------------------------------------------------------------- #
# Fold helpers                                                                 #
# --------------------------------------------------------------------------- #


def _advance(
    current: UniverseExecutionState,
    requested_outcome: str,
    states: Mapping[str, UniverseExecutionState],
    audit: AuditLog,
) -> tuple[UniverseExecutionState, AuditLog]:
    """Advance one pending universe to its terminal state, recording every hop."""
    blocker = _blocking_dependency(current, states)
    if blocker is not None:
        return _skip(current, audit, detail=f"blocked-by:{blocker}")
    if requested_outcome == SKIPPED:
        return _skip(current, audit, detail="operator-skipped")

    audit = _record(audit, current, PENDING, READY)
    audit = _record(audit, current, READY, RUNNING)
    terminal = COMPLETED if requested_outcome == COMPLETED else FAILED
    require_transition(RUNNING, terminal)
    audit = _record(audit, current, RUNNING, terminal, detail=f"outcome:{terminal}")
    return current.with_status(terminal, outcome=f"outcome:{terminal}"), audit


def _skip(
    current: UniverseExecutionState, audit: AuditLog, *, detail: str
) -> tuple[UniverseExecutionState, AuditLog]:
    require_transition(PENDING, SKIPPED)
    audit = _record(audit, current, PENDING, SKIPPED, detail=detail)
    return current.with_status(SKIPPED, outcome=detail), audit


def _record(
    audit: AuditLog,
    state: UniverseExecutionState,
    source: str,
    target: str,
    *,
    detail: str = "",
) -> AuditLog:
    require_transition(source, target)
    return audit.append(
        event=TRANSITION,
        universe_id=state.universe_id,
        stage=state.stage,
        source_state=source,
        target_state=target,
        detail=detail,
    )


def _blocking_dependency(
    current: UniverseExecutionState, states: Mapping[str, UniverseExecutionState]
) -> str | None:
    """The first (sorted) dependency that did not complete, or ``None``."""
    for dependency in current.depends_on:
        if states[dependency].status != COMPLETED:
            return dependency
    return None


def _seed_states(
    composition: RuntimeComposition,
    stage_map: Mapping[str, int],
    resume: Checkpoint | None,
) -> dict[str, UniverseExecutionState]:
    """Build the initial state map (all pending, or seeded from a checkpoint)."""
    seeded = resume.state_map() if resume is not None else {}
    states: dict[str, UniverseExecutionState] = {}
    for universe in composition.universes:
        prior = seeded.get(universe.universe_id)
        status = prior.status if prior is not None else PENDING
        outcome = prior.outcome if prior is not None else ""
        states[universe.universe_id] = UniverseExecutionState(
            universe_id=universe.universe_id,
            context_id=universe.context_id,
            stage=stage_map[universe.universe_id],
            status=status,
            depends_on=universe.depends_on,
            outcome=outcome,
        )
    return states


# --------------------------------------------------------------------------- #
# Validation / identity / descriptor                                          #
# --------------------------------------------------------------------------- #


def _validate_outcomes(
    composition: RuntimeComposition, outcomes: Mapping[str, str] | None
) -> dict[str, str]:
    if not outcomes:
        return {}
    members = set(composition.universe_ids())
    validated: dict[str, str] = {}
    for universe_id, outcome in outcomes.items():
        if universe_id not in members:
            raise ExecutionScheduleError(
                "modelled outcome names a universe outside the composition",
                universe_id=universe_id,
            )
        if outcome not in REQUESTABLE_OUTCOMES:
            raise ExecutionScheduleError(
                "unrecognised modelled outcome",
                universe_id=universe_id,
                outcome=outcome,
                allowed=list(REQUESTABLE_OUTCOMES),
            )
        validated[universe_id] = outcome
    return validated


def _run_id(
    composition_id: str,
    coordination: str,
    outcomes: Mapping[str, str],
    resume: Checkpoint | None,
) -> str:
    outcome_part = ";".join(f"{k}={outcomes[k]}" for k in sorted(outcomes))
    resume_part = resume.checkpoint_id if resume is not None else "none"
    payload = (
        f"{composition_id}||coordination={coordination}"
        f"||outcomes={outcome_part}||resume={resume_part}"
    )
    digest = hashlib.sha256(payload.encode()).hexdigest()
    return f"UCOS-EXEC-RUN-{digest[:16]}"


def build_run_descriptor(
    *,
    run_id: str,
    composition: RuntimeComposition,
    authorization_id: str,
    execution_schedule: ExecutionSchedule,
    states: tuple[UniverseExecutionState, ...],
    audit: AuditLog,
    status: str,
) -> dict[str, Any]:
    """Build the deterministic, auditable execution-run descriptor (reusable)."""
    return {
        "execution_run_format": EXECUTION_RUN_FORMAT,
        "run_id": run_id,
        "authority": "ENGINEERING-EXECUTION-ONLY",
        "composition_id": composition.composition_id,
        "coordination": composition.coordination,
        "authorization_id": authorization_id,
        "status": status,
        "schedule": execution_schedule.to_dict(),
        "states": [state.to_dict() for state in states],
        "audit": audit.to_dict(),
        "provisional_state_disclosure": composition.disclosure,
    }


__all__ = [
    "EXECUTION_RUN_FORMAT",
    "REQUESTABLE_OUTCOMES",
    "ExecutionRun",
    "coordinate",
    "build_run_descriptor",
]
