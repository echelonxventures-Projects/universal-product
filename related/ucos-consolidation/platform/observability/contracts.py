"""EC2-TASK-000178 — Observability Contracts (EC2-EPIC-013).

The versioned contract surface for the UCOS Platform Observability & Monitoring
layer (L8 Operations of the Program architecture, §4). Every observability service —
the metric registry, the log buffer, the trace recorder, the health registry, the
alert engine, and the audit trail — is published as a documented, semantically
versioned :class:`Contract` (AR-03/PL-05), reusing the certified EC-1 contract
machinery through the Platform Foundation
(:func:`~platform.foundation.contracts.platform_contract`,
:class:`~platform.foundation.contracts.ContractRef`).

This module also defines the immutable **core vocabulary** every observability
service speaks:

    * :class:`Severity` — the ordered severity levels for logs and alerts.
    * :class:`MetricKind` — the three metric kinds (counter, gauge, histogram).
    * :class:`HealthStatus` — the fail-closed health verdict (``HEALTHY`` /
      ``DEGRADED`` / ``UNHEALTHY``) with a deterministic aggregation rule.

All types are **immutable, typed, deterministic, and serializable**, hold no runtime
state, and record no secret material (SEC-04).
"""

from __future__ import annotations

from enum import Enum
from platform.foundation.contracts import (
    Contract,
    ContractRef,
    platform_contract,
)
from platform.foundation.errors import PlatformContractError
from platform.observability.errors import ObservabilityContractError

#: The semantic version of the Observability Platform contract surface (AR-03/PL-05).
OBSERVABILITY_CONTRACT_VERSION = "1.0.0"


class MetricKind(str, Enum):
    """The three supported metric kinds."""

    COUNTER = "counter"
    GAUGE = "gauge"
    HISTOGRAM = "histogram"


class Severity(str, Enum):
    """Ordered severity levels shared by structured logs and alerts.

    Ordering (ascending) is ``DEBUG < INFO < WARNING < ERROR < CRITICAL`` and is used
    for deterministic threshold comparisons (e.g. "alert on WARNING or above").
    """

    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"

    @property
    def rank(self) -> int:
        """The ascending numeric rank of this severity (DEBUG=0 … CRITICAL=4)."""
        return _SEVERITY_ORDER[self]

    def at_least(self, other: Severity) -> bool:
        """True iff this severity is ``other`` or more severe."""
        return self.rank >= other.rank


_SEVERITY_ORDER: dict[Severity, int] = {
    Severity.DEBUG: 0,
    Severity.INFO: 1,
    Severity.WARNING: 2,
    Severity.ERROR: 3,
    Severity.CRITICAL: 4,
}


class HealthStatus(str, Enum):
    """The fail-closed health verdict for a check or an aggregate report."""

    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"

    @property
    def rank(self) -> int:
        """Ascending severity rank (HEALTHY=0 < DEGRADED=1 < UNHEALTHY=2)."""
        return _HEALTH_ORDER[self]

    @classmethod
    def worst(cls, statuses: object) -> HealthStatus:
        """Return the most severe status in ``statuses`` (empty ⇒ ``HEALTHY``).

        The aggregation rule is deterministic and fail-closed: any UNHEALTHY makes
        the aggregate UNHEALTHY; otherwise any DEGRADED makes it DEGRADED.
        """
        worst = cls.HEALTHY
        for status in statuses:  # type: ignore[attr-defined]
            if not isinstance(status, HealthStatus):
                raise ObservabilityContractError("health aggregation requires HealthStatus")
            if status.rank > worst.rank:
                worst = status
        return worst


_HEALTH_ORDER: dict[HealthStatus, int] = {
    HealthStatus.HEALTHY: 0,
    HealthStatus.DEGRADED: 1,
    HealthStatus.UNHEALTHY: 2,
}


def all_severities() -> tuple[Severity, ...]:
    """Return every severity level in ascending order."""
    return (Severity.DEBUG, Severity.INFO, Severity.WARNING, Severity.ERROR, Severity.CRITICAL)


def all_metric_kinds() -> tuple[MetricKind, ...]:
    """Return every metric kind in stable declaration order."""
    return tuple(MetricKind)


# --------------------------------------------------------------------------- #
# The published observability contract surface (L8 Operations).               #
# --------------------------------------------------------------------------- #

#: The observability service contract identities the L8 layer publishes. Each maps
#: to one EC2-EPIC-013 deliverable; consumers (Execution Dashboard EPIC-008,
#: Administration EPIC-014, …) bind to these by reference (PL-05, versioned).
_OBSERVABILITY_CONTRACT_NAMES: tuple[tuple[str, str], ...] = (
    ("observability.metrics.registry", "Metric registry — counters, gauges, histograms."),
    ("observability.logs.buffer", "Structured log buffer — append-only, redacted."),
    ("observability.traces.recorder", "Trace recorder — spans over governed actions."),
    ("observability.health.registry", "Health registry — checks + aggregate health endpoint."),
    ("observability.alerting.engine", "Alert engine — fire alerts on defined conditions."),
    ("observability.audit.trail", "Audit trail — append-only record of governed actions."),
)

#: Immutable references to the six published observability contracts (name + version).
OBSERVABILITY_CONTRACTS: tuple[ContractRef, ...] = tuple(
    ContractRef(name, OBSERVABILITY_CONTRACT_VERSION) for name, _ in _OBSERVABILITY_CONTRACT_NAMES
)


def observability_contract(name: str, description: str = "") -> Contract:
    """Build a versioned observability :class:`Contract` at the contract version."""
    if not isinstance(name, str) or not name:
        raise ObservabilityContractError("observability contract name is required")
    try:
        return platform_contract(name, OBSERVABILITY_CONTRACT_VERSION, description)
    except PlatformContractError as exc:  # normalise into the observability taxonomy
        raise ObservabilityContractError(str(exc), name=name) from exc


def default_observability_contracts() -> tuple[Contract, ...]:
    """The six published observability contracts as concrete :class:`Contract` objects."""
    return tuple(
        observability_contract(name, description)
        for name, description in _OBSERVABILITY_CONTRACT_NAMES
    )


__all__ = [
    "OBSERVABILITY_CONTRACT_VERSION",
    "MetricKind",
    "Severity",
    "HealthStatus",
    "all_severities",
    "all_metric_kinds",
    "OBSERVABILITY_CONTRACTS",
    "observability_contract",
    "default_observability_contracts",
]
