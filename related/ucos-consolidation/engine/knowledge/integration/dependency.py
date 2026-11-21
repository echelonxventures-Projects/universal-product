"""UKI Deliverable 4 — Universal Dependency Graph Integration (EPIC-UKDA-002).

Automatically exposes, for any canonical artifact (or a not-yet-created intent), its
dependencies, impacts, consumers, providers, and local composition graph — all
projected from the single UKDA :class:`~engine.knowledge.graph.KnowledgeGraph`
(reused verbatim; no second relationship store).

    * :class:`DependencyView` — the immutable dependency projection for one node.
    * :class:`DependencyIntegration` — builds a view for a registered node, or for an
      :class:`~engine.knowledge.integration.contracts.ArtifactIntent` by projecting its
      candidate object into the graph so a proposed artifact's dependencies and
      providers are visible *before* it is created.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from engine.knowledge.graph import KnowledgeGraph
from engine.knowledge.integration.contracts import ArtifactIntent
from engine.knowledge.model import RelationType
from engine.knowledge.store import KnowledgeBase


@dataclass(frozen=True, slots=True)
class DependencyView:
    """The dependency/impact/consumer/provider projection of one node (Deliverable 4)."""

    node: str
    dependencies: tuple[str, ...]
    providers: tuple[str, ...]
    consumers: tuple[str, ...]
    dependents: tuple[str, ...]
    impact: tuple[str, ...]
    composition: tuple[dict[str, str], ...]

    def to_dict(self) -> dict[str, Any]:
        return {
            "node": self.node,
            "dependencies": list(self.dependencies),
            "providers": list(self.providers),
            "consumers": list(self.consumers),
            "dependents": list(self.dependents),
            "impact": list(self.impact),
            "composition": [dict(edge) for edge in self.composition],
        }


class DependencyIntegration:
    """Exposes the universal dependency graph for artifacts and intents (Deliverable 4)."""

    __slots__ = ("_base", "_graph")

    def __init__(self, base: KnowledgeBase) -> None:
        self._base = base
        self._graph = base.graph()

    @property
    def graph(self) -> KnowledgeGraph:
        return self._graph

    def _view(self, graph: KnowledgeGraph, node: str) -> DependencyView:
        composition = tuple(
            edge.to_dict()
            for edge in sorted(
                (*graph.edges_from(node), *graph.edges_to(node)),
                key=lambda e: e.key(),
            )
        )
        return DependencyView(
            node=node,
            dependencies=graph.dependencies_of(node),
            providers=graph.reachable_from(node),
            consumers=graph.predecessors(node, type=RelationType.CONSUMES),
            dependents=graph.dependents_of(node),
            impact=graph.impact_of(node),
            composition=composition,
        )

    def view(self, cko_id: str) -> DependencyView:
        """Return the dependency view of an existing canonical node."""
        return self._view(self._graph, cko_id)

    def view_intent(self, intent: ArtifactIntent) -> DependencyView:
        """Return the dependency view of a proposed intent, projected into the graph."""
        candidate = intent.to_cko()
        graph = KnowledgeGraph.from_objects((*self._base.objects(), candidate))
        return self._view(graph, intent.intent_id)


__all__ = ["DependencyView", "DependencyIntegration"]
