"""EC2-TASK-000116 — Generation request health tests (EC2-EPIC-007).

Covers the deterministic health probe: healthy baseline, the dispatch-integrity
invariant (a request that reached the runtime without a recorded dispatch is a
bypass fault → UNHEALTHY), and the execution-integrity invariant (an orphaned dispatch
→ UNHEALTHY). This backs the "no runtime bypass path" guarantee (§7, OP-C1).
"""

from __future__ import annotations

from platform.blueprints.contracts import BlueprintFamily
from platform.generation.contracts import RequestStatus
from platform.generation.dispatch import DispatchLedger, DispatchRecord
from platform.generation.health import (
    DISPATCH_CHECK,
    INTEGRITY_CHECK,
    REGISTRY_CHECK,
    RequestHealth,
    generation_request_health_checks,
)
from platform.generation.registry import GenerationRequestRegistry
from platform.observability.contracts import HealthStatus

import pytest


def _dispatch_record(request_ref):
    return DispatchRecord.create(
        request_ref=request_ref,
        blueprint_ref="UCOS-BLPR-a",
        family=BlueprintFamily.DATA,
        content_hash="c0ffee",
        tick=5,
    )


def test_health_checks_are_all_critical():
    checks = generation_request_health_checks()
    assert {c.name for c in checks} == {REGISTRY_CHECK, DISPATCH_CHECK, INTEGRITY_CHECK}
    assert all(c.critical for c in checks)


def test_construction_validates_components():
    with pytest.raises(TypeError):
        RequestHealth("nope", DispatchLedger())  # type: ignore[arg-type]
    with pytest.raises(TypeError):
        RequestHealth(GenerationRequestRegistry(), "nope")  # type: ignore[arg-type]


def test_healthy_baseline():
    reg = GenerationRequestRegistry()
    dispatch = DispatchLedger()
    reg.create("r", "UCOS-BLPR-a", "UCOS-WSPC-1", "arch@x", BlueprintFamily.DATA, submitted_tick=1)
    health = RequestHealth(reg, dispatch)
    assert health.healthy is True
    assert health.probe()[REGISTRY_CHECK] is HealthStatus.HEALTHY


def test_dispatch_integrity_fault_on_bypass():
    reg = GenerationRequestRegistry()
    dispatch = DispatchLedger()
    req = reg.create(
        "r", "UCOS-BLPR-a", "UCOS-WSPC-1", "arch@x", BlueprintFamily.DATA, submitted_tick=1
    )
    # Drive to DISPATCHED WITHOUT a dispatch record — a runtime bypass fault.
    reg.transition(req.request_id, RequestStatus.VALIDATING, tick=2)
    reg.transition(req.request_id, RequestStatus.APPROVED, tick=3)
    reg.transition(req.request_id, RequestStatus.QUEUED, tick=4)
    reg.transition(req.request_id, RequestStatus.DISPATCHED, tick=5)
    health = RequestHealth(reg, dispatch)
    assert req.request_id in health.undispatched_executing_requests()
    assert health.probe()[DISPATCH_CHECK] is HealthStatus.UNHEALTHY
    assert health.healthy is False


def test_failed_before_dispatch_is_not_a_fault():
    reg = GenerationRequestRegistry()
    dispatch = DispatchLedger()
    req = reg.create(
        "r", "UCOS-BLPR-a", "UCOS-WSPC-1", "arch@x", BlueprintFamily.DATA, submitted_tick=1
    )
    reg.transition(req.request_id, RequestStatus.VALIDATING, tick=2)
    reg.transition(req.request_id, RequestStatus.FAILED, tick=3)  # failed in validation
    health = RequestHealth(reg, dispatch)
    assert health.undispatched_executing_requests() == ()
    assert health.probe()[DISPATCH_CHECK] is HealthStatus.HEALTHY


def test_execution_integrity_fault_on_orphaned_dispatch():
    reg = GenerationRequestRegistry()
    dispatch = DispatchLedger()
    dispatch.record(_dispatch_record("UCOS-GREQ-orphan"))  # no such request registered
    health = RequestHealth(reg, dispatch)
    assert "UCOS-GREQ-orphan" in health.orphaned_dispatches()
    assert health.probe()[INTEGRITY_CHECK] is HealthStatus.UNHEALTHY
