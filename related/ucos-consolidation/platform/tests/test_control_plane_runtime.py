"""UCOS-CTRL-000001 — Registration, Linkage, Consumption, Durable Replay, Gate.

Waves 6 to 10 together. The through-line is that each of these is a
*measurement*, not an assertion: registration is discovered by introspecting the
package rather than read from a list, linkage is a set of resolvable identities
rather than a set of booleans, consumption is counted invocations rather than
available imports, and replay is a chain that either reconstructs or fails.
"""

from __future__ import annotations

import json
from platform.tests.control_plane_helpers import build_substrate, discover_plane
from platform.universal_control_plane.consumption import (
    DEFAULT_CONSUMERS,
    OUTCOME_FAILED,
    OUTCOME_SERVED,
    Consumer,
    ConsumptionEngine,
    ConsumptionRecord,
    default_consumers,
)
from platform.universal_control_plane.discovery import (
    DEMO_MARKERS,
    REQUIRED_ENGINES,
    CompletionReport,
    ControlPlane,
    GateCriterion,
    demo_markers_present,
)
from platform.universal_control_plane.durable import (
    EVENT_CERTIFIED,
    EVENT_GOVERNED,
    EVENT_REGISTERED,
    EVENT_TRUTH_DISCOVERED,
    GENESIS_HASH,
    DurableJournal,
    ReplayedState,
)
from platform.universal_control_plane.errors import (
    ControlPlaneError,
    JournalError,
    LinkageError,
    ObjectNotFoundError,
    RegistrationError,
)
from platform.universal_control_plane.linkage import LinkageEngine
from platform.universal_control_plane.manifest import default_manifest
from platform.universal_control_plane.ontology import (
    AgentRecord,
    BacklogItem,
    DependencyRecord,
    JournalEntry,
    payload_digest,
)
from platform.universal_control_plane.registration import (
    CONTROL_PLANE_PACKAGE,
    EXCLUDED_MODULES,
    EngineDescriptor,
    RegistrationEngine,
    discover_engines,
)

import pytest


@pytest.fixture(scope="module")
def plane(tmp_path_factory):
    root = tmp_path_factory.mktemp("runtime-plane")
    composed = discover_plane(root)
    composed.consume()
    return composed


# ---------------------------------------------------------------------------
# Registration (Wave 8)
# ---------------------------------------------------------------------------


class TestEngineDiscovery:
    def test_every_required_engine_is_discovered_by_introspection(self):
        """The required set is measured against what the package actually
        defines. Nothing declares this list to discovery — deleting an engine
        would fail here rather than leaving a stale registration behind."""
        names = {d.name for d in discover_engines()}
        assert set(REQUIRED_ENGINES) <= names

    def test_every_discovered_engine_is_assigned_a_declared_layer(self):
        assert all(d.layer != "UNCLASSIFIED" for d in discover_engines())

    def test_the_cli_module_is_excluded_from_discovery(self):
        assert "cli" in EXCLUDED_MODULES
        assert all(not d.module.endswith(".cli") for d in discover_engines())

    def test_a_class_is_attributed_to_the_module_that_defines_it(self):
        """Re-exports must not register the same engine twice. Every descriptor's
        module is the one the class was defined in, not one that imported it."""
        descriptors = discover_engines()
        assert len({d.subject_id for d in descriptors}) == len(descriptors)
        plan_engines = [d for d in descriptors if d.name == "PlanEngine"]
        assert len(plan_engines) == 1
        assert plan_engines[0].module.endswith(".plan")

    def test_discovery_is_deterministic_and_ordered(self):
        first = [d.subject_id for d in discover_engines()]
        assert first == sorted(first)
        assert first == [d.subject_id for d in discover_engines()]

    def test_engines_carry_their_own_docline_as_a_description(self):
        descriptor = next(d for d in discover_engines() if d.name == "VersionEngine")
        assert descriptor.description
        assert descriptor.to_dict()["subject_id"] == descriptor.subject_id

    def test_the_package_under_discovery_is_resolved_from_this_module(self):
        assert CONTROL_PLANE_PACKAGE == "platform.universal_control_plane"


class TestRegistration:
    def test_registering_populates_all_three_registries(self):
        engine = RegistrationEngine()
        records = engine.register_all()
        assert len(records) == engine.count()
        assert engine.capability_registry.count() == engine.count()
        assert engine.ownership_registry.count() == engine.count()
        assert engine.dependency_registry.count() > 0

    def test_the_declared_layer_graph_is_acyclic(self):
        engine = RegistrationEngine()
        engine.register_all()
        assert engine.dependency_registry.has_cycle() is False

    def test_dependency_edges_follow_the_declared_layer_graph(self):
        engine = RegistrationEngine()
        engine.register_all()
        taxonomy = engine.manifest.engine_taxonomy
        for edge in engine.dependency_registry.all():
            assert edge.attributes["to_layer"] in taxonomy.dependencies_of(
                edge.attributes["from_layer"]
            )

    def test_lineage_is_the_containment_chain(self):
        engine = RegistrationEngine()
        engine.register_all()
        record = engine.registration_of("platform.universal_control_plane.plan.PlanEngine")
        assert record.lineage == (
            "UCOS-CTRL-000001",
            "UCOS-CTRL-000001::PLANNING",
            "UCOS-CTRL-000001::PLANNING::platform.universal_control_plane.plan",
        )
        assert engine.lineage_of(record.subject_id) == record.lineage

    def test_ownership_binds_every_engine_to_the_universe(self):
        engine = RegistrationEngine()
        engine.register_all()
        owners = {r.owner_id for r in engine.registrations()}
        assert owners == {default_manifest().universe_id}

    def test_registering_the_same_engine_twice_is_refused(self):
        engine = RegistrationEngine()
        descriptor = EngineDescriptor(name="XEngine", module="m", layer="PLANNING")
        engine.register(descriptor)
        with pytest.raises(RegistrationError, match="already registered"):
            engine.register(descriptor)

    def test_an_unregistered_engine_is_an_absence(self):
        engine = RegistrationEngine()
        assert engine.is_registered("PlanEngine") is False
        with pytest.raises(ObjectNotFoundError, match="engine not registered"):
            engine.registration_of("nope")

    def test_registration_can_be_driven_from_supplied_descriptors(self):
        engine = RegistrationEngine()
        engine.register_all(
            [
                EngineDescriptor(name="AEngine", module="m.a", layer="REPOSITORY-TRUTH"),
                EngineDescriptor(name="BEngine", module="m.b", layer="REGISTRATION"),
            ]
        )
        assert engine.names() == ("AEngine", "BEngine")
        assert engine.layers() == ("REGISTRATION", "REPOSITORY-TRUTH")
        assert len(engine.by_layer("REGISTRATION")) == 1
        assert engine.dependency_registry.count() == 1

    def test_a_module_the_manifest_never_placed_is_reported_unclassified(self):
        engine = RegistrationEngine()
        engine.register_all(
            [EngineDescriptor(name="XEngine", module="m.invented", layer="UNCLASSIFIED")]
        )
        assert [r.name for r in engine.unclassified()] == ["XEngine"]

    def test_an_engine_never_depends_on_itself(self):
        engine = RegistrationEngine()
        engine.register_all(
            [
                EngineDescriptor(name="AEngine", module="m.a", layer="REGISTRATION"),
                EngineDescriptor(name="BEngine", module="m.b", layer="REGISTRATION"),
            ]
        )
        assert all(e.from_id != e.to_id for e in engine.dependency_registry.all())

    def test_the_projection_reports_counts_layers_and_records(self):
        engine = RegistrationEngine()
        engine.register_all()
        projection = engine.to_dict()
        assert projection["engine"] == "RegistrationEngine"
        assert projection["counts"]["registered"] == engine.count()
        assert projection["counts"]["unclassified"] == 0
        assert len(projection["registrations"]) == engine.count()
        assert len(engine.descriptors()) == engine.count()


# ---------------------------------------------------------------------------
# Linkage (Wave 10)
# ---------------------------------------------------------------------------


def _complete_links() -> dict[str, str]:
    return {dimension: f"id-{dimension}" for dimension in default_manifest().linkage_dimensions}


class TestLinkage:
    def test_a_fully_linked_subject_closes(self):
        engine = LinkageEngine()
        record = engine.link("S", _complete_links())
        assert record.complete is True
        assert record.missing == ()
        assert engine.complete() is True
        assert engine.coverage() == 1.0

    def test_an_empty_dimension_is_an_orphan(self):
        engine = LinkageEngine()
        links = _complete_links()
        links["certification"] = ""
        record = engine.link("S", links)
        assert record.complete is False
        assert record.missing == ("certification",)
        assert [r.subject_id for r in engine.orphans()] == ["S"]
        assert engine.complete() is False

    def test_an_omitted_dimension_is_missing_not_ignored(self):
        engine = LinkageEngine()
        links = _complete_links()
        del links["replay"]
        assert engine.link("S", links).missing == ("replay",)

    def test_an_undeclared_dimension_fails_closed(self):
        """A linkage the constitution never asked for is not a bonus: it is a
        claim that something was measured against a rule that does not exist."""
        with pytest.raises(LinkageError, match="undeclared linkage dimension"):
            LinkageEngine().link("S", {**_complete_links(), "invented": "x"})

    def test_an_empty_subject_id_is_refused(self):
        with pytest.raises(LinkageError, match="non-empty subject_id"):
            LinkageEngine().link("  ", _complete_links())

    def test_nothing_measured_is_not_completeness(self):
        engine = LinkageEngine()
        assert engine.complete() is False
        assert engine.coverage() == 0.0
        assert engine.count() == 0

    def test_an_unlinked_subject_is_an_absence(self):
        with pytest.raises(ObjectNotFoundError, match="no linkage recorded"):
            LinkageEngine().record_of("S")

    def test_link_all_is_order_independent(self):
        engine = LinkageEngine()
        records = engine.link_all([("B", _complete_links()), ("A", _complete_links())])
        assert [r.subject_id for r in records] == ["A", "B"]

    def test_missing_linkages_are_attributed_to_their_dimension(self):
        engine = LinkageEngine()
        links = _complete_links()
        links["version"] = ""
        engine.link("A", links)
        engine.link("B", links)
        engine.link("C", _complete_links())
        assert engine.missing_by_dimension()["version"] == 2
        assert engine.missing_by_dimension()["governance"] == 0
        assert engine.coverage() == round(1 / 3, 4)

    def test_the_projection_reports_orphans_and_a_digest(self):
        engine = LinkageEngine()
        engine.link("S", _complete_links())
        projection = engine.to_dict()
        assert projection["engine"] == "LinkageEngine"
        assert projection["counts"]["orphans"] == 0
        assert len(projection["digest"]) == 64
        assert len(projection["dimensions"]) == 9


# ---------------------------------------------------------------------------
# Consumption (Wave 9)
# ---------------------------------------------------------------------------


class TestConsumption:
    def test_registration_alone_is_not_consumption(self):
        """The whole point of the measurement: six bound consumers that have
        never run must not read as six consumed services."""
        engine = ConsumptionEngine()
        engine.register_all(default_consumers())
        assert engine.operational() is False
        assert engine.coverage() == 0.0
        assert engine.invocation_count() == 0

    def test_invoking_a_consumer_records_what_it_consumed(self):
        engine = ConsumptionEngine()
        engine.register(Consumer("c", "svc", lambda _plane: {"a": 1, "b": 2}))
        record = engine.invoke("c", object())
        assert record.outcome == OUTCOME_SERVED
        assert record.served is True
        assert record.result_digest == payload_digest({"a": 1, "b": 2})
        assert "2 key(s)" in record.detail

    def test_a_failing_consumer_is_recorded_rather_than_raised(self):
        """One subsystem's integration breaking is a measurement about that
        subsystem; losing the other five results to it would destroy the
        measurement."""
        engine = ConsumptionEngine()
        engine.register(Consumer("ok", "svc", lambda _p: [1, 2, 3]))
        engine.register(Consumer("bad", "svc", _raise))
        records = engine.invoke_all(object())
        assert len(records) == 2
        assert {r.outcome for r in records} == {OUTCOME_SERVED, OUTCOME_FAILED}
        assert "RuntimeError: consumer exploded" in engine.failed()[0].detail
        assert engine.consumed_by() == ("ok",)
        assert engine.operational() is False

    @pytest.mark.parametrize(
        ("result", "expected"),
        [({"a": 1}, "1 key(s)"), ([1, 2], "2 item(s)"), ("text", "str")],
    )
    def test_results_are_summarised_deterministically(self, result, expected):
        engine = ConsumptionEngine()
        engine.register(Consumer("c", "svc", lambda _p: result))
        assert expected in engine.invoke("c", object()).detail

    def test_an_unregistered_consumer_is_an_absence(self):
        with pytest.raises(ObjectNotFoundError, match="consumer not registered"):
            ConsumptionEngine().invoke("nope", object())

    def test_an_empty_consumer_id_is_refused(self):
        with pytest.raises(ControlPlaneError, match="non-empty consumer_id"):
            ConsumptionEngine().register(Consumer("  ", "svc", lambda _p: None))

    def test_records_can_be_read_globally_or_per_consumer(self):
        engine = ConsumptionEngine()
        engine.register(Consumer("a", "svc", lambda _p: 1))
        engine.register(Consumer("b", "svc", lambda _p: 1))
        engine.invoke_all(object())
        assert len(engine.records()) == 2
        assert len(engine.records("a")) == 1
        assert [c.consumer_id for c in engine.consumers()] == ["a", "b"]

    def test_the_six_repository_domains_ship_bound(self):
        assert {c.consumer_id for c in default_consumers()} == set(DEFAULT_CONSUMERS)
        assert all(c.description and c.service for c in default_consumers())
        assert default_consumers()[0].to_dict()["consumer_id"] in DEFAULT_CONSUMERS

    def test_every_bound_domain_consumes_against_a_live_plane(self, plane):
        assert plane.consumption.operational() is True
        assert plane.consumption.coverage() == 1.0
        assert plane.consumption.failed() == ()

    def test_the_governance_domain_consumes_the_canonical_decision(self, plane):
        record = plane.consumption.records("governance")[0]
        assert record.served is True
        assert "decision_sha256" in record.detail or record.result_digest

    def test_a_record_projects_every_field(self):
        record = ConsumptionRecord("c", "s", OUTCOME_SERVED, "d", "detail", tick=2)
        assert record.to_dict() == {
            "consumer_id": "c",
            "service": "s",
            "outcome": OUTCOME_SERVED,
            "served": True,
            "result_digest": "d",
            "detail": "detail",
            "tick": 2,
        }

    def test_the_projection_reports_coverage_and_who_consumed(self, plane):
        projection = plane.consumption.to_dict()
        assert projection["engine"] == "ConsumptionEngine"
        assert projection["operational"] is True
        assert set(projection["consumed_by"]) == set(DEFAULT_CONSUMERS)


def _raise(_plane):
    raise RuntimeError("consumer exploded")


# ---------------------------------------------------------------------------
# Durable replay (Wave 7)
# ---------------------------------------------------------------------------


class TestDurableJournal:
    def test_the_first_entry_binds_to_genesis(self, tmp_path):
        journal = DurableJournal.open(tmp_path)
        entry = journal.append("S", "EVENT", {"k": "v"})
        assert entry.previous_hash == GENESIS_HASH
        assert entry.sequence == 1
        assert journal.head_hash == entry.entry_hash

    def test_each_entry_binds_to_the_one_before_it(self, tmp_path):
        journal = DurableJournal.open(tmp_path)
        first = journal.append("S", "E", {"n": 1})
        second = journal.append("S", "E", {"n": 2})
        assert second.previous_hash == first.entry_hash
        assert journal.verify() is True

    def test_a_journal_survives_the_process_that_wrote_it(self, tmp_path):
        """The property the old process-local replay never had: state written
        before a restart is still there afterwards."""
        writer = DurableJournal.open(tmp_path)
        writer.append("S", EVENT_TRUTH_DISCOVERED, {"truth_id": "t-1"})
        reader = DurableJournal.open(tmp_path)
        assert reader.count() == 1
        assert reader.verify() is True
        assert reader.reconstruct().truth_id == "t-1"

    def test_reopening_without_loading_starts_empty(self, tmp_path):
        DurableJournal.open(tmp_path).append("S", "E", {})
        assert DurableJournal.open(tmp_path, load=False).count() == 0

    def test_a_tampered_payload_fails_closed(self, tmp_path):
        journal = DurableJournal.open(tmp_path)
        journal.append("S", "E", {"n": 1})
        journal._entries[0] = JournalEntry(
            sequence=1,
            subject_id="S",
            event="E",
            payload_digest="wrong",
            previous_hash=GENESIS_HASH,
            payload={"n": 1},
        )
        with pytest.raises(JournalError, match="does not match its digest"):
            journal.verify()

    def test_a_broken_chain_link_fails_closed(self, tmp_path):
        journal = DurableJournal.open(tmp_path)
        journal.append("S", "E", {"n": 1})
        journal.append("S", "E", {"n": 2})
        journal._entries[1] = JournalEntry(
            sequence=2,
            subject_id="S",
            event="E",
            payload_digest=payload_digest({"n": 2}),
            previous_hash="f" * 64,
            payload={"n": 2},
        )
        with pytest.raises(JournalError, match="chain breaks at entry 2"):
            journal.verify()

    def test_a_broken_sequence_fails_closed(self, tmp_path):
        journal = DurableJournal.open(tmp_path)
        journal.append("S", "E", {})
        journal._entries[0] = JournalEntry(
            sequence=9,
            subject_id="S",
            event="E",
            payload_digest=payload_digest({}),
            previous_hash=GENESIS_HASH,
            payload={},
        )
        with pytest.raises(JournalError, match="sequence breaks at position 1"):
            journal.verify()

    def test_an_unreadable_line_fails_closed(self, tmp_path):
        journal = DurableJournal.open(tmp_path)
        journal.append("S", "E", {})
        journal.path.write_text("{not json}\n", encoding="utf-8")
        with pytest.raises(JournalError, match="not a readable journal entry"):
            DurableJournal.open(tmp_path)

    def test_blank_lines_are_tolerated(self, tmp_path):
        journal = DurableJournal.open(tmp_path)
        journal.append("S", "E", {})
        with journal.path.open("a", encoding="utf-8") as handle:
            handle.write("\n\n")
        assert DurableJournal.open(tmp_path).count() == 1

    def test_an_absent_journal_loads_as_empty(self, tmp_path):
        journal = DurableJournal(path=tmp_path / "absent.ndjson")
        assert journal.load() == ()
        assert journal.verify() is True

    def test_an_unwritable_path_fails_closed(self, tmp_path):
        journal = DurableJournal(path=tmp_path / "dir-in-the-way")
        journal.path.mkdir()
        with pytest.raises(JournalError, match="could not be written"):
            journal.append("S", "E", {})

    @pytest.mark.parametrize(
        ("subject", "event", "match"),
        [("  ", "E", "non-empty subject_id"), ("S", "  ", "non-empty event")],
    )
    def test_a_malformed_entry_is_refused(self, tmp_path, subject, event, match):
        with pytest.raises(JournalError, match=match):
            DurableJournal.open(tmp_path).append(subject, event, {})

    def test_entries_are_filterable_by_subject_and_event(self, tmp_path):
        journal = DurableJournal.open(tmp_path)
        journal.append("A", "X", {})
        journal.append("B", "Y", {})
        assert len(journal.for_subject("A")) == 1
        assert len(journal.by_event("Y")) == 1
        assert len(journal.entries()) == 2

    def test_the_projection_reports_the_head_and_events(self, tmp_path):
        journal = DurableJournal.open(tmp_path)
        journal.append("A", "X", {})
        projection = journal.to_dict()
        assert projection["engine"] == "DurableJournal"
        assert projection["events"] == ["X"]
        assert projection["head_hash"] == journal.head_hash


class TestReconstruction:
    def test_every_record_type_is_rebuilt_as_itself(self, plane, tmp_path):
        journal = DurableJournal.open(tmp_path)
        registration = plane.registration.registrations()[0]
        journal.append_record(EVENT_REGISTERED, registration)
        journal.append_record(EVENT_GOVERNED, plane.governance.state_of(registration.subject_id))
        journal.append_record(
            EVENT_CERTIFIED, plane.certification.state_of(registration.subject_id)
        )
        state = journal.reconstruct()
        assert state.registrations[0].to_dict() == registration.to_dict()
        assert state.governance_of(registration.subject_id).governed is True
        assert state.certification_of(registration.subject_id).certified is True

    def test_versions_and_changes_accumulate_while_states_supersede(self, plane, tmp_path):
        journal = DurableJournal.open(tmp_path)
        subject = plane.registration.registrations()[0].subject_id
        journal.record_all("VERSIONED", plane.version.lineage(subject, kind="implementation"))
        journal.record_all("CHANGED", plane.evolution.changes(subject))
        journal.append_record(EVENT_GOVERNED, plane.governance.state_of(subject))
        journal.append_record(EVENT_GOVERNED, plane.governance.state_of(subject))
        state = journal.reconstruct()
        assert len(state.versions_of(subject)) == 1
        assert len(state.changes) == len(plane.evolution.changes(subject))
        assert len(state.governance) == 1

    def test_an_unknown_event_is_carried_not_reinterpreted(self, tmp_path):
        journal = DurableJournal.open(tmp_path)
        journal.append("S", "SOMETHING-NEW", {"k": "v"})
        state = journal.reconstruct()
        assert state.unknown_events == ("SOMETHING-NEW",)
        assert state.counts() == dict.fromkeys(
            ("registrations", "governance", "certifications", "versions", "changes"), 0
        )

    def test_reconstruction_verifies_the_chain_before_trusting_it(self, tmp_path):
        journal = DurableJournal.open(tmp_path)
        journal.append("S", EVENT_TRUTH_DISCOVERED, {"truth_id": "t"})
        journal._entries[0] = JournalEntry(
            sequence=1,
            subject_id="S",
            event=EVENT_TRUTH_DISCOVERED,
            payload_digest="tampered",
            previous_hash=GENESIS_HASH,
            payload={"truth_id": "t"},
        )
        with pytest.raises(JournalError):
            journal.reconstruct()

    def test_the_reconstructed_state_digest_is_stable(self, plane, tmp_path):
        journal = DurableJournal.open(tmp_path)
        journal.record_all(EVENT_REGISTERED, plane.registration.registrations())
        assert journal.reconstruct().digest() == journal.reconstruct().digest()
        assert json.loads(json.dumps(journal.reconstruct().to_dict(), default=str))

    def test_an_empty_state_is_projectable(self):
        state = ReplayedState(truth_id="")
        assert state.governance_of("x") is None
        assert state.certification_of("x") is None
        assert state.versions_of("x") == ()


# ---------------------------------------------------------------------------
# The composed plane and the completion gate (Wave 6)
# ---------------------------------------------------------------------------


class TestRuntimeDiscovery:
    def test_the_universe_is_declared_not_invented(self, plane):
        universe = plane.universe()
        assert universe.universe_id == "UCOS-CTRL-000001"
        assert universe.name == default_manifest().universe_name

    def test_goals_are_derived_from_registered_programmes(self, plane):
        goals = {
            entry["goal"]["goal_id"]
            for vision in plane.plan.to_dict()["plan"]
            for entry in vision["goals"]
        }
        assert goals == {f"GOAL-{p}" for p in {"UKB", "GOV", "CERTIF", "EES", "DET"}}

    def test_milestones_are_derived_from_registry_volumes(self, plane):
        assert [m.milestone_id for m in plane.roadmap.ordered()] == [
            "VOL-000",
            "VOL-001",
            "VOL-002",
        ]
        assert [m.sequence for m in plane.roadmap.ordered()] == [0, 1, 2]

    def test_agents_are_the_owners_the_registry_declares(self, plane):
        assert "FIXTURE-CUSTODIAN" in {a.agent_id for a in plane.agents.all()}

    def test_the_backlog_is_what_governance_found_wrong(self, plane):
        """Work is not invented to fill a plan. Every item is a violation, and
        the item ids are the violation ids that produced them."""
        assert {i.item_id for i in plane.backlog.ordered()} == {
            v.violation_id for v in plane.governance.violations()
        }
        assert plane.backlog.count() > 0

    def test_backlog_priority_is_attributable_to_severity(self, plane):
        for item in plane.backlog.ordered():
            severity = item.attributes["severity"]
            assert (severity == "CRITICAL") == (item.priority == "CRITICAL")

    def test_engines_are_governed_and_certified_like_everything_else(self, plane):
        """No exemption at the centre: the control plane's own engines are
        subjects of the same rules it applies to the repository."""
        for record in plane.registration.registrations():
            assert plane.governance.state_of(record.subject_id).governed is True
            assert plane.certification.state_of(record.subject_id).certified is True

    def test_engines_are_versioned_in_the_implementation_dimension(self, plane):
        subject = plane.registration.registrations()[0].subject_id
        assert plane.version.current_version(subject, kind="implementation") == "1.0.0"

    def test_artifacts_are_versioned_in_the_artifact_dimension(self, plane):
        assert plane.version.current_version("UCOS-GOV-000001", kind="artifact") == "2.1.0"

    def test_evolution_observes_governance_and_certification(self, plane):
        assert set(plane.evolution.dimensions()) == {"GOVERNANCE", "CERTIFICATION"}

    def test_every_registered_engine_closes_all_nine_linkages(self, plane):
        assert plane.linkage.count() == plane.registration.count()
        assert plane.linkage.orphans() == ()

    def test_progress_and_metrics_measure_the_derived_state(self, plane):
        progress = plane.progress.latest("UCOS-CTRL-000001")
        assert progress.total == plane.governance.count()
        assert progress.completed == len(plane.governance.governed())
        assert plane.metrics.latest("UCOS-CTRL-000001", "engines.registered").value == float(
            plane.registration.count()
        )

    def test_the_schedule_covers_the_derived_backlog(self, plane):
        schedule = plane.schedule()
        assert len(schedule.entries) == plane.backlog.count()
        assert {e.agent_id for e in schedule.entries} <= {a.agent_id for a in plane.agents.all()}

    def test_the_dashboard_reports_every_section(self, plane):
        snapshot = plane.dashboard()
        assert snapshot["dashboard"] == "UCOS-CTRL-000001"
        assert snapshot["registries"][0]["count"] == plane.registration.count()

    def test_a_supplied_truth_engine_skips_rediscovery(self, plane, tmp_path):
        other = ControlPlane.discover(truth=plane.truth, journal_root=tmp_path)
        assert other.truth is plane.truth
        assert other.registration.count() == plane.registration.count()

    def test_the_projection_summarises_every_engine(self, plane):
        projection = plane.to_dict()
        assert projection["control_plane"] == "UCOS-CTRL-000001"
        assert projection["linkage"]["orphans"] == 0
        assert projection["plan"]["milestones"] == plane.roadmap.count()


class TestCompletionGate:
    def test_all_ten_criteria_pass_against_a_composed_plane(self, plane):
        report = plane.completion()
        assert report.complete is True, report.failures
        assert len(report.criteria) == 10
        assert report.failures == ()

    def test_the_gate_names_what_it_measured_for_every_criterion(self, plane):
        assert all(c.measured for c in plane.completion().criteria)

    def test_the_gate_projects_a_pass_count(self, plane):
        projection = plane.completion().to_dict()
        assert projection["passed"] == projection["total"] == 10
        assert projection["truth_id"]

    def test_consumption_is_not_operational_before_anything_consumes(self, tmp_path):
        composed = discover_plane(tmp_path)
        report = composed.completion()
        assert "consumption-operational" in report.failures
        assert report.complete is False
        detail = next(
            c.detail for c in report.criteria if c.criterion_id == "consumption-operational"
        )
        assert "run ControlPlane.consume()" in detail

    def test_replay_is_not_operational_without_a_journal(self, tmp_path):
        repository_root, data_dir = build_substrate(tmp_path)
        composed = ControlPlane.discover(data_dir=data_dir, repository_root=repository_root)
        composed.consume()
        report = composed.completion()
        assert "durable-replay-operational" in report.failures
        criterion = next(
            c for c in report.criteria if c.criterion_id == "durable-replay-operational"
        )
        assert "journal_root=" in criterion.detail

    def test_a_missing_required_engine_fails_the_registration_criterion(self, plane, monkeypatch):
        monkeypatch.setattr(
            type(plane.registration),
            "is_registered",
            lambda self, name: name != "VersionEngine",
        )
        criterion = plane._registration_criterion()
        assert criterion.passed is False
        assert "missing: VersionEngine" in criterion.detail

    def test_the_demo_marker_search_is_executable_not_asserted(self):
        """Deleting the demo and re-adding it later must fail the gate rather
        than pass on a stale claim, so the gate imports and looks."""
        assert demo_markers_present() == ()
        assert "_demo_universe" in DEMO_MARKERS

    def test_a_reintroduced_demo_marker_is_found(self, monkeypatch):
        from platform.universal_control_plane import plan as plan_module

        monkeypatch.setattr(plan_module, "_demo_universe", lambda: None, raising=False)
        assert "platform.universal_control_plane.plan._demo_universe" in demo_markers_present()

    def test_a_non_callable_attribute_is_not_a_demo_marker(self, monkeypatch):
        from platform.universal_control_plane import plan as plan_module

        monkeypatch.setattr(plan_module, "_demo_universe", "just a string", raising=False)
        assert demo_markers_present() == ()

    def test_an_empty_report_is_not_complete(self):
        assert CompletionReport(universe_id="U", truth_id="t", criteria=()).complete is False

    def test_a_criterion_projects_every_field(self):
        criterion = GateCriterion("c", True, "measured", "detail")
        assert criterion.to_dict() == {
            "criterion_id": "c",
            "passed": True,
            "measured": "measured",
            "detail": "detail",
        }


# ---------------------------------------------------------------------------
# Edges the happy path never reaches
# ---------------------------------------------------------------------------


class TestEdges:
    def test_a_journal_free_command_opens_no_journal(self, tmp_path):
        from platform.universal_control_plane import cli as cli_mod

        repository_root, data_dir = build_substrate(tmp_path)
        namespace = cli_mod._build_parser().parse_args(
            ["truth", "--data-dir", str(data_dir), "--repository-root", str(repository_root)]
        )
        assert cli_mod._default_journal_root(namespace) is None

    def test_consumption_coverage_of_nothing_is_zero(self):
        assert ConsumptionEngine().coverage() == 0.0
        assert ConsumptionEngine().operational() is False

    def test_a_malformed_lineage_reconstructs_as_empty_rather_than_crashing(self, tmp_path):
        journal = DurableJournal.open(tmp_path)
        journal.append(
            "S",
            EVENT_REGISTERED,
            {"registration_id": "R", "subject_id": "S", "lineage": "not a list"},
        )
        assert journal.reconstruct().registrations[0].lineage == ()

    def test_an_unreadable_journal_path_fails_closed(self, tmp_path):
        journal = DurableJournal(path=tmp_path / "a-directory")
        journal.path.mkdir()
        with pytest.raises(JournalError, match="could not be read"):
            journal.load()

    def test_a_journal_entry_identifies_itself_by_its_chain_link(self, tmp_path):
        entry = DurableJournal.open(tmp_path).append("S", "E", {})
        assert entry.identity == entry.entry_hash
        assert JournalEntry.from_dict(entry.to_dict()).entry_hash == entry.entry_hash

    def test_rewiring_dependencies_does_not_duplicate_an_edge(self):
        engine = RegistrationEngine()
        engine.register_all()
        before = engine.dependency_registry.count()
        engine._wire_dependencies()
        assert engine.dependency_registry.count() == before

    def test_a_layer_that_depends_on_itself_yields_no_self_edge(self):
        """Defensive against a specialised manifest: a layer declaring itself a
        dependency must not produce an edge from an engine to itself, which the
        dependency registry would refuse outright."""
        import copy
        from platform.universal_control_plane.manifest import (
            ControlPlaneManifest,
            catalog_path,
        )

        document = copy.deepcopy(json.loads(catalog_path().read_text("utf-8")))
        document["engine_taxonomy"]["layer_dependencies"]["PLANNING"] = ["PLANNING"]
        engine = RegistrationEngine(manifest=ControlPlaneManifest.from_document(document))
        engine.register_all(
            [
                EngineDescriptor(name="AEngine", module="m.a", layer="PLANNING"),
                EngineDescriptor(name="BEngine", module="m.b", layer="PLANNING"),
            ]
        )
        edges = engine.dependency_registry.all()
        assert len(edges) == 2
        assert all(e.from_id != e.to_id for e in edges)

    def test_a_violation_on_a_non_artifact_subject_has_no_milestone(self, plane):
        from platform.universal_control_plane.discovery import _milestone_for

        assert _milestone_for(plane, "platform.universal_control_plane.plan.PlanEngine") == ""
        assert _milestone_for(plane, "UCOS-GOV-000001") == "VOL-001"

    def test_a_volume_identifier_without_digits_sequences_at_zero(self):
        from platform.universal_control_plane.discovery import _volume_sequence

        assert _volume_sequence("VOL-007") == 7
        assert _volume_sequence("UNNUMBERED") == 0


def test_a_diamond_dependency_is_scheduled_without_being_mistaken_for_a_cycle() -> None:
    """a depends on b and c; b and c depend on leaf: the second visit must skip, not fail.

    The DFS guard distinguishes "already finished" (skip) from "on the stack" (cycle).
    A diamond exercises precisely the skip arm; a checker that only ever met back-edges
    has not been shown to tolerate shared dependencies, which is the normal case.
    """
    from platform.universal_control_plane.execution import SchedulerEngine
    from platform.universal_control_plane.registry import AgentRegistry, DependencyRegistry

    deps = DependencyRegistry()
    deps.register(DependencyRecord("D1", "a", "b"))
    deps.register(DependencyRecord("D2", "a", "c"))
    deps.register(DependencyRecord("D3", "b", "leaf"))
    deps.register(DependencyRecord("D4", "c", "leaf"))
    agents = AgentRegistry()
    agents.register(AgentRecord(agent_id="AGT-1", name="one", capabilities=()))
    items = [BacklogItem(item_id=i, universe_id="U", title=i) for i in ("leaf", "b", "c", "a")]
    schedule = SchedulerEngine().schedule(items, deps, agents)
    waves = {e.item_id: e.wave for e in schedule.entries}
    assert waves["leaf"] < waves["b"] == waves["c"] < waves["a"]
