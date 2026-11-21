"""EC2-TASK-000129 — Artifact Explorer Lineage / Provenance / Trace (EC2-EPIC-009).

The immutable, content-addressed **navigation projections** the Artifact Explorer
surfaces over the EC-2 traceability chain — all derived **by reference** from certified
EC2-EPIC-007 records, re-deriving nothing:

    * :class:`ArtifactProvenance` — a faithful read-only projection of a
      :class:`~platform.generation.provenance.RequestProvenance` (the GOV-002 **link-4**
      ``Generation Artifact → Blueprint → Request → Implementation Artifact`` provenance
      -by-reference edge). It **reuses the existing** ``provenance_id`` (no duplicate
      provenance model) and reproduces the certified trace edge byte-for-byte.
    * :class:`ArtifactLineage` — the ordered lineage of nodes
      (``generation → blueprint → request → implementation``) an artifact traverses,
      carrying the dependency chain and a completeness predicate.
    * :class:`ArtifactTrace` — the full navigation edge combining the provenance trace
      edge with the :class:`~platform.generation.dispatch.DispatchRecord` execution
      handoff edge, so a caller can navigate an artifact from its ``05-GENERATION`` origin
      all the way to the certified EC-1 Execution Runtime handoff — read-only.

All ids are content-addressed and reproducible (IMP-007 §5); no synthetic linkage is
introduced (every field is an explicit citation drawn from the certified record).
"""

from __future__ import annotations

from dataclasses import dataclass
from platform.artifact_explorer.errors import (
    ArtifactLineageError,
    ArtifactProvenanceError,
    ArtifactTraceError,
)
from platform.blueprints.contracts import BlueprintFamily
from platform.foundation.contracts import content_hash
from platform.generation.contracts import GenerationRequest
from platform.generation.dispatch import DispatchRecord
from platform.generation.provenance import RequestProvenance
from typing import Any


@dataclass(frozen=True, slots=True)
class ArtifactProvenance:
    """An immutable read-only projection of a certified :class:`RequestProvenance` (link-4).

    Reuses the existing ``provenance_id`` (no new id, no duplicate provenance model) and
    carries the explicit ``Generation → Blueprint → Request → Implementation`` citations
    by reference. :meth:`edge` reproduces the certified provenance trace edge exactly.
    """

    provenance_id: str
    request_ref: str
    family: BlueprintFamily
    generation_reference: str
    generation_artifact_id: str
    blueprint_ref: str
    blueprint_provenance_ref: str
    implementation_target: str
    dependency_chain: tuple[str, ...]
    content_hash: str
    is_traceable: bool

    @classmethod
    def from_provenance(cls, provenance: RequestProvenance) -> ArtifactProvenance:
        """Project a certified :class:`RequestProvenance` (fail-closed; reuses its id)."""
        if not isinstance(provenance, RequestProvenance):
            raise ArtifactProvenanceError("ArtifactProvenance requires a RequestProvenance")
        return cls(
            provenance_id=provenance.provenance_id,
            request_ref=provenance.request_ref,
            family=provenance.family,
            generation_reference=provenance.generation_reference,
            generation_artifact_id=provenance.generation_artifact_id,
            blueprint_ref=provenance.blueprint_ref,
            blueprint_provenance_ref=provenance.blueprint_provenance_ref,
            implementation_target=provenance.implementation_target,
            dependency_chain=tuple(provenance.dependency_chain),
            content_hash=provenance.content_hash,
            is_traceable=provenance.is_traceable,
        )

    def edge(self) -> dict[str, Any]:
        """Reproduce the certified link-4 trace edge (faithful, by reference)."""
        return {
            "provenance_id": self.provenance_id,
            "link": "GOV-002-link-4",
            "generation": {
                "reference": self.generation_reference,
                "artifact_id": self.generation_artifact_id,
                "family": self.family.value,
            },
            "blueprint": {
                "blueprint_ref": self.blueprint_ref,
                "provenance_ref": self.blueprint_provenance_ref,
            },
            "request": {"request_ref": self.request_ref, "content_hash": self.content_hash},
            "implementation": {
                "target": self.implementation_target,
                "dependency_chain": list(self.dependency_chain),
            },
            "traceable": self.is_traceable,
        }

    def to_dict(self) -> dict[str, Any]:
        return {
            "provenance_id": self.provenance_id,
            "request_ref": self.request_ref,
            "family": self.family.value,
            "generation_reference": self.generation_reference,
            "generation_artifact_id": self.generation_artifact_id,
            "blueprint_ref": self.blueprint_ref,
            "blueprint_provenance_ref": self.blueprint_provenance_ref,
            "implementation_target": self.implementation_target,
            "dependency_chain": list(self.dependency_chain),
            "content_hash": self.content_hash,
            "is_traceable": self.is_traceable,
        }

    def fingerprint(self) -> str:
        return content_hash(self.to_dict())


@dataclass(frozen=True, slots=True)
class ArtifactLineage:
    """An immutable, content-addressed ordered lineage of an artifact (by reference).

    The lineage nodes model the ``Generation Artifact → Blueprint → Request →
    Implementation Artifact`` chain. When no provenance is recorded yet, the lineage is a
    partial ``Blueprint → Request`` view (``is_complete`` is False) — never fabricated.
    """

    lineage_id: str
    request_ref: str
    blueprint_ref: str
    family: BlueprintFamily
    nodes: tuple[tuple[str, str], ...]
    dependency_chain: tuple[str, ...]
    is_complete: bool

    @classmethod
    def from_request(
        cls,
        request: GenerationRequest,
        *,
        provenance: RequestProvenance | None = None,
    ) -> ArtifactLineage:
        """Build a deterministic lineage projection (pure; fail-closed)."""
        if not isinstance(request, GenerationRequest):
            raise ArtifactLineageError("artifact lineage requires a GenerationRequest")
        if provenance is not None and not isinstance(provenance, RequestProvenance):
            raise ArtifactLineageError("provenance must be a RequestProvenance when provided")
        nodes: list[tuple[str, str]] = []
        if provenance is not None:
            nodes.append(("generation", provenance.generation_artifact_id))
        nodes.append(("blueprint", request.blueprint_ref))
        nodes.append(("request", request.request_id))
        if provenance is not None:
            nodes.append(("implementation", provenance.implementation_target))
        dependency_chain = tuple(provenance.dependency_chain) if provenance is not None else ()
        is_complete = provenance is not None and provenance.is_traceable
        node_tuple = tuple(nodes)
        core = {
            "request_ref": request.request_id,
            "blueprint_ref": request.blueprint_ref,
            "family": request.family.value,
            "nodes": [list(n) for n in node_tuple],
            "dependency_chain": list(dependency_chain),
            "is_complete": is_complete,
        }
        return cls(
            lineage_id=f"UCOS-AXLN-{content_hash(core)[:16]}",
            request_ref=request.request_id,
            blueprint_ref=request.blueprint_ref,
            family=request.family,
            nodes=node_tuple,
            dependency_chain=dependency_chain,
            is_complete=is_complete,
        )

    def edge(self) -> dict[str, Any]:
        """The explicit ordered lineage edge (audit evidence)."""
        return {
            "lineage_id": self.lineage_id,
            "link": "artifact-lineage",
            "request_ref": self.request_ref,
            "family": self.family.value,
            "nodes": [{"kind": kind, "reference": ref} for kind, ref in self.nodes],
            "dependency_chain": list(self.dependency_chain),
            "complete": self.is_complete,
        }

    def to_dict(self) -> dict[str, Any]:
        return {
            "lineage_id": self.lineage_id,
            "request_ref": self.request_ref,
            "blueprint_ref": self.blueprint_ref,
            "family": self.family.value,
            "nodes": [list(n) for n in self.nodes],
            "dependency_chain": list(self.dependency_chain),
            "is_complete": self.is_complete,
        }

    def fingerprint(self) -> str:
        return content_hash(self.to_dict())


@dataclass(frozen=True, slots=True)
class ArtifactTrace:
    """An immutable, content-addressed full artifact trace navigation edge (by reference).

    Combines the link-4 provenance trace edge (Generation → Blueprint → Request →
    Implementation) with the execution-dispatch handoff edge (Request → Execution
    Runtime), so a caller navigates the artifact end to end. ``is_traceable`` is True iff
    both the provenance edge is present-and-traceable **and** the execution handoff is
    recorded.
    """

    trace_id: str
    request_ref: str
    blueprint_ref: str
    family: BlueprintFamily
    has_provenance: bool
    has_dispatch: bool
    is_traceable: bool
    provenance_edge: dict[str, Any] | None
    dispatch_edge: dict[str, Any] | None

    @classmethod
    def from_parts(
        cls,
        request: GenerationRequest,
        *,
        provenance: RequestProvenance | None = None,
        dispatch: DispatchRecord | None = None,
    ) -> ArtifactTrace:
        """Build a deterministic full trace edge (pure; fail-closed)."""
        if not isinstance(request, GenerationRequest):
            raise ArtifactTraceError("artifact trace requires a GenerationRequest")
        if provenance is not None and not isinstance(provenance, RequestProvenance):
            raise ArtifactTraceError("provenance must be a RequestProvenance when provided")
        if dispatch is not None and not isinstance(dispatch, DispatchRecord):
            raise ArtifactTraceError("dispatch must be a DispatchRecord when provided")
        provenance_edge = provenance.trace_edge() if provenance is not None else None
        dispatch_edge = dispatch.handoff_edge() if dispatch is not None else None
        is_traceable = provenance is not None and provenance.is_traceable and dispatch is not None
        core = {
            "request_ref": request.request_id,
            "blueprint_ref": request.blueprint_ref,
            "family": request.family.value,
            "has_provenance": provenance is not None,
            "has_dispatch": dispatch is not None,
            "is_traceable": is_traceable,
            "provenance_edge": provenance_edge,
            "dispatch_edge": dispatch_edge,
        }
        return cls(
            trace_id=f"UCOS-AXTR-{content_hash(core)[:16]}",
            request_ref=request.request_id,
            blueprint_ref=request.blueprint_ref,
            family=request.family,
            has_provenance=provenance is not None,
            has_dispatch=dispatch is not None,
            is_traceable=is_traceable,
            provenance_edge=provenance_edge,
            dispatch_edge=dispatch_edge,
        )

    def edge(self) -> dict[str, Any]:
        """The explicit end-to-end (generation → execution) navigation edge."""
        return {
            "trace_id": self.trace_id,
            "link": "artifact-trace",
            "request_ref": self.request_ref,
            "family": self.family.value,
            "provenance": self.provenance_edge,
            "dispatch": self.dispatch_edge,
            "traceable": self.is_traceable,
        }

    def to_dict(self) -> dict[str, Any]:
        return {
            "trace_id": self.trace_id,
            "request_ref": self.request_ref,
            "blueprint_ref": self.blueprint_ref,
            "family": self.family.value,
            "has_provenance": self.has_provenance,
            "has_dispatch": self.has_dispatch,
            "is_traceable": self.is_traceable,
            "provenance_edge": self.provenance_edge,
            "dispatch_edge": self.dispatch_edge,
        }

    def fingerprint(self) -> str:
        return content_hash(self.to_dict())


__all__ = ["ArtifactProvenance", "ArtifactLineage", "ArtifactTrace"]
