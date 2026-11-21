"""EPIC-007 (Terminal T7) — Runtime Services (Universal Runtime Platform).

The **Runtime Services** catalog — the deterministic declaration of the canonical
platform runtime services the plane provides (:class:`RuntimeServiceKind`), each declared
by an immutable :class:`~platform.foundation.services.ServiceDescriptor` publishing a
versioned contract. It **reuses** the Platform Foundation
:class:`~platform.foundation.services.ServiceRegistry` verbatim — it declares no second
registry and implements no service discovery of its own — and layers on the runtime
plane's fixed service topology + capability anchors (CAP-15 Runtime & Compute, CAP-18
Workflow, CAP-19 Registry, PE-04 Messaging).

The catalog stores declarations only; it starts nothing and runs nothing. Services list
and resolve in a stable dependency-honest order.
"""

from __future__ import annotations

from platform.foundation.services import ServiceDescriptor, ServiceRegistry
from platform.runtime_platform.contracts import (
    RuntimeServiceKind,
    RuntimeServiceView,
    all_runtime_service_kinds,
    runtime_platform_contract,
)
from platform.runtime_platform.errors import RuntimeServiceRegistryError
from typing import Any

#: The capability anchor(s) each runtime service kind maps to (deterministic).
_CAPABILITY_ANCHORS: dict[RuntimeServiceKind, tuple[str, ...]] = {
    RuntimeServiceKind.EXECUTION_SCHEDULING: ("CAP-15",),
    RuntimeServiceKind.WORKLOAD_PLACEMENT: ("CAP-15",),
    RuntimeServiceKind.RUNTIME_LIFECYCLE: ("CAP-15",),
    RuntimeServiceKind.CAPACITY_GOVERNANCE: ("CAP-15",),
    RuntimeServiceKind.WORKFLOW_RESOLUTION: ("CAP-18",),
    RuntimeServiceKind.WORKFLOW_EXECUTION: ("CAP-18",),
    RuntimeServiceKind.EVENT_PUBLICATION: ("CAP-17",),
    RuntimeServiceKind.EVENT_DELIVERY: ("CAP-17",),
    RuntimeServiceKind.EXECUTION_REGISTRATION: ("CAP-19",),
}

#: The declared intra-plane dependencies between runtime services (deterministic DAG).
_SERVICE_DEPENDENCIES: dict[RuntimeServiceKind, tuple[RuntimeServiceKind, ...]] = {
    RuntimeServiceKind.EXECUTION_SCHEDULING: (RuntimeServiceKind.CAPACITY_GOVERNANCE,),
    RuntimeServiceKind.WORKLOAD_PLACEMENT: (RuntimeServiceKind.EXECUTION_SCHEDULING,),
    RuntimeServiceKind.RUNTIME_LIFECYCLE: (RuntimeServiceKind.WORKLOAD_PLACEMENT,),
    RuntimeServiceKind.CAPACITY_GOVERNANCE: (),
    RuntimeServiceKind.WORKFLOW_RESOLUTION: (),
    RuntimeServiceKind.WORKFLOW_EXECUTION: (
        RuntimeServiceKind.WORKFLOW_RESOLUTION,
        RuntimeServiceKind.RUNTIME_LIFECYCLE,
    ),
    RuntimeServiceKind.EVENT_PUBLICATION: (),
    RuntimeServiceKind.EVENT_DELIVERY: (RuntimeServiceKind.EVENT_PUBLICATION,),
    RuntimeServiceKind.EXECUTION_REGISTRATION: (),
}


def runtime_service_descriptor(kind: RuntimeServiceKind) -> ServiceDescriptor:
    """Build the immutable :class:`ServiceDescriptor` for a runtime service kind."""
    if not isinstance(kind, RuntimeServiceKind):
        raise RuntimeServiceRegistryError(
            "runtime_service_descriptor requires a RuntimeServiceKind"
        )
    return ServiceDescriptor(
        name=kind.service_name,
        contract=runtime_platform_contract(kind),
        capabilities=_CAPABILITY_ANCHORS[kind],
        dependencies=tuple(dep.service_name for dep in _SERVICE_DEPENDENCIES[kind]),
        description=f"UCOS Universal Runtime Platform runtime service: {kind.value}.",
    )


def runtime_service_descriptors() -> tuple[ServiceDescriptor, ...]:
    """Every runtime-service descriptor in deterministic (kind) order."""
    return tuple(runtime_service_descriptor(kind) for kind in all_runtime_service_kinds())


class RuntimeServiceCatalog:
    """The deterministic catalog of Universal Runtime Platform runtime services."""

    __slots__ = ("_registry",)

    def __init__(self, registry: ServiceRegistry | None = None) -> None:
        if registry is not None and not isinstance(registry, ServiceRegistry):
            raise RuntimeServiceRegistryError("RuntimeServiceCatalog requires a ServiceRegistry")
        self._registry = registry if registry is not None else ServiceRegistry()
        self._declare()

    def _declare(self) -> None:
        for descriptor in runtime_service_descriptors():
            if descriptor.name in self._registry:
                continue
            self._registry.register(descriptor, provider=lambda kind=descriptor.name: kind)
        self._registry.validate()

    @property
    def registry(self) -> ServiceRegistry:
        """The underlying Foundation service registry (the single declaration home)."""
        return self._registry

    @property
    def names(self) -> tuple[str, ...]:
        """Every runtime-service contract name (deterministic order)."""
        return tuple(kind.service_name for kind in all_runtime_service_kinds())

    def startup_order(self) -> tuple[str, ...]:
        """The deterministic dependency-honest startup order of the runtime services."""
        ordered = self._registry.startup_order()
        service_names = set(self.names)
        return tuple(name for name in ordered if name in service_names)

    def view(self, kind: RuntimeServiceKind) -> RuntimeServiceView:
        """Return a read projection of a declared runtime service (fail-closed)."""
        if not isinstance(kind, RuntimeServiceKind):
            raise RuntimeServiceRegistryError("view requires a RuntimeServiceKind")
        return RuntimeServiceView(
            kind=kind,
            service_name=kind.service_name,
            capabilities=_CAPABILITY_ANCHORS[kind],
        )

    def views(self) -> tuple[RuntimeServiceView, ...]:
        """Every runtime-service view in deterministic order."""
        return tuple(self.view(kind) for kind in all_runtime_service_kinds())

    def __len__(self) -> int:
        return len(self.names)

    def to_dict(self) -> dict[str, Any]:
        return {
            "service_count": len(self.names),
            "startup_order": list(self.startup_order()),
            "services": [view.to_dict() for view in self.views()],
        }


__all__ = [
    "runtime_service_descriptor",
    "runtime_service_descriptors",
    "RuntimeServiceCatalog",
]
