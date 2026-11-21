"""TASK-000038 — Factory Layer error taxonomy (EPIC-006).

The Factory Layer reuses the EC-1 Foundation error discipline (TASK-000006):
every error is rooted in :class:`FoundationError`, carries a stable,
category-prefixed ``code`` and structured, non-secret ``context`` so failures are
auditable (PL-02, IP-12) and machine-consumable.

The Factory Layer is a *thin, additive orchestration model* over the certified
compiler and runtime subsystems: it classifies blueprints from registry metadata,
routes them to a registered factory, and executes the existing pipeline. It
invents no behaviour (TP-01) — a class it cannot classify, a factory it cannot
resolve, or a duplicate registration all fail loudly with a specific error.
"""

from __future__ import annotations

from engine.foundation.obs.errors import FoundationError


class FactoryError(FoundationError):
    """Base class for all Factory Layer errors (EPIC-006)."""

    code = "FAC-000"


class ClassificationError(FactoryError):
    """A blueprint's class could not be derived from its metadata (TASK-000039)."""

    code = "FAC-CLASS-001"


class FactoryRegistrationError(FactoryError):
    """A factory registration is invalid or duplicates an existing class (TASK-000040)."""

    code = "FAC-REG-001"


class FactoryNotFoundError(FactoryError):
    """No factory is registered for a requested blueprint class (TASK-000040)."""

    code = "FAC-REG-404"


class OrchestrationError(FactoryError):
    """The generation orchestrator could not complete a request (TASK-000041)."""

    code = "FAC-ORCH-001"


class BlueprintResolutionError(FactoryError):
    """A blueprint id could not be resolved to an input document (TASK-000041)."""

    code = "FAC-BP-404"


class GenerationPhaseError(FactoryError):
    """A generation phase declaration is invalid, or no order exists for it (WP-UCDA-018).

    Raised for a duplicate phase key, a second delegation seam, a requirement naming an
    undeclared phase, a declared cycle, or an absent seam. The generation runtime derives
    its order from these declarations, so an unusable declaration is refused rather than
    silently ordered — a runtime that cannot say what order it runs in has no evidentiary
    value.
    """

    code = "FAC-PHASE-001"


__all__ = [
    "FactoryError",
    "ClassificationError",
    "FactoryRegistrationError",
    "FactoryNotFoundError",
    "OrchestrationError",
    "BlueprintResolutionError",
    "GenerationPhaseError",
]
