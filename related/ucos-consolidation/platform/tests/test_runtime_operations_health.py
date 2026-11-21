"""EC2-TASK-000171 — Runtime Operations health tests (EC2-EPIC-012).

Covers the deterministic health probe over the registry, ledger, and façade: all-healthy
baseline, ledger tamper detection, fidelity fault detection, reversibility fault
detection, and fail-closed construction.
"""

from __future__ import annotations

import dataclasses
from platform.observability.contracts import HealthStatus
from platform.runtime_operations.contracts import RuntimeOperationKind, RuntimeOperationRecord
from platform.runtime_operations.facade import RuntimeFacade
from platform.runtime_operations.health import (
    FIDELITY_CHECK,
    LEDGER_CHECK,
    REGISTRY_CHECK,
    REVERSIBILITY_CHECK,
    RuntimeOperationsHealth,
    runtime_operations_health_checks,
)
from platform.runtime_operations.ledger import RuntimeOperationLedger
from platform.runtime_operations.operations import RuntimeOperationPlanner, RuntimeOperationRegistry
from platform.tests.runtime_operations_helpers import certification_record, runtime_unit

import pytest

_FACADE = RuntimeFacade()


def _healthy():
    registry = RuntimeOperationRegistry()
    ledger = RuntimeOperationLedger()
    plan = RuntimeOperationPlanner().plan_deploy(
        runtime_unit(), certification_record(), owner_subject="op@x"
    )
    registry.record(plan.record)
    ledger.append(plan.record)
    return registry, ledger, RuntimeOperationsHealth(registry, ledger, _FACADE)


def test_health_checks_are_all_critical():
    checks = runtime_operations_health_checks()
    assert {c.name for c in checks} == {
        REGISTRY_CHECK,
        LEDGER_CHECK,
        FIDELITY_CHECK,
        REVERSIBILITY_CHECK,
    }
    assert all(c.critical for c in checks)


def test_healthy_baseline():
    _, _, health = _healthy()
    probe = health.probe()
    assert all(status is HealthStatus.HEALTHY for status in probe.values())
    assert health.healthy is True
    assert health.infidelic_operations() == ()
    assert health.irreversible_rollbacks() == ()


def test_ledger_tamper_drives_unhealthy():
    _, ledger, health = _healthy()
    ledger._entries[0] = dataclasses.replace(ledger._entries[0], descriptor_sha256="bad")
    assert health.probe()[LEDGER_CHECK] is HealthStatus.UNHEALTHY
    assert health.healthy is False


def test_fidelity_fault_detected():
    registry = RuntimeOperationRegistry()
    ledger = RuntimeOperationLedger()
    unit = runtime_unit()
    # Store a deployment descriptor generated for a DIFFERENT environment than the record's
    # declared environment, so a fresh reproduction over the recorded environment diverges.
    divergent = _FACADE.deployment_descriptor(unit, environment="staging")
    record = RuntimeOperationRecord.create(
        kind=RuntimeOperationKind.DEPLOY,
        unit=unit,
        certification=certification_record(),
        deployment=divergent,
        owner_subject="op@x",
        environment="production",
    )
    registry.record(record)
    ledger.append(record)
    health = RuntimeOperationsHealth(registry, ledger, _FACADE)
    assert record.operation_id in health.infidelic_operations()
    assert health.probe()[FIDELITY_CHECK] is HealthStatus.UNHEALTHY


def test_reversibility_fault_detected():
    registry = RuntimeOperationRegistry()
    ledger = RuntimeOperationLedger()
    unit = runtime_unit()
    irreversible = dataclasses.replace(_FACADE.rollback_descriptor(unit), reversible=False)
    record = RuntimeOperationRecord.create(
        kind=RuntimeOperationKind.ROLLBACK,
        unit=unit,
        certification=certification_record(),
        rollback=irreversible,
        owner_subject="op@x",
        environment="runtime",
    )
    registry.record(record)
    ledger.append(record)
    health = RuntimeOperationsHealth(registry, ledger, _FACADE)
    assert record.operation_id in health.irreversible_rollbacks()
    assert health.probe()[REVERSIBILITY_CHECK] is HealthStatus.UNHEALTHY


def test_health_rejects_bad_components():
    registry = RuntimeOperationRegistry()
    ledger = RuntimeOperationLedger()
    with pytest.raises(TypeError):
        RuntimeOperationsHealth("nope", ledger, _FACADE)  # type: ignore[arg-type]
    with pytest.raises(TypeError):
        RuntimeOperationsHealth(registry, "nope", _FACADE)  # type: ignore[arg-type]
    with pytest.raises(TypeError):
        RuntimeOperationsHealth(registry, ledger, "nope")  # type: ignore[arg-type]
