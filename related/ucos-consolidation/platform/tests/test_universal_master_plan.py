"""UCOS-CTRL-PLAN-000001 — Master Plan Engine (Wave 12) validation suite.

The suite the wave enters the coverage gate carrying. It exercises the seven things the wave
was required to make true — aggregation, normalization, identity, lineage, dependency mapping,
composition and projection — and it exercises them the way the repository requires: against
the real composed control plane for the integration claims, and against small constructed
snapshots for the behavioural ones, so a failure names the behaviour rather than the substrate.

Three properties are asserted as *proofs* rather than comparisons. Membership fidelity: the
plan holds exactly one node per planning entity the snapshot carries and no node for the
registration, governance, certification, version, ownership, dependency or capability records
that belong to other authorities. Determinism: composing the same snapshot twice yields the
same plan identity, which can only hold if no clock and no iteration order leaked in. Replay:
the journal reconstructs the plan through the same normalization and linkage rules that built
it, so equal identity means the plan was recovered rather than copied.

The suite also pins the wave's central restraint. An edge exists only where an identifier the
state already carries resolves to an entity the state already holds; an unresolvable reference
produces no edge and is *counted*. Several tests below exist purely to keep a future change
from turning that measured absence into a fabricated relationship.
"""

from __future__ import annotations

import tempfile
from pathlib import Path
from platform.universal_control_plane import ControlPlane
from platform.universal_control_plane.durable import DurableJournal
from platform.universal_control_plane.ontology import (
    LIFECYCLE_ACTIVE,
    LIFECYCLE_DRAFT,
    PRIORITY_HIGH,
    BacklogItem,
    Goal,
    Milestone,
    Objective,
    Vision,
)
from platform.universal_master_plan import (
    EDGE_CONTAINS,
    EDGE_REQUIRES,
    EVENT_PLAN_COMPOSED,
    MAX_LINEAGE_DEPTH,
    PLAN_KINDS,
    MasterPlan,
    MasterPlanEngine,
    MasterPlanError,
    MasterPlanRegistry,
    PlanDelta,
    PlanEdge,
    PlanNode,
    compose_edges,
    compose_plan,
    is_plan_entity,
    plan_dependencies,
    plan_entries,
    plan_from_payload,
    plan_kinds,
    plan_payload,
    plan_references,
    reconstruct,
    reconstruct_all,
    reconstruct_at,
    record_plan,
    replays,
)
from platform.universal_project_state import (
    EVENT_STATE_PROJECTED,
    ProjectStateEngine,
    ProjectStateSnapshot,
    StateEntity,
    discover_entity_kinds,
)

import pytest

REPO = Path(__file__).resolve().parents[2]


# ---------------------------------------------------------------------------
# fixtures — small constructed state; no repository scan
# ---------------------------------------------------------------------------


def _entity(kind: str, entity_id: str, **attributes: object) -> StateEntity:
    """A state entity built from a projection shaped exactly as the ontology emits one."""
    raw: dict[str, object] = {
        "kind": kind,
        "identity": f"id-{entity_id}",
        f"{kind.lower()}_id": entity_id,
    }
    raw.update(attributes)
    return StateEntity.from_projection(raw, tick=1)


def _snapshot(*entities: StateEntity) -> ProjectStateSnapshot:
    return ProjectStateSnapshot(
        universe_id="UCOS-CTRL-000001", truth_id="truth-1", entities=entities, tick=1
    )


def _ontology_snapshot() -> ProjectStateSnapshot:
    """A snapshot of real ontology objects wired the way the control plane wires them."""
    vision = Vision(vision_id="VIS-1", universe_id="U-1", statement="the declared direction")
    goal = Goal(goal_id="GOAL-1", vision_id="VIS-1", title="Programme A", priority=PRIORITY_HIGH)
    objective = Objective(
        objective_id="OBJ-1", goal_id="GOAL-1", title="A/CAT", success_criteria="governed"
    )
    milestone = Milestone(
        milestone_id="MS-1",
        universe_id="U-1",
        title="Volume 1",
        sequence=1,
        objective_ids=("OBJ-1",),
    )
    item = BacklogItem(
        item_id="ITEM-1",
        universe_id="U-1",
        title="fix it",
        milestone_id="MS-1",
        objective_id="OBJ-1",
        estimate=5,
        state=LIFECYCLE_DRAFT,
    )
    return _snapshot(
        *(
            StateEntity.from_projection(obj.to_dict(), tick=1)
            for obj in (vision, goal, objective, milestone, item)
        )
    )


@pytest.fixture(scope="module")
def plane() -> ControlPlane:
    """The real composed control plane — the substrate the master plan is derived from."""
    return ControlPlane.discover()


@pytest.fixture(scope="module")
def derived(plane: ControlPlane) -> tuple[MasterPlanEngine, MasterPlan]:
    """One real derivation, journalled, shared by the integration assertions."""
    engine = MasterPlanEngine(journal=DurableJournal.open(tempfile.mkdtemp()))
    return engine, engine.derive(plane, tick=1)


# ---------------------------------------------------------------------------
# membership — the declared planning vocabulary, and nothing beside it
# ---------------------------------------------------------------------------


def test_the_planning_vocabulary_is_the_declared_seven_kinds():
    assert plan_kinds() == PLAN_KINDS
    assert set(PLAN_KINDS) == {
        "Vision",
        "Goal",
        "Objective",
        "Milestone",
        "BacklogItem",
        "Assignment",
        "ProgressRecord",
    }
    assert PLAN_KINDS == tuple(sorted(PLAN_KINDS)), "membership must be deterministically ordered"


def test_every_declared_plan_kind_exists_in_the_control_plane_ontology():
    """The declaration is resolved against the ontology, so a rename fails loudly."""
    known = set(discover_entity_kinds())
    assert set(PLAN_KINDS) <= known


def test_the_populations_owned_by_other_authorities_are_not_planning_kinds():
    for excluded in (
        "RegistrationRecord",
        "GovernanceRecord",
        "CertificationState",
        "VersionRecord",
        "OwnershipRecord",
        "DependencyRecord",
        "Capability",
    ):
        assert excluded not in PLAN_KINDS
        assert not is_plan_entity(_entity(excluded, "X-1"))


def test_membership_is_decided_by_kind_alone():
    assert is_plan_entity(_entity("Goal", "G-1"))
    assert not is_plan_entity(_entity("ArtifactRecord", "ART-1"))


def test_a_declared_plan_kind_the_ontology_no_longer_defines_fails_closed(
    monkeypatch: pytest.MonkeyPatch,
):
    from platform.universal_master_plan import master_plan as module

    monkeypatch.setattr(module, "PLAN_KINDS", (*PLAN_KINDS, "RenamedAwayEntity"))
    with pytest.raises(MasterPlanError, match="absent from the control-plane ontology"):
        module.plan_kinds()
    with pytest.raises(MasterPlanError, match="RenamedAwayEntity"):
        module.compose_plan(_ontology_snapshot())


# ---------------------------------------------------------------------------
# aggregation
# ---------------------------------------------------------------------------


def test_every_planning_entity_becomes_exactly_one_plan_node():
    snapshot = _ontology_snapshot()
    plan = compose_plan(snapshot)
    assert len(plan.nodes) == len(snapshot.entities)
    assert {n.node_id for n in plan.nodes} == {e.subject_id for e in snapshot.entities}


def test_an_entity_belonging_to_another_authority_is_not_projected():
    """The plan reads the planning vocabulary; it does not re-read governed populations."""
    snapshot = _snapshot(
        _entity("Goal", "G-1"),
        _entity("Capability", "CAP-1"),
        _entity("GovernanceRecord", "GOV-1"),
        _entity("VersionRecord", "VER-1"),
    )
    plan = compose_plan(snapshot)
    assert plan.kinds() == ("Goal",)
    assert plan.counts()["nodes"] == 1
    assert len(snapshot.entities) == 4, "the snapshot still holds them; the plan just isn't them"


def test_an_excluded_entity_cannot_become_a_plan_parent():
    """Excluding a kind excludes its edges too — no half-membership through linkage."""
    plan = compose_plan(
        _snapshot(_entity("Capability", "CAP-1"), _entity("Goal", "G-1", capability_id="CAP-1"))
    )
    assert plan.edges == ()
    assert plan.unresolved_references() == (("Goal::G-1", "capability_id", "CAP-1"),)


def test_an_empty_snapshot_composes_an_empty_plan_rather_than_failing():
    plan = compose_plan(_snapshot())
    assert plan.nodes == () and plan.edges == ()
    assert plan.counts()["nodes"] == 0
    assert plan.linkage_coverage() == 0.0
    assert plan.containment_coverage() == 0.0
    assert plan.height() == 0
    assert plan.acyclic()


def test_the_plan_inherits_the_state_it_projects():
    snapshot = _ontology_snapshot()
    plan = compose_plan(snapshot)
    assert plan.universe_id == snapshot.universe_id
    assert plan.truth_id == snapshot.truth_id
    assert plan.snapshot_id == snapshot.snapshot_id
    assert plan.tick == snapshot.tick


# ---------------------------------------------------------------------------
# normalization — one shape, read from what the ontology publishes
# ---------------------------------------------------------------------------


def test_normalization_reads_lifecycle_and_owner_from_project_state_not_again():
    entity = _entity("BacklogItem", "ITEM-1", state=LIFECYCLE_ACTIVE, owner="Terminal T5")
    node = PlanNode.from_entity(entity)
    assert node.lifecycle == entity.lifecycle == LIFECYCLE_ACTIVE
    assert node.owner == entity.owner == "Terminal T5"
    assert node.node_id == entity.subject_id


def test_normalization_reads_the_title_keys_the_ontology_publishes():
    assert PlanNode.from_entity(_entity("Goal", "G-1", title="a title")).title == "a title"
    assert PlanNode.from_entity(_entity("Vision", "V-1", statement="a claim")).title == "a claim"
    assert PlanNode.from_entity(_entity("ProgressRecord", "P-1")).title == ""


def test_title_precedence_is_declared_and_stable():
    node = PlanNode.from_entity(_entity("Goal", "G-1", title="T", statement="S"))
    assert node.title == "T"


def test_absent_ordering_facts_are_reported_absent_rather_than_defaulted():
    node = PlanNode.from_entity(_entity("Goal", "G-1"))
    assert node.title == "" and node.priority == ""
    assert node.sequence == 0 and node.estimate == 0


def test_ordering_facts_are_read_when_the_entity_publishes_them():
    node = PlanNode.from_entity(
        _entity("Milestone", "MS-1", priority=PRIORITY_HIGH, sequence=7, estimate=3)
    )
    assert (node.priority, node.sequence, node.estimate) == (PRIORITY_HIGH, 7, 3)


def test_a_non_numeric_ordering_fact_is_measured_as_absent_not_guessed():
    node = PlanNode.from_entity(_entity("Milestone", "MS-1", sequence="seventh", estimate=None))
    assert node.sequence == 0 and node.estimate == 0
    numeric = PlanNode.from_entity(_entity("Milestone", "MS-2", sequence="7"))
    assert numeric.sequence == 7


def test_a_boolean_is_not_read_as_a_number():
    assert PlanNode.from_entity(_entity("Milestone", "MS-1", sequence=True)).sequence == 0


def test_a_real_ontology_object_normalizes_through_its_own_projection():
    goal = Goal(goal_id="GOAL-1", vision_id="VIS-1", title="Programme A", priority=PRIORITY_HIGH)
    node = PlanNode.from_entity(StateEntity.from_projection(goal.to_dict(), tick=1))
    assert node.kind == "Goal" and node.entity_id == "GOAL-1"
    assert node.title == "Programme A" and node.priority == PRIORITY_HIGH
    assert node.references == (("vision_id", "VIS-1"),)


# ---------------------------------------------------------------------------
# reference reading — the entity's own identifier is never a reference
# ---------------------------------------------------------------------------


def test_the_entitys_own_identifier_is_not_read_as_a_reference():
    raw = {"kind": "Goal", "identity": "x", "goal_id": "GOAL-1", "vision_id": "VIS-1"}
    assert plan_references(raw) == (("vision_id", "VIS-1"),)


def test_the_first_non_empty_identifier_is_the_subject_exactly_as_state_decides():
    """Reading positionally is what keeps a foreign key from becoming the subject."""
    raw = {"kind": "Goal", "identity": "x", "goal_id": "", "vision_id": "VIS-1"}
    # goal_id is empty, so vision_id is the subject — the identical rule entity_id_of applies.
    assert plan_references(raw) == ()


def test_a_collection_of_identifiers_is_read_as_many_references():
    raw = {
        "kind": "Milestone",
        "milestone_id": "MS-1",
        "objective_ids": ["OBJ-1", "OBJ-2", ""],
    }
    assert plan_references(raw) == (("objective_ids", "OBJ-1"), ("objective_ids", "OBJ-2"))


def test_a_collection_key_holding_a_scalar_yields_nothing_rather_than_a_guess():
    assert plan_references({"kind": "M", "m_id": "M-1", "objective_ids": "OBJ-1"}) == ()


def test_an_empty_or_absent_reference_yields_nothing():
    raw = {"kind": "BacklogItem", "item_id": "ITEM-1", "milestone_id": "", "objective_id": None}
    assert plan_references(raw) == ()


def test_dependencies_are_read_through_project_states_own_key():
    raw = {"kind": "Goal", "goal_id": "G-1", "dependencies": ["G-0", "G-0", ""]}
    assert plan_dependencies(raw) == (("dependencies", "G-0"),)
    assert plan_dependencies({"kind": "Goal", "goal_id": "G-1"}) == ()


def test_targets_reports_every_named_identifier_once_in_declared_order():
    node = PlanNode.from_entity(
        _entity(
            "BacklogItem",
            "ITEM-1",
            milestone_id="MS-1",
            objective_id="OBJ-1",
            dependencies=["MS-1", "ITEM-0"],
        )
    )
    assert node.targets() == ("MS-1", "OBJ-1", "ITEM-0")


# ---------------------------------------------------------------------------
# identity — content-addressed, tick-free
# ---------------------------------------------------------------------------


def test_node_identity_is_content_addressed_and_ignores_the_tick():
    raw = {"kind": "Goal", "goal_id": "G-1", "title": "t"}
    left = PlanNode.from_entity(StateEntity.from_projection(raw, tick=1))
    right = PlanNode.from_entity(StateEntity.from_projection(raw, tick=99))
    assert left.identity == right.identity, "a logical tick is not content"
    other = PlanNode.from_entity(StateEntity.from_projection({**raw, "title": "u"}, tick=1))
    assert other.identity != left.identity


def test_composing_the_same_snapshot_twice_yields_the_same_plan_identity():
    snapshot = _ontology_snapshot()
    assert compose_plan(snapshot).plan_id == compose_plan(snapshot).plan_id


def test_plan_identity_changes_when_a_node_changes():
    base = _ontology_snapshot()
    mutated = _snapshot(*base.entities[:-1])
    assert compose_plan(mutated).plan_id != compose_plan(base).plan_id


def test_plan_identity_binds_the_truth_and_the_snapshot_it_projects():
    entities = _ontology_snapshot().entities
    left = ProjectStateSnapshot(universe_id="U", truth_id="t-1", entities=entities, tick=1)
    right = ProjectStateSnapshot(universe_id="U", truth_id="t-2", entities=entities, tick=1)
    assert compose_plan(left).plan_id != compose_plan(right).plan_id


def test_edge_identity_is_content_addressed_and_readable():
    edge = PlanEdge("Goal::G-1", "Objective::OBJ-1", EDGE_CONTAINS, "goal_id")
    assert edge.edge_id == "CONTAINS:Goal::G-1->Objective::OBJ-1:goal_id"
    assert (
        edge.identity
        == PlanEdge("Goal::G-1", "Objective::OBJ-1", EDGE_CONTAINS, "goal_id").identity
    )
    assert edge.to_dict()["edge_kind"] == EDGE_CONTAINS


# ---------------------------------------------------------------------------
# linkage — only what the state supports, and absence is measured
# ---------------------------------------------------------------------------


def test_containment_edges_are_resolved_from_published_identifiers():
    plan = compose_plan(_ontology_snapshot())
    assert "Goal::GOAL-1" in plan.parents_of("Objective::OBJ-1")
    assert "Objective::OBJ-1" in plan.children_of("Goal::GOAL-1")
    assert "Milestone::MS-1" in plan.parents_of("BacklogItem::ITEM-1")
    assert "Objective::OBJ-1" in plan.parents_of("BacklogItem::ITEM-1")
    # A collection of identifiers resolves by the same rule: the node that publishes the
    # reference is the child, so the milestone's objective_ids place it under the objective.
    assert "Objective::OBJ-1" in plan.parents_of("Milestone::MS-1")
    assert plan.edges_of_kind(EDGE_CONTAINS)[0].attribute in {
        "goal_id",
        "milestone_id",
        "objective_id",
        "objective_ids",
        "vision_id",
    }


def test_an_unresolvable_reference_produces_no_edge_and_is_counted():
    plan = compose_plan(_snapshot(_entity("Goal", "G-1", vision_id="VIS-MISSING")))
    assert plan.edges == ()
    assert plan.unresolved_references() == (("Goal::G-1", "vision_id", "VIS-MISSING"),)
    assert plan.counts()["unresolved_references"] == 1


def test_the_real_universe_reference_is_left_absent_rather_than_invented():
    """Vision names a universe; no Universe entity is populated, so no parent is fabricated."""
    plan = compose_plan(_ontology_snapshot())
    assert plan.parents_of("Vision::VIS-1") == ()
    assert ("Vision::VIS-1", "universe_id", "U-1") in plan.unresolved_references()


def test_a_reference_resolving_to_several_entities_links_to_each_and_is_counted():
    plan = compose_plan(
        _snapshot(
            _entity("Goal", "SHARED"),
            _entity("Milestone", "SHARED"),
            _entity("Objective", "OBJ-1", goal_id="SHARED"),
        )
    )
    parents = plan.parents_of("Objective::OBJ-1")
    assert parents == ("Goal::SHARED", "Milestone::SHARED")
    assert plan.counts()["ambiguous_references"] == 1


def test_a_self_reference_never_becomes_an_edge():
    plan = compose_plan(_snapshot(_entity("Goal", "G-1", dependencies=["G-1"])))
    assert plan.edges == ()
    assert plan.unresolved_references() == ()


def test_a_containment_self_reference_never_becomes_an_edge():
    """A second identifier naming the entity itself is not a parent of itself."""
    plan = compose_plan(_snapshot(_entity("Goal", "G-1", peer_id="G-1")))
    assert plan.edges == ()
    assert plan.roots() == ("Goal::G-1",)


def test_two_attributes_naming_one_parent_are_one_adjacency_but_two_edges():
    """The edges are attributed separately; the graph they induce holds the target once."""
    plan = compose_plan(
        _snapshot(
            _entity("Milestone", "SHARED"),
            _entity("BacklogItem", "ITEM-1", milestone_id="SHARED", objective_id="SHARED"),
        )
    )
    assert len(plan.edges) == 2
    assert {e.attribute for e in plan.edges} == {"milestone_id", "objective_id"}
    assert plan.parents_of("BacklogItem::ITEM-1") == ("Milestone::SHARED",)
    assert plan.children_of("Milestone::SHARED") == ("BacklogItem::ITEM-1",)
    assert plan.depths() == {"BacklogItem::ITEM-1": 1, "Milestone::SHARED": 0}


def test_plan_identity_and_plan_id_are_one_value():
    plan = compose_plan(_ontology_snapshot())
    assert plan.identity == plan.plan_id


def test_dependency_edges_run_from_the_dependent_to_its_dependency():
    plan = compose_plan(
        _snapshot(_entity("Goal", "G-1", dependencies=["G-0"]), _entity("Goal", "G-0"))
    )
    assert plan.requires("Goal::G-1") == ("Goal::G-0",)
    assert plan.required_by("Goal::G-0") == ("Goal::G-1",)
    assert plan.edges_of_kind(EDGE_REQUIRES)[0].kind == EDGE_REQUIRES
    assert plan.edges_of_kind(EDGE_CONTAINS) == ()


def test_edges_are_de_duplicated_and_deterministically_ordered():
    snapshot = _ontology_snapshot()
    left, right = compose_plan(snapshot).edges, compose_plan(snapshot).edges
    assert left == right
    assert len({e.edge_id for e in left}) == len(left)
    assert [e.edge_id for e in left] == sorted(e.edge_id for e in left)


def test_compose_edges_over_no_nodes_is_empty():
    assert compose_edges(()) == ()


def test_roots_leaves_and_isolation_are_measured_from_the_edges_that_exist():
    plan = compose_plan(_ontology_snapshot())
    assert "Vision::VIS-1" in plan.roots()
    assert "BacklogItem::ITEM-1" in plan.leaves()
    lonely = compose_plan(_snapshot(_entity("Goal", "G-1")))
    assert lonely.isolated() == ("Goal::G-1",)
    assert lonely.linkage_coverage() == 0.0
    assert lonely.containment_coverage() == 0.0


def test_coverage_is_a_fraction_of_the_population_it_measures():
    plan = compose_plan(_ontology_snapshot())
    assert 0.0 < plan.containment_coverage() <= 1.0
    assert 0.0 < plan.linkage_coverage() <= 1.0


# ---------------------------------------------------------------------------
# lineage
# ---------------------------------------------------------------------------


def test_lineage_is_the_containment_chain_nearest_ancestor_last():
    plan = compose_plan(
        _snapshot(
            _entity("Vision", "VIS-1"),
            _entity("Goal", "GOAL-1", vision_id="VIS-1"),
            _entity("Objective", "OBJ-1", goal_id="GOAL-1"),
        )
    )
    assert plan.lineage_of("Objective::OBJ-1") == ("Vision::VIS-1", "Goal::GOAL-1")
    assert plan.lineage_of("Vision::VIS-1") == ()


def test_lineage_of_an_unknown_node_fails_closed():
    with pytest.raises(MasterPlanError, match="no such plan node"):
        compose_plan(_ontology_snapshot()).lineage_of("Goal::NOPE")


def test_lineage_terminates_on_a_cyclic_projection_rather_than_hanging():
    plan = compose_plan(
        _snapshot(
            _entity("Goal", "A", peer_id="B"),
            _entity("Goal", "B", peer_id="A"),
        )
    )
    assert plan.lineage_of("Goal::A") == ("Goal::B",)
    assert not plan.acyclic()
    assert plan.cycles() == ("Goal::A", "Goal::B")


def test_depths_are_computed_for_the_whole_plan_at_once():
    plan = compose_plan(
        _snapshot(
            _entity("Vision", "VIS-1"),
            _entity("Goal", "GOAL-1", vision_id="VIS-1"),
            _entity("Objective", "OBJ-1", goal_id="GOAL-1"),
        )
    )
    assert plan.depths() == {"Goal::GOAL-1": 1, "Objective::OBJ-1": 2, "Vision::VIS-1": 0}
    assert plan.depth_of("Objective::OBJ-1") == 2
    assert plan.height() == 2


def test_a_node_unreachable_from_any_root_reports_an_absent_depth():
    plan = compose_plan(
        _snapshot(_entity("Goal", "A", peer_id="B"), _entity("Goal", "B", peer_id="A"))
    )
    assert plan.depth_of("Goal::A") == -1


def test_a_lineage_deeper_than_the_declared_bound_is_truncated_not_unbounded():
    depth = MAX_LINEAGE_DEPTH + 6
    chain = [_entity("Goal", "G-0")]
    chain.extend(_entity("Goal", f"G-{i}", parent_id=f"G-{i - 1}") for i in range(1, depth))
    plan = compose_plan(_snapshot(*chain))
    lineage = plan.lineage_of(f"Goal::G-{depth - 1}")
    assert len(lineage) == MAX_LINEAGE_DEPTH, "the walk stops at the declared bound"
    assert plan.depth_of(f"Goal::G-{depth - 1}") == depth - 1, "depth is computed without the bound"


# ---------------------------------------------------------------------------
# composition and ordering
# ---------------------------------------------------------------------------


def test_the_ordering_places_a_parent_before_its_child():
    plan = compose_plan(_ontology_snapshot())
    order = plan.topological()
    assert set(order) == {n.node_id for n in plan.nodes}
    assert order.index("Goal::GOAL-1") < order.index("Objective::OBJ-1")
    assert order.index("Milestone::MS-1") < order.index("BacklogItem::ITEM-1")


def test_the_ordering_is_a_function_of_the_plan_and_nothing_else():
    snapshot = _ontology_snapshot()
    assert compose_plan(snapshot).topological() == compose_plan(snapshot).topological()


def test_a_dependency_is_ordered_before_the_node_requiring_it():
    plan = compose_plan(
        _snapshot(_entity("Goal", "G-1", dependencies=["G-0"]), _entity("Goal", "G-0"))
    )
    order = plan.topological()
    assert order.index("Goal::G-1") < order.index("Goal::G-0")
    # Containment is measured separately: a dependency edge places nothing under a parent.
    assert plan.depths() == {"Goal::G-0": 0, "Goal::G-1": 0}
    assert plan.lineage_of("Goal::G-0") == ()


def test_a_cyclic_node_is_left_unordered_rather_than_given_an_invented_position():
    plan = compose_plan(
        _snapshot(_entity("Goal", "A", peer_id="B"), _entity("Goal", "B", peer_id="A"))
    )
    assert plan.topological() == ()
    assert plan.cycles() == ("Goal::A", "Goal::B")


def test_projection_reports_the_composed_structure():
    plan = compose_plan(_ontology_snapshot())
    projection = plan.projection()
    assert projection["plan_id"] == plan.plan_id
    assert projection["order"] == list(plan.topological())
    assert projection["roots"] == list(plan.roots())
    assert projection["by_kind"]["Goal"] == 1


def test_the_plan_projection_carries_its_measurements():
    body = compose_plan(_ontology_snapshot()).to_dict()
    assert body["kind"] == "MasterPlan"
    assert body["identity"] == body["plan_id"]
    assert body["counts"]["nodes"] == 5
    assert body["acyclic"] is True
    assert set(body) >= {"universe_id", "truth_id", "snapshot_id", "digest", "height"}


def test_node_and_edge_projections_are_complete():
    plan = compose_plan(_ontology_snapshot())
    node = plan.node("Goal::GOAL-1").to_dict()
    assert node["kind"] == "PlanNode" and node["node_id"] == "Goal::GOAL-1"
    assert node["references"] == [["vision_id", "VIS-1"]]
    assert plan.edges[0].to_dict()["kind"] == "PlanEdge"


def test_node_lookup_fails_closed():
    with pytest.raises(MasterPlanError, match="no such plan node"):
        compose_plan(_ontology_snapshot()).node("Goal::NOPE")


def test_of_kind_and_owners_report_the_populations_they_hold():
    plan = compose_plan(_snapshot(_entity("Goal", "G-1", owner="T5"), _entity("Goal", "G-2")))
    assert len(plan.of_kind("Goal")) == 2
    assert plan.of_kind("Vision") == ()
    assert plan.owners() == ("T5",)
    assert plan.by_kind() == {"Goal": 2}


def test_the_plan_digest_is_the_digest_of_its_node_identities():
    snapshot = _ontology_snapshot()
    assert compose_plan(snapshot).digest() == compose_plan(snapshot).digest()


# ---------------------------------------------------------------------------
# the delta
# ---------------------------------------------------------------------------


def test_a_plan_delta_measures_added_removed_and_changed_nodes():
    before = compose_plan(_snapshot(_entity("Goal", "G-1"), _entity("Goal", "G-2")))
    after = compose_plan(_snapshot(_entity("Goal", "G-1", title="renamed"), _entity("Goal", "G-3")))
    delta = PlanDelta.between(before, after)
    assert delta.added == ("Goal::G-3",)
    assert delta.removed == ("Goal::G-2",)
    assert delta.changed == ("Goal::G-1",)
    assert not delta.empty
    assert delta.to_dict()["counts"] == {"added": 1, "removed": 1, "changed": 1}


def test_an_unchanged_plan_has_an_empty_delta():
    snapshot = _ontology_snapshot()
    delta = PlanDelta.between(compose_plan(snapshot), compose_plan(snapshot))
    assert delta.empty and delta.to_dict()["empty"] is True


# ---------------------------------------------------------------------------
# the registry
# ---------------------------------------------------------------------------


def test_the_registry_holds_a_plan_with_its_nodes_and_edges():
    registry = MasterPlanRegistry()
    plan = registry.register_plan(compose_plan(_ontology_snapshot()))
    assert registry.plan(plan.plan_id) is plan
    assert registry.latest() is plan
    assert registry.count() == len(plan.nodes)
    assert len(registry.edges()) == len(plan.edges)
    assert registry.plan_ids() == (plan.plan_id,)


def test_registration_is_idempotent_by_identity():
    registry = MasterPlanRegistry()
    plan = compose_plan(_ontology_snapshot())
    registry.register_plan(plan)
    registry.register_plan(plan)
    assert registry.plan_count() == 1
    assert registry.replacements() == {}


def test_a_changed_node_is_a_recorded_replacement_not_a_silent_duplicate():
    registry = MasterPlanRegistry()
    registry.register_plan(compose_plan(_snapshot(_entity("Goal", "G-1"))))
    registry.register_plan(compose_plan(_snapshot(_entity("Goal", "G-1", title="new"))))
    assert registry.count() == 1
    assert registry.replacements() == {"Goal::G-1": 1}
    assert registry.plan_count() == 2
    assert registry.node("Goal::G-1").title == "new"


def test_the_registry_indexes_containment_dependency_kind_and_owner():
    registry = MasterPlanRegistry()
    registry.register_plan(
        compose_plan(
            _snapshot(
                _entity("Goal", "G-1", owner="T5"),
                _entity("Objective", "OBJ-1", goal_id="G-1", dependencies=["G-1"]),
            )
        )
    )
    assert registry.children_of("Goal::G-1") == ("Objective::OBJ-1",)
    assert registry.parents_of("Objective::OBJ-1") == ("Goal::G-1",)
    assert registry.dependencies_of("Objective::OBJ-1") == ("Goal::G-1",)
    assert registry.dependents_of("Goal::G-1") == ("Objective::OBJ-1",)
    assert registry.kinds() == ("Goal", "Objective")
    assert registry.of_kind("Goal")[0].node_id == "Goal::G-1"
    assert registry.owners() == ("T5",)
    assert registry.owned_by("T5")[0].node_id == "Goal::G-1"
    assert [n.node_id for n in registry.unowned()] == ["Objective::OBJ-1"]
    assert registry.coverage() == 0.5


def test_the_registry_selects_plans_by_the_state_they_project():
    registry = MasterPlanRegistry()
    snapshot = _ontology_snapshot()
    plan = registry.register_plan(compose_plan(snapshot))
    assert registry.plans_for_snapshot(snapshot.snapshot_id) == (plan,)
    assert registry.plans_for_truth("truth-1") == (plan,)
    assert registry.plans_for_truth("truth-absent") == ()


def test_the_registry_fails_closed_on_absence():
    registry = MasterPlanRegistry()
    with pytest.raises(MasterPlanError, match="no master plan has been registered"):
        registry.latest()
    with pytest.raises(MasterPlanError, match="no such master plan"):
        registry.plan("nope")
    with pytest.raises(MasterPlanError, match="no such plan node"):
        registry.node("Goal::NOPE")


def test_a_node_without_an_identifier_is_refused():
    registry = MasterPlanRegistry()
    with pytest.raises(MasterPlanError, match="non-empty entity_id"):
        registry.register_node(PlanNode(kind="Goal", entity_id=" "))


def test_a_plan_without_a_plan_id_is_refused():
    class _Unidentified:
        plan_id = ""
        nodes: tuple[PlanNode, ...] = ()
        edges: tuple[PlanEdge, ...] = ()

    with pytest.raises(MasterPlanError, match="resolvable plan_id"):
        MasterPlanRegistry().register_plan(_Unidentified())  # type: ignore[arg-type]


def test_the_registry_projection_reports_its_populations():
    registry = MasterPlanRegistry()
    registry.register_plan(compose_plan(_ontology_snapshot()))
    body = registry.to_dict()
    assert body["engine"] == "MasterPlanRegistry"
    assert body["counts"]["plans"] == 1 and body["counts"]["nodes"] == 5
    assert body["by_kind"]["Milestone"] == 1
    assert registry.node_ids() == tuple(sorted(registry.node_ids()))
    assert registry.coverage() == 0.0


# ---------------------------------------------------------------------------
# replay — through the journal the control plane already owns
# ---------------------------------------------------------------------------


def test_a_plan_is_journalled_under_the_declared_event_token(tmp_path: Path):
    journal = DurableJournal.open(tmp_path)
    plan = compose_plan(_ontology_snapshot())
    entry = record_plan(journal, plan, tick=1)
    assert entry.event == EVENT_PLAN_COMPOSED
    assert entry.subject_id == plan.plan_id
    assert len(plan_entries(journal)) == 1
    assert journal.verify()


def test_the_journal_reconstructs_the_plan_identity_exactly(tmp_path: Path):
    journal = DurableJournal.open(tmp_path)
    plan = compose_plan(_ontology_snapshot())
    record_plan(journal, plan, tick=1)
    replayed = reconstruct(journal)
    assert replayed.plan_id == plan.plan_id
    assert replayed.edges == plan.edges, "linkage is re-resolved, not re-serialised"
    assert replays(journal, plan)


def test_reconstruction_rebuilds_normalization_rather_than_copying_it(tmp_path: Path):
    journal = DurableJournal.open(tmp_path)
    plan = compose_plan(_ontology_snapshot())
    record_plan(journal, plan, tick=1)
    payload = plan_entries(journal)[-1].payload
    assert "title" not in payload, "the payload carries projections, not normalized nodes"
    replayed = reconstruct(journal)
    assert replayed.node("Goal::GOAL-1").title == "Programme A"


def test_every_recorded_plan_is_reconstructable_by_history_and_by_sequence(tmp_path: Path):
    journal = DurableJournal.open(tmp_path)
    first = compose_plan(_snapshot(_entity("Goal", "G-1")))
    second = compose_plan(_snapshot(_entity("Goal", "G-1"), _entity("Goal", "G-2")))
    entry = record_plan(journal, first, tick=1)
    record_plan(journal, second, tick=2)
    history = reconstruct_all(journal)
    assert [p.plan_id for p in history] == [first.plan_id, second.plan_id]
    assert reconstruct_at(journal, entry.sequence).plan_id == first.plan_id


def test_replay_fails_closed_on_an_empty_or_wrong_journal(tmp_path: Path):
    journal = DurableJournal.open(tmp_path)
    with pytest.raises(MasterPlanError, match="no PLAN_COMPOSED entry to replay"):
        reconstruct(journal)
    assert not replays(journal, compose_plan(_ontology_snapshot()))
    record_plan(journal, compose_plan(_snapshot(_entity("Goal", "G-1"))), tick=1)
    with pytest.raises(MasterPlanError, match="no PLAN_COMPOSED entry at 99"):
        reconstruct_at(journal, 99)
    assert not replays(journal, compose_plan(_ontology_snapshot()))


def test_a_malformed_payload_is_refused_rather_than_half_reconstructed():
    with pytest.raises(MasterPlanError, match="carries no nodes array"):
        plan_from_payload({"universe_id": "U"})
    with pytest.raises(MasterPlanError, match="carries no nodes array"):
        plan_from_payload({"nodes": "not-an-array"})
    with pytest.raises(MasterPlanError, match="not an object"):
        plan_from_payload({"nodes": ["not-an-object"]})


def test_the_payload_is_the_declared_shape():
    plan = compose_plan(_ontology_snapshot())
    payload = plan_payload(plan)
    assert set(payload) == {"universe_id", "truth_id", "snapshot_id", "tick", "nodes"}
    assert len(payload["nodes"]) == len(plan.nodes)
    assert payload["snapshot_id"] == plan.snapshot_id


def test_a_tampered_chain_is_not_replayable(tmp_path: Path):
    journal = DurableJournal.open(tmp_path)
    plan = compose_plan(_ontology_snapshot())
    record_plan(journal, plan, tick=1)
    original = journal.path.read_text("utf-8")
    assert "Programme A" in original, "the payload carries the projection it recorded"
    journal.path.write_text(original.replace("Programme A", "Programme B"), "utf-8")
    tampered = DurableJournal.open(tmp_path)
    assert not replays(tampered, plan), "an edited payload no longer matches its digest"


# ---------------------------------------------------------------------------
# the engine
# ---------------------------------------------------------------------------


def test_the_engine_composes_registers_and_records_in_one_call(tmp_path: Path):
    engine = MasterPlanEngine(journal=DurableJournal.open(tmp_path))
    plan = engine.compose(_ontology_snapshot(), tick=1)
    assert engine.plan() is plan
    assert engine.registry.latest() is plan
    assert engine.replayable()
    assert engine.counts()["plans"] == 1


def test_the_engine_fails_closed_before_anything_is_composed():
    engine = MasterPlanEngine()
    with pytest.raises(MasterPlanError, match="no master plan has been composed"):
        engine.plan()
    assert engine.plans() == ()
    assert engine.delta().empty
    assert not engine.replayable()
    assert engine.counts() == {
        "plans": 0,
        "nodes": 0,
        "kinds": 0,
        "edges": 0,
        "roots": 0,
        "cycles": 0,
    }
    assert engine.to_dict()["plan"] is None


def test_the_engine_measures_the_delta_between_successive_plans():
    engine = MasterPlanEngine()
    engine.compose(_snapshot(_entity("Goal", "G-1")), tick=1)
    engine.compose(_snapshot(_entity("Goal", "G-1"), _entity("Goal", "G-2")), tick=2)
    assert engine.delta().added == ("Goal::G-2",)
    assert len(engine.plans()) == 2


def test_the_engine_projects_lineage_dependencies_order_and_absence():
    engine = MasterPlanEngine()
    engine.compose(_ontology_snapshot(), tick=1)
    assert engine.lineage_of("Objective::OBJ-1")[-1] in {"Goal::GOAL-1", "Milestone::MS-1"}
    assert engine.dependencies_of("BacklogItem::ITEM-1") == ()
    assert engine.order()[0] in engine.plan().roots()
    assert any(ref[1] == "universe_id" for ref in engine.unresolved())


def test_the_engine_reuses_wave_eleven_rather_than_re_deriving_state():
    engine = MasterPlanEngine()
    assert engine.state is None
    first = engine.state_engine()
    assert isinstance(first, ProjectStateEngine)
    assert engine.state_engine() is first, "the state engine is reused, not rebuilt"
    assert first.manifest is engine.manifest


def test_a_replay_without_a_journal_is_reported_false_not_asserted():
    engine = MasterPlanEngine()
    engine.compose(_ontology_snapshot(), tick=1)
    assert not engine.replayable()
    assert engine.to_dict()["replayable"] is False


# ---------------------------------------------------------------------------
# integration — the real composed control plane
# ---------------------------------------------------------------------------


def test_the_real_plane_derives_a_populated_master_plan(
    derived: tuple[MasterPlanEngine, MasterPlan],
):
    _, plan = derived
    assert plan.universe_id == "UCOS-CTRL-000001"
    assert plan.truth_id, "the plan names the Repository Truth it was derived over"
    assert plan.snapshot_id, "the plan names the project state it projects"
    assert len(plan.nodes) > 100, f"the real plane projects far more than this: {len(plan.nodes)}"
    assert len(plan.kinds()) > 5


def test_the_real_plan_holds_one_node_per_planning_entity_and_no_other(
    derived: tuple[MasterPlanEngine, MasterPlan],
):
    engine, plan = derived
    snapshot = engine.state_engine().snapshot()
    planning = {e.subject_id for e in snapshot.entities if is_plan_entity(e)}
    assert {n.node_id for n in plan.nodes} == planning
    assert len(plan.nodes) < len(
        snapshot.entities
    ), "the snapshot holds populations that belong to other authorities"
    assert set(plan.kinds()) <= set(PLAN_KINDS)


def test_the_real_plan_resolves_edges_and_reports_the_references_it_could_not(
    derived: tuple[MasterPlanEngine, MasterPlan],
):
    _, plan = derived
    counts = plan.counts()
    assert counts["edges"] > 0, "the real state publishes identifiers that resolve"
    assert counts["containment_edges"] > 0
    assert counts["roots"] > 0
    # Unresolved references are a measurement of the state, not a failure of the plan.
    assert counts["unresolved_references"] == len(plan.unresolved_references())


def test_the_real_plan_orders_every_node_it_can_and_names_the_rest(
    derived: tuple[MasterPlanEngine, MasterPlan],
):
    _, plan = derived
    order = plan.topological()
    assert len(order) + len(plan.cycles()) == len(plan.nodes)
    assert len(set(order)) == len(order), "no node is ordered twice"


def test_the_real_derivation_is_deterministic(plane: ControlPlane):
    left = MasterPlanEngine().derive(plane, tick=1)
    right = MasterPlanEngine().derive(plane, tick=1)
    assert left.plan_id == right.plan_id, "a plan of one state at one tick is one plan"


def test_the_real_plan_replays_through_the_journal(
    derived: tuple[MasterPlanEngine, MasterPlan],
):
    engine, plan = derived
    assert engine.journal is not None
    assert engine.replayable()
    assert reconstruct(engine.journal).plan_id == plan.plan_id


def test_state_and_plan_share_one_chained_journal(plane: ControlPlane):
    journal = DurableJournal.open(tempfile.mkdtemp())
    engine = MasterPlanEngine(journal=journal)
    engine.derive(plane, tick=1)
    assert len(journal.by_event(EVENT_STATE_PROJECTED)) == 1
    assert len(journal.by_event(EVENT_PLAN_COMPOSED)) == 1
    assert journal.verify()


def test_the_engine_projection_over_the_real_plane_is_complete(
    derived: tuple[MasterPlanEngine, MasterPlan],
):
    engine, plan = derived
    body = engine.to_dict()
    assert body["engine"] == "MasterPlanEngine"
    assert body["universe_id"] == "UCOS-CTRL-000001"
    assert body["plan"]["plan_id"] == plan.plan_id
    assert body["registry"]["counts"]["nodes"] == len(plan.nodes)
    assert body["replayable"] is True


def test_a_shared_child_is_only_counted_once_as_the_frontier_widens() -> None:
    """Two goals containing one milestone: the second parent meets a child already placed.

    The skip arm of the frontier walk is what keeps depths stable under a diamond — a
    plan that re-discarded the shared child would report the shallower parent as deeper
    than the first assignment proved it to be.
    """
    plan = compose_plan(
        _snapshot(
            _entity("Vision", "VIS-1"),
            _entity("Goal", "GOAL-A", vision_id="VIS-1"),
            _entity("Goal", "GOAL-B", vision_id="VIS-1"),
            _entity("Milestone", "M-1", goal_id="GOAL-A"),
        )
    )
    depths = plan.depths()
    assert depths["Milestone::M-1"] == 2
    assert depths["Goal::GOAL-B"] == 1


def test_a_child_claimed_by_two_parents_is_placed_by_the_first_frontier_visit_only() -> None:
    """The already-placed arm of the depths walk: two roots, one shared child.

    A BacklogItem naming both a Milestone and an Objective has two containment parents.
    The frontier meets it twice in one level; the second meeting must skip, so a node's
    depth is decided once and a widened frontier cannot re-decide it.
    """
    plan = compose_plan(
        _snapshot(
            _entity("Milestone", "M-A"),
            _entity("Objective", "O-B"),
            _entity("BacklogItem", "C", milestone_id="M-A", objective_id="O-B"),
        )
    )
    depths = plan.depths()
    assert depths["BacklogItem::C"] == 1
    assert depths["Milestone::M-A"] == 0
    assert depths["Objective::O-B"] == 0
