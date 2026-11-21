"""UCOS-EPIC-010 (Terminal T2) — deterministic higher-order graph algorithms.

Dependency-free, deterministic algorithms that the Architecture Intelligence
engines build on but which the certified EPIC-002 :mod:`engine.graph.queries`
substrate does not provide:

    * :func:`strongly_connected_components` — **all** maximal cycles via an
      iterative (stack-safe) Tarjan, so *every* circular dependency is surfaced
      (EPIC-002 ``find_cycle`` returns only one).
    * :func:`condensation` — the acyclic condensation (SCC-DAG): each SCC becomes
      one super-node, so critical-path / longest-path analysis is well-defined
      even when Registry Truth contains a genuine cycle (UMB-007 §5).
    * :func:`longest_paths` — node-weighted longest-path DP over a DAG (the
      critical-path substrate) with deterministic tie-breaking.

Every routine visits nodes and neighbours in sorted immutable-identifier order and
returns results in a canonical order, so output is byte-reproducible (determinism
gate). Nothing here mutates the graph or the corpus (DP-03).

The algorithms operate on a plain, pre-materialised adjacency mapping
(``dict[str, tuple[str, ...]]``) rather than a :class:`KnowledgeGraph` directly, so
they are reusable across every projected relation family (dependency, capability,
layer, impact) without coupling to a specific edge type.
"""

from __future__ import annotations

from collections.abc import Mapping

#: A deterministic adjacency mapping: node id -> sorted, de-duplicated successors.
Adjacency = Mapping[str, tuple[str, ...]]


def normalise_adjacency(nodes: object, edges: object) -> dict[str, tuple[str, ...]]:
    """Build a canonical adjacency mapping from ``nodes`` and directed ``edges``.

    ``nodes`` is any iterable of node identifiers; ``edges`` is any iterable of
    ``(source, target)`` pairs. Every node appears as a key (isolated nodes map to
    an empty tuple), successors are sorted and de-duplicated, and edges whose
    endpoints are not in ``nodes`` are ignored. The result is deterministic.
    """
    node_set = set(nodes)  # type: ignore[arg-type]
    succ: dict[str, set[str]] = {n: set() for n in node_set}
    for source, target in edges:  # type: ignore[misc]
        if source in node_set and target in node_set and source != target:
            succ[source].add(target)
    return {n: tuple(sorted(succ[n])) for n in sorted(node_set)}


def strongly_connected_components(adjacency: Adjacency) -> tuple[tuple[str, ...], ...]:
    """Return every strongly-connected component via iterative Tarjan.

    Each component is returned as a tuple of node ids sorted by identifier, and the
    components are ordered by their smallest member id, so the whole result is
    deterministic and independent of traversal order. Every node — including
    singletons — appears in exactly one component.
    """
    index_of: dict[str, int] = {}
    low_of: dict[str, int] = {}
    on_stack: set[str] = set()
    stack: list[str] = []
    components: list[tuple[str, ...]] = []
    counter = 0

    for root in sorted(adjacency):
        if root in index_of:
            continue
        # Iterative DFS frame: (node, next-successor-index).
        work: list[tuple[str, int]] = [(root, 0)]
        while work:
            node, next_idx = work[-1]
            if next_idx == 0:
                index_of[node] = counter
                low_of[node] = counter
                counter += 1
                stack.append(node)
                on_stack.add(node)
            successors = adjacency.get(node, ())
            advanced = False
            for i in range(next_idx, len(successors)):
                child = successors[i]
                if child not in adjacency:
                    continue
                if child not in index_of:
                    work[-1] = (node, i + 1)
                    work.append((child, 0))
                    advanced = True
                    break
                if child in on_stack:
                    low_of[node] = min(low_of[node], index_of[child])
            if advanced:
                continue
            # All successors processed: settle this node.
            if low_of[node] == index_of[node]:
                member: list[str] = []
                while True:
                    w = stack.pop()
                    on_stack.discard(w)
                    member.append(w)
                    if w == node:
                        break
                components.append(tuple(sorted(member)))
            work.pop()
            if work:
                parent = work[-1][0]
                low_of[parent] = min(low_of[parent], low_of[node])

    components.sort(key=lambda comp: comp[0])
    return tuple(components)


def cyclic_components(adjacency: Adjacency) -> tuple[tuple[str, ...], ...]:
    """Return only the *non-trivial* SCCs — the genuine circular dependencies.

    A component is circular if it has more than one member, or a single member with
    a self-loop. Singletons without a self-loop (the common, healthy case) are
    excluded. Deterministic (ordered by smallest member id).
    """
    result: list[tuple[str, ...]] = []
    for comp in strongly_connected_components(adjacency):
        if len(comp) > 1:
            result.append(comp)
        elif len(comp) == 1 and comp[0] in adjacency.get(comp[0], ()):
            result.append(comp)
    return tuple(result)


def condensation(
    adjacency: Adjacency,
) -> tuple[dict[str, tuple[str, ...]], dict[str, str], dict[str, tuple[str, ...]]]:
    """Return the acyclic condensation (SCC-DAG) of ``adjacency``.

    Returns a triple ``(dag, member_of, members)`` where:

        * ``dag`` maps each component-id to its sorted successor component-ids
          (self-edges from intra-component links are dropped, so ``dag`` is a DAG);
        * ``member_of`` maps every original node id to its component-id;
        * ``members`` maps every component-id to its sorted member node ids.

    A component-id is the smallest member identifier prefixed with ``SCC::`` so it
    can never collide with a real node id. Deterministic.
    """
    comps = strongly_connected_components(adjacency)
    member_of: dict[str, str] = {}
    members: dict[str, tuple[str, ...]] = {}
    for comp in comps:
        comp_id = "SCC::" + comp[0]
        members[comp_id] = comp
        for node in comp:
            member_of[node] = comp_id

    dag_sets: dict[str, set[str]] = {cid: set() for cid in members}
    for source, targets in adjacency.items():
        src_comp = member_of.get(source)
        if src_comp is None:
            continue
        for target in targets:
            dst_comp = member_of.get(target)
            if dst_comp is not None and dst_comp != src_comp:
                dag_sets[src_comp].add(dst_comp)
    dag = {cid: tuple(sorted(dag_sets[cid])) for cid in sorted(dag_sets)}
    return dag, member_of, members


def topological_order(adjacency: Adjacency) -> tuple[str, ...]:
    """Deterministic Kahn topological order over a DAG adjacency.

    Raises:
        ValueError: the adjacency contains a directed cycle (not a DAG). Use
            :func:`condensation` first for graphs that may contain cycles.
    """
    indeg: dict[str, int] = {n: 0 for n in adjacency}
    for _, targets in adjacency.items():
        for target in targets:
            if target in indeg:
                indeg[target] += 1
    ready = sorted(n for n in adjacency if indeg[n] == 0)
    order: list[str] = []
    while ready:
        current = ready.pop(0)
        order.append(current)
        for nxt in adjacency.get(current, ()):
            if nxt not in indeg:
                continue
            indeg[nxt] -= 1
            if indeg[nxt] == 0:
                _insert_sorted(ready, nxt)
    if len(order) != len(adjacency):
        raise ValueError("adjacency is not a DAG (contains a directed cycle)")
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


def longest_paths(
    adjacency: Adjacency, *, weights: Mapping[str, int] | None = None
) -> tuple[dict[str, int], dict[str, str | None]]:
    """Node-weighted longest-path DP over a DAG.

    Returns ``(dist, nxt)`` where ``dist[n]`` is the maximum total node-weight of any
    path starting at ``n`` (inclusive) and ``nxt[n]`` is the successor on that
    maximal path (``None`` at a path end). Default weight is 1 per node, so ``dist``
    counts nodes on the longest downstream chain. Ties break on the smallest
    successor id, so the recovered path is deterministic.

    Raises:
        ValueError: ``adjacency`` is not a DAG.
    """
    order = topological_order(adjacency)

    def weight_of(n: str) -> int:
        return int(weights[n]) if weights and n in weights else 1

    dist: dict[str, int] = {}
    nxt: dict[str, str | None] = {}
    # Process in reverse topological order so successors are settled first.
    for node in reversed(order):
        best_total = weight_of(node)
        best_next: str | None = None
        for child in adjacency.get(node, ()):
            if child not in dist:
                continue
            candidate = weight_of(node) + dist[child]
            if candidate > best_total or (candidate == best_total and best_next is None):
                best_total = candidate
                best_next = child
        dist[node] = best_total
        nxt[node] = best_next
    return dist, nxt


def reconstruct_path(nxt: Mapping[str, str | None], start: str) -> tuple[str, ...]:
    """Rebuild the longest path from ``start`` using a ``nxt`` map from
    :func:`longest_paths`. Guards against accidental repetition (defensive)."""
    path: list[str] = []
    seen: set[str] = set()
    current: str | None = start
    while current is not None and current not in seen:
        path.append(current)
        seen.add(current)
        current = nxt.get(current)
    return tuple(path)


__all__ = [
    "Adjacency",
    "normalise_adjacency",
    "strongly_connected_components",
    "cyclic_components",
    "condensation",
    "topological_order",
    "longest_paths",
    "reconstruct_path",
]
