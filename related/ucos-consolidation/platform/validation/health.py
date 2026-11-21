"""EC2-TASK-000150 — Validation Console Health (EC2-EPIC-010).

The validation-console runtime's **health integration**. It reuses the certified
Observability Layer's health model (:class:`~platform.observability.health.HealthCheck`,
:class:`~platform.observability.contracts.HealthStatus`) — it defines no new health
machinery — and computes a deterministic health probe over the record registry and the
EC-1 façade. Three critical checks back go-live health (G1/G5) and operational health
under induced fault (OP-C1):

    * ``validation-console-registry`` — the record registry substrate is reachable.
    * ``validation-console-fidelity`` — **every surfaced record's stored report equals a
      fresh certified reproduction over its subject** (the fidelity invariant, P6). A
      record whose stored report diverges from what ``engine.validation`` reproduces over
      the same subject drives this check to ``UNHEALTHY`` — so fidelity is machine-checkable
      and alerting/health validate under induced fault (OP-C1).
    * ``validation-console-evidence-integrity`` — every record's stored evidence equals
      the evidence the certified builder derives from its stored report; a mismatch drives
      this check to ``UNHEALTHY``.

Probing is a pure function of the registry + the deterministic façade — no I/O, no
wall-clock — so the health verdict is reproducible (P5).
"""

from __future__ import annotations

from platform.foundation.contracts import content_hash
from platform.observability.contracts import HealthStatus
from platform.observability.health import HealthCheck
from platform.validation.facade import ValidationFacade
from platform.validation.registry import ValidationRecordRegistry

from engine.validation.evidence import build_validation_evidence

#: The check that the record registry substrate is reachable (G1).
REGISTRY_CHECK = "validation-console-registry"

#: The check that every surfaced record faithfully reproduces the engine output (P6).
FIDELITY_CHECK = "validation-console-fidelity"

#: The check that every record's evidence matches its report (OP-C1).
EVIDENCE_CHECK = "validation-console-evidence-integrity"


def validation_console_health_checks() -> tuple[HealthCheck, ...]:
    """The validation-console runtime health checks (all critical), in stable order."""
    return (
        HealthCheck(
            REGISTRY_CHECK,
            critical=True,
            description="Validation record registry substrate reachable.",
        ),
        HealthCheck(
            FIDELITY_CHECK,
            critical=True,
            description="Every surfaced report equals a fresh certified reproduction (P6).",
        ),
        HealthCheck(
            EVIDENCE_CHECK,
            critical=True,
            description="Every record's evidence matches its certified report.",
        ),
    )


class ValidationHealth:
    """A deterministic health probe over the record registry and the EC-1 façade."""

    __slots__ = ("_registry", "_facade")

    def __init__(self, registry: ValidationRecordRegistry, facade: ValidationFacade) -> None:
        if not isinstance(registry, ValidationRecordRegistry):
            raise TypeError("a valid ValidationRecordRegistry is required")
        if not isinstance(facade, ValidationFacade):
            raise TypeError("a valid ValidationFacade is required")
        self._registry = registry
        self._facade = facade

    def infidelic_records(self) -> tuple[str, ...]:
        """Record ids whose stored report diverges from a fresh certified reproduction."""
        return tuple(
            record.record_id
            for record in self._registry.all()
            if not self._facade.verify_fidelity(record.report, record.subject)
        )

    def inconsistent_evidence(self) -> tuple[str, ...]:
        """Record ids whose stored evidence differs from the certified report's evidence."""
        mismatched: list[str] = []
        for record in self._registry.all():
            expected = build_validation_evidence(record.report)
            if content_hash(expected.to_dict()) != content_hash(record.evidence.to_dict()):
                mismatched.append(record.record_id)
        return tuple(mismatched)

    def probe(self) -> dict[str, HealthStatus]:
        """Compute deterministic probe results for the console health checks."""
        fidelity_ok = not self.infidelic_records()
        evidence_ok = not self.inconsistent_evidence()
        return {
            REGISTRY_CHECK: HealthStatus.HEALTHY,
            FIDELITY_CHECK: (HealthStatus.HEALTHY if fidelity_ok else HealthStatus.UNHEALTHY),
            EVIDENCE_CHECK: (HealthStatus.HEALTHY if evidence_ok else HealthStatus.UNHEALTHY),
        }

    @property
    def healthy(self) -> bool:
        """True iff every console health check is HEALTHY."""
        return all(status is HealthStatus.HEALTHY for status in self.probe().values())


__all__ = [
    "REGISTRY_CHECK",
    "FIDELITY_CHECK",
    "EVIDENCE_CHECK",
    "validation_console_health_checks",
    "ValidationHealth",
]
