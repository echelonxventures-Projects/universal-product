"""TASK-000042 — Common factory contract (EPIC-006).

Every factory implements the **same** contract and shares the **same** execution
path. A factory is a thin strategy object that binds a blueprint class to a
:class:`~engine.factory.contracts.FactoryCapability`; it holds **no** pipeline
logic of its own. Generation is delegated, unchanged, to the orchestrator's
execution path (:class:`FactoryExecution`), so there is exactly one implementation
of compile + assemble across the whole layer (no duplicated pipeline logic, no
special-case paths).

    * :class:`FactoryExecution` — the structural interface the orchestrator
      satisfies; ``execute(context)`` runs the certified compiler + runtime path.
    * :class:`ExecutionContext` — the immutable inputs handed to an execution.
    * :class:`Factory` — the structural contract every factory satisfies.
    * :class:`BaseFactory` — the shared implementation; concrete factories only
      declare their class, name, and capability.

The stage vocabulary a factory advertises is **derived**, not frozen:
:func:`~engine.factory.phases.generation_stages` computes it from the declared phase graph
on every construction. This module previously carried a ``DEFAULT_STAGES`` tuple, which was
a second declaration of the runtime order and could drift from the order actually executed
— the defect recorded as ``DEC-MCOS-14`` and closed by ``WP-UCDA-018``. What a factory
advertises is now, by construction, what the runtime runs.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any, ClassVar, Protocol, runtime_checkable

from engine.compiler.ir import BlueprintFamily
from engine.factory.classifier import BlueprintClassification
from engine.factory.contracts import (
    FactoryCapability,
    FactoryDescriptor,
    FactoryRequest,
    FactoryResult,
)
from engine.factory.phases import generation_stages


@dataclass(frozen=True, slots=True)
class ExecutionContext:
    """The immutable inputs for one generation execution."""

    request: FactoryRequest
    document: Mapping[str, Any]
    classification: BlueprintClassification
    descriptor: FactoryDescriptor


@runtime_checkable
class FactoryExecution(Protocol):
    """The execution path a factory delegates to (satisfied by the orchestrator)."""

    def execute(self, context: ExecutionContext) -> FactoryResult:  # pragma: no cover
        ...


@runtime_checkable
class Factory(Protocol):
    """The common contract every factory satisfies."""

    @property
    def descriptor(self) -> FactoryDescriptor:  # pragma: no cover - interface
        ...

    @property
    def capability(self) -> FactoryCapability:  # pragma: no cover - interface
        ...

    def generate(
        self, context: ExecutionContext, execution: FactoryExecution
    ) -> FactoryResult:  # pragma: no cover - interface
        ...


class BaseFactory:
    """Shared factory implementation — concrete factories declare only their class.

    Subclasses set :attr:`blueprint_class` and :attr:`factory_name` (and optionally
    :attr:`description`). All generation is delegated to the shared orchestrator
    execution path, so no factory contains or duplicates pipeline logic.
    """

    #: The blueprint class this factory serves (set by subclasses).
    blueprint_class: ClassVar[BlueprintFamily]
    #: The registered factory name (set by subclasses).
    factory_name: ClassVar[str]
    #: A human-readable capability description (optional).
    description: ClassVar[str] = ""

    __slots__ = ("_descriptor",)

    def __init__(self) -> None:
        cls = type(self)
        if not isinstance(getattr(cls, "blueprint_class", None), BlueprintFamily):
            raise TypeError(f"{cls.__name__} must declare a BlueprintFamily blueprint_class")
        if not getattr(cls, "factory_name", ""):
            raise TypeError(f"{cls.__name__} must declare a factory_name")
        capability = FactoryCapability(
            blueprint_class=cls.blueprint_class.value,
            stages=generation_stages(),
            description=cls.description or f"Generation factory for {cls.blueprint_class.value}.",
        )
        self._descriptor = FactoryDescriptor(
            name=cls.factory_name,
            blueprint_class=cls.blueprint_class.value,
            capability=capability,
        )

    @property
    def descriptor(self) -> FactoryDescriptor:
        return self._descriptor

    @property
    def capability(self) -> FactoryCapability:
        return self._descriptor.capability

    def generate(self, context: ExecutionContext, execution: FactoryExecution) -> FactoryResult:
        """Delegate generation to the shared orchestrator execution path."""
        return execution.execute(context)


__all__ = [
    "ExecutionContext",
    "FactoryExecution",
    "Factory",
    "BaseFactory",
]
