"""TASK-000042 — DataFactory (EPIC-006). Serves the BP-DATA blueprint class."""

from __future__ import annotations

from engine.compiler.ir import BlueprintFamily
from engine.factory.factories.base import BaseFactory


class DataFactory(BaseFactory):
    """Generation factory for the BP-DATA blueprint class (fully compilable)."""

    blueprint_class = BlueprintFamily.DATA
    factory_name = "data-factory"
    description = "Generates persistent data entities from BP-DATA blueprints."


__all__ = ["DataFactory"]
