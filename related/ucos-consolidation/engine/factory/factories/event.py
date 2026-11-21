"""TASK-000042 — EventFactory (EPIC-006). Serves the BP-EVENT blueprint class."""

from __future__ import annotations

from engine.compiler.ir import BlueprintFamily
from engine.factory.factories.base import BaseFactory


class EventFactory(BaseFactory):
    """Generation factory for the BP-EVENT blueprint class."""

    blueprint_class = BlueprintFamily.EVENT
    factory_name = "event-factory"
    description = "Generates event streams from BP-EVENT blueprints."


__all__ = ["EventFactory"]
