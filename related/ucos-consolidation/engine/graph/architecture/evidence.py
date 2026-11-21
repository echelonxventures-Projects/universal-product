"""UCOS-EPIC-010 (Terminal T2) — Architecture Intelligence evidence.

Produces an auditable, deterministic evidence artifact describing the built
Architecture Intelligence Engine: its provenance, the five deliverables
(Dependency Intelligence, Architecture Impact Engine, Critical Path Engine, Blast
Radius Engine, Knowledge Insights Report), and worked query exemplars proving each
engine is *operational* over Registry Truth (the mission success criterion).

The builder is read-only over Registry Truth (DP-03). It optionally writes the
evidence document to a mutable runtime directory (never the corpus); the writer
refuses to target the frozen corpus.
"""

from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from engine.foundation.guards.frozen_paths import find_frozen_writes
from engine.graph.architecture.engine import (
    ARCHITECTURE_INTELLIGENCE_CONTRACT,
    ArchitectureIntelligenceEngine,
)
from engine.graph.architecture.errors import InsightsWriteError
from engine.graph.architecture.reachability import SemanticReachability
from engine.graph.model import KIND_ARTIFACT

#: Evidence document schema version (append-only, semantically versioned).
EVIDENCE_VERSION = "1.0.0"


def _exemplars(aie: ArchitectureIntelligenceEngine) -> dict[str, Any]:
    """Worked exemplars proving every engine answers real questions."""
    blast = aie.blast_radius
    # The artifact with the largest blast radius exercises non-trivial traversal.
    top = blast.top(limit=1)
    subject = top[0].subject if top else ""

    result: dict[str, Any] = {"subject": subject}
    if subject:
        result["blast_radius"] = blast.analyze(subject).to_dict()
        result["impact_prediction"] = aie.predict_impact([subject]).to_dict()
        reach = SemanticReachability(aie.core)
        result["reachability"] = reach.summary(subject)
    result["critical_path_length"] = aie.analyze_critical_path().length
    result["circular_dependencies"] = aie.dependency.circular().to_dict()["count"]
    return result


def build_evidence(aie: ArchitectureIntelligenceEngine, *, limit: int = 10) -> dict[str, Any]:
    """Build the read-only evidence document for the Architecture Intelligence Engine."""
    aie.build_all()
    core = aie.core
    insights = aie.insights(limit=limit)
    exemplars = _exemplars(aie)

    deliverables = {
        "dependency_intelligence": aie.dependency.summary(),
        "architecture_impact_engine": aie.impact.summary(limit=limit),
        "critical_path_engine": aie.critical_path.summary(limit=limit),
        "blast_radius_engine": aie.blast_radius.summary(limit=limit),
        "knowledge_insights_report": {
            "totals": insights["totals"],
            "findings": insights["findings"],
            "healthy": insights["healthy"],
        },
    }
    operational = (
        core.order() > 0
        and len(core.nodes_of_kind(KIND_ARTIFACT)) > 0
        and bool(exemplars["subject"])
        and insights["insights_version"] == "1.0.0"
    )
    return {
        "evidence_version": EVIDENCE_VERSION,
        "generated_at": datetime.now(tz=UTC).isoformat(),
        "contract": {
            "name": ARCHITECTURE_INTELLIGENCE_CONTRACT.name,
            "version": str(ARCHITECTURE_INTELLIGENCE_CONTRACT.version),
            "description": ARCHITECTURE_INTELLIGENCE_CONTRACT.description,
        },
        "provenance": core.provenance.to_dict(),
        "core": {"nodes": core.order(), "edges": core.size()},
        "deliverables": deliverables,
        "insights": insights,
        "exemplars": exemplars,
        "operational": operational,
    }


def _assert_writable(path: Path) -> None:
    """Refuse to write into the frozen corpus (DP-03)."""
    try:
        repo_root = Path(__file__).resolve().parents[3]
        relative = path.resolve().relative_to(repo_root)
    except ValueError:
        return  # outside the repo entirely — allowed (e.g. tmp dirs)
    if find_frozen_writes([relative.as_posix()]):
        raise InsightsWriteError(
            "refusing to write architecture-intelligence evidence into the frozen corpus",
            path=str(path),
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
    "build_evidence",
    "write_evidence",
]
