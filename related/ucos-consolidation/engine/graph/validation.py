"""UCOS-EPIC-002 (Terminal T2) — Universal Knowledge Graph validation.

Read-only structural validation of a projected :class:`KnowledgeGraph` against the
mission invariants. The report is a pure query — it never mutates the graph or the
corpus (DP-03) — and it distinguishes hard *violations* (which fail the graph)
from informational *findings* (e.g. known external trace markers, UMB-007 §5).

Invariants checked:
    * **No duplicate nodes** — every ``node_id`` is unique (guaranteed at build
      time, re-asserted here for defence in depth).
    * **Immutable identifiers** — every node/edge identifier matches an accepted
      immutable-identifier shape (``UCOS-*`` / ``UEDGE-*`` / ``VOL-*`` / ``USIG-*``
      / a namespaced synthetic ``PREFIX::...`` anchor).
    * **Referential integrity** — every edge endpoint resolves to a node; the
      count of unresolved endpoints is reported.
    * **Version awareness** — every artifact node carries a non-empty version.
    * **Acyclic dependency projection** — the ``Depends-On`` DAG has no cycle. A
      reported cycle FAILS validity (CEP-009 Art XV.2 / Art XX.2), so the CLI and
      every gate built on ``is_valid`` fail closed on it.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any

from engine.graph.engine import DEPENDS_ON
from engine.graph.model import KIND_ARTIFACT, KnowledgeGraph
from engine.graph.queries import find_cycle

# Accepted immutable-identifier shapes. Registry identifiers are the certified
# ``UCOS-*`` / ``UEDGE-*`` / ``VOL-*`` / ``USIG-*`` families; synthetic projection
# anchors are namespaced with a ``PREFIX::`` marker so they can never be confused
# with (or collide against) a registry identifier.
_IMMUTABLE_ID = re.compile(
    r"^(UCOS-[A-Z0-9]+-\d+|UEDGE-\d+|USIG-\d+|VOL-\d+|[A-Z][A-Za-z0-9_]*::.+"
    r"|KGE::.+|UCHG-\d+|URUN-\d+)$"
)


@dataclass(frozen=True, slots=True)
class GraphValidationReport:
    """Read-only findings from validating a projected knowledge graph."""

    node_count: int
    edge_count: int
    duplicate_node_ids: tuple[str, ...] = ()
    malformed_node_ids: tuple[str, ...] = ()
    malformed_edge_ids: tuple[str, ...] = ()
    dangling_edge_endpoints: tuple[str, ...] = ()
    unversioned_artifacts: tuple[str, ...] = ()
    dependency_cycle: tuple[str, ...] = ()

    @property
    def is_valid(self) -> bool:
        """True iff no hard mission invariant was violated.

        The hard invariants are: no duplicate nodes, immutable identifiers,
        version-awareness, and an **acyclic ``Depends-On`` projection**.

        ``dependency_cycle`` is a validity FAILURE, not a finding. CEP-009
        Art XV.2 provides that a lineage forming a cycle IS PROHIBITED and
        Art XX.2 that such a cycle places the Program in HALTED; a gate that
        reported the cycle while returning valid was fail-open (UCCEP-F-003,
        discharged by WP-UCCEP-003 T-2 / UCCEP-000005). The graph still never
        invents or hides a cycle — it reflects Registry Truth faithfully in
        ``dependency_cycle`` — but it no longer certifies it as valid. Callers
        that must inspect a knowingly-cyclic substrate pass
        ``require_acyclic_dependencies=False`` to ``validate_graph``, which
        leaves the field empty and the invariant unasserted.

        One condition remains a *finding* rather than a validity failure because
        it is a property of Registry Truth by design rather than a defect:

            * ``dangling_edge_endpoints`` — external trace markers exist by design
              (UMB-007 §5).
        """
        return not (
            self.duplicate_node_ids
            or self.malformed_node_ids
            or self.malformed_edge_ids
            or self.unversioned_artifacts
            or self.dependency_cycle
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "is_valid": self.is_valid,
            "node_count": self.node_count,
            "edge_count": self.edge_count,
            "duplicate_node_ids": list(self.duplicate_node_ids),
            "malformed_node_ids": list(self.malformed_node_ids),
            "malformed_edge_ids": list(self.malformed_edge_ids),
            "dangling_edge_endpoints": list(self.dangling_edge_endpoints),
            "unversioned_artifacts": list(self.unversioned_artifacts),
            "dependency_cycle": list(self.dependency_cycle),
        }


def _is_immutable(identifier: str) -> bool:
    return bool(_IMMUTABLE_ID.match(identifier))


def validate_graph(
    graph: KnowledgeGraph, *, require_acyclic_dependencies: bool = True
) -> GraphValidationReport:
    """Validate ``graph`` against the mission invariants and return a report."""
    seen: set[str] = set()
    duplicates: dict[str, None] = {}
    malformed_nodes: list[str] = []
    unversioned: list[str] = []
    for node in graph.nodes():
        if node.node_id in seen:
            duplicates.setdefault(node.node_id, None)
        seen.add(node.node_id)
        if not _is_immutable(node.node_id):
            malformed_nodes.append(node.node_id)
        if node.kind == KIND_ARTIFACT and not node.version:
            unversioned.append(node.node_id)

    malformed_edges: list[str] = []
    dangling: dict[str, None] = {}
    for edge in graph.edges():
        if not _is_immutable(edge.edge_id):
            malformed_edges.append(edge.edge_id)
        for endpoint in (edge.source, edge.target):
            if not graph.has_node(endpoint):
                dangling.setdefault(endpoint, None)

    cycle: tuple[str, ...] = ()
    if require_acyclic_dependencies:
        cycle = find_cycle(graph, types=[DEPENDS_ON])

    return GraphValidationReport(
        node_count=graph.order(),
        edge_count=graph.size(),
        duplicate_node_ids=tuple(sorted(duplicates)),
        malformed_node_ids=tuple(sorted(malformed_nodes)),
        malformed_edge_ids=tuple(sorted(malformed_edges)),
        dangling_edge_endpoints=tuple(sorted(dangling)),
        unversioned_artifacts=tuple(sorted(unversioned)),
        dependency_cycle=cycle,
    )


__all__ = ["GraphValidationReport", "validate_graph"]
