"""UKDA Part 01/05/12 — Universal Knowledge Model vocabularies (EPIC-UKDA).

The controlled vocabularies that give every canonical knowledge object a
self-describing, machine-consumable identity:

    * :class:`KnowledgeKind` — Part 01, the universal knowledge taxonomy (fact,
      decision, principle, rule, constraint, policy, pattern, convention, standard,
      evidence, rationale, exception, guideline, best-practice, anti-pattern,
      example, reference).
    * :class:`KnowledgeAuthority` — Part 02, the authority tier that a decision
      carries (constitutional > architectural > engineering > advisory).
    * :class:`Lifecycle` — Part 12, the ten canonical lifecycle stages with an
      explicit, enforced transition graph (no illegal jumps).
    * :class:`RelationType` — Part 05, the seventeen canonical, bidirectional
      knowledge-graph relationship types with their inverses.

Every vocabulary is *open by construction where the corpus is open* (UMB-006):
:class:`KnowledgeKind` and :class:`RelationType` expose ``coerce`` so unknown
future values fail loudly rather than silently, while remaining a single edit
(a new member) away from extension. The module is standard-library only
(TP-04/TP-05) and holds no runtime state.
"""

from __future__ import annotations

from enum import Enum
from typing import Any

from engine.knowledge.errors import (
    KnowledgeValidationError,
    LifecycleTransitionError,
    RelationshipError,
)

# The canonical serialization primitive has exactly one definition, in UCKP Layer Zero
# (UCKP-LAW-0001 Art-13, UCKP-INV-03). Re-exported unchanged for existing callers.
from engine.uckp.canonical import canonical_json, content_hash


class KnowledgeKind(str, Enum):
    """Part 01 — the universal taxonomy of what a canonical object *is*."""

    FACT = "fact"
    DECISION = "decision"
    PRINCIPLE = "principle"
    RULE = "rule"
    CONSTRAINT = "constraint"
    POLICY = "policy"
    PATTERN = "pattern"
    CONVENTION = "convention"
    STANDARD = "standard"
    EVIDENCE = "evidence"
    RATIONALE = "rationale"
    EXCEPTION = "exception"
    GUIDELINE = "guideline"
    BEST_PRACTICE = "best-practice"
    ANTI_PATTERN = "anti-pattern"
    EXAMPLE = "example"
    REFERENCE = "reference"
    LAW = "law"

    @classmethod
    def coerce(cls, value: Any, *, context: str = "knowledge") -> KnowledgeKind:
        """Return the enum member for ``value`` or raise a validation error."""
        try:
            return cls(str(value))
        except ValueError as exc:
            raise KnowledgeValidationError(
                "unknown knowledge kind", value=value, at=context
            ) from exc


class KnowledgeAuthority(str, Enum):
    """Part 02 — the authority tier a canonical object carries (ordered)."""

    CONSTITUTIONAL = "constitutional"
    ARCHITECTURAL = "architectural"
    ENGINEERING = "engineering"
    ADVISORY = "advisory"

    @property
    def rank(self) -> int:
        """Numeric precedence; lower is more authoritative (constitutional = 0)."""
        return _AUTHORITY_ORDER[self]

    def outranks(self, other: KnowledgeAuthority) -> bool:
        """True iff ``self`` is strictly more authoritative than ``other``."""
        return self.rank < other.rank

    @classmethod
    def coerce(cls, value: Any, *, context: str = "knowledge") -> KnowledgeAuthority:
        try:
            return cls(str(value))
        except ValueError as exc:
            raise KnowledgeValidationError(
                "unknown knowledge authority", value=value, at=context
            ) from exc


_AUTHORITY_ORDER: dict[KnowledgeAuthority, int] = {
    KnowledgeAuthority.CONSTITUTIONAL: 0,
    KnowledgeAuthority.ARCHITECTURAL: 1,
    KnowledgeAuthority.ENGINEERING: 2,
    KnowledgeAuthority.ADVISORY: 3,
}


class Lifecycle(str, Enum):
    """Part 12 — the ten canonical lifecycle stages of a knowledge object."""

    DRAFT = "draft"
    REVIEW = "review"
    APPROVED = "approved"
    RATIFIED = "ratified"
    IMPLEMENTED = "implemented"
    OPERATIONAL = "operational"
    DEPRECATED = "deprecated"
    SUPERSEDED = "superseded"
    ARCHIVED = "archived"
    HISTORICAL = "historical"

    @classmethod
    def coerce(cls, value: Any, *, context: str = "knowledge") -> Lifecycle:
        try:
            return cls(str(value))
        except ValueError as exc:
            raise KnowledgeValidationError(
                "unknown lifecycle stage", value=value, at=context
            ) from exc

    def can_transition_to(self, target: Lifecycle) -> bool:
        """True iff moving from ``self`` to ``target`` is a legal transition."""
        return target in _LIFECYCLE_TRANSITIONS.get(self, frozenset())

    def require_transition(self, target: Lifecycle, *, at: str = "knowledge") -> None:
        """Raise :class:`LifecycleTransitionError` if the transition is illegal."""
        if not self.can_transition_to(target):
            raise LifecycleTransitionError(
                "illegal lifecycle transition",
                at=at,
                current=self.value,
                target=target.value,
                allowed=sorted(t.value for t in _LIFECYCLE_TRANSITIONS.get(self, ())),
            )

    @property
    def is_active(self) -> bool:
        """True iff the object is a live source of authority (not retired)."""
        return self in _ACTIVE_STAGES

    @property
    def is_terminal(self) -> bool:
        """True iff no further transitions are possible from this stage."""
        return not _LIFECYCLE_TRANSITIONS.get(self)


# The explicit lifecycle transition graph (Part 12). Forward progression plus the
# two divergences every institutional-memory system needs: deprecation and
# supersession. Nothing may skip ratification on the way to being operational.
_LIFECYCLE_TRANSITIONS: dict[Lifecycle, frozenset[Lifecycle]] = {
    Lifecycle.DRAFT: frozenset({Lifecycle.REVIEW, Lifecycle.ARCHIVED}),
    Lifecycle.REVIEW: frozenset({Lifecycle.APPROVED, Lifecycle.DRAFT, Lifecycle.ARCHIVED}),
    Lifecycle.APPROVED: frozenset({Lifecycle.RATIFIED, Lifecycle.REVIEW}),
    Lifecycle.RATIFIED: frozenset(
        {Lifecycle.IMPLEMENTED, Lifecycle.DEPRECATED, Lifecycle.SUPERSEDED}
    ),
    Lifecycle.IMPLEMENTED: frozenset(
        {Lifecycle.OPERATIONAL, Lifecycle.DEPRECATED, Lifecycle.SUPERSEDED}
    ),
    Lifecycle.OPERATIONAL: frozenset({Lifecycle.DEPRECATED, Lifecycle.SUPERSEDED}),
    Lifecycle.DEPRECATED: frozenset({Lifecycle.SUPERSEDED, Lifecycle.ARCHIVED}),
    Lifecycle.SUPERSEDED: frozenset({Lifecycle.ARCHIVED, Lifecycle.HISTORICAL}),
    Lifecycle.ARCHIVED: frozenset({Lifecycle.HISTORICAL}),
    Lifecycle.HISTORICAL: frozenset(),
}

_ACTIVE_STAGES: frozenset[Lifecycle] = frozenset(
    {
        Lifecycle.RATIFIED,
        Lifecycle.IMPLEMENTED,
        Lifecycle.OPERATIONAL,
    }
)


class RelationType(str, Enum):
    """Part 05 — the canonical, bidirectional knowledge-graph relationship types."""

    DEPENDS_ON = "depends-on"
    IMPLEMENTS = "implements"
    EXTENDS = "extends"
    INHERITS = "inherits"
    REFERENCES = "references"
    GOVERNS = "governs"
    CERTIFIES = "certifies"
    VALIDATES = "validates"
    CONSUMES = "consumes"
    PRODUCES = "produces"
    OWNS = "owns"
    DERIVED_FROM = "derived-from"
    GENERATED_FROM = "generated-from"
    SUPERSEDES = "supersedes"
    EQUIVALENT_TO = "equivalent-to"
    CONFLICTS_WITH = "conflicts-with"
    RELATED_TO = "related-to"

    @classmethod
    def coerce(cls, value: Any, *, context: str = "relationship") -> RelationType:
        try:
            return cls(str(value))
        except ValueError as exc:
            raise RelationshipError("unknown relationship type", value=value, at=context) from exc

    @property
    def is_symmetric(self) -> bool:
        """True iff the relationship reads identically in both directions.

        Symmetric edges (``equivalent-to``, ``conflicts-with``, ``related-to``)
        require no distinct inverse type; every other type is navigated in reverse
        structurally through the graph's inbound adjacency (predecessors), so no
        second "…-by" vocabulary is needed to keep the graph bidirectional.
        """
        return self in _SYMMETRIC_RELATIONS


_SYMMETRIC_RELATIONS: frozenset[RelationType] = frozenset(
    {
        RelationType.EQUIVALENT_TO,
        RelationType.CONFLICTS_WITH,
        RelationType.RELATED_TO,
    }
)


__all__ = [
    "canonical_json",
    "content_hash",
    "KnowledgeKind",
    "KnowledgeAuthority",
    "Lifecycle",
    "RelationType",
]
