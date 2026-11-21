"""UCOS-CTRL-PLAN-000001 — Master Plan Engine (Wave 12).

The runtime of the wave: the engine that turns authoritative Project State into the canonical
executable master plan, holds it in the
:class:`~platform.universal_master_plan.master_plan_registry.MasterPlanRegistry`, and persists
it through the durable journal the control plane already owns.

It is a **consumer**, not an authority. Repository Truth is discovered by the control plane's
:class:`~platform.universal_control_plane.truth.RepositoryTruthEngine`; the entity population
is projected by the control plane's registration-derived composition and fixed by Wave 11's
:class:`~platform.universal_project_state.state_runtime.ProjectStateEngine`; persistence and
replay run through :class:`~platform.universal_control_plane.durable.DurableJournal`. This
engine invokes all three and re-implements none of them.

What it adds is the plan itself: aggregation of the snapshot's planning entities, normalization
into one node shape, linkage from the identifiers those entities already publish, composition
into an immutable ordered plan, and projection of that plan. It determines no truth, no
ownership, no governance and no certification — every such fact arrives already determined on
the entity, and a relationship the state does not support is left absent and counted.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from platform.universal_control_plane.durable import DurableJournal
from platform.universal_control_plane.manifest import ControlPlaneManifest, default_manifest
from platform.universal_master_plan.master_plan import (
    MasterPlan,
    MasterPlanError,
    PlanDelta,
    compose_plan,
)
from platform.universal_master_plan.master_plan_registry import MasterPlanRegistry
from platform.universal_master_plan.master_plan_replay import record_plan, replays
from platform.universal_project_state.state import ProjectStateSnapshot
from platform.universal_project_state.state_runtime import ProjectStateEngine
from typing import Any


@dataclass
class MasterPlanEngine:
    """Aggregates, normalizes, links, composes and projects the canonical master plan."""

    manifest: ControlPlaneManifest = field(default_factory=default_manifest)
    registry: MasterPlanRegistry = field(default_factory=MasterPlanRegistry)
    state: ProjectStateEngine | None = None
    journal: DurableJournal | None = None
    _plans: list[MasterPlan] = field(default_factory=list)

    # -- the project state seam ------------------------------------------

    def state_engine(self) -> ProjectStateEngine:
        """The Project State Engine this plan is derived from, created on first use.

        Wave 11 is reused rather than re-entered: the engine is constructed with this wave's
        manifest and journal so state and plan land in one chain, and the snapshot it produces
        is taken as authoritative without re-deriving a single entity.
        """
        if self.state is None:
            self.state = ProjectStateEngine(manifest=self.manifest, journal=self.journal)
        return self.state

    # -- composition -----------------------------------------------------

    def compose(self, snapshot: ProjectStateSnapshot, *, tick: int = 0) -> MasterPlan:
        """Compose, register and record the master plan of an authoritative *snapshot*."""
        plan = compose_plan(snapshot)
        self.registry.register_plan(plan)
        self._plans.append(plan)
        if self.journal is not None:
            record_plan(self.journal, plan, tick=tick or snapshot.tick)
        return plan

    def derive(self, plane: Any, *, tick: int = 0) -> MasterPlan:
        """Project *plane* into project state through Wave 11, then compose its master plan."""
        snapshot = self.state_engine().project(plane, tick=tick)
        return self.compose(snapshot, tick=tick)

    # -- state -----------------------------------------------------------

    def plan(self) -> MasterPlan:
        """The most recent plan; fail-closed before anything has been composed."""
        if not self._plans:
            raise MasterPlanError("no master plan has been composed yet")
        return self._plans[-1]

    def plans(self) -> tuple[MasterPlan, ...]:
        return tuple(self._plans)

    def delta(self) -> PlanDelta:
        """The delta between the two most recent plans; empty when fewer than two exist."""
        if len(self._plans) < 2:
            return PlanDelta()
        return PlanDelta.between(self._plans[-2], self._plans[-1])

    # -- lineage and dependency projection -------------------------------

    def lineage_of(self, node_id: str) -> tuple[str, ...]:
        """The containment chain above *node_id* in the current plan."""
        return self.plan().lineage_of(node_id)

    def dependencies_of(self, node_id: str) -> tuple[str, ...]:
        return self.plan().requires(node_id)

    def order(self) -> tuple[str, ...]:
        """The current plan's deterministic execution ordering."""
        return self.plan().topological()

    def unresolved(self) -> tuple[tuple[str, str, str], ...]:
        """Every reference the current plan could not resolve — absence, measured."""
        return self.plan().unresolved_references()

    # -- replay ----------------------------------------------------------

    def replayable(self) -> bool:
        """Whether the journal replays the current plan exactly."""
        if self.journal is None or not self._plans:
            return False
        return replays(self.journal, self.plan())

    # -- projection ------------------------------------------------------

    def counts(self) -> dict[str, int]:
        current = self._plans[-1] if self._plans else None
        return {
            "plans": len(self._plans),
            "nodes": self.registry.count(),
            "kinds": len(self.registry.kinds()),
            "edges": len(self.registry.edges()),
            "roots": len(current.roots()) if current else 0,
            "cycles": len(current.cycles()) if current else 0,
        }

    def to_dict(self) -> dict[str, Any]:
        return {
            "engine": "MasterPlanEngine",
            "universe_id": self.manifest.universe_id,
            "counts": self.counts(),
            "registry": self.registry.to_dict(),
            "replayable": self.replayable(),
            "plan": self._plans[-1].to_dict() if self._plans else None,
        }


__all__ = ["MasterPlanEngine"]
