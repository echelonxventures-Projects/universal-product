"""TASK-000038 — Runtime Composition Graph + Dependency Resolution (EPIC-006).

Realises the **runtime graph** and **dependency resolver** of the Universal
Runtime Composition Engine (RUNTIME-013 §D8 Composition; ORL-11 well-founded,
ORL-17 acyclic/downward/closed). A :class:`RuntimeGraph` is a read-only, directed,
**acyclic** graph over the participating runtime units ("Universes"): its nodes are
universe ids and its edges are the ``depends-on`` dependencies between them.

The graph reuses the Universal Compiler's proven, deterministic graph primitives
**verbatim** (Mandatory Rule 4 — no duplicate dependency/cycle logic):

    * :func:`engine.compiler.cycles.detect_cycle` — finds the first founding cycle;
    * :func:`engine.compiler.cycles.topological_order` — the deterministic compile
      order (a node's dependencies always precede it).

The graph is a pure structure over ids: it holds **no** ``RuntimeUnit`` and so sits
below :mod:`engine.runtime.composition` in the layering (no import cycle). It is
deterministic (every collection is sorted), closed (every referenced dependency is
a declared node, ORL-17), and acyclic (a cycle is refused with the offending path).
It is a composition structure only — it schedules and executes nothing (ORL-15).
"""

from __future__ import annotations

from collections.abc import Iterable, Mapping

from engine.compiler.cycles import detect_cycle, topological_order
from engine.foundation.obs.logging import get_logger
from engine.foundation.obs.telemetry import trace
from engine.runtime.errors import RuntimeGraphError

_logger = get_logger("runtime.graph")

#: The canonical runtime dependency edge type (a universe ``depends-on`` another).
DEPENDS_ON = "depends-on"


class RuntimeGraph:
    """A read-only, deterministic, acyclic dependency graph over universe ids.

    Construct from an edge mapping ``{universe_id: (dependency_id, ...)}``. The
    graph validates closure (ORL-17) and acyclicity (ORL-11/17) at construction, so
    an ill-formed composition graph fails loudly and auditably before any
    downstream context/plan generation.
    """

    __slots__ = ("_deps", "_dependents", "_order", "_depth")

    def __init__(self, edges: Mapping[str, Iterable[str]]) -> None:
        deps: dict[str, tuple[str, ...]] = {}
        for node, out in edges.items():
            if not isinstance(node, str) or not node:
                raise RuntimeGraphError("universe id must be a non-empty string")
            unique = sorted({dep for dep in out})
            deps[node] = tuple(unique)

        # Closure (ORL-17): every referenced dependency must be a declared node.
        for node, out in deps.items():
            for dep in out:
                if dep == node:
                    raise RuntimeGraphError("a universe cannot depend on itself", universe_id=node)
                if dep not in deps:
                    raise RuntimeGraphError(
                        "dependency is not a member of the composition (open graph)",
                        universe_id=node,
                        dependency=dep,
                    )

        # Acyclicity (ORL-11/17): reuse the compiler's deterministic cycle finder.
        cycle = detect_cycle(deps)
        if cycle is not None:
            raise RuntimeGraphError(
                "circular dependency detected in the runtime composition graph",
                cycle=list(cycle),
            )

        # Deterministic compile order (dependencies first) — reuse the compiler.
        order = topological_order(deps)

        dependents: dict[str, list[str]] = {node: [] for node in deps}
        for node, out in deps.items():
            for dep in out:
                dependents[dep].append(node)

        self._deps = deps
        self._dependents = {n: tuple(sorted(v)) for n, v in dependents.items()}
        self._order = order
        self._depth = self._compute_depth(deps, order)

    # -- construction ----------------------------------------------------------

    @classmethod
    def of(cls, edges: Mapping[str, Iterable[str]]) -> RuntimeGraph:
        """Build a :class:`RuntimeGraph` from an edge mapping (traced)."""
        with trace("runtime.graph.build", nodes=len(edges)):
            graph = cls(edges)
        _logger.info(
            "runtime.graph.built",
            nodes=len(graph._deps),
            edges=sum(len(v) for v in graph._deps.values()),
        )
        return graph

    @staticmethod
    def _compute_depth(
        deps: Mapping[str, tuple[str, ...]], order: tuple[str, ...]
    ) -> dict[str, int]:
        """Depth = 0 for a root; else 1 + max(depth of dependencies).

        Computed over the topological ``order`` so every dependency's depth is
        already known when a node is visited (deterministic).
        """
        depth: dict[str, int] = {}
        for node in order:
            out = deps.get(node, ())
            depth[node] = 0 if not out else 1 + max(depth[dep] for dep in out)
        return depth

    # -- size / membership -----------------------------------------------------

    def __len__(self) -> int:
        return len(self._deps)

    def __contains__(self, node: object) -> bool:
        return node in self._deps

    def count(self) -> int:
        """Total number of universes (nodes) in the graph."""
        return len(self._deps)

    def has_node(self, node: str) -> bool:
        """True iff ``node`` is a member of the composition graph."""
        return node in self._deps

    def nodes(self) -> tuple[str, ...]:
        """Every universe id, in stable sorted order."""
        return tuple(sorted(self._deps))

    # -- edge / neighbour queries ---------------------------------------------

    def dependencies_of(self, node: str) -> tuple[str, ...]:
        """The direct dependencies of ``node`` (its out-edges), sorted."""
        self._require(node)
        return self._deps[node]

    def dependents_of(self, node: str) -> tuple[str, ...]:
        """The universes that directly depend on ``node`` (its in-edges), sorted."""
        self._require(node)
        return self._dependents[node]

    def roots(self) -> tuple[str, ...]:
        """Universes that depend on nothing (composition entry points), sorted."""
        return tuple(sorted(n for n, out in self._deps.items() if not out))

    def leaves(self) -> tuple[str, ...]:
        """Universes that nothing depends on (composition terminals), sorted."""
        return tuple(sorted(n for n, d in self._dependents.items() if not d))

    def edges(self) -> tuple[tuple[str, str], ...]:
        """Every ``(universe, dependency)`` edge, in stable sorted order."""
        pairs = [(n, dep) for n, out in self._deps.items() for dep in out]
        return tuple(sorted(pairs))

    # -- ordering / layering ---------------------------------------------------

    def order(self) -> tuple[str, ...]:
        """The deterministic compile order: a node's dependencies precede it."""
        return self._order

    def depth(self, node: str) -> int:
        """The dependency depth of ``node`` (0 for a root)."""
        self._require(node)
        return self._depth[node]

    def levels(self) -> tuple[tuple[str, ...], ...]:
        """Universes grouped by dependency depth (level 0 = roots first).

        Each level contains universes whose dependencies are all satisfied by
        earlier levels; the members of a level are mutually independent and are
        returned sorted. Used to derive concurrent coordination (RUNTIME-013 §D9).
        """
        if not self._depth:
            return ()
        max_depth = max(self._depth.values())
        buckets: list[list[str]] = [[] for _ in range(max_depth + 1)]
        for node, d in self._depth.items():
            buckets[d].append(node)
        return tuple(tuple(sorted(bucket)) for bucket in buckets)

    # -- helpers ---------------------------------------------------------------

    def _require(self, node: str) -> None:
        if node not in self._deps:
            raise RuntimeGraphError("unknown universe id", universe_id=node)

    def to_dict(self) -> dict[str, object]:
        """A deterministic, JSON-serialisable view of the graph."""
        return {
            "edge_type": DEPENDS_ON,
            "nodes": list(self.nodes()),
            "edges": [{"universe": u, "depends_on": d} for u, d in self.edges()],
            "order": list(self._order),
            "roots": list(self.roots()),
            "leaves": list(self.leaves()),
        }


__all__ = ["RuntimeGraph", "DEPENDS_ON"]
