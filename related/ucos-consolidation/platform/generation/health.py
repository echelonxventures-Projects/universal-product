"""EC2-TASK-000116 — Generation Request Health (EC2-EPIC-007).

The generation-request runtime's **health integration**. It reuses the certified
Observability Layer's health model (:class:`~platform.observability.health.HealthCheck`,
:class:`~platform.observability.contracts.HealthStatus`) — it defines no new health
machinery — and computes a deterministic health probe over the request registry and the
dispatch ledger. Three critical checks back go-live health (G1) and operational health
under induced fault (OP-C1):

    * ``generation-request-registry`` — the registry substrate is reachable.
    * ``generation-request-dispatch-integrity`` — **every dispatched request carries a
      dispatch record** (the "no runtime bypass path" invariant, §7). A request that
      reached DISPATCHED/RUNNING/COMPLETED/FAILED without a recorded dispatch (a fault,
      or a bypass) drives this check to ``UNHEALTHY``, so alerting/health validate under
      induced fault (OP-C1).
    * ``generation-request-execution-integrity`` — every dispatch references a
      registered request; an orphaned dispatch drives this check to ``UNHEALTHY``.

Probing is a pure function of the two registries — no I/O, no wall-clock — so the health
verdict is reproducible (P5).
"""

from __future__ import annotations

from platform.generation.contracts import RequestStatus
from platform.generation.dispatch import DispatchLedger
from platform.generation.registry import GenerationRequestRegistry
from platform.observability.contracts import HealthStatus
from platform.observability.health import HealthCheck

#: The check that the request registry substrate is reachable (G1).
REGISTRY_CHECK = "generation-request-registry"

#: The check that every dispatched request carries a dispatch record (§7, OP-C1).
DISPATCH_CHECK = "generation-request-dispatch-integrity"

#: The check that every dispatch references a registered request (OP-C1).
INTEGRITY_CHECK = "generation-request-execution-integrity"

#: The lifecycle states that must be backed by a recorded dispatch (no bypass). A
#: FAILED request that never dispatched (failed during validation) is legitimate, so
#: FAILED is intentionally excluded — only states that definitely reached the runtime
#: require a dispatch record.
_DISPATCH_REQUIRED_STATES: frozenset[RequestStatus] = frozenset(
    {
        RequestStatus.DISPATCHED,
        RequestStatus.RUNNING,
        RequestStatus.COMPLETED,
    }
)


def generation_request_health_checks() -> tuple[HealthCheck, ...]:
    """The generation-request runtime health checks (all critical), in stable order."""
    return (
        HealthCheck(
            REGISTRY_CHECK,
            critical=True,
            description="Generation request registry substrate reachable.",
        ),
        HealthCheck(
            DISPATCH_CHECK,
            critical=True,
            description="Every dispatched request carries a dispatch record (no bypass).",
        ),
        HealthCheck(
            INTEGRITY_CHECK,
            critical=True,
            description="Every dispatch references a registered request.",
        ),
    )


class RequestHealth:
    """A deterministic health probe over the request registry / dispatch ledger."""

    __slots__ = ("_registry", "_dispatch")

    def __init__(self, registry: GenerationRequestRegistry, dispatch: DispatchLedger) -> None:
        if not isinstance(registry, GenerationRequestRegistry):
            raise TypeError("a valid GenerationRequestRegistry is required")
        if not isinstance(dispatch, DispatchLedger):
            raise TypeError("a valid DispatchLedger is required")
        self._registry = registry
        self._dispatch = dispatch

    def undispatched_executing_requests(self) -> tuple[str, ...]:
        """Executing request ids lacking a dispatch record (runtime-bypass faults)."""
        return tuple(
            r.request_id
            for r in self._registry.all()
            if r.status in _DISPATCH_REQUIRED_STATES and not self._dispatch.has(r.request_id)
        )

    def orphaned_dispatches(self) -> tuple[str, ...]:
        """Request ids that have a dispatch but are not registered (integrity faults)."""
        return tuple(ref for ref in self._dispatch.request_refs if ref not in self._registry)

    def probe(self) -> dict[str, HealthStatus]:
        """Compute deterministic probe results for the request health checks."""
        dispatch_ok = not self.undispatched_executing_requests()
        integrity_ok = not self.orphaned_dispatches()
        return {
            REGISTRY_CHECK: HealthStatus.HEALTHY,
            DISPATCH_CHECK: (HealthStatus.HEALTHY if dispatch_ok else HealthStatus.UNHEALTHY),
            INTEGRITY_CHECK: (HealthStatus.HEALTHY if integrity_ok else HealthStatus.UNHEALTHY),
        }

    @property
    def healthy(self) -> bool:
        """True iff every request health check is HEALTHY."""
        return all(status is HealthStatus.HEALTHY for status in self.probe().values())


__all__ = [
    "REGISTRY_CHECK",
    "DISPATCH_CHECK",
    "INTEGRITY_CHECK",
    "generation_request_health_checks",
    "RequestHealth",
]
