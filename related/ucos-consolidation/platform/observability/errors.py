"""EC2-TASK-000177 — Platform Observability error taxonomy (EC2-EPIC-013).

The Observability Platform **reuses** the EC-2 Platform Foundation error discipline
(EC2-TASK-000055) additively — every observability error is rooted in
:class:`~platform.foundation.errors.PlatformError` (itself rooted in the certified
EC-1 :class:`~engine.foundation.obs.errors.FoundationError`), carries a stable,
category-prefixed ``code`` (``EC2-OBS-*``) and structured, **non-secret** ``context``
so every failure is auditable (PL-02, IP-12, PC-16) and machine-consumable by
TRACK-001.

The Observability Platform is *additive over EC-1 and over the Platform Foundation*:
it consumes both only through published contracts, modifies neither, and never
writes to the certified corpus (DP-03). A malformed observability contract, metric,
log entry, span, health check, alert rule, or audit event fails loudly and
fail-closed with a specific error. Secrets are never recorded (SEC-04).
"""

from __future__ import annotations

from platform.foundation.errors import PlatformError


class ObservabilityError(PlatformError):
    """Base class for all EC-2 Observability Platform errors."""

    code = "EC2-OBS-200"


class ObservabilityContractError(ObservabilityError):
    """An observability contract is malformed or violates versioning (AR-03/PL-05)."""

    code = "EC2-OBS-CONTRACT-001"


class MetricError(ObservabilityError):
    """A metric sample is malformed or a metric operation is invalid."""

    code = "EC2-OBS-METRIC-001"


class LogError(ObservabilityError):
    """A structured log entry is malformed (fail-closed)."""

    code = "EC2-OBS-LOG-001"


class TraceError(ObservabilityError):
    """A span/trace record is malformed or a span operation is invalid."""

    code = "EC2-OBS-TRACE-001"


class HealthError(ObservabilityError):
    """A health check is malformed or a health registration is invalid."""

    code = "EC2-OBS-HEALTH-001"


class AlertError(ObservabilityError):
    """An alert rule or alert-engine operation is malformed (fail-closed)."""

    code = "EC2-OBS-ALERT-001"


class AuditError(ObservabilityError):
    """An audit event or audit-trail operation is malformed (fail-closed)."""

    code = "EC2-OBS-AUDIT-001"


class ObservabilityServiceError(ObservabilityError):
    """The observability service could not be composed or bound (fail-closed)."""

    code = "EC2-OBS-SERVICE-001"


__all__ = [
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
