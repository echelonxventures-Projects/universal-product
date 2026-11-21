"""TASK-000022 — Cycle detection (EPIC-003, IMP-007 §4/§17).

Circular dependencies **SHALL FAIL** the build (AR-01). This module provides the
pure graph primitives the Dependency Resolution Engine (TASK-000021) uses to
guarantee an acyclic, single-direction dependency graph:

    * :func:`detect_cycle` — return the first cycle found (a node path) or ``None``;
    * :func:`assert_acyclic` — raise :class:`CyclicDependencyError` on any cycle;
    * :func:`topological_order` — a deterministic topological ordering, raising on
      a cycle.

All traversal is deterministic (nodes and edges are visited in sorted order), so
identical graphs yield identical results and identical cycle reports
(reproducibility, IMP-007 §5). Pure, stdlib-only, side-effect free.
"""

from __future__ import annotations

from collections.abc import Iterable, Mapping

from engine.compiler.errors import CyclicDependencyError

# A dependency graph maps a node to the nodes it depends on (its out-edges).
Graph = Mapping[str, Iterable[str]]


def _normalized(graph: Graph) -> dict[str, tuple[str, ...]]:
    """Return a graph with every referenced node present and edges sorted."""
    normalized: dict[str, list[str]] = {node: [] for node in graph}
    for node, edges in graph.items():
        for edge in edges:
            normalized.setdefault(edge, [])
            normalized[node].append(edge)
    return {node: tuple(sorted(edges)) for node, edges in normalized.items()}


def detect_cycle(graph: Graph) -> tuple[str, ...] | None:
    """Return the first dependency cycle as an ordered node path, or ``None``.

    The returned path is closed: its first and last elements are the same node
    (e.g. ``("a", "b", "a")``). Traversal is deterministic (sorted).
    """
    adjacency = _normalized(graph)
    WHITE, GREY, BLACK = 0, 1, 2
    colour: dict[str, int] = dict.fromkeys(adjacency, WHITE)
    stack: list[str] = []

    def visit(node: str) -> tuple[str, ...] | None:
        colour[node] = GREY
        stack.append(node)
        for neighbour in adjacency[node]:
            if colour[neighbour] == GREY:
                # Found a back-edge: close the cycle from the grey ancestor.
                index = stack.index(neighbour)
                return (*stack[index:], neighbour)
            if colour[neighbour] == WHITE:
                found = visit(neighbour)
                if found is not None:
                    return found
        stack.pop()
        colour[node] = BLACK
        return None

    for start in sorted(adjacency):
        if colour[start] == WHITE:
            cycle = visit(start)
            if cycle is not None:
                return cycle
    return None


def assert_acyclic(graph: Graph) -> None:
    """Raise :class:`CyclicDependencyError` if ``graph`` contains any cycle."""
    cycle = detect_cycle(graph)
    if cycle is not None:
        raise CyclicDependencyError(
            "circular dependency detected; the build must fail",
            cycle=list(cycle),
        )


def topological_order(graph: Graph) -> tuple[str, ...]:
    """Return a deterministic topological ordering (dependencies first).

    Uses Kahn's algorithm with deterministic (sorted) node selection. Raises
    :class:`CyclicDependencyError` if the graph is not a DAG.
    """
    adjacency = _normalized(graph)
    indegree: dict[str, int] = dict.fromkeys(adjacency, 0)
    for edges in adjacency.values():
        for edge in edges:
            indegree[edge] += 1

    # Seed with nodes that depend on nothing (indegree 0), sorted for determinism.
    ready = sorted(node for node, degree in indegree.items() if degree == 0)
    order: list[str] = []
    while ready:
        node = ready.pop(0)
        order.append(node)
        for neighbour in adjacency[node]:
            indegree[neighbour] -= 1
            if indegree[neighbour] == 0:
                # Insert preserving sorted order (deterministic).
                _insort(ready, neighbour)

    if len(order) != len(adjacency):
        assert_acyclic(graph)  # raises with the offending cycle
    # Dependencies must appear before dependents: reverse Kahn's (edges are
    # "depends-on"), so a node's dependencies come first.
    return tuple(reversed(order))


def _insort(items: list[str], value: str) -> None:
    """Insert ``value`` into a sorted list, keeping it sorted (deterministic)."""
    low, high = 0, len(items)
    while low < high:
        mid = (low + high) // 2
        if items[mid] < value:
            low = mid + 1
        else:
            high = mid
    items.insert(low, value)


__all__ = ["Graph", "detect_cycle", "assert_acyclic", "topological_order"]
