"""ZG-P-02 — Coverage evidence sources (Universe→Code Coverage Instrument).

The coverage graph is reconstructed **only** from authoritative evidence — never from a
hardcoded universe map or a manual coverage table. An :class:`EvidenceSource` produces an
:class:`EvidenceBundle` (the declared nodes + adjacency-checked edges). Two sources exist:

    * :class:`InMemoryEvidenceSource` — an explicit bundle (used to test the pure graph /
      engine / registry / health / certification core deterministically).
    * :class:`~platform.coverage.repository.RepositoryEvidenceSource` — parses the real
      repository artifacts (universe catalog, IMP tracker, ``06-IMPLEMENTATION/``,
      ``platform/**``, ``engine/**``) into a bundle.

An :class:`EvidenceBundle` is immutable and **self-normalizing**: nodes and edges are
deduplicated by content-addressed id and returned in stable (sorted) order, so the bundle
fingerprint is byte-identical across processes for identical evidence.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Iterable
from dataclasses import dataclass
from platform.coverage.contracts import CoverageEdge, CoverageNode
from platform.coverage.errors import CoverageEvidenceError
from platform.foundation.contracts import content_hash
from typing import Any


@dataclass(frozen=True, slots=True)
class EvidenceBundle:
    """An immutable, normalized set of coverage nodes and edges from one evidence pass."""

    nodes: tuple[CoverageNode, ...]
    edges: tuple[CoverageEdge, ...]

    @classmethod
    def create(cls, nodes: Iterable[CoverageNode], edges: Iterable[CoverageEdge]) -> EvidenceBundle:
        """Build a normalized bundle: dedupe by id, order deterministically, fail-closed."""
        node_map: dict[str, CoverageNode] = {}
        for node in nodes:
            if not isinstance(node, CoverageNode):
                raise CoverageEvidenceError("evidence nodes must be CoverageNode instances")
            existing = node_map.get(node.node_id)
            if existing is not None and existing.fingerprint() != node.fingerprint():
                # Same identity (kind+ref) but conflicting authority/label/metadata:
                # keep the first-seen deterministically ordered variant (fail-closed:
                # a genuine conflict cannot silently overwrite an existing declaration).
                raise CoverageEvidenceError(
                    "conflicting evidence for the same coverage node",
                    node_id=node.node_id,
                    ref=node.ref,
                )
            node_map.setdefault(node.node_id, node)
        edge_map: dict[str, CoverageEdge] = {}
        for edge in edges:
            if not isinstance(edge, CoverageEdge):
                raise CoverageEvidenceError("evidence edges must be CoverageEdge instances")
            edge_map.setdefault(edge.edge_id, edge)
        ordered_nodes = tuple(sorted(node_map.values(), key=lambda n: n.node_id))
        ordered_edges = tuple(sorted(edge_map.values(), key=lambda e: e.edge_id))
        return cls(nodes=ordered_nodes, edges=ordered_edges)

    def to_dict(self) -> dict[str, Any]:
        return {
            "node_count": len(self.nodes),
            "edge_count": len(self.edges),
            "nodes": [n.to_dict() for n in self.nodes],
            "edges": [e.to_dict() for e in self.edges],
        }

    def fingerprint(self) -> str:
        """Deterministic fingerprint of the evidence (excludes logical ticks)."""
        return content_hash(self.to_dict())


class EvidenceSource(ABC):
    """Abstract source of coverage evidence. ``collect`` must be deterministic + pure."""

    @abstractmethod
    def collect(self) -> EvidenceBundle:
        """Return the coverage evidence bundle. Repeated calls MUST be identical."""
        raise NotImplementedError  # pragma: no cover - abstract


class InMemoryEvidenceSource(EvidenceSource):
    """An explicit, in-memory evidence source (the deterministic test/fixture source)."""

    __slots__ = ("_bundle",)

    def __init__(self, nodes: Iterable[CoverageNode], edges: Iterable[CoverageEdge]) -> None:
        self._bundle = EvidenceBundle.create(nodes, edges)

    def collect(self) -> EvidenceBundle:
        return self._bundle


__all__ = ["EvidenceBundle", "EvidenceSource", "InMemoryEvidenceSource"]
