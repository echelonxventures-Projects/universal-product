"""EPIC-007 (Terminal T7) — Runtime Platform Health (Universal Runtime Platform).

A deterministic, self-contained health surface for the Universal Runtime Platform. It
probes the composed plane — the append-only execution registry's chain integrity, the
declared runtime-service topology, and the admission gate — and derives a single status
without any wall-clock or ambient state, so the same plane state always reports the same
health (P5). It starts nothing and runs nothing live.
"""

from __future__ import annotations

from dataclasses import dataclass
from platform.runtime_platform.contracts import all_runtime_service_kinds
from platform.runtime_platform.core import RuntimeKernel
from platform.runtime_platform.errors import RuntimePlatformError
from typing import Any

# --- health states (ordered worst-last for aggregation) --------------------------
HEALTHY = "healthy"
DEGRADED = "degraded"
UNHEALTHY = "unhealthy"
HEALTH_STATES: tuple[str, ...] = (HEALTHY, DEGRADED, UNHEALTHY)

#: The recorded health format.
HEALTH_FORMAT = "ucos-runtime-platform-health/1.0.0"

_EXPECTED_SERVICE_COUNT = len(all_runtime_service_kinds())


@dataclass(frozen=True, slots=True)
class HealthCheckResult:
    """An immutable result of one runtime-platform health check."""

    name: str
    status: str
    detail: str

    @property
    def ok(self) -> bool:
        return self.status == HEALTHY

    def to_dict(self) -> dict[str, Any]:
        return {"name": self.name, "status": self.status, "detail": self.detail}


@dataclass(frozen=True, slots=True)
class RuntimePlatformHealthReport:
    """An immutable, deterministic aggregate health report for the runtime plane."""

    status: str
    checks: tuple[HealthCheckResult, ...]

    @property
    def healthy(self) -> bool:
        return self.status == HEALTHY

    def to_dict(self) -> dict[str, Any]:
        return {
            "health_format": HEALTH_FORMAT,
            "status": self.status,
            "checks": [check.to_dict() for check in self.checks],
        }


class RuntimePlatformHealth:
    """The deterministic health probe over a composed :class:`RuntimeKernel`."""

    __slots__ = ("_kernel",)

    def __init__(self, kernel: RuntimeKernel) -> None:
        if not isinstance(kernel, RuntimeKernel):
            raise RuntimePlatformError("RuntimePlatformHealth requires a RuntimeKernel")
        self._kernel = kernel

    def probe(self) -> RuntimePlatformHealthReport:
        """Probe the plane and derive a deterministic aggregate health report."""
        checks = (self._registry_check(), self._services_check(), self._consumption_check())
        status = HEALTHY
        for check in checks:
            if check.status == UNHEALTHY:
                status = UNHEALTHY
                break
            if check.status == DEGRADED and status == HEALTHY:
                status = DEGRADED
        return RuntimePlatformHealthReport(status=status, checks=checks)

    def _registry_check(self) -> HealthCheckResult:
        intact = self._kernel.registry.verify()
        return HealthCheckResult(
            name="execution-registry-intact",
            status=HEALTHY if intact else UNHEALTHY,
            detail=(
                f"chain intact over {len(self._kernel.registry)} entries"
                if intact
                else "execution registry hash chain broken (tamper detected)"
            ),
        )

    def _services_check(self) -> HealthCheckResult:
        declared = len(self._kernel.services)
        ok = declared == _EXPECTED_SERVICE_COUNT
        return HealthCheckResult(
            name="runtime-services-declared",
            status=HEALTHY if ok else DEGRADED,
            detail=f"{declared}/{_EXPECTED_SERVICE_COUNT} runtime services declared",
        )

    def _consumption_check(self) -> HealthCheckResult:
        consumed = len(self._kernel.consumed_contracts)
        ok = consumed > 0
        return HealthCheckResult(
            name="upstream-consumption-bound",
            status=HEALTHY if ok else UNHEALTHY,
            detail=f"{consumed} upstream capability contracts bound by reference",
        )


__all__ = [
    "HEALTHY",
    "DEGRADED",
    "UNHEALTHY",
    "HEALTH_STATES",
    "HEALTH_FORMAT",
    "HealthCheckResult",
    "RuntimePlatformHealthReport",
    "RuntimePlatformHealth",
]
