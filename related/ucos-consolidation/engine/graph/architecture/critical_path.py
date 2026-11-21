"""UCOS-EPIC-010 (Terminal T2) — Critical Path Engine.

Computes the **critical path** of the architecture: the longest chain of
``Depends-On`` dependencies in the certified Universal Knowledge Graph. The length
of this chain is the *dependency depth* of the system — the minimum number of
sequential layers any full rebuild/verification must traverse — and the artifacts
on it are the ones whose change most lengthens the critical path.

Registry Truth may contain a genuine ``Depends-On`` cycle (UMB-007 §5), which
would make "longest path" ill-defined on the raw graph. The engine therefore
computes over the **acyclic condensation** (each strongly-connected component
collapsed to one super-node) so the analysis is always well-defined and
deterministic, then expands the resulting super-path back into concrete artifact
ids. A component's weight is its member count, so a cyclic cluster contributes its
true size to the path length.

Read-only over Registry Truth (DP-03); deterministic (sorted tie-breaks).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from engine.graph.architecture.algorithms import (
    condensation,
    longest_paths,
    normalise_adjacency,
    reconstruct_path,
)
from engine.graph.engine import DEPENDS_ON
from engine.graph.model import KIND_ARTIFACT, KnowledgeGraph


@dataclass(frozen=True, slots=True)
class CriticalPathReport:
    """The deterministic critical-path assessment of the dependency graph."""

    length: int
    path: tuple[str, ...]
    depth_of: tuple[tuple[str, int], ...]
    cyclic: bool

    def to_dict(self) -> dict[str, Any]:
        return {
            "length": self.length,
            "path": list(self.path),
            "cyclic": self.cyclic,
            "depth_of": [{"node": node, "depth": depth} for node, depth in self.depth_of],
        }


class CriticalPathEngine:
    """Read-only critical-path (longest dependency chain) analysis."""

    __slots__ = ("_adjacency", "_dag", "_member_of", "_members", "_dist", "_nxt")

    def __init__(self, core: KnowledgeGraph) -> None:
        artifacts = {n.node_id for n in core.nodes_of_kind(KIND_ARTIFACT)}
        pairs = [
            (e.source, e.target)
            for e in core.edges_of_type(DEPENDS_ON)
            if e.source in artifacts and e.target in artifacts
        ]
        self._adjacency = normalise_adjacency(artifacts, pairs)
        # Collapse cycles so longest-path is well-defined; weight = component size.
        self._dag, self._member_of, self._members = condensation(self._adjacency)
        weights = {cid: len(members) for cid, members in self._members.items()}
        self._dist, self._nxt = longest_paths(self._dag, weights=weights)

    @property
    def is_cyclic(self) -> bool:
        """True iff any strongly-connected component holds more than one artifact."""
        return any(len(members) > 1 for members in self._members.values())

    def depth_of(self, node_id: str) -> int:
        """The length (in artifacts) of the longest dependency chain starting at ``node_id``."""
        comp = self._member_of.get(node_id)
        if comp is None:
            return 0
        return self._dist.get(comp, 0)

    def critical_path(self) -> CriticalPathReport:
        """Return the single longest dependency chain in the graph (deterministic).

        Ties (equal-length paths) break on the smallest component root id, so the
        returned path is reproducible.
        """
        if not self._dag:
            return CriticalPathReport(length=0, path=(), depth_of=(), cyclic=False)

        start = min(self._dag, key=lambda cid: (-self._dist[cid], cid))
        comp_path = reconstruct_path(self._nxt, start)

        path: list[str] = []
        for comp_id in comp_path:
            path.extend(self._members[comp_id])  # already sorted within component

        depth_of = tuple(
            sorted(
                ((node, self.depth_of(node)) for node in self._member_of),
                key=lambda item: (-item[1], item[0]),
            )
        )
        return CriticalPathReport(
            length=len(path),
            path=tuple(path),
            depth_of=depth_of,
            cyclic=self.is_cyclic,
        )

    def deepest(self, *, limit: int = 10) -> tuple[tuple[str, int], ...]:
        """The ``limit`` artifacts with the greatest dependency depth (ranked)."""
        scored = [(node, self.depth_of(node)) for node in self._member_of]
        scored.sort(key=lambda item: (-item[1], item[0]))
        return tuple(scored[:limit])

    def summary(self, *, limit: int = 10) -> dict[str, Any]:
        report = self.critical_path()
        return {
            "length": report.length,
            "cyclic": report.cyclic,
            "path": list(report.path),
            "deepest": [{"node": n, "depth": d} for n, d in self.deepest(limit=limit)],
        }


__all__ = ["CriticalPathReport", "CriticalPathEngine"]
