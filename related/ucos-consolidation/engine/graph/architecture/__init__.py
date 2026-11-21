"""UCOS Ω∞ — Architecture Intelligence Engine (UCOS-EPIC-010, Terminal T2).

Extends the certified Universal Knowledge Graph (UCOS-EPIC-002) into an
**Architecture Intelligence Engine**: higher-order, deterministic graph
intelligence built **read-only** over Registry Truth (DP-03). It adds no store and
mutates no corpus — every engine is a pure analytical view of the one core graph
(UMB-006 *three roots, one graph*; GOV-INT-001 single source of truth).

Higher-order intelligence delivered:
    * **Capability dependency graph** & **Dependency Intelligence**
      (:mod:`engine.graph.architecture.dependency_intelligence`).
    * **Layer dependency graph**, inversions & layer cycles
      (:mod:`engine.graph.architecture.layers`).
    * **Circular dependency detection** — every cycle via SCC analysis
      (:mod:`engine.graph.architecture.algorithms`,
      :mod:`~engine.graph.architecture.dependency_intelligence`).
    * **Blast-radius analysis** (:mod:`engine.graph.architecture.blast_radius`).
    * **Critical-path analysis** (:mod:`engine.graph.architecture.critical_path`).
    * **Impact prediction** — the Architecture Impact Engine
      (:mod:`engine.graph.architecture.impact`).
    * **Semantic reachability** (:mod:`engine.graph.architecture.reachability`).
    * **Architecture visualization models**
      (:mod:`engine.graph.architecture.visualization`).
    * **Knowledge Insights Report** (:mod:`engine.graph.architecture.insights`).

The five mission deliverables (Dependency Intelligence, Architecture Impact
Engine, Critical Path Engine, Blast Radius Engine, Knowledge Insights Report) are
composed behind the Foundation-contract-compliant
:class:`~engine.graph.architecture.engine.ArchitectureIntelligenceEngine`
(``architecture.intelligence`` v1.0.0) with a CLI
(:mod:`engine.graph.architecture.cli`) and deterministic evidence
(:mod:`engine.graph.architecture.evidence`).
"""

from __future__ import annotations

from engine.graph.architecture.algorithms import (
    condensation,
    cyclic_components,
    longest_paths,
    normalise_adjacency,
    strongly_connected_components,
)
from engine.graph.architecture.blast_radius import BlastRadiusEngine, BlastRadiusReport
from engine.graph.architecture.critical_path import CriticalPathEngine, CriticalPathReport
from engine.graph.architecture.dependency_intelligence import (
    CapabilityDependencyGraph,
    CircularDependencyReport,
    DependencyIntelligence,
    detect_circular_dependencies,
)
from engine.graph.architecture.engine import (
    ARCHITECTURE_INTELLIGENCE_CONTRACT,
    DIAGRAM_NAMES,
    ArchitectureIntelligenceEngine,
)
from engine.graph.architecture.errors import (
    ArchitectureIntelligenceError,
    InsightsWriteError,
    ReachabilityError,
    UnknownEngineError,
)
from engine.graph.architecture.evidence import (
    EVIDENCE_VERSION,
    build_evidence,
    write_evidence,
)
from engine.graph.architecture.impact import ArchitectureImpactEngine, ImpactPrediction
from engine.graph.architecture.insights import INSIGHTS_VERSION, build_insights_report
from engine.graph.architecture.layers import (
    LAYER_ORDER,
    UNCLASSIFIED,
    LayerDependency,
    LayerDependencyGraph,
    layer_depth,
    layer_of_category,
)
from engine.graph.architecture.reachability import (
    RELATION_FAMILIES,
    ReachabilityResult,
    SemanticReachability,
)
from engine.graph.architecture.visualization import (
    VISUALIZATION_FORMATS,
    ArchitectureModel,
    ModelEdge,
    ModelNode,
    capability_diagram,
    condensation_diagram,
    layer_diagram,
)

__all__ = [
    # facade + contract
    "ArchitectureIntelligenceEngine",
    "ARCHITECTURE_INTELLIGENCE_CONTRACT",
    "DIAGRAM_NAMES",
    # dependency intelligence
    "DependencyIntelligence",
    "CapabilityDependencyGraph",
    "CircularDependencyReport",
    "detect_circular_dependencies",
    # layers
    "LayerDependencyGraph",
    "LayerDependency",
    "LAYER_ORDER",
    "UNCLASSIFIED",
    "layer_of_category",
    "layer_depth",
    # blast radius
    "BlastRadiusEngine",
    "BlastRadiusReport",
    # critical path
    "CriticalPathEngine",
    "CriticalPathReport",
    # impact
    "ArchitectureImpactEngine",
    "ImpactPrediction",
    # reachability
    "SemanticReachability",
    "ReachabilityResult",
    "RELATION_FAMILIES",
    # visualization
    "ArchitectureModel",
    "ModelNode",
    "ModelEdge",
    "layer_diagram",
    "capability_diagram",
    "condensation_diagram",
    "VISUALIZATION_FORMATS",
    # insights
    "build_insights_report",
    "INSIGHTS_VERSION",
    # algorithms
    "strongly_connected_components",
    "cyclic_components",
    "condensation",
    "longest_paths",
    "normalise_adjacency",
    # evidence
    "build_evidence",
    "write_evidence",
    "EVIDENCE_VERSION",
    # errors
    "ArchitectureIntelligenceError",
    "UnknownEngineError",
    "InsightsWriteError",
    "ReachabilityError",
]
