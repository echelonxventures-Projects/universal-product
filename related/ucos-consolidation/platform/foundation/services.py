"""EC2-TASK-000058 — Platform Service Registry (EC2-EPIC-001).

The deterministic seam through which every EC-2 platform service is declared,
discovered, and resolved. A service is *declared* by an immutable
:class:`ServiceDescriptor` (identity + published contract + declared dependencies +
provided capabilities) and *provided* by a lazily-instantiated factory. The registry
is additive, in-memory, and dependency-free.

Guarantees:
    * **Deterministic** — services list and resolve in a stable order (sorted by
      name); registration order does not affect observable behavior.
    * **Contract-first (AR-03/PL-05)** — each service publishes a versioned
      :class:`Contract` into the platform contract registry on registration.
    * **Dependency-honest (IP-04)** — a service declaring a dependency on an
      unregistered service is rejected; the registry can order all services via the
      dependency model (:mod:`platform.foundation.dependencies`).
    * **Fail-closed** — duplicate registration and unknown resolution raise.

The registry stores *declarations and factories only*; it starts nothing and
implements no service (no portal/workspace/dashboard/runtime — those are later
epics). It is the reusable substrate they register into.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field
from platform.foundation.dependencies import DependencyGraph
from platform.foundation.errors import (
    ServiceRegistrationError,
    ServiceResolutionError,
)
from typing import Any

from engine.foundation.contracts.contract import Contract, ContractRegistry

#: A service provider is a zero-argument factory returning the service instance.
ServiceProvider = Callable[[], Any]


@dataclass(frozen=True, slots=True)
class ServiceDescriptor:
    """An immutable declaration of a platform service."""

    name: str
    contract: Contract
    capabilities: tuple[str, ...] = ()
    dependencies: tuple[str, ...] = ()
    description: str = ""

    def __post_init__(self) -> None:
        if not isinstance(self.name, str) or not self.name:
            raise ServiceRegistrationError("service name is required")
        if not isinstance(self.contract, Contract):
            raise ServiceRegistrationError("service must publish a Contract", name=self.name)

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "contract": {"name": self.contract.name, "version": str(self.contract.version)},
            "capabilities": list(self.capabilities),
            "dependencies": list(self.dependencies),
            "description": self.description,
        }


@dataclass(frozen=True, slots=True)
class _Registration:
    descriptor: ServiceDescriptor
    provider: ServiceProvider | None = None
    _instance_box: list[Any] = field(default_factory=list, compare=False)


class ServiceRegistry:
    """A deterministic, additive registry of platform service declarations."""

    __slots__ = ("_registrations", "_contracts")

    def __init__(self, contracts: ContractRegistry | None = None) -> None:
        self._registrations: dict[str, _Registration] = {}
        self._contracts = contracts if contracts is not None else ContractRegistry()

    @property
    def contracts(self) -> ContractRegistry:
        """The platform contract registry these services publish into."""
        return self._contracts

    def register(
        self,
        descriptor: ServiceDescriptor,
        provider: ServiceProvider | None = None,
    ) -> ServiceDescriptor:
        """Register a service declaration and publish its contract (fail-closed)."""
        if descriptor.name in self._registrations:
            raise ServiceRegistrationError("service already registered", name=descriptor.name)
        # Publish the contract (reuses EC-1 versioning discipline; may raise).
        self._contracts.register(descriptor.contract)
        self._registrations[descriptor.name] = _Registration(
            descriptor=descriptor, provider=provider
        )
        return descriptor

    def __contains__(self, name: str) -> bool:
        return name in self._registrations

    def __len__(self) -> int:
        return len(self._registrations)

    @property
    def names(self) -> tuple[str, ...]:
        return tuple(sorted(self._registrations))

    def descriptor(self, name: str) -> ServiceDescriptor:
        """Return a service's descriptor (raises if absent)."""
        return self._require(name).descriptor

    def descriptors(self) -> tuple[ServiceDescriptor, ...]:
        """Every descriptor in deterministic (name) order."""
        return tuple(self._registrations[n].descriptor for n in self.names)

    def resolve(self, name: str) -> Any:
        """Resolve a service instance via its provider (lazy, memoized)."""
        registration = self._require(name)
        if registration.provider is None:
            raise ServiceResolutionError("service has no provider factory", name=name)
        if not registration._instance_box:
            registration._instance_box.append(registration.provider())
        return registration._instance_box[0]

    def dependency_graph(self) -> DependencyGraph:
        """Build the dependency graph over registered services (validated)."""
        graph = DependencyGraph()
        for name in self.names:
            graph.add(name, self._registrations[name].descriptor.dependencies)
        graph.validate()
        return graph

    def startup_order(self) -> tuple[str, ...]:
        """Return the deterministic dependency-honest startup order of services."""
        return self.dependency_graph().topological_order()

    def validate(self) -> None:
        """Validate every declared dependency resolves to a registered service."""
        known = set(self._registrations)
        for name in self.names:
            for dep in self._registrations[name].descriptor.dependencies:
                if dep not in known:
                    raise ServiceRegistrationError(
                        "service declares an unregistered dependency",
                        name=name,
                        missing=dep,
                    )
        # Cycle check via the dependency model.
        self.dependency_graph()

    def _require(self, name: str) -> _Registration:
        registration = self._registrations.get(name)
        if registration is None:
            raise ServiceResolutionError("no such service", name=name)
        return registration

    def to_dict(self) -> dict[str, Any]:
        return {
            "service_count": len(self._registrations),
            "services": [d.to_dict() for d in self.descriptors()],
        }


__all__ = ["ServiceProvider", "ServiceDescriptor", "ServiceRegistry"]
