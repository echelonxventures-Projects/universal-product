"""UCOS-EPIC-010 (Terminal T2) — Knowledge Insights Report.

The single, deterministic roll-up that fuses every architecture-intelligence engine
into one evidence-grade document: dependency intelligence, the layer dependency
graph and its findings, circular dependencies, the critical path, and the
highest-blast-radius artifacts. It is the human- and machine-facing "state of the
architecture" summary derived read-only from Registry Truth (DP-03).

The report is a pure query — it never mutates the graph or the corpus — and every
field is deterministically ordered so the whole document is byte-reproducible.
"""

from __future__ import annotations

from typing import Any

from engine.graph.architecture.blast_radius import BlastRadiusEngine
from engine.graph.architecture.critical_path import CriticalPathEngine
from engine.graph.architecture.dependency_intelligence import DependencyIntelligence
from engine.graph.architecture.layers import LayerDependencyGraph
from engine.graph.model import KIND_ARTIFACT, KnowledgeGraph

#: Insights document schema version (append-only, semantically versioned).
INSIGHTS_VERSION = "1.0.0"


def build_insights_report(
    core: KnowledgeGraph,
    *,
    dependency: DependencyIntelligence | None = None,
    layers: LayerDependencyGraph | None = None,
    critical: CriticalPathEngine | None = None,
    blast: BlastRadiusEngine | None = None,
    limit: int = 10,
) -> dict[str, Any]:
    """Build the deterministic Knowledge Insights Report over the core graph.

    Any sub-engine not supplied is constructed internally, so the report is usable
    standalone; the :class:`~engine.graph.architecture.engine.ArchitectureIntelligenceEngine`
    facade passes its memoised engines to avoid rebuilding them.
    """
    dependency = dependency or DependencyIntelligence(core)
    layers = layers or LayerDependencyGraph(core)
    critical = critical or CriticalPathEngine(core)
    blast = blast or BlastRadiusEngine(core, layers=layers)

    circular = dependency.circular()
    critical_report = critical.critical_path()
    top_blast = blast.top(limit=limit)

    artifact_count = len(core.nodes_of_kind(KIND_ARTIFACT))
    findings = _findings(layers, circular, critical_report.cyclic)

    return {
        "insights_version": INSIGHTS_VERSION,
        "totals": {
            "artifacts": artifact_count,
            "nodes": core.order(),
            "edges": core.size(),
            "layers": len(layers.layers()),
        },
        "dependency_intelligence": dependency.summary(),
        "layer_intelligence": layers.summary(),
        "circular_dependencies": circular.to_dict(),
        "critical_path": critical_report.to_dict(),
        "blast_radius": {
            "impactable_nodes": blast.impactable_nodes,
            "top": [
                {"subject": r.subject, "radius": r.radius, "severity": r.severity}
                for r in top_blast
            ],
        },
        "findings": findings,
        "healthy": not findings,
    }


def _findings(
    layers: LayerDependencyGraph,
    circular: Any,
    critical_cyclic: bool,
) -> list[dict[str, Any]]:
    """Deterministically ordered list of architectural findings (non-blocking)."""
    findings: list[dict[str, Any]] = []
    for inv in layers.inversions():
        findings.append(
            {
                "kind": "layer_inversion",
                "detail": f"{inv.source} depends upward on {inv.target}",
                "weight": inv.weight,
            }
        )
    for cycle in layers.cycles():
        findings.append({"kind": "layer_cycle", "detail": list(cycle)})
    for cycle in circular.combined_cycles:
        findings.append({"kind": "circular_dependency", "detail": list(cycle)})
    # Stable ordering: by kind then serialised detail.
    findings.sort(key=lambda f: (f["kind"], str(f["detail"])))
    return findings


__all__ = ["INSIGHTS_VERSION", "build_insights_report"]
