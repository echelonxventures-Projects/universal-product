"""UCOS-EPIC-002 (Terminal T2) — Universal Knowledge Graph domain model.

Immutable, typed value objects for the Universal Knowledge Graph plus the core
:class:`KnowledgeGraph` container. The graph is a *read projection* of Registry
Truth (the read-only ``00-BOOK`` substrate exposed by the EPIC-002 Registry
Adapter): nodes and edges are constructed once and never mutate the corpus (DP-03).

Mission invariants enforced here:
    * **No duplicate nodes** — a node identifier maps to exactly one node; a
      conflicting re-declaration raises :class:`DuplicateNodeError`.
    * **Immutable identifiers** — :class:`Node` / :class:`Edge` are frozen; the
      identifier is the key and cannot be reassigned. Empty/invalid identifiers
      raise :class:`ImmutableIdentifierError`.
    * **Version aware** — every node carries an immutable ``version`` string and
      the graph records the provenance (``generated_at``/``generator_version``)
      of the substrate it was projected from.

The node/edge *type* vocabularies are intentionally open (UMB-006 §3): types are
plain strings so new entity classes and relationship kinds extend the graph
additively without a schema rewrite.
"""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from dataclasses import dataclass, field
from types import MappingProxyType
from typing import Any

from engine.graph.errors import (
    DuplicateEdgeError,
    DuplicateNodeError,
    ImmutableIdentifierError,
    NodeNotFoundError,
)

# --- open node-kind vocabulary (UMB-006 §3 — node types are open) --------------
# Canonical kinds the builder mints. New kinds may be added by projections without
# any change here; these constants exist only so call-sites avoid string typos.
KIND_ARTIFACT = "Artifact"
KIND_VOLUME = "Volume"
KIND_CATEGORY = "Category"
KIND_PROGRAM = "Program"
KIND_SIGNAL = "Signal"
KIND_CERT_DOMAIN = "CertificationDomain"


def _require_identifier(value: Any, *, what: str) -> str:
    """Return ``value`` as a non-empty string identifier or raise (immutable ids)."""
    if not isinstance(value, str) or not value:
        raise ImmutableIdentifierError(
            "identifier must be a non-empty string", what=what, value=repr(value)
        )
    return value


def _freeze_attributes(attributes: Mapping[str, Any] | None) -> Mapping[str, Any]:
    """Return a read-only view of ``attributes`` (defensive, immutable)."""
    if not attributes:
        return MappingProxyType({})
    return MappingProxyType(dict(attributes))


@dataclass(frozen=True, slots=True)
class Node:
    """A single, immutable node in the Universal Knowledge Graph.

    ``node_id`` is the immutable identity (e.g. ``UCOS-REG-000001``, ``VOL-000``,
    ``USIG-000000001`` or a synthetic ontology anchor like ``CATEGORY::REG``).
    ``kind`` is an open type string; ``version`` makes the node version-aware.
    """

    node_id: str
    kind: str
    label: str = ""
    version: str = ""
    attributes: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        _require_identifier(self.node_id, what="node_id")
        if not isinstance(self.kind, str) or not self.kind:
            raise ImmutableIdentifierError(
                "node kind must be a non-empty string", node=self.node_id
            )
        # Normalise attributes to a read-only mapping without breaking frozen-ness.
        object.__setattr__(self, "attributes", _freeze_attributes(self.attributes))
        object.__setattr__(self, "label", self.label or self.node_id)

    def identity(self) -> tuple[str, str, str, str, tuple[tuple[str, Any], ...]]:
        """A structural identity used to detect *conflicting* duplicate nodes."""
        return (
            self.node_id,
            self.kind,
            self.label,
            self.version,
            tuple(sorted(self.attributes.items())),
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.node_id,
            "kind": self.kind,
            "label": self.label,
            "version": self.version,
            "attributes": dict(self.attributes),
        }


@dataclass(frozen=True, slots=True)
class Edge:
    """A single, immutable directed edge in the Universal Knowledge Graph.

    ``edge_id`` is the immutable identity (e.g. ``UEDGE-000000001`` or a synthetic
    projection edge id). ``type`` is an open relationship-type string (UMB-006 §3).
    """

    edge_id: str
    source: str
    target: str
    type: str
    note: str = ""
    attributes: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        _require_identifier(self.edge_id, what="edge_id")
        _require_identifier(self.source, what="edge.source")
        _require_identifier(self.target, what="edge.target")
        if not isinstance(self.type, str) or not self.type:
            raise ImmutableIdentifierError(
                "edge type must be a non-empty string", edge=self.edge_id
            )
        object.__setattr__(self, "attributes", _freeze_attributes(self.attributes))

    def identity(self) -> tuple[str, str, str, str]:
        """Structural identity used to detect *conflicting* duplicate edges."""
        return (self.edge_id, self.source, self.target, self.type)

    def to_dict(self) -> dict[str, Any]:
        return {
            "edge_id": self.edge_id,
            "from": self.source,
            "to": self.target,
            "type": self.type,
            "note": self.note,
            "attributes": dict(self.attributes),
        }


@dataclass(frozen=True, slots=True)
class GraphProvenance:
    """Version-awareness provenance for a projected graph (UMB-007 §7)."""

    generated_at: str = ""
    generator_version: str = ""
    artifact_count: int = 0
    relationship_count: int = 0
    volume_count: int = 0

    def to_dict(self) -> dict[str, Any]:
        return {
            "generated_at": self.generated_at,
            "generator_version": self.generator_version,
            "artifact_count": self.artifact_count,
            "relationship_count": self.relationship_count,
            "volume_count": self.volume_count,
        }


class KnowledgeGraph:
    """Read-only, directed multigraph over Registry Truth.

    The graph indexes nodes by immutable ``node_id`` and edges by immutable
    ``edge_id``, and maintains outbound/inbound adjacency for deterministic
    traversal. It never mutates its inputs and exposes only immutable value
    objects and tuples, so callers cannot alter the loaded topology.
    """

    __slots__ = ("_nodes", "_edges", "_out", "_in", "_provenance")

    def __init__(
        self,
        nodes: Iterable[Node] = (),
        edges: Iterable[Edge] = (),
        *,
        provenance: GraphProvenance | None = None,
    ) -> None:
        self._nodes: dict[str, Node] = {}
        self._edges: dict[str, Edge] = {}
        self._out: dict[str, list[Edge]] = {}
        self._in: dict[str, list[Edge]] = {}
        self._provenance = provenance or GraphProvenance()
        for node in nodes:
            self.add_node(node)
        for edge in edges:
            self.add_edge(edge)

    # -- mutation (build-time only; the corpus itself is never touched) --------

    def add_node(self, node: Node) -> None:
        """Register ``node``. Idempotent for identical nodes; raises on conflict.

        Enforces *No duplicate nodes*: re-adding a byte-identical node is a no-op,
        but presenting a different node under an already-used ``node_id`` raises
        :class:`DuplicateNodeError`.
        """
        existing = self._nodes.get(node.node_id)
        if existing is not None:
            if existing.identity() != node.identity():
                raise DuplicateNodeError(
                    "conflicting node already registered under this identifier",
                    node_id=node.node_id,
                    existing_kind=existing.kind,
                    incoming_kind=node.kind,
                )
            return
        self._nodes[node.node_id] = node

    def add_edge(self, edge: Edge) -> None:
        """Register ``edge``. Idempotent for identical edges; raises on conflict."""
        existing = self._edges.get(edge.edge_id)
        if existing is not None:
            if existing.identity() != edge.identity():
                raise DuplicateEdgeError(
                    "conflicting edge already registered under this identifier",
                    edge_id=edge.edge_id,
                )
            return
        self._edges[edge.edge_id] = edge
        self._out.setdefault(edge.source, []).append(edge)
        self._in.setdefault(edge.target, []).append(edge)

    # -- provenance ------------------------------------------------------------

    @property
    def provenance(self) -> GraphProvenance:
        """Version-awareness provenance of the substrate this graph projects."""
        return self._provenance

    # -- size / iteration ------------------------------------------------------

    def __len__(self) -> int:
        return len(self._nodes)

    def order(self) -> int:
        """Number of nodes (graph *order*)."""
        return len(self._nodes)

    def size(self) -> int:
        """Number of edges (graph *size*)."""
        return len(self._edges)

    def nodes(self) -> tuple[Node, ...]:
        """Every node, ordered by immutable identifier."""
        return tuple(self._nodes[nid] for nid in sorted(self._nodes))

    def edges(self) -> tuple[Edge, ...]:
        """Every edge, ordered by immutable identifier."""
        return tuple(self._edges[eid] for eid in sorted(self._edges))

    def node_ids(self) -> tuple[str, ...]:
        """Every node identifier, ordered."""
        return tuple(sorted(self._nodes))

    # -- lookups ---------------------------------------------------------------

    def has_node(self, node_id: str) -> bool:
        return node_id in self._nodes

    def has_edge(self, edge_id: str) -> bool:
        return edge_id in self._edges

    def node(self, node_id: str) -> Node:
        """Return the node with ``node_id`` or raise :class:`NodeNotFoundError`."""
        try:
            return self._nodes[node_id]
        except KeyError as exc:
            raise NodeNotFoundError("no node with that identifier", node_id=node_id) from exc

    def find(self, node_id: str) -> Node | None:
        """Return the node with ``node_id`` or ``None``."""
        return self._nodes.get(node_id)

    def edge(self, edge_id: str) -> Edge | None:
        """Return the edge with ``edge_id`` or ``None``."""
        return self._edges.get(edge_id)

    def version_of(self, node_id: str) -> str:
        """Return the immutable version string recorded for ``node_id``."""
        return self.node(node_id).version

    # -- kind / type views -----------------------------------------------------

    def nodes_of_kind(self, kind: str) -> tuple[Node, ...]:
        """All nodes of a given ``kind``, ordered by identifier."""
        return tuple(n for n in self.nodes() if n.kind == kind)

    def kinds(self) -> tuple[str, ...]:
        """Distinct node kinds present, ordered."""
        return tuple(sorted({n.kind for n in self._nodes.values()}))

    def edge_types(self) -> tuple[str, ...]:
        """Distinct edge types present, ordered."""
        return tuple(sorted({e.type for e in self._edges.values()}))

    # -- edge queries ----------------------------------------------------------

    def edges_from(self, node_id: str, *, type: str | None = None) -> tuple[Edge, ...]:
        """Outbound edges from ``node_id``, optionally filtered by ``type``."""
        edges = self._out.get(node_id, ())
        if type is not None:
            return tuple(e for e in edges if e.type == type)
        return tuple(edges)

    def edges_to(self, node_id: str, *, type: str | None = None) -> tuple[Edge, ...]:
        """Inbound edges into ``node_id``, optionally filtered by ``type``."""
        edges = self._in.get(node_id, ())
        if type is not None:
            return tuple(e for e in edges if e.type == type)
        return tuple(edges)

    def edges_of_type(self, type: str) -> tuple[Edge, ...]:
        """Every edge of a given relationship ``type`` (ordered by edge id)."""
        return tuple(e for e in self.edges() if e.type == type)

    # -- neighbour queries -----------------------------------------------------

    def successors(self, node_id: str, *, type: str | None = None) -> tuple[str, ...]:
        """Distinct target nodes reachable from ``node_id`` via one edge."""
        seen: dict[str, None] = {}
        for edge in self.edges_from(node_id, type=type):
            seen.setdefault(edge.target, None)
        return tuple(seen)

    def predecessors(self, node_id: str, *, type: str | None = None) -> tuple[str, ...]:
        """Distinct source nodes that reach ``node_id`` via one edge."""
        seen: dict[str, None] = {}
        for edge in self.edges_to(node_id, type=type):
            seen.setdefault(edge.source, None)
        return tuple(seen)

    def neighbors(self, node_id: str) -> tuple[str, ...]:
        """Distinct nodes adjacent to ``node_id`` in either direction, ordered."""
        seen: set[str] = set()
        seen.update(self.successors(node_id))
        seen.update(self.predecessors(node_id))
        return tuple(sorted(seen))

    def out_degree(self, node_id: str) -> int:
        return len(self._out.get(node_id, ()))

    def in_degree(self, node_id: str) -> int:
        return len(self._in.get(node_id, ()))

    def degree(self, node_id: str) -> int:
        """Total edges incident to ``node_id`` (out + in)."""
        return self.out_degree(node_id) + self.in_degree(node_id)

    def is_orphan(self, node_id: str) -> bool:
        """True iff ``node_id`` participates in no edge (UMB-006 §5 forbids these)."""
        return self.degree(node_id) == 0

    # -- projection support ----------------------------------------------------

    def subgraph(
        self,
        *,
        node_ids: Iterable[str] | None = None,
        edge_types: Iterable[str] | None = None,
        extra_nodes: Iterable[Node] = (),
        extra_edges: Iterable[Edge] = (),
        keep_isolated: bool = False,
        provenance: GraphProvenance | None = None,
    ) -> KnowledgeGraph:
        """Return a new :class:`KnowledgeGraph` induced by a filter.

        The subgraph reuses the *same* immutable node/edge objects (no copies of
        identity, so identifiers stay immutable and shared — never duplicated).

        Args:
            node_ids: if given, restrict to these nodes (and edges between them).
            edge_types: if given, keep only edges whose type is in this set.
            extra_nodes / extra_edges: synthetic projection nodes/edges to add.
            keep_isolated: keep nodes that end up with no incident edges.
        """
        type_filter = set(edge_types) if edge_types is not None else None
        id_filter = set(node_ids) if node_ids is not None else None

        kept_edges: list[Edge] = []
        for edge in self._edges.values():
            if type_filter is not None and edge.type not in type_filter:
                continue
            if id_filter is not None and (
                edge.source not in id_filter or edge.target not in id_filter
            ):
                continue
            kept_edges.append(edge)
        kept_edges.extend(extra_edges)

        candidate_ids: set[str]
        if id_filter is not None:
            candidate_ids = set(id_filter)
        else:
            candidate_ids = set(self._nodes)
        kept_nodes: list[Node] = [self._nodes[nid] for nid in candidate_ids if nid in self._nodes]
        kept_nodes.extend(extra_nodes)

        graph = KnowledgeGraph(provenance=provenance or self._provenance)
        for node in kept_nodes:
            graph.add_node(node)
        for edge in kept_edges:
            # Endpoints not present as nodes are tolerated by add_edge (adjacency
            # only); but for a clean projection we ensure endpoints exist.
            if not graph.has_node(edge.source) and edge.source in self._nodes:
                graph.add_node(self._nodes[edge.source])
            if not graph.has_node(edge.target) and edge.target in self._nodes:
                graph.add_node(self._nodes[edge.target])
            graph.add_edge(edge)

        if not keep_isolated:
            incident = {e.source for e in graph.edges()} | {e.target for e in graph.edges()}
            pruned = KnowledgeGraph(provenance=graph.provenance)
            for node in graph.nodes():
                if node.node_id in incident:
                    pruned.add_node(node)
            for edge in graph.edges():
                pruned.add_edge(edge)
            return pruned
        return graph


__all__ = [
    "Node",
    "Edge",
    "GraphProvenance",
    "KnowledgeGraph",
    "KIND_ARTIFACT",
    "KIND_VOLUME",
    "KIND_CATEGORY",
    "KIND_PROGRAM",
    "KIND_SIGNAL",
    "KIND_CERT_DOMAIN",
]
