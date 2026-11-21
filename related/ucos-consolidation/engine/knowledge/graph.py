"""UKDA Part 05 — Universal Knowledge Graph (EPIC-UKDA).

A read-only, directed multigraph over canonical knowledge. Every edge is a typed,
first-class :class:`KnowledgeEdge` drawn from the seventeen canonical
:class:`~engine.knowledge.model.RelationType` values. The graph is derived
deterministically from the link topology already carried by each
:class:`~engine.knowledge.cko.CanonicalKnowledgeObject` (Part 02) — plus any
explicitly authored edges — so relationships are never a second, drifting source
of truth: they are a projection of the objects themselves.

The graph answers the navigation, dependency, reverse-dependency and impact
queries that Repository Intelligence (Part 09) and Validation (Part 10) build on.
It never mutates its inputs and exposes only immutable tuples.
"""

from __future__ import annotations

from collections.abc import Iterable

from engine.knowledge.cko import CanonicalKnowledgeObject
from engine.knowledge.errors import RelationshipError
from engine.knowledge.model import RelationType

# Edge types that propagate architectural impact backward (who is affected if the
# target changes). If X depends-on / consumes / extends / implements Y, then a
# change to Y impacts X. Impact analysis walks these edges in the inbound direction.
_IMPACT_TYPES: frozenset[RelationType] = frozenset(
    {
        RelationType.DEPENDS_ON,
        RelationType.CONSUMES,
        RelationType.EXTENDS,
        RelationType.IMPLEMENTS,
        RelationType.DERIVED_FROM,
        RelationType.GENERATED_FROM,
    }
)


class KnowledgeEdge:
    """A single typed, directional edge in the Universal Knowledge Graph."""

    __slots__ = ("source", "target", "type", "note")

    def __init__(self, source: str, target: str, type: RelationType, note: str = "") -> None:
        if not source or not target:
            raise RelationshipError(
                "edge endpoints must be non-empty", source=source, target=target
            )
        if not isinstance(type, RelationType):
            raise RelationshipError("edge type must be a RelationType", type=str(type))
        self.source = source
        self.target = target
        self.type = type
        self.note = note

    def key(self) -> tuple[str, str, str]:
        """A stable de-duplication key (source, target, type)."""
        return (self.source, self.target, self.type.value)

    def to_dict(self) -> dict[str, str]:
        return {
            "from": self.source,
            "to": self.target,
            "type": self.type.value,
            "note": self.note,
        }

    def __eq__(self, other: object) -> bool:
        return isinstance(other, KnowledgeEdge) and self.key() == other.key()

    def __hash__(self) -> int:
        return hash(self.key())

    def __repr__(self) -> str:  # pragma: no cover - debug aid
        return f"KnowledgeEdge({self.source!r} -{self.type.value}-> {self.target!r})"


def derive_edges(cko: CanonicalKnowledgeObject) -> tuple[KnowledgeEdge, ...]:
    """Project the typed edges implied by a single CKO's link topology (Part 02→05)."""
    edges: list[KnowledgeEdge] = []
    me = cko.cko_id

    def add(src: str, tgt: str, rel: RelationType, note: str) -> None:
        edges.append(KnowledgeEdge(src, tgt, rel, note))

    if cko.parent:
        add(me, cko.parent, RelationType.EXTENDS, "structural:parent")
    for child in cko.children:
        add(child, me, RelationType.EXTENDS, "structural:child")
    for dep in cko.dependencies:
        add(me, dep, RelationType.DEPENDS_ON, "structural:dependency")
    for consumer in cko.consumers:
        add(consumer, me, RelationType.CONSUMES, "structural:consumer")
    for old in cko.supersedes:
        add(me, old, RelationType.SUPERSEDES, "structural:supersedes")
    if cko.superseded_by:
        add(cko.superseded_by, me, RelationType.SUPERSEDES, "structural:superseded-by")
    for link in cko.knowledge_links:
        add(me, link, RelationType.RELATED_TO, "structural:knowledge-link")
    for rival in cko.conflicts_with:
        add(me, rival, RelationType.CONFLICTS_WITH, "structural:conflict")
    for decision in cko.decision_links:
        add(me, decision, RelationType.REFERENCES, "structural:decision-link")
    return tuple(edges)


class KnowledgeGraph:
    """Read-only, directed multigraph over canonical knowledge (Part 05)."""

    __slots__ = ("_edges", "_out", "_in")

    def __init__(self, edges: Iterable[KnowledgeEdge]) -> None:
        deduped: dict[tuple[str, str, str], KnowledgeEdge] = {}
        for edge in edges:
            deduped.setdefault(edge.key(), edge)
        self._edges: tuple[KnowledgeEdge, ...] = tuple(deduped.values())
        out: dict[str, list[KnowledgeEdge]] = {}
        inbound: dict[str, list[KnowledgeEdge]] = {}
        for edge in self._edges:
            out.setdefault(edge.source, []).append(edge)
            inbound.setdefault(edge.target, []).append(edge)
        self._out = out
        self._in = inbound

    # -- construction ----------------------------------------------------------

    @classmethod
    def from_objects(
        cls,
        objects: Iterable[CanonicalKnowledgeObject],
        *,
        extra_edges: Iterable[KnowledgeEdge] = (),
    ) -> KnowledgeGraph:
        """Build the graph by projecting every CKO's links, plus explicit edges."""
        derived: list[KnowledgeEdge] = []
        for cko in objects:
            derived.extend(derive_edges(cko))
        derived.extend(extra_edges)
        return cls(derived)

    # -- size / iteration ------------------------------------------------------

    def __len__(self) -> int:
        return len(self._edges)

    def __iter__(self):
        return iter(self._edges)

    def all(self) -> tuple[KnowledgeEdge, ...]:
        return self._edges

    def nodes(self) -> tuple[str, ...]:
        """Every distinct node that participates in an edge, ordered."""
        return tuple(sorted(set(self._out) | set(self._in)))

    def types(self) -> tuple[RelationType, ...]:
        """Distinct relationship types present, ordered by value."""
        return tuple(sorted({e.type for e in self._edges}, key=lambda t: t.value))

    def has_node(self, node: str) -> bool:
        return node in self._out or node in self._in

    # -- edge queries ----------------------------------------------------------

    def edges_from(
        self, node: str, *, type: RelationType | None = None
    ) -> tuple[KnowledgeEdge, ...]:
        edges = self._out.get(node, ())
        if type is not None:
            return tuple(e for e in edges if e.type is type)
        return tuple(edges)

    def edges_to(self, node: str, *, type: RelationType | None = None) -> tuple[KnowledgeEdge, ...]:
        edges = self._in.get(node, ())
        if type is not None:
            return tuple(e for e in edges if e.type is type)
        return tuple(edges)

    def edges_of_type(self, type: RelationType) -> tuple[KnowledgeEdge, ...]:
        return tuple(e for e in self._edges if e.type is type)

    # -- neighbour queries -----------------------------------------------------

    def successors(self, node: str, *, type: RelationType | None = None) -> tuple[str, ...]:
        seen: dict[str, None] = {}
        for edge in self.edges_from(node, type=type):
            seen.setdefault(edge.target, None)
        return tuple(seen)

    def predecessors(self, node: str, *, type: RelationType | None = None) -> tuple[str, ...]:
        seen: dict[str, None] = {}
        for edge in self.edges_to(node, type=type):
            seen.setdefault(edge.source, None)
        return tuple(seen)

    def neighbors(self, node: str) -> tuple[str, ...]:
        seen: dict[str, None] = {}
        for target in self.successors(node):
            seen.setdefault(target, None)
        for source in self.predecessors(node):
            seen.setdefault(source, None)
        return tuple(seen)

    def degree(self, node: str) -> int:
        return len(self._out.get(node, ())) + len(self._in.get(node, ()))

    # -- semantic helpers ------------------------------------------------------

    def dependencies_of(self, node: str) -> tuple[str, ...]:
        """Nodes that ``node`` directly depends on (outbound ``depends-on``)."""
        return self.successors(node, type=RelationType.DEPENDS_ON)

    def dependents_of(self, node: str) -> tuple[str, ...]:
        """Nodes that directly depend on ``node`` (inbound ``depends-on``)."""
        return self.predecessors(node, type=RelationType.DEPENDS_ON)

    def conflicts_of(self, node: str) -> tuple[str, ...]:
        """Nodes declared to conflict with ``node`` (symmetric ``conflicts-with``)."""
        seen: dict[str, None] = {}
        for target in self.successors(node, type=RelationType.CONFLICTS_WITH):
            seen.setdefault(target, None)
        for source in self.predecessors(node, type=RelationType.CONFLICTS_WITH):
            seen.setdefault(source, None)
        return tuple(seen)

    def _transitive(
        self, start: str, *, inbound: bool, types: frozenset[RelationType] | None
    ) -> tuple[str, ...]:
        """Deterministic BFS closure over inbound/outbound edges filtered by ``types``."""
        order: dict[str, None] = {}
        frontier = [start]
        visited = {start}
        while frontier:
            current = frontier.pop(0)
            adjacency = self._in.get(current, ()) if inbound else self._out.get(current, ())
            nexts = []
            for edge in adjacency:
                if types is not None and edge.type not in types:
                    continue
                nexts.append(edge.source if inbound else edge.target)
            for node in sorted(set(nexts)):
                if node not in visited:
                    visited.add(node)
                    order.setdefault(node, None)
                    frontier.append(node)
        return tuple(order)

    def impact_of(self, node: str) -> tuple[str, ...]:
        """Transitive reverse-dependency closure: everything affected if ``node`` changes."""
        return self._transitive(node, inbound=True, types=_IMPACT_TYPES)

    def reachable_from(self, node: str) -> tuple[str, ...]:
        """Transitive outbound closure of everything ``node`` (transitively) relies on."""
        return self._transitive(node, inbound=False, types=_IMPACT_TYPES)


__all__ = ["KnowledgeEdge", "KnowledgeGraph", "derive_edges"]
