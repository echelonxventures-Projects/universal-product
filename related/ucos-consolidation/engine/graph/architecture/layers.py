"""UCOS-EPIC-010 (Terminal T2) — architectural layer model & layer dependency graph.

Classifies every artifact node of the Universal Knowledge Graph into exactly one
**architectural layer** (a deterministic function of the artifact's certified
``category`` / ``program`` attributes), then aggregates the artifact-level
``Depends-On`` relation up to the layer level to produce the **layer dependency
graph**: which layers depend on which, weighted by the number of underlying
artifact dependencies.

Because the layers form an intended acyclic *stack* (foundational layers at the
bottom, applied layers at the top), the layer dependency graph also surfaces two
classes of architectural finding, deterministically and read-only (DP-03):

    * **Layer inversions** — a more-foundational layer depending on a
      less-foundational one (a strictly upward edge in the stack).
    * **Layer cycles** — mutually-dependent layers (a cycle in the layer graph).

The category→layer mapping is heuristic but explicit and stable; unknown
categories fall through to :data:`UNCLASSIFIED` and are excluded from inversion
logic (they have no defined position in the stack).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from engine.graph.architecture.algorithms import cyclic_components, normalise_adjacency
from engine.graph.engine import DEPENDS_ON
from engine.graph.model import KIND_ARTIFACT, KnowledgeGraph

#: The intended architectural stack, most-foundational first. A layer's *depth* is
#: its index here; a healthy ``Depends-On`` edge points from a higher depth toward
#: an equal-or-lower depth (applied code depends on foundations, never the reverse).
LAYER_ORDER: tuple[str, ...] = (
    "book",
    "constitution",
    "governance",
    "architecture",
    "registry",
    "engineering",
    "implementation",
    "runtime",
    "platform",
    "data",
    "service",
    "application",
    "infrastructure",
    "security",
)

#: Fallback layer for categories with no defined position in the stack.
UNCLASSIFIED = "unclassified"

#: Deterministic category → layer mapping over the certified corpus vocabulary.
_CATEGORY_LAYER: dict[str, str] = {
    "BOOK": "book",
    "IDX": "book",
    "CON": "constitution",
    "GOV": "governance",
    "ADR": "governance",
    "DEC": "governance",
    "ARCH": "architecture",
    "UMB": "architecture",
    "MASTER": "architecture",
    "CEP": "architecture",
    "REG": "registry",
    "NOM": "registry",
    "ENG": "engineering",
    "IMP": "implementation",
    "SRC": "implementation",
    "GEN": "implementation",
    "RUN": "runtime",
    "PLAT": "platform",
    "PL": "platform",
    "DATA": "data",
    "DAT": "data",
    "SVC": "service",
    "APP": "application",
    "INF": "infrastructure",
    "SEC": "security",
}

_DEPTH_OF: dict[str, int] = {name: i for i, name in enumerate(LAYER_ORDER)}


def layer_of_category(category: str) -> str:
    """Return the architectural layer for a certified ``category`` (deterministic)."""
    return _CATEGORY_LAYER.get(category.upper(), UNCLASSIFIED)


def layer_depth(layer: str) -> int:
    """Return the stack depth of ``layer`` (``-1`` for :data:`UNCLASSIFIED`)."""
    return _DEPTH_OF.get(layer, -1)


@dataclass(frozen=True, slots=True)
class LayerDependency:
    """One directed layer→layer dependency, weighted by underlying artifact edges."""

    source: str
    target: str
    weight: int
    inversion: bool

    def to_dict(self) -> dict[str, Any]:
        return {
            "source": self.source,
            "target": self.target,
            "weight": self.weight,
            "inversion": self.inversion,
        }


class LayerDependencyGraph:
    """The layer-level dependency graph derived from the artifact ``Depends-On`` DAG.

    Read-only. Every artifact is classified to a layer; each ``Depends-On`` edge
    contributes one unit of weight to the corresponding layer→layer dependency.
    Self-dependencies (both endpoints in the same layer) are retained as weighted
    self-edges but are never inversions.
    """

    __slots__ = ("_layer_of", "_members", "_dependencies", "_edges")

    def __init__(self, core: KnowledgeGraph) -> None:
        layer_of: dict[str, str] = {}
        members: dict[str, list[str]] = {name: [] for name in LAYER_ORDER}
        members[UNCLASSIFIED] = []
        for node in core.nodes_of_kind(KIND_ARTIFACT):
            layer = layer_of_category(str(node.attributes.get("category") or ""))
            layer_of[node.node_id] = layer
            members[layer].append(node.node_id)

        weights: dict[tuple[str, str], int] = {}
        for edge in core.edges_of_type(DEPENDS_ON):
            src_layer = layer_of.get(edge.source)
            dst_layer = layer_of.get(edge.target)
            if src_layer is None or dst_layer is None:
                continue
            key = (src_layer, dst_layer)
            weights[key] = weights.get(key, 0) + 1

        dependencies: list[LayerDependency] = []
        for (src_layer, dst_layer), weight in weights.items():
            dependencies.append(
                LayerDependency(
                    source=src_layer,
                    target=dst_layer,
                    weight=weight,
                    inversion=self._is_inversion(src_layer, dst_layer),
                )
            )
        dependencies.sort(key=lambda d: (d.source, d.target))

        self._layer_of = layer_of
        self._members = {name: tuple(sorted(ids)) for name, ids in members.items()}
        self._dependencies = tuple(dependencies)
        self._edges = {(d.source, d.target): d for d in dependencies}

    @staticmethod
    def _is_inversion(src_layer: str, dst_layer: str) -> bool:
        """True iff ``src_layer`` -> ``dst_layer`` points strictly *up* the stack."""
        src_depth = layer_depth(src_layer)
        dst_depth = layer_depth(dst_layer)
        if src_depth < 0 or dst_depth < 0:
            return False  # unclassified layers have no stack position
        return src_depth < dst_depth

    # -- queries ---------------------------------------------------------------

    def layer_of(self, node_id: str) -> str:
        """Return the layer of an artifact node (``''`` if not an artifact)."""
        return self._layer_of.get(node_id, "")

    def layers(self) -> tuple[str, ...]:
        """Every layer that has at least one member artifact, in stack order."""
        ordered = [name for name in LAYER_ORDER if self._members.get(name)]
        if self._members.get(UNCLASSIFIED):
            ordered.append(UNCLASSIFIED)
        return tuple(ordered)

    def members(self, layer: str) -> tuple[str, ...]:
        """The artifact ids classified into ``layer`` (sorted)."""
        return self._members.get(layer, ())

    def dependencies(self) -> tuple[LayerDependency, ...]:
        """Every layer→layer dependency, ordered by (source, target)."""
        return self._dependencies

    def dependencies_of(self, layer: str) -> tuple[LayerDependency, ...]:
        """Outbound layer dependencies from ``layer``."""
        return tuple(d for d in self._dependencies if d.source == layer)

    def inversions(self) -> tuple[LayerDependency, ...]:
        """Layer dependencies that point strictly up the stack (architectural smells)."""
        return tuple(d for d in self._dependencies if d.inversion)

    def cycles(self) -> tuple[tuple[str, ...], ...]:
        """Every circular set of mutually-dependent layers (deterministic)."""
        adjacency = normalise_adjacency(
            self.layers(),
            ((d.source, d.target) for d in self._dependencies),
        )
        return cyclic_components(adjacency)

    def is_stratified(self) -> bool:
        """True iff the layering is clean: no inversions and no layer cycles."""
        return not self.inversions() and not self.cycles()

    def summary(self) -> dict[str, Any]:
        """A deterministic, loggable summary of the layer dependency graph."""
        return {
            "layers": [
                {"layer": name, "depth": layer_depth(name), "members": len(self.members(name))}
                for name in self.layers()
            ],
            "dependencies": [d.to_dict() for d in self._dependencies],
            "inversions": [d.to_dict() for d in self.inversions()],
            "cycles": [list(c) for c in self.cycles()],
            "is_stratified": self.is_stratified(),
        }


__all__ = [
    "LAYER_ORDER",
    "UNCLASSIFIED",
    "layer_of_category",
    "layer_depth",
    "LayerDependency",
    "LayerDependencyGraph",
]
