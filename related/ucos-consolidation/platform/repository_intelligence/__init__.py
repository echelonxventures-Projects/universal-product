"""UCOS-EPIC-014 — Repository Intelligence (Terminal T5).

The platform-layer **repository intelligence** subsystem: a deterministic, fail-closed,
evidence-producing engine that continuously searches the repository and answers, from the
repository's own substrate, the eight questions a repository must never guess at —

    what exists · what it can do · what may be reused · what depends on what ·
    what is missing · what conflicts · what is duplicated · who owns it

— then graphs the answer, ranks what to do about it, validates it, and seals it into a
certificate. Its purpose is to make two rules mechanically enforceable rather than
aspirational: **never duplicate a capability**, and **everything must extend the existing
repository**.

Deliverables:

    * Repository Discovery, Capability Discovery, Reuse Discovery, Dependency Discovery,
      Gap Discovery, Conflict Discovery, Duplicate Detection and Ownership Discovery —
      the eight :class:`DiscoveryDimension` s of :mod:`~platform.repository_intelligence.discovery`.
    * the **Repository Graph** (:class:`RepositoryGraph`) with topological layering, cycle
      detection, change-impact profiles and DOT/Mermaid rendering.
    * the **Repository Intelligence Runtime** (:class:`RepositoryIntelligenceRuntime`) —
      idempotent re-scanning with drift detection and a determinism proof.
    * the **Repository Recommendation Engine** (:class:`RepositoryRecommendationEngine`),
      whose :meth:`~RepositoryRecommendationEngine.advise` is the never-duplicate guard:
      given a proposed capability it returns the existing one to reuse, extend or compose,
      and permits creation only when the repository genuinely has no candidate.
    * **Repository Validation** (:class:`RepositoryValidator`), which *composes* the
      certified :mod:`engine.acceptance` gate suite by supplying the
      :class:`~engine.acceptance.contracts.RepositorySubject` producer it never had.
    * **Repository Certification** (:class:`RepositoryCertificate`) — sealed, self-verifying,
      fail-closed.
    * the one-command CLI ``ucos-repo-intel``.

Reuse-over-reinvention, applied to itself (TP-05). This subsystem **composes and does not
duplicate**:

    * capability identity, category, authority and reuse policy → **UCOS-RIE-001**
      (``intelligence/rie``), consumed live when importable and via its sealed catalog
      artefact otherwise; never re-derived here.
    * repository adjudication → :mod:`engine.acceptance` gates, run over a projected subject.
    * content hashing and canonical serialization → :mod:`platform.foundation.contracts`.
    * the fail-closed outcome vocabulary (``Severity``/``FindingStatus``/``Verdict``) →
      :mod:`platform.validation_intelligence.contracts` (UCOS-EPIC-013).
    * the provisional-state disclosure → :mod:`engine.runtime.disclosure` (DE-05 / IP-01).

What is genuinely new — and had no owner before — is dependency discovery over the real
import graph, conflict discovery between code and declarations, duplicate detection over
content and public surfaces, ownership derivation, the repository graph, the reuse proof, the
recommendation engine, and repository-intelligence validation and certification.

It is strictly additive and read-only over the repository: it writes only its own artefacts
under its configured output directory, never modifies a code root or the certified corpus
(DP-03), asserts ``ENGINEERING-EXECUTION-ONLY`` authority, and records that repository
evidence remains the only authority. Runtime code is Python standard library only (TP-04).
"""

from __future__ import annotations

from platform.repository_intelligence.certification import (
    GATE_CLOSED,
    GATE_OPEN,
    RepositoryCertificate,
    certify,
)
from platform.repository_intelligence.config import (
    RepositoryIntelligenceConfig,
    load_config,
    parse_config,
    resolve_repository_root,
)
from platform.repository_intelligence.contracts import (
    CERTIFICATE_FORMAT,
    DEPENDENCY_GRAPH_FORMAT,
    DERIVED_TRUTH,
    EVIDENCE_FORMAT,
    INTELLIGENCE_REPORT_FORMAT,
    RECOMMENDATION_FORMAT,
    REPOSITORY_INTELLIGENCE_AUTHORITY,
    REPOSITORY_INTELLIGENCE_CONTRACT_VERSION,
    REPOSITORY_INTELLIGENCE_PROGRAMME,
    VALIDATION_REPORT_FORMAT,
    CapabilityRecord,
    DependencyEdge,
    Determination,
    DimensionResult,
    DiscoveryDimension,
    EdgeKind,
    Finding,
    FindingStatus,
    OwnershipRecord,
    Recommendation,
    RecommendationAction,
    RepositoryIntelligenceReport,
    RepositoryUnit,
    ReuseAssessment,
    ReuseProof,
    Severity,
    UnitKind,
    Verdict,
)
from platform.repository_intelligence.discovery import (
    DiscoveryOutcome,
    detect_duplicates,
    dimension_summary,
    discover_all,
    discover_capabilities,
    discover_conflicts,
    discover_dependencies,
    discover_gaps,
    discover_ownership,
    discover_repository,
    discover_reuse,
    implementation_capabilities,
)
from platform.repository_intelligence.errors import (
    DiscoveryError,
    GraphError,
    IntelligenceConfigurationError,
    RecommendationError,
    RepositoryCertificationError,
    RepositoryIntelligenceError,
    RepositoryValidationError,
    SubstrateError,
)
from platform.repository_intelligence.evidence import (
    ARTIFACT_NAMES,
    RepositoryIntelligenceEvidence,
    build_artifacts,
    build_evidence,
)
from platform.repository_intelligence.graph import (
    GraphNode,
    RepositoryGraph,
    build_graph,
    strongly_connected_components,
)
from platform.repository_intelligence.recommendation import (
    RepositoryRecommendationEngine,
    ReuseCandidate,
    build_recommendations,
)
from platform.repository_intelligence.runtime import (
    IntelligenceCycle,
    RepositoryIntelligenceRuntime,
    detect_drift,
    gate,
    run_once,
)
from platform.repository_intelligence.service import (
    RepositoryIntelligenceService,
    build_repository_intelligence_service,
)
from platform.repository_intelligence.substrate import (
    CATALOG_SOURCE_ABSENT,
    CATALOG_SOURCE_ARTIFACT,
    CATALOG_SOURCE_PACKAGE,
    Declarations,
    ModuleFact,
    RepositorySubstrate,
)
from platform.repository_intelligence.validation import (
    COMPOSED_GATES,
    RepositoryValidationReport,
    RepositoryValidator,
    RuleOutcome,
    validate_report,
)

__all__ = [
    # contracts
    "REPOSITORY_INTELLIGENCE_CONTRACT_VERSION",
    "REPOSITORY_INTELLIGENCE_PROGRAMME",
    "REPOSITORY_INTELLIGENCE_AUTHORITY",
    "DERIVED_TRUTH",
    "INTELLIGENCE_REPORT_FORMAT",
    "DEPENDENCY_GRAPH_FORMAT",
    "RECOMMENDATION_FORMAT",
    "VALIDATION_REPORT_FORMAT",
    "CERTIFICATE_FORMAT",
    "EVIDENCE_FORMAT",
    "DiscoveryDimension",
    "UnitKind",
    "ReuseProof",
    "EdgeKind",
    "RecommendationAction",
    "Determination",
    "Severity",
    "FindingStatus",
    "Verdict",
    "RepositoryUnit",
    "CapabilityRecord",
    "ReuseAssessment",
    "DependencyEdge",
    "OwnershipRecord",
    "Finding",
    "DimensionResult",
    "Recommendation",
    "RepositoryIntelligenceReport",
    # config
    "RepositoryIntelligenceConfig",
    "resolve_repository_root",
    "parse_config",
    "load_config",
    # substrate
    "CATALOG_SOURCE_PACKAGE",
    "CATALOG_SOURCE_ARTIFACT",
    "CATALOG_SOURCE_ABSENT",
    "ModuleFact",
    "Declarations",
    "RepositorySubstrate",
    # discovery
    "DiscoveryOutcome",
    "implementation_capabilities",
    "discover_repository",
    "discover_capabilities",
    "discover_reuse",
    "discover_dependencies",
    "discover_gaps",
    "discover_conflicts",
    "detect_duplicates",
    "discover_ownership",
    "discover_all",
    "dimension_summary",
    # graph
    "strongly_connected_components",
    "GraphNode",
    "RepositoryGraph",
    "build_graph",
    # recommendation
    "ReuseCandidate",
    "RepositoryRecommendationEngine",
    "build_recommendations",
    # validation
    "COMPOSED_GATES",
    "RuleOutcome",
    "RepositoryValidationReport",
    "RepositoryValidator",
    "validate_report",
    # certification
    "GATE_OPEN",
    "GATE_CLOSED",
    "RepositoryCertificate",
    "certify",
    # evidence
    "ARTIFACT_NAMES",
    "RepositoryIntelligenceEvidence",
    "build_evidence",
    "build_artifacts",
    # runtime
    "IntelligenceCycle",
    "RepositoryIntelligenceRuntime",
    "detect_drift",
    "run_once",
    "gate",
    # service
    "RepositoryIntelligenceService",
    "build_repository_intelligence_service",
    # errors
    "RepositoryIntelligenceError",
    "IntelligenceConfigurationError",
    "SubstrateError",
    "DiscoveryError",
    "GraphError",
    "RecommendationError",
    "RepositoryValidationError",
    "RepositoryCertificationError",
]
