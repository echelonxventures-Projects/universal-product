"""EC2-TASK-000059 — Platform Dependency Model (EC2-EPIC-001).

A deterministic, acyclic dependency model reused across the foundation: it orders
services for bootstrap, orders capabilities, and can order epics/components. It is a
pure value model (no I/O, no wall-clock) built on a directed graph of declared
dependencies.

Guarantees (IMP-007 §5, AR-01 acyclic):
    * **Deterministic topological order** — nodes are returned in a stable order
      (Kahn's algorithm with a lexicographic tie-break by id), so identical graphs
      always yield identical orderings.
    * **Cycle detection** — a cyclic graph is rejected (AR-01 downward-only).
    * **Closure honesty** — a dependency on an unknown node is rejected (IP-04).
"""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
from platform.foundation.errors import DependencyError
from typing import Any


@dataclass(frozen=True, slots=True)
class DependencyNode:
    """An immutable node: an id plus the ids it depends on."""

    node_id: str
    depends_on: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if not isinstance(self.node_id, str) or not self.node_id:
            raise DependencyError("dependency node id is required")

    def to_dict(self) -> dict[str, Any]:
        return {"node_id": self.node_id, "depends_on": list(self.depends_on)}


class DependencyGraph:
    """A deterministic, acyclic dependency graph over named nodes."""

    __slots__ = ("_nodes",)

    def __init__(self) -> None:
        self._nodes: dict[str, DependencyNode] = {}

    def add(self, node_id: str, depends_on: Iterable[str] = ()) -> DependencyNode:
        """Add a node (idempotent id uniqueness enforced)."""
        if node_id in self._nodes:
            raise DependencyError("duplicate dependency node", node_id=node_id)
        # Deduplicate + sort deps for deterministic structure.
        deps = tuple(sorted(set(depends_on)))
        node = DependencyNode(node_id=node_id, depends_on=deps)
        self._nodes[node_id] = node
        return node

    def __contains__(self, node_id: str) -> bool:
        return node_id in self._nodes

    def __len__(self) -> int:
        return len(self._nodes)

    @property
    def node_ids(self) -> tuple[str, ...]:
        return tuple(sorted(self._nodes))

    def dependencies_of(self, node_id: str) -> tuple[str, ...]:
        self._require(node_id)
        return self._nodes[node_id].depends_on

    def dependents_of(self, node_id: str) -> tuple[str, ...]:
        self._require(node_id)
        return tuple(sorted(n.node_id for n in self._nodes.values() if node_id in n.depends_on))

    def validate(self) -> None:
        """Raise :class:`DependencyError` on any unknown dependency or cycle."""
        for node in self._nodes.values():
            for dep in node.depends_on:
                if dep not in self._nodes:
                    raise DependencyError(
                        "dependency references an unknown node",
                        node_id=node.node_id,
                        missing=dep,
                    )
        # Cycle detection via a full topological sort (raises on cycle).
        self._topological_order()

    def topological_order(self) -> tuple[str, ...]:
        """Return a deterministic topological ordering (dependencies first)."""
        self.validate()
        return self._topological_order()

    def has_cycle(self) -> bool:
        """True iff the graph (with all deps known) contains a cycle."""
        try:
            self.validate()
        except DependencyError as exc:
            # Distinguish a cycle from an unknown-dependency error.
            return "cycle" in exc.message
        return False

    # -- internals -------------------------------------------------------------

    def _require(self, node_id: str) -> None:
        if node_id not in self._nodes:
            raise DependencyError("no such dependency node", node_id=node_id)

    def _topological_order(self) -> tuple[str, ...]:
        indegree = {nid: 0 for nid in self._nodes}
        for node in self._nodes.values():
            for _dep in node.depends_on:
                indegree[node.node_id] += 1
        # Kahn's algorithm; ready set drained in sorted order for determinism.
        ready = sorted(nid for nid, deg in indegree.items() if deg == 0)
        order: list[str] = []
        while ready:
            current = ready.pop(0)
            order.append(current)
            for dependent in self.dependents_of(current):
                indegree[dependent] -= 1
                if indegree[dependent] == 0:
                    # insert maintaining sorted order (deterministic)
                    ready.append(dependent)
                    ready.sort()
        if len(order) != len(self._nodes):
            unresolved = sorted(set(self._nodes) - set(order))
            raise DependencyError("dependency graph contains a cycle", unresolved=unresolved)
        return tuple(order)

    def to_dict(self) -> dict[str, Any]:
        return {
            "node_count": len(self._nodes),
            "nodes": [self._nodes[nid].to_dict() for nid in sorted(self._nodes)],
        }


__all__ = ["DependencyNode", "DependencyGraph"]
