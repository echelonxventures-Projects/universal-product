"""EPIC-007 (Terminal T7) — Universal Runtime Platform error taxonomy.

The UCOS **Universal Runtime Platform** (URP) — the operational runtime plane that
governs the scheduling, placement, lifecycle, workflow orchestration, and event flow
of governed executions — reuses the EC-1 / Platform Foundation error discipline
additively; it does not fork or modify it. Every runtime-platform error is rooted in
:class:`~platform.foundation.errors.PlatformError` (itself rooted in the certified EC-1
:class:`~engine.foundation.obs.errors.FoundationError`), carries a stable,
category-prefixed ``code`` (``EC2-URP-*``) and structured, non-secret ``context`` so
failures are auditable (PL-02, IP-12) and machine-consumable.

The Universal Runtime Platform is *additive* over EC-1, the Platform Foundation
(events, services, contracts), and the certified upstream engines it consumes **by
reference** — Registry (``engine.registry.read``), Knowledge, Measurement, Validation,
and Certification. It **governs and records only**: it schedules, places, transitions,
and orchestrates *recorded* execution structures deterministically; it invokes no live
compute and starts no server. Every admission decision is **fail-closed**: only a
workload attested VALIDATED and CERTIFIED by the upstream engines may be admitted for
execution. The execution registry is append-only by construction — the platform
exposes no mutation or deletion path — and it never writes to the certified corpus
(DP-03).
"""

from __future__ import annotations

from platform.foundation.errors import PlatformError


class RuntimePlatformError(PlatformError):
    """Base class for all EPIC-007 Universal Runtime Platform errors."""

    code = "EC2-URP-000"


class RuntimePlatformContractError(RuntimePlatformError):
    """A runtime-platform contract, view, or vocabulary declaration is malformed."""

    code = "EC2-URP-CONTRACT-001"


class RuntimeServiceRegistryError(RuntimePlatformError):
    """A runtime service could not be declared, discovered, or resolved (duplicate/absent)."""

    code = "EC2-URP-SERVICE-001"


class ExecutionRequestError(RuntimePlatformError):
    """An execution request is malformed (missing workload, bad dependency, bad priority)."""

    code = "EC2-URP-REQUEST-001"


class ExecutionScheduleError(RuntimePlatformError):
    """An execution schedule could not be derived (missing dependency or dependency cycle)."""

    code = "EC2-URP-SCHEDULE-001"


class ExecutionEngineError(RuntimePlatformError):
    """A modelled execution could not be run (illegal trajectory or malformed request)."""

    code = "EC2-URP-EXECUTION-001"


class WorkflowError(RuntimePlatformError):
    """A workflow definition, resolution, or saga run is malformed or non-resolvable."""

    code = "EC2-URP-WORKFLOW-001"


class RuntimeEventError(RuntimePlatformError):
    """A runtime event or event-bus operation is malformed (unknown category, bad handler)."""

    code = "EC2-URP-EVENT-001"


class ExecutionRegistryError(RuntimePlatformError):
    """An execution-registry append, traversal, or lineage request is malformed."""

    code = "EC2-URP-REGISTRY-001"


class RuntimeLifecycleError(RuntimePlatformError):
    """An illegal or unknown execution-lifecycle transition was requested (fail-closed)."""

    code = "EC2-URP-LIFECYCLE-001"


class RuntimeInfrastructureError(RuntimePlatformError):
    """A capacity posture or workload-placement request is malformed."""

    code = "EC2-URP-INFRA-001"


class RuntimeAdmissionError(RuntimePlatformError):
    """A workload was refused admission — not VALIDATED and CERTIFIED upstream (fail-closed)."""

    code = "EC2-URP-ADMISSION-001"


class RuntimeKernelError(RuntimePlatformError):
    """The runtime kernel could not be composed or a kernel operation is malformed."""

    code = "EC2-URP-KERNEL-001"


class RuntimePlatformServiceError(RuntimePlatformError):
    """The runtime-platform service could not be composed or an operation is malformed."""

    code = "EC2-URP-PLATFORM-001"


__all__ = [
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
