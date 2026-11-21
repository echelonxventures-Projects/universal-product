"""EPIC-007 (T7) — Runtime services catalog tests."""

from __future__ import annotations

from platform.foundation.services import ServiceRegistry
from platform.runtime_platform.contracts import RuntimeServiceKind
from platform.runtime_platform.errors import RuntimeServiceRegistryError
from platform.runtime_platform.services import (
    RuntimeServiceCatalog,
    runtime_service_descriptor,
    runtime_service_descriptors,
)

import pytest


def test_descriptors_cover_all_kinds():
    descriptors = runtime_service_descriptors()
    assert len(descriptors) == 9
    names = {d.name for d in descriptors}
    assert names == {kind.service_name for kind in RuntimeServiceKind}


def test_descriptor_carries_capabilities_and_dependencies():
    descriptor = runtime_service_descriptor(RuntimeServiceKind.WORKFLOW_EXECUTION)
    assert "CAP-18" in descriptor.capabilities
    assert RuntimeServiceKind.RUNTIME_LIFECYCLE.service_name in descriptor.dependencies


def test_descriptor_rejects_non_kind():
    with pytest.raises(RuntimeServiceRegistryError):
        runtime_service_descriptor("bad")  # type: ignore[arg-type]


def test_catalog_declares_into_registry_and_validates():
    catalog = RuntimeServiceCatalog()
    assert len(catalog) == 9
    assert set(catalog.names) == {kind.service_name for kind in RuntimeServiceKind}
    # every declared service resolves in the shared foundation registry
    for name in catalog.names:
        assert name in catalog.registry


def test_catalog_startup_order_is_dependency_honest():
    catalog = RuntimeServiceCatalog()
    order = catalog.startup_order()
    index = {name: i for i, name in enumerate(order)}
    # capacity-governance precedes execution-scheduling precedes workload-placement
    assert (
        index[RuntimeServiceKind.CAPACITY_GOVERNANCE.service_name]
        < index[RuntimeServiceKind.EXECUTION_SCHEDULING.service_name]
    )
    assert (
        index[RuntimeServiceKind.EXECUTION_SCHEDULING.service_name]
        < index[RuntimeServiceKind.WORKLOAD_PLACEMENT.service_name]
    )
    assert len(order) == 9


def test_catalog_is_idempotent_on_shared_registry():
    registry = ServiceRegistry()
    first = RuntimeServiceCatalog(registry)
    second = RuntimeServiceCatalog(registry)  # must not double-register
    assert len(first) == len(second) == 9


def test_catalog_views_and_dict():
    catalog = RuntimeServiceCatalog()
    view = catalog.view(RuntimeServiceKind.EVENT_DELIVERY)
    assert view.service_name == RuntimeServiceKind.EVENT_DELIVERY.service_name
    assert len(catalog.views()) == 9
    payload = catalog.to_dict()
    assert payload["service_count"] == 9
    assert len(payload["services"]) == 9


def test_catalog_rejects_bad_inputs():
    with pytest.raises(RuntimeServiceRegistryError):
        RuntimeServiceCatalog("bad")  # type: ignore[arg-type]
    with pytest.raises(RuntimeServiceRegistryError):
        RuntimeServiceCatalog().view("bad")  # type: ignore[arg-type]
