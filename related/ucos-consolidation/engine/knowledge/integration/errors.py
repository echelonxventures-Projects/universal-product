"""UKI — Universal Constitutional Knowledge Integration error taxonomy (EPIC-UKDA-002).

The Integration Layer specialises the UKDA Knowledge Layer error discipline
(EPIC-UKDA): every error is rooted in :class:`~engine.knowledge.errors.KnowledgeError`
(and therefore in the EC-1 Foundation :class:`FoundationError`), carries a stable,
category-prefixed ``code`` and structured, non-secret ``context`` so a fail-closed
constitutional violation is auditable (PL-02, IP-12) and machine-consumable.

These types are additive engineering code. They never modify the frozen Foundation
or UKDA taxonomies; they name the *integration* failure modes that the constitutional
execution path fails closed on: an artifact that would duplicate, overlap, orphan
ownership, bypass discovery/reuse, or break end-to-end traceability.
"""

from __future__ import annotations

from engine.knowledge.errors import KnowledgeError


class IntegrationError(KnowledgeError):
    """Base class for all UKI constitutional-integration errors (EPIC-UKDA-002)."""

    code = "UKI-000"


class OwnershipViolationError(IntegrationError):
    """An artifact fails the Canonical Ownership Protocol (Deliverable 3)."""

    code = "UKI-OWNERSHIP-001"


class DuplicationViolationError(IntegrationError):
    """The Duplicate Prevention Engine detected a fail-closed violation (Deliverable 6)."""

    code = "UKI-DUPLICATE-001"


class DiscoveryBypassError(IntegrationError):
    """A constitutional operation attempted to bypass mandatory discovery (Deliverable 2)."""

    code = "UKI-DISCOVERY-001"


class ReuseBypassError(IntegrationError):
    """A create was attempted while reuse/extension was required (Deliverable 5)."""

    code = "UKI-REUSE-001"


class GovernanceGroundingError(IntegrationError):
    """A governance decision is not grounded in canonical knowledge (Deliverable 8)."""

    code = "UKI-GOVERNANCE-001"


class RegistrationConflictError(IntegrationError):
    """A registration would duplicate an already-registered canonical entity (Deliverable 9)."""

    code = "UKI-REGISTRATION-001"


class TraceabilityError(IntegrationError):
    """The constitutional traceability chain is broken or incomplete (Deliverable 7)."""

    code = "UKI-TRACE-001"


class CompositionError(IntegrationError):
    """Autonomous composition was requested without sufficient knowledge (Deliverable 10)."""

    code = "UKI-COMPOSE-001"


class IntentError(IntegrationError):
    """A proposed artifact intent is malformed against its required shape."""

    code = "UKI-INTENT-001"


class RepositoryDiscoveryError(IntegrationError):
    """A live repository could not be discovered or assimilated (EPIC-UKDA-004)."""

    code = "UKI-REPOSITORY-001"


__all__ = [
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
