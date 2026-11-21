"""ZG-P-02 — Coverage registry (Universe→Code Coverage Instrument).

An append-only, content-addressed registry of coverage nodes and edges — the durable,
audit-safe, recomputable record of a coverage graph. It mirrors the certified
append-only ledger discipline (e.g. ``platform.security.classification.ClassificationLedger``,
``platform.blueprints.provenance.ProvenanceLedger``): records are keyed by their
content-addressed id, re-recording an identical record is idempotent, and recording a
*different* record under an already-known id is refused (fail-closed — no silent
overwrite, no duplicate coverage identity). It creates no alternate registry authority;
it is a deterministic in-memory record surface recomputable from evidence at any time.
"""

from __future__ import annotations

from platform.coverage.contracts import CoverageEdge, CoverageNode
from platform.coverage.errors import CoverageRegistryError
from platform.coverage.evidence import EvidenceBundle
from platform.coverage.graph import CoverageGraph
from platform.foundation.contracts import content_hash
from typing import Any


class CoverageRegistry:
    """A deterministic, append-only, content-addressed coverage record surface."""

    __slots__ = ("_nodes", "_edges")

    def __init__(self) -> None:
        self._nodes: dict[str, CoverageNode] = {}
        self._edges: dict[str, CoverageEdge] = {}

    # -- append-only recording --------------------------------------------------

    def record_node(self, node: CoverageNode) -> CoverageNode:
        """Record a node (idempotent by id; fail-closed on a conflicting duplicate)."""
        if not isinstance(node, CoverageNode):
            raise CoverageRegistryError("only a CoverageNode may be recorded")
        existing = self._nodes.get(node.node_id)
        if existing is not None:
            if existing.fingerprint() == node.fingerprint():
                return existing
            raise CoverageRegistryError(
                "node id already recorded with different content (duplicate coverage)",
                node_id=node.node_id,
            )
        self._nodes[node.node_id] = node
        return node

    def record_edge(self, edge: CoverageEdge) -> CoverageEdge:
        """Record an edge (idempotent by id; append-only).

        An edge's ``edge_id`` is a content hash of exactly the same fields as its
        ``fingerprint``, so a matching id provably denotes identical content — recording
        an already-known edge is therefore idempotent (no conflicting-duplicate case can
        arise for edges, unlike nodes whose id excludes authority/metadata).
        """
        if not isinstance(edge, CoverageEdge):
            raise CoverageRegistryError("only a CoverageEdge may be recorded")
        existing = self._edges.get(edge.edge_id)
        if existing is not None:
            return existing
        self._edges[edge.edge_id] = edge
        return edge

    def ingest(self, bundle: EvidenceBundle) -> None:
        """Record every node and edge of an evidence bundle (append-only, fail-closed)."""
        if not isinstance(bundle, EvidenceBundle):
            raise CoverageRegistryError("ingest requires an EvidenceBundle")
        for node in bundle.nodes:
            self.record_node(node)
        for edge in bundle.edges:
            self.record_edge(edge)

    # -- accessors --------------------------------------------------------------

    def __len__(self) -> int:
        return len(self._nodes) + len(self._edges)

    @property
    def node_count(self) -> int:
        return len(self._nodes)

    @property
    def edge_count(self) -> int:
        return len(self._edges)

    def has_node(self, node_id: str) -> bool:
        return node_id in self._nodes

    def has_edge(self, edge_id: str) -> bool:
        return edge_id in self._edges

    def nodes(self) -> tuple[CoverageNode, ...]:
        return tuple(self._nodes[nid] for nid in sorted(self._nodes))

    def edges(self) -> tuple[CoverageEdge, ...]:
        return tuple(self._edges[eid] for eid in sorted(self._edges))

    def duplicate_edge_refs(self) -> tuple[str, ...]:
        """Distinct (source→target) pairs asserted by more than one recorded edge.

        Multiple *authorities* citing the same coverage relationship is a duplicate
        coverage record (the same logical edge recorded under different evidence). This
        surfaces them for the ``duplicate-coverage`` health check (advisory — the id
        space itself never collides because ids are content-addressed).
        """
        seen: dict[tuple[str, str, str, str], int] = {}
        for edge in self._edges.values():
            key = (
                edge.source_kind.value,
                edge.source_ref,
                edge.target_kind.value,
                edge.target_ref,
            )
            seen[key] = seen.get(key, 0) + 1
        return tuple(f"{k[0]}:{k[1]}->{k[2]}:{k[3]}" for k, n in sorted(seen.items()) if n > 1)

    def to_dict(self) -> dict[str, Any]:
        return {
            "node_count": len(self._nodes),
            "edge_count": len(self._edges),
            "nodes": [n.to_dict() for n in self.nodes()],
            "edges": [e.to_dict() for e in self.edges()],
        }

    def fingerprint(self) -> str:
        """Deterministic fingerprint over all recorded nodes + edges."""
        return content_hash(self.to_dict())

    def as_bundle(self) -> EvidenceBundle:
        """Reconstruct an evidence bundle from the recorded records."""
        return EvidenceBundle.create(self.nodes(), self.edges())

    def graph(self) -> CoverageGraph:
        """Build a coverage graph from the recorded records (deterministic)."""
        return CoverageGraph(self.as_bundle())


__all__ = ["CoverageRegistry"]
