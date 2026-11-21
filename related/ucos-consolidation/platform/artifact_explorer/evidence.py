"""EC2-TASK-000131 — Artifact Explorer Evidence (EC2-EPIC-009).

The deterministic, content-addressed record of the artifact-explorer runtime state
(evidence). It embeds no wall-clock and no ambient state, so an identical runtime state
(consumed registry/dispatch/provenance fingerprints, navigation counters, access
evaluations, health) yields a byte-identical :class:`ExplorerEvidence` and fingerprint
(P5 / Mandatory Rule 6 — every determination yields evidence). It is *runtime* evidence
over the explorer itself; the artifacts it surfaces are the certified EC2-EPIC-007
records it consumes by reference.
"""

from __future__ import annotations

from dataclasses import dataclass
from platform.foundation.contracts import content_hash
from typing import Any


@dataclass(frozen=True, slots=True)
class ExplorerEvidence:
    """A deterministic, content-addressed record of explorer runtime state (evidence)."""

    registry_fingerprint: str
    dispatch_fingerprint: str
    provenance_fingerprint: str
    artifact_count: int
    dispatched_count: int
    provenance_count: int
    traceable_count: int
    lookup_count: int
    search_count: int
    lineage_count: int
    provenance_navigation_count: int
    trace_count: int
    access_evaluation_count: int
    health_status: str
    evidence_id: str = ""

    @classmethod
    def create(
        cls,
        *,
        registry_fingerprint: str,
        dispatch_fingerprint: str,
        provenance_fingerprint: str,
        artifact_count: int,
        dispatched_count: int,
        provenance_count: int,
        traceable_count: int,
        lookup_count: int,
        search_count: int,
        lineage_count: int,
        provenance_navigation_count: int,
        trace_count: int,
        access_evaluation_count: int,
        health_status: str,
    ) -> ExplorerEvidence:
        core = {
            "registry_fingerprint": registry_fingerprint,
            "dispatch_fingerprint": dispatch_fingerprint,
            "provenance_fingerprint": provenance_fingerprint,
            "artifact_count": artifact_count,
            "dispatched_count": dispatched_count,
            "provenance_count": provenance_count,
            "traceable_count": traceable_count,
            "lookup_count": lookup_count,
            "search_count": search_count,
            "lineage_count": lineage_count,
            "provenance_navigation_count": provenance_navigation_count,
            "trace_count": trace_count,
            "access_evaluation_count": access_evaluation_count,
            "health_status": health_status,
        }
        return cls(
            registry_fingerprint=registry_fingerprint,
            dispatch_fingerprint=dispatch_fingerprint,
            provenance_fingerprint=provenance_fingerprint,
            artifact_count=artifact_count,
            dispatched_count=dispatched_count,
            provenance_count=provenance_count,
            traceable_count=traceable_count,
            lookup_count=lookup_count,
            search_count=search_count,
            lineage_count=lineage_count,
            provenance_navigation_count=provenance_navigation_count,
            trace_count=trace_count,
            access_evaluation_count=access_evaluation_count,
            health_status=health_status,
            evidence_id=f"UCOS-AXEV-{content_hash(core)[:16]}",
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "evidence_id": self.evidence_id,
            "registry_fingerprint": self.registry_fingerprint,
            "dispatch_fingerprint": self.dispatch_fingerprint,
            "provenance_fingerprint": self.provenance_fingerprint,
            "artifact_count": self.artifact_count,
            "dispatched_count": self.dispatched_count,
            "provenance_count": self.provenance_count,
            "traceable_count": self.traceable_count,
            "lookup_count": self.lookup_count,
            "search_count": self.search_count,
            "lineage_count": self.lineage_count,
            "provenance_navigation_count": self.provenance_navigation_count,
            "trace_count": self.trace_count,
            "access_evaluation_count": self.access_evaluation_count,
            "health_status": self.health_status,
        }

    def fingerprint(self) -> str:
        return content_hash(self.to_dict())


__all__ = ["ExplorerEvidence"]
