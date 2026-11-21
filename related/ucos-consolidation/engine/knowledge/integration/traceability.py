"""UKI Deliverable 7 — Constitutional Traceability Engine (EPIC-UKDA-002).

Produces the deterministic, end-to-end traceability chain (``UKI-LAW-006``) for any
canonical artifact:

    Constitution -> Universe -> Capability -> Implementation -> Validation ->
    Certification -> Evidence -> Deployment -> Runtime

Every stage is resolved from the artifact's own canonical fields and the single UKDA
:class:`~engine.knowledge.graph.KnowledgeGraph` (reused verbatim): constitutional
ancestors from the transitive provider closure, implementations from inbound
``implements`` edges, validation/certification/evidence from the object's recorded
links, and deployment/runtime from its lifecycle. The chain is pure and reproducible
(IMP-007 §5).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from engine.knowledge.graph import KnowledgeGraph
from engine.knowledge.model import KnowledgeAuthority, Lifecycle, RelationType
from engine.knowledge.store import KnowledgeBase

#: The ordered constitutional traceability stages (stable).
TRACE_STAGES: tuple[str, ...] = (
    "constitution",
    "universe",
    "capability",
    "implementation",
    "validation",
    "certification",
    "evidence",
    "deployment",
    "runtime",
)


@dataclass(frozen=True, slots=True)
class TraceStage:
    """One resolved stage of the constitutional traceability chain."""

    name: str
    references: tuple[str, ...]

    @property
    def present(self) -> bool:
        return bool(self.references)

    def to_dict(self) -> dict[str, Any]:
        return {"name": self.name, "present": self.present, "references": list(self.references)}


@dataclass(frozen=True, slots=True)
class TraceabilityChain:
    """The deterministic Constitution -> ... -> Runtime chain for one artifact."""

    target: str
    stages: tuple[TraceStage, ...]

    def stage(self, name: str) -> TraceStage | None:
        for stage in self.stages:
            if stage.name == name:
                return stage
        return None

    @property
    def gaps(self) -> tuple[str, ...]:
        """Names of the stages that could not be resolved (in canonical order)."""
        return tuple(s.name for s in self.stages if not s.present)

    @property
    def complete(self) -> bool:
        return not self.gaps

    def to_dict(self) -> dict[str, Any]:
        return {
            "target": self.target,
            "complete": self.complete,
            "gaps": list(self.gaps),
            "stages": [s.to_dict() for s in self.stages],
        }


class TraceabilityEngine:
    """Builds the constitutional traceability chain for an artifact (Deliverable 7)."""

    __slots__ = ("_base", "_graph")

    def __init__(self, base: KnowledgeBase) -> None:
        self._base = base
        self._graph: KnowledgeGraph = base.graph()

    def _constitution(self, cko_id: str) -> tuple[str, ...]:
        roots: list[str] = []
        obj = self._base.get_object(cko_id)
        if obj is not None and obj.authority is KnowledgeAuthority.CONSTITUTIONAL:
            roots.append(cko_id)
        for ref in self._graph.reachable_from(cko_id):
            provider = self._base.get_object(ref)
            if provider is not None and provider.authority is KnowledgeAuthority.CONSTITUTIONAL:
                roots.append(ref)
        return tuple(sorted(set(roots)))

    def _implementation(self, cko_id: str) -> tuple[str, ...]:
        refs = set(self._graph.predecessors(cko_id, type=RelationType.IMPLEMENTS))
        refs.update(self._graph.successors(cko_id, type=RelationType.IMPLEMENTS))
        return tuple(sorted(refs))

    def trace(self, cko_id: str) -> TraceabilityChain:
        """Return the deterministic traceability chain for ``cko_id`` (fail-closed lookup)."""
        obj = self._base.require_object(cko_id)
        deployment = (
            (obj.lifecycle.value,)
            if obj.lifecycle in (Lifecycle.IMPLEMENTED, Lifecycle.OPERATIONAL)
            else ()
        )
        runtime = (obj.lifecycle.value,) if obj.lifecycle is Lifecycle.OPERATIONAL else ()
        stages = (
            TraceStage("constitution", self._constitution(cko_id)),
            TraceStage("universe", (obj.universe,) if obj.universe else ()),
            TraceStage("capability", (cko_id,)),
            TraceStage("implementation", self._implementation(cko_id)),
            TraceStage("validation", (obj.validation,) if obj.validation else ()),
            TraceStage("certification", (obj.certification,) if obj.certification else ()),
            TraceStage("evidence", obj.evidence),
            TraceStage("deployment", deployment),
            TraceStage("runtime", runtime),
        )
        return TraceabilityChain(target=cko_id, stages=stages)


__all__ = ["TRACE_STAGES", "TraceStage", "TraceabilityChain", "TraceabilityEngine"]
