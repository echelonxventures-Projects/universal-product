"""EC2-TASK-000165 — Runtime Descriptor Discovery & Inspection (EC2-EPIC-012).

The deterministic, read-only **descriptor catalog** — the runtime home of Program Surface
#11 *Runtime Operations* descriptor **discovery** and **inspection** (PC-11). It is a pure
read view over the append-only
:class:`~platform.runtime_operations.operations.RuntimeOperationRegistry`: it discovers the
deploy/rollback descriptors of governed operations (optionally scoped to a runtime unit,
kind, or environment) and inspects a single operation's descriptor as a faithful
projection of the certified EC-1 output (P6). It generates nothing and mutates nothing —
descriptors are produced only by the EC-1 façade and recorded only by the orchestration
engine; this catalog surfaces what already exists, deterministically (P5).
"""

from __future__ import annotations

from platform.foundation.contracts import content_hash
from platform.runtime_operations.contracts import (
    DeploymentDescriptorView,
    RollbackDescriptorView,
    RuntimeOperationKind,
    RuntimeOperationRecord,
)
from platform.runtime_operations.errors import RuntimeDescriptorError
from platform.runtime_operations.operations import RuntimeOperationRegistry
from typing import Any


class DescriptorCatalog:
    """A deterministic, read-only discovery + inspection catalog over recorded descriptors."""

    __slots__ = ("_registry",)

    def __init__(self, registry: RuntimeOperationRegistry) -> None:
        if not isinstance(registry, RuntimeOperationRegistry):
            raise RuntimeDescriptorError("DescriptorCatalog requires a RuntimeOperationRegistry")
        self._registry = registry

    def discover(
        self,
        *,
        runtime_id: str | None = None,
        kind: RuntimeOperationKind | None = None,
        environment: str | None = None,
    ) -> tuple[RuntimeOperationRecord, ...]:
        """Discover governed operations carrying descriptors, optionally scoped (stable order)."""
        return self._registry.discover(runtime_id=runtime_id, kind=kind, environment=environment)

    def deployment_views(
        self, *, runtime_id: str | None = None
    ) -> tuple[DeploymentDescriptorView, ...]:
        """Discover deployment descriptor views, optionally scoped to a runtime unit."""
        return tuple(
            record.deployment_view()
            for record in self._registry.discover(
                runtime_id=runtime_id, kind=RuntimeOperationKind.DEPLOY
            )
        )

    def rollback_views(
        self, *, runtime_id: str | None = None
    ) -> tuple[RollbackDescriptorView, ...]:
        """Discover rollback descriptor views, optionally scoped to a runtime unit."""
        return tuple(
            record.rollback_view()
            for record in self._registry.discover(
                runtime_id=runtime_id, kind=RuntimeOperationKind.ROLLBACK
            )
        )

    def inspect(self, operation_id: str) -> DeploymentDescriptorView | RollbackDescriptorView:
        """Inspect a single operation's governing descriptor as a read view (fail-closed)."""
        record = self._registry.get(operation_id)
        if record.kind is RuntimeOperationKind.DEPLOY:
            return record.deployment_view()
        return record.rollback_view()

    def count(self) -> dict[str, int]:
        """A deterministic deploy/rollback descriptor census (delegates to the registry)."""
        return self._registry.count_by_kind()

    def to_dict(self) -> dict[str, Any]:
        return {
            "deployment_descriptors": [v.to_dict() for v in self.deployment_views()],
            "rollback_descriptors": [v.to_dict() for v in self.rollback_views()],
            "census": self.count(),
        }

    def fingerprint(self) -> str:
        return content_hash(self.to_dict())


__all__ = ["DescriptorCatalog"]
