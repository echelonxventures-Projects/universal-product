"""TASK-000042 — WorkflowFactory (EPIC-006). Serves the BP-WORKFLOW blueprint class."""

from __future__ import annotations

from engine.compiler.ir import BlueprintFamily
from engine.factory.factories.base import BaseFactory


class WorkflowFactory(BaseFactory):
    """Generation factory for the BP-WORKFLOW blueprint class."""

    blueprint_class = BlueprintFamily.WORKFLOW
    factory_name = "workflow-factory"
    description = "Generates orchestrated workflows from BP-WORKFLOW blueprints."


__all__ = ["WorkflowFactory"]
