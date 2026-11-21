"""UCOS-CTRL-000001 — Universal Scheduler and Assignment Engine.

SchedulerEngine  — produces a wave-based, topologically-ordered execution schedule
                   from a backlog and a dependency registry.
AssignmentEngine — binds backlog items to agents and tracks those bindings.

``Scheduler`` remains available from the package root as a compatibility alias for
callers written before the class carried the ``Engine`` suffix the control-plane
registration taxonomy selects on.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from platform.universal_control_plane.errors import (
    AssignmentError,
    DuplicateObjectError,
    ObjectNotFoundError,
    SchedulerError,
)
from platform.universal_control_plane.ontology import (
    LIFECYCLE_ACTIVE,
    Assignment,
    BacklogItem,
    ScheduleEntry,
)
from platform.universal_control_plane.registry import (
    AgentRegistry,
    DependencyRegistry,
)
from typing import Any


@dataclass(frozen=True)
class Schedule:
    """An immutable, ordered execution schedule."""

    entries: tuple[ScheduleEntry, ...]
    wave_count: int
    tick: int = 0

    def for_wave(self, wave: int) -> list[ScheduleEntry]:
        return [e for e in self.entries if e.wave == wave]

    def for_agent(self, agent_id: str) -> list[ScheduleEntry]:
        return [e for e in self.entries if e.agent_id == agent_id]

    def to_dict(self) -> dict[str, Any]:
        return {
            "kind": "Schedule",
            "wave_count": self.wave_count,
            "total_entries": len(self.entries),
            "tick": self.tick,
            "entries": [e.to_dict() for e in self.entries],
        }


@dataclass
class SchedulerEngine:
    """Produces a wave-based schedule from items and dependency constraints.

    The scheduler assigns each backlog item a wave number such that all of a
    item's declared dependencies appear in earlier waves. Within a wave, items
    are ordered by priority then ID for determinism. Agent assignment is
    round-robin over active agents unless the caller supplies a mapping.
    """

    def schedule(
        self,
        items: list[BacklogItem],
        dep_registry: DependencyRegistry,
        agent_registry: AgentRegistry,
        *,
        agent_map: dict[str, str] | None = None,
        tick: int = 0,
    ) -> Schedule:
        """Produce a Schedule for *items* respecting *dep_registry* constraints."""
        if not items:
            return Schedule(entries=(), wave_count=0, tick=tick)

        active_agents = agent_registry.active()
        if not active_agents:
            raise SchedulerError("no active agents available for scheduling")

        item_ids = {i.item_id for i in items}
        item_map = {i.item_id: i for i in items}

        # Build a dependency sub-graph restricted to the items being scheduled.
        deps: dict[str, set[str]] = {iid: set() for iid in item_ids}
        for rec in dep_registry.all():
            if rec.from_id in item_ids and rec.to_id in item_ids and not rec.optional:
                deps[rec.from_id].add(rec.to_id)

        # Detect cycles in the restricted graph.
        #
        # THE TRAVERSAL IS SORTED, AND THAT IS A DETERMINISM FIX RATHER THAN A STYLE CHOICE.
        # `item_ids` and every value of `deps` are SETS, whose iteration order varies with
        # PYTHONHASHSEED — so the depth-first walk visited nodes in a different order on every
        # process. The schedule it produces was unaffected (wave numbers are a `max` over
        # dependencies, and each wave is re-sorted by priority then id), which is exactly why this
        # went unnoticed: nothing about the OUTPUT moved. What moved was the walk, and it surfaced
        # as the one row that differed between two whole-suite coverage reports over an identical
        # tree — `105->101` in one run and `103->101` in the next, same 108 statements, same 99%.
        # A verification artifact that changes between runs cannot be evidence of determinism, so
        # the order is made a property of the data rather than of the interpreter's hash seed.
        # It also fixes a real, if narrow, behavioural non-determinism: WHICH cycle is found first
        # in a graph containing several was previously a matter of hash seed.
        visited: set[str] = set()
        in_stack: set[str] = set()

        def _has_cycle(n: str) -> bool:
            visited.add(n)
            in_stack.add(n)
            for nb in sorted(deps.get(n, set())):
                if nb not in visited:
                    if _has_cycle(nb):
                        return True
                elif nb in in_stack:
                    return True
            in_stack.discard(n)
            return False

        for iid in sorted(item_ids):
            if iid not in visited and _has_cycle(iid):
                raise SchedulerError(
                    "dependency cycle detected among scheduled items; cannot schedule"
                )

        # Assign wave numbers: a node's wave = 1 + max(wave of its dependencies).
        wave: dict[str, int] = {}

        def _wave(iid: str) -> int:
            if iid in wave:
                return wave[iid]
            if not deps.get(iid):
                wave[iid] = 0
                return 0
            w = 1 + max(_wave(d) for d in deps[iid])
            wave[iid] = w
            return w

        for iid in sorted(item_ids):
            _wave(iid)

        # Sort items within each wave by priority then ID.
        _PRIO = {"CRITICAL": 0, "HIGH": 1, "MEDIUM": 2, "LOW": 3}
        waves: dict[int, list[BacklogItem]] = {}
        for iid, w in wave.items():
            waves.setdefault(w, []).append(item_map[iid])
        for w in waves:
            waves[w].sort(key=lambda i: (_PRIO.get(i.priority, 99), i.item_id))

        # Assign agents round-robin (or from caller-supplied map).
        entries: list[ScheduleEntry] = []
        agent_ids = [a.agent_id for a in active_agents]
        counter = 0
        position = 0

        for w in sorted(waves):
            for item in waves[w]:
                if agent_map and item.item_id in agent_map:
                    assigned = agent_map[item.item_id]
                else:
                    assigned = agent_ids[counter % len(agent_ids)]
                    counter += 1
                entry_id = f"SE-{item.item_id}-W{w}-P{position}"
                entries.append(
                    ScheduleEntry(
                        entry_id=entry_id,
                        item_id=item.item_id,
                        agent_id=assigned,
                        position=position,
                        wave=w,
                        tick=tick,
                    )
                )
                position += 1

        return Schedule(
            entries=tuple(entries),
            wave_count=len(waves),
            tick=tick,
        )


# ---------------------------------------------------------------------------
# Assignment Engine
# ---------------------------------------------------------------------------


@dataclass
class AssignmentEngine:
    """Governs and tracks item-to-agent assignments."""

    _assignments: dict[str, Assignment] = field(default_factory=dict)
    # item_id → assignment_id (one active assignment per item)
    _by_item: dict[str, str] = field(default_factory=dict)

    def assign(self, assignment: Assignment) -> Assignment:
        if assignment.assignment_id in self._assignments:
            raise DuplicateObjectError(f"assignment already exists: {assignment.assignment_id}")
        if assignment.item_id in self._by_item:
            existing = self._assignments[self._by_item[assignment.item_id]]
            if existing.state == LIFECYCLE_ACTIVE:
                raise AssignmentError(
                    f"item {assignment.item_id!r} already has an active assignment; "
                    "complete or cancel the existing one first"
                )
        self._assignments[assignment.assignment_id] = assignment
        self._by_item[assignment.item_id] = assignment.assignment_id
        return assignment

    def get(self, assignment_id: str) -> Assignment:
        if assignment_id not in self._assignments:
            raise ObjectNotFoundError(f"assignment not found: {assignment_id}")
        return self._assignments[assignment_id]

    def for_item(self, item_id: str) -> Assignment | None:
        aid = self._by_item.get(item_id)
        return self._assignments[aid] if aid else None

    def for_agent(self, agent_id: str) -> list[Assignment]:
        return [a for a in self._assignments.values() if a.agent_id == agent_id]

    def active(self) -> list[Assignment]:
        return [a for a in self._assignments.values() if a.state == LIFECYCLE_ACTIVE]

    def count(self) -> int:
        return len(self._assignments)

    def to_dict(self) -> dict[str, Any]:
        return {
            "engine": "AssignmentEngine",
            "total": self.count(),
            "active": len(self.active()),
            "assignments": [a.to_dict() for a in self._assignments.values()],
        }
