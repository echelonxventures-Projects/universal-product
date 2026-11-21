"""UCOS-EPIC-010 (Terminal T2) — Architecture Impact Engine & impact prediction.

Given a proposed **change set** (one or more artifacts a change will touch), the
engine predicts the architecture-wide consequence *before* the change is made:

    * the union blast radius across the whole change set (de-duplicated);
    * the impacted artifacts ranked by **propagation distance** (nearest first),
      so reviewers see the most-directly-affected artifacts first;
    * the set of architectural **layers** and **capabilities** the change reaches;
    * the **certified surface** the change disturbs (CERTIFIED / FROZEN / FINAL);
    * a bounded, deterministic **risk score** (0–100) and a severity band.

All analysis is read-only over the certified Universal Knowledge Graph (DP-03),
building on the EPIC-002 ``Affects`` impact closure. Output is deterministic.
"""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass
from typing import Any

from engine.graph.architecture.blast_radius import BlastRadiusEngine
from engine.graph.architecture.layers import LayerDependencyGraph
from engine.graph.engine import CONSUMES
from engine.graph.model import KnowledgeGraph
from engine.graph.projections import ImpactGraph

_CERTIFIED_STATUSES = frozenset({"CERTIFIED", "FROZEN", "FINAL"})


@dataclass(frozen=True, slots=True)
class ImpactPrediction:
    """The deterministic predicted consequence of changing a set of artifacts."""

    change_set: tuple[str, ...]
    known: tuple[str, ...]
    unknown: tuple[str, ...]
    impacted: tuple[str, ...]
    ranked: tuple[tuple[str, int], ...]
    layers: tuple[str, ...]
    capabilities_disrupted: tuple[str, ...]
    certified_impacted: tuple[str, ...]
    max_depth: int
    risk_score: int
    severity: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "change_set": list(self.change_set),
            "known": list(self.known),
            "unknown": list(self.unknown),
            "impacted": list(self.impacted),
            "ranked": [{"node": node, "distance": dist} for node, dist in self.ranked],
            "layers": list(self.layers),
            "capabilities_disrupted": list(self.capabilities_disrupted),
            "certified_impacted": list(self.certified_impacted),
            "max_depth": self.max_depth,
            "risk_score": self.risk_score,
            "severity": self.severity,
        }


class ArchitectureImpactEngine:
    """Read-only predictive impact analysis over the ``Affects`` closure."""

    __slots__ = ("_core", "_impact", "_layers", "_blast")

    def __init__(
        self,
        core: KnowledgeGraph,
        *,
        impact: ImpactGraph | None = None,
        layers: LayerDependencyGraph | None = None,
    ) -> None:
        self._core = core
        self._impact = impact if impact is not None else ImpactGraph(core)
        self._layers = layers if layers is not None else LayerDependencyGraph(core)
        self._blast = BlastRadiusEngine(core, impact=self._impact, layers=self._layers)

    def _distances(self, sources: tuple[str, ...]) -> dict[str, int]:
        """Multi-source BFS distance over ``Affects`` from every source in ``sources``."""
        graph = self._impact.graph
        dist: dict[str, int] = {}
        queue: deque[str] = deque()
        for src in sources:
            if graph.has_node(src) and src not in dist:
                dist[src] = 0
                queue.append(src)
        while queue:
            current = queue.popleft()
            for nxt in graph.successors(current, type=ImpactGraph.EDGE_TYPE):
                if nxt not in dist:
                    dist[nxt] = dist[current] + 1
                    queue.append(nxt)
        return dist

    def _risk(
        self,
        impacted: tuple[str, ...],
        certified: tuple[str, ...],
        layers: tuple[str, ...],
        max_depth: int,
    ) -> int:
        """A bounded, deterministic 0–100 risk score.

        Combines reach (fraction of the impactable universe), certified-surface
        disturbance, layer spread, and propagation depth. Monotonic in each factor.
        """
        universe = max(self._impact.graph.order(), 1)
        reach = min(len(impacted) / universe, 1.0)
        cert = min(len(certified) / 10.0, 1.0)
        spread = min(len(layers) / len(_layer_universe(self._layers)), 1.0)
        depth = min(max_depth / 8.0, 1.0)
        score = 100.0 * (0.45 * reach + 0.30 * cert + 0.15 * spread + 0.10 * depth)
        return int(round(score))

    @staticmethod
    def _severity(score: int) -> str:
        if score >= 70:
            return "CRITICAL"
        if score >= 40:
            return "HIGH"
        if score >= 15:
            return "MEDIUM"
        if score > 0:
            return "LOW"
        return "NONE"

    def predict(self, change_set: object) -> ImpactPrediction:
        """Predict the consequence of changing every artifact in ``change_set``.

        ``change_set`` is any iterable of artifact ids. Ids absent from the graph are
        reported under ``unknown`` (not silently dropped), so callers can detect a
        stale or mistyped change set.
        """
        requested = tuple(sorted({str(x) for x in change_set}))  # type: ignore[union-attr]
        known = tuple(s for s in requested if self._core.has_node(s))
        unknown = tuple(s for s in requested if not self._core.has_node(s))

        dist = self._distances(known)
        # The change set members themselves are the "sources" (distance 0); the
        # impacted set is everything reachable *beyond* them.
        impacted = tuple(sorted(node for node, d in dist.items() if d > 0))
        ranked = tuple(
            sorted(
                ((node, dist[node]) for node in impacted),
                key=lambda item: (item[1], item[0]),
            )
        )
        max_depth = max((d for d in dist.values()), default=0)

        layer_counts: set[str] = set()
        certified: list[str] = []
        for node_id in impacted:
            layer = self._layers.layer_of(node_id)
            if layer:
                layer_counts.add(layer)
            node = self._core.find(node_id)
            if node is not None and str(node.attributes.get("status")) in _CERTIFIED_STATUSES:
                certified.append(node_id)

        capabilities = self._capabilities_disrupted(known)
        layers = tuple(sorted(layer_counts))
        certified_t = tuple(sorted(certified))
        score = self._risk(impacted, certified_t, layers, max_depth)
        return ImpactPrediction(
            change_set=requested,
            known=known,
            unknown=unknown,
            impacted=impacted,
            ranked=ranked,
            layers=layers,
            capabilities_disrupted=capabilities,
            certified_impacted=certified_t,
            max_depth=max_depth,
            risk_score=score,
            severity=self._severity(score),
        )

    def _capabilities_disrupted(self, sources: tuple[str, ...]) -> tuple[str, ...]:
        """Artifacts that consume a capability provided by any source (direct consumers)."""
        disrupted: set[str] = set()
        source_set = set(sources)
        for edge in self._core.edges_of_type(CONSUMES):
            if edge.target in source_set:
                disrupted.add(edge.source)
        return tuple(sorted(disrupted))

    def blast_radius(self, subject: str) -> dict[str, Any]:
        """Single-subject blast radius (delegates to the Blast Radius Engine)."""
        return self._blast.analyze(subject).to_dict()

    def summary(self, *, limit: int = 10) -> dict[str, Any]:
        return {
            "impactable_nodes": self._impact.graph.order(),
            "blast_radius": self._blast.summary(limit=limit),
        }


def _layer_universe(layers: LayerDependencyGraph) -> tuple[str, ...]:
    """The layers present (at least one), guaranteeing a non-empty denominator."""
    present = layers.layers()
    return present if present else ("unclassified",)


__all__ = ["ImpactPrediction", "ArchitectureImpactEngine"]
