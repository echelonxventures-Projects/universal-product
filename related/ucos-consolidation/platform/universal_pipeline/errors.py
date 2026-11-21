"""UAPF-000001 — Universal Autonomous Pipeline Framework error taxonomy.

UAPF reuses the Platform Foundation error discipline additively; it does not fork or
modify it. Every UAPF error is rooted in
:class:`~platform.foundation.errors.PlatformError` (itself rooted in the certified EC-1
:class:`~engine.foundation.obs.errors.FoundationError`), carries a stable,
category-prefixed ``code`` (``EC2-UAPF-*``) and structured, non-secret ``context`` so
every failure is auditable (PL-02, IP-12) and machine-consumable.

Every UAPF decision is **fail-closed**: an unknown pipeline type, an unregistered event
category, an unregistered stage handler, an unresolvable stage order, a dependency cycle,
an illegal lifecycle transition, a duplicate registration, an unauthorized execution, or
a gateway refusal raises rather than degrading silently. Nothing bypasses the gateway,
so a refusal is an error and never a warning.
"""

from __future__ import annotations

from platform.foundation.errors import PlatformError


class UniversalPipelineError(PlatformError):
    """Base class for every UAPF-000001 Universal Autonomous Pipeline Framework error."""

    code = "EC2-UAPF-000"


class PipelineIdentityError(UniversalPipelineError):
    """A universal identity could not be minted (unknown object kind, malformed tuple)."""

    code = "EC2-UAPF-IDENTITY-001"


class PipelineDefinitionError(UniversalPipelineError):
    """A pipeline, stage, policy, gate, capability or plugin declaration is malformed."""

    code = "EC2-UAPF-DEFINITION-001"


class PipelineTypeError(UniversalPipelineError):
    """An unregistered pipeline type was declared (extension is by registration)."""

    code = "EC2-UAPF-TYPE-001"


class PipelinePlanError(UniversalPipelineError):
    """A pipeline plan could not be derived (unresolvable stage order / declared cycle)."""

    code = "EC2-UAPF-PLAN-001"


class PipelineRegistryError(UniversalPipelineError):
    """A pipeline registration, version chain, traversal or integrity check failed."""

    code = "EC2-UAPF-REGISTRY-001"


class PipelineStateError(UniversalPipelineError):
    """An illegal or unknown execution-unit lifecycle transition was requested."""

    code = "EC2-UAPF-STATE-001"


class PipelineQueueError(UniversalPipelineError):
    """A queue operation is malformed or violates a queue invariant (fail-closed)."""

    code = "EC2-UAPF-QUEUE-001"


class PipelineScheduleError(UniversalPipelineError):
    """A schedule could not be derived (unknown dependency, unresolvable declaration)."""

    code = "EC2-UAPF-SCHEDULE-001"


class PipelineDependencyError(UniversalPipelineError):
    """A dependency declaration is unresolved, cyclic, or closes over an unknown node."""

    code = "EC2-UAPF-DEPENDENCY-001"


class PipelineEventError(UniversalPipelineError):
    """An event category is unregistered, or an event operation is malformed."""

    code = "EC2-UAPF-EVENT-001"


class PipelineGatewayError(UniversalPipelineError):
    """A gateway submission is malformed, or work attempted to bypass the gateway."""

    code = "EC2-UAPF-GATEWAY-001"


class PipelineHandlerError(UniversalPipelineError):
    """A stage handler is unregistered, duplicated, or returned a malformed outcome."""

    code = "EC2-UAPF-HANDLER-001"


class PipelineExecutionError(UniversalPipelineError):
    """An execution unit could not be executed (unauthorized, malformed, or out of order)."""

    code = "EC2-UAPF-EXECUTION-001"


class PipelineValidationError(UniversalPipelineError):
    """A validation or verification request is malformed (the verdict itself is a record)."""

    code = "EC2-UAPF-VALIDATION-001"


class PipelineCertificationError(UniversalPipelineError):
    """A certification request is malformed, or certification was attempted out of order."""

    code = "EC2-UAPF-CERTIFICATION-001"


class PipelineGovernanceError(UniversalPipelineError):
    """A policy, governance obligation, audit entry or recovery point is malformed."""

    code = "EC2-UAPF-GOVERNANCE-001"


class PipelineSecurityError(UniversalPipelineError):
    """A security declaration is malformed, or a required permission is absent."""

    code = "EC2-UAPF-SECURITY-001"


class PipelineObservabilityError(UniversalPipelineError):
    """A metric, telemetry span, health probe or bottleneck query is malformed."""

    code = "EC2-UAPF-OBSERVABILITY-001"


class PipelineDiscoveryError(UniversalPipelineError):
    """A declaration catalogue could not be discovered, parsed, or admitted."""

    code = "EC2-UAPF-DISCOVERY-001"


class PipelineOrchestrationError(UniversalPipelineError):
    """An orchestration tick is malformed, or orchestration state is inconsistent."""

    code = "EC2-UAPF-ORCHESTRATION-001"


class PipelinePlatformError(UniversalPipelineError):
    """The UAPF platform façade could not be composed, or an operation is malformed."""

    code = "EC2-UAPF-PLATFORM-001"


class PipelineExceptionEscalation(UniversalPipelineError):
    """Autonomy halted and human intervention is required (Human Intervention by Exception).

    Raised only for the four conditions Repository Truth reserves to a human decision:
    constitutional ambiguity, conflicting canonical authority, a missing external
    authority, or an explicit human-decision requirement. Everything else continues
    automatically, so this error is the sole autonomy escape hatch and it names its
    reason.
    """

    code = "EC2-UAPF-ESCALATION-001"


__all__ = [
    "UniversalPipelineError",
    "PipelineCertificationError",
    "PipelineDefinitionError",
    "PipelineDependencyError",
    "PipelineDiscoveryError",
    "PipelineEventError",
    "PipelineExceptionEscalation",
    "PipelineExecutionError",
    "PipelineGatewayError",
    "PipelineGovernanceError",
    "PipelineHandlerError",
    "PipelineIdentityError",
    "PipelineObservabilityError",
    "PipelineOrchestrationError",
    "PipelinePlanError",
    "PipelinePlatformError",
    "PipelineQueueError",
    "PipelineRegistryError",
    "PipelineScheduleError",
    "PipelineSecurityError",
    "PipelineStateError",
    "PipelineTypeError",
    "PipelineValidationError",
]
