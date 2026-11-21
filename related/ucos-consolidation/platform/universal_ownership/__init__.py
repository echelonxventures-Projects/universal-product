"""UCOS Ω∞ — Universal Ownership Framework (``platform.universal_ownership``).

**UCOS-UOF-001.** The reusable Foundation capability that replaces per-repository ownership
heuristics with a constitutional contract plus a pluggable evidence framework.

Three parts, each reusable by any project:

    * the **Ownership Declaration Contract** — seven constitutional requirements a claim
      must satisfy before the platform will call it canonical ownership;
    * the **evidence framework** — pluggable providers (governed assignment catalogues,
      definitional locators inside declared home zones, registration ledgers, and any
      future authority) ordered by declared precedence, never insertion order;
    * the **determination engine** — DECLARED, CONTESTED or UNRESOLVED, and nothing else.

The framework **never fabricates ownership**. Where evidence is absent it records a named
reason from a closed vocabulary, and :meth:`OwnershipDeterminationEngine.require_owner`
raises rather than inventing an owner to close a measurement. It does, however, **diagnose**
that absence: every record carries the candidate locators the declarations refused and the
declared eligibility rule that refused each one (:class:`EvidenceRefusal`). That turns an
undifferentiated residue into two separable populations — subjects needing a mechanical act
and subjects genuinely needing an authority — which is what
:attr:`GovernanceWorkload.governance_minimum` measures. Identities live in a disjoint
``UCOS-UOF*`` namespace, hold no wall-clock, and are content-addressed (IMP-007 §5).
"""

from __future__ import annotations

from platform.universal_ownership.bootstrap import (
    OWNERSHIP_SERVICE_NAME,
    bootstrap_ownership,
    default_evidence_providers,
    ownership_service_descriptor,
    register_ownership,
)
from platform.universal_ownership.contracts import (
    CONSTITUTIVE_EVIDENCE_KINDS,
    CORROBORATIVE_EVIDENCE_KINDS,
    OWNERSHIP_CONTRACT_VERSION,
    OWNERSHIP_CONTRACTS,
    OWNERSHIP_REQUIREMENTS,
    REASON_CONTEST_UNSETTLED,
    REASON_INELIGIBLE_ZONE,
    REASON_NO_CONSTITUTIVE_DECLARATION,
    REASON_NO_EVIDENCE,
    REASON_SUBJECT_NOT_REGISTERED,
    RULE_CONTEST_SETTLED,
    RULE_SOLE_DECLARATION,
    UNASSIGNED_OWNER,
    UNRESOLVED_REASONS,
    UOF_ID,
    EvidenceKind,
    OwnershipDeclaration,
    OwnershipDeclarationContract,
    OwnershipDetermination,
    OwnershipEvidence,
    OwnershipGranularity,
    OwnershipRecord,
    OwnershipRequirement,
    OwnershipStanding,
    default_ownership_contract,
    ownership_contract_names,
)
from platform.universal_ownership.determination import (
    CANONICAL_HOME_REFUSER,
    OwnershipDeterminationEngine,
)
from platform.universal_ownership.errors import (
    OwnershipContractError,
    OwnershipDeterminationError,
    OwnershipError,
    OwnershipEvidenceError,
    OwnershipFabricationError,
    OwnershipProviderConflictError,
)
from platform.universal_ownership.evidence import (
    DEFAULT_IDENTITY_LABELS,
    CallableEvidenceProvider,
    DeclaredAssignmentProvider,
    DeclaredIdentityProvider,
    DefinitionalLocatorProvider,
    EvidenceProviderDescriptor,
    EvidenceProviderRegistry,
    EvidenceRefusal,
    HomeGatedEvidenceProvider,
    OwnershipEvidenceProvider,
    RegistrationEvidenceProvider,
    RoleLocatorProvider,
    declared_identities,
    read_declared_identities,
)
from platform.universal_ownership.recommendation import (
    RECOMMENDATION_BASES,
    EligibleLocatorRecommendationProvider,
    GovernanceReductionEngine,
    GovernanceWorkload,
    OwnershipRecommendation,
    OwnershipRecommendationProvider,
    PeerPrecedentRecommendationProvider,
    RecommendationProviderDescriptor,
    RecommendationProviderRegistry,
    build_governance_reduction,
)

__all__ = [
    "UOF_ID",
    "OWNERSHIP_CONTRACT_VERSION",
    "OWNERSHIP_CONTRACTS",
    "ownership_contract_names",
    "UNASSIGNED_OWNER",
    "EvidenceKind",
    "CONSTITUTIVE_EVIDENCE_KINDS",
    "CORROBORATIVE_EVIDENCE_KINDS",
    "OwnershipStanding",
    "UNRESOLVED_REASONS",
    "REASON_NO_EVIDENCE",
    "REASON_NO_CONSTITUTIVE_DECLARATION",
    "REASON_INELIGIBLE_ZONE",
    "REASON_CONTEST_UNSETTLED",
    "REASON_SUBJECT_NOT_REGISTERED",
    "RULE_SOLE_DECLARATION",
    "RULE_CONTEST_SETTLED",
    "OwnershipEvidence",
    "OwnershipRequirement",
    "OWNERSHIP_REQUIREMENTS",
    "OwnershipDeclarationContract",
    "default_ownership_contract",
    "OwnershipDeclaration",
    "OwnershipRecord",
    "OwnershipDetermination",
    "EvidenceProviderDescriptor",
    "EvidenceRefusal",
    "CANONICAL_HOME_REFUSER",
    "OwnershipEvidenceProvider",
    "HomeGatedEvidenceProvider",
    "DeclaredAssignmentProvider",
    "DeclaredIdentityProvider",
    "DefinitionalLocatorProvider",
    "DEFAULT_IDENTITY_LABELS",
    "declared_identities",
    "RegistrationEvidenceProvider",
    "CallableEvidenceProvider",
    "EvidenceProviderRegistry",
    "RoleLocatorProvider",
    "read_declared_identities",
    "OwnershipGranularity",
    "RECOMMENDATION_BASES",
    "EligibleLocatorRecommendationProvider",
    "GovernanceReductionEngine",
    "GovernanceWorkload",
    "OwnershipRecommendation",
    "OwnershipRecommendationProvider",
    "PeerPrecedentRecommendationProvider",
    "RecommendationProviderDescriptor",
    "RecommendationProviderRegistry",
    "build_governance_reduction",
    "OwnershipDeterminationEngine",
    "OWNERSHIP_SERVICE_NAME",
    "bootstrap_ownership",
    "default_evidence_providers",
    "ownership_service_descriptor",
    "register_ownership",
    "OwnershipError",
    "OwnershipContractError",
    "OwnershipEvidenceError",
    "OwnershipProviderConflictError",
    "OwnershipDeterminationError",
    "OwnershipFabricationError",
]
