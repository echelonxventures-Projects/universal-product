"""URI-000001 — traceability closure.

Traceability here is not a report written after the fact; it is a graph built from the
seals each stage already carries, then checked for closure in **both** directions:

* **forward** — every realizable canonical object reaches at least one materialized
  artifact. A canonical fact that realizes into nothing is an unrealized obligation.
* **backward** — every generated artifact reaches at least one canonical object. An
  artifact with no canonical ancestor is an orphan: something was invented.

Either failure is a governance rejection, not a warning. That is the mechanical form of
the mission constraint "everything generated from canonical knowledge": if it holds, no
output exists that canonical knowledge does not explain, and no canonical knowledge exists
that the output ignores.

Edge relations reuse the canonical UKDA relationship vocabulary
(:class:`~engine.knowledge.model.RelationType`) rather than inventing a second edge
language.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any

from engine.knowledge.model import RelationType
from intelligence.realization.contracts import (
    GenerationManifest,
    ImplementationRecord,
    RealizationComposition,
    RealizationPlan,
    RealizationStage,
    TraceEdge,
)
from intelligence.realization.knowledge import KnowledgeIntake

#: The realization spine, expressed in the canonical relationship vocabulary.
SPINE = (
    ("canonical-object", RelationType.GOVERNS, "target"),
    ("target", RelationType.PRODUCES, "step"),
    ("step", RelationType.IMPLEMENTS, "unit"),
    ("unit", RelationType.GENERATED_FROM, "artifact"),
    ("artifact", RelationType.DERIVED_FROM, "file"),
)


@dataclass(frozen=True, slots=True)
class TraceLedger:
    """The realization traceability graph and its closure verdict."""

    edges: tuple[TraceEdge, ...]
    knowledge_seal: str
    forward_gaps: tuple[str, ...]
    orphan_artifacts: tuple[str, ...]
    unmaterialized: tuple[str, ...]

    @property
    def closed(self) -> bool:
        """Closure is binary and fail-closed: any gap or orphan breaks it."""
        return not (self.forward_gaps or self.orphan_artifacts or self.unmaterialized)

    def relations(self) -> dict[str, int]:
        counts: dict[str, int] = {}
        for edge in self.edges:
            counts[edge.relation] = counts.get(edge.relation, 0) + 1
        return dict(sorted(counts.items()))

    def chain(self, cko_id: str) -> dict[str, list[str]]:
        """The forward chain from one canonical object to the files it realizes into."""
        hops: dict[str, list[str]] = {}
        frontier = {cko_id}
        for source_kind, relation, target_kind in SPINE:
            reached = sorted(
                {
                    edge.target
                    for edge in self.edges
                    if edge.relation == relation.value and edge.source in frontier
                }
            )
            hops[f"{source_kind}->{target_kind}"] = reached
            frontier = set(reached)
        return hops

    def to_dict(self) -> dict[str, Any]:
        return {
            "closed": self.closed,
            "knowledge_seal": self.knowledge_seal,
            "edge_count": len(self.edges),
            "relations": self.relations(),
            "spine": [{"from": src, "relation": rel.value, "to": dst} for src, rel, dst in SPINE],
            "forward_gaps": list(self.forward_gaps),
            "orphan_artifacts": list(self.orphan_artifacts),
            "unmaterialized": list(self.unmaterialized),
            "edges": [edge.to_dict() for edge in self.edges],
        }


class TraceabilityEngine:
    """Builds the realization trace ledger and verifies closure both ways."""

    def build(
        self,
        intake: KnowledgeIntake,
        plan: RealizationPlan,
        composition: RealizationComposition,
        manifest: GenerationManifest,
        record: ImplementationRecord | None = None,
    ) -> TraceLedger:
        edges: list[TraceEdge] = []

        # canonical object -> target
        for target in plan.targets:
            for cko_id in target.cko_ids:
                edges.append(
                    TraceEdge(
                        source=cko_id,
                        relation=RelationType.GOVERNS.value,
                        target=target.target_id,
                        stage=RealizationStage.INTAKE,
                    )
                )
        # target -> step
        for step in plan.steps:
            edges.append(
                TraceEdge(
                    source=step.target_id,
                    relation=RelationType.PRODUCES.value,
                    target=step.step_id,
                    stage=RealizationStage.PLANNING,
                )
            )
        # step -> unit
        for unit in composition.units:
            edges.append(
                TraceEdge(
                    source=unit.step_id,
                    relation=RelationType.IMPLEMENTS.value,
                    target=unit.unit_id,
                    stage=RealizationStage.COMPOSITION,
                )
            )
        # unit -> artifact
        for artifact in manifest.artifacts:
            edges.append(
                TraceEdge(
                    source=artifact.provenance.unit_id,
                    relation=RelationType.GENERATED_FROM.value,
                    target=artifact.relative_path,
                    stage=RealizationStage.GENERATION,
                )
            )
        # artifact -> materialized file
        materialized: set[str] = set()
        if record is not None:
            for item in record.files:
                materialized.add(item.relative_path)
                edges.append(
                    TraceEdge(
                        source=item.relative_path,
                        relation=RelationType.DERIVED_FROM.value,
                        target=f"file:{item.relative_path}",
                        stage=RealizationStage.IMPLEMENTATION,
                    )
                )

        return TraceLedger(
            edges=tuple(sorted(edges, key=lambda e: (e.relation, e.source, e.target))),
            knowledge_seal=intake.knowledge_seal,
            forward_gaps=self._forward_gaps(intake, manifest),
            orphan_artifacts=self._orphans(manifest),
            unmaterialized=self._unmaterialized(manifest, materialized, record),
        )

    # -- closure checks -------------------------------------------------------

    @staticmethod
    def _forward_gaps(intake: KnowledgeIntake, manifest: GenerationManifest) -> tuple[str, ...]:
        """Realizable canonical objects that no artifact cites as a source."""
        realized = {
            cko_id for artifact in manifest.artifacts for cko_id in artifact.provenance.source_ckos
        }
        return tuple(sorted(cko for cko in intake.realizable_ids() if cko not in realized))

    @staticmethod
    def _orphans(manifest: GenerationManifest) -> tuple[str, ...]:
        """Artifacts with no canonical ancestor — the signature of invention."""
        return tuple(
            sorted(
                artifact.relative_path
                for artifact in manifest.artifacts
                if not artifact.provenance.source_ckos
            )
        )

    @staticmethod
    def _unmaterialized(
        manifest: GenerationManifest,
        materialized: set[str],
        record: ImplementationRecord | None,
    ) -> tuple[str, ...]:
        """Generated artifacts that never reached a file (skipped when no pass ran)."""
        if record is None or record.dry_run:
            return ()
        return tuple(sorted(path for path in manifest.paths() if path not in materialized))


def build_trace(
    intake: KnowledgeIntake,
    plan: RealizationPlan,
    composition: RealizationComposition,
    manifest: GenerationManifest,
    record: ImplementationRecord | None = None,
) -> TraceLedger:
    """Convenience entry point: build the realization trace ledger."""
    return TraceabilityEngine().build(intake, plan, composition, manifest, record)


def coverage_summary(ledger: TraceLedger, intake: KnowledgeIntake) -> Mapping[str, Any]:
    """A compact, deterministic coverage view over the trace ledger."""
    realizable = intake.realizable_ids()
    realized = [cko for cko in realizable if cko not in ledger.forward_gaps]
    return {
        "realizable": len(realizable),
        "realized": len(realized),
        "gaps": len(ledger.forward_gaps),
        "coverage_pct": round(100.0 * len(realized) / len(realizable), 2) if realizable else 0.0,
        "closed": ledger.closed,
    }


__all__ = [
    "SPINE",
    "TraceLedger",
    "TraceabilityEngine",
    "build_trace",
    "coverage_summary",
]
