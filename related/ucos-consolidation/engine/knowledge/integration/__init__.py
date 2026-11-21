"""UCOS Ω∞ — Universal Constitutional Knowledge Integration (UKI), EPIC-UKDA-002.

Transforms the Universal Knowledge & Decision Architecture (UKDA, EPIC-UKDA) from an
isolated engine into the **mandatory constitutional knowledge backbone** of UCOS. It
is additive integration, not feature expansion: it reuses the UKDA store, graph,
intelligence, validation, and certification verbatim and wires them into a single,
fail-closed constitutional execution path so that every future capability first
consults constitutional knowledge before creating or modifying an artifact.

Deliverables (each a module in this package):

    * ``constitution``  — D1: the Universal Knowledge Integration Constitution
      (canonical layers, ``UKI-LAW-*``, and the constitutional sequence).
    * ``discovery``     — D2: the mandatory, deterministic Knowledge Discovery Protocol.
    * ``ownership``     — D3: the Canonical Ownership Protocol (exactly-one, fail-closed).
    * ``dependency``    — D4: Universal Dependency Graph Integration.
    * ``reuse``         — D5: the Knowledge Reuse Engine (reuse/extend/compose/create).
    * ``duplication``   — D6: the Duplicate Prevention Engine (fail-closed).
    * ``traceability``  — D7: the Constitutional Traceability Engine.
    * ``governance``    — D8: Knowledge Governance Integration.
    * ``registration``  — D9: Universal Registration Integration (no duplicates).
    * ``composition``   — D10: Autonomous Knowledge Composition.
    * ``pipeline``      — the Constitutional Execution Path binding all of the above.
    * ``cli``           — the operational command-line surface.

The layer is standard-library only (TP-04/TP-05), deterministic (IMP-007 §5), never
mutates the certified corpus (DP-03), and exposes its capability through the versioned
:data:`UKI_CONTRACT` (AR-03/PL-05), built additively on :data:`~engine.knowledge.UKDA_CONTRACT`.
"""

from __future__ import annotations

from engine.knowledge.integration.composition import AutonomousComposer, CompositionResult
from engine.knowledge.integration.constitution import (
    INTEGRATION_DECISION_OBJECT_ID,
    INTEGRATION_DECISION_RECORD_ID,
    INTEGRATION_LAWS,
    INTEGRATION_PRINCIPLE_ID,
    IntegrationConstitution,
    IntegrationLaw,
    constitution_objects,
    extend_base_with_constitution,
    integration_constitution,
)
from engine.knowledge.integration.contracts import (
    CANONICAL_LAYERS,
    CONSTITUTIONAL_SEQUENCE,
    UKI_CONTRACT,
    ArtifactIntent,
    ConstitutionalLayer,
    DiscoveryPhase,
    Disposition,
    Operation,
    SequenceStage,
)
from engine.knowledge.integration.dependency import DependencyIntegration, DependencyView
from engine.knowledge.integration.discovery import DiscoveryProtocol, DiscoveryResult
from engine.knowledge.integration.duplication import (
    DuplicatePreventionEngine,
    DuplicationReport,
    DuplicationViolation,
)
from engine.knowledge.integration.errors import (
    CompositionError,
    DiscoveryBypassError,
    DuplicationViolationError,
    GovernanceGroundingError,
    IntegrationError,
    IntentError,
    OwnershipViolationError,
    RegistrationConflictError,
    RepositoryDiscoveryError,
    ReuseBypassError,
    TraceabilityError,
)
from engine.knowledge.integration.governance import (
    GOVERNANCE_KINDS,
    GovernanceIntegration,
    GovernanceReference,
)
from engine.knowledge.integration.ownership import (
    CanonicalOwnership,
    OwnershipAssessment,
    OwnershipOverlap,
    OwnershipProtocol,
)
from engine.knowledge.integration.pipeline import (
    ConstitutionalDecision,
    ConstitutionalPipeline,
    Outcome,
    StageRecord,
    StageStatus,
)
from engine.knowledge.integration.registration import (
    RegistrationEntry,
    RegistrationIntegration,
    RegistrationPlan,
)
from engine.knowledge.integration.repository import (
    DEFAULT_REPOSITORY_OWNER,
    CommitRef,
    DependencySignal,
    DriftItem,
    FrontierItem,
    OwnershipSignal,
    RepositoryAssimilationEvidence,
    RepositoryAssimilator,
    RepositoryCheckpoint,
    RepositoryDiscoveryReport,
    RepositoryDriftReport,
    RepositoryFrontierReport,
    RepositoryProbe,
    RepositorySnapshot,
    RepositorySubject,
    RepositoryUnit,
    UnitAssimilation,
    Workstream,
    discover_checkpoints,
    discover_drift,
    discover_frontier,
    discover_repository,
    discover_workstreams,
    emit_evidence,
)
from engine.knowledge.integration.reuse import ReuseAssessment, ReuseCandidate, ReuseEngine
from engine.knowledge.integration.traceability import (
    TraceabilityChain,
    TraceabilityEngine,
    TraceStage,
)

__all__ = [
    "UKI_CONTRACT",
    # contracts
    "ArtifactIntent",
    "Operation",
    "DiscoveryPhase",
    "Disposition",
    "SequenceStage",
    "ConstitutionalLayer",
    "CANONICAL_LAYERS",
    "CONSTITUTIONAL_SEQUENCE",
    # constitution (D1)
    "IntegrationConstitution",
    "IntegrationLaw",
    "INTEGRATION_LAWS",
    "integration_constitution",
    "constitution_objects",
    "extend_base_with_constitution",
    "INTEGRATION_PRINCIPLE_ID",
    "INTEGRATION_DECISION_OBJECT_ID",
    "INTEGRATION_DECISION_RECORD_ID",
    # discovery (D2)
    "DiscoveryProtocol",
    "DiscoveryResult",
    # ownership (D3)
    "OwnershipProtocol",
    "CanonicalOwnership",
    "OwnershipOverlap",
    "OwnershipAssessment",
    # dependency (D4)
    "DependencyIntegration",
    "DependencyView",
    # reuse (D5)
    "ReuseEngine",
    "ReuseAssessment",
    "ReuseCandidate",
    # duplication (D6)
    "DuplicatePreventionEngine",
    "DuplicationReport",
    "DuplicationViolation",
    # traceability (D7)
    "TraceabilityEngine",
    "TraceabilityChain",
    "TraceStage",
    # governance (D8)
    "GovernanceIntegration",
    "GovernanceReference",
    "GOVERNANCE_KINDS",
    # registration (D9)
    "RegistrationIntegration",
    "RegistrationPlan",
    "RegistrationEntry",
    # composition (D10)
    "AutonomousComposer",
    "CompositionResult",
    # repository discovery & assimilation (EPIC-UKDA-004)
    "RepositoryProbe",
    "RepositoryAssimilator",
    "RepositorySnapshot",
    "RepositorySubject",
    "RepositoryUnit",
    "RepositoryDiscoveryReport",
    "RepositoryFrontierReport",
    "RepositoryDriftReport",
    "RepositoryAssimilationEvidence",
    "UnitAssimilation",
    "RepositoryCheckpoint",
    "Workstream",
    "FrontierItem",
    "DriftItem",
    "OwnershipSignal",
    "DependencySignal",
    "CommitRef",
    "DEFAULT_REPOSITORY_OWNER",
    "discover_repository",
    "discover_frontier",
    "discover_drift",
    "discover_checkpoints",
    "discover_workstreams",
    "emit_evidence",
    # pipeline (constitutional execution path)
    "ConstitutionalPipeline",
    "ConstitutionalDecision",
    "Outcome",
    "StageStatus",
    "StageRecord",
    # errors
    "IntegrationError",
    "OwnershipViolationError",
    "DuplicationViolationError",
    "DiscoveryBypassError",
    "ReuseBypassError",
    "GovernanceGroundingError",
    "RegistrationConflictError",
    "TraceabilityError",
    "CompositionError",
    "IntentError",
    "RepositoryDiscoveryError",
]
