"""EPIC-RTE-002 — Universal Runtime Execution Platform.

Public API surface for the Runtime Execution Platform: it extends the EPIC-006
Universal Runtime Composition Engine (``engine.runtime``) into a complete,
deterministic, resumable, observable execution platform. It **composes and executes
nothing live** — it models execution as a deterministic state machine over an
existing :class:`~engine.runtime.composition.RuntimeComposition` and its recorded
:class:`~engine.runtime.planner.ExecutionPlan`, producing recorded structures only
(RUNTIME-013 ORL-15/ORL-23), carrying the EC-1 provisional-state disclosure and
engineering-execution authority only (IP-01/DE-05; ORL-22).

The platform reuses every existing runtime capability verbatim (Mandatory Rule 4)
and adds no duplicate composition, planning, dependency, context, federation, or
disclosure logic. It realises the twenty EPIC-RTE-002 capabilities:

    scheduler · coordinator · lifecycle · monitoring · recovery · continuation ·
    checkpointing · replay · rollback · isolation · federation · authorization ·
    auditing · metrics · health · diagnostics · state · snapshot · persistence ·
    replay validation

— unified by the :class:`ExecutionPlatform` facade.
"""

from __future__ import annotations

from engine.runtime.execution.auditing import (
    AUDIT_LOG_FORMAT,
    AuditEvent,
    AuditLog,
)
from engine.runtime.execution.authorization import (
    AUTHORIZATION_FORMAT,
    EXECUTION_AUTHORITY,
    Authorization,
    authorize,
    require_authorization,
)
from engine.runtime.execution.checkpoint import (
    CHECKPOINT_FORMAT,
    Checkpoint,
    checkpoint,
)
from engine.runtime.execution.continuation import (
    continue_execution,
    verify_continuation,
)
from engine.runtime.execution.coordinator import (
    EXECUTION_RUN_FORMAT,
    REQUESTABLE_OUTCOMES,
    ExecutionRun,
    build_run_descriptor,
    coordinate,
)
from engine.runtime.execution.diagnostics import (
    DIAGNOSTICS_FORMAT,
    ExecutionDiagnostics,
    Finding,
    diagnose,
)
from engine.runtime.execution.errors import (
    CheckpointError,
    ContinuationError,
    ExecutionAuthorizationError,
    ExecutionFederationError,
    ExecutionIsolationError,
    ExecutionLifecycleError,
    ExecutionScheduleError,
    PersistenceError,
    RecoveryError,
    ReplayError,
    ReplayValidationError,
    RollbackError,
    RuntimeExecutionError,
    SnapshotError,
)
from engine.runtime.execution.federation import (
    FEDERATION_FORMAT,
    FederatedLink,
    FederationView,
    assert_federated,
    federate,
)
from engine.runtime.execution.health import (
    DEGRADED,
    HEALTH_FORMAT,
    HEALTH_STATES,
    HEALTHY,
    UNHEALTHY,
    ExecutionHealth,
    health,
)
from engine.runtime.execution.isolation import (
    ISOLATION_FORMAT,
    IsolationPartition,
    IsolationView,
    isolate,
)
from engine.runtime.execution.lifecycle import (
    LIFECYCLE_TRANSITIONS,
    allowed_transitions,
    can_transition,
    require_transition,
)
from engine.runtime.execution.metrics import (
    METRICS_FORMAT,
    ExecutionMetrics,
    execution_metrics,
)
from engine.runtime.execution.monitoring import (
    MONITOR_FORMAT,
    ExecutionMonitor,
    monitor,
)
from engine.runtime.execution.persistence import (
    Serialisable,
    from_json,
    persist_checkpoint,
    persist_run,
    persist_snapshot,
    restore_checkpoint,
    to_json,
)
from engine.runtime.execution.platform import (
    EXECUTION_RESULT_FORMAT,
    ExecutionPlatform,
    ExecutionResult,
)
from engine.runtime.execution.recovery import (
    recover,
    recover_and_continue,
    recovery_stage,
)
from engine.runtime.execution.replay import replay, requested_outcomes
from engine.runtime.execution.replay_validation import (
    REPLAY_VALIDATION_FORMAT,
    ReplayValidation,
    compare_runs,
    require_replay,
    validate_replay,
)
from engine.runtime.execution.rollback import (
    ROLLBACK_PLAN_FORMAT,
    RollbackPlan,
    rollback,
    rollback_plan,
)
from engine.runtime.execution.scheduler import (
    EXECUTION_SCHEDULE_FORMAT,
    ExecutionSchedule,
    ScheduledStep,
    schedule,
)
from engine.runtime.execution.snapshot import (
    SNAPSHOT_FORMAT,
    Snapshot,
    snapshot,
)
from engine.runtime.execution.state import (
    COMPLETED,
    EXECUTION_STATES,
    FAILED,
    PARTIAL,
    PENDING,
    READY,
    ROLLED_BACK,
    ROLLED_BACK_RUN,
    RUN_FAILED,
    RUN_STATUSES,
    RUNNING,
    SKIPPED,
    SUCCEEDED,
    TERMINAL_STATES,
    UniverseExecutionState,
    derive_run_status,
    is_terminal,
    require_state,
)

__all__ = [
    # ---- state + lifecycle ----
    "PENDING",
    "READY",
    "RUNNING",
    "COMPLETED",
    "FAILED",
    "SKIPPED",
    "ROLLED_BACK",
    "EXECUTION_STATES",
    "TERMINAL_STATES",
    "SUCCEEDED",
    "RUN_FAILED",
    "PARTIAL",
    "ROLLED_BACK_RUN",
    "RUN_STATUSES",
    "UniverseExecutionState",
    "derive_run_status",
    "is_terminal",
    "require_state",
    "LIFECYCLE_TRANSITIONS",
    "allowed_transitions",
    "can_transition",
    "require_transition",
    # ---- auditing ----
    "AUDIT_LOG_FORMAT",
    "AuditEvent",
    "AuditLog",
    # ---- authorization / isolation / federation ----
    "EXECUTION_AUTHORITY",
    "AUTHORIZATION_FORMAT",
    "Authorization",
    "authorize",
    "require_authorization",
    "ISOLATION_FORMAT",
    "IsolationPartition",
    "IsolationView",
    "isolate",
    "FEDERATION_FORMAT",
    "FederatedLink",
    "FederationView",
    "federate",
    "assert_federated",
    # ---- scheduler / coordinator ----
    "EXECUTION_SCHEDULE_FORMAT",
    "ScheduledStep",
    "ExecutionSchedule",
    "schedule",
    "EXECUTION_RUN_FORMAT",
    "REQUESTABLE_OUTCOMES",
    "ExecutionRun",
    "coordinate",
    "build_run_descriptor",
    # ---- observability ----
    "MONITOR_FORMAT",
    "ExecutionMonitor",
    "monitor",
    "METRICS_FORMAT",
    "ExecutionMetrics",
    "execution_metrics",
    "HEALTHY",
    "DEGRADED",
    "UNHEALTHY",
    "HEALTH_STATES",
    "HEALTH_FORMAT",
    "ExecutionHealth",
    "health",
    "DIAGNOSTICS_FORMAT",
    "Finding",
    "ExecutionDiagnostics",
    "diagnose",
    # ---- checkpoint / continuation / recovery ----
    "CHECKPOINT_FORMAT",
    "Checkpoint",
    "checkpoint",
    "continue_execution",
    "verify_continuation",
    "recovery_stage",
    "recover",
    "recover_and_continue",
    # ---- rollback / snapshot / persistence ----
    "ROLLBACK_PLAN_FORMAT",
    "RollbackPlan",
    "rollback_plan",
    "rollback",
    "SNAPSHOT_FORMAT",
    "Snapshot",
    "snapshot",
    "Serialisable",
    "to_json",
    "from_json",
    "persist_checkpoint",
    "restore_checkpoint",
    "persist_snapshot",
    "persist_run",
    # ---- replay / replay validation ----
    "requested_outcomes",
    "replay",
    "REPLAY_VALIDATION_FORMAT",
    "ReplayValidation",
    "compare_runs",
    "validate_replay",
    "require_replay",
    # ---- platform facade ----
    "EXECUTION_RESULT_FORMAT",
    "ExecutionResult",
    "ExecutionPlatform",
    # ---- errors ----
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
