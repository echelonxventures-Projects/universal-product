"""UCOS-EPIC-002 (Terminal T2) — Universal Knowledge Graph query algorithms.

Deterministic, dependency-free graph algorithms over the read-only
:class:`~engine.graph.model.KnowledgeGraph`. Every traversal visits neighbours in
sorted identifier order so results are reproducible (determinism gate). Nothing
here mutates the graph or the corpus (DP-03).

The algorithms are the shared substrate for the ten graph projections and the
query CLI: reachability, transitive closure (forward/reverse), shortest path,
topological ordering, and cycle detection.
"""

from __future__ import annotations

from collections import deque
from collections.abc import Iterable

from engine.graph.model import KnowledgeGraph


def _adjacent(
    graph: KnowledgeGraph, node_id: str, *, inbound: bool, types: frozenset[str] | None
) -> list[str]:
    """Return sorted, de-duplicated neighbours of ``node_id`` for a traversal."""
    edges = graph.edges_to(node_id) if inbound else graph.edges_from(node_id)
    out: set[str] = set()
    for edge in edges:
        if types is not None and edge.type not in types:
            continue
        out.add(edge.source if inbound else edge.target)
    return sorted(out)


def breadth_first(
    graph: KnowledgeGraph,
    start: str,
    *,
    inbound: bool = False,
    types: Iterable[str] | None = None,
) -> tuple[str, ...]:
    """Deterministic BFS order from ``start`` (excluding ``start`` itself)."""
    type_set = frozenset(types) if types is not None else None
    order: list[str] = []
    visited = {start}
    queue: deque[str] = deque([start])
    while queue:
        current = queue.popleft()
        for nxt in _adjacent(graph, current, inbound=inbound, types=type_set):
            if nxt not in visited:
                visited.add(nxt)
                order.append(nxt)
                queue.append(nxt)
    return tuple(order)


def transitive_closure(
    graph: KnowledgeGraph,
    start: str,
    *,
    inbound: bool = False,
    types: Iterable[str] | None = None,
) -> tuple[str, ...]:
    """Every node (transitively) reachable from ``start`` (BFS closure)."""
    return breadth_first(graph, start, inbound=inbound, types=types)


def descendants(
    graph: KnowledgeGraph, start: str, *, types: Iterable[str] | None = None
) -> tuple[str, ...]:
    """Transitive outbound closure — everything ``start`` (transitively) points at."""
    return transitive_closure(graph, start, inbound=False, types=types)


def ancestors(
    graph: KnowledgeGraph, start: str, *, types: Iterable[str] | None = None
) -> tuple[str, ...]:
    """Transitive inbound closure — everything that (transitively) points at ``start``."""
    return transitive_closure(graph, start, inbound=True, types=types)


def shortest_path(
    graph: KnowledgeGraph,
    start: str,
    goal: str,
    *,
    inbound: bool = False,
    types: Iterable[str] | None = None,
) -> tuple[str, ...]:
    """Return a shortest node path ``start -> ... -> goal`` (empty if unreachable).

    Ties are broken by sorted identifier order, so the path is deterministic. The
    returned tuple includes both endpoints; an empty tuple means no path exists.
    """
    if start == goal:
        return (start,)
    type_set = frozenset(types) if types is not None else None
    prev: dict[str, str] = {}
    visited = {start}
    queue: deque[str] = deque([start])
    while queue:
        current = queue.popleft()
        for nxt in _adjacent(graph, current, inbound=inbound, types=type_set):
            if nxt in visited:
                continue
            visited.add(nxt)
            prev[nxt] = current
            if nxt == goal:
                return _reconstruct(prev, start, goal)
            queue.append(nxt)
    return ()


def _reconstruct(prev: dict[str, str], start: str, goal: str) -> tuple[str, ...]:
    path = [goal]
    while path[-1] != start:
        path.append(prev[path[-1]])
    return tuple(reversed(path))


def has_path(
    graph: KnowledgeGraph,
    start: str,
    goal: str,
    *,
    inbound: bool = False,
    types: Iterable[str] | None = None,
) -> bool:
    """True iff ``goal`` is reachable from ``start`` over the filtered edges."""
    return bool(shortest_path(graph, start, goal, inbound=inbound, types=types))


def topological_order(
    graph: KnowledgeGraph, *, types: Iterable[str] | None = None
) -> tuple[str, ...]:
    """Deterministic Kahn topological order over the (optionally filtered) DAG.

    Raises:
        ValueError: the filtered graph contains a cycle (not a DAG).
    """
    type_set = frozenset(types) if types is not None else None
    nodes = list(graph.node_ids())
    indeg: dict[str, int] = {n: 0 for n in nodes}
    succ: dict[str, list[str]] = {n: [] for n in nodes}
    for edge in graph.edges():
        if type_set is not None and edge.type not in type_set:
            continue
        if edge.source not in indeg or edge.target not in indeg:
            continue
        succ[edge.source].append(edge.target)
        indeg[edge.target] += 1

    ready = sorted(n for n in nodes if indeg[n] == 0)
    order: list[str] = []
    while ready:
        current = ready.pop(0)
        order.append(current)
        for nxt in sorted(set(succ[current])):
            indeg[nxt] -= 1
            if indeg[nxt] == 0:
                # keep the ready list sorted for determinism
                _insert_sorted(ready, nxt)
    if len(order) != len(nodes):
        raise ValueError("graph is not a DAG under the given edge-type filter")
    return tuple(order)


def _insert_sorted(items: list[str], value: str) -> None:
    lo, hi = 0, len(items)
    while lo < hi:
        mid = (lo + hi) // 2
        if items[mid] < value:
            lo = mid + 1
        else:
            hi = mid
    items.insert(lo, value)


def is_acyclic(graph: KnowledgeGraph, *, types: Iterable[str] | None = None) -> bool:
    """True iff the (optionally filtered) graph has no directed cycle."""
    try:
        topological_order(graph, types=types)
    except ValueError:
        return False
    return True


def find_cycle(graph: KnowledgeGraph, *, types: Iterable[str] | None = None) -> tuple[str, ...]:
    """Return one directed cycle as a node path, or an empty tuple if acyclic.

    Uses an iterative colour DFS (WHITE/GREY/BLACK) with sorted successors so the
    returned cycle is deterministic.
    """
    type_set = frozenset(types) if types is not None else None
    succ: dict[str, list[str]] = {}
    for node_id in graph.node_ids():
        succ[node_id] = _adjacent(graph, node_id, inbound=False, types=type_set)

    WHITE, GREY, BLACK = 0, 1, 2
    colour: dict[str, int] = {n: WHITE for n in succ}
    parent: dict[str, str] = {}

    for root in sorted(succ):
        if colour[root] != WHITE:
            continue
        stack: list[tuple[str, int]] = [(root, 0)]
        colour[root] = GREY
        while stack:
            node_id, idx = stack[-1]
            children = succ[node_id]
            if idx < len(children):
                stack[-1] = (node_id, idx + 1)
                child = children[idx]
                if child not in colour:
                    continue
                if colour[child] == WHITE:
                    colour[child] = GREY
                    parent[child] = node_id
                    stack.append((child, 0))
                elif colour[child] == GREY:
                    return _extract_cycle(parent, node_id, child)
            else:
                colour[node_id] = BLACK
                stack.pop()
    return ()


def _extract_cycle(parent: dict[str, str], tail: str, head: str) -> tuple[str, ...]:
    """Rebuild the cycle head -> ... -> tail -> head from the DFS parent map."""
    path = [tail]
    while path[-1] != head:
        path.append(parent[path[-1]])
    path.reverse()
    path.append(head)
    return tuple(path)


def connected_component(graph: KnowledgeGraph, start: str) -> tuple[str, ...]:
    """The weakly-connected component containing ``start`` (undirected reach)."""
    visited = {start}
    queue: deque[str] = deque([start])
    while queue:
        current = queue.popleft()
        for nxt in sorted(set(graph.neighbors(current))):
            if nxt not in visited:
                visited.add(nxt)
                queue.append(nxt)
    return tuple(sorted(visited))


__all__ = [
    "breadth_first",
    "transitive_closure",
    "descendants",
    "ancestors",
    "shortest_path",
    "has_path",
    "topological_order",
    "is_acyclic",
    "find_cycle",
    "connected_component",
]
