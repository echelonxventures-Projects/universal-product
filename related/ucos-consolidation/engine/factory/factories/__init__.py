"""EC-1 Factory implementations (EPIC-006, TASK-000042).

The initial set of factories, all implementing the common contract and reusing the
single orchestrator execution path. :func:`build_default_registry` wires them into
a :class:`~engine.factory.registry.FactoryRegistry` with **explicit** registration
(no dynamic imports).
"""

from __future__ import annotations

from engine.factory.factories.api import ApiFactory
from engine.factory.factories.application import ApplicationFactory
from engine.factory.factories.base import (
    BaseFactory,
    ExecutionContext,
    Factory,
    FactoryExecution,
)
from engine.factory.factories.data import DataFactory
from engine.factory.factories.event import EventFactory
from engine.factory.factories.service import ServiceFactory
from engine.factory.factories.workflow import WorkflowFactory
from engine.factory.registry import FactoryRegistry

#: The factory set, in deterministic construction order following the closed
#: realization chain (Data → Event → API → Workflow → Service → Application;
#: REF-000 §19). One factory per registered BlueprintFamily realization class.
DEFAULT_FACTORIES: tuple[type[BaseFactory], ...] = (
    DataFactory,
    EventFactory,
    ApiFactory,
    WorkflowFactory,
    ServiceFactory,
    ApplicationFactory,
)


def build_default_registry() -> FactoryRegistry:
    """Construct a registry with the initial factories explicitly registered."""
    registry = FactoryRegistry()
    for factory_cls in DEFAULT_FACTORIES:
        registry.register_factory(factory_cls())
    return registry


__all__ = [
    "BaseFactory",
    "Factory",
    "FactoryExecution",
    "ExecutionContext",
    "DataFactory",
    "EventFactory",
    "ApiFactory",
    "WorkflowFactory",
    "ServiceFactory",
    "ApplicationFactory",
    "DEFAULT_FACTORIES",
    "build_default_registry",
]
