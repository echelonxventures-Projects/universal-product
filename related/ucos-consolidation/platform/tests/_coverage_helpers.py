"""Shared deterministic fixtures for the Universe→Code Coverage Instrument tests (ZG-P-02).

Not a test module — provides builders for well-formed, gapped, orphaned, partial, and
duplicate coverage evidence so the pure graph/engine/registry/health/certification core
is exercised deterministically without coupling to the live repository.
"""

from __future__ import annotations

from platform.coverage.contracts import CoverageEdge, CoverageNode, CoverageNodeKind
from platform.coverage.evidence import InMemoryEvidenceSource

K = CoverageNodeKind


def node(kind: CoverageNodeKind, ref: str, authority: str = "test-authority") -> CoverageNode:
    return CoverageNode.create(kind, ref, authority=authority)


def edge(
    sk: CoverageNodeKind,
    sr: str,
    tk: CoverageNodeKind,
    tr: str,
    *,
    authority: str = "test-authority",
    evidence: str = "test-evidence",
    tick: int = 0,
) -> CoverageEdge:
    return CoverageEdge.create(
        source_kind=sk,
        source_ref=sr,
        target_kind=tk,
        target_ref=tr,
        authority=authority,
        evidence=evidence,
        tick=tick,
    )


def _complete_nodes_edges() -> tuple[list[CoverageNode], list[CoverageEdge]]:
    """A fully COVERED chain: 2 universes → phase → program → impl → epic → 2 modules
    → 2 code assets → 1 runtime asset."""
    nodes = [
        node(K.UNIVERSE, "UNI-001"),
        node(K.UNIVERSE, "UNI-002"),
        node(K.PHASE, "IMP-005"),
        node(K.PROGRAM, "06-IMPLEMENTATION/IDENTITY.md"),
        node(K.IMPLEMENTATION, "platform/identity"),
        node(K.EPIC, "EC2-EPIC-002"),
        node(K.MODULE, "platform/identity/service.py"),
        node(K.MODULE, "platform/identity/roles.py"),
        node(K.CODE_ASSET, "platform/identity/service.py::AuthorizationService"),
        node(K.CODE_ASSET, "platform/identity/roles.py::Role"),
        node(K.RUNTIME_ASSET, "runtime:platform/identity"),
    ]
    edges = [
        edge(K.UNIVERSE, "UNI-001", K.PHASE, "IMP-005"),
        edge(K.UNIVERSE, "UNI-002", K.PHASE, "IMP-005"),
        edge(K.PHASE, "IMP-005", K.PROGRAM, "06-IMPLEMENTATION/IDENTITY.md"),
        edge(K.PROGRAM, "06-IMPLEMENTATION/IDENTITY.md", K.IMPLEMENTATION, "platform/identity"),
        edge(K.IMPLEMENTATION, "platform/identity", K.EPIC, "EC2-EPIC-002"),
        edge(K.EPIC, "EC2-EPIC-002", K.MODULE, "platform/identity/service.py"),
        edge(K.EPIC, "EC2-EPIC-002", K.MODULE, "platform/identity/roles.py"),
        edge(
            K.MODULE,
            "platform/identity/service.py",
            K.CODE_ASSET,
            "platform/identity/service.py::AuthorizationService",
        ),
        edge(
            K.MODULE,
            "platform/identity/roles.py",
            K.CODE_ASSET,
            "platform/identity/roles.py::Role",
        ),
        edge(
            K.CODE_ASSET,
            "platform/identity/service.py::AuthorizationService",
            K.RUNTIME_ASSET,
            "runtime:platform/identity",
        ),
        edge(
            K.CODE_ASSET,
            "platform/identity/roles.py::Role",
            K.RUNTIME_ASSET,
            "runtime:platform/identity",
        ),
    ]
    return nodes, edges


def complete_source() -> InMemoryEvidenceSource:
    nodes, edges = _complete_nodes_edges()
    return InMemoryEvidenceSource(nodes, edges)


def gapped_source() -> InMemoryEvidenceSource:
    """Complete chain plus a universe whose phase has no program (UNCOVERED gap)."""
    nodes, edges = _complete_nodes_edges()
    nodes.append(node(K.UNIVERSE, "UNI-099"))
    nodes.append(node(K.PHASE, "IMP-012"))
    edges.append(edge(K.UNIVERSE, "UNI-099", K.PHASE, "IMP-012"))
    return InMemoryEvidenceSource(nodes, edges)


def partial_source() -> InMemoryEvidenceSource:
    """A chain where one module has no code asset ⇒ module UNCOVERED ⇒ epic PARTIAL."""
    nodes, edges = _complete_nodes_edges()
    nodes.append(node(K.MODULE, "platform/identity/empty.py"))
    edges.append(edge(K.EPIC, "EC2-EPIC-002", K.MODULE, "platform/identity/empty.py"))
    return InMemoryEvidenceSource(nodes, edges)


def orphan_universe_source() -> InMemoryEvidenceSource:
    """A universe with no downstream edge (structural orphan)."""
    return InMemoryEvidenceSource([node(K.UNIVERSE, "UNI-500")], [])


def orphan_code_source() -> InMemoryEvidenceSource:
    """An epic→module→code_asset→runtime chain with no upward lineage to a universe."""
    nodes = [
        node(K.EPIC, "EC2-EPIC-XX"),
        node(K.MODULE, "platform/x/m.py"),
        node(K.CODE_ASSET, "platform/x/m.py::f"),
        node(K.RUNTIME_ASSET, "runtime:platform/x"),
    ]
    edges = [
        edge(K.EPIC, "EC2-EPIC-XX", K.MODULE, "platform/x/m.py"),
        edge(K.MODULE, "platform/x/m.py", K.CODE_ASSET, "platform/x/m.py::f"),
        edge(K.CODE_ASSET, "platform/x/m.py::f", K.RUNTIME_ASSET, "runtime:platform/x"),
    ]
    return InMemoryEvidenceSource(nodes, edges)


def duplicate_source() -> InMemoryEvidenceSource:
    """Complete chain plus a duplicate logical edge under a different authority."""
    nodes, edges = _complete_nodes_edges()
    edges.append(
        edge(
            K.PHASE,
            "IMP-005",
            K.PROGRAM,
            "06-IMPLEMENTATION/IDENTITY.md",
            authority="second-authority",
            evidence="second-evidence",
        )
    )
    return InMemoryEvidenceSource(nodes, edges)


__all__ = [
    "K",
    "node",
    "edge",
    "complete_source",
    "gapped_source",
    "partial_source",
    "orphan_universe_source",
    "orphan_code_source",
    "duplicate_source",
]
