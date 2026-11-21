"""EPIC-RTE-002 — Runtime Execution Platform error taxonomy.

The Universal Runtime Execution Platform extends the EPIC-006 Universal Runtime
Composition Engine into a complete, deterministic, resumable, observable execution
platform. Like every other EC-1 capability it reuses the Foundation error
discipline (TASK-000006): every error is rooted in :class:`FoundationError`,
carries a stable, category-prefixed ``code`` and structured, non-secret
``context`` so failures are auditable (PL-02, IP-12) and machine-consumable.

Execution is a **recorded composition structure only** (RUNTIME-013 ORL-15/ORL-23):
the platform models execution as a deterministic state machine over an existing
:class:`~engine.runtime.composition.RuntimeComposition` and its recorded
:class:`~engine.runtime.planner.ExecutionPlan`. It launches no process, opens no
socket, and confers no authority (ORL-22). Its errors therefore form a distinct
root from both :class:`~engine.runtime.errors.RuntimeAssemblyError` and
:class:`~engine.runtime.errors.RuntimeCompositionError`, because execution is a
separate runtime capability (no duplicate capability ownership).
"""

from __future__ import annotations

from engine.foundation.obs.errors import FoundationError


class RuntimeExecutionError(FoundationError):
    """Base class for all Runtime Execution Platform errors (EPIC-RTE-002)."""

    code = "RT-EXEC-000"


class ExecutionLifecycleError(RuntimeExecutionError):
    """An illegal execution-state transition was attempted (ORL-15)."""

    code = "RT-EXEC-LIFE-001"


class ExecutionScheduleError(RuntimeExecutionError):
    """A deterministic execution schedule could not be produced (ORL-09/ORL-20)."""

    code = "RT-EXEC-SCHED-001"


class ExecutionAuthorizationError(RuntimeExecutionError):
    """Execution was not authorised — no EC-1 disclosure or authority overreach.

    Authorisation confers **engineering-execution authority only** and never
    constitutional authority (ORL-22; IP-01/DE-05).
    """

    code = "RT-EXEC-AUTH-001"


class ExecutionIsolationError(RuntimeExecutionError):
    """An execution crossed a bounding-context boundary without isolation (ORL-13)."""

    code = "RT-EXEC-ISO-001"


class ExecutionFederationError(RuntimeExecutionError):
    """A cross-context execution reference lacked an explicit federation (ORL-12)."""

    code = "RT-EXEC-FED-001"


class CheckpointError(RuntimeExecutionError):
    """A checkpoint could not be produced, is malformed, or does not match a run."""

    code = "RT-EXEC-CKPT-001"


class ContinuationError(RuntimeExecutionError):
    """Execution could not be resumed from the supplied checkpoint (resumability)."""

    code = "RT-EXEC-CONT-001"


class RecoveryError(RuntimeExecutionError):
    """No consistent recovery point could be established for the run."""

    code = "RT-EXEC-RECOV-001"


class RollbackError(RuntimeExecutionError):
    """A reversible rollback of the recorded execution could not be produced (IP-08)."""

    code = "RT-EXEC-RBACK-001"


class SnapshotError(RuntimeExecutionError):
    """An execution snapshot could not be produced or is malformed."""

    code = "RT-EXEC-SNAP-001"


class PersistenceError(RuntimeExecutionError):
    """A persisted execution artefact could not be serialised or restored."""

    code = "RT-EXEC-PERS-001"


class ReplayError(RuntimeExecutionError):
    """An execution could not be deterministically replayed."""

    code = "RT-EXEC-REPLAY-001"


class ReplayValidationError(RuntimeExecutionError):
    """A replay did not reproduce the original execution byte-for-byte (ORL-20)."""

    code = "RT-EXEC-REPLAYVAL-001"


__all__ = [
    "RuntimeExecutionError",
    "ExecutionLifecycleError",
    "ExecutionScheduleError",
    "ExecutionAuthorizationError",
    "ExecutionIsolationError",
    "ExecutionFederationError",
    "CheckpointError",
    "ContinuationError",
    "RecoveryError",
    "RollbackError",
    "SnapshotError",
    "PersistenceError",
    "ReplayError",
    "ReplayValidationError",
]
