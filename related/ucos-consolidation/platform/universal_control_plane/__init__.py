"""UCOS-CTRL-000001 — Universal Control Plane public API.

The constitutional Engineering Operating System of the repository: it discovers
what the repository contains, governs and certifies every object it finds,
versions and tracks their evolution, registers its own engines under the same
rules, and records the whole determination durably enough to survive a restart.

Start at :class:`~platform.universal_control_plane.discovery.ControlPlane` — one
call composes every engine below from live repository state:

    >>> from platform.universal_control_plane import ControlPlane
    >>> plane = ControlPlane.discover()        # doctest: +SKIP
    >>> plane.completion().complete            # doctest: +SKIP

Import the engines directly when you need one in isolation; this module
re-exports the canonical surface so callers need only
``from platform.universal_control_plane import <Name>``.
"""

from __future__ import annotations

from platform.universal_control_plane.certification import (
    CertificationEngine,
    CertificationSubject,
    certification_subjects,
)
from platform.universal_control_plane.consumption import (
    Consumer,
    ConsumptionEngine,
    ConsumptionRecord,
    default_consumers,
)
from platform.universal_control_plane.discovery import (
    REQUIRED_ENGINES,
    CompletionReport,
    ControlPlane,
    GateCriterion,
    demo_markers_present,
)
from platform.universal_control_plane.durable import DurableJournal, ReplayedState
from platform.universal_control_plane.errors import (
    AssignmentError,
    CertificationStateError,
    ControlPlaneError,
    DeterminationError,
    DuplicateObjectError,
    EvidenceError,
    EvolutionError,
    GovernanceStateError,
    JournalError,
    LinkageError,
    ManifestError,
    ObjectNotFoundError,
    PromptRenderError,
    RegistrationError,
    ReplayError,
    SchedulerError,
    StateTransitionError,
    TruthDiscoveryError,
    VersionError,
)
from platform.universal_control_plane.evolution import EvolutionEngine, Observation
from platform.universal_control_plane.execution import (
    AssignmentEngine,
    Schedule,
    SchedulerEngine,
)
from platform.universal_control_plane.governance import (
    GovernanceEngine,
    GovernanceSubject,
    governance_subjects,
)
from platform.universal_control_plane.intelligence import (
    DashboardEngine,
    MetricsEngine,
    ProgressEngine,
)
from platform.universal_control_plane.linkage import LinkageEngine
from platform.universal_control_plane.manifest import (
    ArtifactClass,
    ControlPlaneManifest,
    DocumentRef,
    EngineTaxonomy,
    Rule,
    default_manifest,
    load_manifest,
)
from platform.universal_control_plane.ontology import (
    BLOCKING_SEVERITIES,
    CERTIFICATION_CERTIFIED,
    CERTIFICATION_NOT_CERTIFIED,
    CERTIFICATION_UNCERTIFIED,
    CRITERION_ADVISORY,
    CRITERION_BLOCKING,
    DEFAULT_LIFECYCLE,
    GOVERNANCE_GOVERNED,
    GOVERNANCE_NOT_GOVERNED,
    GOVERNANCE_UNGOVERNED,
    LIFECYCLE_ACTIVE,
    LIFECYCLE_ARCHIVED,
    LIFECYCLE_CANCELLED,
    LIFECYCLE_COMPLETE,
    LIFECYCLE_DRAFT,
    LIFECYCLE_PAUSED,
    PRIORITY_CRITICAL,
    PRIORITY_HIGH,
    PRIORITY_LOW,
    PRIORITY_MEDIUM,
    SEVERITY_CRITICAL,
    SEVERITY_HIGH,
    SEVERITY_LOW,
    SEVERITY_MEDIUM,
    VERSION_ARTIFACT,
    VERSION_CAPABILITY,
    VERSION_CERTIFICATION,
    VERSION_CONSTITUTIONAL,
    VERSION_GOVERNANCE,
    VERSION_IMPLEMENTATION,
    VERSION_KINDS,
    VERSION_SEMANTIC,
    AgentRecord,
    ArtifactRecord,
    Assignment,
    BacklogItem,
    Capability,
    CertificationState,
    ChangeRecord,
    CriterionOutcome,
    Decision,
    DependencyRecord,
    Determination,
    Evidence,
    Goal,
    GovernanceRecord,
    GovernanceViolation,
    HistoryEntry,
    JournalEntry,
    LinkageRecord,
    Metric,
    Milestone,
    Objective,
    OwnershipRecord,
    ProgressRecord,
    Prompt,
    RegistrationRecord,
    ReplayRecord,
    Universe,
    VersionRecord,
    Vision,
    payload_digest,
)
from platform.universal_control_plane.plan import BacklogEngine, PlanEngine, RoadmapEngine
from platform.universal_control_plane.prompt import PromptEngine
from platform.universal_control_plane.registration import (
    EngineDescriptor,
    RegistrationEngine,
    discover_engines,
)
from platform.universal_control_plane.registry import (
    AgentRegistry,
    CapabilityRegistry,
    DependencyRegistry,
    OwnershipRegistry,
)
from platform.universal_control_plane.state import StateEngine, Transition
from platform.universal_control_plane.trace import (
    DecisionEngine,
    DeterminationEngine,
    EvidenceEngine,
    HistoryEngine,
    ReplayEngine,
)
from platform.universal_control_plane.truth import (
    RepositoryTruth,
    RepositoryTruthEngine,
    TruthSource,
    build_truth_engine,
)
from platform.universal_control_plane.version import (
    SemanticVersion,
    VersionEngine,
    compare_versions,
)

#: Compatibility alias. The scheduler carried no ``Engine`` suffix before the
#: registration taxonomy began selecting on one; callers written against the old
#: name keep working, and the class is registered exactly once under the new one.
Scheduler = SchedulerEngine

__all__ = [
    # Errors
    "ControlPlaneError",
    "RegistrationError",
    "StateTransitionError",
    "ObjectNotFoundError",
    "DuplicateObjectError",
    "AssignmentError",
    "PromptRenderError",
    "DeterminationError",
    "ReplayError",
    "EvidenceError",
    "SchedulerError",
    "ManifestError",
    "TruthDiscoveryError",
    "GovernanceStateError",
    "CertificationStateError",
    "VersionError",
    "EvolutionError",
    "JournalError",
    "LinkageError",
    # Lifecycle, priority, severity and status constants
    "DEFAULT_LIFECYCLE",
    "LIFECYCLE_DRAFT",
    "LIFECYCLE_ACTIVE",
    "LIFECYCLE_PAUSED",
    "LIFECYCLE_COMPLETE",
    "LIFECYCLE_CANCELLED",
    "LIFECYCLE_ARCHIVED",
    "PRIORITY_CRITICAL",
    "PRIORITY_HIGH",
    "PRIORITY_MEDIUM",
    "PRIORITY_LOW",
    "SEVERITY_CRITICAL",
    "SEVERITY_HIGH",
    "SEVERITY_MEDIUM",
    "SEVERITY_LOW",
    "BLOCKING_SEVERITIES",
    "GOVERNANCE_GOVERNED",
    "GOVERNANCE_NOT_GOVERNED",
    "GOVERNANCE_UNGOVERNED",
    "CERTIFICATION_CERTIFIED",
    "CERTIFICATION_NOT_CERTIFIED",
    "CERTIFICATION_UNCERTIFIED",
    "CRITERION_BLOCKING",
    "CRITERION_ADVISORY",
    "VERSION_KINDS",
    "VERSION_SEMANTIC",
    "VERSION_CONSTITUTIONAL",
    "VERSION_ARTIFACT",
    "VERSION_CAPABILITY",
    "VERSION_IMPLEMENTATION",
    "VERSION_GOVERNANCE",
    "VERSION_CERTIFICATION",
    # Domain objects
    "Universe",
    "Capability",
    "OwnershipRecord",
    "DependencyRecord",
    "AgentRecord",
    "Vision",
    "Goal",
    "Objective",
    "Milestone",
    "BacklogItem",
    "Assignment",
    "Prompt",
    "Metric",
    "ProgressRecord",
    "Determination",
    "Decision",
    "Evidence",
    "HistoryEntry",
    "ReplayRecord",
    "ArtifactRecord",
    "GovernanceRecord",
    "GovernanceViolation",
    "CertificationState",
    "CriterionOutcome",
    "VersionRecord",
    "ChangeRecord",
    "RegistrationRecord",
    "LinkageRecord",
    "JournalEntry",
    "payload_digest",
    # Manifest
    "ControlPlaneManifest",
    "ArtifactClass",
    "DocumentRef",
    "EngineTaxonomy",
    "Rule",
    "default_manifest",
    "load_manifest",
    # Engines
    "StateEngine",
    "Transition",
    "CapabilityRegistry",
    "OwnershipRegistry",
    "DependencyRegistry",
    "AgentRegistry",
    "PlanEngine",
    "RoadmapEngine",
    "BacklogEngine",
    "SchedulerEngine",
    "Scheduler",
    "Schedule",
    "AssignmentEngine",
    "PromptEngine",
    "ProgressEngine",
    "MetricsEngine",
    "DashboardEngine",
    "DeterminationEngine",
    "DecisionEngine",
    "HistoryEngine",
    "ReplayEngine",
    "EvidenceEngine",
    "RepositoryTruthEngine",
    "RepositoryTruth",
    "TruthSource",
    "build_truth_engine",
    "GovernanceEngine",
    "GovernanceSubject",
    "governance_subjects",
    "CertificationEngine",
    "CertificationSubject",
    "certification_subjects",
    "VersionEngine",
    "SemanticVersion",
    "compare_versions",
    "EvolutionEngine",
    "Observation",
    "RegistrationEngine",
    "EngineDescriptor",
    "discover_engines",
    "LinkageEngine",
    "ConsumptionEngine",
    "Consumer",
    "ConsumptionRecord",
    "default_consumers",
    "DurableJournal",
    "ReplayedState",
    # Composition root and completion gate
    "ControlPlane",
    "CompletionReport",
    "GateCriterion",
    "REQUIRED_ENGINES",
    "demo_markers_present",
]
