"""UCOS Ω∞ — Universal Knowledge Intelligence Platform (UKIP), EPIC-UKDA-003.

Knowledge Intelligence: the admission and intelligence layer that lets canonical
knowledge arrive from an **unbounded number of providers** while remaining authored
exactly once.

UKIP is additive. It owns nothing that the Universal Knowledge & Decision Architecture
(UKDA, EPIC-UKDA) or the Universal Constitutional Knowledge Integration (UKI,
EPIC-UKDA-002) already own, and it reuses them verbatim:

    * the knowledge vocabularies, canonical JSON form and content hash come from
      :mod:`engine.knowledge.model`;
    * the duplication identity is :meth:`CanonicalKnowledgeObject.semantic_hash`'s
      payload, reproduced field-for-field, so "the same knowledge" means the same
      thing in UKIP and UKDA and cannot drift;
    * the graph structure and every traversal primitive are the UKDA Part 05
      :class:`~engine.knowledge.graph.KnowledgeGraph`;
    * the validation verdict/severity/finding types are the UKDA Part 10 types, and
      the whole UKDA suite runs over the registry's projected base;
    * the certification status vocabulary is the UKDA Part 11
      :class:`~engine.knowledge.certification.CertStatus`;
    * the integration laws are referenced from
      :mod:`engine.knowledge.integration.constitution`, never restated.

The eleven capabilities, each a module in this package:

    * ``constitution``   — Part 02: the Knowledge Constitution (``UKIP-LAW-001…012``).
    * ``graph``          — Part 08: the Knowledge Graph over the registry.
    * ``registry``       — Part 06: the Knowledge Registry (the single canonical home).
    * ``discovery``      — Part 09: Knowledge Discovery + discover-before-create.
    * ``assimilation``   — Part 10: the one pipeline knowledge enters through.
    * ``relationships``  — Part 07: the relationship algebra (closure, composition).
    * ``classification`` — Part 04: total, deterministic, explained classification.
    * ``provenance``     — Part 05: hash-chained provenance.
    * ``evidence``       — Part 13: sealed, self-verifying evidence bundles.
    * ``validation``     — Part 11: the fail-closed check suite.
    * ``certification``  — Part 12: per-capability certification.

Supporting modules: ``contracts`` (Part 01, the provider wire shape), ``providers``
(Part 03, the unbounded provider set), ``cli`` (Part 14), ``errors``.

How the guarantees are achieved, rather than asserted:

    **Unlimited providers.** :class:`~engine.knowledge.ukip.providers.KnowledgeProvider`
    is the only provider abstraction the rest of the platform knows about, and
    :class:`~engine.knowledge.ukip.providers.ProviderRegistry` orders providers by
    ``(priority, provider_id)`` rather than insertion. Adding a provider requires no
    change to any engine, and the assimilation result does not depend on the order
    providers were added in.

    **Knowledge Once / no duplicate knowledge.** A canonical identifier is *derived*
    from the knowledge substance, never asserted by a provider, so two providers that
    observe the same knowledge compute the same identifier. The registry's second
    admission of an identity is therefore corroboration on the existing record, not a
    second record: duplicate knowledge is unrepresentable rather than merely detected.

    **Canonical knowledge only.** Nothing is admitted without total classification and
    a grounded provenance chain, and the advisory
    ``canonical-knowledge-only`` check reports any record left in draft or review.

    **Everything traceable.** Every record carries a hash-chained provenance chain from
    the observed source through classification, registration, corroboration and
    relationship wiring; altering any step invalidates every later digest.

    **Everything discoverable.** Every record answers to its identifier, its content
    digest, a provider-local address, its classification, its provider, and ranked
    search — verified by the ``universal-discoverability`` check, not assumed.

    **Everything composable.** Relationships compose through declared, data-driven
    rules into derived views that cite the path they were computed from, so a
    composition never becomes a second copy of the knowledge.

Standard-library only (TP-04/TP-05), never writes the frozen corpus (DP-03), and
deterministic with no wall-clock (IMP-007 §5), so identical knowledge always yields an
identical seal.
"""

from __future__ import annotations

from engine.foundation.contracts.contract import Contract, Version
from engine.knowledge.ukip.assimilation import (
    AssimilationReport,
    Disposition,
    KnowledgeAssimilator,
    LedgerEntry,
    assimilate_base,
)
from engine.knowledge.ukip.certification import (
    CRITERIA,
    CertificationSubject,
    CertStatus,
    Criterion,
    CriterionResult,
    KnowledgeCertificate,
    KnowledgeIntelligenceCertifier,
    certify_assimilation,
    certify_registry,
)
from engine.knowledge.ukip.classification import (
    DEFAULT_RULES,
    FACETS,
    Classification,
    ClassificationRule,
    Facet,
    FacetDecision,
    KnowledgeClassifier,
    classify_unit,
)
from engine.knowledge.ukip.constitution import (
    KNOWLEDGE_CAPABILITIES,
    KNOWLEDGE_LAWS,
    KnowledgeCapability,
    KnowledgeConstitution,
    KnowledgeLaw,
    constitution_objects,
    extend_base_with_knowledge_constitution,
    knowledge_constitution,
)
from engine.knowledge.ukip.contracts import (
    KNOWLEDGE_ID_PREFIX,
    KnowledgeUnit,
    ProviderKind,
    RelationDeclaration,
    SourceRef,
    unit_document,
)
from engine.knowledge.ukip.discovery import (
    CoverageReport,
    DiscoveryAnswer,
    DiscoveryHit,
    KnowledgeDiscovery,
    ReuseCandidate,
    build_discovery,
)
from engine.knowledge.ukip.errors import (
    AssimilationError,
    ClassificationError,
    DiscoveryBypassError,
    DuplicateHomeError,
    EvidenceError,
    KnowledgeIntelligenceError,
    ProvenanceError,
    ProviderConflictError,
    ProviderError,
    RegistrationError,
    RelationshipCompositionError,
    UnitError,
)
from engine.knowledge.ukip.evidence import (
    EVIDENCE_FILENAME,
    KnowledgeEvidence,
    build_evidence,
    build_evidence_from_assimilation,
    read_evidence,
    verify_evidence,
    write_evidence,
)
from engine.knowledge.ukip.graph import (
    PROJECTION_NAMES,
    PROJECTIONS,
    KnowledgeIntelligenceGraph,
    KnowledgeNode,
    build_graph,
)
from engine.knowledge.ukip.provenance import (
    PROVENANCE_STAGES,
    REQUIRED_STAGES,
    ProvenanceChain,
    ProvenanceLedger,
    ProvenanceStep,
    Stage,
    begin_chain,
)
from engine.knowledge.ukip.providers import (
    CallableProvider,
    CanonicalStoreProvider,
    DecisionLogProvider,
    DocumentProvider,
    KnowledgeProvider,
    MappingProvider,
    ProviderDescriptor,
    ProviderRegistry,
    default_providers,
    default_registry,
)
from engine.knowledge.ukip.registry import (
    Admission,
    AdmissionOutcome,
    KnowledgeRegistry,
    RegisteredKnowledge,
)
from engine.knowledge.ukip.relationships import (
    ACYCLIC_FAMILIES,
    COMPOSITION_RULES,
    SEMANTIC_INVERSES,
    Cycle,
    DanglingRelationship,
    Relationship,
    RelationshipSet,
    build_relationships,
)
from engine.knowledge.ukip.validation import (
    KnowledgeIntelligenceValidator,
    ValidationReport,
    ValidationSubject,
    Verdict,
    default_checks,
    validate_assimilation,
    validate_registry,
)

#: The versioned public contract of the Knowledge Intelligence layer (AR-03 / PL-05).
UKIP_CONTRACT = Contract(
    name="knowledge.ukip",
    version=Version(1, 0, 0),
    description=(
        "Universal Knowledge Intelligence Platform: admit canonical knowledge from an "
        "unbounded number of providers, home it exactly once by content-derived "
        "identity, and keep it classified, provenanced, related, discoverable, "
        "composable, validated and certified."
    ),
)

__all__ = [
    "UKIP_CONTRACT",
    # contracts (Part 01)
    "KNOWLEDGE_ID_PREFIX",
    "ProviderKind",
    "SourceRef",
    "RelationDeclaration",
    "KnowledgeUnit",
    "unit_document",
    # constitution (Part 02)
    "KnowledgeCapability",
    "KNOWLEDGE_CAPABILITIES",
    "KnowledgeLaw",
    "KNOWLEDGE_LAWS",
    "KnowledgeConstitution",
    "knowledge_constitution",
    "constitution_objects",
    "extend_base_with_knowledge_constitution",
    # providers (Part 03)
    "ProviderDescriptor",
    "KnowledgeProvider",
    "ProviderRegistry",
    "CallableProvider",
    "CanonicalStoreProvider",
    "DecisionLogProvider",
    "MappingProvider",
    "DocumentProvider",
    "default_providers",
    "default_registry",
    # classification (Part 04)
    "Facet",
    "FACETS",
    "FacetDecision",
    "Classification",
    "ClassificationRule",
    "DEFAULT_RULES",
    "KnowledgeClassifier",
    "classify_unit",
    # provenance (Part 05)
    "Stage",
    "PROVENANCE_STAGES",
    "REQUIRED_STAGES",
    "ProvenanceStep",
    "ProvenanceChain",
    "ProvenanceLedger",
    "begin_chain",
    # registry (Part 06)
    "AdmissionOutcome",
    "Admission",
    "RegisteredKnowledge",
    "KnowledgeRegistry",
    # relationships (Part 07)
    "SEMANTIC_INVERSES",
    "COMPOSITION_RULES",
    "ACYCLIC_FAMILIES",
    "Relationship",
    "DanglingRelationship",
    "Cycle",
    "RelationshipSet",
    "build_relationships",
    # graph (Part 08)
    "PROJECTIONS",
    "PROJECTION_NAMES",
    "KnowledgeNode",
    "KnowledgeIntelligenceGraph",
    "build_graph",
    # discovery (Part 09)
    "DiscoveryHit",
    "ReuseCandidate",
    "DiscoveryAnswer",
    "CoverageReport",
    "KnowledgeDiscovery",
    "build_discovery",
    # assimilation (Part 10)
    "Disposition",
    "LedgerEntry",
    "AssimilationReport",
    "KnowledgeAssimilator",
    "assimilate_base",
    # validation (Part 11)
    "Verdict",
    "ValidationSubject",
    "ValidationReport",
    "KnowledgeIntelligenceValidator",
    "default_checks",
    "validate_registry",
    "validate_assimilation",
    # certification (Part 12)
    "CertStatus",
    "CertificationSubject",
    "Criterion",
    "CriterionResult",
    "CRITERIA",
    "KnowledgeCertificate",
    "KnowledgeIntelligenceCertifier",
    "certify_registry",
    "certify_assimilation",
    # evidence (Part 13)
    "EVIDENCE_FILENAME",
    "KnowledgeEvidence",
    "build_evidence",
    "build_evidence_from_assimilation",
    "verify_evidence",
    "write_evidence",
    "read_evidence",
    # errors
    "KnowledgeIntelligenceError",
    "ProviderError",
    "ProviderConflictError",
    "UnitError",
    "ClassificationError",
    "RegistrationError",
    "DuplicateHomeError",
    "ProvenanceError",
    "RelationshipCompositionError",
    "DiscoveryBypassError",
    "AssimilationError",
    "EvidenceError",
]
