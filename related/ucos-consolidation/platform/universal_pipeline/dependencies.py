"""UAPF-000001 — the Universal Dependency Engine and Universal Relationship Engine.

Dependencies and relationships are the same structure viewed from two ends: an edge
``a → b`` is *a depends on b* read forward and *b impacts a* read backward. Modelling
them once means the dependency graph and the impact graph can never disagree — so this
module holds one edge set and derives both views from it, rather than maintaining a
dependency graph beside a relationship graph that must be reconciled.

No second dependency algorithm
------------------------------
Topology, cycle detection and closure honesty come from
:class:`platform.foundation.dependencies.DependencyGraph` — the repository's existing
deterministic, acyclic dependency model. UAPF adds no traversal of its own and only
translates that model's :class:`~platform.foundation.errors.DependencyError` into its own
domain error so a failure names UAPF's fail-closed contract while the *decision* stays
with the canonical authority.

Declaration order independence
------------------------------
:meth:`DependencyManager.declare` accepts an edge to a node that has not been declared
yet, because requiring declaration order would make a graph's validity depend on the
sequence in which a catalogue happened to be read. Honesty is enforced at *use*:
:meth:`DependencyManager.validate`, :meth:`order` and :meth:`closure` reject an unknown
node and a cycle. So a dangling edge is always caught, and never caught early enough to
forbid a legitimate declaration.

Determinism: every traversal is sorted, so closures, orders, impact sets and fingerprints
are byte-identical across runs. No wall-clock, no RNG, no I/O.
"""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
from platform.foundation.contracts import content_hash
from platform.foundation.dependencies import DependencyGraph
from platform.foundation.errors import DependencyError
from platform.universal_pipeline.errors import PipelineDependencyError
from platform.universal_pipeline.identity import Identity, mint
from typing import Any


@dataclass(frozen=True, slots=True)
class DependencyClosure:
    """The complete, transitive dependency closure of one node.

    ``direct`` is what the node itself declares; ``transitive`` is everything reachable
    through those declarations (excluding the node). ``order`` is a dependency-first
    ordering of the closure *plus* the node, so it is directly executable: satisfying the
    closure in this order never violates a declared edge. ``depth`` is the longest chain
    in the closure — the shortest possible number of sequential steps.
    """

    node_id: str
    direct: tuple[str, ...]
    transitive: tuple[str, ...]
    order: tuple[str, ...]
    depth: int

    def __post_init__(self) -> None:
        if not isinstance(self.node_id, str) or not self.node_id:
            raise PipelineDependencyError("closure node id is required")
        if self.depth < 0:
            raise PipelineDependencyError("closure depth must be non-negative", node=self.node_id)

    @property
    def identity(self) -> Identity:
        return mint("dependency-closure", self.node_id)

    @property
    def is_closed(self) -> bool:
        """True iff every transitive dependency appears in the executable order."""
        return set(self.transitive) <= set(self.order)

    def to_dict(self) -> dict[str, Any]:
        return {
            "node_id": self.node_id,
            "identity": self.identity.value,
            "direct": list(self.direct),
            "transitive": list(self.transitive),
            "order": list(self.order),
            "depth": self.depth,
        }

    def fingerprint(self) -> str:
        return content_hash(self.to_dict())


class DependencyManager:
    """The declared edge set of one platform instance, with derived views over it.

    Holds *declarations* only. Every question — order, closure, impact, cycles — is
    answered by deriving from those declarations through the canonical dependency model,
    so there is nothing to keep in step and nothing that can be stale.
    """

    __slots__ = ("_edges",)

    def __init__(self) -> None:
        # node_id -> the node ids it declares a dependency on (sorted, deduplicated).
        self._edges: dict[str, tuple[str, ...]] = {}

    # -- declaration ------------------------------------------------------------------

    def declare(self, node_id: str, depends_on: Iterable[str] = ()) -> tuple[str, ...]:
        """Declare ``node_id`` and the node ids it depends on; return the resolved edges.

        Edges are deduplicated and sorted, so a declaration's *structure* is independent
        of the order the caller listed it in.

        Raises:
            PipelineDependencyError: if ``node_id`` is not a non-empty string, is already
                declared (a node has exactly one declaration), depends on itself, or any
                edge is not a non-empty string.
        """
        if not isinstance(node_id, str) or not node_id:
            raise PipelineDependencyError("dependency node id is required")
        if node_id in self._edges:
            raise PipelineDependencyError("dependency node already declared", node=node_id)
        resolved = tuple(sorted(set(depends_on)))
        for edge in resolved:
            if not isinstance(edge, str) or not edge:
                raise PipelineDependencyError(
                    "dependency edges must be non-empty strings", node=node_id
                )
        if node_id in resolved:
            raise PipelineDependencyError("a node cannot depend on itself", node=node_id)
        self._edges[node_id] = resolved
        return resolved

    def __contains__(self, node_id: str) -> bool:
        return node_id in self._edges

    def __len__(self) -> int:
        return len(self._edges)

    @property
    def node_ids(self) -> tuple[str, ...]:
        """Every declared node id, sorted."""
        return tuple(sorted(self._edges))

    @property
    def edge_count(self) -> int:
        """The total number of declared edges."""
        return sum(len(edges) for edges in self._edges.values())

    # -- derived views ----------------------------------------------------------------

    def _graph(self) -> DependencyGraph:
        """Project the declarations onto the canonical dependency model.

        Rebuilt per query rather than cached: a cache would be a second copy of the truth
        held here, and the projection is pure, so rebuilding it cannot disagree with the
        declarations while a stale cache could.
        """
        graph = DependencyGraph()
        for node_id in sorted(self._edges):
            graph.add(node_id, self._edges[node_id])
        return graph

    def dependencies_of(self, node_id: str) -> tuple[str, ...]:
        """The edges ``node_id`` declares (fail-closed if it is not declared)."""
        self._require(node_id)
        return self._edges[node_id]

    def dependents_of(self, node_id: str) -> tuple[str, ...]:
        """The declared nodes that depend directly on ``node_id``, sorted.

        ``node_id`` need not itself be declared: an edge may legitimately name a node a
        catalogue has not reached yet, and asking who points at it is still meaningful.
        """
        return tuple(sorted(nid for nid, edges in self._edges.items() if node_id in edges))

    def validate(self) -> None:
        """Fail closed on any unknown dependency or any cycle.

        Raises:
            PipelineDependencyError: naming the offending node and the missing edge, or
                the nodes no order could place when the graph is cyclic.
        """
        try:
            self._graph().validate()
        except DependencyError as exc:
            raise PipelineDependencyError(
                "dependency declarations are not valid",
                reason=exc.message,
                detail=dict(exc.context),
            ) from exc

    def has_cycle(self) -> bool:
        """True iff the declared graph contains a cycle (unknown edges raise)."""
        self._require_closed()
        return self._graph().has_cycle()

    def order(self) -> tuple[str, ...]:
        """A deterministic dependency-first ordering of every declared node.

        Raises:
            PipelineDependencyError: on an unknown edge or a cycle (fail-closed).
        """
        self.validate()
        return self._graph().topological_order()

    def closure(self, node_id: str) -> DependencyClosure:
        """The transitive dependency closure of ``node_id``.

        Raises:
            PipelineDependencyError: if ``node_id`` is not declared, an edge in its
                closure names an unknown node, or the closure contains a cycle.
        """
        self._require(node_id)
        self.validate()
        direct = self._edges[node_id]
        transitive: set[str] = set()
        frontier = list(direct)
        while frontier:
            current = frontier.pop()
            if current in transitive:
                continue
            transitive.add(current)
            frontier.extend(self._edges.get(current, ()))
        members = transitive | {node_id}
        full_order = self._graph().topological_order()
        order = tuple(nid for nid in full_order if nid in members)
        return DependencyClosure(
            node_id=node_id,
            direct=direct,
            transitive=tuple(sorted(transitive)),
            order=order,
            depth=self._depth(node_id),
        )

    def impact(self, node_id: str) -> tuple[str, ...]:
        """Every node transitively affected by ``node_id`` — the impact-analysis view.

        The backward reading of the same edge set: if ``node_id`` changes, exactly these
        nodes may need to change with it. Derived, so it can never disagree with
        :meth:`closure`.
        """
        affected: set[str] = set()
        frontier = list(self.dependents_of(node_id))
        while frontier:
            current = frontier.pop()
            if current in affected:
                continue
            affected.add(current)
            frontier.extend(self.dependents_of(current))
        return tuple(sorted(affected))

    def roots(self) -> tuple[str, ...]:
        """Declared nodes that depend on nothing (the entry points), sorted."""
        return tuple(sorted(nid for nid, edges in self._edges.items() if not edges))

    def leaves(self) -> tuple[str, ...]:
        """Declared nodes nothing depends on (the tips), sorted."""
        depended = {edge for edges in self._edges.values() for edge in edges}
        return tuple(sorted(nid for nid in self._edges if nid not in depended))

    def orphans(self) -> tuple[str, ...]:
        """Declared nodes with no edge in either direction, sorted.

        An orphan is not an error — a standalone unit is legitimate — but it is a
        *finding*: orphan prevention is a declared repository obligation, so the set is
        reported rather than left to be discovered by absence.
        """
        depended = {edge for edges in self._edges.values() for edge in edges}
        return tuple(
            sorted(nid for nid, edges in self._edges.items() if not edges and nid not in depended)
        )

    def unresolved_edges(self) -> tuple[tuple[str, str], ...]:
        """Every declared edge whose target is not declared, sorted (closure honesty)."""
        return tuple(
            sorted(
                (node_id, edge)
                for node_id, edges in self._edges.items()
                for edge in edges
                if edge not in self._edges
            )
        )

    # -- internals --------------------------------------------------------------------

    def _require(self, node_id: str) -> None:
        if node_id not in self._edges:
            raise PipelineDependencyError("no such dependency node", node=node_id)

    def _require_closed(self) -> None:
        unresolved = self.unresolved_edges()
        if unresolved:
            raise PipelineDependencyError(
                "dependency edge names an undeclared node (closure honesty)",
                unresolved=[list(pair) for pair in unresolved],
            )

    def _depth(self, node_id: str) -> int:
        """The longest declared chain below ``node_id`` (0 for a root).

        Safe on a validated graph: :meth:`closure` validates before calling, so the walk
        terminates. ``visiting`` guards the recursion anyway, so a cyclic graph yields a
        finite answer instead of exhausting the stack.
        """

        def walk(current: str, visiting: frozenset[str]) -> int:
            if current in visiting:
                return 0
            edges = self._edges.get(current, ())
            if not edges:
                return 0
            return 1 + max(walk(edge, visiting | {current}) for edge in edges)

        return walk(node_id, frozenset())

    def to_dict(self) -> dict[str, Any]:
        """A deterministic, serializable render of the declared graph (evidence)."""
        return {
            "node_count": len(self._edges),
            "edge_count": self.edge_count,
            "nodes": [
                {"node_id": nid, "depends_on": list(self._edges[nid])}
                for nid in sorted(self._edges)
            ],
            "roots": list(self.roots()),
            "leaves": list(self.leaves()),
            "orphans": list(self.orphans()),
            "unresolved_edges": [list(pair) for pair in self.unresolved_edges()],
        }

    def fingerprint(self) -> str:
        """A deterministic content hash of the declared graph."""
        return content_hash(self.to_dict())


__all__ = ["DependencyClosure", "DependencyManager"]
