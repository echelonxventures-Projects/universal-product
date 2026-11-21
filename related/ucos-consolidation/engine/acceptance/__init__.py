"""EPIC-VAL-002 — Universal Repository Acceptance Engine (Terminal T3).

Public API surface for the Repository Acceptance Engine: the **final acceptance
gate**. It determines whether an EPIC, feature, implementation, or repository may
legally be accepted, and — being fail-closed — nothing is accepted without it.

The engine assimilates the acceptance-relevant facts of a repository into a
normalized :class:`~engine.acceptance.contracts.RepositorySubject`, then runs the
universal acceptance suite over it:

    context assimilation · repository discovery · constitution discovery ·
    ownership · dependencies · reuse · implementation · validation · certification ·
    registration · traceability · coverage (100%) · zero missing · zero duplication ·
    zero overlap · repository reconciliation · cross-EPIC integration ·
    architecture consistency · repository health · repository freeze readiness.

It aggregates the gate findings into:

    * an **Acceptance Decision** (fail-closed ACCEPTED / REJECTED),
    * an **immutable, content-addressed Acceptance Certificate**,
    * an **Acceptance Evidence** record (closing the subject → decision → evidence
      chain),
    * a **Repository Readiness** report (the freeze-readiness verdict).

The layer is additive and constitutional: it invents no verdict (TP-01 — it only
aggregates the assimilated facts), mutates no subject, never writes to the certified
corpus (DP-03), and is fully deterministic (IMP-007 §5) — an identical subject yields
a byte-identical decision, certificate, evidence, and readiness report. Acceptance
records **engineering readiness only** and carries the EC-1 provisional-state
disclosure — it confers no constitutional finality or authority (DE-05 / IP-01).
"""

from __future__ import annotations

from engine.acceptance.contracts import (
    ACCEPTANCE_AUTHORITY,
    ACCEPTANCE_CONTRACT_VERSION,
    ACCEPTANCE_STANDARD,
    ACCEPTANCE_STANDARD_VERSION,
    REQUIRED_TRACE_STAGES,
    AcceptanceFinding,
    AcceptanceRecord,
    AcceptanceStatus,
    CoverageDimension,
    CoverageProfile,
    DependencyRecord,
    GateSeverity,
    GateStatus,
    IntegrationRecord,
    RepositoryHealth,
    RepositoryInventory,
    RepositorySubject,
    ReuseRecord,
    UnitRecord,
    canonical_json,
    content_hash,
)
from engine.acceptance.engine import (
    AcceptanceDecision,
    AcceptanceEngine,
    accept_repository,
    enforce_acceptance,
)
from engine.acceptance.errors import (
    AcceptanceIntegrityError,
    AcceptanceLayerError,
    AcceptanceRejectedError,
    RepositorySubjectError,
)
from engine.acceptance.evidence import (
    EVIDENCE_FORMAT,
    AcceptanceEvidence,
    build_acceptance_evidence,
)
from engine.acceptance.gates import (
    AcceptanceGate,
    ArchitectureConsistencyGate,
    CertificationGate,
    ConstitutionDiscoveryGate,
    ContextAssimilationGate,
    CoverageGate,
    CrossEpicIntegrationGate,
    DependenciesGate,
    FreezeReadinessGate,
    ImplementationGate,
    OwnershipGate,
    RegistrationGate,
    RepositoryDiscoveryGate,
    RepositoryHealthGate,
    RepositoryReconciliationGate,
    ReuseGate,
    TraceabilityGate,
    ValidationGate,
    ZeroDuplicationGate,
    ZeroMissingGate,
    ZeroOverlapGate,
    default_gates,
)
from engine.acceptance.readiness import (
    NOT_READY,
    READINESS_FORMAT,
    READY,
    RepositoryReadiness,
    build_repository_readiness,
)

__all__ = [
    # contracts
    "ACCEPTANCE_CONTRACT_VERSION",
    "ACCEPTANCE_STANDARD",
    "ACCEPTANCE_STANDARD_VERSION",
    "ACCEPTANCE_AUTHORITY",
    "REQUIRED_TRACE_STAGES",
    "canonical_json",
    "content_hash",
    "GateSeverity",
    "GateStatus",
    "AcceptanceStatus",
    "CoverageDimension",
    "CoverageProfile",
    "UnitRecord",
    "DependencyRecord",
    "ReuseRecord",
    "IntegrationRecord",
    "RepositoryInventory",
    "RepositoryHealth",
    "AcceptanceFinding",
    "RepositorySubject",
    "AcceptanceRecord",
    # gates
    "AcceptanceGate",
    "ContextAssimilationGate",
    "RepositoryDiscoveryGate",
    "ConstitutionDiscoveryGate",
    "OwnershipGate",
    "DependenciesGate",
    "ReuseGate",
    "ImplementationGate",
    "ValidationGate",
    "CertificationGate",
    "RegistrationGate",
    "TraceabilityGate",
    "CoverageGate",
    "ZeroMissingGate",
    "ZeroDuplicationGate",
    "ZeroOverlapGate",
    "RepositoryReconciliationGate",
    "CrossEpicIntegrationGate",
    "ArchitectureConsistencyGate",
    "RepositoryHealthGate",
    "FreezeReadinessGate",
    "default_gates",
    # decision engine
    "AcceptanceDecision",
    "AcceptanceEngine",
    "accept_repository",
    "enforce_acceptance",
    # evidence
    "AcceptanceEvidence",
    "build_acceptance_evidence",
    "EVIDENCE_FORMAT",
    # readiness
    "RepositoryReadiness",
    "build_repository_readiness",
    "READINESS_FORMAT",
    "READY",
    "NOT_READY",
    # errors
    "AcceptanceLayerError",
    "RepositorySubjectError",
    "AcceptanceRejectedError",
    "AcceptanceIntegrityError",
]
