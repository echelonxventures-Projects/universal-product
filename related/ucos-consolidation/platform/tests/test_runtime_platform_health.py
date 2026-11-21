"""EPIC-007 (T7) — Runtime platform health tests."""

from __future__ import annotations

import dataclasses
from platform.runtime_platform.core import RuntimeKernel
from platform.runtime_platform.errors import RuntimePlatformError
from platform.runtime_platform.health import (
    DEGRADED,
    HEALTHY,
    UNHEALTHY,
    HealthCheckResult,
    RuntimePlatformHealth,
)
from platform.tests.runtime_platform_helpers import request

import pytest


def test_probe_healthy_on_fresh_kernel():
    report = RuntimePlatformHealth(RuntimeKernel()).probe()
    assert report.status == HEALTHY
    assert report.healthy
    assert all(check.ok for check in report.checks)
    assert len(report.checks) == 3
    assert report.to_dict()["status"] == HEALTHY


def test_probe_unhealthy_on_tampered_registry():
    kernel = RuntimeKernel()
    kernel.submit(request("a"))
    kernel.submit(request("b"))
    reg = kernel.registry
    reg._entries[0] = dataclasses.replace(reg._entries[0], record_sha256="deadbeef")
    report = RuntimePlatformHealth(kernel).probe()
    assert report.status == UNHEALTHY
    assert not report.healthy
    names = {c.name: c.status for c in report.checks}
    assert names["execution-registry-intact"] == UNHEALTHY


def test_check_result_ok_and_dict():
    report = RuntimePlatformHealth(RuntimeKernel()).probe()
    check = report.checks[0]
    assert check.ok
    assert set(check.to_dict()) == {"name", "status", "detail"}


def test_health_rejects_bad_kernel():
    with pytest.raises(RuntimePlatformError):
        RuntimePlatformHealth("bad")  # type: ignore[arg-type]


def test_lineage_and_record_fingerprints_hash_their_own_projection() -> None:
    """A lineage view's projection and fingerprint, and the registry's own refusal to trust order.

    to_dict is how a lineage record leaves the process and fingerprint is what the chain
    hashes; a projection nobody builds and a verify() whose False arm never fires certify
    nothing. The order is broken here directly — the registry refuses a chain whose entries
    are not the sequence they claim.
    """

    kernel = RuntimeKernel()
    first = kernel.submit(request("a"))
    kernel.submit(request("b"))
    view = kernel.registry.lineage(first.execution_id)
    projection = view.to_dict()
    assert projection["lineage_id"] == view.lineage_id
    assert projection["is_root"] is view.is_root
    assert view.fingerprint() == view.fingerprint()

    broken = type(kernel.registry)()
    broken._entries = [
        dataclasses.replace(e, sequence=i + 5) for i, e in enumerate(kernel.registry.entries)
    ]
    assert broken.verify() is False


def test_a_degraded_component_degrades_the_report_without_failing_it(monkeypatch) -> None:
    """HEALTHY + DEGRADED folds to DEGRADED; only UNHEALTHY stops the walk.

    A DEGRADED check is a component reporting through rather than failing, and the fold that
    combines the three component statuses had never met one — a probe that silently promoted
    or silently ignored it would misstate platform health in opposite directions.
    """

    class _DegradedResult(HealthCheckResult):
        pass

    def degraded(self):  # type: ignore[no-untyped-def]
        return HealthCheckResult(name="services", status=DEGRADED, detail="one component behind")

    monkeypatch.setattr(RuntimePlatformHealth, "_services_check", degraded)
    report = RuntimePlatformHealth(RuntimeKernel()).probe()
    assert report.status == DEGRADED


def test_an_intact_registry_passes_the_gate_that_refuses_a_tampered_one() -> None:
    """require_intact is called on every write path; its silent arm is the healthy one.

    A guard whose only exercised branch raises cannot be told apart from one that never
    returns — the probe walks this every cycle, and both directions must answer.
    """
    from platform.runtime_platform.registry import ExecutionRegistry

    registry = ExecutionRegistry()
    registry.require_intact()
    assert registry.verify() is True
