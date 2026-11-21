"""UCOS Ω∞ — Universal Foundation Platform (``platform.universal_foundation``).

Two capabilities live here, and the distinction between them is the whole architecture:

**UCOS-UFC-001 — the Universal Foundation Constitution.** The single law every Foundation
capability obeys: seventeen articles over thirteen governed domains, each bound to one executable
probe, plus the convergence measurement that proves each constitutional model has exactly one
implementation and the freeze readiness determination built on both. The law names no
capability; its population is a declared register.

**UCOS-UFP-001 — the Universal Foundation Platform.** The composition in which the four
reusable Foundation capabilities become one determination, and in which a project participates
by **declaration** rather than by code:

    * ``UCOS-URTF-001`` Universal Repository Truth Framework — what is Truth, by policy.
    * ``UCOS-UOF-001``  Universal Ownership Framework — who owns it, by evidence.
    * ``UCOS-USAF-001`` Universal Source Assimilation Framework — how anything becomes content.
    * ``UCOS-UMPF-001`` Universal Measurement Policy Framework — how any of it is measured.

A project supplies one :class:`FoundationSpecialization` document naming its Truth policy, its
governed ownership assignments, its registration ledger and eligibility rules, the grain at
which it holds ownership, and how to project its existing population. That document is the only
place a project's own names appear anywhere in the Foundation — which is the mechanical reason a
repository-specific fix can no longer be written: there is nowhere to put it.

Repository discovery is a **reusable service** here, not the first step of every
implementation: :meth:`UniversalFoundation.project_population` executes from the project's
declared Truth document, and no Foundation module scans a filesystem.
"""

from __future__ import annotations

from platform.universal_foundation.bootstrap import (
    CONSTITUTION_SERVICE_NAME,
    FOUNDATION_CONTRACT_VERSION,
    FOUNDATION_CONTRACTS,
    FOUNDATION_SERVICE_NAME,
    UFP_ID,
    bootstrap_foundation_constitution,
    bootstrap_project_ownership,
    bootstrap_universal_foundation,
    canonical_home_policy,
    constitution_service_descriptor,
    foundation_contract_names,
    foundation_service_descriptor,
    ownership_evidence_providers,
    register_foundation_constitution,
    register_universal_foundation,
    registered_locators,
)
from platform.universal_foundation.conformance import (
    CapabilityConformance,
    CapabilityDeclaration,
    CapabilityRegister,
    ConformanceDetermination,
    ConformanceEngine,
    ConformanceProbe,
    FacetDeclaration,
    FacetStatus,
    GateResult,
    NucleusProfile,
    ProbeContext,
    ProbeRegistry,
    Verdict,
    default_capability_register,
    default_probe_registry,
    load_capability_register,
)
from platform.universal_foundation.constitution import (
    CONSTITUTION_CONTRACTS,
    FOUNDATION_ARTICLES,
    FOUNDATION_CONSTITUTION_ID,
    FOUNDATION_CONSTITUTION_VERSION,
    MATURITY_GATES,
    ArticleScope,
    ConstitutionalDomain,
    FoundationArticle,
    FoundationConstitution,
    MaturityAxis,
    article,
    article_for_gate,
    articles_of_domain,
    foundation_constitution,
    maturity_axes,
)
from platform.universal_foundation.convergence import (
    ConstitutionalModel,
    ConvergenceDetermination,
    ConvergenceEngine,
    ConvergenceRegister,
    ConvergenceRelation,
    ModelConvergence,
    SubordinateSurface,
    bootstrap_convergence,
    default_convergence_register,
    load_convergence_register,
)
from platform.universal_foundation.errors import (
    FoundationCompositionError,
    FoundationConformanceError,
    FoundationConstitutionError,
    FoundationConvergenceError,
    FoundationFreezeError,
    FoundationNucleusError,
    SpecializationError,
    UniversalFoundationError,
)
from platform.universal_foundation.freeze import (
    CriterionKind,
    CriterionResult,
    CriterionVerdict,
    FreezeCriteriaRegister,
    FreezeCriterion,
    FreezeDetermination,
    FreezeReadinessEngine,
    bootstrap_freeze_readiness,
    default_freeze_criteria,
    load_freeze_criteria,
)
from platform.universal_foundation.nucleus import (
    GATE_NUCLEUS_COMPLETE,
    FacetResolution,
    FacetResult,
    FacetVerdict,
    NucleusCompleteness,
    NucleusCompletenessEngine,
    NucleusContract,
    NucleusDetermination,
    NucleusFacet,
    bootstrap_nucleus_completeness,
    default_nucleus_contract,
    load_nucleus_contract,
)
from platform.universal_foundation.service import (
    COMPOSED_CAPABILITIES,
    FoundationDetermination,
    UniversalFoundation,
)
from platform.universal_foundation.specialization import (
    FoundationSpecialization,
    catalog_path,
    default_specialization,
    load_specialization,
)

__all__ = [
    # the platform
    "UFP_ID",
    "FOUNDATION_CONTRACT_VERSION",
    "FOUNDATION_CONTRACTS",
    "COMPOSED_CAPABILITIES",
    "FoundationSpecialization",
    "load_specialization",
    "default_specialization",
    "catalog_path",
    "FoundationDetermination",
    "UniversalFoundation",
    "FOUNDATION_SERVICE_NAME",
    "bootstrap_universal_foundation",
    "bootstrap_project_ownership",
    "canonical_home_policy",
    "ownership_evidence_providers",
    "registered_locators",
    "foundation_contract_names",
    "foundation_service_descriptor",
    "register_universal_foundation",
    # the constitution
    "FOUNDATION_CONSTITUTION_ID",
    "FOUNDATION_CONSTITUTION_VERSION",
    "FOUNDATION_ARTICLES",
    "CONSTITUTION_CONTRACTS",
    "CONSTITUTION_SERVICE_NAME",
    "MATURITY_GATES",
    "ArticleScope",
    "ConstitutionalDomain",
    "FoundationArticle",
    "FoundationConstitution",
    "MaturityAxis",
    "article",
    "article_for_gate",
    "articles_of_domain",
    "foundation_constitution",
    "maturity_axes",
    "bootstrap_foundation_constitution",
    "constitution_service_descriptor",
    "register_foundation_constitution",
    # conformance
    "CapabilityConformance",
    "CapabilityDeclaration",
    "CapabilityRegister",
    "FacetDeclaration",
    "FacetStatus",
    "NucleusProfile",
    "ConformanceDetermination",
    "ConformanceEngine",
    "ConformanceProbe",
    "GateResult",
    "ProbeContext",
    "ProbeRegistry",
    "Verdict",
    "default_capability_register",
    "default_probe_registry",
    "load_capability_register",
    # convergence
    "ConstitutionalModel",
    "ConvergenceDetermination",
    "ConvergenceEngine",
    "ConvergenceRegister",
    "ConvergenceRelation",
    "ModelConvergence",
    "SubordinateSurface",
    "bootstrap_convergence",
    "default_convergence_register",
    "load_convergence_register",
    # freeze
    "CriterionKind",
    "CriterionResult",
    "CriterionVerdict",
    "FreezeCriteriaRegister",
    "FreezeCriterion",
    "FreezeDetermination",
    "FreezeReadinessEngine",
    "bootstrap_freeze_readiness",
    "default_freeze_criteria",
    "load_freeze_criteria",
    # Ω Nucleus completeness
    "GATE_NUCLEUS_COMPLETE",
    "FacetResolution",
    "FacetResult",
    "FacetVerdict",
    "NucleusCompleteness",
    "NucleusCompletenessEngine",
    "NucleusContract",
    "NucleusDetermination",
    "NucleusFacet",
    "bootstrap_nucleus_completeness",
    "default_nucleus_contract",
    "load_nucleus_contract",
    # errors
    "UniversalFoundationError",
    "FoundationNucleusError",
    "SpecializationError",
    "FoundationCompositionError",
    "FoundationConstitutionError",
    "FoundationConformanceError",
    "FoundationConvergenceError",
    "FoundationFreezeError",
]
