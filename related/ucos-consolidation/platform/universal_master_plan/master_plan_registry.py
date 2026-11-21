"""UCOS-CTRL-PLAN-000001 — Master Plan Registry (Wave 12).

The canonical index of composed master plans: every :class:`~platform.universal_master_plan.
master_plan.MasterPlan` held once under its content identity, every
:class:`~platform.universal_master_plan.master_plan.PlanNode` held once under its node
identifier, with the containment, dependency and ownership indices the plan layer queries.

This is a registry in the same sense as
:class:`~platform.universal_project_state.state_registry.ProjectStateRegistry` — a container
with queries, not an engine with policy. It adjudicates nothing, decides nothing and derives
no relationship of its own: edges arrive already resolved by plan composition, and ownership
arrives already carried by the node. Registration is idempotent by identity, so re-registering
an unchanged node is a no-op and re-registering a changed one is a recorded replacement rather
than a silent duplicate.

It is not a replacement for any existing registry. The capability, ownership, dependency and
project-state registries hold different populations; this one holds plans and plan nodes,
which none of them holds.
"""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from dataclasses import dataclass, field
from platform.universal_master_plan.master_plan import (
    EDGE_CONTAINS,
    EDGE_REQUIRES,
    MasterPlan,
    MasterPlanError,
    PlanEdge,
    PlanNode,
)
from typing import Any


@dataclass
class MasterPlanRegistry:
    """Holds every composed plan and every plan node once, with the plan-layer indices."""

    _plans: dict[str, MasterPlan] = field(default_factory=dict)
    _order: list[str] = field(default_factory=list)
    _nodes: dict[str, PlanNode] = field(default_factory=dict)
    _edges: dict[str, PlanEdge] = field(default_factory=dict)
    _replaced: dict[str, int] = field(default_factory=dict)

    # -- registration ----------------------------------------------------

    def register_node(self, node: PlanNode) -> PlanNode:
        """Register *node*, recording a replacement only when its content changed."""
        if not node.entity_id.strip():
            raise MasterPlanError("a plan node requires a non-empty entity_id")
        existing = self._nodes.get(node.node_id)
        if existing is not None and existing.identity != node.identity:
            self._replaced[node.node_id] = self._replaced.get(node.node_id, 0) + 1
        self._nodes[node.node_id] = node
        return node

    def register_nodes(self, nodes: Iterable[PlanNode]) -> tuple[PlanNode, ...]:
        return tuple(self.register_node(node) for node in nodes)

    def register_edge(self, edge: PlanEdge) -> PlanEdge:
        self._edges[edge.edge_id] = edge
        return edge

    def register_plan(self, plan: MasterPlan) -> MasterPlan:
        """Register a composed plan together with every node and edge it carries."""
        if not plan.plan_id:
            raise MasterPlanError("a master plan requires a resolvable plan_id")
        if plan.plan_id not in self._plans:
            self._order.append(plan.plan_id)
        self._plans[plan.plan_id] = plan
        self.register_nodes(plan.nodes)
        for edge in plan.edges:
            self.register_edge(edge)
        return plan

    # -- plan queries ----------------------------------------------------

    def plan(self, plan_id: str) -> MasterPlan:
        try:
            return self._plans[plan_id]
        except KeyError as exc:
            raise MasterPlanError(f"no such master plan: {plan_id!r}") from exc

    def plans(self) -> tuple[MasterPlan, ...]:
        """Every registered plan in registration order — the plan's recorded history."""
        return tuple(self._plans[plan_id] for plan_id in self._order)

    def latest(self) -> MasterPlan:
        if not self._order:
            raise MasterPlanError("no master plan has been registered yet")
        return self._plans[self._order[-1]]

    def plan_ids(self) -> tuple[str, ...]:
        return tuple(self._order)

    def plans_for_snapshot(self, snapshot_id: str) -> tuple[MasterPlan, ...]:
        return tuple(p for p in self.plans() if p.snapshot_id == snapshot_id)

    def plans_for_truth(self, truth_id: str) -> tuple[MasterPlan, ...]:
        return tuple(p for p in self.plans() if p.truth_id == truth_id)

    # -- node queries ----------------------------------------------------

    def node(self, node_id: str) -> PlanNode:
        try:
            return self._nodes[node_id]
        except KeyError as exc:
            raise MasterPlanError(f"no such plan node: {node_id!r}") from exc

    def nodes(self) -> tuple[PlanNode, ...]:
        return tuple(self._nodes[key] for key in sorted(self._nodes))

    def node_ids(self) -> tuple[str, ...]:
        return tuple(sorted(self._nodes))

    def kinds(self) -> tuple[str, ...]:
        return tuple(sorted({n.kind for n in self._nodes.values()}))

    def of_kind(self, kind: str) -> tuple[PlanNode, ...]:
        return tuple(n for n in self.nodes() if n.kind == kind)

    def owners(self) -> tuple[str, ...]:
        return tuple(sorted({n.owner for n in self._nodes.values() if n.owner}))

    def owned_by(self, owner: str) -> tuple[PlanNode, ...]:
        return tuple(n for n in self.nodes() if n.owner == owner)

    def unowned(self) -> tuple[PlanNode, ...]:
        """Every registered node carrying no owner — the plan's ownership gap, measured."""
        return tuple(n for n in self.nodes() if not n.owner)

    def replacements(self) -> Mapping[str, int]:
        return dict(sorted(self._replaced.items()))

    def count(self) -> int:
        return len(self._nodes)

    def plan_count(self) -> int:
        return len(self._plans)

    # -- edge queries ----------------------------------------------------

    def edges(self) -> tuple[PlanEdge, ...]:
        return tuple(self._edges[key] for key in sorted(self._edges))

    def edges_of_kind(self, kind: str) -> tuple[PlanEdge, ...]:
        return tuple(e for e in self.edges() if e.kind == kind)

    def children_of(self, node_id: str) -> tuple[str, ...]:
        return tuple(
            sorted(
                {
                    e.to_id
                    for e in self._edges.values()
                    if e.kind == EDGE_CONTAINS and e.from_id == node_id
                }
            )
        )

    def parents_of(self, node_id: str) -> tuple[str, ...]:
        return tuple(
            sorted(
                {
                    e.from_id
                    for e in self._edges.values()
                    if e.kind == EDGE_CONTAINS and e.to_id == node_id
                }
            )
        )

    def dependencies_of(self, node_id: str) -> tuple[str, ...]:
        return tuple(
            sorted(
                {
                    e.to_id
                    for e in self._edges.values()
                    if e.kind == EDGE_REQUIRES and e.from_id == node_id
                }
            )
        )

    def dependents_of(self, node_id: str) -> tuple[str, ...]:
        return tuple(
            sorted(
                {
                    e.from_id
                    for e in self._edges.values()
                    if e.kind == EDGE_REQUIRES and e.to_id == node_id
                }
            )
        )

    def coverage(self) -> float:
        """The fraction of registered nodes carrying an owner, to four places."""
        if not self._nodes:
            return 0.0
        return round(1 - (len(self.unowned()) / len(self._nodes)), 4)

    # -- projection ------------------------------------------------------

    def counts(self) -> dict[str, int]:
        return {
            "plans": self.plan_count(),
            "nodes": self.count(),
            "kinds": len(self.kinds()),
            "edges": len(self._edges),
            "containment_edges": len(self.edges_of_kind(EDGE_CONTAINS)),
            "dependency_edges": len(self.edges_of_kind(EDGE_REQUIRES)),
            "owners": len(self.owners()),
            "unowned": len(self.unowned()),
            "replacements": len(self._replaced),
        }

    def by_kind(self) -> dict[str, int]:
        counts: dict[str, int] = {}
        for node in self._nodes.values():
            counts[node.kind] = counts.get(node.kind, 0) + 1
        return dict(sorted(counts.items()))

    def to_dict(self) -> dict[str, Any]:
        return {
            "engine": "MasterPlanRegistry",
            "counts": self.counts(),
            "by_kind": self.by_kind(),
            "ownership_coverage": self.coverage(),
            "kinds": list(self.kinds()),
            "plan_ids": list(self.plan_ids()),
        }


__all__ = ["MasterPlanRegistry"]
