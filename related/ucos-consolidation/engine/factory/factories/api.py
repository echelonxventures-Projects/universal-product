"""TASK-000042 — ApiFactory (EPIC-006). Serves the BP-API blueprint class."""

from __future__ import annotations

from engine.compiler.ir import BlueprintFamily
from engine.factory.factories.base import BaseFactory


class ApiFactory(BaseFactory):
    """Generation factory for the BP-API blueprint class."""

    blueprint_class = BlueprintFamily.API
    factory_name = "api-factory"
    description = "Generates API surfaces from BP-API blueprints."


__all__ = ["ApiFactory"]
