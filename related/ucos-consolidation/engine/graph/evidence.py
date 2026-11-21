"""UCOS-EPIC-002 (Terminal T2) — Universal Knowledge Graph evidence.

Produces an auditable, deterministic evidence artifact describing a built
knowledge graph: its provenance, per-projection sizes, validation verdict, and a
set of worked query exemplars (dependency / impact / trace) that demonstrate the
graph is *operational* (the mission success criterion).

The evidence builder is read-only over Registry Truth (DP-03). It optionally
writes the evidence document to a mutable runtime directory (never the corpus);
the writer refuses to target the frozen corpus.
"""

from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from engine.foundation.guards.frozen_paths import find_frozen_writes
from engine.graph.adapter import KNOWLEDGE_GRAPH_CONTRACT, KnowledgeGraphAdapter
from engine.graph.errors import GraphError
from engine.graph.projections import PROJECTION_NAMES

#: Evidence document schema version (append-only, semantically versioned).
EVIDENCE_VERSION = "1.0.0"


class EvidenceWriteError(GraphError):
    """Refused to write evidence (e.g. target resolves under the frozen corpus)."""

    code = "KG-EVIDENCE-001"


def _exemplars(adapter: KnowledgeGraphAdapter) -> dict[str, Any]:
    """Worked query exemplars proving the graph answers real questions."""
    dependency = adapter.dependency()
    impact = adapter.impact()

    # Pick the subject with the largest change-impact blast radius, so the
    # exemplar demonstrably exercises a non-trivial transitive traversal.
    subject = ""
    best = -1
    for node in impact.graph.nodes():
        radius = impact.blast_radius(node.node_id)
        if radius > best:
            best, subject = radius, node.node_id

    result: dict[str, Any] = {"subject": subject}
    if subject:
        result["direct_dependencies"] = list(dependency.dependencies_of(subject))
        result["direct_dependents"] = list(dependency.dependents_of(subject))
        result["blast_radius"] = impact.blast_radius(subject)
        result["impacted_sample"] = list(impact.impact_of(subject)[:10])
    result["dependency_acyclic"] = dependency.is_acyclic()
    return result


def build_evidence(adapter: KnowledgeGraphAdapter) -> dict[str, Any]:
    """Build the read-only evidence document for the built knowledge graph."""
    adapter.build_all()
    core = adapter.core
    report = adapter.validate()
    projections = {name: adapter.projection(name).summary() for name in PROJECTION_NAMES}
    return {
        "evidence_version": EVIDENCE_VERSION,
        "generated_at": datetime.now(tz=UTC).isoformat(),
        "contract": {
            "name": KNOWLEDGE_GRAPH_CONTRACT.name,
            "version": str(KNOWLEDGE_GRAPH_CONTRACT.version),
            "description": KNOWLEDGE_GRAPH_CONTRACT.description,
        },
        "provenance": core.provenance.to_dict(),
        "core": {
            "nodes": core.order(),
            "edges": core.size(),
            "kinds": list(core.kinds()),
            "edge_types": list(core.edge_types()),
        },
        "projections": projections,
        "validation": report.to_dict(),
        "certification_verdict": str(adapter.certification.get("verdict") or "UNKNOWN"),
        "exemplars": _exemplars(adapter),
        "operational": report.is_valid and len(projections) == len(PROJECTION_NAMES),
    }


def _assert_writable(path: Path) -> None:
    """Refuse to write into the frozen corpus (DP-03)."""
    try:
        repo_root = Path(__file__).resolve().parents[2]
        relative = path.resolve().relative_to(repo_root)
    except ValueError:
        return  # outside the repo entirely — allowed (e.g. tmp dirs)
    if find_frozen_writes([relative.as_posix()]):
        raise EvidenceWriteError(
            "refusing to write evidence into the frozen corpus", path=str(path)
        )


def write_evidence(evidence: dict[str, Any], path: str | Path) -> Path:
    """Write the evidence document to ``path`` (never the frozen corpus)."""
    target = Path(path)
    _assert_writable(target)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(evidence, indent=2, sort_keys=True), encoding="utf-8")
    return target


__all__ = [
    "EVIDENCE_VERSION",
    "EvidenceWriteError",
    "build_evidence",
    "write_evidence",
]
