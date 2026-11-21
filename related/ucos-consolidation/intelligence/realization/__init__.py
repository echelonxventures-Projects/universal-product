"""UCOS Ω∞ — Universal Realization Intelligence (URI) · URI-000001.

The subsystem that turns canonical knowledge into architecture, schemas, APIs, runtime,
deployment, tests and documentation — deterministically, governed, and traceably.

Four engines and seven generators, one pipeline::

    canonical knowledge store (UKDA)          the only input authority
        │  KnowledgeIntake      integrity-verified, sealed
        ▼
    1. PlanningEngine           targets × families → acyclic, waved plan
    2. CompositionEngine        steps → sealed units; conflicts + duplicates refused
    3. GenerationEngine         units → sealed artifacts (pure; no I/O)
    4. ImplementationEngine     artifacts → files (frozen-path guarded, idempotent)
        │
        ├─ RealizationGovernor  twelve fail-closed gates → GOVERNED | REJECTED
        ├─ TraceabilityEngine   closure verified in BOTH directions
        └─ evidence             consolidated, sealed bundle (TRACK-001)

Generators: Architecture · Schema · API · Runtime · Deployment · Test · Documentation.

Invariants honoured by construction:

* **Derive, never author.** Canonical knowledge is read-only here. Knowledge absent from
  the store is reported as a coverage gap, never invented (``UCKO-PRIN-0001``).
* **Compose, never duplicate.** Hashing composes :mod:`engine.knowledge.model`; the output
  sink composes :mod:`intelligence.rie.config`; the gate ladder composes UCIC-001.
* **Governance precedes materialization.** A rejected run writes nothing.
* **Deterministic.** No wall-clock, no environment reads, sorted collections everywhere:
  identical canonical knowledge ⇒ byte-identical artifacts (``UCKO-PRIN-0005``).
* **Additive.** Writes land only in the generated-artifact root and the evidence
  directory; ``engine/**``, ``platform/**`` and the frozen corpus are never touched
  (``UCKO-PRIN-0002`` / DP-03).
* **Traceable.** Every artifact records the generator, plan, step, unit, target, source
  canonical objects, and knowledge seal it was derived from.

Standard library only (``UCKO-PRIN-0003`` / TP-04, TP-05). Authority: NONE — derived truth.
"""

from __future__ import annotations

from engine.foundation.contracts.contract import Contract, Version
from intelligence.realization.composition import (
    CompositionEngine,
    CompositionFindings,
    compose_plan,
)
from intelligence.realization.config import CAPABILITY_ID, RealizationConfig
from intelligence.realization.contracts import (
    FAMILY_DEPENDENCIES,
    FAMILY_ORDER,
    ArtifactFamily,
    CompositionUnit,
    GeneratedArtifact,
    GenerationManifest,
    ImplementationRecord,
    Invariant,
    MaterializedFile,
    MediaKind,
    PlanStep,
    Provenance,
    RealizationComposition,
    RealizationPlan,
    RealizationStage,
    RealizationTarget,
    TraceEdge,
    family_order,
    register_family,
    registered_families,
)
from intelligence.realization.engine import (
    RealizationIntelligenceEngine,
    RealizationResult,
    realize,
)
from intelligence.realization.errors import (
    CompositionError,
    DeterminismError,
    EvidenceError,
    FrozenSurfaceError,
    GenerationError,
    GovernanceRejectedError,
    ImplementationError,
    KnowledgeIntakeError,
    PlanningError,
    RealizationError,
    TraceabilityError,
)
from intelligence.realization.evidence import (
    REQUIRED_FILES,
    RealizationEvidence,
    build_evidence,
    emit_evidence,
    verify_bundle,
)
from intelligence.realization.generation import GenerationEngine, generate_artifacts
from intelligence.realization.generators import (
    GENERATORS,
    ApiGenerator,
    ArchitectureGenerator,
    DeploymentGenerator,
    DocumentationGenerator,
    GenerationContext,
    Generator,
    RuntimeGenerator,
    SchemaGenerator,
    TestGenerator,
    generator_for,
    register_generator,
    registry_manifest,
)
from intelligence.realization.governance import (
    GATES,
    VERDICT_GOVERNED,
    VERDICT_REJECTED,
    GateOutcome,
    RealizationDecision,
    RealizationGovernor,
    enforce_realization,
)
from intelligence.realization.implementation import (
    ImplementationEngine,
    materialize_artifacts,
)
from intelligence.realization.knowledge import (
    NORMATIVE_KINDS,
    REALIZABLE_KINDS,
    KnowledgeIntake,
)
from intelligence.realization.planning import PlanningEngine, build_plan
from intelligence.realization.traceability import (
    TraceabilityEngine,
    TraceLedger,
    build_trace,
    coverage_summary,
)

__version__ = "1.0.0"

#: The versioned public contract of the Realization Intelligence subsystem (AR-03/PL-05).
REALIZATION_CONTRACT = Contract(
    name="intelligence.realization",
    version=Version(1, 0, 0),
    description=(
        "Universal Realization Intelligence: plan, compose, generate and implement "
        "architecture, schema, API, runtime, deployment, test and documentation artifacts "
        "from canonical knowledge — fail-closed governed and fully traceable."
    ),
)

__all__ = [
    "CAPABILITY_ID",
    "FAMILY_DEPENDENCIES",
    "FAMILY_ORDER",
    "GATES",
    "GENERATORS",
    "NORMATIVE_KINDS",
    "REALIZABLE_KINDS",
    "REALIZATION_CONTRACT",
    "REQUIRED_FILES",
    "VERDICT_GOVERNED",
    "VERDICT_REJECTED",
    "__version__",
    # engines
    "PlanningEngine",
    "CompositionEngine",
    "GenerationEngine",
    "ImplementationEngine",
    "RealizationIntelligenceEngine",
    "RealizationGovernor",
    "TraceabilityEngine",
    # generators
    "ApiGenerator",
    "ArchitectureGenerator",
    "DeploymentGenerator",
    "DocumentationGenerator",
    "RuntimeGenerator",
    "SchemaGenerator",
    "TestGenerator",
    "GenerationContext",
    "Generator",
    "generator_for",
    "register_family",
    "register_generator",
    "registered_families",
    "family_order",
    "registry_manifest",
    # value types
    "ArtifactFamily",
    "CompositionFindings",
    "CompositionUnit",
    "GeneratedArtifact",
    "GenerationManifest",
    "ImplementationRecord",
    "Invariant",
    "MaterializedFile",
    "MediaKind",
    "PlanStep",
    "Provenance",
    "RealizationComposition",
    "RealizationConfig",
    "RealizationDecision",
    "RealizationEvidence",
    "GateOutcome",
    "KnowledgeIntake",
    "RealizationPlan",
    "RealizationResult",
    "RealizationStage",
    "RealizationTarget",
    "TraceEdge",
    "TraceLedger",
    # functions
    "build_evidence",
    "build_plan",
    "build_trace",
    "compose_plan",
    "coverage_summary",
    "emit_evidence",
    "enforce_realization",
    "generate_artifacts",
    "materialize_artifacts",
    "realize",
    "verify_bundle",
    # errors
    "CompositionError",
    "DeterminismError",
    "EvidenceError",
    "FrozenSurfaceError",
    "GenerationError",
    "GovernanceRejectedError",
    "ImplementationError",
    "KnowledgeIntakeError",
    "PlanningError",
    "RealizationError",
    "TraceabilityError",
]
