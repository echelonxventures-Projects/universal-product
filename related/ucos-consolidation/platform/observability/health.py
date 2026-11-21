"""EC2-TASK-000182 — Platform Health (EC2-EPIC-013).

The health model and registry backing the platform's **live health endpoint** (go-live
condition G1 "Platform Running"). Health checks are deterministic, pure functions of a
supplied probe result — they perform no I/O and open no socket here (that binding
belongs to later operational epics); this module defines the reusable, deterministic
health substrate.

Design (G1 platform-running; PC-12 monitoring; IMP-007 §5 determinism):
    * :class:`HealthCheck` is an immutable declaration of a named component check
      plus whether it is *critical* to the aggregate verdict.
    * :class:`HealthResult` is an immutable, content-addressed observation of a
      check's :class:`~platform.observability.contracts.HealthStatus` and a detail.
    * :class:`HealthRegistry` registers checks and, given a mapping of probe results,
      produces a deterministic aggregate :class:`HealthReport` and a serializable
      **health endpoint** view. Aggregation is fail-closed: a missing result for a
      registered critical check is treated as ``UNHEALTHY``.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from platform.foundation.contracts import content_hash
from platform.observability.contracts import HealthStatus
from platform.observability.errors import HealthError
from typing import Any


@dataclass(frozen=True, slots=True)
class HealthCheck:
    """An immutable declaration of a named component health check."""

    name: str
    critical: bool = True
    description: str = ""

    def __post_init__(self) -> None:
        if not isinstance(self.name, str) or not self.name:
            raise HealthError("health check name is required")


@dataclass(frozen=True, slots=True)
class HealthResult:
    """An immutable, content-addressed observation of a single check."""

    name: str
    status: HealthStatus
    detail: str = ""
    result_id: str = ""

    @classmethod
    def create(cls, name: str, status: HealthStatus, detail: str = "") -> HealthResult:
        if not isinstance(name, str) or not name:
            raise HealthError("health result name is required")
        if not isinstance(status, HealthStatus):
            raise HealthError("health status must be a HealthStatus", name=name)
        core = {"name": name, "status": status.value, "detail": detail}
        return cls(
            name=name,
            status=status,
            detail=detail,
            result_id=f"UCOS-HLTH-{content_hash(core)[:16]}",
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "result_id": self.result_id,
            "name": self.name,
            "status": self.status.value,
            "detail": self.detail,
        }


@dataclass(frozen=True, slots=True)
class HealthReport:
    """An immutable, content-addressed aggregate health verdict over all checks."""

    status: HealthStatus
    results: tuple[HealthResult, ...]
    report_id: str = ""

    @classmethod
    def create(cls, results: tuple[HealthResult, ...]) -> HealthReport:
        ordered = tuple(sorted(results, key=lambda r: r.name))
        status = HealthStatus.worst(r.status for r in ordered)
        core = {"status": status.value, "results": [r.to_dict() for r in ordered]}
        return cls(
            status=status,
            results=ordered,
            report_id=f"UCOS-HRPT-{content_hash(core)[:16]}",
        )

    @property
    def healthy(self) -> bool:
        return self.status is HealthStatus.HEALTHY

    def to_dict(self) -> dict[str, Any]:
        return {
            "report_id": self.report_id,
            "status": self.status.value,
            "results": [r.to_dict() for r in self.results],
        }

    def fingerprint(self) -> str:
        return content_hash(self.to_dict())


class HealthRegistry:
    """A deterministic registry of health checks producing the live health endpoint."""

    __slots__ = ("_checks",)

    def __init__(self) -> None:
        self._checks: dict[str, HealthCheck] = {}

    def register(self, check: HealthCheck) -> HealthCheck:
        """Register a health check (fail-closed on duplicate)."""
        if not isinstance(check, HealthCheck):
            raise HealthError("register requires a HealthCheck")
        if check.name in self._checks:
            raise HealthError("health check already registered", name=check.name)
        self._checks[check.name] = check
        return check

    def __contains__(self, name: str) -> bool:
        return name in self._checks

    def __len__(self) -> int:
        return len(self._checks)

    @property
    def names(self) -> tuple[str, ...]:
        return tuple(sorted(self._checks))

    def report(self, results: Mapping[str, HealthStatus]) -> HealthReport:
        """Aggregate a deterministic :class:`HealthReport` from probe ``results``.

        Fail-closed: a registered *critical* check with no supplied result is treated
        as ``UNHEALTHY``; a non-critical check with no result is treated as
        ``DEGRADED``. Unknown result keys are rejected.
        """
        for key in results:
            if key not in self._checks:
                raise HealthError("result for unregistered check", name=key)
        observed: list[HealthResult] = []
        for name in self.names:
            check = self._checks[name]
            if name in results:
                status = results[name]
                if not isinstance(status, HealthStatus):
                    raise HealthError("health status must be a HealthStatus", name=name)
                observed.append(HealthResult.create(name, status, check.description))
            else:
                missing = HealthStatus.UNHEALTHY if check.critical else HealthStatus.DEGRADED
                observed.append(HealthResult.create(name, missing, "no result supplied"))
        return HealthReport.create(tuple(observed))

    def endpoint(self, results: Mapping[str, HealthStatus]) -> dict[str, Any]:
        """The serializable live health-endpoint view (G1 versioned health contract)."""
        report = self.report(results)
        return {
            "status": report.status.value,
            "healthy": report.healthy,
            "checks": [r.to_dict() for r in report.results],
            "report_id": report.report_id,
        }

    def to_dict(self) -> dict[str, Any]:
        return {
            "check_count": len(self._checks),
            "checks": [
                {"name": c.name, "critical": c.critical, "description": c.description}
                for c in (self._checks[n] for n in self.names)
            ],
        }


__all__ = ["HealthCheck", "HealthResult", "HealthReport", "HealthRegistry"]
