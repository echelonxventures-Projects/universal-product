"""ZG-P-02 — Coverage graph model (Universe→Code Coverage Instrument).

A deterministic directed acyclic graph over the coverage spine
(Universe→Phase→Program→Implementation→Epic→Module→Code Asset→Runtime Asset),
reconstructed from an :class:`~platform.coverage.evidence.EvidenceBundle`. The graph
computes, for every node, a fail-closed :class:`~platform.coverage.contracts.CoverageStatus`:

    * ``COVERED``   — a downstream path reaches runtime evidence and no child is a gap.
    * ``PARTIAL``   — some downstream children are covered, some are gaps.
    * ``UNCOVERED`` — no downstream runtime evidence (a well-formed coverage gap).
    * ``ORPHANED``  — structural defect: a non-universe node with no lineage to a universe,
      or a universe with no downstream edge.

The graph is a pure function of the bundle: identical evidence yields a byte-identical
:meth:`fingerprint`. Construction is fail-closed — a dangling edge endpoint or an illegal
(non-adjacent) edge raises :class:`~platform.coverage.errors.CoverageGraphError`.
"""

from __future__ import annotations

from platform.coverage.contracts import (
    ROOT_KIND,
    TERMINAL_KIND,
    CoverageEdge,
    CoverageNode,
    CoverageNodeKind,
    CoverageStatus,
)
from platform.coverage.errors import CoverageGraphError
from platform.coverage.evidence import EvidenceBundle
from platform.foundation.contracts import content_hash
from typing import Any


class CoverageGraph:
    """A deterministic, fail-closed coverage graph reconstructed from evidence."""

    __slots__ = (
        "_nodes",
        "_edges",
        "_children",
        "_parents",
        "_status",
    )

    def __init__(self, bundle: EvidenceBundle) -> None:
        if not isinstance(bundle, EvidenceBundle):
            raise CoverageGraphError("a CoverageGraph requires an EvidenceBundle")
        self._nodes: dict[str, CoverageNode] = {n.node_id: n for n in bundle.nodes}
        self._edges: tuple[CoverageEdge, ...] = bundle.edges
        self._children: dict[str, set[str]] = {nid: set() for nid in self._nodes}
        self._parents: dict[str, set[str]] = {nid: set() for nid in self._nodes}
        self._index_edges()
        self._status: dict[str, CoverageStatus] = {}
        self._compute_status()

    # -- construction -----------------------------------------------------------

    def _index_edges(self) -> None:
        for edge in self._edges:
            src = edge.source_node_id()
            tgt = edge.target_node_id()
            if src not in self._nodes:
                raise CoverageGraphError(
                    "coverage edge references an undeclared source node",
                    edge_id=edge.edge_id,
                    source_ref=edge.source_ref,
                )
            if tgt not in self._nodes:
                raise CoverageGraphError(
                    "coverage edge references an undeclared target node",
                    edge_id=edge.edge_id,
                    target_ref=edge.target_ref,
                )
            self._children[src].add(tgt)
            self._parents[tgt].add(src)

    def _compute_status(self) -> None:
        # The spine adjacency rule (an edge always descends exactly one tier) guarantees
        # the graph is acyclic by construction, so memoized recursion is sufficient and
        # no cycle guard is required. Downward coverage (memoized DFS).
        covered_cache: dict[str, CoverageStatus] = {}

        def down(nid: str) -> CoverageStatus:
            if nid in covered_cache:
                return covered_cache[nid]
            node = self._nodes[nid]
            if node.kind is TERMINAL_KIND:
                covered_cache[nid] = CoverageStatus.COVERED
                return CoverageStatus.COVERED
            children = self._children[nid]
            if not children:
                covered_cache[nid] = CoverageStatus.UNCOVERED
                return CoverageStatus.UNCOVERED
            child_status = [down(c) for c in sorted(children)]
            covered = any(s is CoverageStatus.COVERED for s in child_status)
            gapped = any(
                s in (CoverageStatus.UNCOVERED, CoverageStatus.PARTIAL) for s in child_status
            )
            if covered and not gapped:
                result = CoverageStatus.COVERED
            elif covered and gapped:
                result = CoverageStatus.PARTIAL
            else:
                result = CoverageStatus.UNCOVERED
            covered_cache[nid] = result
            return result

        # Upward lineage to a universe (orphan detection), memoized.
        reaches_cache: dict[str, bool] = {}

        def reaches_universe(nid: str) -> bool:
            if nid in reaches_cache:
                return reaches_cache[nid]
            node = self._nodes[nid]
            if node.kind is ROOT_KIND:
                reaches_cache[nid] = True
                return True
            parents = self._parents[nid]
            # Provisionally mark False to break any (adjacency-prevented) revisit safely.
            reaches_cache[nid] = False
            result = any(reaches_universe(p) for p in sorted(parents))
            reaches_cache[nid] = result
            return result

        for nid, node in self._nodes.items():
            if node.kind is ROOT_KIND:
                # A universe with no downstream edge is a structural orphan.
                self._status[nid] = down(nid) if self._children[nid] else CoverageStatus.ORPHANED
            else:
                self._status[nid] = down(nid) if reaches_universe(nid) else CoverageStatus.ORPHANED

    # -- accessors --------------------------------------------------------------

    def __len__(self) -> int:
        return len(self._nodes)

    def __contains__(self, node_id: str) -> bool:
        return node_id in self._nodes

    @property
    def node_ids(self) -> tuple[str, ...]:
        return tuple(sorted(self._nodes))

    def nodes(self) -> tuple[CoverageNode, ...]:
        return tuple(self._nodes[nid] for nid in self.node_ids)

    def edges(self) -> tuple[CoverageEdge, ...]:
        return self._edges

    def get(self, node_id: str) -> CoverageNode:
        node = self._nodes.get(node_id)
        if node is None:
            raise CoverageGraphError("unknown coverage node", node_id=node_id)
        return node

    def status_of(self, node_id: str) -> CoverageStatus:
        if node_id not in self._status:
            raise CoverageGraphError("unknown coverage node", node_id=node_id)
        return self._status[node_id]

    def children_of(self, node_id: str) -> tuple[str, ...]:
        return tuple(sorted(self._children.get(node_id, set())))

    def parents_of(self, node_id: str) -> tuple[str, ...]:
        return tuple(sorted(self._parents.get(node_id, set())))

    def nodes_of_kind(self, kind: CoverageNodeKind) -> tuple[CoverageNode, ...]:
        return tuple(n for n in self.nodes() if n.kind is kind)

    # -- derived views ----------------------------------------------------------

    def gaps(self) -> tuple[CoverageNode, ...]:
        """Nodes that are UNCOVERED or PARTIAL (coverage gaps, well-formed)."""
        return tuple(
            n
            for n in self.nodes()
            if self._status[n.node_id] in (CoverageStatus.UNCOVERED, CoverageStatus.PARTIAL)
        )

    def orphans(self) -> tuple[CoverageNode, ...]:
        """Nodes with a structural lineage defect (ORPHANED)."""
        return tuple(n for n in self.nodes() if self._status[n.node_id] is CoverageStatus.ORPHANED)

    def orphan_code(self) -> tuple[CoverageNode, ...]:
        """Code/module/asset/runtime nodes with no lineage to a universe (fail-closed)."""
        code_kinds = {
            CoverageNodeKind.MODULE,
            CoverageNodeKind.CODE_ASSET,
            CoverageNodeKind.RUNTIME_ASSET,
            CoverageNodeKind.EPIC,
        }
        return tuple(n for n in self.orphans() if n.kind in code_kinds)

    def orphan_universes(self) -> tuple[CoverageNode, ...]:
        """Universe nodes with no downstream edge (ORPHANED)."""
        return tuple(n for n in self.orphans() if n.kind is ROOT_KIND)

    def covered(self) -> tuple[CoverageNode, ...]:
        return tuple(n for n in self.nodes() if self._status[n.node_id] is CoverageStatus.COVERED)

    def coverage_percentage(self, kind: CoverageNodeKind = ROOT_KIND) -> float:
        """Percentage of nodes of ``kind`` that are fully COVERED (0.0 when none exist)."""
        population = self.nodes_of_kind(kind)
        if not population:
            return 0.0
        covered = sum(1 for n in population if self._status[n.node_id] is CoverageStatus.COVERED)
        return round(100.0 * covered / len(population), 4)

    def to_dict(self) -> dict[str, Any]:
        return {
            "node_count": len(self._nodes),
            "edge_count": len(self._edges),
            "nodes": [
                {**n.to_dict(), "status": self._status[n.node_id].value} for n in self.nodes()
            ],
            "edges": [e.to_dict() for e in self._edges],
        }

    def fingerprint(self) -> str:
        """Deterministic fingerprint of the whole graph incl. computed statuses."""
        return content_hash(self.to_dict())


__all__ = ["CoverageGraph"]
