"""UCOS-CTRL-000001 — Version (Wave 4) and Evolution (Wave 5) Engines.

The claim being tested is that version and change are *executable*: a lineage can
be promoted, rolled back and replayed; a delta can be classified as an
improvement or a regression against a declared ranking; and the whole history
re-folds from its own log to the identical result. A version string that could
only be printed would pass none of these.
"""

from __future__ import annotations

from platform.tests.control_plane_helpers import FIXTURE_CHANGE_LEDGER
from platform.universal_control_plane.errors import (
    EvolutionError,
    ObjectNotFoundError,
    VersionError,
)
from platform.universal_control_plane.evolution import (
    DEFAULT_ORDERINGS,
    EvolutionEngine,
    Observation,
)
from platform.universal_control_plane.ontology import (
    CERTIFICATION_CERTIFIED,
    CERTIFICATION_NOT_CERTIFIED,
    CHANGE_CREATED,
    CHANGE_IMPROVED,
    CHANGE_MODIFIED,
    CHANGE_PROMOTED,
    CHANGE_REGRESSED,
    CHANGE_REMOVED,
    CHANGE_UNCHANGED,
    DIMENSION_ARCHITECTURE,
    DIMENSION_CERTIFICATION,
    DIMENSION_GOVERNANCE,
    DIMENSION_VERSION,
    GOVERNANCE_GOVERNED,
    GOVERNANCE_NOT_GOVERNED,
    VERSION_ARTIFACT,
    VERSION_KINDS,
    VERSION_SEMANTIC,
)
from platform.universal_control_plane.version import (
    LEVEL_MAJOR,
    LEVEL_MINOR,
    LEVEL_PATCH,
    SemanticVersion,
    VersionEngine,
    compare_versions,
)

import pytest

# ---------------------------------------------------------------------------
# Semantic versions
# ---------------------------------------------------------------------------


class TestSemanticVersion:
    @pytest.mark.parametrize(
        ("text", "expected"),
        [
            ("1.2.3", (1, 2, 3, "")),
            ("v2.0.0", (2, 0, 0, "")),
            ("3", (3, 0, 0, "")),
            ("4.5", (4, 5, 0, "")),
            ("1.0.0-rc1", (1, 0, 0, "rc1")),
            ("  1.0.0  ", (1, 0, 0, "")),
        ],
    )
    def test_parsing_is_total_over_the_shapes_the_repository_uses(self, text, expected):
        parsed = SemanticVersion.parse(text)
        assert (parsed.major, parsed.minor, parsed.patch, parsed.pre) == expected

    @pytest.mark.parametrize("text", ["", "abc", "UCOS-CTRL-000001", "1.x.0"])
    def test_an_unparseable_version_is_refused(self, text):
        with pytest.raises(VersionError, match="not a parseable version"):
            SemanticVersion.parse(text)
        assert SemanticVersion.try_parse(text) is None

    def test_a_pre_release_sorts_before_its_release(self):
        assert SemanticVersion.parse("1.0.0-rc1") < SemanticVersion.parse("1.0.0")
        assert SemanticVersion.parse("1.0.0-rc1") <= SemanticVersion.parse("1.0.0")

    def test_ordering_is_by_component_not_by_string(self):
        assert SemanticVersion.parse("1.9.0") < SemanticVersion.parse("1.10.0")
        assert SemanticVersion.parse("2.0.0") <= SemanticVersion.parse("2.0.0")

    @pytest.mark.parametrize(
        ("start", "level", "expected"),
        [
            ("1.2.3", LEVEL_MAJOR, "2.0.0"),
            ("1.2.3", LEVEL_MINOR, "1.3.0"),
            ("1.2.3", LEVEL_PATCH, "1.2.4"),
            ("1.0.0-rc1", LEVEL_PATCH, "1.0.0"),
            ("1.0.0-rc1", LEVEL_MINOR, "1.1.0"),
        ],
    )
    def test_bumping_moves_the_declared_component(self, start, level, expected):
        assert str(SemanticVersion.parse(start).bump(level)) == expected

    def test_an_unknown_promotion_level_is_refused(self):
        with pytest.raises(VersionError, match="unknown promotion level"):
            SemanticVersion.parse("1.0.0").bump("epoch")

    def test_a_version_projects_its_components(self):
        assert SemanticVersion.parse("1.0.0-rc1").to_dict()["version"] == "1.0.0-rc1"

    @pytest.mark.parametrize(
        ("left", "right", "expected"),
        [
            ("1.0.0", "2.0.0", -1),
            ("2.0.0", "1.0.0", 1),
            ("1.0.0", "1.0.0", 0),
            ("1.0.0", "opaque", 1),
            ("opaque", "1.0.0", -1),
            ("alpha", "beta", -1),
            ("beta", "alpha", 1),
            ("opaque", "opaque", 0),
        ],
    )
    def test_comparison_is_total_even_over_opaque_tokens(self, left, right, expected):
        """The repository carries constitutional versions that are not semantic.
        Refusing to order them would make a mixed lineage unsortable, so a
        parseable version outranks an opaque one and two opaque ones compare
        lexically."""
        assert compare_versions(left, right) == expected


# ---------------------------------------------------------------------------
# Version Engine
# ---------------------------------------------------------------------------


class TestVersionRegistration:
    def test_the_first_registration_is_a_lineage_root(self):
        engine = VersionEngine()
        record = engine.register("S", version="1.0.0", content_digest="d")
        assert record.revision == 1
        assert record.is_root is True
        assert record.parent_version_id == ""
        assert engine.current_version("S") == "1.0.0"

    def test_a_second_registration_chains_onto_the_first(self):
        engine = VersionEngine()
        first = engine.register("S", version="1.0.0")
        second = engine.register("S", version="1.1.0")
        assert second.parent_version_id == first.version_id
        assert second.revision == 2
        assert engine.lineage("S")[0].superseded_by == second.version_id

    def test_superseding_does_not_change_an_identity(self):
        """``superseded_by`` sits outside the content address on purpose: if it
        did not, every ancestor link would break the moment something newer
        pointed at it."""
        engine = VersionEngine()
        first = engine.register("S", version="1.0.0")
        original_id = first.version_id
        engine.register("S", version="1.1.0")
        assert engine.lineage("S")[0].version_id == original_id
        assert engine.get(original_id).superseded_by

    def test_re_registering_identical_content_is_idempotent(self):
        engine = VersionEngine()
        first = engine.register("S", version="1.0.0", content_digest="d")
        again = engine.register("S", version="1.0.0", content_digest="d")
        assert again is first
        assert engine.count() == 1

    def test_the_same_version_with_new_content_appends(self):
        engine = VersionEngine()
        engine.register("S", version="1.0.0", content_digest="a")
        engine.register("S", version="1.0.0", content_digest="b")
        assert engine.count() == 2

    def test_identity_is_content_addressed(self):
        left = VersionEngine().register("S", version="1.0.0", content_digest="d")
        right = VersionEngine().register("S", version="1.0.0", content_digest="d")
        assert left.version_id == right.version_id
        assert left.identity == left.version_id

    def test_dimensions_are_independent(self):
        engine = VersionEngine()
        engine.register("S", kind=VERSION_SEMANTIC, version="1.0.0")
        engine.register("S", kind=VERSION_ARTIFACT, version="9.9.9")
        assert engine.current_version("S", kind=VERSION_SEMANTIC) == "1.0.0"
        assert engine.current_version("S", kind=VERSION_ARTIFACT) == "9.9.9"
        assert engine.kinds_for("S") == (VERSION_ARTIFACT, VERSION_SEMANTIC)

    @pytest.mark.parametrize("kind", VERSION_KINDS)
    def test_every_declared_dimension_is_registrable(self, kind):
        assert VersionEngine().register("S", kind=kind, version="1.0.0").kind == kind

    @pytest.mark.parametrize(
        ("kwargs", "match"),
        [
            ({"subject_id": " ", "version": "1.0.0"}, "non-empty subject_id"),
            ({"subject_id": "S", "kind": "invented", "version": "1.0.0"}, "unknown version kind"),
            ({"subject_id": "S", "version": "  "}, "must be non-empty"),
        ],
    )
    def test_a_malformed_registration_is_refused(self, kwargs, match):
        subject = kwargs.pop("subject_id")
        with pytest.raises(VersionError, match=match):
            VersionEngine().register(subject, **kwargs)

    def test_an_unregistered_subject_is_an_absence(self):
        engine = VersionEngine()
        assert engine.current_version("nope") == ""
        assert engine.lineage("nope") == ()
        with pytest.raises(ObjectNotFoundError, match="no semantic version registered"):
            engine.current("nope")
        with pytest.raises(ObjectNotFoundError, match="version record not found"):
            engine.get("deadbeef")


class TestVersionLineage:
    def test_ancestry_walks_back_to_the_root(self):
        engine = VersionEngine()
        engine.register("S", version="1.0.0")
        engine.register("S", version="1.1.0")
        head = engine.register("S", version="1.2.0")
        ancestry = engine.ancestry(head.version_id)
        assert [r.version for r in ancestry] == ["1.2.0", "1.1.0", "1.0.0"]
        assert ancestry[-1].is_root

    def test_subjects_are_enumerable_globally_and_per_dimension(self):
        engine = VersionEngine()
        engine.register("A", kind=VERSION_ARTIFACT, version="1.0.0")
        engine.register("B", kind=VERSION_SEMANTIC, version="1.0.0")
        assert engine.subjects() == ("A", "B")
        assert engine.subjects(kind=VERSION_ARTIFACT) == ("A",)

    def test_comparison_orders_two_subjects_in_one_dimension(self):
        engine = VersionEngine()
        engine.register("A", version="2.0.0")
        engine.register("B", version="1.0.0")
        assert engine.compare("A", "B") == 1
        assert engine.is_ahead_of("A", "B") is True
        assert engine.is_ahead_of("B", "A") is False


class TestPromotionAndRollback:
    def test_promotion_appends_the_next_version(self):
        engine = VersionEngine()
        engine.register("S", version="1.2.3", content_digest="d")
        promoted = engine.promote("S", level=LEVEL_MINOR)
        assert promoted.version == "1.3.0"
        assert promoted.revision == 2
        assert promoted.content_digest == "d"
        assert "promoted minor from 1.2.3" in promoted.rationale

    def test_promotion_of_an_opaque_version_is_refused(self):
        engine = VersionEngine()
        engine.register("S", version="UCOS-CTRL-000001")
        with pytest.raises(VersionError, match="cannot promote an unparseable"):
            engine.promote("S")

    def test_rollback_restores_forward_without_deleting_history(self):
        engine = VersionEngine()
        engine.register("S", version="1.0.0", content_digest="a")
        engine.promote("S", level=LEVEL_MINOR, content_digest="b")
        restored = engine.rollback("S", to_revision=1)
        assert restored.version == "1.0.0"
        assert restored.content_digest == "a"
        assert restored.revision == 3
        assert [r.version for r in engine.lineage("S")] == ["1.0.0", "1.1.0", "1.0.0"]
        assert restored.attributes["restored_revision"] == 1

    def test_rollback_records_what_it_rolled_back_from(self):
        engine = VersionEngine()
        engine.register("S", version="1.0.0")
        head = engine.promote("S", level=LEVEL_MAJOR)
        restored = engine.rollback("S", to_revision=1)
        assert restored.attributes["rollback_of"] == head.version_id
        assert "rolled back from 2.0.0" in restored.rationale

    def test_rolling_back_to_the_head_is_refused(self):
        engine = VersionEngine()
        engine.register("S", version="1.0.0")
        with pytest.raises(VersionError, match="already the head"):
            engine.rollback("S", to_revision=1)

    def test_rolling_back_to_an_absent_revision_is_refused(self):
        engine = VersionEngine()
        engine.register("S", version="1.0.0")
        engine.promote("S")
        with pytest.raises(VersionError, match="is not in the semantic lineage"):
            engine.rollback("S", to_revision=9)

    def test_rolling_back_an_unversioned_subject_is_an_absence(self):
        with pytest.raises(ObjectNotFoundError):
            VersionEngine().rollback("nope", to_revision=1)


class TestVersionReplay:
    def test_a_well_formed_lineage_replays(self):
        engine = VersionEngine()
        engine.register("S", version="1.0.0")
        engine.promote("S")
        engine.rollback("S", to_revision=1)
        assert engine.verify("S") is True
        assert len(engine.replay("S")) == 3

    def test_replaying_an_unversioned_subject_is_an_absence(self):
        with pytest.raises(ObjectNotFoundError):
            VersionEngine().replay("nope")

    def test_a_broken_revision_sequence_fails_closed(self):
        engine = VersionEngine()
        engine.register("S", version="1.0.0")
        chain = engine._lineages[("S", VERSION_SEMANTIC)]
        chain[0] = type(chain[0])(
            subject_id="S", kind=VERSION_SEMANTIC, version="1.0.0", revision=7
        )
        with pytest.raises(VersionError, match="breaks at position 1"):
            engine.replay("S")

    def test_a_broken_parent_link_fails_closed(self):
        engine = VersionEngine()
        first = engine.register("S", version="1.0.0")
        engine.register("S", version="1.1.0")
        chain = engine._lineages[("S", VERSION_SEMANTIC)]
        chain[1] = type(first)(
            subject_id="S",
            kind=VERSION_SEMANTIC,
            version="1.1.0",
            revision=2,
            parent_version_id="not-the-parent",
        )
        with pytest.raises(VersionError, match="parent 'not-the-parent'"):
            engine.replay("S")

    def test_an_unindexed_record_fails_closed(self):
        engine = VersionEngine()
        record = engine.register("S", version="1.0.0")
        del engine._by_version_id[record.version_id]
        with pytest.raises(VersionError, match="unindexed version"):
            engine.replay("S")

    def test_a_looping_ancestry_fails_closed(self):
        engine = VersionEngine()
        record = engine.register("S", version="1.0.0")
        looped = type(record)(
            subject_id="S",
            kind=VERSION_SEMANTIC,
            version="1.0.0",
            revision=1,
            parent_version_id=record.version_id,
        )
        engine._by_version_id[record.version_id] = looped
        with pytest.raises(VersionError, match="ancestry loops"):
            engine.ancestry(record.version_id)

    def test_the_replay_digest_is_equal_iff_the_history_is_equal(self):
        left, right = VersionEngine(), VersionEngine()
        for engine in (left, right):
            engine.register("S", version="1.0.0", content_digest="d")
            engine.promote("S")
        assert left.replay_digest() == right.replay_digest()
        right.promote("S")
        assert left.replay_digest() != right.replay_digest()


class TestVersionIngestion:
    def test_the_change_ledger_populates_a_dimension(self):
        engine = VersionEngine()
        appended = engine.ingest_change_ledger(FIXTURE_CHANGE_LEDGER)
        assert appended == 3
        assert engine.current_version("UCOS-GOV-000001", kind=VERSION_ARTIFACT) == "2.1.0"
        assert len(engine.lineage("UCOS-GOV-000001", kind=VERSION_ARTIFACT)) == 2

    def test_a_ledger_without_version_records_fails_closed(self):
        with pytest.raises(VersionError, match="no 'version_records' mapping"):
            VersionEngine().ingest_change_ledger({"counts": {}})

    def test_malformed_ledger_entries_are_skipped_not_fatal(self):
        engine = VersionEngine()
        appended = engine.ingest_change_ledger(
            {
                "version_records": {
                    "A": "not a mapping",
                    "B": {"history": "not a list"},
                    "C": {"history": ["not a mapping", {"version": ""}, {"version": "1.0.0"}]},
                }
            }
        )
        assert appended == 1
        assert engine.subjects() == ("C",)

    def test_pairs_can_be_ingested_with_digests(self):
        engine = VersionEngine()
        records = engine.ingest(
            [("B", "2.0.0"), ("A", "1.0.0"), ("C", "")],
            kind=VERSION_ARTIFACT,
            digests={"A": "da"},
        )
        assert [r.subject_id for r in records] == ["A", "B"]
        assert records[0].content_digest == "da"

    def test_the_projection_reports_counts_by_dimension(self):
        engine = VersionEngine()
        engine.register("A", kind=VERSION_ARTIFACT, version="1.0.0")
        engine.register("B", kind=VERSION_SEMANTIC, version="1.0.0")
        projection = engine.to_dict()
        assert projection["engine"] == "VersionEngine"
        assert projection["counts"]["by_kind"] == {"artifact": 1, "semantic": 1}
        assert projection["kinds"] == list(VERSION_KINDS)


# ---------------------------------------------------------------------------
# Evolution Engine
# ---------------------------------------------------------------------------


class TestEvolutionClassification:
    def test_a_first_observation_is_a_creation(self):
        change = EvolutionEngine().observe("S", DIMENSION_GOVERNANCE, GOVERNANCE_GOVERNED)
        assert change.kind == CHANGE_CREATED
        assert change.from_value == ""
        assert change.sequence == 1

    def test_an_unchanged_observation_says_so(self):
        engine = EvolutionEngine()
        engine.observe("S", DIMENSION_GOVERNANCE, GOVERNANCE_GOVERNED)
        assert (
            engine.observe("S", DIMENSION_GOVERNANCE, GOVERNANCE_GOVERNED).kind == CHANGE_UNCHANGED
        )

    def test_a_declared_ranking_classifies_direction(self):
        engine = EvolutionEngine()
        engine.observe("S", DIMENSION_GOVERNANCE, GOVERNANCE_NOT_GOVERNED)
        assert (
            engine.observe("S", DIMENSION_GOVERNANCE, GOVERNANCE_GOVERNED).kind == CHANGE_PROMOTED
        )
        assert (
            engine.observe("S", DIMENSION_GOVERNANCE, GOVERNANCE_NOT_GOVERNED).kind
            == CHANGE_REGRESSED
        )

    def test_certification_ships_a_declared_ranking_too(self):
        engine = EvolutionEngine()
        engine.observe("S", DIMENSION_CERTIFICATION, CERTIFICATION_NOT_CERTIFIED)
        assert (
            engine.observe("S", DIMENSION_CERTIFICATION, CERTIFICATION_CERTIFIED).kind
            == CHANGE_PROMOTED
        )

    def test_versions_are_ordered_semantically(self):
        engine = EvolutionEngine()
        engine.observe("S", DIMENSION_VERSION, "1.0.0")
        assert engine.observe("S", DIMENSION_VERSION, "1.1.0").kind == CHANGE_PROMOTED
        assert engine.observe("S", DIMENSION_VERSION, "1.0.0").kind == CHANGE_REGRESSED

    def test_two_opaque_versions_in_the_version_dimension_compare_lexically(self):
        engine = EvolutionEngine()
        assert engine.classify(DIMENSION_VERSION, "alpha", "beta") == CHANGE_PROMOTED

    def test_version_shaped_values_are_ordered_in_any_dimension(self):
        assert EvolutionEngine().classify("anything", "1.0.0", "2.0.0") == CHANGE_PROMOTED

    def test_numeric_values_are_improvements_or_regressions(self):
        engine = EvolutionEngine()
        assert engine.classify("coverage", "90.5", "94.4") == CHANGE_IMPROVED
        assert engine.classify("coverage", "94.4", "90.5") == CHANGE_REGRESSED

    def test_an_unranked_dimension_declines_to_editorialise(self):
        """Saying MODIFIED is the honest answer where no ranking is declared;
        guessing a direction would invent an authority over the values."""
        assert EvolutionEngine().classify("colour", "red", "blue") == CHANGE_MODIFIED

    def test_retiring_a_subject_records_its_removal(self):
        engine = EvolutionEngine()
        engine.observe("S", DIMENSION_GOVERNANCE, GOVERNANCE_GOVERNED)
        change = engine.retire("S", DIMENSION_GOVERNANCE)
        assert change.kind == CHANGE_REMOVED
        assert change.to_value == ""
        assert engine.current_value("S", DIMENSION_GOVERNANCE) == ""

    def test_retiring_something_never_observed_is_refused(self):
        with pytest.raises(EvolutionError, match="never observed there"):
            EvolutionEngine().retire("S", DIMENSION_GOVERNANCE)

    @pytest.mark.parametrize(
        ("subject", "dimension", "match"),
        [(" ", "d", "non-empty subject_id"), ("s", " ", "non-empty dimension")],
    )
    def test_a_malformed_observation_is_refused(self, subject, dimension, match):
        with pytest.raises(EvolutionError, match=match):
            EvolutionEngine().observe(subject, dimension, "v")

    def test_dimensions_ship_declared_and_are_extensible(self):
        engine = EvolutionEngine()
        assert set(DEFAULT_ORDERINGS) <= set(engine._orderings)
        engine.register_ordering("maturity", ["ALPHA", "BETA", "GA"])
        assert engine.ordering("maturity") == ("ALPHA", "BETA", "GA")
        engine.observe("S", "maturity", "ALPHA")
        assert engine.observe("S", "maturity", "GA").kind == CHANGE_PROMOTED

    @pytest.mark.parametrize(
        ("dimension", "ranks", "match"),
        [
            (" ", ["A", "B"], "non-empty dimension"),
            ("d", ["A"], "at least two ranked values"),
            ("d", ["A", "A"], "ranks a value twice"),
        ],
    )
    def test_a_malformed_ordering_is_refused(self, dimension, ranks, match):
        with pytest.raises(EvolutionError, match=match):
            EvolutionEngine().register_ordering(dimension, ranks)

    def test_an_unranked_dimension_reports_no_ordering(self):
        assert EvolutionEngine().ordering("invented") == ()


class TestEvolutionSnapshots:
    def test_a_snapshot_observes_everything_present_and_retires_what_vanished(self):
        engine = EvolutionEngine()
        engine.observe_snapshot(DIMENSION_GOVERNANCE, {"A": "GOVERNED", "B": "GOVERNED"})
        changes = engine.observe_snapshot(DIMENSION_GOVERNANCE, {"A": "NOT-GOVERNED"})
        kinds = {c.subject_id: c.kind for c in changes}
        assert kinds == {"A": CHANGE_REGRESSED, "B": CHANGE_REMOVED}

    def test_observe_many_is_order_independent(self):
        engine = EvolutionEngine()
        changes = engine.observe_many(
            [("B", "d", "1"), ("A", "d", "1")],
        )
        assert [c.subject_id for c in changes] == ["A", "B"]

    def test_diff_classifies_without_recording(self):
        engine = EvolutionEngine()
        engine.observe("X", DIMENSION_GOVERNANCE, GOVERNANCE_GOVERNED)
        before = engine.count()
        deltas = engine.diff(
            DIMENSION_GOVERNANCE,
            {"A": GOVERNANCE_NOT_GOVERNED, "B": GOVERNANCE_GOVERNED},
            {"A": GOVERNANCE_GOVERNED},
        )
        assert {c.subject_id: c.kind for c in deltas} == {
            "A": CHANGE_PROMOTED,
            "B": CHANGE_REMOVED,
        }
        assert engine.count() == before

    def test_the_ledger_populates_the_architecture_dimension(self):
        engine = EvolutionEngine()
        assert engine.ingest_change_ledger(FIXTURE_CHANGE_LEDGER) == 3
        assert engine.dimensions() == (DIMENSION_ARCHITECTURE,)
        assert engine.current_value("UCOS-GOV-000001", DIMENSION_ARCHITECTURE) == "ACTIVE"

    def test_a_ledger_without_change_events_fails_closed(self):
        with pytest.raises(EvolutionError, match="no 'change_events' array"):
            EvolutionEngine().ingest_change_ledger({"counts": {}})

    def test_malformed_ledger_events_are_skipped_not_fatal(self):
        engine = EvolutionEngine()
        appended = engine.ingest_change_ledger(
            {"change_events": ["not a mapping", {"subject": ""}, {"subject": "A", "to": "X"}]}
        )
        assert appended == 1


class TestEvolutionReplay:
    def test_replaying_the_log_reproduces_the_recorded_history(self):
        engine = EvolutionEngine()
        engine.observe("A", DIMENSION_GOVERNANCE, GOVERNANCE_NOT_GOVERNED)
        engine.observe("A", DIMENSION_GOVERNANCE, GOVERNANCE_GOVERNED)
        engine.retire("A", DIMENSION_GOVERNANCE)
        assert engine.verify() is True
        assert [c.to_dict() for c in engine.replay()] == [c.to_dict() for c in engine.changes()]

    def test_a_corrupt_history_is_detected(self):
        engine = EvolutionEngine()
        engine.observe("A", DIMENSION_GOVERNANCE, GOVERNANCE_GOVERNED)
        engine._changes.clear()
        with pytest.raises(EvolutionError, match="replay diverged"):
            engine.verify()

    def test_changes_can_be_filtered_three_ways(self):
        engine = EvolutionEngine()
        engine.observe("A", DIMENSION_GOVERNANCE, GOVERNANCE_NOT_GOVERNED)
        engine.observe("A", DIMENSION_GOVERNANCE, GOVERNANCE_GOVERNED)
        engine.observe("B", DIMENSION_VERSION, "1.0.0")
        assert len(engine.changes("A")) == 2
        assert len(engine.changes(dimension=DIMENSION_VERSION)) == 1
        assert len(engine.changes(kind=CHANGE_PROMOTED)) == 1
        assert len(engine.promotions()) == 1
        assert engine.regressions() == ()
        assert engine.improvements() == ()

    def test_deltas_exclude_the_unchanged(self):
        engine = EvolutionEngine()
        engine.observe("A", "d", "1")
        engine.observe("A", "d", "1")
        assert engine.count() == 2
        assert len(engine.deltas()) == 1

    def test_the_projection_reports_the_histogram_and_digest(self):
        engine = EvolutionEngine()
        engine.observe("A", DIMENSION_GOVERNANCE, GOVERNANCE_GOVERNED)
        projection = engine.to_dict()
        assert projection["engine"] == "EvolutionEngine"
        assert projection["histogram"] == {CHANGE_CREATED: 1}
        assert len(projection["replay_digest"]) == 64
        assert projection["counts"]["observations"] == 1

    def test_observations_are_the_durable_state_and_are_readable(self):
        engine = EvolutionEngine()
        engine.observe("A", "d", "v", tick=4)
        observation = engine.observations()[0]
        assert observation == Observation("A", "d", "v", tick=4)
        assert observation.to_dict()["present"] is True


class TestClassificationEdges:
    def test_equal_versions_written_differently_are_unchanged(self):
        """``1.0`` and ``1.0.0`` are the same version spelled two ways; the
        classifier compares parsed components, not the strings."""
        assert EvolutionEngine().classify(DIMENSION_VERSION, "1.0", "1.0.0") == CHANGE_UNCHANGED

    def test_a_lower_version_in_the_version_dimension_is_a_regression(self):
        assert EvolutionEngine().classify(DIMENSION_VERSION, "2.0.0", "1.0.0") == CHANGE_REGRESSED
