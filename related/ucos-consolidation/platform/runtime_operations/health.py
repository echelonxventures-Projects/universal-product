"""EC2-TASK-000171 — Runtime Operations Health (EC2-EPIC-012).

The runtime-operations runtime's **health integration**. It reuses the certified
Observability Layer's health model (:class:`~platform.observability.health.HealthCheck`,
:class:`~platform.observability.contracts.HealthStatus`) — it defines no new health
machinery — and computes a deterministic health probe over the operation registry, the
append-only ledger, and the EC-1 façade. Four critical checks back go-live health
(G1/G5) and operational health under induced fault (OP-C1):

    * ``runtime-operations-registry`` — the operation registry substrate is reachable.
    * ``runtime-operations-ledger-integrity`` — the append-only ledger hash chain verifies
      (tamper-evident); a broken chain drives this check ``UNHEALTHY``.
    * ``runtime-operations-fidelity`` — **every recorded operation's stored descriptor
      equals a fresh EC-1 reproduction over its runtime unit** (the fidelity invariant,
      P6). A record whose stored descriptor diverges from what ``engine.runtime``
      reproduces drives this check ``UNHEALTHY``.
    * ``runtime-operations-reversibility`` — **every rollback operation is provably
      reversible** (IP-08). A rollback whose descriptor fails the reversibility proof
      drives this check ``UNHEALTHY``.

Probing is a pure function of the registry + ledger + the deterministic façade — no I/O,
no wall-clock — so the health verdict is reproducible (P5).
"""

from __future__ import annotations

from platform.observability.contracts import HealthStatus
from platform.observability.health import HealthCheck
from platform.runtime_operations.contracts import RuntimeOperationKind
from platform.runtime_operations.facade import RuntimeFacade
from platform.runtime_operations.ledger import RuntimeOperationLedger
from platform.runtime_operations.operations import RuntimeOperationRegistry
from platform.runtime_operations.reversibility import prove_reversibility

#: The check that the operation registry substrate is reachable (G1).
REGISTRY_CHECK = "runtime-operations-registry"

#: The check that the append-only ledger hash chain verifies (tamper-evident).
LEDGER_CHECK = "runtime-operations-ledger-integrity"

#: The check that every recorded descriptor faithfully reproduces the engine output (P6).
FIDELITY_CHECK = "runtime-operations-fidelity"

#: The check that every rollback operation is provably reversible (IP-08).
REVERSIBILITY_CHECK = "runtime-operations-reversibility"


def runtime_operations_health_checks() -> tuple[HealthCheck, ...]:
    """The runtime-operations runtime health checks (all critical), in stable order."""
    return (
        HealthCheck(
            REGISTRY_CHECK,
            critical=True,
            description="Runtime operation registry substrate reachable.",
        ),
        HealthCheck(
            LEDGER_CHECK,
            critical=True,
            description="Append-only runtime operation ledger hash chain verifies.",
        ),
        HealthCheck(
            FIDELITY_CHECK,
            critical=True,
            description="Every recorded descriptor equals a fresh EC-1 reproduction (P6).",
        ),
        HealthCheck(
            REVERSIBILITY_CHECK,
            critical=True,
            description="Every rollback operation is provably reversible (IP-08).",
        ),
    )


class RuntimeOperationsHealth:
    """A deterministic health probe over the operation registry, the ledger, and the façade."""

    __slots__ = ("_registry", "_ledger", "_facade")

    def __init__(
        self,
        registry: RuntimeOperationRegistry,
        ledger: RuntimeOperationLedger,
        facade: RuntimeFacade,
    ) -> None:
        if not isinstance(registry, RuntimeOperationRegistry):
            raise TypeError("a valid RuntimeOperationRegistry is required")
        if not isinstance(ledger, RuntimeOperationLedger):
            raise TypeError("a valid RuntimeOperationLedger is required")
        if not isinstance(facade, RuntimeFacade):
            raise TypeError("a valid RuntimeFacade is required")
        self._registry = registry
        self._ledger = ledger
        self._facade = facade

    def _fidelity_ok(self, record) -> bool:  # noqa: ANN001 - internal record type
        if record.kind is RuntimeOperationKind.DEPLOY:
            return self._facade.verify_deployment_fidelity(
                record.deployment, record.unit, environment=record.environment
            )
        return self._facade.verify_rollback_fidelity(
            record.rollback,
            record.unit,
            previous=record.previous_unit,
            environment=record.environment,
        )

    def infidelic_operations(self) -> tuple[str, ...]:
        """Operation ids whose stored descriptor diverges from a fresh reproduction (P6)."""
        return tuple(
            record.operation_id for record in self._registry.all() if not self._fidelity_ok(record)
        )

    def irreversible_rollbacks(self) -> tuple[str, ...]:
        """Rollback operation ids whose descriptor fails the reversibility proof (IP-08)."""
        return tuple(
            record.operation_id
            for record in self._registry.by_kind(RuntimeOperationKind.ROLLBACK)
            if not prove_reversibility(record.rollback).reversible
        )

    def probe(self) -> dict[str, HealthStatus]:
        """Compute deterministic probe results for the runtime-operations health checks."""
        ledger_ok = self._ledger.verify()
        fidelity_ok = not self.infidelic_operations()
        reversibility_ok = not self.irreversible_rollbacks()
        return {
            REGISTRY_CHECK: HealthStatus.HEALTHY,
            LEDGER_CHECK: (HealthStatus.HEALTHY if ledger_ok else HealthStatus.UNHEALTHY),
            FIDELITY_CHECK: (HealthStatus.HEALTHY if fidelity_ok else HealthStatus.UNHEALTHY),
            REVERSIBILITY_CHECK: (
                HealthStatus.HEALTHY if reversibility_ok else HealthStatus.UNHEALTHY
            ),
        }

    @property
    def healthy(self) -> bool:
        """True iff every runtime-operations health check is HEALTHY."""
        return all(status is HealthStatus.HEALTHY for status in self.probe().values())


__all__ = [
    "REGISTRY_CHECK",
    "LEDGER_CHECK",
    "FIDELITY_CHECK",
    "REVERSIBILITY_CHECK",
    "runtime_operations_health_checks",
    "RuntimeOperationsHealth",
]
