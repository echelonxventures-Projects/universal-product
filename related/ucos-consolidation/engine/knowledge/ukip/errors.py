"""UKIP — Universal Knowledge Intelligence Platform error taxonomy (EPIC-UKDA-003).

The Knowledge Intelligence layer specialises the UKDA Knowledge Layer error
discipline (:mod:`engine.knowledge.errors`), which itself is rooted in the EC-1
Foundation :class:`~engine.foundation.obs.errors.FoundationError`. Every error
carries a stable, category-prefixed ``code`` and structured, non-secret context so
failures are auditable (PL-02, IP-12) and machine-consumable.

These types are additive engineering code. They never modify the frozen Foundation
or UKDA taxonomies; they name the failure modes that only exist once knowledge may
arrive from *unlimited providers*: a provider may be malformed, may contradict a
canonical record, may attempt to re-home knowledge that already has a canonical
home, or may bypass discovery.
"""

from __future__ import annotations

from engine.knowledge.errors import KnowledgeError


class KnowledgeIntelligenceError(KnowledgeError):
    """Base class for all UKIP Knowledge Intelligence errors (EPIC-UKDA-003)."""

    code = "UKIP-000"


class ProviderError(KnowledgeIntelligenceError):
    """A knowledge provider is malformed, unreadable, or emitted an invalid unit."""

    code = "UKIP-PROVIDER-001"


class ProviderConflictError(KnowledgeIntelligenceError):
    """Two providers registered under the same provider identity."""

    code = "UKIP-PROVIDER-002"


class UnitError(KnowledgeIntelligenceError):
    """A :class:`~engine.knowledge.ukip.contracts.KnowledgeUnit` failed its shape rules."""

    code = "UKIP-UNIT-001"


class ClassificationError(KnowledgeIntelligenceError):
    """A knowledge unit could not be deterministically classified."""

    code = "UKIP-CLASS-001"


class RegistrationError(KnowledgeIntelligenceError):
    """A knowledge record could not be admitted to the Knowledge Registry."""

    code = "UKIP-REGISTRY-001"


class DuplicateHomeError(KnowledgeIntelligenceError):
    """Knowledge already has a canonical home (the Knowledge Once Principle)."""

    code = "UKIP-REGISTRY-002"


class ProvenanceError(KnowledgeIntelligenceError):
    """A provenance chain is broken, unsealed, or out of order."""

    code = "UKIP-PROVENANCE-001"


class RelationshipCompositionError(KnowledgeIntelligenceError):
    """A relationship could not be composed, inverted, or closed."""

    code = "UKIP-RELATION-001"


class DiscoveryBypassError(KnowledgeIntelligenceError):
    """Knowledge was created without the mandatory prior discovery determination."""

    code = "UKIP-DISCOVERY-001"


class AssimilationError(KnowledgeIntelligenceError):
    """The assimilation pipeline failed closed on an unresolvable contribution."""

    code = "UKIP-ASSIMILATION-001"


class EvidenceError(KnowledgeIntelligenceError):
    """A knowledge evidence bundle could not be built or written."""

    code = "UKIP-EVIDENCE-001"


__all__ = [
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
