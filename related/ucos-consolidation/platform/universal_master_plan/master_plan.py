"""UCOS-CTRL-PLAN-000001 — Master Plan (Wave 12).

The canonical executable master plan. It is a **deterministic projection**, not an authority:
Repository Truth, the Control Plane and Project State determine what exists, who owns it,
whether it is governed and whether it is certified. This module determines none of those. It
reads what they already decided and composes it into one plan.

What the wave contributes is the five operations the plan layer needs and project state does
not perform:

    aggregation    the planning entities of the authoritative snapshot become plan nodes
    normalization  heterogeneous kinds are read through one uniform node shape
    identity       node, edge and plan are content-addressed
    linkage        containment and dependency edges are resolved between existing identifiers
    composition    the result is one immutable, ordered, replayable :class:`MasterPlan`

Membership is the declared planning vocabulary of the existing ontology — :data:`PLAN_KINDS`.
Those seven kinds are the objects that already carry planning intent; the registration,
governance, certification, version, ownership, dependency and capability records the same
snapshot holds are *not* plan objects, and projecting them would make this module a second
reading of populations that already have authorities. No category beyond the declared seven is
introduced, and no new planning taxonomy is derived.

The linkage rule is the part worth stating plainly, because it is where a planning layer
usually starts inventing. An edge exists only when an identifier a plan entity *already
publishes* resolves to another plan entity that is *also in the snapshot*. A reference that
resolves to nothing produces no edge; it is recorded by
:meth:`MasterPlan.unresolved_references` and counted. A reference that resolves to more than
one entity produces an edge to each and is counted by
:meth:`MasterPlan.ambiguous_references`. Absence is measured, never inferred, and never
filled in.

Deterministic and clock-free: identity is a content digest, ordering is explicit, and the
logical ``tick`` comes from the snapshot. Python standard library only.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field
from platform.universal_control_plane.ontology import payload_digest
from platform.universal_project_state.state import (
    ID_SUFFIX,
    ProjectStateSnapshot,
    StateEntity,
    discover_entity_kinds,
)
from platform.universal_project_state.state_registry import DEPENDENCY_KEYS
from typing import Any

#: The suffix borne by a projected key that names a *collection* of foreign identifiers.
#: ``_id`` (imported from project state rather than respelled) names a single one.
IDS_SUFFIX = "_ids"

#: The declared planning vocabulary: the entity kinds of the existing control-plane ontology
#: that already carry planning intent. Membership in the master plan is exactly this set.
#:
#: The registration, governance, certification, version, ownership, dependency and capability
#: records the same snapshot holds are deliberately absent. Each already has an authority that
#: determines it, and projecting one into a plan node would make the plan a second reading of a
#: population it does not own. Every name below is verified against the ontology at import by
#: :func:`plan_kinds`, so a rename in the ontology fails loudly here instead of silently
#: emptying the plan.
PLAN_KINDS: tuple[str, ...] = (
    "Assignment",
    "BacklogItem",
    "Goal",
    "Milestone",
    "Objective",
    "ProgressRecord",
    "Vision",
)

#: Keys consulted, in order, for a node's human-facing title. Both name a field a declared
#: plan kind actually publishes — ``title`` on a goal, objective, milestone or backlog item,
#: ``statement`` on a vision. No key is listed speculatively.
TITLE_KEYS: tuple[str, ...] = ("title", "statement")

#: Keys read for the three ordering facts the ontology publishes. An entity that publishes
#: none of them is normalized with them absent — that is a measurement, not a default.
PRIORITY_KEY = "priority"
SEQUENCE_KEY = "sequence"
ESTIMATE_KEY = "estimate"

#: The two edge kinds. ``CONTAINS`` runs parent → child and is resolved from a foreign
#: identifier a child publishes; ``REQUIRES`` runs dependent → dependency and is resolved
#: from the ``dependencies`` key project state already reads for the same purpose.
EDGE_CONTAINS = "CONTAINS"
EDGE_REQUIRES = "REQUIRES"

#: The bound on lineage walks. A projected graph is not guaranteed acyclic — the plan
#: measures cycles rather than assuming their absence — so every ancestor walk is bounded.
MAX_LINEAGE_DEPTH = 64


class MasterPlanError(Exception):
    """Raised when a master plan cannot be composed, queried or reconstructed."""


# ---------------------------------------------------------------------------
# membership — the declared planning vocabulary of the existing ontology
# ---------------------------------------------------------------------------


def plan_kinds() -> tuple[str, ...]:
    """The declared planning kinds, checked against the ontology project state discovered.

    The check is what keeps :data:`PLAN_KINDS` honest. It is a declaration, so it *could*
    drift from the ontology it names; resolving it against
    :func:`~platform.universal_project_state.state.discover_entity_kinds` means a renamed or
    removed planning object fails closed here rather than quietly shrinking every plan.
    """
    known = frozenset(discover_entity_kinds())
    missing = tuple(kind for kind in PLAN_KINDS if kind not in known)
    if missing:
        raise MasterPlanError(
            f"declared plan kinds are absent from the control-plane ontology: {missing}"
        )
    return PLAN_KINDS


def is_plan_entity(entity: StateEntity) -> bool:
    """Whether *entity* carries planning intent — that is, whether its kind is declared."""
    return entity.kind in PLAN_KINDS


# ---------------------------------------------------------------------------
# normalization — reading the references an entity already publishes
# ---------------------------------------------------------------------------


def plan_references(raw: Mapping[str, Any]) -> tuple[tuple[str, str], ...]:
    """Every foreign identifier *raw* publishes, as ``(attribute, target)`` pairs.

    The entity's *own* identifier is excluded. It is recognised exactly as
    :func:`~platform.universal_project_state.state.entity_id_of` recognises it — the first
    ``*_id`` key carrying a non-empty value — so a projection cannot be read as referring to
    itself, and the two modules cannot disagree about which key is the subject.
    """
    own_seen = False
    references: list[tuple[str, str]] = []
    for key, value in raw.items():
        if key.endswith(IDS_SUFFIX):
            if isinstance(value, Sequence) and not isinstance(value, str | bytes):
                for item in value:
                    target = str(item).strip()
                    if target:
                        references.append((key, target))
            continue
        if not key.endswith(ID_SUFFIX):
            continue
        target = "" if value is None else str(value).strip()
        if not own_seen:
            own_seen = bool(target)
            continue
        if target:
            references.append((key, target))
    return tuple(references)


def plan_dependencies(raw: Mapping[str, Any]) -> tuple[tuple[str, str], ...]:
    """Every declared dependency *raw* publishes, as ``(attribute, target)`` pairs.

    The keys are project state's own :data:`DEPENDENCY_KEYS`; no second spelling of
    "depends on" is introduced here.
    """
    dependencies: list[tuple[str, str]] = []
    for key in DEPENDENCY_KEYS:
        value = raw.get(key)
        if isinstance(value, Sequence) and not isinstance(value, str | bytes):
            for item in value:
                target = str(item).strip()
                if target and (key, target) not in dependencies:
                    dependencies.append((key, target))
    return tuple(dependencies)


def _first_present(raw: Mapping[str, Any], keys: Sequence[str]) -> str:
    for key in keys:
        value = raw.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()
    return ""


def _as_int(raw: Mapping[str, Any], key: str) -> int:
    value = raw.get(key)
    if isinstance(value, bool) or not isinstance(value, int | float | str):
        return 0
    try:
        return int(value)
    except (TypeError, ValueError):
        return 0


# ---------------------------------------------------------------------------
# the plan model
# ---------------------------------------------------------------------------


@dataclass(frozen=True, slots=True)
class PlanNode:
    """One normalized master-plan node: a project-state entity read through one shape."""

    kind: str
    entity_id: str
    title: str = ""
    lifecycle: str = ""
    owner: str = ""
    priority: str = ""
    sequence: int = 0
    estimate: int = 0
    references: tuple[tuple[str, str], ...] = ()
    dependencies: tuple[tuple[str, str], ...] = ()
    attributes: Mapping[str, Any] = field(default_factory=dict)
    tick: int = 0

    @classmethod
    def from_entity(cls, entity: StateEntity) -> PlanNode:
        """Normalize one authoritative project-state entity into a plan node.

        Kind, identifier, lifecycle and owner are taken from the entity as project state
        already derived them — they are not re-derived from the raw attributes here, so the
        two layers cannot disagree about what an entity is.
        """
        raw = entity.attributes
        return cls(
            kind=entity.kind,
            entity_id=entity.entity_id,
            title=_first_present(raw, TITLE_KEYS),
            lifecycle=entity.lifecycle,
            owner=entity.owner,
            priority=_first_present(raw, (PRIORITY_KEY,)),
            sequence=_as_int(raw, SEQUENCE_KEY),
            estimate=_as_int(raw, ESTIMATE_KEY),
            references=plan_references(raw),
            dependencies=plan_dependencies(raw),
            attributes=dict(raw),
            tick=entity.tick,
        )

    @property
    def node_id(self) -> str:
        """The node's stable identifier — the same kind-qualified subject project state uses."""
        return f"{self.kind}::{self.entity_id}"

    @property
    def identity(self) -> str:
        """The content-addressed identity of this node."""
        return payload_digest(self.core())

    def core(self) -> dict[str, Any]:
        """The hashable core: the normalized projection only, no wall-clock and no tick."""
        return {
            "kind": self.kind,
            "entity_id": self.entity_id,
            "title": self.title,
            "lifecycle": self.lifecycle,
            "owner": self.owner,
            "priority": self.priority,
            "sequence": self.sequence,
            "estimate": self.estimate,
            "references": [list(pair) for pair in self.references],
            "dependencies": [list(pair) for pair in self.dependencies],
        }

    def targets(self) -> tuple[str, ...]:
        """Every foreign identifier this node names, de-duplicated, in declared order."""
        seen: list[str] = []
        for _, target in (*self.references, *self.dependencies):
            if target not in seen:
                seen.append(target)
        return tuple(seen)

    def to_dict(self) -> dict[str, Any]:
        return {
            "kind": "PlanNode",
            "identity": self.identity,
            "node_id": self.node_id,
            "entity_kind": self.kind,
            "entity_id": self.entity_id,
            "title": self.title,
            "lifecycle": self.lifecycle,
            "owner": self.owner,
            "priority": self.priority,
            "sequence": self.sequence,
            "estimate": self.estimate,
            "references": [list(pair) for pair in self.references],
            "dependencies": [list(pair) for pair in self.dependencies],
            "tick": self.tick,
        }


@dataclass(frozen=True, slots=True)
class PlanEdge:
    """One resolved master-plan edge, attributed to the key that produced it."""

    from_id: str
    to_id: str
    kind: str
    attribute: str = ""

    @property
    def edge_id(self) -> str:
        return f"{self.kind}:{self.from_id}->{self.to_id}:{self.attribute}"

    @property
    def identity(self) -> str:
        return payload_digest(self.core())

    def core(self) -> dict[str, Any]:
        return {
            "from_id": self.from_id,
            "to_id": self.to_id,
            "kind": self.kind,
            "attribute": self.attribute,
        }

    def to_dict(self) -> dict[str, Any]:
        return {
            "kind": "PlanEdge",
            "identity": self.identity,
            "edge_id": self.edge_id,
            "from_id": self.from_id,
            "to_id": self.to_id,
            "edge_kind": self.kind,
            "attribute": self.attribute,
        }


def compose_edges(nodes: Sequence[PlanNode]) -> tuple[PlanEdge, ...]:
    """Resolve every edge the nodes' own identifiers support — and no other edge.

    A reference resolving to no node yields nothing; a reference resolving to several yields
    an edge to each. Both outcomes are recoverable from the composed plan, which is the point:
    the plan reports what the state supports rather than repairing it.
    """
    index: dict[str, list[str]] = {}
    for node in nodes:
        index.setdefault(node.entity_id, []).append(node.node_id)

    edges: dict[str, PlanEdge] = {}
    for node in sorted(nodes, key=lambda n: n.node_id):
        for attribute, target in node.references:
            for parent in sorted(index.get(target, ())):
                if parent == node.node_id:
                    continue
                edge = PlanEdge(parent, node.node_id, EDGE_CONTAINS, attribute)
                edges.setdefault(edge.edge_id, edge)
        for attribute, target in node.dependencies:
            for other in sorted(index.get(target, ())):
                if other == node.node_id:
                    continue
                edge = PlanEdge(node.node_id, other, EDGE_REQUIRES, attribute)
                edges.setdefault(edge.edge_id, edge)
    return tuple(edges[key] for key in sorted(edges))


@dataclass(frozen=True, slots=True)
class MasterPlan:
    """The canonical, immutable, content-addressed master plan at one logical tick."""

    universe_id: str
    truth_id: str
    snapshot_id: str
    nodes: tuple[PlanNode, ...] = ()
    edges: tuple[PlanEdge, ...] = ()
    tick: int = 0

    # -- identity --------------------------------------------------------

    @property
    def plan_id(self) -> str:
        """The content-addressed identity of this plan."""
        return payload_digest(self.core())

    @property
    def identity(self) -> str:
        return self.plan_id

    def core(self) -> dict[str, Any]:
        """The hashable core: the state it projects, its nodes and its resolved edges."""
        return {
            "universe_id": self.universe_id,
            "truth_id": self.truth_id,
            "snapshot_id": self.snapshot_id,
            "nodes": [n.identity for n in self.nodes],
            "edges": [e.identity for e in self.edges],
        }

    def digest(self) -> str:
        return payload_digest([n.identity for n in self.nodes])

    # -- aggregation queries ---------------------------------------------

    def node(self, node_id: str) -> PlanNode:
        for node in self.nodes:
            if node.node_id == node_id:
                return node
        raise MasterPlanError(f"no such plan node: {node_id!r}")

    def kinds(self) -> tuple[str, ...]:
        return tuple(sorted({n.kind for n in self.nodes}))

    def of_kind(self, kind: str) -> tuple[PlanNode, ...]:
        return tuple(n for n in self.nodes if n.kind == kind)

    def owners(self) -> tuple[str, ...]:
        return tuple(sorted({n.owner for n in self.nodes if n.owner}))

    def by_kind(self) -> dict[str, int]:
        counts: dict[str, int] = {}
        for node in self.nodes:
            counts[node.kind] = counts.get(node.kind, 0) + 1
        return dict(sorted(counts.items()))

    # -- linkage ---------------------------------------------------------

    def _adjacency(
        self, kind: str | None = None
    ) -> tuple[dict[str, list[str]], dict[str, list[str]]]:
        """Forward and reverse adjacency over the edges of *kind* (all edges when None)."""
        forward: dict[str, list[str]] = {}
        reverse: dict[str, list[str]] = {}
        for edge in self.edges:
            if kind is not None and edge.kind != kind:
                continue
            if edge.to_id not in forward.setdefault(edge.from_id, []):
                forward[edge.from_id].append(edge.to_id)
            if edge.from_id not in reverse.setdefault(edge.to_id, []):
                reverse[edge.to_id].append(edge.from_id)
        return forward, reverse

    def edges_of_kind(self, kind: str) -> tuple[PlanEdge, ...]:
        return tuple(e for e in self.edges if e.kind == kind)

    def children_of(self, node_id: str) -> tuple[str, ...]:
        return tuple(
            sorted(
                {e.to_id for e in self.edges if e.kind == EDGE_CONTAINS and e.from_id == node_id}
            )
        )

    def parents_of(self, node_id: str) -> tuple[str, ...]:
        return tuple(
            sorted(
                {e.from_id for e in self.edges if e.kind == EDGE_CONTAINS and e.to_id == node_id}
            )
        )

    def requires(self, node_id: str) -> tuple[str, ...]:
        return tuple(
            sorted(
                {e.to_id for e in self.edges if e.kind == EDGE_REQUIRES and e.from_id == node_id}
            )
        )

    def required_by(self, node_id: str) -> tuple[str, ...]:
        return tuple(
            sorted(
                {e.from_id for e in self.edges if e.kind == EDGE_REQUIRES and e.to_id == node_id}
            )
        )

    def roots(self) -> tuple[str, ...]:
        """Every node no containment edge points at — the plan's own entry points."""
        contained = {e.to_id for e in self.edges if e.kind == EDGE_CONTAINS}
        return tuple(sorted(n.node_id for n in self.nodes if n.node_id not in contained))

    def leaves(self) -> tuple[str, ...]:
        parents = {e.from_id for e in self.edges if e.kind == EDGE_CONTAINS}
        return tuple(sorted(n.node_id for n in self.nodes if n.node_id not in parents))

    def isolated(self) -> tuple[str, ...]:
        """Every node no edge touches — a measured absence of linkage, not a defect to fix."""
        touched = {e.from_id for e in self.edges} | {e.to_id for e in self.edges}
        return tuple(sorted(n.node_id for n in self.nodes if n.node_id not in touched))

    # -- lineage ---------------------------------------------------------

    def lineage_of(self, node_id: str) -> tuple[str, ...]:
        """The containment chain above *node_id*, nearest ancestor last.

        The walk is bounded by :data:`MAX_LINEAGE_DEPTH` and stops on re-entry, so a cyclic
        projection yields a truncated lineage rather than a hang.
        """
        self.node(node_id)
        _, reverse = self._adjacency(EDGE_CONTAINS)
        chain: list[str] = []
        seen = {node_id}
        current = node_id
        for _ in range(MAX_LINEAGE_DEPTH):
            parents = sorted(reverse.get(current, ()))
            nxt = next((p for p in parents if p not in seen), "")
            if not nxt:
                break
            chain.append(nxt)
            seen.add(nxt)
            current = nxt
        return tuple(reversed(chain))

    def depths(self) -> dict[str, int]:
        """The containment depth of every node, computed once for the whole plan."""
        forward, _ = self._adjacency(EDGE_CONTAINS)
        depths = {node_id: 0 for node_id in self.roots()}
        frontier = sorted(depths)
        level = 0
        remaining = {n.node_id for n in self.nodes} - set(depths)
        while frontier and remaining:
            level += 1
            nxt: list[str] = []
            for node_id in frontier:
                for child in sorted(forward.get(node_id, ())):
                    if child in remaining:
                        remaining.discard(child)
                        depths[child] = level
                        nxt.append(child)
            frontier = nxt
        return dict(sorted(depths.items()))

    def depth_of(self, node_id: str) -> int:
        """The containment depth of *node_id*; -1 when it is unreachable from any root."""
        self.node(node_id)
        return self.depths().get(node_id, -1)

    def height(self) -> int:
        depths = self.depths()
        return max(depths.values()) if depths else 0

    # -- composition and ordering ----------------------------------------

    def topological(self) -> tuple[str, ...]:
        """A deterministic execution order over every edge the plan resolved.

        Kahn's algorithm with a sorted frontier, so the ordering is a function of the plan
        and nothing else. Nodes inside a cycle are *not* ordered — they are returned by
        :meth:`cycles`, because inventing a position for them would be fabrication.
        """
        forward, reverse = self._adjacency()
        indegree = {n.node_id: len(reverse.get(n.node_id, ())) for n in self.nodes}
        frontier = sorted(node_id for node_id, degree in indegree.items() if degree == 0)
        order: list[str] = []
        while frontier:
            node_id = frontier.pop(0)
            order.append(node_id)
            released: list[str] = []
            for child in forward.get(node_id, ()):
                indegree[child] -= 1
                if indegree[child] == 0:
                    released.append(child)
            if released:
                frontier = sorted(frontier + released)
        return tuple(order)

    def cycles(self) -> tuple[str, ...]:
        """Every node the ordering could not place — the measured cyclic residue."""
        ordered = set(self.topological())
        return tuple(sorted(n.node_id for n in self.nodes if n.node_id not in ordered))

    def acyclic(self) -> bool:
        return not self.cycles()

    # -- measured absence ------------------------------------------------

    def unresolved_references(self) -> tuple[tuple[str, str, str], ...]:
        """Every ``(node_id, attribute, target)`` naming an identifier no node carries."""
        known = {n.entity_id for n in self.nodes}
        return tuple(
            (node.node_id, attribute, target)
            for node in self.nodes
            for attribute, target in (*node.references, *node.dependencies)
            if target not in known
        )

    def ambiguous_references(self) -> tuple[tuple[str, str, str], ...]:
        """Every reference whose target identifier is carried by more than one node."""
        counts: dict[str, int] = {}
        for node in self.nodes:
            counts[node.entity_id] = counts.get(node.entity_id, 0) + 1
        return tuple(
            (node.node_id, attribute, target)
            for node in self.nodes
            for attribute, target in (*node.references, *node.dependencies)
            if counts.get(target, 0) > 1
        )

    def linkage_coverage(self) -> float:
        """The fraction of nodes at least one edge touches, to four places."""
        if not self.nodes:
            return 0.0
        return round(1 - (len(self.isolated()) / len(self.nodes)), 4)

    def containment_coverage(self) -> float:
        """The fraction of nodes a containment edge places under a parent, to four places."""
        if not self.nodes:
            return 0.0
        contained = {e.to_id for e in self.edges if e.kind == EDGE_CONTAINS}
        return round(len(contained) / len(self.nodes), 4)

    # -- projection ------------------------------------------------------

    def counts(self) -> dict[str, int]:
        return {
            "nodes": len(self.nodes),
            "kinds": len(self.kinds()),
            "edges": len(self.edges),
            "containment_edges": len(self.edges_of_kind(EDGE_CONTAINS)),
            "dependency_edges": len(self.edges_of_kind(EDGE_REQUIRES)),
            "roots": len(self.roots()),
            "leaves": len(self.leaves()),
            "isolated": len(self.isolated()),
            "owners": len(self.owners()),
            "unresolved_references": len(self.unresolved_references()),
            "ambiguous_references": len(self.ambiguous_references()),
            "cycles": len(self.cycles()),
        }

    def projection(self) -> dict[str, Any]:
        """The plan as a composed structure: ordering, roots, depth and per-kind population."""
        return {
            "plan_id": self.plan_id,
            "order": list(self.topological()),
            "roots": list(self.roots()),
            "height": self.height(),
            "by_kind": self.by_kind(),
        }

    def to_dict(self) -> dict[str, Any]:
        return {
            "kind": "MasterPlan",
            "identity": self.plan_id,
            "plan_id": self.plan_id,
            "universe_id": self.universe_id,
            "truth_id": self.truth_id,
            "snapshot_id": self.snapshot_id,
            "tick": self.tick,
            "counts": self.counts(),
            "by_kind": self.by_kind(),
            "linkage_coverage": self.linkage_coverage(),
            "containment_coverage": self.containment_coverage(),
            "acyclic": self.acyclic(),
            "height": self.height(),
            "digest": self.digest(),
        }


@dataclass(frozen=True, slots=True)
class PlanDelta:
    """The measured difference between two master plans, by node identifier."""

    added: tuple[str, ...] = ()
    removed: tuple[str, ...] = ()
    changed: tuple[str, ...] = ()

    @classmethod
    def between(cls, before: MasterPlan, after: MasterPlan) -> PlanDelta:
        prior = {n.node_id: n.identity for n in before.nodes}
        current = {n.node_id: n.identity for n in after.nodes}
        return cls(
            added=tuple(sorted(set(current) - set(prior))),
            removed=tuple(sorted(set(prior) - set(current))),
            changed=tuple(sorted(k for k in set(prior) & set(current) if prior[k] != current[k])),
        )

    @property
    def empty(self) -> bool:
        return not (self.added or self.removed or self.changed)

    def counts(self) -> dict[str, int]:
        return {
            "added": len(self.added),
            "removed": len(self.removed),
            "changed": len(self.changed),
        }

    def to_dict(self) -> dict[str, Any]:
        return {
            "kind": "PlanDelta",
            "identity": payload_digest(self.counts()),
            "counts": self.counts(),
            "added": list(self.added),
            "removed": list(self.removed),
            "changed": list(self.changed),
            "empty": self.empty,
        }


def compose_plan(snapshot: ProjectStateSnapshot) -> MasterPlan:
    """Compose the master plan of *snapshot* over the declared planning kinds.

    Membership is :func:`plan_kinds` and nothing else: an entity that carries planning intent
    becomes a node, and an entity that belongs to another authority — a registration,
    governance, certification, version, ownership, dependency or capability record — does not.
    The plan inherits the snapshot's universe, Repository Truth identity and tick, so a plan
    always names the state it projects and the Truth that state was taken over.
    """
    declared = frozenset(plan_kinds())
    nodes = tuple(
        PlanNode.from_entity(entity) for entity in snapshot.entities if entity.kind in declared
    )
    return MasterPlan(
        universe_id=snapshot.universe_id,
        truth_id=snapshot.truth_id,
        snapshot_id=snapshot.snapshot_id,
        nodes=nodes,
        edges=compose_edges(nodes),
        tick=snapshot.tick,
    )


__all__ = [
    "EDGE_CONTAINS",
    "EDGE_REQUIRES",
    "ESTIMATE_KEY",
    "IDS_SUFFIX",
    "MAX_LINEAGE_DEPTH",
    "PLAN_KINDS",
    "PRIORITY_KEY",
    "SEQUENCE_KEY",
    "TITLE_KEYS",
    "MasterPlan",
    "MasterPlanError",
    "PlanDelta",
    "PlanEdge",
    "PlanNode",
    "compose_edges",
    "compose_plan",
    "is_plan_entity",
    "plan_dependencies",
    "plan_kinds",
    "plan_references",
]
