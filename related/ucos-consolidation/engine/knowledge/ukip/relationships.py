"""UKIP Part 07 — Knowledge Relationships (EPIC-UKDA-003).

The algebra that turns a set of independently-supplied records into a navigable,
composable body of knowledge (UKIP-LAW-006, UKIP-LAW-008).

Providers declare relationships one-directionally and in their own local vocabulary
of targets. This module resolves and closes them:

    * **Resolution** — a declared target may be a canonical ``UKID-*``, a
      ``provider:key`` address, a bare provider-local key, or a content digest.
      Everything is resolved through the registry's alias map; anything that cannot
      be resolved becomes a reported :class:`DanglingRelationship`, never a silently
      dropped edge.
    * **Symmetric closure** — the three symmetric UDKA relation types
      (``equivalent-to``, ``conflicts-with``, ``related-to``) are closed in both
      directions, so "does A conflict with B?" has the same answer as "does B
      conflict with A?" regardless of which provider said it.
    * **Structural inversion** — asymmetric relations are *not* given a second
      "…-by" vocabulary (which would be a duplicate taxonomy). They are navigated in
      reverse through inbound adjacency, and :data:`SEMANTIC_INVERSES` names the
      reading of that reverse direction for presentation only.
    * **Composition** — :data:`COMPOSITION_RULES` declares which relation pairs
      compose transitively (``depends-on ∘ depends-on → depends-on``), so derived
      relationships are *computed* from asserted ones rather than stored a second
      time. A composed relationship always cites the path it came from.
    * **Cycle detection** over the relation families that must stay acyclic
      (dependency, structure, supersession), because a cycle there is a real defect
      rather than a legitimate shape.

The relation vocabulary itself is reused verbatim from
:class:`engine.knowledge.model.RelationType` — seventeen types, one definition.
"""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from dataclasses import dataclass, replace
from typing import Any

from engine.knowledge.model import RelationType, content_hash
from engine.knowledge.ukip.errors import RelationshipCompositionError
from engine.knowledge.ukip.registry import KnowledgeRegistry, RegisteredKnowledge
from engine.temporal.coordinate import Ordering, TemporalCoordinate, ValidityPeriod
from engine.temporal.operations import TemporalRegistry, compare

#: The symmetric relation types, taken from the UKDA model rather than re-listed.
SYMMETRIC: frozenset[RelationType] = frozenset(r for r in RelationType if r.is_symmetric)

#: How the reverse direction of an asymmetric relation *reads*. Presentation only:
#: no inverse edge is stored, because the graph already answers reverse queries
#: through inbound adjacency. Naming the reading here keeps it out of the taxonomy.
SEMANTIC_INVERSES: dict[RelationType, str] = {
    RelationType.DEPENDS_ON: "required-by",
    RelationType.IMPLEMENTS: "implemented-by",
    RelationType.EXTENDS: "extended-by",
    RelationType.INHERITS: "inherited-by",
    RelationType.REFERENCES: "referenced-by",
    RelationType.GOVERNS: "governed-by",
    RelationType.CERTIFIES: "certified-by",
    RelationType.VALIDATES: "validated-by",
    RelationType.CONSUMES: "consumed-by",
    RelationType.PRODUCES: "produced-by",
    RelationType.OWNS: "owned-by",
    RelationType.DERIVED_FROM: "source-of",
    RelationType.GENERATED_FROM: "generator-of",
    RelationType.SUPERSEDES: "superseded-by",
}

#: Which relation pairs compose transitively, and what the composite means.
#: Composition is what makes knowledge composable without copying it: a derived
#: relationship is recomputed from asserted ones on demand and cites its path.
COMPOSITION_RULES: dict[tuple[RelationType, RelationType], RelationType] = {
    (RelationType.DEPENDS_ON, RelationType.DEPENDS_ON): RelationType.DEPENDS_ON,
    (RelationType.EXTENDS, RelationType.EXTENDS): RelationType.EXTENDS,
    (RelationType.INHERITS, RelationType.INHERITS): RelationType.INHERITS,
    (RelationType.CONSUMES, RelationType.CONSUMES): RelationType.CONSUMES,
    (RelationType.SUPERSEDES, RelationType.SUPERSEDES): RelationType.SUPERSEDES,
    (RelationType.DERIVED_FROM, RelationType.DERIVED_FROM): RelationType.DERIVED_FROM,
    (RelationType.GENERATED_FROM, RelationType.GENERATED_FROM): RelationType.GENERATED_FROM,
    (RelationType.EQUIVALENT_TO, RelationType.EQUIVALENT_TO): RelationType.EQUIVALENT_TO,
    # An implementation of an extension implements the extended thing too.
    (RelationType.IMPLEMENTS, RelationType.EXTENDS): RelationType.IMPLEMENTS,
    # Anything depending on a dependency's extension still depends on it.
    (RelationType.DEPENDS_ON, RelationType.EXTENDS): RelationType.DEPENDS_ON,
    # Equivalence propagates any relation it is composed with.
    (RelationType.EQUIVALENT_TO, RelationType.DEPENDS_ON): RelationType.DEPENDS_ON,
    (RelationType.EQUIVALENT_TO, RelationType.CONFLICTS_WITH): RelationType.CONFLICTS_WITH,
    (RelationType.DEPENDS_ON, RelationType.EQUIVALENT_TO): RelationType.DEPENDS_ON,
}

#: Relation families that must remain acyclic. A cycle in any of these is a genuine
#: modelling defect: knowledge cannot depend on, extend, or supersede itself.
ACYCLIC_FAMILIES: dict[str, frozenset[RelationType]] = {
    "dependency": frozenset({RelationType.DEPENDS_ON, RelationType.CONSUMES}),
    "structure": frozenset({RelationType.EXTENDS, RelationType.INHERITS}),
    "supersession": frozenset({RelationType.SUPERSEDES}),
    "derivation": frozenset({RelationType.DERIVED_FROM, RelationType.GENERATED_FROM}),
}


@dataclass(frozen=True, slots=True)
class Relationship:
    """One resolved relationship between two canonical knowledge identifiers.

    ``derived`` marks a relationship that was *computed* by composition rather than
    asserted by a provider, and ``path`` records the identifiers it was computed
    through — so a derived relationship can always be traced back to the asserted
    ones that justify it (UKIP-LAW-008).
    """

    source: str
    target: str
    relation: RelationType
    note: str = ""
    derived: bool = False
    path: tuple[str, ...] = ()
    validity: ValidityPeriod | None = None

    def key(self) -> tuple[str, str, str]:
        """The stable navigation/grouping key — every temporal version shares one."""
        return (self.source, self.target, self.relation.value)

    def identity(self) -> tuple[str, str, str, str | None]:
        """The stable per-instance identity, temporal version included.

        :meth:`key` deliberately groups every validity-scoped version of a
        relationship together, because navigation ("what does A depend on")
        should not require picking a moment in time. This is the narrower
        identity used wherever two versions of the same triple must NOT be
        treated as the same thing — de-duplication and content sealing
        (UCKP-ART-07 temporal validity, P4-F-002).
        """
        marker = None if self.validity is None else self.validity.since.qualified
        return (*self.key(), marker)

    @property
    def is_symmetric(self) -> bool:
        return self.relation.is_symmetric

    @property
    def inverse_reading(self) -> str:
        """How the reverse direction reads (the relation itself when symmetric)."""
        if self.relation.is_symmetric:
            return self.relation.value
        return SEMANTIC_INVERSES.get(self.relation, f"inverse-of-{self.relation.value}")

    def mirrored(self) -> Relationship:
        """The symmetric counterpart (only meaningful for symmetric relations)."""
        if not self.relation.is_symmetric:
            raise RelationshipCompositionError(
                "only a symmetric relation may be mirrored",
                relation=self.relation.value,
                source=self.source,
            )
        return replace(self, source=self.target, target=self.source, note="symmetric-closure")

    def to_dict(self) -> dict[str, Any]:
        return {
            "source": self.source,
            "target": self.target,
            "relation": self.relation.value,
            "inverse_reading": self.inverse_reading,
            "note": self.note,
            "derived": self.derived,
            "path": list(self.path),
            "validity": None if self.validity is None else self.validity.to_dict(),
        }


@dataclass(frozen=True, slots=True)
class DanglingRelationship:
    """A declared relationship whose target could not be resolved."""

    source: str
    declared_target: str
    relation: RelationType
    note: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "source": self.source,
            "declared_target": self.declared_target,
            "relation": self.relation.value,
            "note": self.note,
        }


@dataclass(frozen=True, slots=True)
class Cycle:
    """A detected cycle within one acyclic relation family."""

    family: str
    members: tuple[str, ...]

    def to_dict(self) -> dict[str, Any]:
        return {"family": self.family, "members": list(self.members)}


def _lt(
    x: TemporalCoordinate, y: TemporalCoordinate, registry: TemporalRegistry | None = None
) -> bool | None:
    """Whether ``x`` is provably before ``y``, or ``None`` if that cannot be proven."""
    verdict = compare(x, y, registry)
    if verdict is Ordering.INCOMPARABLE:
        return None
    return verdict is Ordering.BEFORE


def _overlaps(a: ValidityPeriod | None, b: ValidityPeriod | None) -> bool:
    """Whether two validity windows provably share an instant.

    ``None`` is timeless and overlaps everything — the untimed case behaves exactly
    as before this field existed. Half-open windows ``[since, until)`` overlap iff
    each starts before the other ends. When that cannot be *proven* (different
    reference systems, no declared conversion — Law 7), the pair is treated as NOT
    overlapping: collapsing two relationships on an unproven claim is the defect
    UCKP-ART-07 temporal validity exists to remove, so an unproven case is left as
    two coexisting instances rather than guessed into one (P4-F-002).
    """
    if a is None or b is None:
        return True
    if not a.since.reference_system.same_system(b.since.reference_system):
        # No registry is threaded through merge-time dedup, so cross-system
        # windows are only ever compared via a declared conversion the caller
        # applied before construction — otherwise they are not provably disjoint,
        # but neither are they provably the same instant.
        return False
    left = True if b.until is None else _lt(a.since, b.until)
    right = True if a.until is None else _lt(b.since, a.until)
    if left is None or right is None:
        return False
    return left and right


def _temporal_sort_key(relationship: Relationship) -> tuple[int, str]:
    """Deterministic (not temporal) ordering for display/sealing — timeless first."""
    if relationship.validity is None:
        return (0, "")
    return (1, relationship.validity.since.qualified)


def _holds_at(
    validity: ValidityPeriod | None,
    coordinate: TemporalCoordinate,
    registry: TemporalRegistry | None,
) -> bool:
    """Whether a validity window provably contains ``coordinate``."""
    if validity is None:
        return True
    since_verdict = compare(validity.since, coordinate, registry)
    if since_verdict is Ordering.AFTER or since_verdict is Ordering.INCOMPARABLE:
        return False
    if validity.until is None:
        return True
    until_verdict = compare(validity.until, coordinate, registry)
    if until_verdict is Ordering.INCOMPARABLE:
        return False
    return until_verdict is Ordering.AFTER


class RelationshipSet:
    """The resolved, symmetrically-closed relationships over a registry."""

    __slots__ = ("_relationships", "_out", "_in", "_dangling")

    def __init__(
        self,
        relationships: Iterable[Relationship] = (),
        dangling: Iterable[DanglingRelationship] = (),
    ) -> None:
        # Two relationships that share a (source, target, relation) key coexist
        # unless their validity windows provably overlap — see _overlaps(). A
        # timeless relationship (validity=None) overlaps everything, which is
        # exactly the old single-winner-per-key behaviour when nobody uses
        # validity at all (UCKP-ART-07 temporal validity, P4-F-002).
        groups: dict[tuple[str, str, str], list[Relationship]] = {}
        for relationship in relationships:
            group = groups.setdefault(relationship.key(), [])
            for index, existing in enumerate(group):
                if _overlaps(existing.validity, relationship.validity):
                    # An asserted relationship always wins over a derived one
                    # occupying the same window: provider assertion is evidence,
                    # composition is inference.
                    if existing.derived and not relationship.derived:
                        group[index] = relationship
                    break
            else:
                group.append(relationship)
        self._relationships = tuple(
            r for k in sorted(groups) for r in sorted(groups[k], key=_temporal_sort_key)
        )
        out: dict[str, list[Relationship]] = {}
        inbound: dict[str, list[Relationship]] = {}
        for relationship in self._relationships:
            out.setdefault(relationship.source, []).append(relationship)
            inbound.setdefault(relationship.target, []).append(relationship)
        self._out = out
        self._in = inbound
        self._dangling = tuple(
            sorted(dangling, key=lambda d: (d.source, d.relation.value, d.declared_target))
        )

    # -- size / iteration ------------------------------------------------------

    def __len__(self) -> int:
        return len(self._relationships)

    def __iter__(self):
        return iter(self._relationships)

    def all(self) -> tuple[Relationship, ...]:
        return self._relationships

    def dangling(self) -> tuple[DanglingRelationship, ...]:
        """Every declared relationship whose target does not resolve."""
        return self._dangling

    def asserted(self) -> tuple[Relationship, ...]:
        return tuple(r for r in self._relationships if not r.derived)

    def derived(self) -> tuple[Relationship, ...]:
        return tuple(r for r in self._relationships if r.derived)

    def nodes(self) -> tuple[str, ...]:
        return tuple(sorted(set(self._out) | set(self._in)))

    def types(self) -> tuple[RelationType, ...]:
        return tuple(sorted({r.relation for r in self._relationships}, key=lambda t: t.value))

    # -- queries ---------------------------------------------------------------

    def outbound(
        self, node: str, *, relation: RelationType | None = None
    ) -> tuple[Relationship, ...]:
        found = self._out.get(node, ())
        if relation is not None:
            return tuple(r for r in found if r.relation is relation)
        return tuple(found)

    def inbound(
        self, node: str, *, relation: RelationType | None = None
    ) -> tuple[Relationship, ...]:
        found = self._in.get(node, ())
        if relation is not None:
            return tuple(r for r in found if r.relation is relation)
        return tuple(found)

    def of_type(self, relation: RelationType) -> tuple[Relationship, ...]:
        return tuple(r for r in self._relationships if r.relation is relation)

    def neighbours(self, node: str) -> tuple[str, ...]:
        """Every node reachable in one hop, in either direction."""
        seen: dict[str, None] = {}
        for relationship in self.outbound(node):
            seen.setdefault(relationship.target, None)
        for relationship in self.inbound(node):
            seen.setdefault(relationship.source, None)
        return tuple(seen)

    def degree(self, node: str) -> int:
        return len(self._out.get(node, ())) + len(self._in.get(node, ()))

    def is_navigable_both_ways(self, relationship: Relationship) -> bool:
        """True iff the relationship is answerable from either endpoint (UKIP-LAW-006).

        Symmetric relations must have their mirror present; asymmetric relations are
        navigable because the target's inbound adjacency contains them.
        """
        if relationship.relation.is_symmetric:
            mirror = relationship.mirrored().key()
            return any(r.key() == mirror for r in self._relationships)
        return relationship in self.inbound(relationship.target)

    def unnavigable(self) -> tuple[Relationship, ...]:
        """Relationships that cannot be read from both endpoints."""
        return tuple(r for r in self._relationships if not self.is_navigable_both_ways(r))

    # -- composition -----------------------------------------------------------

    def compose(self, *, max_depth: int = 3) -> RelationshipSet:
        """Return a new set including relationships derived by composition.

        Fixed-point iteration bounded by ``max_depth``: knowledge composes, but the
        closure is computed on demand and bounded, so a derived view can never become
        an unbounded second copy of the corpus.
        """
        if max_depth < 1:
            raise RelationshipCompositionError("max_depth must be at least 1", depth=max_depth)
        # Keyed by identity(), not key(): the seed set may hold several validity-
        # scoped versions of the same triple, and keying by key() alone would drop
        # every version but the last one seen (P4-F-002 regression guard).
        known: dict[tuple[str, str, str, str | None], Relationship] = {
            r.identity(): r for r in self._relationships
        }
        frontier = list(self._relationships)
        for _ in range(max_depth):
            produced: list[Relationship] = []
            for left in frontier:
                for right in self.outbound(left.target):
                    composite = COMPOSITION_RULES.get((left.relation, right.relation))
                    if composite is None:
                        continue
                    if left.source == right.target:
                        continue  # composing back onto the origin adds nothing
                    candidate = Relationship(
                        source=left.source,
                        target=right.target,
                        relation=composite,
                        note=f"composed:{left.relation.value}+{right.relation.value}",
                        derived=True,
                        path=(left.source, left.target, right.target),
                    )
                    if candidate.identity() in known:
                        continue
                    known[candidate.identity()] = candidate
                    produced.append(candidate)
            if not produced:
                break
            frontier = produced
        return RelationshipSet(known.values(), self._dangling)

    def transitive(
        self, node: str, *, relation: RelationType, inbound: bool = False
    ) -> tuple[str, ...]:
        """Deterministic transitive closure over one relation type."""
        order: dict[str, None] = {}
        visited = {node}
        frontier = [node]
        while frontier:
            current = frontier.pop(0)
            adjacency = (
                self.inbound(current, relation=relation)
                if inbound
                else self.outbound(current, relation=relation)
            )
            nexts = sorted({r.source if inbound else r.target for r in adjacency})
            for candidate in nexts:
                if candidate not in visited:
                    visited.add(candidate)
                    order.setdefault(candidate, None)
                    frontier.append(candidate)
        return tuple(order)

    # -- cycles ----------------------------------------------------------------

    def cycles(self) -> tuple[Cycle, ...]:
        """Every cycle found within a family that must remain acyclic."""
        found: list[Cycle] = []
        for family, types in sorted(ACYCLIC_FAMILIES.items()):
            adjacency: dict[str, list[str]] = {}
            for relationship in self._relationships:
                if relationship.relation in types:
                    adjacency.setdefault(relationship.source, []).append(relationship.target)
            for node in sorted(adjacency):
                members = self._find_cycle(adjacency, node)
                if members and not any(
                    c.family == family and set(c.members) == set(members) for c in found
                ):
                    found.append(Cycle(family=family, members=members))
        return tuple(found)

    @staticmethod
    def _find_cycle(adjacency: Mapping[str, list[str]], start: str) -> tuple[str, ...]:
        """Depth-first search for a cycle reachable from ``start`` (iterative)."""
        stack: list[tuple[str, list[str]]] = [(start, [start])]
        seen: set[str] = set()
        while stack:
            node, path = stack.pop()
            for neighbour in sorted(adjacency.get(node, ())):
                if neighbour == start:
                    return tuple(path)
                if neighbour in path:
                    return tuple(path[path.index(neighbour) :])
                if neighbour in seen:
                    continue
                seen.add(neighbour)
                stack.append((neighbour, [*path, neighbour]))
        return ()

    @property
    def is_acyclic(self) -> bool:
        return not self.cycles()

    # -- serialization ---------------------------------------------------------

    def counts(self) -> dict[str, int]:
        return {
            "relationships": len(self._relationships),
            "asserted": len(self.asserted()),
            "derived": len(self.derived()),
            "dangling": len(self._dangling),
            "nodes": len(self.nodes()),
            "types": len(self.types()),
        }

    def seal(self) -> str:
        # identity(), not key(): two validity-scoped versions of one triple must
        # produce different content, or the seal could not detect a temporal edit.
        return content_hash([list(r.identity()) for r in self._relationships])

    # -- temporal (UCKP-ART-07 validity, P4-F-002) ------------------------------

    def valid_at(
        self, coordinate: TemporalCoordinate, *, registry: TemporalRegistry | None = None
    ) -> RelationshipSet:
        """Historical reconstruction: the subgraph that held at ``coordinate``.

        A timeless relationship (``validity=None``) always holds. A relationship
        whose window cannot be compared to ``coordinate`` — no shared reference
        system and no declared conversion — is excluded rather than guessed into
        either state: Law 7 makes that comparison undefined, and an undefined
        comparison is not evidence of validity.
        """
        kept = [r for r in self._relationships if _holds_at(r.validity, coordinate, registry)]
        return RelationshipSet(kept, self._dangling)

    def to_dict(self) -> dict[str, Any]:
        return {
            "counts": self.counts(),
            "seal": self.seal(),
            "acyclic": self.is_acyclic,
            "types": [t.value for t in self.types()],
            "relationships": [r.to_dict() for r in self._relationships],
            "dangling": [d.to_dict() for d in self._dangling],
            "cycles": [c.to_dict() for c in self.cycles()],
        }


def build_relationships(
    registry: KnowledgeRegistry, *, close_symmetric: bool = True
) -> RelationshipSet:
    """Resolve and close every relationship declared across the registry.

    Resolution uses the registry's alias map, so a provider may cite a peer by
    whichever address it knows — canonical id, ``provider:key``, bare key, or content
    digest — and still produce a correctly wired graph.
    """
    resolver = registry.reference_map()
    resolved: list[Relationship] = []
    dangling: list[DanglingRelationship] = []
    for record in registry.records():
        for declaration in record.relations:
            target = resolver.get(declaration.target)
            if target is None:
                dangling.append(
                    DanglingRelationship(
                        source=record.knowledge_id,
                        declared_target=declaration.target,
                        relation=declaration.relation,
                        note=declaration.note,
                    )
                )
                continue
            if target == record.knowledge_id:
                continue  # a record relating to itself carries no information
            relationship = Relationship(
                source=record.knowledge_id,
                target=target,
                relation=declaration.relation,
                note=declaration.note,
                validity=declaration.validity,
            )
            resolved.append(relationship)
            if close_symmetric and relationship.relation.is_symmetric:
                resolved.append(relationship.mirrored())
    return RelationshipSet(resolved, dangling)


def relationships_of(
    registry: KnowledgeRegistry, record: RegisteredKnowledge
) -> tuple[Relationship, ...]:
    """Convenience: every resolved relationship touching one record."""
    relationships = build_relationships(registry)
    return tuple(
        sorted(
            {
                *relationships.outbound(record.knowledge_id),
                *relationships.inbound(record.knowledge_id),
            },
            key=lambda r: r.key(),
        )
    )


__all__ = [
    "SYMMETRIC",
    "SEMANTIC_INVERSES",
    "COMPOSITION_RULES",
    "ACYCLIC_FAMILIES",
    "Relationship",
    "DanglingRelationship",
    "Cycle",
    "RelationshipSet",
    "build_relationships",
    "relationships_of",
]
