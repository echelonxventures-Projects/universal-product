"""UCOS-CTRL-000001 — Plan, Roadmap, Backlog, and Milestone Engines.

Four engines that together constitute the Universal Master Plan layer:

    PlanEngine        — the master plan over all universes
    RoadmapEngine     — milestones sequenced along a logical timeline
    BacklogEngine     — ordered, prioritised backlog of work items
    MilestoneEngine   — milestone lifecycle and readiness measurement

All engines are stateless over pure registries; they read and produce
value objects without consulting the clock.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from platform.universal_control_plane.errors import (
    DuplicateObjectError,
    ObjectNotFoundError,
    RegistrationError,
)
from platform.universal_control_plane.ontology import (
    LIFECYCLE_ACTIVE,
    LIFECYCLE_COMPLETE,
    LIFECYCLE_DRAFT,
    PRIORITY_CRITICAL,
    PRIORITY_HIGH,
    BacklogItem,
    Goal,
    Milestone,
    Objective,
    Vision,
)
from typing import Any

_PRIORITY_ORDER = {PRIORITY_CRITICAL: 0, PRIORITY_HIGH: 1, "MEDIUM": 2, "LOW": 3}


# ---------------------------------------------------------------------------
# Plan Engine (Master Plan)
# ---------------------------------------------------------------------------


@dataclass
class PlanEngine:
    """The Universal Master Plan: visions, goals, objectives, and their ordering."""

    _visions: dict[str, Vision] = field(default_factory=dict)
    _goals: dict[str, Goal] = field(default_factory=dict)
    _objectives: dict[str, Objective] = field(default_factory=dict)

    # -- Registration --

    def register_vision(self, vision: Vision) -> Vision:
        if vision.vision_id in self._visions:
            raise DuplicateObjectError(f"vision already registered: {vision.vision_id}")
        self._visions[vision.vision_id] = vision
        return vision

    def register_goal(self, goal: Goal) -> Goal:
        if goal.goal_id in self._goals:
            raise DuplicateObjectError(f"goal already registered: {goal.goal_id}")
        if goal.vision_id not in self._visions:
            raise RegistrationError(
                f"vision {goal.vision_id!r} not registered; register it before its goals"
            )
        self._goals[goal.goal_id] = goal
        return goal

    def register_objective(self, obj: Objective) -> Objective:
        if obj.objective_id in self._objectives:
            raise DuplicateObjectError(f"objective already registered: {obj.objective_id}")
        if obj.goal_id not in self._goals:
            raise RegistrationError(
                f"goal {obj.goal_id!r} not registered; register it before its objectives"
            )
        self._objectives[obj.objective_id] = obj
        return obj

    # -- Retrieval --

    def get_vision(self, vision_id: str) -> Vision:
        if vision_id not in self._visions:
            raise ObjectNotFoundError(f"vision not found: {vision_id}")
        return self._visions[vision_id]

    def get_goal(self, goal_id: str) -> Goal:
        if goal_id not in self._goals:
            raise ObjectNotFoundError(f"goal not found: {goal_id}")
        return self._goals[goal_id]

    def get_objective(self, objective_id: str) -> Objective:
        if objective_id not in self._objectives:
            raise ObjectNotFoundError(f"objective not found: {objective_id}")
        return self._objectives[objective_id]

    # -- Queries --

    def goals_for_vision(self, vision_id: str) -> list[Goal]:
        return sorted(
            [g for g in self._goals.values() if g.vision_id == vision_id],
            key=lambda g: (_PRIORITY_ORDER.get(g.priority, 99), g.goal_id),
        )

    def objectives_for_goal(self, goal_id: str) -> list[Objective]:
        return sorted(
            [o for o in self._objectives.values() if o.goal_id == goal_id],
            key=lambda o: (_PRIORITY_ORDER.get(o.priority, 99), o.objective_id),
        )

    def active_objectives(self) -> list[Objective]:
        return [o for o in self._objectives.values() if o.state == LIFECYCLE_ACTIVE]

    def completion_rate(self) -> float:
        """Fraction of objectives in COMPLETE state."""
        total = len(self._objectives)
        if total == 0:
            return 0.0
        done = sum(1 for o in self._objectives.values() if o.state == LIFECYCLE_COMPLETE)
        return round(done / total, 4)

    def to_dict(self) -> dict[str, Any]:
        return {
            "engine": "PlanEngine",
            "visions": len(self._visions),
            "goals": len(self._goals),
            "objectives": len(self._objectives),
            "completion_rate": self.completion_rate(),
            "plan": [
                {
                    "vision": v.to_dict(),
                    "goals": [
                        {
                            "goal": g.to_dict(),
                            "objectives": [
                                o.to_dict() for o in self.objectives_for_goal(g.goal_id)
                            ],
                        }
                        for g in self.goals_for_vision(v.vision_id)
                    ],
                }
                for v in self._visions.values()
            ],
        }


# ---------------------------------------------------------------------------
# Roadmap Engine
# ---------------------------------------------------------------------------


@dataclass
class RoadmapEngine:
    """Milestones arranged in logical sequence along the universal roadmap."""

    _milestones: dict[str, Milestone] = field(default_factory=dict)

    def register(self, milestone: Milestone) -> Milestone:
        if milestone.milestone_id in self._milestones:
            raise DuplicateObjectError(f"milestone already registered: {milestone.milestone_id}")
        self._milestones[milestone.milestone_id] = milestone
        return milestone

    def get(self, milestone_id: str) -> Milestone:
        if milestone_id not in self._milestones:
            raise ObjectNotFoundError(f"milestone not found: {milestone_id}")
        return self._milestones[milestone_id]

    def ordered(self) -> list[Milestone]:
        """Return milestones sorted by logical sequence, then by ID for determinism."""
        return sorted(self._milestones.values(), key=lambda m: (m.sequence, m.milestone_id))

    def by_universe(self, universe_id: str) -> list[Milestone]:
        return [m for m in self.ordered() if m.universe_id == universe_id]

    def next_milestone(self, universe_id: str) -> Milestone | None:
        """The first non-COMPLETE milestone for *universe_id* in sequence order."""
        for m in self.by_universe(universe_id):
            if m.state != LIFECYCLE_COMPLETE:
                return m
        return None

    def completion_rate(self, universe_id: str | None = None) -> float:
        pool = self.by_universe(universe_id) if universe_id else list(self._milestones.values())
        if not pool:
            return 0.0
        done = sum(1 for m in pool if m.state == LIFECYCLE_COMPLETE)
        return round(done / len(pool), 4)

    def count(self) -> int:
        return len(self._milestones)

    def to_dict(self) -> dict[str, Any]:
        return {
            "engine": "RoadmapEngine",
            "total_milestones": self.count(),
            "milestones": [m.to_dict() for m in self.ordered()],
        }


# ---------------------------------------------------------------------------
# Backlog Engine
# ---------------------------------------------------------------------------


@dataclass
class BacklogEngine:
    """Ordered, prioritised universal backlog of work items."""

    _items: dict[str, BacklogItem] = field(default_factory=dict)

    def add(self, item: BacklogItem) -> BacklogItem:
        if item.item_id in self._items:
            raise DuplicateObjectError(f"backlog item already exists: {item.item_id}")
        self._items[item.item_id] = item
        return item

    def get(self, item_id: str) -> BacklogItem:
        if item_id not in self._items:
            raise ObjectNotFoundError(f"backlog item not found: {item_id}")
        return self._items[item_id]

    def ordered(self) -> list[BacklogItem]:
        """Priority-ordered backlog: CRITICAL → HIGH → MEDIUM → LOW, then by ID."""
        return sorted(
            self._items.values(),
            key=lambda i: (_PRIORITY_ORDER.get(i.priority, 99), i.item_id),
        )

    def ready(self) -> list[BacklogItem]:
        """Items in DRAFT state, ready to be activated."""
        return [i for i in self.ordered() if i.state == LIFECYCLE_DRAFT]

    def active(self) -> list[BacklogItem]:
        return [i for i in self.ordered() if i.state == LIFECYCLE_ACTIVE]

    def for_milestone(self, milestone_id: str) -> list[BacklogItem]:
        return [i for i in self.ordered() if i.milestone_id == milestone_id]

    def for_universe(self, universe_id: str) -> list[BacklogItem]:
        return [i for i in self.ordered() if i.universe_id == universe_id]

    def total_estimate(self) -> int:
        return sum(i.estimate for i in self._items.values())

    def count(self) -> int:
        return len(self._items)

    def to_dict(self) -> dict[str, Any]:
        return {
            "engine": "BacklogEngine",
            "count": self.count(),
            "total_estimate": self.total_estimate(),
            "items": [i.to_dict() for i in self.ordered()],
        }
