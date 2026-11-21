"""UCOS Ω∞ — Universal Knowledge & Decision Architecture (UKDA), EPIC-UKDA.

A permanent, repository-native institutional-knowledge capability built on the EC-1
Foundation (EPIC-001). It ratifies and operationalises the **Knowledge Once
Principle**: a canonical architectural decision exists exactly once, and everything
else is generated, derived, linked, validated, certified, or consumed from that
single source.

Layers (each a module in this package):

    * ``model``        — Part 01/05/12: knowledge kinds, authority, lifecycle, relations.
    * ``cko``          — Part 02/03: Canonical Knowledge Object + Universal Decision Model.
    * ``graph``        — Part 05: the Universal Knowledge Graph.
    * ``store``        — Part 04/13: the canonical, authored-once knowledge store.
    * ``intelligence`` — Part 04/09: institutional memory + repository intelligence.
    * ``validation``   — Part 10: knowledge validation (fail-closed gate).
    * ``certification``— Part 11: knowledge certification (completeness).
    * ``docs``         — Part 07/08: generated developer/agent handbooks.
    * ``bootstrap``    — Part 06/14: agent/developer auto-bootstrap digest.
    * ``seed``         — the founding canonical knowledge.
    * ``cli``          — Part 13: the operational command-line surface.

The Knowledge Layer never mutates the certified corpus (DP-03), is standard-library
only (TP-04/TP-05), deterministic (IMP-007 §5), and exposes its capability through
the versioned :data:`UKDA_CONTRACT` (AR-03/PL-05).
"""

from __future__ import annotations

from engine.foundation.contracts.contract import Contract, Version
from engine.knowledge.bootstrap import BootstrapDigest, build_digest
from engine.knowledge.certification import (
    BaseCertificationReport,
    CertStatus,
    KnowledgeCertificationRecord,
    KnowledgeCertifier,
    certify_base,
)
from engine.knowledge.cko import (
    CanonicalKnowledgeObject,
    DecisionRecord,
    RejectedOption,
)
from engine.knowledge.docs import DocumentationEngine
from engine.knowledge.errors import (
    DuplicateKnowledgeError,
    KnowledgeError,
    KnowledgeIntegrityError,
    KnowledgeNotFoundError,
    KnowledgeSourceError,
    KnowledgeValidationError,
    LifecycleTransitionError,
    RelationshipError,
)
from engine.knowledge.graph import KnowledgeEdge, KnowledgeGraph, derive_edges
from engine.knowledge.intelligence import (
    ConflictFinding,
    CoverageReport,
    DuplicateFinding,
    KnowledgeIntelligence,
    SearchHit,
    build_intelligence,
)
from engine.knowledge.model import (
    KnowledgeAuthority,
    KnowledgeKind,
    Lifecycle,
    RelationType,
    canonical_json,
    content_hash,
)
from engine.knowledge.portal import PORTALS, KnowledgePortal
from engine.knowledge.seed import build_seed_base
from engine.knowledge.store import (
    KnowledgeBase,
    KnowledgeStore,
    default_store_dir,
)
from engine.knowledge.validation import (
    KnowledgeValidationReport,
    KnowledgeValidator,
    Verdict,
    validate_base,
)

#: The versioned public contract of the Knowledge Layer (AR-03 / PL-05).
UKDA_CONTRACT = Contract(
    name="knowledge.ukda",
    version=Version(1, 0, 0),
    description=(
        "Universal Knowledge & Decision Architecture: author canonical knowledge once; "
        "derive, link, validate, certify, document, and consume everything else."
    ),
)

__all__ = [
    "UKDA_CONTRACT",
    # model
    "KnowledgeKind",
    "KnowledgeAuthority",
    "Lifecycle",
    "RelationType",
    "canonical_json",
    "content_hash",
    # cko / decision
    "CanonicalKnowledgeObject",
    "DecisionRecord",
    "RejectedOption",
    # graph
    "KnowledgeGraph",
    "KnowledgeEdge",
    "derive_edges",
    # store
    "KnowledgeBase",
    "KnowledgeStore",
    "default_store_dir",
    "build_seed_base",
    # intelligence
    "KnowledgeIntelligence",
    "build_intelligence",
    "SearchHit",
    "DuplicateFinding",
    "ConflictFinding",
    "CoverageReport",
    # validation
    "KnowledgeValidator",
    "KnowledgeValidationReport",
    "Verdict",
    "validate_base",
    # certification
    "KnowledgeCertifier",
    "KnowledgeCertificationRecord",
    "BaseCertificationReport",
    "CertStatus",
    "certify_base",
    # docs / bootstrap
    "DocumentationEngine",
    "BootstrapDigest",
    "build_digest",
    # portal (EPIC-DOC-002)
    "KnowledgePortal",
    "PORTALS",
    # errors
    "KnowledgeError",
    "KnowledgeValidationError",
    "KnowledgeIntegrityError",
    "KnowledgeSourceError",
    "KnowledgeNotFoundError",
    "DuplicateKnowledgeError",
    "LifecycleTransitionError",
    "RelationshipError",
]
