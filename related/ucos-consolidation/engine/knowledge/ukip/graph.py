"""UKIP Part 08 — the Knowledge Graph over the registry (EPIC-UKDA-003).

A navigable graph whose nodes are canonical knowledge records and whose edges are the
resolved, closed relationships from :mod:`engine.knowledge.ukip.relationships`.

**This is a projection, not a second graph engine.** The edge structure and every
traversal primitive are the UKDA Part 05 :class:`~engine.knowledge.graph.KnowledgeGraph`,
reused verbatim via :meth:`KnowledgeIntelligenceGraph.edges`. What is added here is
only what Part 05 cannot know because it predates providers:

    * node **attribution** — which providers supplied each record, so the graph can
      answer "what does this provider contribute?" and "what is single-sourced?";
    * node **classification** — kind/authority/lifecycle/universe/owner indexes, so a
      subgraph can be cut by classification;
    * **projections** (:data:`PROJECTIONS`) — named, derived views (dependency,
      structure, governance, supersession, conflict, provenance, corroboration) that
      are computed on demand and cite the relations they are built from, never stored;
    * **impact** and **blast radius** over the registry, expressed in canonical
      knowledge identifiers.

Nothing here duplicates the knowledge itself: a node holds an identifier and derived
labels, and the content stays in the registry record (UKIP-LAW-008).
"""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
from typing import Any

from engine.knowledge.graph import KnowledgeEdge, KnowledgeGraph
from engine.knowledge.model import (
    KnowledgeAuthority,
    KnowledgeKind,
    Lifecycle,
    RelationType,
    content_hash,
)
from engine.knowledge.ukip.registry import KnowledgeRegistry, RegisteredKnowledge
from engine.knowledge.ukip.relationships import (
    ACYCLIC_FAMILIES,
    RelationshipSet,
    build_relationships,
)

#: The named derived views, each a set of relation types to keep. Declared as data so
#: adding a projection is one entry, not a new class.
PROJECTIONS: dict[str, frozenset[RelationType]] = {
    "dependency": ACYCLIC_FAMILIES["dependency"],
    "structure": ACYCLIC_FAMILIES["structure"],
    "supersession": ACYCLIC_FAMILIES["supersession"],
    "derivation": ACYCLIC_FAMILIES["derivation"],
    "governance": frozenset(
        {
            RelationType.GOVERNS,
            RelationType.OWNS,
            RelationType.CERTIFIES,
            RelationType.VALIDATES,
        }
    ),
    "implementation": frozenset({RelationType.IMPLEMENTS, RelationType.PRODUCES}),
    "conflict": frozenset({RelationType.CONFLICTS_WITH}),
    "equivalence": frozenset({RelationType.EQUIVALENT_TO}),
    "reference": frozenset({RelationType.REFERENCES, RelationType.RELATED_TO}),
}

#: Projection names in stable order.
PROJECTION_NAMES: tuple[str, ...] = tuple(sorted(PROJECTIONS))


@dataclass(frozen=True, slots=True)
class KnowledgeNode:
    """A graph node: an identifier plus derived labels. Never a copy of the content."""

    knowledge_id: str
    title: str
    kind: KnowledgeKind
    authority: KnowledgeAuthority
    lifecycle: Lifecycle
    universe: str
    owner: str
    provider_ids: tuple[str, ...]
    degree: int = 0

    @property
    def is_single_sourced(self) -> bool:
        return len(self.provider_ids) == 1

    def to_dict(self) -> dict[str, Any]:
        return {
            "knowledge_id": self.knowledge_id,
            "title": self.title,
            "kind": self.kind.value,
            "authority": self.authority.value,
            "lifecycle": self.lifecycle.value,
            "universe": self.universe,
            "owner": self.owner,
            "provider_ids": list(self.provider_ids),
            "degree": self.degree,
            "single_sourced": self.is_single_sourced,
        }


class KnowledgeIntelligenceGraph:
    """The registry projected as a navigable, attributed knowledge graph."""

    __slots__ = ("_registry", "_relationships", "_edges", "_nodes")

    def __init__(
        self, registry: KnowledgeRegistry, relationships: RelationshipSet | None = None
    ) -> None:
        self._registry = registry
        self._relationships = (
            relationships if relationships is not None else build_relationships(registry)
        )
        self._edges = KnowledgeGraph(
            KnowledgeEdge(r.source, r.target, r.relation, r.note) for r in self._relationships
        )
        nodes: dict[str, KnowledgeNode] = {}
        for record in registry.records():
            nodes[record.knowledge_id] = KnowledgeNode(
                knowledge_id=record.knowledge_id,
                title=record.title,
                kind=record.kind,
                authority=record.authority,
                lifecycle=record.lifecycle,
                universe=record.universe,
                owner=record.owner,
                provider_ids=record.provider_ids,
                degree=self._relationships.degree(record.knowledge_id),
            )
        self._nodes = nodes

    # -- construction ----------------------------------------------------------

    @classmethod
    def from_registry(
        cls, registry: KnowledgeRegistry, *, compose: bool = False, max_depth: int = 3
    ) -> KnowledgeIntelligenceGraph:
        """Build the graph, optionally including composed (derived) relationships."""
        relationships = build_relationships(registry)
        if compose:
            relationships = relationships.compose(max_depth=max_depth)
        return cls(registry, relationships)

    # -- structure -------------------------------------------------------------

    @property
    def registry(self) -> KnowledgeRegistry:
        return self._registry

    @property
    def relationships(self) -> RelationshipSet:
        return self._relationships

    def edges(self) -> KnowledgeGraph:
        """The UKDA Part 05 graph carrying every traversal primitive (reused as-is)."""
        return self._edges

    def __len__(self) -> int:
        return len(self._nodes)

    def nodes(self) -> tuple[KnowledgeNode, ...]:
        return tuple(self._nodes[k] for k in sorted(self._nodes))

    def node_ids(self) -> tuple[str, ...]:
        return tuple(sorted(self._nodes))

    def node(self, knowledge_id: str) -> KnowledgeNode | None:
        return self._nodes.get(knowledge_id)

    def record(self, knowledge_id: str) -> RegisteredKnowledge | None:
        """The full content, fetched from the registry rather than duplicated here."""
        return self._registry.get(knowledge_id)

    # -- attribution -----------------------------------------------------------

    def nodes_by_provider(self, provider_id: str) -> tuple[KnowledgeNode, ...]:
        return tuple(n for n in self.nodes() if provider_id in n.provider_ids)

    def provider_contribution(self) -> dict[str, int]:
        """How many records each provider supplied, canonically or as corroboration."""
        counts: dict[str, int] = {}
        for node in self.nodes():
            for provider_id in node.provider_ids:
                counts[provider_id] = counts.get(provider_id, 0) + 1
        return dict(sorted(counts.items()))

    def single_sourced(self) -> tuple[KnowledgeNode, ...]:
        """Records only one provider vouches for (a corroboration gap, not a defect)."""
        return tuple(n for n in self.nodes() if n.is_single_sourced)

    # -- classification cuts ---------------------------------------------------

    def nodes_by_kind(self, kind: KnowledgeKind) -> tuple[KnowledgeNode, ...]:
        return tuple(n for n in self.nodes() if n.kind is kind)

    def nodes_by_authority(self, authority: KnowledgeAuthority) -> tuple[KnowledgeNode, ...]:
        return tuple(n for n in self.nodes() if n.authority is authority)

    def nodes_by_universe(self, universe: str) -> tuple[KnowledgeNode, ...]:
        return tuple(n for n in self.nodes() if n.universe == universe)

    def isolated(self) -> tuple[str, ...]:
        """Records participating in no relationship at all."""
        return tuple(n.knowledge_id for n in self.nodes() if n.degree == 0)

    # -- navigation ------------------------------------------------------------

    def successors(self, knowledge_id: str, *, relation: RelationType | None = None):
        return self._edges.successors(knowledge_id, type=relation)

    def predecessors(self, knowledge_id: str, *, relation: RelationType | None = None):
        return self._edges.predecessors(knowledge_id, type=relation)

    def dependencies_of(self, knowledge_id: str) -> tuple[str, ...]:
        return self._edges.dependencies_of(knowledge_id)

    def dependents_of(self, knowledge_id: str) -> tuple[str, ...]:
        return self._edges.dependents_of(knowledge_id)

    def conflicts_of(self, knowledge_id: str) -> tuple[str, ...]:
        return self._edges.conflicts_of(knowledge_id)

    def impact_of(self, knowledge_id: str) -> tuple[str, ...]:
        """Everything affected if this knowledge changes (UKDA Part 05 semantics)."""
        return self._edges.impact_of(knowledge_id)

    def reachable_from(self, knowledge_id: str) -> tuple[str, ...]:
        return self._edges.reachable_from(knowledge_id)

    def blast_radius(self, knowledge_id: str) -> dict[str, Any]:
        """A composed impact summary: who breaks, and how authoritative they are."""
        affected = self.impact_of(knowledge_id)
        by_authority: dict[str, int] = {}
        for identifier in affected:
            node = self._nodes.get(identifier)
            if node is not None:
                key = node.authority.value
                by_authority[key] = by_authority.get(key, 0) + 1
        return {
            "knowledge_id": knowledge_id,
            "affected_count": len(affected),
            "affected": list(affected),
            "by_authority": dict(sorted(by_authority.items())),
        }

    # -- projections -----------------------------------------------------------

    def projection(self, name: str) -> tuple[Any, ...]:
        """A named derived view as relationships, computed on demand.

        Returns relationship values rather than a new graph object so a projection can
        never be mistaken for, or persisted as, a second source of truth.
        """
        types = PROJECTIONS.get(name)
        if types is None:
            raise KeyError(name)
        return tuple(r for r in self._relationships if r.relation in types)

    def projection_counts(self) -> dict[str, int]:
        return {name: len(self.projection(name)) for name in PROJECTION_NAMES}

    def subgraph(self, knowledge_ids: Iterable[str]) -> KnowledgeIntelligenceGraph:
        """A graph restricted to the given records and the relationships among them."""
        keep = set(knowledge_ids)
        kept = [r for r in self._registry.records() if r.knowledge_id in keep]
        restricted = KnowledgeRegistry(kept)
        relationships = RelationshipSet(
            (r for r in self._relationships if r.source in keep and r.target in keep),
            self._relationships.dangling(),
        )
        return KnowledgeIntelligenceGraph(restricted, relationships)

    # -- integrity / serialization ---------------------------------------------

    def unresolved(self) -> tuple[str, ...]:
        """Edge endpoints with no registry record — must be empty for a valid graph."""
        known = set(self._nodes)
        missing: set[str] = set()
        for edge in self._edges:
            if edge.source not in known:
                missing.add(edge.source)
            if edge.target not in known:
                missing.add(edge.target)
        return tuple(sorted(missing))

    def counts(self) -> dict[str, int]:
        return {
            "nodes": len(self._nodes),
            "edges": len(self._edges),
            "isolated": len(self.isolated()),
            "single_sourced": len(self.single_sourced()),
            "unresolved": len(self.unresolved()),
        }

    def seal(self) -> str:
        return content_hash(
            {
                "nodes": [n.knowledge_id for n in self.nodes()],
                "edges": [list(e.key()) for e in self._edges],
            }
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "counts": self.counts(),
            "seal": self.seal(),
            "provider_contribution": self.provider_contribution(),
            "projections": self.projection_counts(),
            "nodes": [n.to_dict() for n in self.nodes()],
            "edges": [e.to_dict() for e in self._edges],
            "unresolved": list(self.unresolved()),
        }


def build_graph(
    registry: KnowledgeRegistry, *, compose: bool = False
) -> KnowledgeIntelligenceGraph:
    """Convenience constructor mirroring the other UKIP layers."""
    return KnowledgeIntelligenceGraph.from_registry(registry, compose=compose)


__all__ = [
    "PROJECTIONS",
    "PROJECTION_NAMES",
    "KnowledgeNode",
    "KnowledgeIntelligenceGraph",
    "build_graph",
]
