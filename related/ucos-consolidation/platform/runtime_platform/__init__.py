"""UCOS EPIC-007 (Terminal T7) — Universal Runtime Platform.

The **Universal Runtime Platform** (URP) is the operational runtime plane of UCOS: it
governs the scheduling, placement, lifecycle, workflow orchestration, event flow, and
append-only registration of governed executions. It is a strictly **additive**,
**govern/record-only** layer over the Platform Foundation (events, services, contracts)
and the certified upstream engines it consumes **by reference** — Registry, Knowledge,
Measurement, Validation, and Certification. It runs nothing live, starts no server, and
never writes to the certified corpus (DP-03); every structure it produces is
deterministic and content-addressed (P5).

Deliverables:
    * **Runtime Core** — :class:`RuntimeKernel`: the minimal kernel that wires the plane
      and owns the fail-closed admission gate (VALIDATED ∧ CERTIFIED).
    * **Execution Engine** — :class:`ExecutionEngine`: models a governed execution as a
      deterministic lifecycle trajectory over a recorded :class:`ExecutionRecord`.
    * **Scheduling** — :func:`schedule`: a deterministic dependency-ordered
      :class:`ExecutionSchedule` over a batch of :class:`ExecutionRequest` records.
    * **Workflow** — :class:`WorkflowDefinition` / :class:`WorkflowRunner`: metadata-driven
      resolution and a governed saga run with compensate-on-failure.
    * **Event Bus** — :class:`RuntimeEventBus`: a governed façade over the Foundation
      event bus with a fixed runtime event-category vocabulary.
    * **Runtime Services** — :class:`RuntimeServiceCatalog`: the canonical runtime-service
      topology declared into the Foundation service registry.
    * **Execution Registry** — :class:`ExecutionRegistry`: an append-only, hash-chained,
      tamper-evident register of executions with lineage.
    * **Lifecycle** — the closed :mod:`~platform.runtime_platform.lifecycle` transition
      model.
    * **Infrastructure** — :class:`RuntimeInfrastructure` / :class:`CapacityPosture`: a
      technology-neutral capacity posture with deterministic workload placement.

:class:`RuntimePlatformService` is the governed composition point;
:func:`build_runtime_platform_service` provides the default wiring; and
:func:`bootstrap_runtime_platform` composes it onto a Platform Foundation context.
"""

from __future__ import annotations

from platform.runtime_platform.bootstrap import (
    RUNTIME_PLATFORM_BOOTSTRAP_EVENT,
    bootstrap_runtime_platform,
)
from platform.runtime_platform.contracts import (
    CONSUMED_CONTRACTS,
    RUNTIME_PLATFORM_CONTRACT_VERSION,
    RUNTIME_PLATFORM_CONTRACTS,
    RUNTIME_PLATFORM_GROUP,
    ConsumedCapability,
    RuntimePlatformAction,
    RuntimeServiceKind,
    RuntimeServiceView,
    WorkloadAttestation,
    all_runtime_service_kinds,
    default_runtime_platform_contracts,
    runtime_platform_contract,
)
from platform.runtime_platform.core import RUNTIME_KERNEL_FORMAT, RuntimeKernel
from platform.runtime_platform.errors import (
    ExecutionEngineError,
    ExecutionRegistryError,
    ExecutionRequestError,
    ExecutionScheduleError,
    RuntimeAdmissionError,
    RuntimeEventError,
    RuntimeInfrastructureError,
    RuntimeKernelError,
    RuntimeLifecycleError,
    RuntimePlatformContractError,
    RuntimePlatformError,
    RuntimePlatformServiceError,
    RuntimeServiceRegistryError,
    WorkflowError,
)
from platform.runtime_platform.events import (
    CAPACITY_CHANGED,
    EXECUTION_COMPENSATED,
    EXECUTION_FAILED,
    EXECUTION_REGISTERED,
    EXECUTION_SCHEDULED,
    EXECUTION_STARTED,
    EXECUTION_SUCCEEDED,
    LIFECYCLE_CHANGED,
    RUNTIME_EVENT_CATEGORIES,
    RUNTIME_EVENT_SOURCE,
    WORKFLOW_COMPENSATED,
    WORKFLOW_COMPLETED,
    WORKFLOW_RESOLVED,
    WORKFLOW_STEP_COMPLETED,
    WORKLOAD_PLACED,
    RuntimeEventBus,
    require_category,
)
from platform.runtime_platform.execution import (
    EXECUTION_RECORD_FORMAT,
    ExecutionEngine,
    ExecutionRecord,
    ExecutionRequest,
)
from platform.runtime_platform.health import (
    DEGRADED,
    HEALTH_FORMAT,
    HEALTH_STATES,
    HEALTHY,
    UNHEALTHY,
    HealthCheckResult,
    RuntimePlatformHealth,
    RuntimePlatformHealthReport,
)
from platform.runtime_platform.infrastructure import (
    DEFAULT_PARTITIONS,
    DEFAULT_SLOTS_PER_PARTITION,
    INFRASTRUCTURE_FORMAT,
    CapacityPosture,
    PlacementDecision,
    RuntimeInfrastructure,
)
from platform.runtime_platform.lifecycle import (
    CANCELLED,
    COMPENSATED,
    EXECUTION_STATES,
    FAILED,
    LIFECYCLE_FORMAT,
    LIFECYCLE_TRANSITIONS,
    PENDING,
    PLACED,
    RUNNING,
    SCHEDULED,
    SETTLED_STATES,
    SUCCEEDED,
    TERMINAL_STATES,
    allowed_transitions,
    can_transition,
    is_settled,
    is_terminal,
    require_state,
    require_transition,
    validate_trajectory,
)
from platform.runtime_platform.registry import (
    EXECUTION_REGISTRY_FORMAT,
    GENESIS_HASH,
    ExecutionLedgerEntry,
    ExecutionLineageView,
    ExecutionRegistry,
)
from platform.runtime_platform.scheduling import (
    EXECUTION_SCHEDULE_FORMAT,
    ExecutionSchedule,
    ScheduledStep,
    schedule,
)
from platform.runtime_platform.service import (
    RuntimePlatformEvidence,
    RuntimePlatformService,
    build_runtime_platform_service,
)
from platform.runtime_platform.services import (
    RuntimeServiceCatalog,
    runtime_service_descriptor,
    runtime_service_descriptors,
)
from platform.runtime_platform.workflow import (
    WORKFLOW_PLAN_FORMAT,
    WORKFLOW_RUN_FORMAT,
    WorkflowDefinition,
    WorkflowPlan,
    WorkflowRunner,
    WorkflowRunRecord,
    WorkflowStep,
)

__all__ = [
    # contracts / vocabulary
    "RUNTIME_PLATFORM_CONTRACT_VERSION",
    "RUNTIME_PLATFORM_GROUP",
    "RUNTIME_PLATFORM_CONTRACTS",
    "CONSUMED_CONTRACTS",
    "ConsumedCapability",
    "RuntimeServiceKind",
    "RuntimeServiceView",
    "RuntimePlatformAction",
    "WorkloadAttestation",
    "all_runtime_service_kinds",
    "runtime_platform_contract",
    "default_runtime_platform_contracts",
    # lifecycle
    "LIFECYCLE_FORMAT",
    "PENDING",
    "SCHEDULED",
    "PLACED",
    "RUNNING",
    "SUCCEEDED",
    "FAILED",
    "COMPENSATED",
    "CANCELLED",
    "EXECUTION_STATES",
    "TERMINAL_STATES",
    "SETTLED_STATES",
    "LIFECYCLE_TRANSITIONS",
    "require_state",
    "allowed_transitions",
    "is_terminal",
    "is_settled",
    "can_transition",
    "require_transition",
    "validate_trajectory",
    # events
    "RUNTIME_EVENT_SOURCE",
    "RUNTIME_EVENT_CATEGORIES",
    "EXECUTION_SCHEDULED",
    "WORKLOAD_PLACED",
    "EXECUTION_STARTED",
    "EXECUTION_SUCCEEDED",
    "EXECUTION_FAILED",
    "EXECUTION_COMPENSATED",
    "EXECUTION_REGISTERED",
    "LIFECYCLE_CHANGED",
    "WORKFLOW_RESOLVED",
    "WORKFLOW_STEP_COMPLETED",
    "WORKFLOW_COMPLETED",
    "WORKFLOW_COMPENSATED",
    "CAPACITY_CHANGED",
    "require_category",
    "RuntimeEventBus",
    # infrastructure
    "INFRASTRUCTURE_FORMAT",
    "DEFAULT_PARTITIONS",
    "DEFAULT_SLOTS_PER_PARTITION",
    "CapacityPosture",
    "PlacementDecision",
    "RuntimeInfrastructure",
    # scheduling
    "EXECUTION_SCHEDULE_FORMAT",
    "ScheduledStep",
    "ExecutionSchedule",
    "schedule",
    # execution
    "EXECUTION_RECORD_FORMAT",
    "ExecutionRequest",
    "ExecutionRecord",
    "ExecutionEngine",
    # workflow
    "WORKFLOW_PLAN_FORMAT",
    "WORKFLOW_RUN_FORMAT",
    "WorkflowStep",
    "WorkflowPlan",
    "WorkflowDefinition",
    "WorkflowRunRecord",
    "WorkflowRunner",
    # registry
    "EXECUTION_REGISTRY_FORMAT",
    "GENESIS_HASH",
    "ExecutionLedgerEntry",
    "ExecutionLineageView",
    "ExecutionRegistry",
    # services
    "RuntimeServiceCatalog",
    "runtime_service_descriptor",
    "runtime_service_descriptors",
    # core
    "RUNTIME_KERNEL_FORMAT",
    "RuntimeKernel",
    # service
    "RuntimePlatformEvidence",
    "RuntimePlatformService",
    "build_runtime_platform_service",
    # health
    "HEALTHY",
    "DEGRADED",
    "UNHEALTHY",
    "HEALTH_STATES",
    "HEALTH_FORMAT",
    "HealthCheckResult",
    "RuntimePlatformHealthReport",
    "RuntimePlatformHealth",
    # bootstrap
    "RUNTIME_PLATFORM_BOOTSTRAP_EVENT",
    "bootstrap_runtime_platform",
    # errors
    "RuntimePlatformError",
    "RuntimePlatformContractError",
    "RuntimeServiceRegistryError",
    "ExecutionRequestError",
    "ExecutionScheduleError",
    "ExecutionEngineError",
    "WorkflowError",
    "RuntimeEventError",
    "ExecutionRegistryError",
    "RuntimeLifecycleError",
    "RuntimeInfrastructureError",
    "RuntimeAdmissionError",
    "RuntimeKernelError",
    "RuntimePlatformServiceError",
]
