"""UCKP Layer Zero — the Universal Constitutional Knowledge Graph (Article 7).

Every object is a node. Every dependency, relationship, authority derivation, trace
link and evolution step is an edge. Article 7 adds one demand that separates this
from a diagram: *every relationship is executable*. An edge whose target cannot be
resolved to a real object is not a relationship, it is a wish, and
:meth:`UniversalKnowledgeGraph.dangling` finds every one of them.

Edges are **derived, never authored**. :func:`derive_edges` reads them out of the
facets that already state them, so the graph cannot disagree with the objects — there
is no second place to update and therefore no second authority (Article 3). Adding an
edge means changing the object that claims the relationship.

Twelve relationship classes are supported (the ``uckp.relationship-class``
vocabulary). Classing edges is what makes the difficult questions answerable
separately: "is authority acyclic?" is a question about one class, and asking it of
all edges at once would be meaningless, because knowledge legitimately contains
cycles while authority never may.
"""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from dataclasses import dataclass

from engine.uckp.canonical import content_hash
from engine.uckp.errors import CircularAuthorityError, RelationshipError, UnknownObjectError
from engine.uckp.ucko import UCKO

#: Edge target scopes. An ``object`` edge must resolve to a UCKO; a ``state`` edge
#: points into the constitutional timeline, which is a different register.
OBJECT_SCOPE = "object"
STATE_SCOPE = "state"


@dataclass(frozen=True, slots=True)
class UniversalKnowledgeEdge:
    """A derived, executable binding between two constitutional identities."""

    source: str
    target: str
    relation: str
    relationship_class: str
    scope: str = OBJECT_SCOPE

    def to_dict(self) -> dict[str, str]:
        return {
            "source": self.source,
            "target": self.target,
            "relation": self.relation,
            "relationship_class": self.relationship_class,
            "scope": self.scope,
        }

    def key(self) -> tuple[str, str, str, str, str]:
        return (
            self.source,
            self.relationship_class,
            self.relation,
            self.target,
            self.scope,
        )


def derive_edges(obj: UCKO) -> tuple[UniversalKnowledgeEdge, ...]:
    """Read every edge out of an object's facets. Deterministic and total."""
    edges: list[UniversalKnowledgeEdge] = []
    source = obj.ucko_id
    for dependency in obj.dependencies:
        edges.append(UniversalKnowledgeEdge(source, dependency, "depends-on", "constitutional"))
    for relationship in obj.relationships:
        edges.append(
            UniversalKnowledgeEdge(
                source,
                relationship.target,
                relationship.relation,
                relationship.relationship_class,
            )
        )
    parent = obj.authority.derives_from
    if parent and parent != source:
        edges.append(UniversalKnowledgeEdge(source, parent, "derived-from", "authority"))
    if obj.ownership.owner:
        edges.append(
            UniversalKnowledgeEdge(
                source, obj.ownership.owner, "owns", "ownership", scope=STATE_SCOPE
            )
        )
    for link in obj.traceability:
        edges.append(UniversalKnowledgeEdge(source, link.downstream, "references", "traceability"))
        if link.upstream != source:
            edges.append(
                UniversalKnowledgeEdge(source, link.upstream, "derived-from", "traceability")
            )
    for state_id in obj.evolution_history:
        edges.append(
            UniversalKnowledgeEdge(
                source, state_id, "generated-from", "evolution", scope=STATE_SCOPE
            )
        )
    unique = {edge.key(): edge for edge in edges}
    return tuple(unique[key] for key in sorted(unique))


class UniversalKnowledgeGraph:
    """The graph of the Constitutional Knowledge Universe."""

    __slots__ = ("_nodes", "_edges")

    def __init__(self, objects: Iterable[UCKO] = ()) -> None:
        self._nodes: dict[str, UCKO] = {}
        for obj in objects:
            if obj.ucko_id in self._nodes:
                raise RelationshipError("object appears twice in a graph", ucko_id=obj.ucko_id)
            self._nodes[obj.ucko_id] = obj
        derived: dict[tuple[str, str, str, str, str], UniversalKnowledgeEdge] = {}
        for key in sorted(self._nodes):
            for edge in derive_edges(self._nodes[key]):
                derived[edge.key()] = edge
        self._edges: tuple[UniversalKnowledgeEdge, ...] = tuple(
            derived[key] for key in sorted(derived)
        )

    # --- nodes ------------------------------------------------------------------

    @classmethod
    def from_objects(cls, objects: Iterable[UCKO]) -> UniversalKnowledgeGraph:
        return cls(objects)

    def node_ids(self) -> tuple[str, ...]:
        return tuple(sorted(self._nodes))

    def nodes(self) -> tuple[UCKO, ...]:
        return tuple(self._nodes[key] for key in self.node_ids())

    def node(self, ucko_id: str) -> UCKO | None:
        return self._nodes.get(str(ucko_id))

    def require_node(self, ucko_id: str) -> UCKO:
        node = self.node(ucko_id)
        if node is None:
            raise UnknownObjectError("no such knowledge object", ucko_id=str(ucko_id))
        return node

    def __len__(self) -> int:
        return len(self._nodes)

    def __contains__(self, ucko_id: object) -> bool:
        return str(ucko_id) in self._nodes

    # --- edges ------------------------------------------------------------------

    def edges(self) -> tuple[UniversalKnowledgeEdge, ...]:
        return self._edges

    def edges_of_class(self, relationship_class: str) -> tuple[UniversalKnowledgeEdge, ...]:
        return tuple(e for e in self._edges if e.relationship_class == str(relationship_class))

    def relationship_classes(self) -> tuple[str, ...]:
        return tuple(sorted({edge.relationship_class for edge in self._edges}))

    def out_edges(self, ucko_id: str) -> tuple[UniversalKnowledgeEdge, ...]:
        return tuple(e for e in self._edges if e.source == str(ucko_id))

    def in_edges(self, ucko_id: str) -> tuple[UniversalKnowledgeEdge, ...]:
        return tuple(e for e in self._edges if e.target == str(ucko_id))

    def dangling(self) -> tuple[UniversalKnowledgeEdge, ...]:
        """Object-scoped edges whose target does not resolve — the unexecutable ones."""
        return tuple(
            edge
            for edge in self._edges
            if edge.scope == OBJECT_SCOPE and edge.target not in self._nodes
        )

    def execute(self, edge: UniversalKnowledgeEdge) -> UCKO:
        """Resolve an edge to the object it names. This is what "executable" means."""
        if edge.scope != OBJECT_SCOPE:
            raise RelationshipError(
                "only object-scoped relationships resolve to an object",
                scope=edge.scope,
                target=edge.target,
            )
        return self.require_node(edge.target)

    # --- reachability -----------------------------------------------------------

    def neighbours(self, ucko_id: str) -> tuple[str, ...]:
        return tuple(sorted({e.target for e in self.out_edges(ucko_id)}))

    def reachable_from(self, ucko_id: str) -> frozenset[str]:
        """Every object reachable by following object-scoped edges in either direction.

        Reachability is undirected on purpose. Article 5 (Zero Orphans) asks whether an
        object is *connected to the constitution*, and a capability the law governs is
        connected whether it points at the law or the law points at it.
        """
        start = str(ucko_id)
        if start not in self._nodes:
            return frozenset()
        seen = {start}
        frontier = [start]
        adjacency: dict[str, set[str]] = {key: set() for key in self._nodes}
        for edge in self._edges:
            if edge.scope != OBJECT_SCOPE:
                continue
            if edge.source in adjacency and edge.target in adjacency:
                adjacency[edge.source].add(edge.target)
                adjacency[edge.target].add(edge.source)
        while frontier:
            current = frontier.pop()
            for nxt in sorted(adjacency.get(current, ())):
                if nxt not in seen:
                    seen.add(nxt)
                    frontier.append(nxt)
        return frozenset(seen)

    def orphans(self, root_id: str) -> tuple[str, ...]:
        """Objects not connected to ``root_id`` through the graph."""
        reachable = self.reachable_from(root_id)
        return tuple(key for key in self.node_ids() if key not in reachable)

    def roots(self) -> tuple[str, ...]:
        """Objects whose authority derives from themselves — the constitutional roots."""
        return tuple(
            key for key in self.node_ids() if self._nodes[key].authority.derives_from in ("", key)
        )

    # --- cycles -----------------------------------------------------------------

    def cycles(self, relationship_class: str) -> tuple[tuple[str, ...], ...]:
        """Every directed cycle within one relationship class (deterministic order)."""
        adjacency: dict[str, list[str]] = {key: [] for key in self._nodes}
        for edge in self.edges_of_class(relationship_class):
            if edge.source in adjacency and edge.target in adjacency:
                adjacency[edge.source].append(edge.target)
        for key in adjacency:
            adjacency[key].sort()
        found: list[tuple[str, ...]] = []
        seen_cycles: set[frozenset[str]] = set()
        state: dict[str, int] = {}
        path: list[str] = []

        def visit(node: str) -> None:
            state[node] = 1
            path.append(node)
            for nxt in adjacency.get(node, ()):
                if state.get(nxt, 0) == 0:
                    visit(nxt)
                elif state.get(nxt) == 1:
                    cycle = tuple(path[path.index(nxt) :])
                    signature = frozenset(cycle)
                    if signature not in seen_cycles:
                        seen_cycles.add(signature)
                        found.append(cycle)
            path.pop()
            state[node] = 2

        for key in sorted(adjacency):
            if state.get(key, 0) == 0:
                visit(key)
        return tuple(sorted(found))

    def require_acyclic_authority(self) -> None:
        """Fail closed if authority derivation contains a cycle (Article 1)."""
        cycles = self.cycles("authority")
        if cycles:
            raise CircularAuthorityError(
                "authority derivation contains a cycle", cycles=[list(c) for c in cycles]
            )

    def authority_chain(self, ucko_id: str) -> tuple[str, ...]:
        """The chain from ``ucko_id`` to its constitutional root, in order."""
        chain: list[str] = []
        current = str(ucko_id)
        while True:
            node = self.node(current)
            if node is None:
                chain.append(current)
                break
            chain.append(current)
            parent = node.authority.derives_from
            if not parent or parent == current:
                break
            if parent in chain:
                raise CircularAuthorityError(
                    "authority chain re-enters itself", ucko_id=str(ucko_id), at=parent
                )
            current = parent
        return tuple(chain)

    # --- serialization ----------------------------------------------------------

    def counts(self) -> dict[str, int]:
        return {
            "nodes": len(self._nodes),
            "edges": len(self._edges),
            "classes": len(self.relationship_classes()),
            "dangling": len(self.dangling()),
            "roots": len(self.roots()),
        }

    def to_document(self) -> dict[str, object]:
        return {
            "schema": "ucos-uckp-knowledge-graph",
            "version": "1.0.0",
            "counts": self.counts(),
            "nodes": [self._nodes[key].describe() for key in self.node_ids()],
            "edges": [edge.to_dict() for edge in self._edges],
        }

    def fingerprint(self) -> str:
        """The content digest of the whole graph topology."""
        return content_hash(
            {
                "nodes": [
                    {"id": key, "sha256": self._nodes[key].content_sha256}
                    for key in self.node_ids()
                ],
                "edges": [edge.to_dict() for edge in self._edges],
            }
        )

    def adjacency(self) -> Mapping[str, tuple[str, ...]]:
        return {key: self.neighbours(key) for key in self.node_ids()}


__all__ = [
    "OBJECT_SCOPE",
    "STATE_SCOPE",
    "UniversalKnowledgeEdge",
    "UniversalKnowledgeGraph",
    "derive_edges",
]
