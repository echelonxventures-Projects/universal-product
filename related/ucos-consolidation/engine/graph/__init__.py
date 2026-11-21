"""UCOS Ω∞ — Universal Knowledge Graph (UCOS-EPIC-002, Terminal T2).

The complete repository knowledge graph, built **read-only** over Registry Truth
(the ``00-BOOK`` substrate exposed by the EPIC-002 Registry Adapter). Per UMB-006
(*three roots, one graph*), the mission's graphs are projections of one core
graph, not separate stores — preserving single-source-of-truth (GOV-INT-001).

Deliverables (this package):
    * **Graph Engine** — :func:`~engine.graph.engine.build_core_graph` projects
      artifacts + volumes + relationships into the core
      :class:`~engine.graph.model.KnowledgeGraph`.
    * **Ten projections** — ontology, capability, dependency, traceability,
      evidence, requirement, implementation, validation, certification, impact
      (:mod:`engine.graph.projections`).
    * **Queries** — deterministic traversals (:mod:`engine.graph.queries`).
    * **Visualization** — JSON / Cytoscape / DOT / Mermaid
      (:mod:`engine.graph.visualization`).
    * **Validation** — mission-invariant checks
      (:mod:`engine.graph.validation`).
    * **Evidence** — auditable operational evidence
      (:mod:`engine.graph.evidence`).
    * **Adapter** — Foundation-contract-compliant facade
      (:class:`~engine.graph.adapter.KnowledgeGraphAdapter`, ``knowledge.graph``
      v1.0.0) and CLI (:mod:`engine.graph.cli`).

Mission invariants: read Registry only (DP-03), no duplicate nodes, immutable
identifiers, version aware.
"""

from __future__ import annotations

from engine.graph.adapter import KNOWLEDGE_GRAPH_CONTRACT, KnowledgeGraphAdapter
from engine.graph.engine import (
    build_core_graph,
    load_certification,
    load_signals,
    load_twin,
)
from engine.graph.errors import (
    DuplicateEdgeError,
    DuplicateNodeError,
    GraphError,
    GraphValidationError,
    ImmutableIdentifierError,
    NodeNotFoundError,
    ProjectionError,
)
from engine.graph.evidence import build_evidence, write_evidence
from engine.graph.model import (
    Edge,
    GraphProvenance,
    KnowledgeGraph,
    Node,
)
from engine.graph.projections import (
    PROJECTION_NAMES,
    CapabilityGraph,
    CertificationGraph,
    DependencyGraph,
    EvidenceGraph,
    ImpactGraph,
    ImplementationGraph,
    OntologyGraph,
    Projection,
    RequirementGraph,
    TraceabilityGraph,
    ValidationGraph,
    build_projection,
)
from engine.graph.validation import GraphValidationReport, validate_graph
from engine.graph.visualization import (
    VISUALIZATION_FORMATS,
    render,
    to_cytoscape,
    to_dot,
    to_mermaid,
    to_node_link_json,
)

__all__ = [
    # adapter + contract
    "KnowledgeGraphAdapter",
    "KNOWLEDGE_GRAPH_CONTRACT",
    # engine
    "build_core_graph",
    "load_signals",
    "load_certification",
    "load_twin",
    # model
    "Node",
    "Edge",
    "GraphProvenance",
    "KnowledgeGraph",
    # projections
    "Projection",
    "OntologyGraph",
    "CapabilityGraph",
    "DependencyGraph",
    "TraceabilityGraph",
    "EvidenceGraph",
    "RequirementGraph",
    "ImplementationGraph",
    "ValidationGraph",
    "CertificationGraph",
    "ImpactGraph",
    "PROJECTION_NAMES",
    "build_projection",
    # validation
    "GraphValidationReport",
    "validate_graph",
    # visualization
    "render",
    "to_node_link_json",
    "to_cytoscape",
    "to_dot",
    "to_mermaid",
    "VISUALIZATION_FORMATS",
    # evidence
    "build_evidence",
    "write_evidence",
    # errors
    "GraphError",
    "DuplicateNodeError",
    "DuplicateEdgeError",
    "ImmutableIdentifierError",
    "NodeNotFoundError",
    "ProjectionError",
    "GraphValidationError",
]
