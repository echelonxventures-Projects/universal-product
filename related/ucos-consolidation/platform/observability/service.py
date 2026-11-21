"""EC2-TASK-000185 — Observability Service (EC2-EPIC-013).

The single, governed **observability composition point** (L8 Operations of the
Program architecture) that composes the whole Observability Platform into one entry
point:

    MetricRegistry · LogBuffer · TraceRecorder · HealthRegistry · AlertEngine · AuditTrail

Its central guarantee is **structured telemetry on 100% of governed actions**
(acceptance P9; go-live G8): when bound to the Platform Foundation
:class:`~platform.foundation.events.EventBus`, the service subscribes to *every*
published :class:`~platform.foundation.events.PlatformEvent` and, for each one,
records a metric, a structured log entry, **and** an append-only audit event. Because
the foundation event bus is the seam through which every EC-2 governed action is
published, subscribing to it yields complete, append-only coverage by construction.

The service is deterministic: the same registrations and the same ordered sequence
of governed events yield the same :class:`ObservabilityEvidence` fingerprint. It
holds no secret material (SEC-04), starts no server, and opens no socket — it is the
reusable substrate later operational epics build on.

This module also provides the registry-driven composition helpers
:func:`build_observability_service` (default wiring) and
:func:`bootstrap_observability` (binds to a
:class:`~platform.foundation.bootstrap.PlatformContext`, publishes the six
observability contracts into the foundation service registry, subscribes to the
event bus, and emits a composition event).
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from platform.foundation.contracts import content_hash
from platform.foundation.events import EventBus, PlatformEvent
from platform.observability.alerting import Alert, AlertEngine, AlertRule
from platform.observability.audit import AuditTrail
from platform.observability.contracts import (
    OBSERVABILITY_CONTRACTS,
    HealthStatus,
    default_observability_contracts,
)
from platform.observability.errors import ObservabilityServiceError
from platform.observability.health import HealthCheck, HealthRegistry
from platform.observability.logs import LogBuffer
from platform.observability.metrics import MetricRegistry
from platform.observability.traces import TraceRecorder
from typing import Any

#: The event emitted when the Observability Platform is composed onto a context.
OBSERVABILITY_BOOTSTRAP_EVENT = "observability.bootstrap.completed"

#: The metric name incremented once for every governed action observed.
GOVERNED_ACTION_METRIC = "platform.governed_actions"

#: The audit action recorded for every observed governed event.
GOVERNED_ACTION = "governed-action-observed"


@dataclass(frozen=True, slots=True)
class ObservabilityEvidence:
    """A deterministic, content-addressed record of observability state (evidence).

    Aggregates the subsystem fingerprints and the governed-action count into a single
    reproducible evidence object suitable for audit and TRACK-001.
    """

    metrics_fingerprint: str
    logs_fingerprint: str
    traces_fingerprint: str
    alerts_fingerprint: str
    audit_fingerprint: str
    governed_action_count: int
    audit_chain_intact: bool
    evidence_id: str = ""

    @classmethod
    def create(
        cls,
        *,
        metrics_fingerprint: str,
        logs_fingerprint: str,
        traces_fingerprint: str,
        alerts_fingerprint: str,
        audit_fingerprint: str,
        governed_action_count: int,
        audit_chain_intact: bool,
    ) -> ObservabilityEvidence:
        core = {
            "metrics_fingerprint": metrics_fingerprint,
            "logs_fingerprint": logs_fingerprint,
            "traces_fingerprint": traces_fingerprint,
            "alerts_fingerprint": alerts_fingerprint,
            "audit_fingerprint": audit_fingerprint,
            "governed_action_count": governed_action_count,
            "audit_chain_intact": audit_chain_intact,
        }
        return cls(
            metrics_fingerprint=metrics_fingerprint,
            logs_fingerprint=logs_fingerprint,
            traces_fingerprint=traces_fingerprint,
            alerts_fingerprint=alerts_fingerprint,
            audit_fingerprint=audit_fingerprint,
            governed_action_count=governed_action_count,
            audit_chain_intact=audit_chain_intact,
            evidence_id=f"UCOS-OBEV-{content_hash(core)[:16]}",
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "evidence_id": self.evidence_id,
            "metrics_fingerprint": self.metrics_fingerprint,
            "logs_fingerprint": self.logs_fingerprint,
            "traces_fingerprint": self.traces_fingerprint,
            "alerts_fingerprint": self.alerts_fingerprint,
            "audit_fingerprint": self.audit_fingerprint,
            "governed_action_count": self.governed_action_count,
            "audit_chain_intact": self.audit_chain_intact,
        }

    def fingerprint(self) -> str:
        return content_hash(self.to_dict())


class ObservabilityService:
    """The governed L8 composition point for the Observability Platform."""

    __slots__ = (
        "_metrics",
        "_logs",
        "_traces",
        "_health",
        "_alerts",
        "_audit",
        "_events",
        "_observed",
        "_subscribed",
        "_baseline",
    )

    def __init__(
        self,
        *,
        metrics: MetricRegistry,
        logs: LogBuffer,
        traces: TraceRecorder,
        health: HealthRegistry,
        alerts: AlertEngine,
        audit: AuditTrail,
        events: EventBus | None = None,
    ) -> None:
        if not isinstance(metrics, MetricRegistry):
            raise ObservabilityServiceError("a valid MetricRegistry is required")
        if not isinstance(logs, LogBuffer):
            raise ObservabilityServiceError("a valid LogBuffer is required")
        if not isinstance(traces, TraceRecorder):
            raise ObservabilityServiceError("a valid TraceRecorder is required")
        if not isinstance(health, HealthRegistry):
            raise ObservabilityServiceError("a valid HealthRegistry is required")
        if not isinstance(alerts, AlertEngine):
            raise ObservabilityServiceError("a valid AlertEngine is required")
        if not isinstance(audit, AuditTrail):
            raise ObservabilityServiceError("a valid AuditTrail is required")
        if events is not None and not isinstance(events, EventBus):
            raise ObservabilityServiceError("events must be an EventBus when provided")
        self._metrics = metrics
        self._logs = logs
        self._traces = traces
        self._health = health
        self._alerts = alerts
        self._audit = audit
        self._events = events
        self._observed = 0
        self._subscribed = False
        self._baseline = 0
        if events is not None:
            self.bind(events)

    # -- component access -------------------------------------------------------

    @property
    def metrics(self) -> MetricRegistry:
        return self._metrics

    @property
    def logs(self) -> LogBuffer:
        return self._logs

    @property
    def traces(self) -> TraceRecorder:
        return self._traces

    @property
    def health(self) -> HealthRegistry:
        return self._health

    @property
    def alerts(self) -> AlertEngine:
        return self._alerts

    @property
    def audit(self) -> AuditTrail:
        return self._audit

    @property
    def governed_action_count(self) -> int:
        """The number of governed actions observed off the event bus."""
        return self._observed

    # -- binding: 100% governed-action coverage --------------------------------

    def bind(self, events: EventBus) -> None:
        """Subscribe to the foundation event bus (idempotent, fail-closed).

        After binding, every subsequently published :class:`PlatformEvent` is
        recorded as a metric, a log entry, and an append-only audit event — the
        mechanism that delivers structured telemetry on 100% of governed actions.
        """
        if not isinstance(events, EventBus):
            raise ObservabilityServiceError("bind requires an EventBus")
        if self._subscribed and self._events is events:
            return
        self._events = events
        self._baseline = len(events)
        events.subscribe(self._observe)
        self._subscribed = True

    def _observe(self, event: PlatformEvent) -> None:
        """Record telemetry for one governed action (metric + log + audit)."""
        self._observed += 1
        self._metrics.counter(GOVERNED_ACTION_METRIC, 1.0, event_type=event.event_type)
        self._logs.info(
            event.source,
            f"governed-action:{event.event_type}",
            event_id=event.event_id,
            subject=event.subject,
        )
        self._audit.record(
            GOVERNED_ACTION,
            event.source,
            event.subject,
            detail={"event_type": event.event_type, "event_id": event.event_id},
        )

    # -- convenience registration ----------------------------------------------

    def register_health_check(self, check: HealthCheck) -> HealthCheck:
        return self._health.register(check)

    def register_alert_rule(self, rule: AlertRule) -> AlertRule:
        return self._alerts.register(rule)

    def health_endpoint(self, results: Mapping[str, HealthStatus]) -> dict[str, Any]:
        """The live health-endpoint view over supplied probe ``results`` (G1)."""
        return self._health.endpoint(results)

    def evaluate_alerts(self, observation: Mapping[str, Any]) -> tuple[Alert, ...]:
        """Evaluate registered alert rules against ``observation`` (G8/P9)."""
        return self._alerts.evaluate(observation)

    def observed_fraction(self) -> float:
        """Fraction of governed actions published *while bound* that were observed.

        Measured against events published after :meth:`bind` (pre-binding events are
        outside this service's responsibility). Returns ``1.0`` when no governed
        action has occurred since binding (vacuously complete) and ``0.0`` when the
        service is unbound. A value of ``1.0`` evidences telemetry on 100% of
        governed actions (acceptance P9).
        """
        if self._events is None:
            return 0.0
        total = len(self._events) - self._baseline
        if total <= 0:
            return 1.0
        return self._observed / total

    # -- evidence ---------------------------------------------------------------

    def evidence(self) -> ObservabilityEvidence:
        """Produce deterministic Observability Evidence over all subsystems."""
        return ObservabilityEvidence.create(
            metrics_fingerprint=self._metrics.fingerprint(),
            logs_fingerprint=self._logs.fingerprint(),
            traces_fingerprint=self._traces.fingerprint(),
            alerts_fingerprint=self._alerts.fingerprint(),
            audit_fingerprint=self._audit.fingerprint(),
            governed_action_count=self._observed,
            audit_chain_intact=self._audit.verify(),
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "metrics": self._metrics.snapshot(),
            "logs": self._logs.to_dict(),
            "traces": self._traces.to_dict(),
            "health": self._health.to_dict(),
            "alerts": self._alerts.to_dict(),
            "audit": self._audit.to_dict(),
            "governed_action_count": self._observed,
            "evidence": self.evidence().to_dict(),
        }


def build_observability_service(*, events: EventBus | None = None) -> ObservabilityService:
    """Default, registry-driven composition of the Observability Platform.

    Wires fresh metric registry, log buffer, trace recorder, health registry, alert
    engine, and audit trail into an :class:`ObservabilityService`. When an event bus
    is supplied the service binds to it immediately (100% governed-action coverage).
    """
    return ObservabilityService(
        metrics=MetricRegistry(),
        logs=LogBuffer(),
        traces=TraceRecorder(),
        health=HealthRegistry(),
        alerts=AlertEngine(),
        audit=AuditTrail(),
        events=events,
    )


def bootstrap_observability(context: Any) -> ObservabilityService:
    """Compose the Observability Platform onto a :class:`PlatformContext`.

    Publishes the six observability contracts into the foundation service registry
    (EC2-EPIC-001), binds the service to the context event bus (so all subsequent
    governed actions are captured), and emits a deterministic
    ``observability.bootstrap.completed`` event. The parameter is typed loosely to
    avoid a hard import cycle on the foundation bootstrap module.
    """
    from platform.foundation.services import ServiceDescriptor

    service = build_observability_service(events=context.events)

    contracts = {c.name: c for c in default_observability_contracts()}
    for ref in OBSERVABILITY_CONTRACTS:
        if ref.name in context.services:
            continue
        capabilities = ("PC-16",) if "audit" in ref.name else ("PC-12",)
        context.services.register(
            ServiceDescriptor(
                name=ref.name,
                contract=contracts[ref.name],
                capabilities=capabilities,
                description=f"Observability Platform service: {ref.name}.",
            ),
            provider=lambda svc=service: svc,
        )

    context.events.publish(
        OBSERVABILITY_BOOTSTRAP_EVENT,
        source="platform.observability.bootstrap",
        subject=context.program_id,
        payload={
            "observability_contracts": [ref.name for ref in OBSERVABILITY_CONTRACTS],
            "metric_source": GOVERNED_ACTION_METRIC,
        },
    )
    return service


__all__ = [
    "OBSERVABILITY_BOOTSTRAP_EVENT",
    "GOVERNED_ACTION_METRIC",
    "GOVERNED_ACTION",
    "ObservabilityEvidence",
    "ObservabilityService",
    "build_observability_service",
    "bootstrap_observability",
]
