"""TASK-000045 — Factory contract tests (TASK-000038)."""

from __future__ import annotations

import pytest

from engine.factory.contracts import (
    FACTORY_CONTRACT_VERSION,
    FactoryCapability,
    FactoryDescriptor,
    FactoryRequest,
    FactoryResult,
    GenerationStatus,
)


def test_request_is_immutable_and_serializable():
    request = FactoryRequest("BP-DATA-0001", environment="production")
    assert request.to_dict() == {"blueprint_id": "BP-DATA-0001", "environment": "production"}
    with pytest.raises((AttributeError, TypeError)):
        request.blueprint_id = "x"  # type: ignore[misc]


def test_request_default_environment():
    assert FactoryRequest("BP-DATA-0001").environment == "runtime"


def test_capability_and_descriptor_serializable():
    capability = FactoryCapability(blueprint_class="BP-DATA", stages=("compile",), description="d")
    descriptor = FactoryDescriptor(
        name="data-factory", blueprint_class="BP-DATA", capability=capability
    )
    assert descriptor.contract_version == FACTORY_CONTRACT_VERSION
    d = descriptor.to_dict()
    assert d["capability"]["stages"] == ["compile"]
    assert d["name"] == "data-factory"


def test_result_serializable_generated():
    result = FactoryResult(
        blueprint_id="BP-DATA-0001",
        blueprint_class="BP-DATA",
        factory_name="data-factory",
        status=GenerationStatus.GENERATED,
        success=True,
        artifact_id="a",
        runtime_id="r",
        package_sha256="p",
        image_reference="img",
        dependency_closure=({"blueprint_id": "BP-DATA-0001", "role": "root"},),
        disclosure_present=True,
        evidence={"k": "v"},
    )
    d = result.to_dict()
    assert d["status"] == "generated"
    assert d["dependency_closure"] == [{"blueprint_id": "BP-DATA-0001", "role": "root"}]
    assert d["gap"] is None


def test_result_serializable_gap():
    result = FactoryResult(
        blueprint_id="BP-API-0001",
        blueprint_class="BP-API",
        factory_name="api-factory",
        status=GenerationStatus.GAP,
        success=False,
        gap={"stage": "parse"},
    )
    d = result.to_dict()
    assert d["status"] == "gap"
    assert d["gap"] == {"stage": "parse"}
    assert d["artifact_id"] is None
