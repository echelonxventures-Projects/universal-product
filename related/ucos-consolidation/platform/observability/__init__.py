"""UCOS EC-2 Platform Observability & Monitoring (EC2-EPIC-013) — L8 Operations.

The Observability & Monitoring layer of the EC-2 Platform (L8 Operations of the
Program architecture, §4). It provides real-time metrics, logs, traces, health, and
alerting across the platform and pipeline, plus an append-only audit trail — as a
strictly **additive** layer over the certified EC-1 engine and the EC-2 Platform
Foundation (EC2-EPIC-001): it consumes both only through published contracts,
modifies neither, never writes to the certified corpus (DP-03), remains
deterministic, is registry/contract-driven, and preserves every EC-1 certification.

Deliverables (EC2-TASK-000177…000186):
    * **errors** (TASK-000177) — the ``EC2-OBS-*`` error taxonomy over ``PlatformError``.
    * **contracts** (TASK-000178) — the versioned observability contract surface plus
      the core vocabulary: ``MetricKind``, ``Severity``, ``HealthStatus``.
    * **metrics** (TASK-000179) — the deterministic ``MetricRegistry`` (reuses EC-1
      telemetry) + ``MetricSample``.
    * **logs** (TASK-000180) — the append-only ``LogBuffer`` (reuses EC-1 structured
      logging) + ``LogEntry``.
    * **traces** (TASK-000181) — the ``TraceRecorder`` (reuses EC-1 spans) + ``SpanRecord``.
    * **health** (TASK-000182) — ``HealthCheck`` / ``HealthRegistry`` + the live
      health endpoint (G1).
    * **alerting** (TASK-000183) — ``AlertRule`` / ``AlertEngine`` (fire on defined
      conditions, G8/P9).
    * **audit** (TASK-000184) — the hash-chained, append-only ``AuditTrail`` (P9/PC-16).
    * **service** (TASK-000185) — the ``ObservabilityService`` composition root that
      delivers structured telemetry on 100% of governed actions, ``ObservabilityEvidence``,
      and ``bootstrap_observability``.

This epic is **observability services only**: no UI, portal, dashboard, or runtime
operation is implemented here. It carries no constitutional authority; the external
gates (EC-1…EC-6) remain open.
"""

from __future__ import annotations

from platform.observability.alerting import (
    Alert,
    AlertEngine,
    AlertPredicate,
    AlertRule,
)
from platform.observability.audit import (
    GENESIS_HASH,
    AuditEvent,
    AuditTrail,
)
from platform.observability.contracts import (
    OBSERVABILITY_CONTRACT_VERSION,
    OBSERVABILITY_CONTRACTS,
    HealthStatus,
    MetricKind,
    Severity,
    all_metric_kinds,
    all_severities,
    default_observability_contracts,
    observability_contract,
)
from platform.observability.errors import (
    AlertError,
    AuditError,
    HealthError,
    LogError,
    MetricError,
    ObservabilityContractError,
    ObservabilityError,
    ObservabilityServiceError,
    TraceError,
)
from platform.observability.health import (
    HealthCheck,
    HealthRegistry,
    HealthReport,
    HealthResult,
)
from platform.observability.logs import LogBuffer, LogEntry
from platform.observability.metrics import MetricRegistry, MetricSample
from platform.observability.service import (
    GOVERNED_ACTION,
    GOVERNED_ACTION_METRIC,
    OBSERVABILITY_BOOTSTRAP_EVENT,
    ObservabilityEvidence,
    ObservabilityService,
    bootstrap_observability,
    build_observability_service,
)
from platform.observability.traces import SpanRecord, TraceRecorder

__all__ = [
    # contracts (TASK-000178)
    "OBSERVABILITY_CONTRACT_VERSION",
    "OBSERVABILITY_CONTRACTS",
    "MetricKind",
    "Severity",
    "HealthStatus",
    "all_severities",
    "all_metric_kinds",
    "observability_contract",
    "default_observability_contracts",
    # metrics (TASK-000179)
    "MetricSample",
    "MetricRegistry",
    # logs (TASK-000180)
    "LogEntry",
    "LogBuffer",
    # traces (TASK-000181)
    "SpanRecord",
    "TraceRecorder",
    # health (TASK-000182)
    "HealthCheck",
    "HealthResult",
    "HealthReport",
    "HealthRegistry",
    # alerting (TASK-000183)
    "AlertPredicate",
    "AlertRule",
    "Alert",
    "AlertEngine",
    # audit (TASK-000184)
    "GENESIS_HASH",
    "AuditEvent",
    "AuditTrail",
    # service (TASK-000185)
    "OBSERVABILITY_BOOTSTRAP_EVENT",
    "GOVERNED_ACTION_METRIC",
    "GOVERNED_ACTION",
    "ObservabilityEvidence",
    "ObservabilityService",
    "build_observability_service",
    "bootstrap_observability",
    # errors (TASK-000177)
    "ObservabilityError",
    "ObservabilityContractError",
    "MetricError",
    "LogError",
    "TraceError",
    "HealthError",
    "AlertError",
    "AuditError",
    "ObservabilityServiceError",
]
