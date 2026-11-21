"""UKDA — Universal Knowledge & Decision Architecture error taxonomy (EPIC-UKDA).

The Knowledge Layer reuses the EC-1 Foundation error discipline (TASK-000006):
every error is rooted in :class:`FoundationError`, carries a stable, category-
prefixed ``code`` and structured, non-secret ``context`` so failures are auditable
(PL-02, IP-12) and machine-consumable.

These types are additive engineering code. They never modify the frozen Foundation
taxonomy; they specialise it for the Universal Knowledge & Decision Architecture,
which authors a canonical architectural decision exactly once (the Knowledge Once
Principle) and derives everything else from it.
"""

from __future__ import annotations

from engine.foundation.obs.errors import FoundationError


class KnowledgeError(FoundationError):
    """Base class for all UKDA Knowledge Layer errors (EPIC-UKDA)."""

    code = "UKDA-000"


class KnowledgeValidationError(KnowledgeError):
    """A knowledge object failed model validation against its required shape."""

    code = "UKDA-VALID-001"


class KnowledgeIntegrityError(KnowledgeError):
    """A content-addressed knowledge object or decision was mutated after sealing."""

    code = "UKDA-INTEGRITY-001"


class KnowledgeSourceError(KnowledgeError):
    """The canonical knowledge store could not be located, read, or written."""

    code = "UKDA-SOURCE-001"


class KnowledgeNotFoundError(KnowledgeError):
    """A requested canonical knowledge object or decision is absent from the store."""

    code = "UKDA-404"


class DuplicateKnowledgeError(KnowledgeError):
    """A canonical decision/knowledge would be authored twice (Knowledge Once Principle)."""

    code = "UKDA-DUPLICATE-001"


class LifecycleTransitionError(KnowledgeError):
    """An illegal knowledge lifecycle transition was attempted (Part 12)."""

    code = "UKDA-LIFECYCLE-001"


class RelationshipError(KnowledgeError):
    """A knowledge-graph relationship is malformed or references an unknown type."""

    code = "UKDA-RELATION-001"


__all__ = [
    "KnowledgeError",
    "KnowledgeValidationError",
    "KnowledgeIntegrityError",
    "KnowledgeSourceError",
    "KnowledgeNotFoundError",
    "DuplicateKnowledgeError",
    "LifecycleTransitionError",
    "RelationshipError",
]
