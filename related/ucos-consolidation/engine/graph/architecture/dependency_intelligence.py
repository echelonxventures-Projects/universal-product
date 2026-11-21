"""UCOS-EPIC-010 (Terminal T2) — Dependency Intelligence.

Higher-order dependency analysis over the certified Universal Knowledge Graph
(read-only, DP-03). Three complementary views:

    * **Capability dependency graph** — the artifact-to-artifact dependency
      topology induced by the ``Consumes`` capability relation (who relies on whom
      for capability provision), with transitive closure and cycle detection.
    * **Circular dependency detection** — *every* circular dependency (not just
      one) in the ``Depends-On`` relation, the ``Consumes`` relation, and their
      union, via strongly-connected-component analysis.
    * **Dependency Intelligence report** — a deterministic roll-up combining the
      structural ``Depends-On`` DAG, the capability graph, and the circular
      findings into a single evidence-grade summary.

All results are deterministic (sorted) and never mutate the corpus.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from engine.graph.architecture.algorithms import (
    Adjacency,
    cyclic_components,
    normalise_adjacency,
)
from engine.graph.engine import CONSUMES, DEPENDS_ON
from engine.graph.model import KIND_ARTIFACT, KnowledgeGraph
from engine.graph.queries import descendants


def _relation_adjacency(core: KnowledgeGraph, edge_type: str) -> dict[str, tuple[str, ...]]:
    """Adjacency over one edge family, restricted to artifact endpoints."""
    artifacts = {n.node_id for n in core.nodes_of_kind(KIND_ARTIFACT)}
    pairs = [
        (e.source, e.target)
        for e in core.edges_of_type(edge_type)
        if e.source in artifacts and e.target in artifacts
    ]
    return normalise_adjacency(artifacts, pairs)


class CapabilityDependencyGraph:
    """The capability-provision dependency graph (``Consumes`` relation).

    ``A Consumes B`` means artifact ``A`` depends on a capability provided by ``B``.
    The graph answers direct/transitive capability dependencies and dependents, and
    detects capability cycles (mutually-consuming artifacts). Read-only.
    """

    __slots__ = ("_out", "_in")

    def __init__(self, core: KnowledgeGraph) -> None:
        out = _relation_adjacency(core, CONSUMES)
        in_sets: dict[str, set[str]] = {n: set() for n in out}
        for source, targets in out.items():
            for target in targets:
                in_sets.setdefault(target, set()).add(source)
        self._out = out
        self._in = {n: tuple(sorted(s)) for n, s in in_sets.items()}

    def provides_for(self, node_id: str) -> tuple[str, ...]:
        """Artifacts that consume a capability of ``node_id`` (direct dependents)."""
        return self._in.get(node_id, ())

    def consumes(self, node_id: str) -> tuple[str, ...]:
        """Capabilities (artifacts) ``node_id`` directly consumes."""
        return self._out.get(node_id, ())

    def transitive_consumes(self, node_id: str) -> tuple[str, ...]:
        """Everything ``node_id`` (transitively) consumes."""
        if node_id not in self._out:
            return ()
        return _closure(self._out, node_id)

    def cycles(self) -> tuple[tuple[str, ...], ...]:
        """Every circular capability dependency (deterministic)."""
        return cyclic_components(self._out)

    def adjacency(self) -> dict[str, tuple[str, ...]]:
        """The raw ``Consumes`` adjacency (defensive copy semantics)."""
        return dict(self._out)

    def summary(self) -> dict[str, Any]:
        edge_count = sum(len(v) for v in self._out.values())
        return {
            "nodes": len(self._out),
            "edges": edge_count,
            "cycles": [list(c) for c in self.cycles()],
        }


def _closure(adjacency: Adjacency, start: str) -> tuple[str, ...]:
    """Deterministic transitive closure of ``start`` over ``adjacency`` (excl. start)."""
    seen: set[str] = set()
    stack = list(adjacency.get(start, ()))
    while stack:
        current = stack.pop()
        if current in seen or current == start:
            continue
        seen.add(current)
        for nxt in adjacency.get(current, ()):
            if nxt not in seen:
                stack.append(nxt)
    return tuple(sorted(seen))


@dataclass(frozen=True, slots=True)
class CircularDependencyReport:
    """All circular dependencies found across the analysed relations (read-only)."""

    depends_on_cycles: tuple[tuple[str, ...], ...] = ()
    capability_cycles: tuple[tuple[str, ...], ...] = ()
    combined_cycles: tuple[tuple[str, ...], ...] = ()

    @property
    def has_cycles(self) -> bool:
        """True iff any analysed relation contains a circular dependency."""
        return bool(self.depends_on_cycles or self.capability_cycles or self.combined_cycles)

    @property
    def largest_cycle(self) -> tuple[str, ...]:
        """The largest circular component across all relations (deterministic)."""
        best: tuple[str, ...] = ()
        for group in (self.combined_cycles, self.depends_on_cycles, self.capability_cycles):
            for cycle in group:
                if len(cycle) > len(best) or (len(cycle) == len(best) and cycle < best):
                    best = cycle
        return best

    def to_dict(self) -> dict[str, Any]:
        return {
            "has_cycles": self.has_cycles,
            "depends_on_cycles": [list(c) for c in self.depends_on_cycles],
            "capability_cycles": [list(c) for c in self.capability_cycles],
            "combined_cycles": [list(c) for c in self.combined_cycles],
            "largest_cycle": list(self.largest_cycle),
            "count": {
                "depends_on": len(self.depends_on_cycles),
                "capability": len(self.capability_cycles),
                "combined": len(self.combined_cycles),
            },
        }


def detect_circular_dependencies(core: KnowledgeGraph) -> CircularDependencyReport:
    """Detect every circular dependency in the ``Depends-On`` / ``Consumes`` relations.

    The *combined* relation is the union of both edge families, so a cycle that only
    closes when structural dependency and capability consumption are considered
    together is still surfaced. Deterministic and read-only (DP-03).
    """
    depends = _relation_adjacency(core, DEPENDS_ON)
    consumes = _relation_adjacency(core, CONSUMES)

    combined_sets: dict[str, set[str]] = {n: set(depends.get(n, ())) for n in depends}
    for node, targets in consumes.items():
        combined_sets.setdefault(node, set()).update(targets)
    combined = {n: tuple(sorted(s)) for n, s in combined_sets.items()}

    return CircularDependencyReport(
        depends_on_cycles=cyclic_components(depends),
        capability_cycles=cyclic_components(consumes),
        combined_cycles=cyclic_components(combined),
    )


class DependencyIntelligence:
    """The Dependency Intelligence deliverable — a read-only analytical facade.

    Combines the structural ``Depends-On`` dependency relation, the capability
    dependency graph, and circular-dependency detection into one deterministic
    surface over the core knowledge graph.
    """

    __slots__ = ("_core", "_depends", "_capability", "_circular")

    def __init__(self, core: KnowledgeGraph) -> None:
        self._core = core
        self._depends = _relation_adjacency(core, DEPENDS_ON)
        self._capability = CapabilityDependencyGraph(core)
        self._circular: CircularDependencyReport | None = None

    @property
    def capability(self) -> CapabilityDependencyGraph:
        return self._capability

    def dependencies_of(self, node_id: str) -> tuple[str, ...]:
        """Direct structural dependencies (outbound ``Depends-On``)."""
        return self._depends.get(node_id, ())

    def transitive_dependencies(self, node_id: str) -> tuple[str, ...]:
        """Everything ``node_id`` transitively depends on (structural)."""
        if node_id not in self._depends:
            return ()
        return descendants(self._core, node_id, types=[DEPENDS_ON])

    def circular(self) -> CircularDependencyReport:
        """The circular-dependency report (memoised)."""
        if self._circular is None:
            self._circular = detect_circular_dependencies(self._core)
        return self._circular

    def fan_in(self, node_id: str) -> int:
        """Number of direct structural dependents of ``node_id`` (afferent coupling)."""
        return sum(1 for _, targets in self._depends.items() if node_id in targets)

    def fan_out(self, node_id: str) -> int:
        """Number of direct structural dependencies of ``node_id`` (efferent coupling)."""
        return len(self._depends.get(node_id, ()))

    def hubs(self, *, limit: int = 10) -> tuple[tuple[str, int], ...]:
        """The most-depended-upon artifacts (highest fan-in), ranked deterministically."""
        scored = [(node, self.fan_in(node)) for node in self._depends if self.fan_in(node) > 0]
        scored.sort(key=lambda item: (-item[1], item[0]))
        return tuple(scored[:limit])

    def summary(self) -> dict[str, Any]:
        edge_count = sum(len(v) for v in self._depends.values())
        return {
            "depends_on": {"nodes": len(self._depends), "edges": edge_count},
            "capability": self._capability.summary(),
            "circular": self.circular().to_dict(),
            "top_hubs": [{"node": n, "fan_in": s} for n, s in self.hubs()],
        }


__all__ = [
    "CapabilityDependencyGraph",
    "CircularDependencyReport",
    "detect_circular_dependencies",
    "DependencyIntelligence",
]
