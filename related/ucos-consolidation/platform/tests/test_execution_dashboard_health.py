"""EC2-TASK-000130 — Execution dashboard health tests (EC2-EPIC-008).

Covers the deterministic dashboard health probe over the consumed request registry: the
three critical checks (registry reachable, census-integrity, queue-integrity), the healthy
baseline, and the fail-closed UNHEALTHY branch under induced projection drift (OP-C1) — the
projection-fidelity invariant made machine-checkable.
"""

from __future__ import annotations

from platform.blueprints.contracts import BlueprintFamily
from platform.execution_dashboard.health import (
    CENSUS_CHECK,
    QUEUE_CHECK,
    REGISTRY_CHECK,
    DashboardHealth,
    execution_dashboard_health_checks,
)
from platform.generation.registry import GenerationRequestRegistry
from platform.observability.contracts import HealthStatus

import pytest


def _registry(*, count=2):
    reg = GenerationRequestRegistry()
    for i in range(count):
        reg.create(
            f"req-{i}",
            "UCOS-BLPR-1",
            "UCOS-WSPC-1",
            "arch@x",
            BlueprintFamily.DATA,
            submitted_tick=i,
        )
    return reg


def test_health_checks_are_three_critical():
    checks = execution_dashboard_health_checks()
    assert {c.name for c in checks} == {REGISTRY_CHECK, CENSUS_CHECK, QUEUE_CHECK}
    assert all(c.critical for c in checks)


def test_health_requires_valid_registry():
    with pytest.raises(TypeError):
        DashboardHealth("nope")  # type: ignore[arg-type]


def test_probe_healthy_baseline():
    health = DashboardHealth(_registry())
    probe = health.probe()
    assert probe[REGISTRY_CHECK] is HealthStatus.HEALTHY
    assert probe[CENSUS_CHECK] is HealthStatus.HEALTHY
    assert probe[QUEUE_CHECK] is HealthStatus.HEALTHY
    assert health.healthy is True
    assert health.census_drift() == ()
    assert health.queue_drift() is False


def test_census_drift_drives_unhealthy(monkeypatch):
    reg = _registry(count=2)
    health = DashboardHealth(reg)
    # Induce a corrupted authoritative census that disagrees with the live projection.
    monkeypatch.setattr(
        GenerationRequestRegistry,
        "count_by_status",
        lambda self: {"submitted": 99},
        raising=True,
    )
    assert health.census_drift() != ()
    probe = health.probe()
    assert probe[CENSUS_CHECK] is HealthStatus.UNHEALTHY
    assert health.healthy is False


def test_queue_drift_drives_unhealthy(monkeypatch):
    reg = _registry(count=1)
    health = DashboardHealth(reg)

    # Return a census whose non-queue counts still match the projection so only the
    # queue-integrity check trips.
    def _skewed(self):
        base = {
            s: 0
            for s in (
                "submitted",
                "validating",
                "approved",
                "queued",
                "dispatched",
                "running",
                "completed",
                "failed",
                "cancelled",
            )
        }
        base["submitted"] = 1
        base["queued"] = 7  # projection sees 0 QUEUED → drift
        return base

    monkeypatch.setattr(GenerationRequestRegistry, "count_by_status", _skewed, raising=True)
    assert health.queue_drift() is True
    probe = health.probe()
    assert probe[QUEUE_CHECK] is HealthStatus.UNHEALTHY
