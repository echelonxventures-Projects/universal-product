"""EC2-TASK-000159 — Certification Console Health (EC2-EPIC-011).

The certification-console runtime's **health integration**. It reuses the certified
Observability Layer's health model (:class:`~platform.observability.health.HealthCheck`,
:class:`~platform.observability.contracts.HealthStatus`) — it defines no new health
machinery — and computes a deterministic health probe over the record registry, the
append-only ledger, and the EC-1 façade. Four critical checks back go-live health
(G1/G5) and operational health under induced fault (OP-C1):

    * ``certification-console-registry`` — the record registry substrate is reachable.
    * ``certification-console-ledger-integrity`` — the append-only ledger hash chain
      verifies (tamper-evident); a broken chain drives this check ``UNHEALTHY``.
    * ``certification-console-fidelity`` — **every surfaced record's stored certification
      record equals a fresh certified reproduction over its validation output** (the
      fidelity invariant, P6). A record whose stored certification diverges from what
      ``engine.certification`` reproduces drives this check ``UNHEALTHY``.
    * ``certification-console-evidence-integrity`` — every record's stored certification
      evidence equals the evidence the certified builder derives from a fresh decision; a
      mismatch drives this check ``UNHEALTHY``.

Probing is a pure function of the registry + ledger + the deterministic façade — no I/O,
no wall-clock — so the health verdict is reproducible (P5).
"""

from __future__ import annotations

from platform.certification.facade import CertificationFacade
from platform.certification.ledger import CertificationConsoleLedger
from platform.certification.registry import CertificationRegistry
from platform.foundation.contracts import content_hash
from platform.observability.contracts import HealthStatus
from platform.observability.health import HealthCheck

from engine.certification.evidence import build_certification_evidence

#: The check that the record registry substrate is reachable (G1).
REGISTRY_CHECK = "certification-console-registry"

#: The check that the append-only ledger hash chain verifies (tamper-evident).
LEDGER_CHECK = "certification-console-ledger-integrity"

#: The check that every surfaced record faithfully reproduces the engine output (P6).
FIDELITY_CHECK = "certification-console-fidelity"

#: The check that every record's evidence matches its certified decision (OP-C1).
EVIDENCE_CHECK = "certification-console-evidence-integrity"


def certification_console_health_checks() -> tuple[HealthCheck, ...]:
    """The certification-console runtime health checks (all critical), in stable order."""
    return (
        HealthCheck(
            REGISTRY_CHECK,
            critical=True,
            description="Certification record registry substrate reachable.",
        ),
        HealthCheck(
            LEDGER_CHECK,
            critical=True,
            description="Append-only certification ledger hash chain verifies.",
        ),
        HealthCheck(
            FIDELITY_CHECK,
            critical=True,
            description="Every surfaced record equals a fresh certified reproduction (P6).",
        ),
        HealthCheck(
            EVIDENCE_CHECK,
            critical=True,
            description="Every record's evidence matches its certified decision.",
        ),
    )


class CertificationHealth:
    """A deterministic health probe over the record registry, the ledger, and the façade."""

    __slots__ = ("_registry", "_ledger", "_facade")

    def __init__(
        self,
        registry: CertificationRegistry,
        ledger: CertificationConsoleLedger,
        facade: CertificationFacade,
    ) -> None:
        if not isinstance(registry, CertificationRegistry):
            raise TypeError("a valid CertificationRegistry is required")
        if not isinstance(ledger, CertificationConsoleLedger):
            raise TypeError("a valid CertificationConsoleLedger is required")
        if not isinstance(facade, CertificationFacade):
            raise TypeError("a valid CertificationFacade is required")
        self._registry = registry
        self._ledger = ledger
        self._facade = facade

    def infidelic_records(self) -> tuple[str, ...]:
        """Record ids whose stored certification diverges from a fresh reproduction."""
        return tuple(
            record.record_id
            for record in self._registry.all()
            if not self._facade.verify_fidelity(
                record.record,
                record.report,
                record.validation_evidence,
                version=record.version,
                certification_class=record.decision.certification_class,
            )
        )

    def inconsistent_evidence(self) -> tuple[str, ...]:
        """Record ids whose stored evidence differs from the certified decision's evidence."""
        mismatched: list[str] = []
        for record in self._registry.all():
            decision = self._facade.reproduce(
                record.report,
                record.validation_evidence,
                version=record.version,
                certification_class=record.decision.certification_class,
            )
            expected = build_certification_evidence(decision)
            if content_hash(expected.to_dict()) != content_hash(
                record.certification_evidence.to_dict()
            ):
                mismatched.append(record.record_id)
        return tuple(mismatched)

    def probe(self) -> dict[str, HealthStatus]:
        """Compute deterministic probe results for the console health checks."""
        ledger_ok = self._ledger.verify()
        fidelity_ok = not self.infidelic_records()
        evidence_ok = not self.inconsistent_evidence()
        return {
            REGISTRY_CHECK: HealthStatus.HEALTHY,
            LEDGER_CHECK: (HealthStatus.HEALTHY if ledger_ok else HealthStatus.UNHEALTHY),
            FIDELITY_CHECK: (HealthStatus.HEALTHY if fidelity_ok else HealthStatus.UNHEALTHY),
            EVIDENCE_CHECK: (HealthStatus.HEALTHY if evidence_ok else HealthStatus.UNHEALTHY),
        }

    @property
    def healthy(self) -> bool:
        """True iff every console health check is HEALTHY."""
        return all(status is HealthStatus.HEALTHY for status in self.probe().values())


__all__ = [
    "REGISTRY_CHECK",
    "LEDGER_CHECK",
    "FIDELITY_CHECK",
    "EVIDENCE_CHECK",
    "certification_console_health_checks",
    "CertificationHealth",
]
