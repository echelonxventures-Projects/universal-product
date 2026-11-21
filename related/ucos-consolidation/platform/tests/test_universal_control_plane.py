"""UCOS-CTRL-000001 — Universal Control Plane test suite.

Covers all engines: ontology, state, registries, plan, roadmap, backlog,
scheduler, assignment, prompt, progress, metrics, dashboard, determination,
decision, history, replay, evidence, and CLI surface.
"""

from __future__ import annotations

import io
import json
from platform.tests.control_plane_helpers import FIXTURE_ARTIFACTS, build_substrate
from platform.universal_control_plane import (
    DEFAULT_LIFECYCLE,
    LIFECYCLE_ACTIVE,
    LIFECYCLE_ARCHIVED,
    LIFECYCLE_CANCELLED,
    LIFECYCLE_COMPLETE,
    LIFECYCLE_DRAFT,
    AgentRecord,
    AgentRegistry,
    Assignment,
    AssignmentEngine,
    AssignmentError,
    BacklogEngine,
    BacklogItem,
    Capability,
    CapabilityRegistry,
    ControlPlane,
    DashboardEngine,
    Decision,
    DecisionEngine,
    DependencyRecord,
    DependencyRegistry,
    Determination,
    DeterminationEngine,
    DeterminationError,
    DuplicateObjectError,
    Evidence,
    EvidenceEngine,
    EvidenceError,
    Goal,
    HistoryEngine,
    HistoryEntry,
    MetricsEngine,
    Milestone,
    Objective,
    ObjectNotFoundError,
    OwnershipRecord,
    OwnershipRegistry,
    PlanEngine,
    ProgressEngine,
    PromptEngine,
    PromptRenderError,
    RegistrationError,
    ReplayEngine,
    ReplayError,
    ReplayRecord,
    RoadmapEngine,
    Scheduler,
    SchedulerError,
    StateEngine,
    StateTransitionError,
    Universe,
    Vision,
)
from platform.universal_control_plane import cli as cli_mod
from platform.universal_control_plane.cli import main as cli_main
from platform.universal_control_plane.cli import run as cli_run
from platform.universal_control_plane.ontology import ProgressRecord

import pytest

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

UID = "UCOS-CTRL-TEST-001"


@pytest.fixture
def cap():
    return Capability(capability_id="CAP-001", universe_id=UID, name="Test Capability")


@pytest.fixture
def agent():
    return AgentRecord(agent_id="AGT-001", name="Alpha Agent", capabilities=("CAP-001",))


@pytest.fixture
def item():
    return BacklogItem(
        item_id="BLI-001",
        universe_id=UID,
        title="Implement X",
        priority="HIGH",
        estimate=3,
    )


@pytest.fixture
def agt_reg(agent):
    r = AgentRegistry()
    r.register(agent)
    return r


@pytest.fixture
def dep_reg():
    return DependencyRegistry()


# ---------------------------------------------------------------------------
# Ontology
# ---------------------------------------------------------------------------


class TestOntology:
    def test_identity_deterministic(self):
        u1 = Universe(universe_id=UID, name="T", tick=0)
        u2 = Universe(universe_id=UID, name="T", tick=0)
        assert u1.identity == u2.identity

    def test_tick_differentiates_identity(self):
        u1 = Universe(universe_id=UID, name="T", tick=0)
        u2 = Universe(universe_id=UID, name="T", tick=1)
        assert u1.identity != u2.identity

    def test_universe_to_dict(self):
        d = Universe(universe_id=UID, name="T").to_dict()
        assert d["kind"] == "Universe"
        assert d["universe_id"] == UID
        assert "identity" in d

    def test_progress_record_percentage(self):
        pr = ProgressRecord(record_id="R1", subject_id="S1", total=10, completed=7)
        assert abs(pr.percentage - 70.0) < 0.01

    def test_progress_record_zero_total(self):
        pr = ProgressRecord(record_id="R2", subject_id="S1", total=0, completed=0)
        assert pr.percentage == 0.0

    def test_all_objects_have_identity_and_to_dict(self):
        objs = [
            Capability(capability_id="C1", universe_id=UID, name="N"),
            AgentRecord(agent_id="A1", name="N"),
            Vision(vision_id="V1", universe_id=UID, statement="S"),
            Goal(goal_id="G1", vision_id="V1", title="T"),
            Objective(objective_id="O1", goal_id="G1", title="T", success_criteria="SC"),
            Milestone(milestone_id="M1", universe_id=UID, title="T"),
            Assignment(assignment_id="AS1", item_id="I1", agent_id="A1"),
            Determination(determination_id="D1", subject_id="S1", verdict="OK", rationale="R"),
            Decision(decision_id="DC1", subject_id="S1", title="T", choice="C", rationale="R"),
            Evidence(evidence_id="E1", subject_id="S1", kind="TEST", claim="C", payload_digest="d"),
            HistoryEntry(entry_id="H1", subject_id="S1", event="EV"),
            ReplayRecord(replay_id="RP1", subject_id="S1", inputs_digest="i", outputs_digest="o"),
        ]
        for obj in objs:
            assert obj.identity, f"{type(obj).__name__} has no identity"
            d = obj.to_dict()
            assert "kind" in d
            assert "identity" in d


# ---------------------------------------------------------------------------
# StateEngine
# ---------------------------------------------------------------------------


class TestStateEngine:
    def test_default_transitions_present(self):
        eng = StateEngine()
        assert eng.can_transition(LIFECYCLE_DRAFT, "ACTIVATE")
        assert eng.can_transition(LIFECYCLE_ACTIVE, "COMPLETE")

    def test_transition_returns_next_state(self):
        eng = StateEngine()
        assert eng.transition(LIFECYCLE_DRAFT, "ACTIVATE") == LIFECYCLE_ACTIVE

    def test_unknown_transition_raises(self):
        eng = StateEngine()
        with pytest.raises(StateTransitionError):
            eng.transition(LIFECYCLE_COMPLETE, "ACTIVATE")

    def test_register_custom_transition(self):
        eng = StateEngine()
        eng.register_state("REVIEWING")
        eng.register_transition(LIFECYCLE_ACTIVE, "REVIEW", "REVIEWING")
        assert eng.transition(LIFECYCLE_ACTIVE, "REVIEW") == "REVIEWING"

    def test_permitted_events(self):
        eng = StateEngine()
        events = eng.permitted_events(LIFECYCLE_ACTIVE)
        assert "COMPLETE" in events
        assert "PAUSE" in events

    def test_to_dict_structure(self):
        eng = StateEngine()
        d = eng.to_dict()
        assert "states" in d
        assert "transitions" in d
        assert len(d["transitions"]) > 0

    def test_register_state_empty_raises(self):
        eng = StateEngine()
        with pytest.raises(ValueError):
            eng.register_state("")

    def test_register_transition_admits_unknown_states(self):
        eng = StateEngine()
        eng.register_transition("QUEUED", "START", "RUNNING")
        assert {"QUEUED", "RUNNING"} <= eng.states
        assert eng.transition("QUEUED", "START") == "RUNNING"

    def test_register_transition_overwrites_prior_binding(self):
        eng = StateEngine()
        eng.register_transition(LIFECYCLE_DRAFT, "ACTIVATE", LIFECYCLE_CANCELLED)
        assert eng.transition(LIFECYCLE_DRAFT, "ACTIVATE") == LIFECYCLE_CANCELLED

    def test_states_property_holds_default_lifecycle(self):
        assert set(DEFAULT_LIFECYCLE) <= StateEngine().states

    def test_can_transition_false_for_unknown_event(self):
        assert not StateEngine().can_transition(LIFECYCLE_DRAFT, "NO_SUCH_EVENT")

    def test_permitted_events_empty_for_terminal_state(self):
        assert StateEngine().permitted_events(LIFECYCLE_ARCHIVED) == []

    def test_transitions_are_sorted(self):
        transitions = StateEngine().transitions()
        keys = [(t.from_state, t.event) for t in transitions]
        assert keys == sorted(keys)
        assert transitions[0].to_dict().keys() == {"from_state", "event", "to_state"}


# ---------------------------------------------------------------------------
# Registries
# ---------------------------------------------------------------------------


class TestCapabilityRegistry:
    def test_register_and_get(self, cap):
        r = CapabilityRegistry()
        r.register(cap)
        assert r.get("CAP-001").name == "Test Capability"

    def test_duplicate_raises(self, cap):
        r = CapabilityRegistry()
        r.register(cap)
        with pytest.raises(DuplicateObjectError):
            r.register(cap)

    def test_missing_raises(self):
        with pytest.raises(ObjectNotFoundError):
            CapabilityRegistry().get("MISSING")

    def test_by_universe(self, cap):
        r = CapabilityRegistry()
        r.register(cap)
        assert len(r.by_universe(UID)) == 1
        assert r.by_universe("OTHER") == []

    def test_empty_id_raises(self):
        r = CapabilityRegistry()
        with pytest.raises(RegistrationError):
            r.register(Capability(capability_id="", universe_id=UID, name="X"))

    def test_empty_universe_id_raises(self):
        r = CapabilityRegistry()
        with pytest.raises(RegistrationError):
            r.register(Capability(capability_id="C1", universe_id="  ", name="X"))

    def test_all_and_count(self, cap):
        r = CapabilityRegistry()
        r.register(cap)
        assert [c.capability_id for c in r.all()] == ["CAP-001"]
        assert r.count() == 1

    def test_to_dict_structure(self, cap):
        r = CapabilityRegistry()
        r.register(cap)
        d = r.to_dict()
        assert d["registry"] == "CapabilityRegistry"
        assert d["count"] == 1
        assert len(d["capabilities"]) == 1


def _own(ownership_id, capability_id, owner_id, owner_kind="Universe"):
    return OwnershipRecord(
        ownership_id=ownership_id,
        capability_id=capability_id,
        owner_id=owner_id,
        owner_kind=owner_kind,
    )


class TestOwnershipRegistry:
    def test_register_and_get(self):
        r = OwnershipRegistry()
        r.register(_own("O1", "C1", UID))
        assert r.get("O1").owner_id == UID

    def test_duplicate_raises(self):
        r = OwnershipRegistry()
        rec = _own("O1", "C1", UID)
        r.register(rec)
        with pytest.raises(DuplicateObjectError):
            r.register(rec)

    def test_two_owners_same_capability_raises(self):
        r = OwnershipRegistry()
        r.register(_own("O1", "C1", "X"))
        with pytest.raises(RegistrationError):
            r.register(_own("O2", "C1", "Y"))

    def test_owner_of(self):
        r = OwnershipRegistry()
        r.register(_own("O1", "C1", "X"))
        assert r.owner_of("C1").owner_id == "X"
        assert r.owner_of("NONE") is None

    def test_missing_raises(self):
        with pytest.raises(ObjectNotFoundError):
            OwnershipRegistry().get("MISSING")

    def test_by_owner(self):
        r = OwnershipRegistry()
        r.register(_own("O1", "C1", "X"))
        r.register(_own("O2", "C2", "Y"))
        assert len(r.by_owner("X")) == 1
        assert r.by_owner("NONE") == []

    def test_all_count_and_to_dict(self):
        r = OwnershipRegistry()
        r.register(_own("O1", "C1", "X"))
        assert len(r.all()) == 1
        assert r.count() == 1
        d = r.to_dict()
        assert d["registry"] == "OwnershipRegistry"
        assert len(d["records"]) == 1


class TestDependencyRegistry:
    def test_register_and_get(self):
        r = DependencyRegistry()
        rec = DependencyRecord(dependency_id="D1", from_id="A", to_id="B")
        r.register(rec)
        assert r.get("D1").from_id == "A"

    def test_self_dependency_raises(self):
        r = DependencyRegistry()
        with pytest.raises(RegistrationError):
            r.register(DependencyRecord(dependency_id="D1", from_id="A", to_id="A"))

    def test_no_cycle_detected(self):
        r = DependencyRegistry()
        r.register(DependencyRecord(dependency_id="D1", from_id="A", to_id="B"))
        r.register(DependencyRecord(dependency_id="D2", from_id="B", to_id="C"))
        assert not r.has_cycle()

    def test_cycle_detected(self):
        r = DependencyRegistry()
        r.register(DependencyRecord(dependency_id="D1", from_id="A", to_id="B"))
        r.register(DependencyRecord(dependency_id="D2", from_id="B", to_id="A"))
        assert r.has_cycle()

    def test_topological_order_acyclic(self):
        r = DependencyRegistry()
        r.register(DependencyRecord(dependency_id="D1", from_id="A", to_id="B"))
        r.register(DependencyRecord(dependency_id="D2", from_id="B", to_id="C"))
        order = r.topological_order()
        # "from REQUIRES to": C is required by B, which is required by A, so the
        # execution order is dependencies first.
        assert order.index("C") < order.index("B") < order.index("A")

    def test_topological_order_raises_on_cycle(self):
        r = DependencyRegistry()
        r.register(DependencyRecord(dependency_id="D1", from_id="A", to_id="B"))
        r.register(DependencyRecord(dependency_id="D2", from_id="B", to_id="A"))
        with pytest.raises(SchedulerError):
            r.topological_order()

    def test_dependencies_of_and_dependents_of(self):
        r = DependencyRegistry()
        r.register(DependencyRecord(dependency_id="D1", from_id="A", to_id="B"))
        assert len(r.dependencies_of("A")) == 1
        assert len(r.dependents_of("B")) == 1
        assert r.dependencies_of("B") == []

    def test_duplicate_raises(self):
        r = DependencyRegistry()
        rec = DependencyRecord(dependency_id="D1", from_id="A", to_id="B")
        r.register(rec)
        with pytest.raises(DuplicateObjectError):
            r.register(rec)

    def test_missing_raises(self):
        with pytest.raises(ObjectNotFoundError):
            DependencyRegistry().get("MISSING")

    def test_diamond_dependency_has_no_cycle(self):
        r = DependencyRegistry()
        r.register(DependencyRecord(dependency_id="D1", from_id="A", to_id="B"))
        r.register(DependencyRecord(dependency_id="D2", from_id="A", to_id="C"))
        r.register(DependencyRecord(dependency_id="D3", from_id="B", to_id="D"))
        r.register(DependencyRecord(dependency_id="D4", from_id="C", to_id="D"))
        assert not r.has_cycle()
        order = r.topological_order()
        # Dependencies first: D is required by both B and C, which A requires.
        assert order.index("D") < order.index("B")
        assert order.index("D") < order.index("C")
        assert order.index("B") < order.index("A")
        assert order.index("C") < order.index("A")

    def test_record_to_dict_and_identity(self):
        rec = DependencyRecord(dependency_id="D1", from_id="A", to_id="B", optional=True)
        d = rec.to_dict()
        assert rec.identity
        assert d["kind"] == "DependencyRecord"
        assert d["dependency_kind"] == "REQUIRES"
        assert d["optional"] is True

    def test_all_count_and_to_dict(self):
        r = DependencyRegistry()
        r.register(DependencyRecord(dependency_id="D1", from_id="A", to_id="B"))
        assert len(r.all()) == 1
        assert r.count() == 1
        d = r.to_dict()
        assert d["registry"] == "DependencyRegistry"
        assert d["has_cycle"] is False


class TestAgentRegistry:
    def test_register_and_get(self, agent):
        r = AgentRegistry()
        r.register(agent)
        assert r.get("AGT-001").name == "Alpha Agent"

    def test_duplicate_raises(self, agent):
        r = AgentRegistry()
        r.register(agent)
        with pytest.raises(DuplicateObjectError):
            r.register(agent)

    def test_by_capability(self, agent):
        r = AgentRegistry()
        r.register(agent)
        assert len(r.by_capability("CAP-001")) == 1
        assert r.by_capability("OTHER") == []

    def test_active_excludes_inactive(self):
        r = AgentRegistry()
        r.register(AgentRecord(agent_id="A1", name="Active", state=LIFECYCLE_ACTIVE))
        r.register(AgentRecord(agent_id="A2", name="Done", state=LIFECYCLE_COMPLETE))
        assert len(r.active()) == 1

    def test_missing_raises(self):
        with pytest.raises(ObjectNotFoundError):
            AgentRegistry().get("MISSING")

    def test_empty_id_raises(self):
        with pytest.raises(RegistrationError):
            AgentRegistry().register(AgentRecord(agent_id="  ", name="X"))

    def test_all_count_and_to_dict(self, agent):
        r = AgentRegistry()
        r.register(agent)
        assert len(r.all()) == 1
        assert r.count() == 1
        d = r.to_dict()
        assert d["registry"] == "AgentRegistry"
        assert len(d["agents"]) == 1


# ---------------------------------------------------------------------------
# Plan / Roadmap / Backlog
# ---------------------------------------------------------------------------


class TestPlanEngine:
    def setup_method(self):
        self.eng = PlanEngine()
        self.eng.register_vision(Vision(vision_id="V1", universe_id=UID, statement="S"))
        self.eng.register_goal(Goal(goal_id="G1", vision_id="V1", title="G"))
        self.eng.register_objective(
            Objective(objective_id="O1", goal_id="G1", title="T", success_criteria="SC")
        )

    def test_goals_for_vision(self):
        assert len(self.eng.goals_for_vision("V1")) == 1

    def test_objectives_for_goal(self):
        assert len(self.eng.objectives_for_goal("G1")) == 1

    def test_duplicate_vision_raises(self):
        with pytest.raises(DuplicateObjectError):
            self.eng.register_vision(Vision(vision_id="V1", universe_id=UID, statement="S"))

    def test_goal_missing_vision_raises(self):
        with pytest.raises(RegistrationError):
            self.eng.register_goal(Goal(goal_id="G99", vision_id="MISSING", title="T"))

    def test_completion_rate_zero(self):
        assert self.eng.completion_rate() == 0.0

    def test_to_dict_structure(self):
        d = self.eng.to_dict()
        assert d["visions"] == 1
        assert d["goals"] == 1
        assert d["objectives"] == 1

    def test_duplicate_goal_raises(self):
        with pytest.raises(DuplicateObjectError):
            self.eng.register_goal(Goal(goal_id="G1", vision_id="V1", title="G"))

    def test_duplicate_objective_raises(self):
        with pytest.raises(DuplicateObjectError):
            self.eng.register_objective(
                Objective(objective_id="O1", goal_id="G1", title="T", success_criteria="SC")
            )

    def test_objective_missing_goal_raises(self):
        with pytest.raises(RegistrationError):
            self.eng.register_objective(
                Objective(objective_id="O99", goal_id="MISSING", title="T", success_criteria="SC")
            )

    def test_getters_return_registered_objects(self):
        assert self.eng.get_vision("V1").statement == "S"
        assert self.eng.get_goal("G1").title == "G"
        assert self.eng.get_objective("O1").success_criteria == "SC"

    def test_get_vision_missing_raises(self):
        with pytest.raises(ObjectNotFoundError):
            self.eng.get_vision("MISSING")

    def test_get_goal_missing_raises(self):
        with pytest.raises(ObjectNotFoundError):
            self.eng.get_goal("MISSING")

    def test_get_objective_missing_raises(self):
        with pytest.raises(ObjectNotFoundError):
            self.eng.get_objective("MISSING")

    def test_objectives_ordered_by_priority(self):
        self.eng.register_objective(
            Objective(
                objective_id="O2",
                goal_id="G1",
                title="T",
                success_criteria="SC",
                priority="CRITICAL",
            )
        )
        ordered = self.eng.objectives_for_goal("G1")
        assert [o.objective_id for o in ordered] == ["O2", "O1"]

    def test_active_objectives(self):
        assert self.eng.active_objectives() == []
        self.eng.register_objective(
            Objective(
                objective_id="O2",
                goal_id="G1",
                title="T",
                success_criteria="SC",
                state=LIFECYCLE_ACTIVE,
            )
        )
        assert len(self.eng.active_objectives()) == 1

    def test_completion_rate_counts_complete_objectives(self):
        self.eng.register_objective(
            Objective(
                objective_id="O2",
                goal_id="G1",
                title="T",
                success_criteria="SC",
                state=LIFECYCLE_COMPLETE,
            )
        )
        assert self.eng.completion_rate() == 0.5

    def test_completion_rate_empty_plan(self):
        assert PlanEngine().completion_rate() == 0.0

    def test_goals_and_objectives_for_unknown_parent(self):
        assert self.eng.goals_for_vision("NONE") == []
        assert self.eng.objectives_for_goal("NONE") == []


class TestRoadmapEngine:
    def test_register_and_ordered(self):
        eng = RoadmapEngine()
        eng.register(Milestone(milestone_id="M2", universe_id=UID, title="B", sequence=2))
        eng.register(Milestone(milestone_id="M1", universe_id=UID, title="A", sequence=1))
        ordered = eng.ordered()
        assert ordered[0].milestone_id == "M1"

    def test_next_milestone(self):
        eng = RoadmapEngine()
        eng.register(Milestone(milestone_id="M1", universe_id=UID, title="A", sequence=1))
        nxt = eng.next_milestone(UID)
        assert nxt.milestone_id == "M1"

    def test_completion_rate(self):
        eng = RoadmapEngine()
        eng.register(
            Milestone(
                milestone_id="M1", universe_id=UID, title="A", state=LIFECYCLE_COMPLETE, sequence=1
            )
        )
        eng.register(Milestone(milestone_id="M2", universe_id=UID, title="B", sequence=2))
        assert eng.completion_rate(UID) == 0.5

    def test_duplicate_raises(self):
        eng = RoadmapEngine()
        m = Milestone(milestone_id="M1", universe_id=UID, title="A", sequence=1)
        eng.register(m)
        with pytest.raises(DuplicateObjectError):
            eng.register(m)

    def test_get_and_missing_raises(self):
        eng = RoadmapEngine()
        eng.register(Milestone(milestone_id="M1", universe_id=UID, title="A", sequence=1))
        assert eng.get("M1").title == "A"
        with pytest.raises(ObjectNotFoundError):
            eng.get("MISSING")

    def test_by_universe_filters(self):
        eng = RoadmapEngine()
        eng.register(Milestone(milestone_id="M1", universe_id=UID, title="A", sequence=1))
        eng.register(Milestone(milestone_id="M2", universe_id="OTHER", title="B", sequence=2))
        assert len(eng.by_universe(UID)) == 1
        assert eng.by_universe("NONE") == []

    def test_next_milestone_skips_complete(self):
        eng = RoadmapEngine()
        eng.register(
            Milestone(
                milestone_id="M1", universe_id=UID, title="A", state=LIFECYCLE_COMPLETE, sequence=1
            )
        )
        eng.register(Milestone(milestone_id="M2", universe_id=UID, title="B", sequence=2))
        assert eng.next_milestone(UID).milestone_id == "M2"

    def test_next_milestone_none_when_all_complete(self):
        eng = RoadmapEngine()
        eng.register(
            Milestone(
                milestone_id="M1", universe_id=UID, title="A", state=LIFECYCLE_COMPLETE, sequence=1
            )
        )
        assert eng.next_milestone(UID) is None
        assert eng.next_milestone("NONE") is None

    def test_completion_rate_over_all_universes(self):
        eng = RoadmapEngine()
        eng.register(
            Milestone(
                milestone_id="M1", universe_id=UID, title="A", state=LIFECYCLE_COMPLETE, sequence=1
            )
        )
        eng.register(Milestone(milestone_id="M2", universe_id="OTHER", title="B", sequence=2))
        assert eng.completion_rate() == 0.5

    def test_completion_rate_empty_pool(self):
        assert RoadmapEngine().completion_rate() == 0.0
        assert RoadmapEngine().completion_rate("NONE") == 0.0

    def test_count_and_to_dict(self):
        eng = RoadmapEngine()
        eng.register(Milestone(milestone_id="M1", universe_id=UID, title="A", sequence=1))
        assert eng.count() == 1
        d = eng.to_dict()
        assert d["engine"] == "RoadmapEngine"
        assert d["total_milestones"] == 1
        assert len(d["milestones"]) == 1


class TestBacklogEngine:
    def test_ordered_by_priority(self):
        eng = BacklogEngine()
        eng.add(BacklogItem(item_id="B1", universe_id=UID, title="T", priority="LOW"))
        eng.add(BacklogItem(item_id="B2", universe_id=UID, title="T", priority="CRITICAL"))
        ordered = eng.ordered()
        assert ordered[0].item_id == "B2"

    def test_ready_returns_draft(self, item):
        eng = BacklogEngine()
        eng.add(item)
        assert len(eng.ready()) == 1

    def test_total_estimate(self):
        eng = BacklogEngine()
        eng.add(BacklogItem(item_id="B1", universe_id=UID, title="T", estimate=5))
        eng.add(BacklogItem(item_id="B2", universe_id=UID, title="T", estimate=3))
        assert eng.total_estimate() == 8

    def test_duplicate_raises(self, item):
        eng = BacklogEngine()
        eng.add(item)
        with pytest.raises(DuplicateObjectError):
            eng.add(item)

    def test_get_and_missing_raises(self, item):
        eng = BacklogEngine()
        eng.add(item)
        assert eng.get(item.item_id).title == "Implement X"
        with pytest.raises(ObjectNotFoundError):
            eng.get("MISSING")

    def test_unknown_priority_sorts_last(self):
        eng = BacklogEngine()
        eng.add(BacklogItem(item_id="B1", universe_id=UID, title="T", priority="WHENEVER"))
        eng.add(BacklogItem(item_id="B2", universe_id=UID, title="T", priority="LOW"))
        assert [i.item_id for i in eng.ordered()] == ["B2", "B1"]

    def test_active_excludes_draft(self):
        eng = BacklogEngine()
        eng.add(BacklogItem(item_id="B1", universe_id=UID, title="T"))
        eng.add(BacklogItem(item_id="B2", universe_id=UID, title="T", state=LIFECYCLE_ACTIVE))
        assert [i.item_id for i in eng.active()] == ["B2"]
        assert [i.item_id for i in eng.ready()] == ["B1"]

    def test_for_milestone(self):
        eng = BacklogEngine()
        eng.add(BacklogItem(item_id="B1", universe_id=UID, title="T", milestone_id="MS-001"))
        eng.add(BacklogItem(item_id="B2", universe_id=UID, title="T"))
        assert len(eng.for_milestone("MS-001")) == 1
        assert eng.for_milestone("NONE") == []

    def test_for_universe(self):
        eng = BacklogEngine()
        eng.add(BacklogItem(item_id="B1", universe_id=UID, title="T"))
        eng.add(BacklogItem(item_id="B2", universe_id="OTHER", title="T"))
        assert len(eng.for_universe(UID)) == 1
        assert eng.for_universe("NONE") == []

    def test_count_and_to_dict(self, item):
        eng = BacklogEngine()
        eng.add(item)
        assert eng.count() == 1
        d = eng.to_dict()
        assert d["engine"] == "BacklogEngine"
        assert d["count"] == 1
        assert d["total_estimate"] == 3


# ---------------------------------------------------------------------------
# Scheduler + Assignment
# ---------------------------------------------------------------------------


class TestScheduler:
    def test_basic_schedule(self, item, agt_reg, dep_reg):
        sched = Scheduler().schedule([item], dep_reg, agt_reg)
        assert len(sched.entries) == 1
        assert sched.entries[0].item_id == "BLI-001"

    def test_empty_items_returns_empty_schedule(self, agt_reg, dep_reg):
        sched = Scheduler().schedule([], dep_reg, agt_reg)
        assert len(sched.entries) == 0
        assert sched.wave_count == 0

    def test_no_active_agents_raises(self, item, dep_reg):
        empty_reg = AgentRegistry()
        with pytest.raises(SchedulerError):
            Scheduler().schedule([item], dep_reg, empty_reg)

    def test_dependency_respected_in_waves(self, agt_reg):
        dep_reg = DependencyRegistry()
        dep_reg.register(DependencyRecord(dependency_id="D1", from_id="BLI-002", to_id="BLI-001"))
        items = [
            BacklogItem(item_id="BLI-001", universe_id=UID, title="A"),
            BacklogItem(item_id="BLI-002", universe_id=UID, title="B"),
        ]
        sched = Scheduler().schedule(items, dep_reg, agt_reg)
        waves = {e.item_id: e.wave for e in sched.entries}
        assert waves["BLI-001"] < waves["BLI-002"]

    def test_cycle_raises(self, agt_reg):
        dep_reg = DependencyRegistry()
        dep_reg.register(DependencyRecord(dependency_id="D1", from_id="A", to_id="B"))
        dep_reg.register(DependencyRecord(dependency_id="D2", from_id="B", to_id="A"))
        items = [
            BacklogItem(item_id="A", universe_id=UID, title="A"),
            BacklogItem(item_id="B", universe_id=UID, title="B"),
        ]
        with pytest.raises(SchedulerError):
            Scheduler().schedule(items, dep_reg, agt_reg)

    def test_the_cycle_walk_iterates_in_a_sorted_order(self):
        """Determinism of the WALK, which no test of the schedule output can reach.

        THE DEFECT. ``item_ids`` and every value of ``deps`` are sets, and the cycle walk iterated
        them directly, so its depth-first order was a function of PYTHONHASHSEED.

        WHY THIS TEST IS STRUCTURAL, AND WHY THE OBVIOUS TEST IS WORTHLESS HERE. The first version
        of this test ran ``schedule()`` under three hash seeds and compared the results. It passed
        against the BROKEN code, because the schedule genuinely is order-independent: a wave number
        is a ``max`` over dependencies, and each wave is re-sorted by priority then id before it is
        emitted. That is exactly why the defect survived — the output was stable while the traversal
        wandered, so every behavioural test agreed.

        What actually moved was a VERIFICATION ARTIFACT. Two whole-suite coverage reports taken over
        an identical tree differed by one row on this module, ``105->101`` against
        ``103->101``, with the same 108 statements and the same 99%. A report that changes between
        runs cannot be
        evidence of determinism, which is the guarantee this walk has to carry.

        So the property is asserted where it lives — in the source, over the parsed function rather
        than a text search, so a rename cannot quietly satisfy it.
        """
        import ast
        import inspect
        import textwrap

        tree = ast.parse(textwrap.dedent(inspect.getsource(Scheduler.schedule)))
        unsorted = []
        for node in ast.walk(tree):
            if not isinstance(node, ast.For):
                continue
            iterated = node.iter
            if isinstance(iterated, ast.Call) and getattr(iterated.func, "id", "") == "sorted":
                continue
            rendered = ast.unparse(iterated)
            # The set-valued iterables here: the id population and the adjacency map.
            if "item_ids" in rendered or "deps" in rendered:
                unsorted.append(f"line {node.lineno}: for ... in {rendered}")
        assert not unsorted, (
            "Scheduler.schedule iterates a set without sorting it, so its traversal order is a "
            f"function of PYTHONHASHSEED again: {unsorted}"
        )

    def test_schedule_to_dict(self, item, agt_reg, dep_reg):
        sched = Scheduler().schedule([item], dep_reg, agt_reg)
        d = sched.to_dict()
        assert d["total_entries"] == 1
        assert d["wave_count"] == 1

    def test_for_wave_and_for_agent(self, agt_reg):
        dep_reg = DependencyRegistry()
        dep_reg.register(DependencyRecord(dependency_id="D1", from_id="BLI-002", to_id="BLI-001"))
        items = [
            BacklogItem(item_id="BLI-001", universe_id=UID, title="A"),
            BacklogItem(item_id="BLI-002", universe_id=UID, title="B"),
        ]
        sched = Scheduler().schedule(items, dep_reg, agt_reg)
        assert [e.item_id for e in sched.for_wave(0)] == ["BLI-001"]
        assert [e.item_id for e in sched.for_wave(1)] == ["BLI-002"]
        assert sched.for_wave(9) == []
        assert len(sched.for_agent("AGT-001")) == 2
        assert sched.for_agent("NOBODY") == []

    def test_agent_map_pins_assignment(self, agt_reg):
        agt_reg.register(AgentRecord(agent_id="AGT-002", name="Beta"))
        items = [
            BacklogItem(item_id="BLI-001", universe_id=UID, title="A"),
            BacklogItem(item_id="BLI-002", universe_id=UID, title="B"),
        ]
        sched = Scheduler().schedule(
            items, DependencyRegistry(), agt_reg, agent_map={"BLI-001": "AGT-002"}
        )
        assigned = {e.item_id: e.agent_id for e in sched.entries}
        assert assigned["BLI-001"] == "AGT-002"

    def test_agents_are_round_robined(self, agt_reg):
        agt_reg.register(AgentRecord(agent_id="AGT-002", name="Beta"))
        items = [
            BacklogItem(item_id="BLI-001", universe_id=UID, title="A"),
            BacklogItem(item_id="BLI-002", universe_id=UID, title="B"),
        ]
        sched = Scheduler().schedule(items, DependencyRegistry(), agt_reg)
        assert {e.agent_id for e in sched.entries} == {"AGT-001", "AGT-002"}

    def test_optional_dependency_does_not_constrain_waves(self, agt_reg):
        dep_reg = DependencyRegistry()
        dep_reg.register(
            DependencyRecord(
                dependency_id="D1",
                from_id="BLI-002",
                to_id="BLI-001",
                optional=True,
            )
        )
        items = [
            BacklogItem(item_id="BLI-001", universe_id=UID, title="A"),
            BacklogItem(item_id="BLI-002", universe_id=UID, title="B"),
        ]
        sched = Scheduler().schedule(items, dep_reg, agt_reg)
        assert sched.wave_count == 1

    def test_dependency_outside_item_set_is_ignored(self, agt_reg):
        dep_reg = DependencyRegistry()
        dep_reg.register(DependencyRecord(dependency_id="D1", from_id="BLI-001", to_id="ELSEWHERE"))
        items = [BacklogItem(item_id="BLI-001", universe_id=UID, title="A")]
        sched = Scheduler().schedule(items, dep_reg, agt_reg)
        assert sched.wave_count == 1

    def test_schedule_is_deterministic(self, agt_reg, dep_reg):
        items = [
            BacklogItem(item_id="BLI-001", universe_id=UID, title="A", priority="LOW"),
            BacklogItem(item_id="BLI-002", universe_id=UID, title="B", priority="CRITICAL"),
        ]
        first = Scheduler().schedule(items, dep_reg, agt_reg).to_dict()
        second = Scheduler().schedule(items, dep_reg, agt_reg).to_dict()
        assert first == second


class TestAssignmentEngine:
    def test_assign_and_retrieve(self, item):
        eng = AssignmentEngine()
        a = Assignment(assignment_id="A1", item_id=item.item_id, agent_id="AGT-001")
        eng.assign(a)
        assert eng.for_item(item.item_id).assignment_id == "A1"

    def test_duplicate_assignment_raises(self, item):
        eng = AssignmentEngine()
        a = Assignment(assignment_id="A1", item_id=item.item_id, agent_id="AGT-001")
        eng.assign(a)
        with pytest.raises(DuplicateObjectError):
            eng.assign(a)

    def test_second_active_assignment_raises(self, item):
        eng = AssignmentEngine()
        eng.assign(Assignment(assignment_id="A1", item_id=item.item_id, agent_id="AGT-001"))
        with pytest.raises(AssignmentError):
            eng.assign(Assignment(assignment_id="A2", item_id=item.item_id, agent_id="AGT-002"))

    def test_for_agent(self, item):
        eng = AssignmentEngine()
        eng.assign(Assignment(assignment_id="A1", item_id=item.item_id, agent_id="AGT-001"))
        assert len(eng.for_agent("AGT-001")) == 1
        assert eng.for_agent("OTHER") == []

    def test_get_and_missing_raises(self, item):
        eng = AssignmentEngine()
        eng.assign(Assignment(assignment_id="A1", item_id=item.item_id, agent_id="AGT-001"))
        assert eng.get("A1").agent_id == "AGT-001"
        with pytest.raises(ObjectNotFoundError):
            eng.get("MISSING")

    def test_for_item_none_when_unassigned(self):
        assert AssignmentEngine().for_item("NOPE") is None

    def test_inactive_assignment_allows_reassignment(self, item):
        eng = AssignmentEngine()
        eng.assign(
            Assignment(
                assignment_id="A1",
                item_id=item.item_id,
                agent_id="AGT-001",
                state=LIFECYCLE_COMPLETE,
            )
        )
        eng.assign(Assignment(assignment_id="A2", item_id=item.item_id, agent_id="AGT-002"))
        assert eng.count() == 2
        assert eng.for_item(item.item_id).assignment_id == "A2"

    def test_to_dict_structure(self, item):
        eng = AssignmentEngine()
        eng.assign(Assignment(assignment_id="A1", item_id=item.item_id, agent_id="AGT-001"))
        d = eng.to_dict()
        assert d["engine"] == "AssignmentEngine"
        assert d["total"] == 1
        assert d["active"] == 1
        assert len(d["assignments"]) == 1


# ---------------------------------------------------------------------------
# Prompt
# ---------------------------------------------------------------------------


class TestPromptEngine:
    def test_default_template_registered(self):
        assert "ctrl.prompt.default" in PromptEngine().template_ids()

    def test_render_produces_content_addressed_prompt(self, item, agent):
        p = PromptEngine().render(item, agent, universe_id=UID)
        assert p.prompt_id.startswith("PRM-")
        assert p.item_id == item.item_id
        assert p.agent_id == agent.agent_id
        assert p.universe_id == UID
        assert p.template_id == "ctrl.prompt.default"

    def test_render_substitutes_every_field(self, agent):
        item = BacklogItem(
            item_id="BLI-9",
            universe_id=UID,
            title="Ship it",
            priority="CRITICAL",
            description="Do the thing",
            milestone_id="MS-1",
            objective_id="OBJ-1",
        )
        text = (
            PromptEngine()
            .render(
                item,
                agent,
                universe_id=UID,
                success_criteria="All gates green",
            )
            .text
        )
        for expected in (
            UID,
            "BLI-9",
            "Ship it",
            "CRITICAL",
            "Do the thing",
            "MS-1",
            "OBJ-1",
            agent.agent_id,
            agent.name,
            agent.kind,
            "All gates green",
        ):
            assert expected in text
        assert "{" not in text  # no unsubstituted placeholders remain

    def test_empty_optionals_render_as_none_marker(self, item, agent):
        text = PromptEngine().render(item, agent, universe_id=UID).text
        assert text.count("(none)") == 5  # description, milestone, objective, criteria, context

    def test_render_is_deterministic_across_engines(self, item, agent):
        a = PromptEngine().render(item, agent, universe_id=UID)
        b = PromptEngine().render(item, agent, universe_id=UID)
        assert a.prompt_id == b.prompt_id
        assert a.text == b.text

    def test_render_is_cached_and_returns_same_object(self, item, agent):
        eng = PromptEngine()
        first = eng.render(item, agent, universe_id=UID)
        second = eng.render(item, agent, universe_id=UID)
        assert first is second
        assert eng.count() == 1

    def test_context_is_rendered_sorted(self, item, agent):
        p = PromptEngine().render(
            item,
            agent,
            universe_id=UID,
            context={"zeta": 2, "alpha": 1},
        )
        assert p.text.index("alpha: 1") < p.text.index("zeta: 2")

    def test_context_changes_prompt_identity(self, item, agent):
        eng = PromptEngine()
        bare = eng.render(item, agent, universe_id=UID)
        ctx = eng.render(item, agent, universe_id=UID, context={"k": "v"})
        assert bare.prompt_id != ctx.prompt_id
        assert bare.context_digest != ctx.context_digest
        assert eng.count() == 2

    def test_universe_changes_prompt_identity(self, item, agent):
        eng = PromptEngine()
        a = eng.render(item, agent, universe_id=UID)
        b = eng.render(item, agent, universe_id="OTHER-UNIVERSE")
        assert a.prompt_id != b.prompt_id

    def test_register_and_use_custom_template(self, item, agent):
        eng = PromptEngine()
        eng.register_template("custom", "ITEM={item_id} AGENT={agent_id}")
        p = eng.render(item, agent, universe_id=UID, template_id="custom")
        assert p.text == f"ITEM={item.item_id} AGENT={agent.agent_id}"
        assert p.template_id == "custom"
        assert eng.template_ids() == ["ctrl.prompt.default", "custom"]

    def test_register_blank_template_id_raises(self):
        with pytest.raises(PromptRenderError):
            PromptEngine().register_template("   ", "body")

    def test_register_blank_template_body_raises(self):
        with pytest.raises(PromptRenderError):
            PromptEngine().register_template("custom", "   ")

    def test_unregistered_template_raises(self, item, agent):
        with pytest.raises(PromptRenderError):
            PromptEngine().render(item, agent, universe_id=UID, template_id="nope")

    def test_template_with_unknown_field_raises(self, item, agent):
        eng = PromptEngine()
        eng.register_template("bad", "value = {not_a_real_field}")
        with pytest.raises(PromptRenderError):
            eng.render(item, agent, universe_id=UID, template_id="bad")

    def test_template_id_is_not_part_of_prompt_identity(self, item, agent):
        """DEFECT-1 (documented): template_id is excluded from the content address,
        so a second render with a different template silently returns the cached
        prompt built from the first template."""
        eng = PromptEngine()
        default = eng.render(item, agent, universe_id=UID)
        eng.register_template("custom", "ITEM={item_id}")
        again = eng.render(item, agent, universe_id=UID, template_id="custom")
        assert again is default
        assert again.template_id == "ctrl.prompt.default"

    def test_success_criteria_is_not_part_of_prompt_identity(self, item, agent):
        """DEFECT-2 (documented): success_criteria is excluded from the content
        address, so changing it does not produce a new prompt."""
        eng = PromptEngine()
        first = eng.render(item, agent, universe_id=UID, success_criteria="CRITERIA-A")
        second = eng.render(item, agent, universe_id=UID, success_criteria="CRITERIA-B")
        assert second is first
        assert "CRITERIA-A" in second.text
        assert "CRITERIA-B" not in second.text

    def test_get_and_for_item(self, item, agent):
        eng = PromptEngine()
        p = eng.render(item, agent, universe_id=UID)
        assert eng.get(p.prompt_id) is p
        assert eng.get("PRM-missing") is None
        assert eng.for_item(item.item_id) == [p]
        assert eng.for_item("OTHER") == []

    def test_tick_is_carried_onto_the_prompt(self, item, agent):
        assert PromptEngine().render(item, agent, universe_id=UID, tick=7).tick == 7

    def test_to_dict(self, item, agent):
        eng = PromptEngine()
        eng.render(item, agent, universe_id=UID)
        d = eng.to_dict()
        assert d["engine"] == "PromptEngine"
        assert d["prompts_rendered"] == 1
        assert d["templates"] == ["ctrl.prompt.default"]
        assert len(d["prompts"]) == 1

    def test_to_dict_empty(self):
        d = PromptEngine().to_dict()
        assert d["prompts_rendered"] == 0
        assert d["prompts"] == []


# ---------------------------------------------------------------------------
# Progress
# ---------------------------------------------------------------------------


class TestProgressEngine:
    @staticmethod
    def _items(states):
        return [
            BacklogItem(item_id=f"BLI-{n}", universe_id=UID, title=f"T{n}", state=s)
            for n, s in enumerate(states)
        ]

    def test_measure_counts_completed(self):
        items = self._items([LIFECYCLE_COMPLETE, LIFECYCLE_COMPLETE, LIFECYCLE_DRAFT])
        rec = ProgressEngine().measure(UID, items)
        assert rec.total == 3
        assert rec.completed == 2
        assert rec.record_id.startswith("PRG-")
        assert rec.state == LIFECYCLE_ACTIVE
        assert abs(rec.percentage - (200 / 3)) < 0.01

    def test_measure_empty_item_list(self):
        rec = ProgressEngine().measure(UID, [])
        assert (rec.total, rec.completed, rec.percentage) == (0, 0, 0.0)

    def test_measure_all_complete(self):
        rec = ProgressEngine().measure(UID, self._items([LIFECYCLE_COMPLETE] * 4))
        assert rec.completed == 4
        assert rec.percentage == 100.0

    def test_record_id_is_deterministic_for_subject_and_tick(self):
        a = ProgressEngine().measure(UID, [], tick=3)
        b = ProgressEngine().measure(UID, [], tick=3)
        c = ProgressEngine().measure(UID, [], tick=4)
        assert a.record_id == b.record_id
        assert a.record_id != c.record_id

    def test_latest_returns_most_recent_measurement(self):
        eng = ProgressEngine()
        eng.measure(UID, self._items([LIFECYCLE_DRAFT]), tick=0)
        eng.measure(UID, self._items([LIFECYCLE_COMPLETE]), tick=1)
        assert eng.latest(UID).completed == 1

    def test_latest_unknown_subject_is_none(self):
        assert ProgressEngine().latest("NOPE") is None

    def test_history_accumulates_and_is_a_copy(self):
        eng = ProgressEngine()
        eng.measure(UID, [], tick=0)
        eng.measure(UID, [], tick=1)
        hist = eng.history(UID)
        assert len(hist) == 2
        hist.clear()
        assert len(eng.history(UID)) == 2

    def test_history_unknown_subject_is_empty(self):
        assert ProgressEngine().history("NOPE") == []

    def test_all_subjects_sorted(self):
        eng = ProgressEngine()
        eng.measure("Z-SUBJ", [])
        eng.measure("A-SUBJ", [])
        assert eng.all_subjects() == ["A-SUBJ", "Z-SUBJ"]

    def test_to_dict(self):
        eng = ProgressEngine()
        eng.measure(UID, self._items([LIFECYCLE_COMPLETE]))
        d = eng.to_dict()
        assert d["engine"] == "ProgressEngine"
        assert d["subjects"] == [UID]
        assert len(d["records"][UID]) == 1

    def test_to_dict_empty(self):
        d = ProgressEngine().to_dict()
        assert d["subjects"] == []
        assert d["records"] == {}


# ---------------------------------------------------------------------------
# Metrics
# ---------------------------------------------------------------------------


class TestMetricsEngine:
    def test_record_returns_metric(self):
        m = MetricsEngine().record(UID, "latency", 1.5, unit="s", tick=2)
        assert m.metric_id.startswith("MET-")
        assert (m.subject_id, m.name, m.value, m.unit, m.tick) == (UID, "latency", 1.5, "s", 2)

    def test_metric_id_is_deterministic(self):
        a = MetricsEngine().record(UID, "n", 1.0, tick=0)
        b = MetricsEngine().record(UID, "n", 9.0, tick=0)
        c = MetricsEngine().record(UID, "n", 1.0, tick=1)
        assert a.metric_id == b.metric_id  # value is not part of identity
        assert a.metric_id != c.metric_id

    def test_latest_returns_last_recorded(self):
        eng = MetricsEngine()
        eng.record(UID, "n", 1.0, tick=0)
        eng.record(UID, "n", 2.0, tick=1)
        assert eng.latest(UID, "n").value == 2.0

    def test_latest_unknown_series_is_none(self):
        assert MetricsEngine().latest(UID, "nope") is None

    def test_series_is_a_copy(self):
        eng = MetricsEngine()
        eng.record(UID, "n", 1.0)
        series = eng.series(UID, "n")
        series.clear()
        assert len(eng.series(UID, "n")) == 1

    def test_series_unknown_is_empty(self):
        assert MetricsEngine().series(UID, "nope") == []

    def test_aggregate(self):
        eng = MetricsEngine()
        for tick, value in enumerate((2.0, 4.0, 9.0)):
            eng.record(UID, "n", value, tick=tick)
        assert eng.aggregate(UID, "n") == {
            "count": 3.0,
            "min": 2.0,
            "max": 9.0,
            "sum": 15.0,
            "mean": 5.0,
        }

    def test_aggregate_rounds_mean(self):
        eng = MetricsEngine()
        for tick, value in enumerate((1.0, 2.0)):
            eng.record(UID, "n", value, tick=tick)
        assert eng.aggregate(UID, "n")["mean"] == 1.5

    def test_aggregate_empty_series_is_empty_dict(self):
        assert MetricsEngine().aggregate(UID, "nope") == {}

    def test_subjects_deduplicated_and_sorted(self):
        eng = MetricsEngine()
        eng.record("Z-SUBJ", "a", 1.0)
        eng.record("A-SUBJ", "a", 1.0)
        eng.record("A-SUBJ", "b", 1.0)
        assert eng.subjects() == ["A-SUBJ", "Z-SUBJ"]

    def test_metric_names_scoped_to_subject(self):
        eng = MetricsEngine()
        eng.record(UID, "zeta", 1.0)
        eng.record(UID, "alpha", 1.0)
        eng.record("OTHER", "omega", 1.0)
        assert eng.metric_names(UID) == ["alpha", "zeta"]
        assert eng.metric_names("MISSING") == []

    def test_count_spans_all_series(self):
        eng = MetricsEngine()
        eng.record(UID, "a", 1.0, tick=0)
        eng.record(UID, "a", 1.0, tick=1)
        eng.record(UID, "b", 1.0, tick=0)
        assert eng.count() == 3

    def test_to_dict(self):
        eng = MetricsEngine()
        eng.record(UID, "n", 1.0)
        d = eng.to_dict()
        assert d["engine"] == "MetricsEngine"
        assert d["total_records"] == 1
        assert d["subjects"] == [UID]
        assert len(d["series"][f"{UID}::n"]) == 1

    def test_to_dict_empty(self):
        d = MetricsEngine().to_dict()
        assert d["total_records"] == 0
        assert d["series"] == {}


# ---------------------------------------------------------------------------
# Dashboard
# ---------------------------------------------------------------------------


class TestDashboardEngine:
    def test_empty_snapshot_has_only_header(self):
        assert DashboardEngine().snapshot() == {
            "dashboard": "UCOS-CTRL-000001",
            "tick": 0,
        }

    def test_tick_is_carried(self):
        assert DashboardEngine().snapshot(tick=11)["tick"] == 11

    def test_plan_section(self):
        d = DashboardEngine().snapshot(
            plan_dict={
                "visions": 1,
                "goals": 2,
                "objectives": 3,
                "completion_rate": 50.0,
            }
        )
        assert d["plan"] == {
            "visions": 1,
            "goals": 2,
            "objectives": 3,
            "completion_rate": 50.0,
        }

    def test_sections_use_defaults_for_missing_keys(self):
        d = DashboardEngine().snapshot(plan_dict={"visions": 1})
        assert d["plan"] == {
            "visions": 1,
            "goals": 0,
            "objectives": 0,
            "completion_rate": 0.0,
        }

    def test_all_sections_present(self):
        d = DashboardEngine().snapshot(
            plan_dict={"visions": 1},
            roadmap_dict={"total_milestones": 2},
            backlog_dict={"count": 3, "total_estimate": 9},
            schedule_dict={"wave_count": 1, "total_entries": 3},
            assignment_dict={"total": 2, "active": 1},
            progress_dict={"subjects": [UID]},
            metrics_dict={"total_records": 4, "subjects": [UID]},
            registry_dicts=[{"registry": "CapabilityRegistry", "count": 2}],
            tick=1,
        )
        assert set(d) == {
            "dashboard",
            "tick",
            "plan",
            "roadmap",
            "backlog",
            "schedule",
            "assignments",
            "progress",
            "metrics",
            "registries",
        }
        assert d["roadmap"]["total_milestones"] == 2
        assert d["backlog"] == {"count": 3, "total_estimate": 9}
        assert d["schedule"] == {"wave_count": 1, "total_entries": 3}
        assert d["assignments"] == {"total": 2, "active": 1}
        assert d["progress"] == {"subjects": [UID]}
        assert d["metrics"] == {"total_records": 4, "subjects": [UID]}
        assert d["registries"] == [{"name": "CapabilityRegistry", "count": 2}]

    def test_registry_dict_without_name_falls_back(self):
        d = DashboardEngine().snapshot(registry_dicts=[{}])
        assert d["registries"] == [{"name": "?", "count": 0}]

    def test_falsy_sections_are_omitted(self):
        """DEFECT-3 (documented): sections are gated on truthiness, so a genuinely
        empty engine summary ({}) is dropped rather than reported as empty."""
        d = DashboardEngine().snapshot(
            plan_dict={},
            roadmap_dict={},
            backlog_dict={},
            schedule_dict={},
            assignment_dict={},
            progress_dict={},
            metrics_dict={},
            registry_dicts=[],
        )
        assert set(d) == {"dashboard", "tick"}

    def test_snapshot_over_real_engines(self, item, agt_reg, dep_reg):
        back = BacklogEngine()
        back.add(item)
        prog = ProgressEngine()
        prog.measure(UID, back.ordered())
        met = MetricsEngine()
        met.record(UID, "backlog.count", float(back.count()))
        d = DashboardEngine().snapshot(
            backlog_dict=back.to_dict(),
            schedule_dict=Scheduler().schedule(back.ready(), dep_reg, agt_reg).to_dict(),
            progress_dict=prog.to_dict(),
            metrics_dict=met.to_dict(),
            registry_dicts=[agt_reg.to_dict()],
        )
        assert d["backlog"]["count"] == 1
        assert d["schedule"]["total_entries"] == 1
        assert d["progress"]["subjects"] == [UID]
        assert d["metrics"]["total_records"] == 1


# ---------------------------------------------------------------------------
# Determination
# ---------------------------------------------------------------------------


def _det(det_id="DET-001", subject_id="SUBJ-1", verdict="AUTHORIZED", tick=0):
    return Determination(
        determination_id=det_id,
        subject_id=subject_id,
        verdict=verdict,
        rationale="because the evidence supports it",
        tick=tick,
    )


class TestDeterminationEngine:
    def test_record_and_get(self):
        eng = DeterminationEngine()
        det = eng.record(_det())
        assert eng.get("DET-001") is det
        assert eng.count() == 1

    def test_duplicate_raises(self):
        eng = DeterminationEngine()
        eng.record(_det())
        with pytest.raises(DuplicateObjectError):
            eng.record(_det())

    def test_blank_verdict_raises(self):
        with pytest.raises(DeterminationError):
            DeterminationEngine().record(_det(verdict="   "))

    def test_get_missing_raises(self):
        with pytest.raises(ObjectNotFoundError):
            DeterminationEngine().get("DET-missing")

    def test_for_subject(self):
        eng = DeterminationEngine()
        eng.record(_det("DET-1", "S1"))
        eng.record(_det("DET-2", "S1"))
        eng.record(_det("DET-3", "S2"))
        assert len(eng.for_subject("S1")) == 2
        assert eng.for_subject("MISSING") == []

    def test_latest_for_subject_picks_highest_tick(self):
        eng = DeterminationEngine()
        eng.record(_det("DET-1", "S1", tick=5))
        eng.record(_det("DET-2", "S1", tick=2))
        assert eng.latest_for_subject("S1").determination_id == "DET-1"

    def test_latest_for_unknown_subject_is_none(self):
        assert DeterminationEngine().latest_for_subject("MISSING") is None

    def test_by_verdict(self):
        eng = DeterminationEngine()
        eng.record(_det("DET-1", verdict="AUTHORIZED"))
        eng.record(_det("DET-2", verdict="BLOCKED"))
        assert [d.determination_id for d in eng.by_verdict("BLOCKED")] == ["DET-2"]
        assert eng.by_verdict("DEFERRED") == []

    def test_evidence_ids_are_carried(self):
        det = Determination(
            determination_id="DET-9",
            subject_id="S1",
            verdict="AUTHORIZED",
            rationale="r",
            evidence_ids=("EV-1", "EV-2"),
        )
        assert DeterminationEngine().record(det).to_dict()["evidence_ids"] == ["EV-1", "EV-2"]

    def test_to_dict(self):
        eng = DeterminationEngine()
        eng.record(_det())
        d = eng.to_dict()
        assert d["engine"] == "DeterminationEngine"
        assert d["count"] == 1
        assert d["determinations"][0]["determination_id"] == "DET-001"

    def test_to_dict_empty(self):
        assert DeterminationEngine().to_dict()["determinations"] == []


# ---------------------------------------------------------------------------
# Decision
# ---------------------------------------------------------------------------


def _decision(dec_id="DEC-001", subject_id="SUBJ-1", choice="Adopt A", det_id=""):
    return Decision(
        decision_id=dec_id,
        subject_id=subject_id,
        title="Choose an approach",
        choice=choice,
        rationale="A is reversible",
        alternatives=("B", "C"),
        determination_id=det_id,
    )


class TestDecisionEngine:
    def test_record_and_get(self):
        eng = DecisionEngine()
        dec = eng.record(_decision())
        assert eng.get("DEC-001") is dec
        assert eng.count() == 1

    def test_duplicate_raises(self):
        eng = DecisionEngine()
        eng.record(_decision())
        with pytest.raises(DuplicateObjectError):
            eng.record(_decision())

    def test_blank_choice_raises(self):
        with pytest.raises(DeterminationError):
            DecisionEngine().record(_decision(choice="  "))

    def test_get_missing_raises(self):
        with pytest.raises(ObjectNotFoundError):
            DecisionEngine().get("DEC-missing")

    def test_for_subject(self):
        eng = DecisionEngine()
        eng.record(_decision("DEC-1", "S1"))
        eng.record(_decision("DEC-2", "S2"))
        assert [d.decision_id for d in eng.for_subject("S1")] == ["DEC-1"]
        assert eng.for_subject("MISSING") == []

    def test_for_determination(self):
        eng = DecisionEngine()
        eng.record(_decision("DEC-1", det_id="DET-1"))
        eng.record(_decision("DEC-2", det_id="DET-2"))
        assert [d.decision_id for d in eng.for_determination("DET-2")] == ["DEC-2"]
        assert eng.for_determination("DET-missing") == []

    def test_alternatives_are_carried(self):
        assert DecisionEngine().record(_decision()).to_dict()["alternatives"] == ["B", "C"]

    def test_to_dict(self):
        eng = DecisionEngine()
        eng.record(_decision())
        d = eng.to_dict()
        assert d["engine"] == "DecisionEngine"
        assert d["count"] == 1
        assert d["decisions"][0]["decision_id"] == "DEC-001"

    def test_to_dict_empty(self):
        assert DecisionEngine().to_dict()["decisions"] == []


# ---------------------------------------------------------------------------
# History
# ---------------------------------------------------------------------------


def _entry(entry_id="HIS-001", subject_id="SUBJ-1", event="STATE_CHANGED", tick=0):
    return HistoryEntry(
        entry_id=entry_id,
        subject_id=subject_id,
        event=event,
        detail="DRAFT -> ACTIVE",
        actor_id="AGT-001",
        tick=tick,
    )


class TestHistoryEngine:
    def test_append_returns_entry_and_counts(self):
        eng = HistoryEngine()
        entry = eng.append(_entry())
        assert entry.entry_id == "HIS-001"
        assert eng.count() == 1

    def test_duplicate_ids_are_allowed_append_only(self):
        eng = HistoryEngine()
        eng.append(_entry())
        eng.append(_entry())
        assert eng.count() == 2

    def test_order_is_preserved(self):
        eng = HistoryEngine()
        for n in range(3):
            eng.append(_entry(entry_id=f"HIS-{n}"))
        assert [e.entry_id for e in eng.all()] == ["HIS-0", "HIS-1", "HIS-2"]

    def test_all_is_a_copy(self):
        eng = HistoryEngine()
        eng.append(_entry())
        entries = eng.all()
        entries.clear()
        assert eng.count() == 1

    def test_for_subject(self):
        eng = HistoryEngine()
        eng.append(_entry("HIS-1", "S1"))
        eng.append(_entry("HIS-2", "S2"))
        assert [e.entry_id for e in eng.for_subject("S1")] == ["HIS-1"]
        assert eng.for_subject("MISSING") == []

    def test_by_event(self):
        eng = HistoryEngine()
        eng.append(_entry("HIS-1", event="ASSIGNED"))
        eng.append(_entry("HIS-2", event="DETERMINED"))
        assert [e.entry_id for e in eng.by_event("DETERMINED")] == ["HIS-2"]
        assert eng.by_event("MISSING") == []

    def test_digest_of_empty_log_is_stable(self):
        assert HistoryEngine().digest() == HistoryEngine().digest()

    def test_digest_changes_on_append(self):
        eng = HistoryEngine()
        before = eng.digest()
        eng.append(_entry())
        assert eng.digest() != before

    def test_digest_is_order_sensitive(self):
        a, b = HistoryEngine(), HistoryEngine()
        a.append(_entry("HIS-1"))
        a.append(_entry("HIS-2"))
        b.append(_entry("HIS-2"))
        b.append(_entry("HIS-1"))
        assert a.digest() != b.digest()

    def test_equal_logs_share_a_digest(self):
        a, b = HistoryEngine(), HistoryEngine()
        a.append(_entry())
        b.append(_entry())
        assert a.digest() == b.digest()

    def test_to_dict(self):
        eng = HistoryEngine()
        eng.append(_entry())
        d = eng.to_dict()
        assert d["engine"] == "HistoryEngine"
        assert d["count"] == 1
        assert d["digest"] == eng.digest()
        assert d["entries"][0]["entry_id"] == "HIS-001"


# ---------------------------------------------------------------------------
# Replay
# ---------------------------------------------------------------------------


def _replay(replay_id="RPL-001", subject_id="SUBJ-1", inputs="IN", outputs="OUT"):
    return ReplayRecord(
        replay_id=replay_id,
        subject_id=subject_id,
        inputs_digest=inputs,
        outputs_digest=outputs,
        history_ids=("HIS-1",),
    )


class TestReplayEngine:
    def test_record_and_get(self):
        eng = ReplayEngine()
        rec = eng.record(_replay())
        assert eng.get("RPL-001") is rec
        assert eng.count() == 1

    def test_duplicate_raises(self):
        eng = ReplayEngine()
        eng.record(_replay())
        with pytest.raises(DuplicateObjectError):
            eng.record(_replay())

    def test_get_missing_raises(self):
        with pytest.raises(ObjectNotFoundError):
            ReplayEngine().get("RPL-missing")

    def test_verify_matching_digests(self):
        eng = ReplayEngine()
        eng.record(_replay())
        assert eng.verify("RPL-001", "IN", "OUT") is True

    def test_verify_inputs_mismatch_raises(self):
        eng = ReplayEngine()
        eng.record(_replay())
        with pytest.raises(ReplayError, match="inputs digest mismatch"):
            eng.verify("RPL-001", "WRONG", "OUT")

    def test_verify_outputs_mismatch_raises(self):
        eng = ReplayEngine()
        eng.record(_replay())
        with pytest.raises(ReplayError, match="outputs digest mismatch"):
            eng.verify("RPL-001", "IN", "WRONG")

    def test_verify_unknown_replay_raises(self):
        with pytest.raises(ObjectNotFoundError):
            ReplayEngine().verify("RPL-missing", "IN", "OUT")

    def test_for_subject(self):
        eng = ReplayEngine()
        eng.record(_replay("RPL-1", "S1"))
        eng.record(_replay("RPL-2", "S2"))
        assert [r.replay_id for r in eng.for_subject("S1")] == ["RPL-1"]
        assert eng.for_subject("MISSING") == []

    def test_history_ids_are_carried(self):
        assert ReplayEngine().record(_replay()).to_dict()["history_ids"] == ["HIS-1"]

    def test_to_dict(self):
        eng = ReplayEngine()
        eng.record(_replay())
        d = eng.to_dict()
        assert d["engine"] == "ReplayEngine"
        assert d["count"] == 1
        assert d["records"][0]["replay_id"] == "RPL-001"

    def test_to_dict_empty(self):
        assert ReplayEngine().to_dict()["records"] == []


# ---------------------------------------------------------------------------
# Evidence
# ---------------------------------------------------------------------------


def _evidence(evidence_id="EV-001", subject_id="SUBJ-1", kind="TEST", digest="d"):
    return Evidence(
        evidence_id=evidence_id,
        subject_id=subject_id,
        kind=kind,
        claim="the suite passes",
        payload_digest=digest,
    )


class TestEvidenceEngine:
    def test_make_digest_is_deterministic(self):
        payload = {"b": 2, "a": 1}
        assert EvidenceEngine.make_digest(payload) == EvidenceEngine.make_digest(payload)

    def test_make_digest_is_key_order_independent(self):
        assert EvidenceEngine.make_digest({"a": 1, "b": 2}) == EvidenceEngine.make_digest(
            {"b": 2, "a": 1}
        )

    def test_make_digest_differs_on_content(self):
        assert EvidenceEngine.make_digest({"a": 1}) != EvidenceEngine.make_digest({"a": 2})

    def test_record_and_get(self):
        eng = EvidenceEngine()
        ev = eng.record(_evidence())
        assert eng.get("EV-001") is ev
        assert eng.count() == 1

    def test_duplicate_raises(self):
        eng = EvidenceEngine()
        eng.record(_evidence())
        with pytest.raises(DuplicateObjectError):
            eng.record(_evidence())

    def test_blank_digest_raises(self):
        with pytest.raises(EvidenceError):
            EvidenceEngine().record(_evidence(digest="   "))

    def test_get_missing_raises(self):
        with pytest.raises(ObjectNotFoundError):
            EvidenceEngine().get("EV-missing")

    def test_verify_round_trip(self):
        eng = EvidenceEngine()
        payload = {"tests": 512, "failures": 0}
        eng.record(_evidence(digest=EvidenceEngine.make_digest(payload)))
        assert eng.verify("EV-001", payload) is True

    def test_verify_tampered_payload_raises(self):
        eng = EvidenceEngine()
        eng.record(_evidence(digest=EvidenceEngine.make_digest({"tests": 512})))
        with pytest.raises(EvidenceError, match="digest mismatch"):
            eng.verify("EV-001", {"tests": 511})

    def test_verify_unknown_evidence_raises(self):
        with pytest.raises(ObjectNotFoundError):
            EvidenceEngine().verify("EV-missing", {})

    def test_for_subject(self):
        eng = EvidenceEngine()
        eng.record(_evidence("EV-1", "S1"))
        eng.record(_evidence("EV-2", "S2"))
        assert [e.evidence_id for e in eng.for_subject("S1")] == ["EV-1"]
        assert eng.for_subject("MISSING") == []

    def test_by_kind(self):
        eng = EvidenceEngine()
        eng.record(_evidence("EV-1", kind="TEST"))
        eng.record(_evidence("EV-2", kind="AUDIT"))
        assert [e.evidence_id for e in eng.by_kind("AUDIT")] == ["EV-2"]
        assert eng.by_kind("REVIEW") == []

    def test_to_dict(self):
        eng = EvidenceEngine()
        eng.record(_evidence())
        d = eng.to_dict()
        assert d["engine"] == "EvidenceEngine"
        assert d["count"] == 1
        assert d["evidence"][0]["evidence_id"] == "EV-001"
        assert d["evidence"][0]["evidence_kind"] == "TEST"

    def test_to_dict_empty(self):
        assert EvidenceEngine().to_dict()["evidence"] == []


# ---------------------------------------------------------------------------
# CLI
#
# Every command reads discovered repository state, so each test drives the CLI
# against a hermetic fixture substrate rather than the packaged registry. That
# keeps the suite fast and — more importantly — proves the CLI carries no path:
# if any command reached for the real repository, none of these would pass.
# ---------------------------------------------------------------------------

COMMANDS = cli_mod.COMMANDS


@pytest.fixture(scope="module")
def substrate(tmp_path_factory):
    root = tmp_path_factory.mktemp("cli-substrate")
    repository_root, data_dir = build_substrate(root)
    return repository_root, data_dir, root / "runtime"


def _invoke(argv, substrate=None):
    out, err = io.StringIO(), io.StringIO()
    if substrate is not None:
        repository_root, data_dir, journal_root = substrate
        argv = [
            *argv,
            "--data-dir",
            str(data_dir),
            "--repository-root",
            str(repository_root),
            "--journal-root",
            str(journal_root),
        ]
    code = cli_run(argv, out=out, err=err)
    return code, out.getvalue(), err.getvalue()


class TestCLI:
    @pytest.mark.parametrize("command", COMMANDS)
    def test_command_succeeds_and_writes_text(self, command, substrate):
        code, out, err = _invoke([command], substrate)
        assert code == 0
        assert out.strip()
        assert err == ""

    @pytest.mark.parametrize("command", COMMANDS)
    def test_command_json_is_parsable(self, command, substrate):
        code, out, _ = _invoke([command, "--json"], substrate)
        assert code == 0
        assert isinstance(json.loads(out), dict)

    @pytest.mark.parametrize("command", COMMANDS)
    def test_command_is_deterministic(self, command, substrate):
        """Two runs over identical repository state must be byte-identical.

        The two journal-reading commands are excluded here and covered by
        :meth:`test_journal_commands_are_deterministic_from_a_fresh_journal`
        instead: a shared journal is append-only, so the second run legitimately
        sees more entries than the first. That is the durability property, not a
        determinism failure — but it does mean the byte-equality has to be
        measured from an equal starting state to mean anything.
        """
        if command in cli_mod.JOURNAL_COMMANDS:
            pytest.skip("covered against a fresh journal, since a shared one is append-only")
        assert (
            _invoke([command, "--json"], substrate)[1] == _invoke([command, "--json"], substrate)[1]
        )

    @pytest.mark.parametrize("command", sorted(cli_mod.JOURNAL_COMMANDS))
    def test_journal_commands_are_deterministic_from_a_fresh_journal(
        self, command, substrate, tmp_path
    ):
        import shutil

        repository_root, data_dir, _ = substrate
        journal_root = tmp_path / "journal"
        outputs = []
        for _ in (1, 2):
            # Same path both times — a differing path would show up as a
            # difference in the output and mask a real divergence.
            shutil.rmtree(journal_root, ignore_errors=True)
            out, err = io.StringIO(), io.StringIO()
            assert (
                cli_run(
                    [
                        command,
                        "--json",
                        "--data-dir",
                        str(data_dir),
                        "--repository-root",
                        str(repository_root),
                        "--journal-root",
                        str(journal_root),
                    ],
                    out=out,
                    err=err,
                )
                == 0
            )
            outputs.append(out.getvalue())
        assert outputs[0] == outputs[1]

    def test_state_lists_lifecycle_states(self, substrate):
        payload = json.loads(_invoke(["state", "--json"], substrate)[1])
        assert LIFECYCLE_DRAFT in json.dumps(payload)
        assert LIFECYCLE_COMPLETE in json.dumps(payload)

    def test_registries_reports_all_four(self, substrate):
        payload = json.loads(_invoke(["registries", "--json"], substrate)[1])
        assert len(payload["registries"]) == 4

    def test_truth_reports_the_declared_sources(self, substrate):
        payload = json.loads(_invoke(["truth", "--json"], substrate)[1])
        assert payload["counts"]["artifacts"] == len(FIXTURE_ARTIFACTS)
        assert {s["source_id"] for s in payload["sources"]} == {
            "artifacts",
            "relationships",
            "certification",
            "change_ledger",
            "capability_catalog",
        }

    def test_plan_is_derived_from_registered_programmes(self, substrate):
        payload = json.loads(_invoke(["plan", "--json"], substrate)[1])
        assert payload["visions"] == 1
        # One goal per programme the fixture artifacts declare.
        assert payload["goals"] == len({a["program"] for a in FIXTURE_ARTIFACTS})
        assert payload["objectives"] >= payload["goals"]

    def test_roadmap_is_derived_from_registry_volumes(self, substrate):
        payload = json.loads(_invoke(["roadmap", "--json"], substrate)[1])
        assert payload["total_milestones"] == len({a["volume"] for a in FIXTURE_ARTIFACTS})
        assert [m["sequence"] for m in payload["milestones"]] == [0, 1, 2]

    def test_backlog_is_derived_from_governance_violations(self, substrate):
        payload = json.loads(_invoke(["backlog", "--json"], substrate)[1])
        governance = json.loads(_invoke(["governance", "--json"], substrate)[1])
        assert payload["count"] == governance["counts"]["violations"]
        assert payload["count"] > 0
        assert {i["attributes"]["rule_id"] for i in payload["items"]} <= {
            r["rule_id"] for r in governance["rules"]
        }

    def test_schedule_covers_every_ready_backlog_item(self, substrate):
        backlog = json.loads(_invoke(["backlog", "--json"], substrate)[1])
        payload = json.loads(_invoke(["schedule", "--json"], substrate)[1])
        assert payload["total_entries"] == backlog["count"]
        assert payload["wave_count"] >= 1

    def test_registration_reports_every_required_engine(self, substrate):
        payload = json.loads(_invoke(["registration", "--json"], substrate)[1])
        names = {r["name"] for r in payload["registrations"]}
        assert set(cli_mod.ControlPlane.__module__.split()) or True  # module import sanity
        from platform.universal_control_plane import REQUIRED_ENGINES

        assert set(REQUIRED_ENGINES) <= names
        assert payload["counts"]["unclassified"] == 0

    def test_governance_can_report_a_single_subject(self, substrate):
        payload = json.loads(
            _invoke(["governance", "--json", "--subject", "UCOS-GOV-000001"], substrate)[1]
        )
        assert payload["subject_id"] == "UCOS-GOV-000001"
        assert payload["kind"] == "GovernanceRecord"

    def test_certification_can_report_a_single_subject(self, substrate):
        payload = json.loads(
            _invoke(["certification", "--json", "--subject", "UCOS-GOV-000001"], substrate)[1]
        )
        assert payload["subject_id"] == "UCOS-GOV-000001"
        assert payload["kind"] == "CertificationState"

    def test_version_can_report_a_single_subject(self, substrate):
        payload = json.loads(
            _invoke(["version", "--json", "--subject", "UCOS-GOV-000001"], substrate)[1]
        )
        assert payload["subject_id"] == "UCOS-GOV-000001"
        assert "artifact" in payload["kinds"]

    def test_unknown_subject_is_an_operational_error(self, substrate):
        code, out, err = _invoke(["governance", "--subject", "NOPE"], substrate)
        assert code == 1
        assert "no governance state resolved" in err
        assert out == ""

    def test_evolution_reports_a_verified_replay_digest(self, substrate):
        payload = json.loads(_invoke(["evolution", "--json"], substrate)[1])
        assert payload["counts"]["changes"] > 0
        assert len(payload["replay_digest"]) == 64

    def test_linkage_reports_no_orphans(self, substrate):
        payload = json.loads(_invoke(["linkage", "--json"], substrate)[1])
        assert payload["counts"]["orphans"] == 0
        assert payload["coverage"] == 1.0

    def test_consumption_measures_every_bound_domain(self, substrate):
        payload = json.loads(_invoke(["consumption", "--json"], substrate)[1])
        assert payload["operational"] is True
        assert payload["counts"]["failed"] == 0

    def test_replay_reconstructs_state_from_the_journal(self, substrate):
        payload = json.loads(_invoke(["replay", "--json"], substrate)[1])
        assert payload["journal"]["count"] > 0
        assert payload["state"]["counts"]["registrations"] > 0

    def test_replay_without_a_journal_root_still_reconstructs(self, tmp_path):
        """A journal-reading command with no ``--journal-root`` gets a fresh one
        rather than failing: the reconstruction is of this run's own record."""
        repository_root, data_dir = build_substrate(tmp_path)
        code, out, _ = _invoke(
            [
                "replay",
                "--json",
                "--data-dir",
                str(data_dir),
                "--repository-root",
                str(repository_root),
            ]
        )
        assert code == 0
        assert json.loads(out)["state"]["counts"]["registrations"] > 0

    def test_completion_passes_and_exits_zero(self, substrate):
        code, out, err = _invoke(["completion", "--json"], substrate)
        payload = json.loads(out)
        assert payload["complete"] is True, payload["failures"]
        assert payload["total"] == 10
        assert code == 0
        assert err == ""

    def test_dashboard_contains_every_section(self, substrate):
        payload = json.loads(_invoke(["dashboard", "--json"], substrate)[1])
        assert payload["dashboard"] == "UCOS-CTRL-000001"
        for section in (
            "plan",
            "roadmap",
            "backlog",
            "schedule",
            "progress",
            "metrics",
            "registries",
        ):
            assert section in payload

    def test_dashboard_reports_the_empty_assignment_section(self, substrate):
        """The plane composes an AssignmentEngine it never assigns into. Its
        to_dict() is still a non-empty mapping, so the truthiness gate in
        DashboardEngine.snapshot keeps the section — reporting zero, not nothing."""
        payload = json.loads(_invoke(["dashboard", "--json"], substrate)[1])
        assert payload["assignments"] == {"total": 0, "active": 0}

    def test_tick_flag_is_threaded_through(self, substrate):
        payload = json.loads(_invoke(["truth", "--json", "--tick", "7"], substrate)[1])
        assert payload["tick"] == 7

    def test_pretty_output_renders_nested_structures(self, substrate):
        out = _invoke(["registries"], substrate)[1]
        assert "registries:" in out
        assert "count:" in out

    def test_pretty_output_renders_scalar_lists(self, substrate):
        out = _invoke(["state"], substrate)[1]
        assert "- " in out

    def test_pretty_renders_a_bare_scalar_payload(self):
        """No command emits a scalar today, but _pretty is total over payloads:
        a non-dict, non-list value prints itself at the current indent."""
        buf = io.StringIO()
        cli_mod._pretty("bare scalar", buf, indent=2)
        assert buf.getvalue() == "    bare scalar\n"

    def test_unknown_command_exits_2(self):
        with pytest.raises(SystemExit) as exc:
            cli_run(["not-a-command"])
        assert exc.value.code == 2

    def test_no_command_exits_2(self):
        with pytest.raises(SystemExit) as exc:
            cli_run([])
        assert exc.value.code == 2

    def test_help_exits_0(self):
        with pytest.raises(SystemExit) as exc:
            cli_run(["--help"])
        assert exc.value.code == 0

    def test_control_plane_error_returns_1(self, monkeypatch, substrate):
        def boom(**_kwargs):
            raise RegistrationError("the control plane is undiscoverable")

        monkeypatch.setattr(cli_mod.ControlPlane, "discover", staticmethod(boom))
        code, out, err = _invoke(["state"], substrate)
        assert code == 1
        assert "error: the control plane is undiscoverable" in err
        assert out == ""

    def test_unexpected_error_returns_2(self, monkeypatch, substrate):
        def boom(**_kwargs):
            raise RuntimeError("something structural broke")

        monkeypatch.setattr(cli_mod.ControlPlane, "discover", staticmethod(boom))
        code, _, err = _invoke(["state"], substrate)
        assert code == 2
        assert "fatal: something structural broke" in err

    def test_completion_exits_one_when_the_gate_is_not_met(self, monkeypatch, substrate):
        """The gate is usable in CI: a failing criterion must set the exit code,
        not merely appear in the report nobody reads."""
        from platform.universal_control_plane.discovery import CompletionReport, GateCriterion

        monkeypatch.setattr(
            cli_mod.ControlPlane,
            "completion",
            lambda self: CompletionReport(
                universe_id="U",
                truth_id="t",
                criteria=(GateCriterion("invented-criterion", False, "0 of 1"),),
            ),
        )
        code, out, err = _invoke(["completion", "--json"], substrate)
        assert code == 1
        assert json.loads(out)["complete"] is False
        assert "gate not met: invented-criterion" in err

    def test_main_exits_with_run_code(self, substrate):
        repository_root, data_dir, journal_root = substrate
        with pytest.raises(SystemExit) as exc:
            cli_main(
                [
                    "state",
                    "--data-dir",
                    str(data_dir),
                    "--repository-root",
                    str(repository_root),
                    "--journal-root",
                    str(journal_root),
                ]
            )
        assert exc.value.code == 0

    def test_main_propagates_failure_code(self, monkeypatch):
        monkeypatch.setattr(cli_mod, "run", lambda argv: 1)
        with pytest.raises(SystemExit) as exc:
            cli_main(["state"])
        assert exc.value.code == 1

    def test_run_defaults_to_process_streams(self, capsys, substrate):
        repository_root, data_dir, journal_root = substrate
        assert (
            cli_run(
                [
                    "state",
                    "--data-dir",
                    str(data_dir),
                    "--repository-root",
                    str(repository_root),
                    "--journal-root",
                    str(journal_root),
                ]
            )
            == 0
        )
        assert capsys.readouterr().out.strip()


class TestDiscoveryArmsThatAssumeNothing:
    """Two arms that prove the discovery walk reads the substrate instead of trusting it.

    A volumeless artifact must be passed by (milestones come only from volumes), and a
    universe that already owns a capability must not be registered as an agent twice —
    the second is the arm that keeps re-discovery idempotent, and neither fires on the
    happy-path fixture.
    """

    def test_a_volumeless_artifact_contributes_no_milestone(self, tmp_path) -> None:
        novolume = dict(FIXTURE_ARTIFACTS[0])
        novolume["universal_id"] = "UCOS-REG-NOVOL-1"
        novolume["name"] = "no-volume record"
        novolume["path"] = "00-BOOK/REGISTRIES/novol.md"
        novolume.pop("volume", None)
        artifacts = tuple([novolume, *FIXTURE_ARTIFACTS[1:]])
        repository_root, data_dir = build_substrate(tmp_path / "vol", artifacts=artifacts)
        plane = ControlPlane.discover(
            data_dir=data_dir,
            repository_root=repository_root,
            journal_root=tmp_path / "runtime",
        )
        volumes = {a.volume for a in plane.truth.artifacts() if a.volume}
        assert volumes == {"VOL-001", "VOL-002"}
        assert plane.roadmap.count() == len(volumes)

    def test_a_universe_that_already_owns_an_artifact_is_not_registered_again(
        self, tmp_path
    ) -> None:
        """The skip arm of the universe rule: owners are derived from what the registry says.

        Agents come from artifact owners, and the universe itself is appended as the agent
        of its engines only when no artifact has already named it. An artifact owned by the
        universe exercises the skip — registering the universe a second time would duplicate
        the one identity every engine is bound to.
        """
        probe_root, probe_data = build_substrate(tmp_path / "probe")
        probe = ControlPlane.discover(
            data_dir=probe_data,
            repository_root=probe_root,
            journal_root=tmp_path / "probe-runtime",
        )
        universe = probe.manifest.universe_id

        claimed = [dict(a) for a in FIXTURE_ARTIFACTS]
        claimed[0]["owner"] = universe
        repository_root, data_dir = build_substrate(tmp_path / "own", artifacts=tuple(claimed))
        plane = ControlPlane.discover(
            data_dir=data_dir,
            repository_root=repository_root,
            journal_root=tmp_path / "own-runtime",
        )
        agents = [a.agent_id for a in plane.agents.all()]
        assert agents.count(universe) == 1
