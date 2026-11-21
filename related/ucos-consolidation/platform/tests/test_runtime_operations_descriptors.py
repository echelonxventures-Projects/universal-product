"""EC2-TASK-000165 — Runtime Operations descriptor discovery/inspection tests (EC2-EPIC-012)."""

from __future__ import annotations

from platform.runtime_operations.contracts import (
    DeploymentDescriptorView,
    RollbackDescriptorView,
    RuntimeOperationKind,
    RuntimeOperationRecord,
)
from platform.runtime_operations.descriptors import DescriptorCatalog
from platform.runtime_operations.errors import RuntimeDescriptorError, RuntimeOperationRecordError
from platform.runtime_operations.facade import RuntimeFacade
from platform.runtime_operations.operations import RuntimeOperationRegistry
from platform.tests.runtime_operations_helpers import certification_record, runtime_unit

import pytest

_FACADE = RuntimeFacade()


def _registry_with_both():
    registry = RuntimeOperationRegistry()
    unit = runtime_unit()
    cert = certification_record()
    deploy = RuntimeOperationRecord.create(
        kind=RuntimeOperationKind.DEPLOY,
        unit=unit,
        certification=cert,
        deployment=_FACADE.deployment_descriptor(unit),
        owner_subject="op@x",
        environment="runtime",
    )
    rollback = RuntimeOperationRecord.create(
        kind=RuntimeOperationKind.ROLLBACK,
        unit=unit,
        certification=cert,
        rollback=_FACADE.rollback_descriptor(unit),
        owner_subject="op@x",
        environment="runtime",
    )
    registry.record(deploy)
    registry.record(rollback)
    return registry, deploy, rollback


def test_catalog_requires_registry():
    with pytest.raises(RuntimeDescriptorError):
        DescriptorCatalog("nope")  # type: ignore[arg-type]


def test_discover_and_views():
    registry, deploy, rollback = _registry_with_both()
    catalog = DescriptorCatalog(registry)
    assert len(catalog.discover()) == 2
    assert len(catalog.discover(kind=RuntimeOperationKind.DEPLOY)) == 1
    assert len(catalog.discover(runtime_id=deploy.runtime_id)) == 2
    deployments = catalog.deployment_views()
    rollbacks = catalog.rollback_views()
    assert len(deployments) == 1 and isinstance(deployments[0], DeploymentDescriptorView)
    assert len(rollbacks) == 1 and isinstance(rollbacks[0], RollbackDescriptorView)
    assert catalog.deployment_views(runtime_id=deploy.runtime_id)
    assert catalog.rollback_views(runtime_id=rollback.runtime_id)


def test_inspect_deploy_and_rollback():
    registry, deploy, rollback = _registry_with_both()
    catalog = DescriptorCatalog(registry)
    assert isinstance(catalog.inspect(deploy.operation_id), DeploymentDescriptorView)
    assert isinstance(catalog.inspect(rollback.operation_id), RollbackDescriptorView)
    with pytest.raises(RuntimeOperationRecordError):
        catalog.inspect("UCOS-ROPR-missing")


def test_count_and_serialise():
    registry, _, _ = _registry_with_both()
    catalog = DescriptorCatalog(registry)
    assert catalog.count() == {"total": 2, "deploy": 1, "rollback": 1}
    payload = catalog.to_dict()
    assert payload["census"]["total"] == 2
    assert catalog.fingerprint() == catalog.fingerprint()
