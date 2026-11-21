"""ZG-P-02 — Coverage engine (Universe→Code Coverage Instrument).

The deterministic recompute engine that closes G4. It exposes the five mandated
operations over an :class:`~platform.coverage.evidence.EvidenceSource`:

    * :meth:`compute`     — reconstruct the coverage graph from evidence and record it.
    * :meth:`verify`      — recompute and check integrity + fingerprint stability.
    * :meth:`reconcile`   — compare the recorded registry against a fresh recompute.
    * :meth:`fingerprint` — the deterministic coverage fingerprint.
    * :meth:`report`      — the full coverage report (status/percentage/gaps/orphans/…).

Every operation is a pure function of repository evidence: identical evidence yields
byte-identical results across processes (IMP-007 §5). The engine fails **closed** — a
malformed bundle, a dangling edge, a graph cycle, or a fingerprint divergence raises or
is reported as a violation rather than silently passing.
"""

from __future__ import annotations

from dataclasses import dataclass
from platform.coverage.contracts import CoverageNodeKind, CoverageStatus
from platform.coverage.errors import CoverageEngineError
from platform.coverage.evidence import EvidenceSource
from platform.coverage.graph import CoverageGraph
from platform.coverage.registry import CoverageRegistry
from platform.foundation.contracts import content_hash
from typing import Any


@dataclass(frozen=True, slots=True)
class CoverageVerification:
    """An immutable, content-addressed result of a coverage verification (fail-closed)."""

    ok: bool
    fingerprint: str
    violations: tuple[str, ...]
    orphan_code_count: int
    orphan_universe_count: int
    duplicate_count: int
    verification_id: str = ""

    @classmethod
    def create(
        cls,
        *,
        fingerprint: str,
        violations: tuple[str, ...],
        orphan_code_count: int,
        orphan_universe_count: int,
        duplicate_count: int,
    ) -> CoverageVerification:
        ok = not violations
        core = {
            "ok": ok,
            "fingerprint": fingerprint,
            "violations": list(violations),
            "orphan_code_count": orphan_code_count,
            "orphan_universe_count": orphan_universe_count,
            "duplicate_count": duplicate_count,
        }
        return cls(
            ok=ok,
            fingerprint=fingerprint,
            violations=violations,
            orphan_code_count=orphan_code_count,
            orphan_universe_count=orphan_universe_count,
            duplicate_count=duplicate_count,
            verification_id=f"UCOS-COVV-{content_hash(core)[:16]}",
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "verification_id": self.verification_id,
            "ok": self.ok,
            "fingerprint": self.fingerprint,
            "violations": list(self.violations),
            "orphan_code_count": self.orphan_code_count,
            "orphan_universe_count": self.orphan_universe_count,
            "duplicate_count": self.duplicate_count,
        }


@dataclass(frozen=True, slots=True)
class CoverageReconciliation:
    """An immutable diff between the recorded registry and a fresh recompute."""

    reconciled: bool
    added_nodes: tuple[str, ...]
    removed_nodes: tuple[str, ...]
    added_edges: tuple[str, ...]
    removed_edges: tuple[str, ...]
    recorded_fingerprint: str
    recomputed_fingerprint: str
    reconciliation_id: str = ""

    @classmethod
    def create(
        cls,
        *,
        added_nodes: tuple[str, ...],
        removed_nodes: tuple[str, ...],
        added_edges: tuple[str, ...],
        removed_edges: tuple[str, ...],
        recorded_fingerprint: str,
        recomputed_fingerprint: str,
    ) -> CoverageReconciliation:
        reconciled = (
            not added_nodes
            and not removed_nodes
            and not added_edges
            and not removed_edges
            and recorded_fingerprint == recomputed_fingerprint
        )
        core = {
            "reconciled": reconciled,
            "added_nodes": list(added_nodes),
            "removed_nodes": list(removed_nodes),
            "added_edges": list(added_edges),
            "removed_edges": list(removed_edges),
            "recorded_fingerprint": recorded_fingerprint,
            "recomputed_fingerprint": recomputed_fingerprint,
        }
        return cls(
            reconciled=reconciled,
            added_nodes=added_nodes,
            removed_nodes=removed_nodes,
            added_edges=added_edges,
            removed_edges=removed_edges,
            recorded_fingerprint=recorded_fingerprint,
            recomputed_fingerprint=recomputed_fingerprint,
            reconciliation_id=f"UCOS-COVR-{content_hash(core)[:16]}",
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "reconciliation_id": self.reconciliation_id,
            "reconciled": self.reconciled,
            "added_nodes": list(self.added_nodes),
            "removed_nodes": list(self.removed_nodes),
            "added_edges": list(self.added_edges),
            "removed_edges": list(self.removed_edges),
            "recorded_fingerprint": self.recorded_fingerprint,
            "recomputed_fingerprint": self.recomputed_fingerprint,
        }


class CoverageEngine:
    """The deterministic Universe→Code coverage recompute engine."""

    __slots__ = ("_source", "_registry")

    def __init__(self, source: EvidenceSource, *, registry: CoverageRegistry | None = None) -> None:
        if not isinstance(source, EvidenceSource):
            raise CoverageEngineError("CoverageEngine requires an EvidenceSource")
        if registry is not None and not isinstance(registry, CoverageRegistry):
            raise CoverageEngineError("registry must be a CoverageRegistry when provided")
        self._source = source
        self._registry = registry if registry is not None else CoverageRegistry()

    @property
    def registry(self) -> CoverageRegistry:
        return self._registry

    # -- coverage.compute() -----------------------------------------------------

    def compute(self) -> CoverageGraph:
        """Reconstruct the coverage graph from evidence and record it (append-only)."""
        bundle = self._source.collect()
        graph = CoverageGraph(bundle)  # fail-closed on dangling/illegal/cyclic edges
        self._registry.ingest(bundle)
        return graph

    # -- coverage.fingerprint() -------------------------------------------------

    def fingerprint(self) -> str:
        """The deterministic coverage fingerprint (recomputed from fresh evidence)."""
        return CoverageGraph(self._source.collect()).fingerprint()

    # -- coverage.verify() ------------------------------------------------------

    def verify(self) -> CoverageVerification:
        """Recompute and assert integrity (orphans, duplicates, fingerprint stability)."""
        bundle = self._source.collect()
        graph = CoverageGraph(bundle)
        # Determinism: two independent recomputes must fingerprint identically.
        fp1 = graph.fingerprint()
        fp2 = CoverageGraph(self._source.collect()).fingerprint()
        violations: list[str] = []
        if fp1 != fp2:
            violations.append("coverage-fingerprint-nondeterministic")
        orphan_code = graph.orphan_code()
        orphan_uni = graph.orphan_universes()
        for node in orphan_code:
            violations.append(f"orphan-code:{node.kind.value}:{node.ref}")
        for node in orphan_uni:
            violations.append(f"orphan-universe:{node.ref}")
        # Registry duplicate detection (multiple authorities for one logical edge).
        dupes = self._registry.duplicate_edge_refs() if self._registry.edge_count else ()
        for dup in dupes:
            violations.append(f"duplicate-coverage:{dup}")
        return CoverageVerification.create(
            fingerprint=fp1,
            violations=tuple(violations),
            orphan_code_count=len(orphan_code),
            orphan_universe_count=len(orphan_uni),
            duplicate_count=len(dupes),
        )

    # -- coverage.reconcile() ---------------------------------------------------

    def reconcile(self) -> CoverageReconciliation:
        """Compare the recorded registry against a fresh recompute (fail-closed diff)."""
        recorded = self._registry.as_bundle()
        recomputed = self._source.collect()
        recorded_nodes = {n.node_id for n in recorded.nodes}
        recomputed_nodes = {n.node_id for n in recomputed.nodes}
        recorded_edges = {e.edge_id for e in recorded.edges}
        recomputed_edges = {e.edge_id for e in recomputed.edges}
        return CoverageReconciliation.create(
            added_nodes=tuple(sorted(recomputed_nodes - recorded_nodes)),
            removed_nodes=tuple(sorted(recorded_nodes - recomputed_nodes)),
            added_edges=tuple(sorted(recomputed_edges - recorded_edges)),
            removed_edges=tuple(sorted(recorded_edges - recomputed_edges)),
            recorded_fingerprint=recorded.fingerprint(),
            recomputed_fingerprint=recomputed.fingerprint(),
        )

    # -- coverage.report() ------------------------------------------------------

    def report(self) -> dict[str, Any]:
        """The full, deterministic coverage report over the current evidence."""
        graph = CoverageGraph(self._source.collect())
        by_kind: dict[str, dict[str, Any]] = {}
        for kind in CoverageNodeKind:
            population = graph.nodes_of_kind(kind)
            covered = sum(
                1 for n in population if graph.status_of(n.node_id) is CoverageStatus.COVERED
            )
            by_kind[kind.value] = {
                "total": len(population),
                "covered": covered,
                "percentage": graph.coverage_percentage(kind),
            }
        return {
            "fingerprint": graph.fingerprint(),
            "node_count": len(graph),
            "edge_count": len(graph.edges()),
            "universe_coverage_percentage": graph.coverage_percentage(CoverageNodeKind.UNIVERSE),
            "by_kind": by_kind,
            "gaps": [
                {"kind": n.kind.value, "ref": n.ref, "status": graph.status_of(n.node_id).value}
                for n in graph.gaps()
            ],
            "orphans": [{"kind": n.kind.value, "ref": n.ref} for n in graph.orphans()],
        }


__all__ = [
    "CoverageVerification",
    "CoverageReconciliation",
    "CoverageEngine",
]
