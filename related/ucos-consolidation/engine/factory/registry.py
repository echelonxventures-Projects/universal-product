"""TASK-000040 — Factory Registry (EPIC-006).

A deterministic, in-memory registry mapping a blueprint class to the factory that
serves it. Registration is **explicit** — there are **no dynamic imports** and no
discovery-by-scanning; a caller constructs factories and registers them, so the
resolved set is a pure function of the registration calls.

Guarantees:
    * **Deterministic ordering** — listings are always sorted by blueprint class.
    * **Immutable registration records** — the stored record is the frozen
      :class:`~engine.factory.contracts.FactoryDescriptor`.
    * **Duplicate protection** — two factories cannot claim the same class.
    * **Capability discovery** — capabilities are enumerable without executing.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from engine.compiler.ir import BlueprintFamily
from engine.factory.classifier import BlueprintClassification
from engine.factory.contracts import FactoryCapability, FactoryDescriptor
from engine.factory.errors import FactoryNotFoundError, FactoryRegistrationError
from engine.foundation.obs.logging import get_logger

if TYPE_CHECKING:  # pragma: no cover - typing only
    from engine.factory.factories.base import Factory

_logger = get_logger("factory.registry")


def _coerce_class(
    blueprint_class: BlueprintFamily | BlueprintClassification | str,
) -> BlueprintFamily:
    if isinstance(blueprint_class, BlueprintClassification):
        return blueprint_class.blueprint_class
    if isinstance(blueprint_class, BlueprintFamily):
        return blueprint_class
    if isinstance(blueprint_class, str):
        try:
            return BlueprintFamily(blueprint_class)
        except ValueError as exc:
            raise FactoryNotFoundError(
                "unknown blueprint class", blueprint_class=blueprint_class
            ) from exc
    raise FactoryNotFoundError(
        "unsupported blueprint class key", got=type(blueprint_class).__name__
    )


class FactoryRegistry:
    """A deterministic registry of factories keyed by blueprint class."""

    __slots__ = ("_factories",)

    def __init__(self) -> None:
        self._factories: dict[BlueprintFamily, Factory] = {}

    def register_factory(self, factory: Factory) -> FactoryDescriptor:
        """Register ``factory`` for its declared class; refuse duplicates.

        Returns the immutable :class:`FactoryDescriptor` registration record.
        """
        descriptor = factory.descriptor
        try:
            family = BlueprintFamily(descriptor.blueprint_class)
        except ValueError as exc:
            raise FactoryRegistrationError(
                "factory declares an unknown blueprint class",
                factory=descriptor.name,
                blueprint_class=descriptor.blueprint_class,
            ) from exc
        if family in self._factories:
            raise FactoryRegistrationError(
                "a factory is already registered for this blueprint class",
                blueprint_class=family.value,
                existing=self._factories[family].descriptor.name,
                attempted=descriptor.name,
            )
        self._factories[family] = factory
        _logger.info(
            "factory.registered",
            factory=descriptor.name,
            blueprint_class=family.value,
        )
        return descriptor

    def resolve_factory(
        self, blueprint_class: BlueprintFamily | BlueprintClassification | str
    ) -> Factory:
        """Return the factory registered for ``blueprint_class`` or raise."""
        family = _coerce_class(blueprint_class)
        factory = self._factories.get(family)
        if factory is None:
            raise FactoryNotFoundError(
                "no factory is registered for this blueprint class",
                blueprint_class=family.value,
                registered=[f.value for f in sorted(self._factories, key=lambda x: x.value)],
            )
        return factory

    def has_factory(self, blueprint_class: BlueprintFamily | BlueprintClassification | str) -> bool:
        """True iff a factory is registered for ``blueprint_class``."""
        return _coerce_class(blueprint_class) in self._factories

    def list_factories(self) -> tuple[FactoryDescriptor, ...]:
        """All registration records, in deterministic blueprint-class order."""
        return tuple(
            self._factories[family].descriptor
            for family in sorted(self._factories, key=lambda f: f.value)
        )

    def capabilities(self) -> tuple[FactoryCapability, ...]:
        """All factory capabilities, in deterministic order (capability discovery)."""
        return tuple(descriptor.capability for descriptor in self.list_factories())

    def __len__(self) -> int:
        return len(self._factories)


__all__ = ["FactoryRegistry"]
