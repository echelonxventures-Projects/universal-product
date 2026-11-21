"""UCOS-EPIC-010 (Terminal T2) — Blast Radius Engine.

Answers *"if this artifact changes, what is the total downstream damage surface?"*
over the certified Universal Knowledge Graph (read-only, DP-03).

The engine builds on the certified EPIC-002 :class:`~engine.graph.projections.ImpactGraph`
— the normalised ``Affects`` closure (``A Affects B`` iff a change to ``A`` propagates
to ``B``) — and enriches a raw blast-radius count with:

    * **propagation depth** — the maximum number of ``Affects`` hops from the
      subject to any impacted node (how *far* a change ripples);
    * **per-layer breakdown** — how many impacted artifacts fall in each
      architectural layer (via :class:`~engine.graph.architecture.layers.LayerDependencyGraph`);
    * **certified-surface impact** — which impacted artifacts are in a certified
      terminal state (CERTIFIED / FROZEN / FINAL), a governance-relevant risk; and
    * a deterministic **severity** classification.

Everything is deterministic (sorted) and derived read-only from Registry Truth.
"""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass
from typing import Any

from engine.graph.architecture.layers import LayerDependencyGraph
from engine.graph.model import KIND_ARTIFACT, KnowledgeGraph
from engine.graph.projections import ImpactGraph

#: Certified terminal lifecycle states (a change here is governance-sensitive).
_CERTIFIED_STATUSES = frozenset({"CERTIFIED", "FROZEN", "FINAL"})

#: Deterministic severity thresholds, expressed as a fraction of all impactable
#: nodes. Ordered high→low; the first threshold the ratio meets wins.
_SEVERITY_THRESHOLDS: tuple[tuple[float, str], ...] = (
    (0.25, "CRITICAL"),
    (0.10, "HIGH"),
    (0.02, "MEDIUM"),
)


@dataclass(frozen=True, slots=True)
class BlastRadiusReport:
    """The deterministic blast-radius assessment for a single subject artifact."""

    subject: str
    radius: int
    max_depth: int
    direct: tuple[str, ...]
    impacted: tuple[str, ...]
    per_layer: tuple[tuple[str, int], ...]
    certified_impacted: tuple[str, ...]
    severity: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "subject": self.subject,
            "radius": self.radius,
            "max_depth": self.max_depth,
            "severity": self.severity,
            "direct": list(self.direct),
            "impacted": list(self.impacted),
            "per_layer": [{"layer": name, "count": count} for name, count in self.per_layer],
            "certified_impacted": list(self.certified_impacted),
        }


class BlastRadiusEngine:
    """Read-only blast-radius analysis over the ``Affects`` impact closure."""

    __slots__ = ("_core", "_impact", "_layers", "_total_impactable")

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
        # The universe a change *could* reach: nodes participating in the impact graph.
        self._total_impactable = max(self._impact.graph.order(), 1)

    @property
    def impactable_nodes(self) -> int:
        """The number of nodes that participate in the ``Affects`` impact closure."""
        return self._impact.graph.order()

    def _depth(self, subject: str) -> int:
        """Maximum ``Affects``-hop distance from ``subject`` (0 if isolated)."""
        graph = self._impact.graph
        if not graph.has_node(subject):
            return 0
        depth: dict[str, int] = {subject: 0}
        queue: deque[str] = deque([subject])
        best = 0
        while queue:
            current = queue.popleft()
            for nxt in graph.successors(current, type=ImpactGraph.EDGE_TYPE):
                if nxt not in depth:
                    depth[nxt] = depth[current] + 1
                    best = max(best, depth[nxt])
                    queue.append(nxt)
        return best

    def _classify(self, radius: int) -> str:
        if radius == 0:
            return "NONE"
        ratio = radius / self._total_impactable
        for threshold, label in _SEVERITY_THRESHOLDS:
            if ratio >= threshold:
                return label
        return "LOW"

    def analyze(self, subject: str) -> BlastRadiusReport:
        """Return the full blast-radius report for ``subject`` (deterministic)."""
        impacted = self._impact.impact_of(subject)
        direct = (
            self._impact.graph.successors(subject, type=ImpactGraph.EDGE_TYPE)
            if self._impact.graph.has_node(subject)
            else ()
        )

        per_layer_counts: dict[str, int] = {}
        certified: list[str] = []
        for node_id in impacted:
            layer = self._layers.layer_of(node_id) or "unclassified"
            per_layer_counts[layer] = per_layer_counts.get(layer, 0) + 1
            node = self._core.find(node_id)
            if node is not None and str(node.attributes.get("status")) in _CERTIFIED_STATUSES:
                certified.append(node_id)

        per_layer = tuple(sorted(per_layer_counts.items(), key=lambda item: (-item[1], item[0])))
        radius = len(impacted)
        return BlastRadiusReport(
            subject=subject,
            radius=radius,
            max_depth=self._depth(subject),
            direct=tuple(sorted(direct)),
            impacted=impacted,
            per_layer=per_layer,
            certified_impacted=tuple(sorted(certified)),
            severity=self._classify(radius),
        )

    def top(self, *, limit: int = 10) -> tuple[BlastRadiusReport, ...]:
        """The ``limit`` artifacts with the largest blast radius, ranked deterministically.

        Ties break on the smaller subject id, so the ranking is reproducible.
        """
        subjects = [
            n.node_id
            for n in self._core.nodes_of_kind(KIND_ARTIFACT)
            if self._impact.graph.has_node(n.node_id)
        ]
        reports = [self.analyze(s) for s in subjects]
        reports.sort(key=lambda r: (-r.radius, r.subject))
        return tuple(reports[:limit])

    def summary(self, *, limit: int = 10) -> dict[str, Any]:
        top = self.top(limit=limit)
        return {
            "impactable_nodes": self._impact.graph.order(),
            "top": [
                {"subject": r.subject, "radius": r.radius, "severity": r.severity} for r in top
            ],
        }


__all__ = ["BlastRadiusReport", "BlastRadiusEngine"]
