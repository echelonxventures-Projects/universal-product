"""UCXI-000001 Part 09 — Context Graph: every context and every relation between them.

The context graph is the navigable form of the registry. It answers the structural
questions resolution and composition cannot: *what contains this context? what depends
on it? what breaks if it changes? is anything unclassified or orphaned?*

The graph is **projected, not stored**: it is built from the registry (contexts,
relations) and the taxonomy (classification), so it can never disagree with them. It
reuses the certified graph substrate — :class:`engine.graph.model.KnowledgeGraph` with
its immutable :class:`~engine.graph.model.Node` / :class:`~engine.graph.model.Edge`
value objects and duplicate refusal — rather than introducing a second graph
implementation, and reuses :func:`engine.compiler.cycles.detect_cycle` /
:func:`~engine.compiler.cycles.topological_order` for hierarchy checks and ordering.

Two node kinds appear: ``Context`` (a registered context) and ``ContextTaxon`` (its
classification). Every context carries exactly one ``classified-as`` edge to its taxon,
which is what makes "nothing is unclassified" a graph-checkable property rather than a
promise.
"""

from __future__ import annotations

from typing import Any

from engine.compiler.cycles import detect_cycle, topological_order
from engine.context.errors import ContextGraphError
from engine.context.model import content_digest, seal
from engine.context.registry import ContextRegistry
from engine.context.taxonomy import ContextRelation
from engine.graph.model import Edge, KnowledgeGraph, Node

#: The node kinds present in a context graph.
NODE_CONTEXT = "Context"
NODE_TAXON = "ContextTaxon"

#: The synthetic edge type binding a taxon to its parent taxon.
TAXON_PARENT = "taxon-parent"


def _taxon_node(taxonomy_entry: Any) -> Node:
    return Node(
        node_id=taxonomy_entry.taxon_id,
        kind=NODE_TAXON,
        label=taxonomy_entry.title,
        attributes={
            "context_kind": taxonomy_entry.kind,
            "universal": taxonomy_entry.universal,
            "parent": taxonomy_entry.parent or "",
        },
    )


def _context_node(record: Any) -> Node:
    return Node(
        node_id=record.context_id,
        kind=NODE_CONTEXT,
        label=f"{record.kind}:{record.natural_key}",
        version=record.content_hash[:12],
        attributes={
            "context_kind": record.kind,
            "namespace": record.namespace,
            "natural_key": record.natural_key,
            "boundary": record.boundary,
            "authority": record.authority.value,
            "lifecycle": record.lifecycle.value,
            "universal": record.universal,
            "taxon_id": record.taxon_id,
            "dimensions": list(record.dimensions()),
        },
    )


class ContextGraph:
    """A read-only projection of the registry and taxonomy as a navigable graph."""

    __slots__ = ("_graph", "_registry")

    def __init__(self, graph: KnowledgeGraph, registry: ContextRegistry) -> None:
        self._graph = graph
        self._registry = registry

    # -- substrate ---------------------------------------------------------- #

    @property
    def graph(self) -> KnowledgeGraph:
        """The underlying, immutable graph substrate."""
        return self._graph

    def order(self) -> int:
        """Number of nodes."""
        return self._graph.order()

    def size(self) -> int:
        """Number of edges."""
        return self._graph.size()

    def contexts(self) -> tuple[str, ...]:
        """Every context node id, ordered."""
        return tuple(node.node_id for node in self._graph.nodes_of_kind(NODE_CONTEXT))

    def taxa(self) -> tuple[str, ...]:
        """Every taxon node id, ordered."""
        return tuple(node.node_id for node in self._graph.nodes_of_kind(NODE_TAXON))

    def node(self, node_id: str) -> Node:
        """Return one node or raise the graph's not-found error."""
        return self._graph.node(node_id)

    # -- navigation --------------------------------------------------------- #

    def taxon_of(self, context_id: str) -> str | None:
        """The taxon a context is classified as, or ``None`` if unclassified."""
        targets = self._graph.successors(context_id, type=ContextRelation.CLASSIFIED_AS.value)
        return targets[0] if targets else None

    def contained_by(self, context_id: str) -> tuple[str, ...]:
        """The contexts that directly contain ``context_id``."""
        return self._graph.predecessors(context_id, type=ContextRelation.CONTAINS.value)

    def contains(self, context_id: str) -> tuple[str, ...]:
        """The contexts ``context_id`` directly contains."""
        return self._graph.successors(context_id, type=ContextRelation.CONTAINS.value)

    def dependencies_of(self, context_id: str) -> tuple[str, ...]:
        """Direct dependencies (``depends-on``, ``derives-from``, ``refines``)."""
        found: set[str] = set()
        for relation in _DEPENDENCY_TYPES:
            found.update(self._graph.successors(context_id, type=relation))
        return tuple(sorted(found))

    def dependents_of(self, context_id: str) -> tuple[str, ...]:
        """Contexts that depend directly on ``context_id``."""
        found: set[str] = set()
        for relation in _DEPENDENCY_TYPES:
            found.update(self._graph.predecessors(context_id, type=relation))
        return tuple(sorted(found))

    def transitive_dependencies(self, context_id: str) -> tuple[str, ...]:
        """Every context reachable through dependency edges, ordered."""
        return self._reach(context_id, self.dependencies_of)

    def impact_of(self, context_id: str) -> tuple[str, ...]:
        """Every context transitively affected if ``context_id`` changes."""
        return self._reach(context_id, self.dependents_of)

    def blast_radius(self, context_id: str) -> int:
        """The number of contexts a change to ``context_id`` would reach."""
        return len(self.impact_of(context_id))

    def _reach(self, start: str, step: Any) -> tuple[str, ...]:
        seen: set[str] = set()
        frontier = list(step(start))
        while frontier:
            current = frontier.pop(0)
            if current in seen or current == start:
                continue
            seen.add(current)
            frontier.extend(step(current))
        return tuple(sorted(seen))

    def constrained_by(self, context_id: str) -> tuple[str, ...]:
        """Contexts that constrain ``context_id`` (governance/security/regulatory)."""
        return self._graph.predecessors(context_id, type=ContextRelation.CONSTRAINS.value)

    def observed_by(self, context_id: str) -> tuple[str, ...]:
        """Observer contexts that observe ``context_id``."""
        return self._graph.predecessors(context_id, type=ContextRelation.OBSERVES.value)

    def federated_from(self, context_id: str) -> tuple[str, ...]:
        """Cross-boundary targets ``context_id`` is authorised to reference."""
        return self._graph.successors(context_id, type=ContextRelation.FEDERATES.value)

    def superseded_by(self, context_id: str) -> tuple[str, ...]:
        """Contexts that supersede ``context_id``."""
        return self._graph.predecessors(context_id, type=ContextRelation.SUPERSEDES.value)

    def by_kind(self, context_kind: str) -> tuple[str, ...]:
        """Every context node of one context kind, ordered."""
        return tuple(
            node.node_id
            for node in self._graph.nodes_of_kind(NODE_CONTEXT)
            if node.attributes.get("context_kind") == context_kind
        )

    def path(self, source: str, target: str) -> tuple[str, ...]:
        """A shortest path from ``source`` to ``target``, or ``()`` if none exists."""
        if not self._graph.has_node(source) or not self._graph.has_node(target):
            return ()
        queue: list[tuple[str, tuple[str, ...]]] = [(source, (source,))]
        seen = {source}
        while queue:
            current, trail = queue.pop(0)
            if current == target:
                return trail
            for successor in sorted(self._graph.successors(current)):
                if successor in seen:
                    continue
                seen.add(successor)
                queue.append((successor, trail + (successor,)))
        return ()

    def order_of_resolution(self) -> tuple[str, ...]:
        """A deterministic dependency-first order over the context nodes."""
        edges = {cid: self.dependencies_of(cid) for cid in self.contexts()}
        return topological_order(edges)

    # -- integrity ---------------------------------------------------------- #

    def cycles(self) -> dict[str, list[str]]:
        """Any cycle found in each hierarchical relation, keyed by relation."""
        found: dict[str, list[str]] = {}
        for relation in ContextRelation:
            if not relation.is_hierarchical:
                continue
            adjacency: dict[str, tuple[str, ...]] = {}
            for node_id in self._graph.node_ids():
                adjacency[node_id] = self._graph.successors(node_id, type=relation.value)
            cycle = detect_cycle(adjacency)
            if cycle is not None:
                found[relation.value] = list(cycle)
        return found

    def unclassified(self) -> tuple[str, ...]:
        """Contexts with no ``classified-as`` edge (must always be empty)."""
        return tuple(cid for cid in self.contexts() if self.taxon_of(cid) is None)

    def orphans(self) -> tuple[str, ...]:
        """Nodes participating in no edge at all."""
        return tuple(nid for nid in self._graph.node_ids() if self._graph.is_orphan(nid))

    def dangling(self) -> tuple[str, ...]:
        """Edges whose endpoints are not both present as nodes."""
        return tuple(
            sorted(
                edge.edge_id
                for edge in self._graph.edges()
                if not self._graph.has_node(edge.source) or not self._graph.has_node(edge.target)
            )
        )

    def validate(self) -> list[str]:
        """Return findings for the graph's structural invariants (empty means valid)."""
        findings: list[str] = []
        for relation, cycle in sorted(self.cycles().items()):
            findings.append(f"relation {relation!r} contains a cycle: {' -> '.join(cycle)}")
        for context_id in self.unclassified():
            findings.append(f"context {context_id} is unclassified (no taxon)")
        for edge_id in self.dangling():
            findings.append(f"edge {edge_id} has an endpoint outside the graph")
        return findings

    def require_valid(self) -> None:
        """Fail-closed form of :meth:`validate`."""
        findings = self.validate()
        if findings:
            raise ContextGraphError(
                "the context graph is not structurally valid", findings=findings
            )

    # -- serialisation ------------------------------------------------------ #

    def seal(self) -> str:
        """The digest of the whole projected graph."""
        return seal(self.to_dict())

    def summary(self) -> dict[str, Any]:
        return {
            "nodes": self.order(),
            "edges": self.size(),
            "contexts": len(self.contexts()),
            "taxa": len(self.taxa()),
            "edge_types": list(self._graph.edge_types()),
            "unclassified": list(self.unclassified()),
            "orphans": list(self.orphans()),
            "cycles": {k: v for k, v in sorted(self.cycles().items())},
            "valid": not self.validate(),
        }

    def to_dict(self) -> dict[str, Any]:
        return {
            "nodes": [node.to_dict() for node in self._graph.nodes()],
            "edges": [edge.to_dict() for edge in self._graph.edges()],
        }


_DEPENDENCY_TYPES: tuple[str, ...] = (
    ContextRelation.DEPENDS_ON.value,
    ContextRelation.DERIVES_FROM.value,
    ContextRelation.REFINES.value,
)


def build_context_graph(registry: ContextRegistry) -> ContextGraph:
    """Project ``registry`` (plus its taxonomy) into a :class:`ContextGraph`."""
    graph = KnowledgeGraph()

    for taxon in registry.taxonomy.taxa():
        graph.add_node(_taxon_node(taxon))
    for taxon in registry.taxonomy.taxa():
        if taxon.parent is None:
            continue
        graph.add_edge(
            Edge(
                edge_id="CTXT-" + content_digest([TAXON_PARENT, taxon.parent, taxon.taxon_id])[:12],
                source=taxon.parent,
                target=taxon.taxon_id,
                type=TAXON_PARENT,
                note="classification hierarchy",
            )
        )

    for record in registry.records():
        graph.add_node(_context_node(record))
        graph.add_edge(
            Edge(
                edge_id="CTXK-"
                + content_digest(
                    [ContextRelation.CLASSIFIED_AS.value, record.context_id, record.taxon_id]
                )[:12],
                source=record.context_id,
                target=record.taxon_id,
                type=ContextRelation.CLASSIFIED_AS.value,
                note="every context is classified by exactly one taxon",
            )
        )

    for edge in registry.relations():
        graph.add_edge(
            Edge(
                edge_id=edge.edge_id,
                source=edge.source,
                target=edge.target,
                type=edge.relation.value,
                note=edge.note,
            )
        )

    return ContextGraph(graph, registry)


__all__ = [
    "NODE_CONTEXT",
    "NODE_TAXON",
    "TAXON_PARENT",
    "ContextGraph",
    "build_context_graph",
]
