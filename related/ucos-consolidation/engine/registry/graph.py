"""TASK-000013 — Relationship graph adapter (EPIC-002, read-only).

A read-only projection of ``00-BOOK/DATA/relationships.json`` as a navigable,
directed multigraph. Every edge is a first-class :class:`Relationship`
(TASK-000011); the adapter builds outbound and inbound adjacency indices once and
answers neighbour / edge / dependency queries deterministically.

The graph never mutates the corpus (DP-03) and exposes only immutable tuples, so
callers cannot alter the loaded topology.
"""

from __future__ import annotations

from collections.abc import Iterable

from engine.registry.errors import RegistryValidationError
from engine.registry.models import Relationship
from engine.registry.source import RELATIONSHIPS_FILE, RegistrySource

# Canonical dependency edge type (relationship.schema.json vocabulary).
DEPENDS_ON = "Depends-On"
PARENT = "Parent"
CHILD = "Child"


class RelationshipGraph:
    """Read-only, directed multigraph over registered relationships."""

    __slots__ = ("_edges", "_by_id", "_out", "_in")

    def __init__(self, relationships: Iterable[Relationship]) -> None:
        self._edges: tuple[Relationship, ...] = tuple(relationships)
        by_id: dict[str, Relationship] = {}
        out: dict[str, list[Relationship]] = {}
        inbound: dict[str, list[Relationship]] = {}
        for edge in self._edges:
            if edge.edge_id in by_id:
                raise RegistryValidationError(
                    "duplicate edge_id in relationship registry", edge_id=edge.edge_id
                )
            by_id[edge.edge_id] = edge
            out.setdefault(edge.source, []).append(edge)
            inbound.setdefault(edge.target, []).append(edge)
        self._by_id = by_id
        self._out = out
        self._in = inbound

    # -- construction ----------------------------------------------------------

    @classmethod
    def from_source(cls, source: RegistrySource) -> RelationshipGraph:
        """Build the graph from the read-only registry source."""
        _envelope, records = source.read_document(RELATIONSHIPS_FILE, root_key="relationships")
        return cls(Relationship.from_dict(record) for record in records)

    # -- size / iteration ------------------------------------------------------

    def __len__(self) -> int:
        return len(self._edges)

    def __iter__(self):
        return iter(self._edges)

    def count(self) -> int:
        """Total number of edges."""
        return len(self._edges)

    def all(self) -> tuple[Relationship, ...]:
        """Every edge in stable registry order."""
        return self._edges

    def edge(self, edge_id: str) -> Relationship | None:
        """Return the edge with ``edge_id`` or ``None``."""
        return self._by_id.get(edge_id)

    # -- edge queries ----------------------------------------------------------

    def edges_from(self, node: str, *, type: str | None = None) -> tuple[Relationship, ...]:
        """Outbound edges from ``node``, optionally filtered by ``type``."""
        edges = self._out.get(node, ())
        if type is not None:
            return tuple(e for e in edges if e.type == type)
        return tuple(edges)

    def edges_to(self, node: str, *, type: str | None = None) -> tuple[Relationship, ...]:
        """Inbound edges into ``node``, optionally filtered by ``type``."""
        edges = self._in.get(node, ())
        if type is not None:
            return tuple(e for e in edges if e.type == type)
        return tuple(edges)

    def edges_of_type(self, type: str) -> tuple[Relationship, ...]:
        """Every edge of a given relationship ``type``."""
        return tuple(e for e in self._edges if e.type == type)

    # -- neighbour queries -----------------------------------------------------

    def successors(self, node: str, *, type: str | None = None) -> tuple[str, ...]:
        """Distinct target nodes reachable from ``node`` via one edge."""
        seen: dict[str, None] = {}
        for edge in self.edges_from(node, type=type):
            seen.setdefault(edge.target, None)
        return tuple(seen)

    def predecessors(self, node: str, *, type: str | None = None) -> tuple[str, ...]:
        """Distinct source nodes that reach ``node`` via one edge."""
        seen: dict[str, None] = {}
        for edge in self.edges_to(node, type=type):
            seen.setdefault(edge.source, None)
        return tuple(seen)

    def neighbors(self, node: str) -> tuple[str, ...]:
        """Distinct nodes adjacent to ``node`` in either direction."""
        seen: dict[str, None] = {}
        for target in self.successors(node):
            seen.setdefault(target, None)
        for source in self.predecessors(node):
            seen.setdefault(source, None)
        return tuple(seen)

    def degree(self, node: str) -> int:
        """Total number of edges incident to ``node`` (out + in)."""
        return len(self._out.get(node, ())) + len(self._in.get(node, ()))

    def has_node(self, node: str) -> bool:
        """True iff ``node`` participates in at least one edge."""
        return node in self._out or node in self._in

    def nodes(self) -> tuple[str, ...]:
        """Every distinct node that participates in an edge, ordered."""
        return tuple(sorted(set(self._out) | set(self._in)))

    def types(self) -> tuple[str, ...]:
        """Distinct relationship types present, ordered."""
        return tuple(sorted({e.type for e in self._edges}))

    # -- semantic helpers ------------------------------------------------------

    def dependencies_of(self, node: str) -> tuple[str, ...]:
        """Nodes that ``node`` Depends-On (outbound ``Depends-On`` targets)."""
        return self.successors(node, type=DEPENDS_ON)

    def dependents_of(self, node: str) -> tuple[str, ...]:
        """Nodes that Depend-On ``node`` (inbound ``Depends-On`` sources)."""
        return self.predecessors(node, type=DEPENDS_ON)

    def parents_of(self, node: str) -> tuple[str, ...]:
        """Parent nodes of ``node`` (outbound ``Parent`` targets)."""
        return self.successors(node, type=PARENT)

    def children_of(self, node: str) -> tuple[str, ...]:
        """Child nodes of ``node`` (outbound ``Child`` targets)."""
        return self.successors(node, type=CHILD)


__all__ = ["RelationshipGraph", "DEPENDS_ON", "PARENT", "CHILD"]
