"""EC-1 Factory Layer (EPIC-006) — a blueprint-type-independent generation model.

Public API surface for the Factory Layer: it turns the certified compiler
(EPIC-003) and runtime assembly (EPIC-005) subsystems into a **reusable factory**
that can orchestrate generation for multiple blueprint classes, driven entirely by
**registry metadata** and **blueprint classifications** — never by hard-coded
per-type logic or special-case execution paths.

The layer is additive and constitutional: it accesses the registry only through
the :class:`~engine.registry.adapter.RegistryAdapter`, never bypasses certification
or the compiler's family gates, writes to no frozen-corpus location, invents no
behaviour (a deferred class yields a faithful gap), and is fully deterministic
(IMP-007 §5). It preserves provenance, signatures, SBOM, dependency closure, and
the EC-1 provisional-state disclosure carried by the runtime units it assembles.

Tasks: TASK-000038 (contracts), TASK-000039 (classification), TASK-000040
(registry), TASK-000041 (orchestrator), TASK-000042 (factories), TASK-000043
(evidence), TASK-000044 (batch), TASK-000045 (tests).
"""

from __future__ import annotations

from engine.factory.batch import generate_many
from engine.factory.classifier import BlueprintClassification, resolve_blueprint_class
from engine.factory.contracts import (
    FACTORY_CONTRACT_VERSION,
    FactoryCapability,
    FactoryDescriptor,
    FactoryRequest,
    FactoryResult,
    GenerationStatus,
)
from engine.factory.errors import (
    BlueprintResolutionError,
    ClassificationError,
    FactoryError,
    FactoryNotFoundError,
    FactoryRegistrationError,
    GenerationPhaseError,
    OrchestrationError,
)
from engine.factory.evidence import (
    EVIDENCE_FORMAT,
    GenerationEvidence,
    build_generation_evidence,
)
from engine.factory.factories import (
    DEFAULT_FACTORIES,
    ApiFactory,
    ApplicationFactory,
    BaseFactory,
    DataFactory,
    ServiceFactory,
    build_default_registry,
)
from engine.factory.factories.base import (
    ExecutionContext,
    Factory,
    FactoryExecution,
)
from engine.factory.orchestrator import GenerationOrchestrator, GenerationState
from engine.factory.phases import (
    GenerationPhase,
    generation_order,
    generation_phases,
    generation_span,
    generation_stages,
    phase_graph,
    register_generation_phase,
    seam_phase,
    unregister_generation_phase,
)
from engine.factory.registry import FactoryRegistry

__all__ = [
    # contracts
    "FACTORY_CONTRACT_VERSION",
    "FactoryRequest",
    "FactoryResult",
    "FactoryCapability",
    "FactoryDescriptor",
    "GenerationStatus",
    # classification
    "resolve_blueprint_class",
    "BlueprintClassification",
    # registry
    "FactoryRegistry",
    # factories
    "BaseFactory",
    "Factory",
    "FactoryExecution",
    "ExecutionContext",
    "DataFactory",
    "ApiFactory",
    "ServiceFactory",
    "ApplicationFactory",
    "DEFAULT_FACTORIES",
    "build_default_registry",
    # orchestrator + batch
    "GenerationOrchestrator",
    "GenerationState",
    "generate_many",
    # declared phase graph (WP-UCDA-018) — the derived generation order
    "GenerationPhase",
    "generation_order",
    "generation_phases",
    "generation_span",
    "generation_stages",
    "phase_graph",
    "register_generation_phase",
    "seam_phase",
    "unregister_generation_phase",
    # evidence
    "GenerationEvidence",
    "build_generation_evidence",
    "EVIDENCE_FORMAT",
    # errors
    "FactoryError",
    "ClassificationError",
    "FactoryRegistrationError",
    "FactoryNotFoundError",
    "OrchestrationError",
    "BlueprintResolutionError",
    "GenerationPhaseError",
]
