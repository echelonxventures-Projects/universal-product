"""UCOS-CTRL-STATE-000001 — Universal Project State (Wave 11) validation suite.

The suite the wave enters the coverage gate carrying. It exercises the six things the wave
was required to make true — automatic entity discovery, deterministic projection, durable
replay, governance participation, certification participation and dependency/ownership
analysis — and it exercises them the way the repository requires: against the real composed
control plane for the integration claims, and against small constructed snapshots for the
behavioural ones, so a failure names the behaviour rather than the substrate.

Two properties are asserted as *proofs* rather than comparisons. Determinism: two projections
of the same plane at the same tick produce the same snapshot identity, which can only hold if
no clock and no iteration order leaked into it. Replay: the journal reconstructs the snapshot
through the same projection rules that built it, so equal identity means the state was truly
recovered rather than copied.
"""

from __future__ import annotations

import json
from pathlib import Path
from platform.universal_control_plane import ControlPlane, ontology
from platform.universal_control_plane.certification import CertificationEngine
from platform.universal_control_plane.durable import DurableJournal
from platform.universal_control_plane.errors import StateTransitionError
from platform.universal_control_plane.governance import GovernanceEngine, GovernanceSubject
from platform.universal_control_plane.ontology import (
    LIFECYCLE_ACTIVE,
    LIFECYCLE_DRAFT,
    BacklogItem,
    Vision,
    dataclass,
)
from platform.universal_project_state import (
    DEPENDENCY_KEYS,
    EVENT_STATE_PROJECTED,
    ProjectStateEngine,
    ProjectStateError,
    ProjectStateRegistry,
    ProjectStateSnapshot,
    StateDelta,
    StateEntity,
    certification_subjects,
    discover_entity_kinds,
    entity_id_of,
    governance_subject,
    governance_subjects,
    plane_projections,
    reconstruct,
    reconstruct_all,
    reconstruct_at,
    record_snapshot,
    replays,
    snapshot_payload,
    state_entries,
    version_index,
)

import pytest

REPO = Path(__file__).resolve().parents[2]


# ---------------------------------------------------------------------------
# fixtures — small, constructed state; no repository scan
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


@pytest.fixture(scope="module")
def plane() -> ControlPlane:
    """The real composed control plane — the substrate project state is projected from."""
    return ControlPlane.discover()


@pytest.fixture(scope="module")
def projected(plane: ControlPlane) -> tuple[ProjectStateEngine, ProjectStateSnapshot]:
    """One real projection, journalled, shared by the integration assertions."""
    import tempfile

    engine = ProjectStateEngine(journal=DurableJournal.open(tempfile.mkdtemp()))
    return engine, engine.project(plane, tick=1)


# ---------------------------------------------------------------------------
# entity-kind discovery — the vocabulary is the existing ontology
# ---------------------------------------------------------------------------


def test_entity_kinds_are_discovered_from_the_ontology_and_not_enumerated():
    kinds = discover_entity_kinds()
    assert len(kinds) > 20, "the ontology defines far more value objects than this"
    assert kinds == tuple(sorted(kinds)), "discovery must be deterministically ordered"
    # The entity roles the wave was required to model resolve to discovered kinds.
    for required in ("Vision", "Goal", "Objective", "Milestone", "Capability", "Assignment"):
        assert required in kinds


def test_discovery_admits_value_objects_and_excludes_engines():
    kinds = discover_entity_kinds()
    assert "Vision" in kinds, "a frozen ontology value object is an entity kind"
    for engine_name in ("StateEngine", "PlanEngine", "GovernanceEngine", "ProjectStateEngine"):
        assert engine_name not in kinds, "a mutable engine is not a unit of project state"


def test_the_source_module_of_a_kind_is_where_it_is_declared():
    """A re-exported name must not be discovered twice under two paths."""
    from platform.universal_control_plane import state as lifecycle_module

    assert discover_entity_kinds(lifecycle_module) == ("Transition",)


# ---------------------------------------------------------------------------
# the state model
# ---------------------------------------------------------------------------


def test_an_entity_takes_its_own_identifier_and_not_a_foreign_key():
    """Positional reading is what keeps a foreign key from becoming the subject."""
    raw = {"kind": "Goal", "identity": "x", "goal_id": "GOAL-1", "universe_id": "U-1"}
    assert entity_id_of(raw) == "GOAL-1"
    # A sorted scan would have returned universe_id here; ordering is the whole point.
    assert sorted(k for k in raw if k.endswith("_id"))[0] == "goal_id"


def test_an_ownership_shaped_projection_is_not_keyed_on_its_capability():
    raw = {
        "kind": "OwnershipRecord",
        "identity": "x",
        "ownership_id": "OWN-1",
        "capability_id": "CAP-1",
    }
    assert entity_id_of(raw) == "OWN-1"


def test_a_projection_without_any_identifier_fails_closed():
    with pytest.raises(ProjectStateError, match="declares no identifier"):
        entity_id_of({"kind": "Goal", "title": "no id here"})


def test_a_projection_without_a_kind_fails_closed():
    with pytest.raises(ProjectStateError, match="declares no 'kind'"):
        StateEntity.from_projection({"goal_id": "GOAL-1"})


def test_entity_identity_is_content_addressed_and_ignores_the_tick():
    left = StateEntity.from_projection({"kind": "Goal", "goal_id": "G-1"}, tick=1)
    right = StateEntity.from_projection({"kind": "Goal", "goal_id": "G-1"}, tick=99)
    assert left.identity == right.identity, "a logical tick is not content"
    other = StateEntity.from_projection({"kind": "Goal", "goal_id": "G-2"}, tick=1)
    assert other.identity != left.identity


def test_lifecycle_and_owner_are_read_from_the_fields_the_ontology_publishes():
    entity = _entity("BacklogItem", "ITEM-1", state=LIFECYCLE_ACTIVE, owner="Terminal T5")
    assert entity.lifecycle == LIFECYCLE_ACTIVE
    assert entity.owner == "Terminal T5"
    assert entity.subject_id == "BacklogItem::ITEM-1"


def test_an_absent_lifecycle_is_reported_absent_rather_than_defaulted():
    assert _entity("Goal", "G-1").lifecycle == ""
    assert _entity("Goal", "G-1").owner == ""


def test_a_real_ontology_object_projects_through_its_own_to_dict():
    vision = Vision(vision_id="VIS-1", universe_id="U-1", statement="s")
    entity = StateEntity.from_projection(vision.to_dict(), tick=3)
    assert (entity.kind, entity.entity_id) == ("Vision", "VIS-1")
    item = BacklogItem(item_id="ITEM-9", universe_id="U-1", title="t")
    assert StateEntity.from_projection(item.to_dict()).entity_id == "ITEM-9"


def test_snapshot_identity_is_a_function_of_its_entities():
    one = _snapshot(_entity("Goal", "G-1"))
    same = _snapshot(_entity("Goal", "G-1"))
    other = _snapshot(_entity("Goal", "G-1"), _entity("Goal", "G-2"))
    assert one.snapshot_id == same.snapshot_id == one.identity
    assert other.snapshot_id != one.snapshot_id


def test_snapshot_queries_count_project_and_fail_closed():
    snapshot = _snapshot(
        _entity("Goal", "G-1", owner="T1"), _entity("Goal", "G-2"), _entity("Milestone", "M-1")
    )
    assert snapshot.counts() == {"Goal": 2, "Milestone": 1}
    assert snapshot.kinds() == ("Goal", "Milestone")
    assert len(snapshot.of_kind("Goal")) == 2
    assert snapshot.coverage() == round(1 / 3, 4)
    assert snapshot.entity("Goal::G-1").owner == "T1"
    assert snapshot.digest()
    assert snapshot.to_dict()["total"] == 3
    with pytest.raises(ProjectStateError, match="no such state entity"):
        snapshot.entity("Goal::ABSENT")


def test_an_empty_snapshot_reports_zero_coverage_rather_than_dividing_by_zero():
    assert _snapshot().coverage() == 0.0


def test_a_delta_measures_what_changed_between_two_snapshots():
    before = _snapshot(_entity("Goal", "G-1"), _entity("Goal", "G-2", state=LIFECYCLE_DRAFT))
    after = _snapshot(_entity("Goal", "G-2", state=LIFECYCLE_ACTIVE), _entity("Goal", "G-3"))
    delta = StateDelta.between(before, after)
    assert delta.added == ("Goal::G-3",)
    assert delta.removed == ("Goal::G-1",)
    assert delta.changed == ("Goal::G-2",)
    assert not delta.empty
    assert delta.counts() == {"added": 1, "removed": 1, "changed": 1}
    assert delta.to_dict()["empty"] is False
    assert StateDelta.between(before, before).empty


# ---------------------------------------------------------------------------
# the canonical registry
# ---------------------------------------------------------------------------


def test_the_registry_holds_each_subject_once_and_records_replacement():
    registry = ProjectStateRegistry()
    registry.register(_entity("Goal", "G-1", state=LIFECYCLE_DRAFT))
    registry.register(_entity("Goal", "G-1", state=LIFECYCLE_DRAFT))
    assert registry.count() == 1
    assert registry.replacements() == {}, "re-registering identical content is not a change"
    registry.register(_entity("Goal", "G-1", state=LIFECYCLE_ACTIVE))
    assert registry.count() == 1
    assert registry.replacements() == {"Goal::G-1": 1}


def test_the_registry_rejects_an_entity_without_an_identifier():
    registry = ProjectStateRegistry()
    with pytest.raises(ProjectStateError, match="non-empty entity_id"):
        registry.register(StateEntity(kind="Goal", entity_id="  "))


def test_registry_ownership_analysis_reports_owners_and_the_gap():
    registry = ProjectStateRegistry()
    registry.register_all(
        [
            _entity("Goal", "G-1", owner="T1"),
            _entity("Goal", "G-2"),
            _entity("Goal", "G-3", owner="T1"),
        ]
    )
    assert registry.owners() == ("T1",)
    assert len(registry.owned_by("T1")) == 2
    assert [e.entity_id for e in registry.unowned()] == ["G-2"]
    assert registry.coverage() == round(2 / 3, 4)


def test_registry_dependency_analysis_reads_declared_edges_only():
    registry = ProjectStateRegistry()
    registry.register_all(
        [
            _entity("Goal", "G-1", dependencies=["G-2", "ABSENT", "G-2"]),
            _entity("Goal", "G-2"),
        ]
    )
    assert registry.dependencies_of("Goal::G-1") == ("G-2", "ABSENT")
    assert registry.dependents_of("G-2") == ("Goal::G-1",)
    assert registry.unresolved_dependencies() == (("Goal::G-1", "ABSENT"),)
    assert DEPENDENCY_KEYS == ("dependencies",)


def test_registry_queries_fail_closed_and_project():
    registry = ProjectStateRegistry()
    registry.register(_entity("Goal", "G-1", owner="T1"))
    assert registry.subjects() == ("Goal::G-1",)
    assert registry.kinds() == ("Goal",)
    assert registry.by_kind() == {"Goal": 1}
    assert registry.entities()[0].entity_id == "G-1"
    assert registry.to_dict()["engine"] == "ProjectStateRegistry"
    assert registry.counts()["entities"] == 1
    with pytest.raises(ProjectStateError, match="no such state entity"):
        registry.entity("Goal::ABSENT")


def test_an_empty_registry_reports_zero_coverage():
    assert ProjectStateRegistry().coverage() == 0.0


# ---------------------------------------------------------------------------
# projection from the real plane
# ---------------------------------------------------------------------------


def test_plane_projections_are_read_from_declared_fields_not_a_named_list(plane: ControlPlane):
    projections = plane_projections(plane)
    assert len(projections) > 10
    engines = {str(p.get("engine")) for p in projections if p.get("engine")}
    assert {"PlanEngine", "RoadmapEngine", "BacklogEngine"} <= engines


def test_projection_requires_a_composed_plane():
    with pytest.raises(ProjectStateError, match="requires a composed control plane"):
        plane_projections(object())


def test_the_real_plane_projects_the_planning_entities_the_wave_requires(
    projected: tuple[ProjectStateEngine, ProjectStateSnapshot],
):
    _, snapshot = projected
    counts = snapshot.counts()
    for kind in ("Vision", "Goal", "Objective", "Milestone", "BacklogItem"):
        assert counts.get(kind, 0) > 0, f"{kind} did not reach project state"
    assert snapshot.universe_id == "UCOS-CTRL-000001"
    assert snapshot.truth_id, "state must be anchored to the Truth it was taken over"


def test_projection_is_deterministic_over_the_same_plane(plane: ControlPlane):
    """Two projections at one tick agree — no clock and no iteration order leaked in."""
    first = ProjectStateEngine().project(plane, tick=7)
    second = ProjectStateEngine().project(plane, tick=7)
    assert first.snapshot_id == second.snapshot_id
    assert first.counts() == second.counts()


def test_the_same_object_reached_twice_is_one_entity(
    projected: tuple[ProjectStateEngine, ProjectStateSnapshot],
):
    _, snapshot = projected
    subjects = [e.subject_id for e in snapshot.entities]
    assert len(subjects) == len(set(subjects))


def test_the_engine_reports_kinds_it_supports_beyond_those_populated(
    projected: tuple[ProjectStateEngine, ProjectStateSnapshot],
):
    """An unpopulated kind is a measured absence, not a missing capability."""
    engine, snapshot = projected
    assert len(engine.entity_kinds()) > len(snapshot.kinds())
    assert set(snapshot.kinds()) <= set(engine.entity_kinds())


def test_the_engine_projects_itself(projected: tuple[ProjectStateEngine, ProjectStateSnapshot]):
    engine, _ = projected
    payload = engine.to_dict()
    assert payload["engine"] == "ProjectStateEngine"
    assert payload["counts"]["entities"] > 0
    assert payload["replayable"] is True
    assert json.dumps(payload, default=str)


def test_state_before_projection_fails_closed():
    engine = ProjectStateEngine()
    with pytest.raises(ProjectStateError, match="no project state has been projected"):
        engine.snapshot()
    assert engine.delta().empty
    assert engine.replayable() is False


def test_a_second_projection_yields_a_measurable_delta(plane: ControlPlane):
    engine = ProjectStateEngine()
    engine.project(plane, tick=1)
    engine.project(plane, tick=2)
    assert len(engine.snapshots()) == 2
    assert engine.delta().empty, "an unchanged plane must produce an empty delta"


def test_an_unreadable_truth_substrate_fails_closed():
    class Broken:
        def truth(self) -> object:
            raise RuntimeError("substrate gone")

    @dataclass
    class FakePlane:
        truth: Broken

    with pytest.raises(ProjectStateError, match="repository truth is unreadable"):
        ProjectStateEngine().project(FakePlane(truth=Broken()))


def test_a_plane_without_a_truth_engine_records_an_empty_truth_id():
    @dataclass
    class BarePlane:
        note: str = "no engines here"

    assert ProjectStateEngine().project(BarePlane()).truth_id == ""


# ---------------------------------------------------------------------------
# lifecycle transitions — through the plane's existing state machine
# ---------------------------------------------------------------------------


def test_a_transition_runs_through_the_existing_lifecycle_state_machine():
    engine = ProjectStateEngine()
    engine.registry.register(_entity("BacklogItem", "ITEM-1", state=LIFECYCLE_DRAFT))
    engine._lifecycles["BacklogItem::ITEM-1"] = LIFECYCLE_DRAFT
    assert engine.transition("BacklogItem::ITEM-1", "ACTIVATE") == LIFECYCLE_ACTIVE
    assert engine.lifecycle_of("BacklogItem::ITEM-1") == LIFECYCLE_ACTIVE
    with pytest.raises(StateTransitionError):
        engine.transition("BacklogItem::ITEM-1", "ACTIVATE")


def test_an_entity_with_no_lifecycle_cannot_be_advanced():
    engine = ProjectStateEngine()
    engine.registry.register(_entity("Goal", "G-1"))
    assert engine.lifecycle_of("Goal::G-1") == ""
    with pytest.raises(ProjectStateError, match="declares no lifecycle state"):
        engine.transition("Goal::G-1", "ACTIVATE")


# ---------------------------------------------------------------------------
# replay — through the control plane's own durable journal
# ---------------------------------------------------------------------------


def test_the_journal_replays_the_snapshot_exactly(tmp_path: Path):
    journal = DurableJournal.open(tmp_path)
    snapshot = _snapshot(_entity("Goal", "G-1", owner="T1"), _entity("Milestone", "M-1"))
    entry = record_snapshot(journal, snapshot, tick=1)
    assert entry.event == EVENT_STATE_PROJECTED
    assert journal.verify()
    replayed = reconstruct(journal)
    assert replayed.snapshot_id == snapshot.snapshot_id
    assert replayed.counts() == snapshot.counts()
    assert replays(journal, snapshot)


def test_replay_survives_a_reopened_journal(tmp_path: Path):
    """State recovered from disk, not from the memory of the process that wrote it."""
    snapshot = _snapshot(_entity("Goal", "G-1"))
    record_snapshot(DurableJournal.open(tmp_path), snapshot, tick=1)
    reopened = DurableJournal.open(tmp_path)
    assert reopened.verify()
    assert reconstruct(reopened).snapshot_id == snapshot.snapshot_id


def test_history_is_reconstructable_at_any_recorded_point(tmp_path: Path):
    journal = DurableJournal.open(tmp_path)
    first = _snapshot(_entity("Goal", "G-1"))
    second = _snapshot(_entity("Goal", "G-1"), _entity("Goal", "G-2"))
    entry_one = record_snapshot(journal, first, tick=1)
    record_snapshot(journal, second, tick=2)
    assert len(state_entries(journal)) == 2
    history = reconstruct_all(journal)
    assert [len(s.entities) for s in history] == [1, 2]
    assert reconstruct_at(journal, entry_one.sequence).snapshot_id == first.snapshot_id
    assert reconstruct(journal).snapshot_id == second.snapshot_id


def test_replay_of_an_absent_or_unknown_entry_fails_closed(tmp_path: Path):
    journal = DurableJournal.open(tmp_path)
    with pytest.raises(ProjectStateError, match="holds no STATE_PROJECTED entry to replay"):
        reconstruct(journal)
    assert replays(journal, _snapshot()) is False
    record_snapshot(journal, _snapshot(_entity("Goal", "G-1")), tick=1)
    with pytest.raises(ProjectStateError, match="at 99"):
        reconstruct_at(journal, 99)


def test_a_malformed_payload_is_refused_rather_than_partially_replayed():
    from platform.universal_project_state.state_replay import snapshot_from_payload

    with pytest.raises(ProjectStateError, match="carries no entities array"):
        snapshot_from_payload({"universe_id": "U", "truth_id": "T"})
    with pytest.raises(ProjectStateError, match="is not an object"):
        snapshot_from_payload({"entities": ["not an object"]})


def test_the_payload_carries_the_original_projection_not_a_second_encoding():
    snapshot = _snapshot(_entity("Goal", "G-1", owner="T1"))
    payload = snapshot_payload(snapshot)
    assert payload["entities"][0]["kind"] == "Goal"
    assert payload["entities"][0]["goal_id"] == "G-1"


def test_the_engine_journals_every_projection_it_makes(plane: ControlPlane, tmp_path: Path):
    engine = ProjectStateEngine(journal=DurableJournal.open(tmp_path))
    snapshot = engine.project(plane, tick=1)
    assert engine.replayable()
    assert reconstruct(engine.journal).snapshot_id == snapshot.snapshot_id


# ---------------------------------------------------------------------------
# governance — an adapter onto the declared rule set, not a second rule set
# ---------------------------------------------------------------------------


def test_a_state_entity_projects_into_the_declared_governance_subject_shape():
    registry = ProjectStateRegistry()
    entity = _entity(
        "BacklogItem",
        "ITEM-1",
        owner="Terminal T5",
        version="1.0.0",
        locator="platform/x",
        evidence_ids=["EV-1"],
        state=LIFECYCLE_ACTIVE,
    )
    registry.register(entity)
    subject = governance_subject(entity, registry=registry)
    assert isinstance(subject, GovernanceSubject)
    assert subject.subject_id == "BacklogItem::ITEM-1"
    assert (subject.owner, subject.version) == ("Terminal T5", "1.0.0")
    assert subject.registered is True
    assert subject.canonical_home is True
    assert subject.evidence_ids == ("EV-1",)
    assert subject.lifecycle_state == LIFECYCLE_ACTIVE


def test_absent_governance_facts_are_reported_absent_rather_than_supplied():
    subject = governance_subject(_entity("Goal", "G-1"))
    assert subject.owner == ""
    assert subject.registered is False, "an unregistered entity must not claim registration"
    assert subject.canonical_home is False
    assert subject.evidence_ids == ()
    assert subject.lifecycle_state == LIFECYCLE_DRAFT


def test_traceability_serves_as_evidence_when_evidence_ids_is_absent():
    subject = governance_subject(_entity("Goal", "G-1", traceability=["T-1", "T-2"]))
    assert subject.evidence_ids == ("T-1", "T-2")


def test_governance_subjects_are_deterministically_ordered():
    subjects = governance_subjects([_entity("Goal", "G-2"), _entity("Goal", "G-1")])
    assert [s.subject_id for s in subjects] == ["Goal::G-1", "Goal::G-2"]


def test_the_declared_rule_set_adjudicates_project_state_with_no_state_rules():
    """The verdict comes from the manifest's rules; this wave contributes no rule of its own."""
    engine = ProjectStateEngine()
    engine._snapshots.append(
        _snapshot(
            _entity(
                "BacklogItem",
                "ITEM-1",
                owner="T5",
                version="1.0.0",
                locator="platform/x",
                evidence_ids=["EV-1"],
                state=LIFECYCLE_ACTIVE,
            ),
            _entity("Goal", "G-1"),
        )
    )
    engine.registry.register_snapshot(engine.snapshot())
    records = engine.govern(GovernanceEngine(), tick=1)
    by_subject = {r.subject_id: r for r in records}
    assert by_subject["BacklogItem::ITEM-1"].governed is True
    assert by_subject["BacklogItem::ITEM-1"].violation_ids == ()
    unowned = by_subject["Goal::G-1"]
    assert unowned.governed is False
    assert any("GOV-OWNED" in v for v in unowned.violation_ids)


# ---------------------------------------------------------------------------
# certification — an adapter onto the declared criteria
# ---------------------------------------------------------------------------


def test_certification_reuses_the_governance_adjudication_rather_than_recounting_it():
    registry = ProjectStateRegistry()
    entity = _entity(
        "BacklogItem",
        "ITEM-1",
        owner="T5",
        version="1.0.0",
        locator="platform/x",
        evidence_ids=["EV-1"],
    )
    registry.register(entity)
    record = GovernanceEngine().resolve(governance_subject(entity, registry=registry), tick=1)
    subjects = certification_subjects([record], versions={"BacklogItem::ITEM-1": "1.0.0"})
    assert len(subjects) == 1
    assert subjects[0].governed is True
    assert subjects[0].critical_violations == 0
    assert subjects[0].version == "1.0.0"
    assert subjects[0].kind == "BacklogItem"


def test_versions_are_read_from_the_entities_themselves():
    entities = [_entity("Goal", "G-1", version="2.1.0"), _entity("Goal", "G-2")]
    assert version_index(entities) == {"Goal::G-1": "2.1.0"}


def test_project_state_is_certified_through_the_declared_criteria():
    engine = ProjectStateEngine()
    engine._snapshots.append(
        _snapshot(
            _entity(
                "BacklogItem",
                "ITEM-1",
                owner="T5",
                version="1.0.0",
                locator="platform/x",
                evidence_ids=["EV-1"],
                state=LIFECYCLE_ACTIVE,
            )
        )
    )
    engine.registry.register_snapshot(engine.snapshot())
    records = engine.govern(GovernanceEngine(), tick=1)
    states = engine.certify(CertificationEngine(), records, tick=1)
    assert states, "a governed, evidenced, versioned subject must be certifiable"
    assert states[0].subject_id == "BacklogItem::ITEM-1"
    assert states[0].criteria


def test_an_ineligible_subject_is_not_certified_rather_than_failed():
    engine = ProjectStateEngine()
    engine._snapshots.append(_snapshot(_entity("Goal", "G-1")))
    engine.registry.register_snapshot(engine.snapshot())
    records = engine.govern(GovernanceEngine(), tick=1)
    assert engine.certify(CertificationEngine(), records, tick=1) == ()


# ---------------------------------------------------------------------------
# repository truth — the wave's own registration in the repository
# ---------------------------------------------------------------------------


def test_the_package_is_in_the_coverage_denominator_it_claims():
    """A capability that is not measured cannot claim to be verified.

    ASKED OF THE DERIVATION, not of ``pyproject.toml``. This test used to grep the file for the
    literal ``"--cov=platform.universal_project_state",`` and a matching ``source`` path — two
    searches against two hand-written lists. UCOS-OMEGA-001 removed both lists: the denominator is
    derived from ``git ls-files '*.py'``, so the honest question is whether the derivation contains
    this package, and the answer no longer depends on how a TOML file happens to be formatted.
    """
    from engine.universal_discovery.discovery import derived_scope

    _test_roots, packages, _exemptions, _transient = derived_scope(str(REPO))
    assert "platform.universal_project_state" in packages, (
        "the package is outside the derived coverage denominator, so its coverage figure is a "
        f"number about something else: {sorted(packages)[:5]}…"
    )


def test_every_declared_wave_module_exists_and_is_importable():
    package = REPO / "platform" / "universal_project_state"
    for module in (
        "state.py",
        "state_registry.py",
        "state_runtime.py",
        "state_replay.py",
        "state_governance.py",
        "state_certification.py",
    ):
        assert (package / module).is_file(), f"{module} is a declared deliverable of Wave 11"


def test_the_package_declares_no_second_governance_or_certification_engine():
    """The wave is a consumer of constitutional services; it must not fork them."""
    package = REPO / "platform" / "universal_project_state"
    sources = "\n".join(p.read_text(encoding="utf-8") for p in sorted(package.glob("*.py")))
    for forbidden in (
        "class StateGovernanceEngine",
        "class StateCertificationEngine",
        "class StateRuleEngine",
        "class StateSeverityModel",
        "class StatePolicyFramework",
    ):
        assert forbidden not in sources, f"{forbidden} would be a parallel authority"


def test_no_wall_clock_reaches_project_state():
    """Determinism is structural: the modules cannot read a clock."""
    package = REPO / "platform" / "universal_project_state"
    for path in sorted(package.glob("*.py")):
        source = path.read_text(encoding="utf-8")
        for forbidden in ("import time", "datetime", "utcnow", "import random", "uuid"):
            assert forbidden not in source, f"{path.name} reaches for {forbidden}"


# ---------------------------------------------------------------------------
# the arms a well-formed control plane never takes
# ---------------------------------------------------------------------------


def test_a_re_exported_name_is_discovered_only_where_it_is_declared():
    """A NAME DISCOVERED TWICE UNDER TWO PATHS IS ONE ENTITY KIND COUNTED TWICE.

    The module check is what enforces that, and its SKIP had never run: the two modules
    discovery is pointed at here happen to declare everything they expose. A control-plane
    package re-exports its ontology, so pointing discovery at the package rather than at the
    module it is declared in is the ordinary way to hit this — and without the skip the same
    frozen dataclass would enter the kind vocabulary under both paths.
    """
    from platform.universal_control_plane import state as lifecycle_module

    assert "Transition" in dir(lifecycle_module)
    assert discover_entity_kinds(lifecycle_module) == ("Transition",)

    # `ontology` re-exports nothing it does not declare, so every discovered kind is its own.
    for kind in discover_entity_kinds(ontology):
        assert getattr(ontology, kind).__module__ == ontology.__name__

    # A module that exposes a dataclass declared elsewhere discovers none of it.
    assert discover_entity_kinds(pytest) == ()


def test_a_projection_keyed_only_on_identity_is_read_from_identity():
    """IDENTITY IS THE FALLBACK, AND IT HAD NO CASE.

    Every ontology ``to_dict`` emits a ``*_id`` key, so the positional scan always answers
    and the fallback below it was dead. It is what keeps the reader total over a projection
    that carries a content identity and no domain identifier — a shape a hand-built or
    rehydrated record takes — and without it such a record would be refused as identifierless
    while plainly carrying an identity.
    """
    assert entity_id_of({"kind": "Goal", "identity": "UCOS-CP-abc123"}) == "UCOS-CP-abc123"
    with pytest.raises(ProjectStateError, match="declares no identifier"):
        entity_id_of({"kind": "Goal", "identity": "   "})


def test_an_entity_resolves_a_declared_fact_and_renders_itself():
    """THE OPEN FACT BAG IS THE POINT OF THE MODEL, AND NOTHING HAD READ FROM IT.

    An entity carries whatever its ontology projection declared, so the resolver is how a
    consumer asks about a field this package does not enumerate — the mechanism that lets a
    new ontology field be queried without a change here. The render beside it is how an
    entity leaves the process, and it names the entity kind under a distinct key so a
    rendered entity cannot be mistaken for the projection it was built from.
    """
    entity = StateEntity.from_projection(
        {"kind": "Goal", "goal_id": "GOAL-1", "title": "a goal", "lifecycle": "ACTIVE"}
    )

    assert entity.fact("title") == "a goal"
    assert entity.fact("a-field-no-ontology-declares") is None

    rendered = entity.to_dict()
    assert rendered["kind"] == "StateEntity"
    assert rendered["entity_kind"] == "Goal"
    assert rendered["entity_id"] == "GOAL-1"


def test_the_registry_selects_the_entities_of_one_kind():
    """A REGISTRY THAT CAN ONLY BE READ WHOLE IS A REGISTRY NOBODY CAN QUERY.

    The kind vocabulary is read and the whole population is read, so the selector between
    them had no caller — and it is what every per-kind report is built from. Selecting on the
    entity's declared kind rather than filtering the projection again is what keeps the
    answer consistent with the vocabulary the registry publishes.
    """
    registry = ProjectStateRegistry()
    registry.register(StateEntity.from_projection({"kind": "Goal", "goal_id": "GOAL-1"}))
    registry.register(StateEntity.from_projection({"kind": "Goal", "goal_id": "GOAL-2"}))
    registry.register(StateEntity.from_projection({"kind": "Vision", "vision_id": "VIS-1"}))

    assert [e.entity_id for e in registry.of_kind("Goal")] == ["GOAL-1", "GOAL-2"]
    assert [e.entity_id for e in registry.of_kind("Vision")] == ["VIS-1"]
    assert registry.of_kind("a-kind-nothing-registered") == ()


def test_a_projection_nested_past_the_declared_depth_is_not_walked_forever():
    """THE BOUND EXISTS SO A SELF-REFERENTIAL PROJECTION CANNOT MAKE HARVESTING ENDLESS.

    A control-plane projection nests a plan three levels deep, so the bound is never
    approached and the arm enforcing it had never run. A projection that contains itself —
    a rehydrated document with a cycle, or a plane whose engine renders its own parent — is
    what it exists for: without it the walk does not terminate, and with it the harvest is
    finite and the entities above the bound are still found.
    """
    from platform.universal_project_state.state_runtime import MAX_PROJECTION_DEPTH, _harvest

    node: dict = {"kind": "Goal", "goal_id": "GOAL-DEEP"}
    for _ in range(MAX_PROJECTION_DEPTH + 4):
        node = {"nested": node}

    found = _harvest(node, frozenset({"Goal"}))

    assert found == [], "everything below the bound is left unwalked rather than looped over"
    assert _harvest({"nested": {"kind": "Goal", "goal_id": "G"}}, frozenset({"Goal"})) != []


def test_a_plane_field_projecting_something_that_is_not_a_mapping_is_skipped():
    """A ``to_dict`` THAT DOES NOT RETURN A DOCUMENT PROJECTS NOTHING.

    Every engine on the composed plane renders a mapping, so the guard had no case. A field
    that publishes a callable ``to_dict`` returning a list or a string is not a projection
    this harvester can read, and appending it would put a non-document into a sequence every
    consumer iterates as mappings.
    """

    @dataclass
    class _Plane:
        good: object
        odd: object
        absent: object = None

    class _Good:
        @staticmethod
        def to_dict() -> dict:
            return {"kind": "Goal", "goal_id": "GOAL-1"}

    class _Odd:
        @staticmethod
        def to_dict() -> list:
            return ["not a document"]

    projections = plane_projections(_Plane(_Good(), _Odd()))

    assert projections == ({"kind": "Goal", "goal_id": "GOAL-1"},)


def test_a_journal_whose_chain_is_broken_does_not_replay(tmp_path: Path):
    """REPLAY IS TWO CLAIMS AND ONLY THE SECOND HAD A CASE.

    A snapshot that reconstructs to a different identity was tested. The first claim — that
    the journal's own chain is intact — had not been falsified, and it is the one that
    matters more: a tampered journal can be made to reconstruct anything, so checking the
    reconstruction without checking the chain would let a rewritten history "replay"
    perfectly.
    """
    journal = DurableJournal.open(tmp_path)
    snapshot = _snapshot(_entity("Goal", "G-1", owner="T1"))
    record_snapshot(journal, snapshot, tick=1)
    assert replays(journal, snapshot) is True

    class _Broken:
        @staticmethod
        def verify() -> bool:
            return False

        def __getattr__(self, name: str):
            return getattr(journal, name)

    assert replays(_Broken(), snapshot) is False


def test_governance_evidence_accepts_a_sequence_as_well_as_a_string() -> None:
    """A control-plane projection carries evidence as a list; a bare string is the other arm.

    The resolver returns the first non-empty shape it finds for each declared key, and both
    shapes are real: the string arrives from a hand-built record, the sequence from an
    entity whose ontology renders a list.
    """
    from platform.universal_project_state.state_governance import _evidence

    assert _evidence({"evidence_ids": ["E-1", " E-2 ", ""]}) == ("E-1", "E-2")
    assert _evidence({"traceability": " T-1 "}) == ("T-1",)
    assert _evidence({}) == ()


def test_an_empty_evidence_sequence_falls_through_to_the_next_key() -> None:
    """A list of blanks is not evidence; the resolver must keep looking and find nothing.

    The ``found`` arm of the sequence branch had never met an all-blank list — the shape a
    projection carries when the ontology declares the field and the subject has nothing to
    cite. Refusing to treat it as evidence is the point.
    """
    from platform.universal_project_state.state_governance import _evidence

    assert _evidence({"evidence_ids": ["", "  "], "traceability": "T-9"}) == ("T-9",)
    assert _evidence({"evidence_ids": [], "traceability": ()}) == ()
