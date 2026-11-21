"""UCOS-EPIC-014 — The Repository Graph (Terminal T5).

One immutable, content-addressed graph over everything discovery found: code roots
*contain* capabilities, capabilities *import* one another, and capabilities *publish*
console scripts. The graph is the subsystem's central artefact — the mission's "produce
dependency graph" deliverable — and every projection over it
(:meth:`RepositoryGraph.topological_layers`, :meth:`RepositoryGraph.cycles`,
:meth:`RepositoryGraph.impact_of`) is a pure function of its nodes and edges.

Edge direction is uniform and load-bearing: **source depends on target**. Consequently
layer 0 of :meth:`topological_layers` is the foundation (nodes that depend on nothing) and
later layers compose earlier ones, which is the same bottom-up reading the repository's own
architecture ladder uses.

Boundary: this is the *code-substrate* graph. The corpus artifact→artifact relationship
graph is owned by :mod:`engine.graph` and the program-rollup graph by UCOS-RIE-001; neither
is re-derived here, and the three answer different questions over different node universes.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field
from platform.foundation.contracts import content_hash
from platform.repository_intelligence.contracts import (
    DEPENDENCY_GRAPH_FORMAT,
    DependencyEdge,
    EdgeKind,
    RepositoryUnit,
    UnitKind,
)
from platform.repository_intelligence.errors import GraphError
from typing import Any


def strongly_connected_components(
    edges: tuple[DependencyEdge, ...],
) -> tuple[tuple[str, ...], ...]:
    """Return the cyclic strongly connected components (size > 1) of ``edges``.

    Iterative Tarjan, so a deep graph cannot exhaust the recursion limit, with every
    neighbour list and every emitted component sorted — identical edges always yield
    identical components. This is the single cycle detector in the subsystem; the
    dependency dimension and the graph both call it rather than each carrying its own.
    """
    adjacency: dict[str, list[str]] = {}
    for edge in edges:
        adjacency.setdefault(edge.source, []).append(edge.target)
        adjacency.setdefault(edge.target, [])
    for node in adjacency:
        adjacency[node] = sorted(adjacency[node])

    index: dict[str, int] = {}
    low: dict[str, int] = {}
    on_stack: set[str] = set()
    stack: list[str] = []
    counter = 0
    components: list[tuple[str, ...]] = []

    for start in sorted(adjacency):
        if start in index:
            continue
        work: list[tuple[str, int]] = [(start, 0)]
        while work:
            node, child = work[-1]
            if child == 0:
                index[node] = low[node] = counter
                counter += 1
                stack.append(node)
                on_stack.add(node)
            neighbours = adjacency[node]
            if child < len(neighbours):
                work[-1] = (node, child + 1)
                target = neighbours[child]
                if target not in index:
                    work.append((target, 0))
                elif target in on_stack:
                    low[node] = min(low[node], index[target])
                continue
            work.pop()
            if work:
                parent = work[-1][0]
                low[parent] = min(low[parent], low[node])
            if low[node] == index[node]:
                component: list[str] = []
                while True:
                    member = stack.pop()
                    on_stack.discard(member)
                    component.append(member)
                    if member == node:
                        break
                if len(component) > 1:
                    components.append(tuple(sorted(component)))
    return tuple(sorted(components))


@dataclass(frozen=True, slots=True)
class GraphNode:
    """A node of the repository graph: a root, a capability, a zone, or an entry point."""

    node_id: str
    kind: UnitKind
    location: str = ""
    loc: int = 0
    tracked_files: int = 0
    label: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.node_id,
            "kind": self.kind.value,
            "location": self.location,
            "loc": self.loc,
            "tracked_files": self.tracked_files,
            "label": self.label,
        }


@dataclass(frozen=True, slots=True)
class RepositoryGraph:
    """The immutable, content-addressed repository dependency graph."""

    nodes: tuple[GraphNode, ...] = ()
    edges: tuple[DependencyEdge, ...] = ()
    _index: Mapping[str, GraphNode] = field(default_factory=dict, repr=False, compare=False)

    # -- construction ----------------------------------------------------
    @classmethod
    def create(
        cls, nodes: tuple[GraphNode, ...], edges: tuple[DependencyEdge, ...]
    ) -> RepositoryGraph:
        """Build a validated graph with deterministically ordered nodes and edges.

        Raises:
            GraphError: on a duplicate node identity, or an edge whose endpoint is not a
                node — a malformed graph must fail loudly rather than silently drop facts.
        """
        ordered_nodes = tuple(sorted(nodes, key=lambda n: (n.kind.value, n.node_id)))
        index: dict[str, GraphNode] = {}
        for node in ordered_nodes:
            if node.node_id in index:
                raise GraphError("duplicate node identity in repository graph", node=node.node_id)
            index[node.node_id] = node
        ordered_edges = tuple(sorted(edges, key=lambda e: (e.kind.value, e.source, e.target)))
        for edge in ordered_edges:
            for endpoint in (edge.source, edge.target):
                if endpoint not in index:
                    raise GraphError(
                        "repository graph edge references an unknown node",
                        edge=f"{edge.source} -> {edge.target}",
                        unknown=endpoint,
                    )
        return cls(nodes=ordered_nodes, edges=ordered_edges, _index=index)

    def node(self, node_id: str) -> GraphNode:
        """Return the node with ``node_id``.

        Raises:
            GraphError: if no such node exists.
        """
        node = self._index.get(node_id) or next(
            (n for n in self.nodes if n.node_id == node_id), None
        )
        if node is None:
            raise GraphError("unknown repository graph node", node=node_id)
        return node

    def node_ids(self) -> tuple[str, ...]:
        return tuple(n.node_id for n in self.nodes)

    # -- projections -----------------------------------------------------
    def dependency_edges(self) -> tuple[DependencyEdge, ...]:
        """Only the ``imports`` edges (the dependency relation proper)."""
        return tuple(e for e in self.edges if e.kind is EdgeKind.IMPORTS)

    def adjacency(self, kind: EdgeKind = EdgeKind.IMPORTS) -> dict[str, tuple[str, ...]]:
        """``node -> nodes it depends on``, for every node (isolated nodes included)."""
        out: dict[str, set[str]] = {n.node_id: set() for n in self.nodes}
        for edge in self.edges:
            if edge.kind is kind:
                out[edge.source].add(edge.target)
        return {node: tuple(sorted(targets)) for node, targets in sorted(out.items())}

    def reverse_adjacency(self, kind: EdgeKind = EdgeKind.IMPORTS) -> dict[str, tuple[str, ...]]:
        """``node -> nodes that depend on it`` (the dependents relation)."""
        out: dict[str, set[str]] = {n.node_id: set() for n in self.nodes}
        for edge in self.edges:
            if edge.kind is kind:
                out[edge.target].add(edge.source)
        return {node: tuple(sorted(sources)) for node, sources in sorted(out.items())}

    def out_degree(self) -> dict[str, int]:
        return {node: len(targets) for node, targets in self.adjacency().items()}

    def in_degree(self) -> dict[str, int]:
        return {node: len(sources) for node, sources in self.reverse_adjacency().items()}

    def foundations(self) -> tuple[str, ...]:
        """Capabilities that depend on nothing and are depended upon (reuse bedrock)."""
        out, into = self.adjacency(), self.reverse_adjacency()
        return tuple(
            node
            for node in sorted(out)
            if not out[node] and into[node] and self._is_capability(node)
        )

    def leaves(self) -> tuple[str, ...]:
        """Capabilities nothing depends on (the top of the composition order)."""
        out, into = self.adjacency(), self.reverse_adjacency()
        return tuple(
            node
            for node in sorted(out)
            if not into[node] and out[node] and self._is_capability(node)
        )

    def isolated(self) -> tuple[str, ...]:
        """Capabilities with no dependency edges at all in either direction."""
        out, into = self.adjacency(), self.reverse_adjacency()
        return tuple(
            node
            for node in sorted(out)
            if not out[node] and not into[node] and self._is_capability(node)
        )

    def _is_capability(self, node_id: str) -> bool:
        node = self._index.get(node_id)
        return node is not None and node.kind is UnitKind.CODE_CAPABILITY

    # -- topology --------------------------------------------------------
    def cycles(self) -> tuple[tuple[str, ...], ...]:
        """Strongly connected components of size > 1, deterministically ordered."""
        return strongly_connected_components(self.dependency_edges())

    def topological_layers(self) -> tuple[tuple[str, ...], ...]:
        """Layer the capability dependency graph bottom-up.

        Layer 0 depends on nothing. A capability joins layer *n* once every capability it
        depends on sits in a layer below *n*. When a cycle exists, the capabilities in it —
        **and every capability that depends on one, directly or transitively** — cannot be
        ordered at all; they are returned together as a final, explicitly unorderable layer
        rather than being silently dropped. The graph reports what it cannot order.
        """
        adjacency = self.adjacency()
        capability_nodes = {n for n in adjacency if self._is_capability(n)}
        remaining = {
            node: {t for t in targets if t in capability_nodes}
            for node, targets in adjacency.items()
            if node in capability_nodes
        }
        placed: set[str] = set()
        layers: list[tuple[str, ...]] = []
        while remaining:
            ready = tuple(sorted(node for node, deps in remaining.items() if deps <= placed))
            if not ready:
                layers.append(tuple(sorted(remaining)))
                break
            layers.append(ready)
            placed.update(ready)
            for node in ready:
                del remaining[node]
        return tuple(layers)

    def unorderable(self) -> tuple[str, ...]:
        """Capabilities that cannot be layered because a cycle blocks their ordering."""
        if not self.cycles():
            return ()
        layers = self.topological_layers()
        return layers[-1] if layers else ()

    def layer_of(self) -> dict[str, int]:
        """``capability -> layer index`` from :meth:`topological_layers`."""
        return {
            node: index for index, layer in enumerate(self.topological_layers()) for node in layer
        }

    def dependencies_of(self, node_id: str, depth: int | None = None) -> tuple[str, ...]:
        """Transitive closure of what ``node_id`` depends on (breadth-first, bounded)."""
        return self._closure(node_id, self.adjacency(), depth)

    def dependents_of(self, node_id: str, depth: int | None = None) -> tuple[str, ...]:
        """Transitive closure of what depends on ``node_id`` (the blast radius)."""
        return self._closure(node_id, self.reverse_adjacency(), depth)

    def _closure(
        self, node_id: str, relation: dict[str, tuple[str, ...]], depth: int | None
    ) -> tuple[str, ...]:
        self.node(node_id)
        seen: set[str] = set()
        frontier = [node_id]
        level = 0
        while frontier and (depth is None or level < depth):
            nxt: list[str] = []
            for current in frontier:
                for neighbour in relation.get(current, ()):
                    if neighbour not in seen and neighbour != node_id:
                        seen.add(neighbour)
                        nxt.append(neighbour)
            frontier = nxt
            level += 1
        return tuple(sorted(seen))

    def impact_of(self, node_id: str) -> dict[str, Any]:
        """The change-impact profile of one capability (what breaks if it changes)."""
        node = self.node(node_id)
        dependents = self.dependents_of(node_id)
        dependencies = self.dependencies_of(node_id)
        return {
            "node": node_id,
            "kind": node.kind.value,
            "direct_dependents": list(self.reverse_adjacency().get(node_id, ())),
            "direct_dependencies": list(self.adjacency().get(node_id, ())),
            "transitive_dependents": list(dependents),
            "transitive_dependencies": list(dependencies),
            "blast_radius": len(dependents),
            "layer": self.layer_of().get(node_id),
        }

    def most_depended_upon(self, limit: int = 10) -> tuple[dict[str, Any], ...]:
        """The capabilities the most other capabilities depend on (the true reuse core)."""
        into = self.reverse_adjacency()
        ranked = sorted(
            (
                {"node": node, "dependents": len(sources)}
                for node, sources in into.items()
                if self._is_capability(node) and sources
            ),
            key=lambda row: (-int(row["dependents"]), str(row["node"])),
        )
        return tuple(ranked[:limit])

    # -- identity + serialization ---------------------------------------
    def core(self) -> dict[str, Any]:
        return {
            "nodes": [n.to_dict() for n in self.nodes],
            "edges": [e.to_dict() for e in self.edges],
        }

    def digest(self) -> str:
        """The deterministic content digest of the graph."""
        return content_hash(self.core())

    def to_dict(self) -> dict[str, Any]:
        layers = self.topological_layers()
        cycles = self.cycles()
        return {
            "graph_format": DEPENDENCY_GRAPH_FORMAT,
            "graph_digest": self.digest(),
            "counts": {
                "nodes": len(self.nodes),
                "edges": len(self.edges),
                "dependency_edges": len(self.dependency_edges()),
                "layers": len(layers),
                "cycles": len(cycles),
            },
            "nodes": [n.to_dict() for n in self.nodes],
            "edges": [e.to_dict() for e in self.edges],
            "acyclic": not cycles,
            "cycles": [list(cycle) for cycle in cycles],
            "topological_layers": [list(layer) for layer in layers],
            "unorderable": list(self.unorderable()),
            "foundations": list(self.foundations()),
            "leaves": list(self.leaves()),
            "isolated": list(self.isolated()),
            "most_depended_upon": [dict(row) for row in self.most_depended_upon()],
        }

    def to_dot(self) -> str:
        """Render the dependency graph as deterministic Graphviz DOT."""
        lines = [
            "digraph repository_dependencies {",
            "  rankdir=BT;",
            '  node [shape=box, fontname="monospace"];',
        ]
        for node in self.nodes:
            if node.kind is not UnitKind.CODE_CAPABILITY:
                continue
            lines.append(f'  "{node.node_id}" [label="{node.node_id}\\n{node.loc} LOC"];')
        for edge in self.dependency_edges():
            lines.append(f'  "{edge.source}" -> "{edge.target}" [label="{edge.weight}"];')
        lines.append("}")
        return "\n".join(lines) + "\n"

    def to_mermaid(self) -> str:
        """Render the dependency graph as a deterministic Mermaid flowchart."""
        alias = {node.node_id: f"n{index}" for index, node in enumerate(self.nodes)}
        lines = ["flowchart BT"]
        for node in self.nodes:
            if node.kind is not UnitKind.CODE_CAPABILITY:
                continue
            lines.append(f'  {alias[node.node_id]}["{node.node_id}"]')
        for edge in self.dependency_edges():
            lines.append(f"  {alias[edge.source]} --> {alias[edge.target]}")
        return "\n".join(lines) + "\n"


def build_graph(
    units: tuple[RepositoryUnit, ...], edges: tuple[DependencyEdge, ...]
) -> RepositoryGraph:
    """Assemble the repository graph from discovered units and dependency edges.

    Adds the structural edges the unit inventory implies — a code root *contains* its
    capabilities, and a capability *publishes* the console scripts whose target resolves
    into it — so the graph is a single connected model rather than an import graph beside
    a loose inventory. Dependency edges whose endpoints are not discovered capabilities are
    dropped, keeping the graph closed under its own node set.
    """
    nodes: list[GraphNode] = []
    for unit in units:
        nodes.append(
            GraphNode(
                node_id=unit.name,
                kind=unit.kind,
                location=unit.location,
                loc=unit.loc,
                tracked_files=unit.tracked_files,
                label=unit.detail,
            )
        )
    known = {node.node_id for node in nodes}
    capabilities = {u.name for u in units if u.kind is UnitKind.CODE_CAPABILITY}
    roots = {u.name for u in units if u.kind is UnitKind.CODE_ROOT}

    structural: list[DependencyEdge] = []
    for capability in sorted(capabilities):
        root = capability.split(".", 1)[0]
        if root in roots:
            structural.append(
                DependencyEdge(source=root, target=capability, kind=EdgeKind.CONTAINS)
            )
    for unit in units:
        if unit.kind is not UnitKind.ENTRY_POINT:
            continue
        module = unit.location.split(":", 1)[0]
        owner = _longest_prefix(module, capabilities)
        if owner:
            structural.append(
                DependencyEdge(source=owner, target=unit.name, kind=EdgeKind.PUBLISHES)
            )
    dependency = tuple(edge for edge in edges if edge.source in known and edge.target in known)
    return RepositoryGraph.create(tuple(nodes), (*dependency, *structural))


def _longest_prefix(module: str, candidates: set[str]) -> str | None:
    """The longest candidate that is a dotted prefix of ``module`` (or equal to it)."""
    parts = module.split(".")
    for cut in range(len(parts), 0, -1):
        candidate = ".".join(parts[:cut])
        if candidate in candidates:
            return candidate
    return None


__all__ = ["strongly_connected_components", "GraphNode", "RepositoryGraph", "build_graph"]
