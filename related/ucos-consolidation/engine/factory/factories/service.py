"""TASK-000042 — ServiceFactory (EPIC-006). Serves the BP-SERVICE blueprint class."""

from __future__ import annotations

from engine.compiler.ir import BlueprintFamily
from engine.factory.factories.base import BaseFactory


class ServiceFactory(BaseFactory):
    """Generation factory for the BP-SERVICE blueprint class."""

    blueprint_class = BlueprintFamily.SERVICE
    factory_name = "service-factory"
    description = "Generates service units from BP-SERVICE blueprints."


__all__ = ["ServiceFactory"]
