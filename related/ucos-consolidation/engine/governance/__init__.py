"""EPIC-VAL-003 — Repository Governance Pipeline (Terminal T3).

Public API surface for the canonical **Repository Governance Pipeline**: the
end-to-end constitutional governance flow that **integrates the existing engines**
(it creates no new validation, certification, or acceptance logic) into one
deterministic, fail-closed, traceable determination:

    Validation (EPIC-007) → Certification (EPIC-008) → Acceptance (EPIC-VAL-002)
        → Repository Readiness → Architecture Freeze

For a :class:`GovernanceInput` (a non-empty set of :class:`GovernanceUnit` plus the
repository-level acceptance facts) the pipeline reuses the real Validation,
Certification, and Acceptance engines and emits a single canonical
:class:`RepositoryGovernanceReport` bundling every unified artifact the mission
requires:

    * unified **governance evidence** (:class:`GovernanceEvidence`) — the closed
      Validation → Certification → Acceptance → Ledger evidence chain,
    * the unified **repository decision** (:class:`RepositoryDecision`) — fail-closed
      GOVERNED / NOT-GOVERNED,
    * the unified **repository certificate** (the immutable Acceptance Record),
    * the unified **repository acceptance** (the Acceptance Decision),
    * the unified **repository readiness** (:class:`RepositoryReadiness`),
    * the architecture **freeze recommendation** (:class:`FreezeRecommendation`).

Everything is deterministic (IMP-007 §5 — an identical input yields a byte-identical,
tamper-evident report), fail-closed (GOVERNED iff every stage passed), and traceable
(every artifact references its subordinate artifacts by content hash). Governance
records **engineering readiness only** and carries the EC-1 provisional-state
disclosure — it confers no constitutional finality or authority (DE-05 / IP-01).
"""

from __future__ import annotations

from engine.governance.contracts import (
    ACCEPTANCE_STAGE,
    CERTIFICATION_STAGE,
    GOVERNANCE_AUTHORITY,
    GOVERNANCE_CONTRACT_VERSION,
    GOVERNANCE_STAGES,
    GOVERNANCE_STANDARD,
    GOVERNANCE_STANDARD_VERSION,
    VALIDATION_STAGE,
    GovernanceInput,
    GovernanceStatus,
    GovernanceUnit,
    RepositoryDecision,
    StageOutcome,
    canonical_json,
    content_hash,
)
from engine.governance.errors import (
    GovernanceInputError,
    GovernanceIntegrityError,
    GovernanceLayerError,
    GovernanceRejectedError,
)
from engine.governance.evidence import (
    EVIDENCE_FORMAT,
    GovernanceEvidence,
    build_governance_evidence,
)
from engine.governance.freeze import (
    DO_NOT_FREEZE,
    FREEZE,
    FREEZE_FORMAT,
    FreezeRecommendation,
    build_freeze_recommendation,
)
from engine.governance.pipeline import (
    RepositoryGovernancePipeline,
    enforce_governance,
    govern_repository,
)
from engine.governance.report import (
    REPORT_FORMAT,
    GovernedUnit,
    RepositoryGovernanceReport,
)

__all__ = [
    # contracts
    "GOVERNANCE_CONTRACT_VERSION",
    "GOVERNANCE_STANDARD",
    "GOVERNANCE_STANDARD_VERSION",
    "GOVERNANCE_AUTHORITY",
    "VALIDATION_STAGE",
    "CERTIFICATION_STAGE",
    "ACCEPTANCE_STAGE",
    "GOVERNANCE_STAGES",
    "canonical_json",
    "content_hash",
    "GovernanceStatus",
    "GovernanceUnit",
    "GovernanceInput",
    "StageOutcome",
    "RepositoryDecision",
    # evidence
    "GovernanceEvidence",
    "build_governance_evidence",
    "EVIDENCE_FORMAT",
    # freeze
    "FreezeRecommendation",
    "build_freeze_recommendation",
    "FREEZE_FORMAT",
    "FREEZE",
    "DO_NOT_FREEZE",
    # report
    "GovernedUnit",
    "RepositoryGovernanceReport",
    "REPORT_FORMAT",
    # pipeline
    "RepositoryGovernancePipeline",
    "govern_repository",
    "enforce_governance",
    # errors
    "GovernanceLayerError",
    "GovernanceInputError",
    "GovernanceRejectedError",
    "GovernanceIntegrityError",
]
