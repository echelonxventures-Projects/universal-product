"""UCOS-CDG-000001 — the Universal Constitutional Dependency Graph (Requirement 001).

The directive lists eleven things to discover: dependencies, prerequisites, constraints,
authorities, inputs, outputs, registrations, certifications, governance dependencies,
execution dependencies and evolution dependencies. They are not eleven mechanisms. Each
is a *relation over the same population*, read from a different declared facet, so this
module holds one derivation and applies it to whichever facets
:mod:`engine.constitution.metadata` marks graph-bearing.

That is the difference between this and a dependency file. A dependency file is a
declared order; this is a graph that a caller *cannot* pre-order, because the only thing
callers supply is what each subject requires. Order is derived downstream by
:mod:`engine.constitution.planner` through the single ordering authority
(:mod:`engine.foundation.composition.ordering`) — no second topological sort exists here,
and none may be added.

What it refuses
---------------
Two things, both fail-closed and both reported before any order is derived:

    * an edge naming a subject the population has never declared (CEL-INV-02) — the
      declaration is a claim about something that does not exist, and ordering around a
      non-existent prerequisite would silently mark a skipped dependency as satisfied;
    * a cycle in any relation (CEL-INV-03…06) — reported as the exact set of subjects no
      order could place, never broken by an arbitrary tie-break.
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from typing import Any

from engine.constitution.errors import GraphError
from engine.constitution.metadata import (
    ConstitutionalMetadata,
    Population,
    graph_bearing_facets,
)
from engine.foundation.composition.ordering import (
    DEFAULT_STRATEGY,
    derive_order,
    unresolved_keys,
)
from engine.uckp.canonical import content_hash

#: The identity of the dependency graph authority this module realises.
GRAPH_ID = "UCOS-CDG-000001"

#: Versioned so relations can be *added* without any prior graph changing meaning.
GRAPH_VERSION = "1.0.0"

#: The relation whose closure decides execution order. Named once, here, so no consumer
#: has to know which facet carries execution dependencies.
EXECUTION_RELATION = "dependencies"


@dataclass(frozen=True, slots=True)
class Edge:
    """One directed, typed edge: ``source`` declares ``target`` under ``relation``.

    The direction is *requires*: the source cannot be complete until the target is. That
    is the direction the ordering authority consumes, so no consumer reverses it and no
    consumer has to remember which way it points.
    """

    source: str
    relation: str
    target: str
    resolved: bool = True

    def to_dict(self) -> dict[str, Any]:
        return {
            "source": self.source,
            "relation": self.relation,
            "target": self.target,
            "resolved": self.resolved,
        }


@dataclass(frozen=True, slots=True)
class DependencyGraph:
    """The whole typed graph derived from one population's declarations."""

    graph_id: str
    edges: tuple[Edge, ...]
    subjects: tuple[str, ...]
    relations: tuple[str, ...]

    # ----------------------------------------------------------------- projections

    def relation_graph(self, relation: str) -> dict[str, tuple[str, ...]]:
        """One relation in the shape the single ordering authority consumes.

        Only *resolved* edges are projected. An unresolved edge names a subject that does
        not exist, and feeding it to the ordering authority would place the source as
        though its prerequisite were satisfied. It is reported by
        :meth:`unknown_referents` and refused by :meth:`require_resolved` instead.
        """
        if relation not in self.relations:
            raise GraphError(
                "no such relation",
                relation=relation,
                allowed=list(self.relations),
            )
        projected: dict[str, set[str]] = {subject: set() for subject in self.subjects}
        for edge in self.edges:
            if edge.relation == relation and edge.resolved:
                projected[edge.source].add(edge.target)
        return {subject: tuple(sorted(targets)) for subject, targets in projected.items()}

    def merged_graph(self, relations: Sequence[str] | None = None) -> dict[str, tuple[str, ...]]:
        """Several relations collapsed into one graph — the *constitutional* closure.

        Execution order depends on more than the ``dependencies`` facet: a subject whose
        certifier has not run has not been certified, and a subject whose registry has not
        been updated is not registered. Merging the relations is what makes the derived
        order account for governance, authority, registration and certification together,
        which is the whole of Requirement 002's "calculate legal execution order".
        """
        chosen = tuple(relations) if relations is not None else self.relations
        merged: dict[str, set[str]] = {subject: set() for subject in self.subjects}
        for relation in chosen:
            for subject, targets in self.relation_graph(relation).items():
                merged[subject].update(targets)
        return {subject: tuple(sorted(targets)) for subject, targets in merged.items()}

    # ----------------------------------------------------------------- measurements

    def unknown_referents(self) -> tuple[Edge, ...]:
        """Every edge naming a subject the population never declared (CEL-INV-02)."""
        return tuple(edge for edge in self.edges if not edge.resolved)

    def closure(self, subject: str, *, relations: Sequence[str] | None = None) -> tuple[str, ...]:
        """The transitive closure of ``subject`` over ``relations``, excluding itself.

        This is what "dependency closure", "governance closure", "authority closure",
        "certification closure", "registration closure" and "evolution closure" all are:
        the same walk over a different relation set. Requirement 002 names six closures;
        this is the one function that computes each of them.
        """
        graph = self.merged_graph(relations)
        if subject not in graph:
            raise GraphError("no such subject in graph", subject=subject)
        reached: set[str] = set()
        frontier = [subject]
        while frontier:
            current = frontier.pop()
            for target in graph.get(current, ()):
                if target not in reached:
                    reached.add(target)
                    frontier.append(target)
        reached.discard(subject)
        return tuple(sorted(reached))

    def cycles(self, relation: str, *, strategy: str = DEFAULT_STRATEGY) -> tuple[str, ...]:
        """The subjects of ``relation`` that no order could place — i.e. its cycles.

        Cycle detection is not reimplemented here. The ordering authority stops at the
        acyclic frontier by design, and everything it could not place is exactly what lies
        on (or behind) a cycle, so reporting is a subtraction rather than a second
        traversal that could disagree with the first.
        """
        graph = self.relation_graph(relation)
        return tuple(unresolved_keys(graph, derive_order(graph, strategy=strategy)))

    def dependents(self, subject: str, *, relation: str = EXECUTION_RELATION) -> tuple[str, ...]:
        """The subjects that directly require ``subject`` — the blast radius of a change."""
        return tuple(
            sorted(
                edge.source
                for edge in self.edges
                if edge.relation == relation and edge.target == subject and edge.resolved
            )
        )

    # ----------------------------------------------------------------- fail-closed

    def require_resolved(self) -> DependencyGraph:
        """Return the graph if every edge resolves, else refuse.

        Raises:
            GraphError: an edge names an unregistered subject, so no order over this
                graph could honestly claim its dependencies are complete.
        """
        unknown = self.unknown_referents()
        if unknown:
            raise GraphError(
                "declared graph names subjects that do not exist",
                graph_id=self.graph_id,
                unknown_referents=[edge.to_dict() for edge in unknown],
            )
        return self

    def require_acyclic(self, *, relations: Sequence[str] | None = None) -> DependencyGraph:
        """Return the graph if every named relation is acyclic, else refuse.

        Raises:
            GraphError: a relation contains a cycle; the offending subjects are named.
        """
        chosen = tuple(relations) if relations is not None else self.relations
        offending = {
            relation: list(found) for relation in chosen if (found := self.cycles(relation))
        }
        if offending:
            raise GraphError(
                "declared graph contains a cycle; no order exists",
                graph_id=self.graph_id,
                cycles=dict(sorted(offending.items())),
            )
        return self

    # ----------------------------------------------------------------- evidence

    def counts(self) -> dict[str, int]:
        """Edge counts per relation, plus the population size."""
        per_relation = {relation: 0 for relation in self.relations}
        for edge in self.edges:
            per_relation[edge.relation] += 1
        return {
            "subjects": len(self.subjects),
            "edges": len(self.edges),
            "unresolved_edges": len(self.unknown_referents()),
            **{f"relation:{relation}": count for relation, count in sorted(per_relation.items())},
        }

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema": "ucos-constitutional-dependency-graph",
            "version": GRAPH_VERSION,
            "graph_id": self.graph_id,
            "subjects": list(self.subjects),
            "relations": list(self.relations),
            "edges": [edge.to_dict() for edge in self.edges],
            "unknown_referents": [edge.to_dict() for edge in self.unknown_referents()],
            "cycles": {
                relation: list(self.cycles(relation))
                for relation in self.relations
                if self.cycles(relation)
            },
            "counts": self.counts(),
        }

    def digest(self) -> str:
        return content_hash(self.to_dict())


def _edges_for(
    record: ConstitutionalMetadata,
    *,
    declared: frozenset[str],
    relations: Sequence[str],
) -> list[Edge]:
    """Every edge one declaration contributes, across every graph-bearing relation."""
    edges: list[Edge] = []
    for relation in relations:
        for target in record.referents(relation):
            edges.append(
                Edge(
                    source=record.subject,
                    relation=relation,
                    target=target,
                    resolved=target in declared,
                )
            )
    return edges


def build(
    population: Population,
    *,
    relations: Sequence[str] | None = None,
) -> DependencyGraph:
    """Discover the whole constitutional graph of ``population``.

    Nothing is asked of the caller but the population: which relations exist comes from
    the metadata mandate, and which edges exist comes from the declarations. There is no
    parameter by which a caller could add an edge the declarations do not support, which
    is what keeps the graph a *discovery* rather than an assertion.
    """
    chosen = tuple(relations) if relations is not None else graph_bearing_facets()
    unknown = sorted(set(chosen) - set(graph_bearing_facets()))
    if unknown:
        raise GraphError(
            "relation is not a graph-bearing facet",
            unknown=unknown,
            allowed=list(graph_bearing_facets()),
        )
    declared = frozenset(population.subjects())
    edges: list[Edge] = []
    for record in population:
        edges.extend(_edges_for(record, declared=declared, relations=chosen))
    edges.sort(key=lambda e: (e.source, e.relation, e.target))
    return DependencyGraph(
        graph_id=GRAPH_ID,
        edges=tuple(edges),
        subjects=population.subjects(),
        relations=chosen,
    )


def discover(population: Population) -> DependencyGraph:
    """Build the graph and refuse it unless every edge resolves and every relation is acyclic.

    The fail-closed entry point every other engine in this package calls. ``build`` exists
    for reporting on a graph that is *known* to be broken; ``discover`` is for using one.
    """
    return build(population).require_resolved().require_acyclic()


def to_document(population: Population) -> dict[str, Any]:
    """The discovered graph of ``population`` as a deterministic document."""
    return build(population).to_dict()


__all__ = [
    "EXECUTION_RELATION",
    "GRAPH_ID",
    "GRAPH_VERSION",
    "DependencyGraph",
    "Edge",
    "build",
    "discover",
    "to_document",
]
