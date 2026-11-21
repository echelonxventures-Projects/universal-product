"""TASK-000042 — ApplicationFactory (EPIC-006). Serves the BP-APPLICATION class."""

from __future__ import annotations

from engine.compiler.ir import BlueprintFamily
from engine.factory.factories.base import BaseFactory


class ApplicationFactory(BaseFactory):
    """Generation factory for the BP-APPLICATION blueprint class."""

    blueprint_class = BlueprintFamily.APPLICATION
    factory_name = "application-factory"
    description = "Generates composed applications from BP-APPLICATION blueprints."


__all__ = ["ApplicationFactory"]
