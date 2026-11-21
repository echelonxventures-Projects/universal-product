"""UCOS-CTRL-000001 — declared manifest and Repository Truth Engine (Wave 1).

Two claims are under test here and they are the load-bearing ones for the whole
control plane: the manifest is fail-closed about every declaration it is missing,
and truth discovery is a pure function of what it read — same substrate, same
``truth_id``, on any machine, in any process.
"""

from __future__ import annotations

import copy
import json
from pathlib import Path
from platform.tests.control_plane_helpers import (
    FIXTURE_ARTIFACTS,
    FIXTURE_CAPABILITIES,
    FIXTURE_CHANGE_LEDGER,
    FIXTURE_RELATIONSHIPS,
    build_substrate,
)
from platform.universal_control_plane.errors import (
    ManifestError,
    ObjectNotFoundError,
    TruthDiscoveryError,
)
from platform.universal_control_plane.manifest import (
    ArtifactClass,
    ControlPlaneManifest,
    DocumentRef,
    EngineTaxonomy,
    Rule,
    catalog_path,
    default_manifest,
    load_manifest,
)
from platform.universal_control_plane.ontology import TRUTH_UNCLASSIFIED
from platform.universal_control_plane.truth import (
    DEPENDENCY_EDGE_TYPES,
    RepositoryTruthEngine,
    TruthSource,
    build_truth_engine,
)

import pytest


@pytest.fixture(scope="module")
def substrate(tmp_path_factory):
    root = tmp_path_factory.mktemp("truth-substrate")
    return build_substrate(root)


@pytest.fixture(scope="module")
def engine(substrate):
    repository_root, data_dir = substrate
    return RepositoryTruthEngine.discover(data_dir=data_dir, repository_root=repository_root)


def _document() -> dict:
    return json.loads(catalog_path().read_text("utf-8"))


# ---------------------------------------------------------------------------
# Manifest
# ---------------------------------------------------------------------------


class TestManifest:
    def test_packaged_manifest_loads(self):
        manifest = default_manifest()
        assert manifest.universe_id == "UCOS-CTRL-000001"
        assert manifest.manifest_id == "ucos.control-plane.discovery"
        assert len(manifest.linkage_dimensions) == 9

    def test_manifest_round_trips_through_its_projection(self):
        manifest = default_manifest()
        assert manifest.to_dict()["universe_id"] == manifest.universe_id
        assert set(manifest.to_dict()["registry_documents"]) == set(manifest.registry_documents)

    def test_declared_documents_are_reachable_by_name(self):
        ref = default_manifest().document("artifacts")
        assert ref.filename == "artifacts.json"
        assert ref.root_key == "artifacts"

    def test_undeclared_document_fails_closed(self):
        with pytest.raises(ManifestError, match="undeclared registry document"):
            default_manifest().document("invented")

    def test_undeclared_artifact_class_fails_closed(self):
        with pytest.raises(ManifestError, match="undeclared artifact class"):
            default_manifest().artifact_class("invented")

    @pytest.mark.parametrize(
        ("category", "expected"),
        [("GOV", "governance"), ("CERTIF", "certification"), ("REG", "registration")],
    )
    def test_categories_select_their_declared_class(self, category, expected):
        assert expected in default_manifest().classify_artifact(category=category)

    def test_a_programme_can_select_a_class_without_the_category(self):
        assert "registration" in default_manifest().classify_artifact(
            category="UNKNOWN", program="UKB"
        )

    def test_an_unknown_category_selects_nothing(self):
        assert default_manifest().classify_artifact(category="ZZZ", program="") == ()

    def test_missing_universe_id_fails_closed(self):
        document = _document()
        document["universe"] = {}
        with pytest.raises(ManifestError, match="no universe_id"):
            ControlPlaneManifest.from_document(document)

    @pytest.mark.parametrize(
        ("key", "value", "match"),
        [
            ("artifact_classes", [], "no artifact classes"),
            ("linkage_dimensions", [], "no linkage dimensions"),
            ("governance_rules", [], "no governance rules"),
            ("certification_criteria", [], "no certification criteria"),
        ],
    )
    def test_an_empty_declaration_fails_closed(self, key, value, match):
        document = _document()
        document[key] = value
        with pytest.raises(ManifestError, match=match):
            ControlPlaneManifest.from_document(document)

    def test_missing_registry_documents_fail_closed(self):
        document = _document()
        document["truth_sources"]["registry"]["documents"] = {}
        with pytest.raises(ManifestError, match="no registry documents"):
            ControlPlaneManifest.from_document(document)

    def test_missing_catalogue_locator_fails_closed(self):
        document = _document()
        document["truth_sources"]["capability_catalog"]["locator"] = ""
        with pytest.raises(ManifestError, match="no capability catalogue locator"):
            ControlPlaneManifest.from_document(document)

    def test_incomplete_replay_location_fails_closed(self):
        document = _document()
        document["replay"]["journal_filename"] = ""
        with pytest.raises(ManifestError, match="incomplete replay journal location"):
            ControlPlaneManifest.from_document(document)

    def test_a_non_mapping_document_fails_closed(self):
        with pytest.raises(ManifestError, match="must be an object"):
            ControlPlaneManifest.from_document(["not", "a", "mapping"])

    def test_a_document_ref_without_a_filename_fails_closed(self):
        with pytest.raises(ManifestError, match="declares no filename"):
            DocumentRef.from_dict("artifacts", {"root_key": "artifacts"})

    def test_an_artifact_class_without_an_id_fails_closed(self):
        with pytest.raises(ManifestError, match="no class_id"):
            ArtifactClass.from_dict({"categories": ["X"]})

    def test_a_non_string_category_list_fails_closed(self):
        with pytest.raises(ManifestError, match="array of strings"):
            ArtifactClass.from_dict({"class_id": "x", "categories": "GOV"})

    def test_a_category_list_containing_a_non_string_fails_closed(self):
        with pytest.raises(ManifestError, match="only strings"):
            ArtifactClass.from_dict({"class_id": "x", "categories": ["GOV", 7]})

    def test_a_rule_without_an_id_fails_closed(self):
        with pytest.raises(ManifestError, match="no rule_id"):
            Rule.from_dict({"requires": "owner"}, at="rules[]")

    def test_a_rule_without_a_required_fact_fails_closed(self):
        with pytest.raises(ManifestError, match="no 'requires' fact"):
            Rule.from_dict({"rule_id": "R"}, at="rules[]")

    def test_a_criterion_may_name_itself_criterion_id(self):
        rule = Rule.from_dict({"criterion_id": "C", "requires": "governed"}, at="criteria[]")
        assert rule.rule_id == "C"
        assert rule.severity == "MEDIUM"

    def test_a_taxonomy_without_suffixes_fails_closed(self):
        with pytest.raises(ManifestError, match="no class_suffixes"):
            EngineTaxonomy.from_dict({"module_layers": {}})

    def test_taxonomy_layer_lookup_uses_the_terminal_module_segment(self):
        taxonomy = default_manifest().engine_taxonomy
        assert taxonomy.layer_for("platform.universal_control_plane.truth") == "REPOSITORY-TRUTH"
        assert taxonomy.layer_for("a.b.invented") == "UNCLASSIFIED"

    def test_taxonomy_recognises_declared_suffixes_only(self):
        taxonomy = default_manifest().engine_taxonomy
        assert taxonomy.is_engine_class("PlanEngine")
        assert taxonomy.is_engine_class("AgentRegistry")
        assert not taxonomy.is_engine_class("Universe")

    def test_layer_dependencies_are_declared_and_readable(self):
        taxonomy = default_manifest().engine_taxonomy
        assert taxonomy.dependencies_of("REPOSITORY-TRUTH") == ()
        assert "REPOSITORY-TRUTH" in taxonomy.dependencies_of("REGISTRATION")
        assert taxonomy.dependencies_of("INVENTED") == ()

    def test_an_unreadable_manifest_fails_closed(self, tmp_path):
        with pytest.raises(ManifestError, match="could not be read"):
            load_manifest(tmp_path / "absent.json")

    def test_a_malformed_manifest_fails_closed(self, tmp_path):
        path = tmp_path / "broken.json"
        path.write_text("{not json", encoding="utf-8")
        with pytest.raises(ManifestError, match="not valid JSON"):
            load_manifest(path)


# ---------------------------------------------------------------------------
# Repository Truth Engine
# ---------------------------------------------------------------------------


class TestTruthDiscovery:
    def test_every_registered_artifact_is_discovered(self, engine):
        assert len(engine.artifacts()) == len(FIXTURE_ARTIFACTS)
        assert [a.artifact_id for a in engine.artifacts()] == sorted(
            a["universal_id"] for a in FIXTURE_ARTIFACTS
        )

    def test_artifacts_carry_their_registered_facts(self, engine):
        artifact = engine.artifact("UCOS-GOV-000001")
        assert artifact.name == "Fixture Governance Record"
        assert artifact.version == "2.1.0"
        assert artifact.owner == "FIXTURE-CUSTODIAN"
        assert artifact.dependencies == ("UCOS-REG-000001",)
        assert artifact.traceability == ("UCOS-IMP-000001",)

    def test_an_unregistered_artifact_is_an_absence(self, engine):
        with pytest.raises(ObjectNotFoundError, match="not found in Repository Truth"):
            engine.artifact("UCOS-NOPE-000001")

    def test_truth_class_comes_from_the_declared_policy(self, engine):
        assert engine.artifact("UCOS-GOV-000001").truth_class == "canonical"
        assert engine.artifact("UCOS-GOV-000001").canonical_home_eligible is True
        assert engine.artifact("UCOS-CERTIF-000001").truth_class == "historical"
        assert engine.artifact("UCOS-CERTIF-000001").canonical_home_eligible is False

    def test_an_empty_locator_is_an_honest_absence(self, engine):
        assert engine.classify("") == (TRUTH_UNCLASSIFIED, False)

    def test_an_engine_without_a_policy_classifies_nothing(self):
        assert build_truth_engine().classify("engine/x.py") == (TRUTH_UNCLASSIFIED, False)

    def test_a_policy_that_raises_reports_an_absence(self):
        class Hostile:
            policy_id = "hostile"

            def classify(self, _locator):
                raise RuntimeError("policy exploded")

        assert build_truth_engine(policy=Hostile()).classify("x") == (TRUTH_UNCLASSIFIED, False)

    @pytest.mark.parametrize(
        ("class_id", "expected"),
        [
            ("registration", {"UCOS-REG-000001"}),
            ("governance", {"UCOS-GOV-000001"}),
            ("certification", {"UCOS-CERTIF-000001"}),
            ("evidence", {"UCOS-EES-000001"}),
            ("determination", {"UCOS-FINALD-000001"}),
        ],
    )
    def test_each_declared_artifact_class_is_a_discovery_surface(self, engine, class_id, expected):
        assert {a.artifact_id for a in engine.artifacts_in_class(class_id)} == expected

    def test_the_five_class_accessors_agree_with_the_generic_one(self, engine):
        assert engine.registrations() == engine.artifacts_in_class("registration")
        assert engine.certifications() == engine.artifacts_in_class("certification")
        assert engine.determinations() == engine.artifacts_in_class("determination")
        assert engine.evidence() == engine.artifacts_in_class("evidence")
        assert engine.governance_records() == engine.artifacts_in_class("governance")

    def test_an_undeclared_class_fails_closed_rather_than_returning_nothing(self, engine):
        with pytest.raises(ManifestError):
            engine.artifacts_in_class("invented")

    def test_capabilities_come_from_the_sealed_catalogue(self, engine):
        assert [c.capability_id for c in engine.capabilities()] == sorted(
            c["canonical_name"] for c in FIXTURE_CAPABILITIES
        )
        capability = engine.capabilities()[0]
        assert capability.attributes["reuse"] == "REUSE/EXTEND"
        assert capability.attributes["truth_class"] == "canonical"

    def test_an_absent_catalogue_is_reported_not_raised(self, tmp_path):
        repository_root, data_dir = build_substrate(tmp_path, capability_catalog=False)
        engine = RepositoryTruthEngine.discover(data_dir=data_dir, repository_root=repository_root)
        assert engine.capabilities() == ()
        assert engine.source("capability_catalog").available is False

    def test_ownership_is_discovered_for_every_owned_artifact(self, engine):
        owned = [a for a in FIXTURE_ARTIFACTS if a["owner"]]
        assert len(engine.ownership()) == len(owned)
        assert engine.owner_of("UCOS-GOV-000001") == "FIXTURE-CUSTODIAN"

    def test_an_unowned_artifact_reports_no_owner(self, engine):
        assert engine.owner_of("UCOS-FINALD-000001") == ""
        assert engine.owner_of("UCOS-ABSENT") == ""

    def test_ownership_records_carry_the_truth_verdict_for_adjudication(self, engine):
        record = next(o for o in engine.ownership() if o.capability_id == "UCOS-CERTIF-000001")
        assert record.attributes["canonical_home_eligible"] is False

    def test_only_forward_dependency_edges_are_admitted(self, engine):
        kinds = {d.kind for d in engine.dependencies()}
        assert kinds <= {t.upper().replace("-", "_") for t in DEPENDENCY_EDGE_TYPES}
        assert "REQUIRED_BY" not in kinds

    def test_a_self_edge_is_dropped(self, engine):
        assert all(d.from_id != d.to_id for d in engine.dependencies())

    def test_dependency_direction_is_navigable_both_ways(self, engine):
        assert engine.dependencies_of("UCOS-GOV-000001") == ("UCOS-REG-000001",)
        assert engine.dependents_of("UCOS-REG-000001") == ("UCOS-GOV-000001",)

    def test_declared_documents_are_carried_through_verbatim(self, engine):
        assert engine.certification_document["verdict"] == "CERTIFIED"
        assert engine.change_ledger["counts"]["versioned_artifacts"] == 2

    def test_regeneration_timestamps_are_excluded_from_carried_documents(self, engine):
        assert "generated_at" not in engine.certification_document
        assert "generator_version" not in engine.change_ledger

    def test_an_undeclared_source_is_an_absence(self, engine):
        with pytest.raises(ObjectNotFoundError, match="truth source not declared"):
            engine.source("invented")


class TestTruthSnapshot:
    def test_the_snapshot_counts_every_discovery_surface(self, engine):
        counts = engine.truth().counts()
        assert counts["artifacts"] == len(FIXTURE_ARTIFACTS)
        assert counts["dependencies"] == 2
        assert counts["governance"] == 1

    def test_the_truth_id_is_a_function_of_content_alone(self, substrate, tmp_path):
        repository_root, data_dir = substrate
        first = RepositoryTruthEngine.discover(
            data_dir=data_dir, repository_root=repository_root
        ).truth()
        second = RepositoryTruthEngine.discover(
            data_dir=data_dir, repository_root=repository_root
        ).truth()
        assert first.truth_id == second.truth_id

    def test_changing_repository_content_changes_the_truth_id(self, tmp_path, engine):
        mutated = copy.deepcopy(list(FIXTURE_ARTIFACTS))
        mutated[0]["version"] = "9.9.9"
        repository_root, data_dir = build_substrate(tmp_path, artifacts=tuple(mutated))
        other = RepositoryTruthEngine.discover(data_dir=data_dir, repository_root=repository_root)
        assert other.truth().truth_id != engine.truth().truth_id

    def test_the_projection_names_its_sources_and_policy(self, engine):
        projection = engine.to_dict()
        assert projection["engine"] == "RepositoryTruthEngine"
        assert projection["policy_id"] == "ucos.repository.truth"
        assert len(projection["sources"]) == 5

    def test_a_supplied_tick_travels_into_every_projected_object(self, engine):
        assert all(a.tick == 5 for a in engine.artifacts(tick=5))
        assert engine.truth(tick=5).tick == 5


class TestTruthFailureModes:
    def test_an_unreachable_registry_fails_closed(self, tmp_path):
        with pytest.raises(TruthDiscoveryError, match="registry substrate is unreachable"):
            RepositoryTruthEngine.discover(data_dir=tmp_path / "absent")

    def test_a_missing_declared_document_fails_closed(self, tmp_path):
        _repository_root, data_dir = build_substrate(tmp_path)
        (data_dir / "change-ledger.json").unlink()
        with pytest.raises(TruthDiscoveryError, match="could not be read"):
            RepositoryTruthEngine.discover(data_dir=data_dir, repository_root=tmp_path)

    def test_a_document_without_its_records_array_fails_closed(self, tmp_path):
        _repository_root, data_dir = build_substrate(tmp_path)
        (data_dir / "artifacts.json").write_text('{"count": 0}', encoding="utf-8")
        with pytest.raises(TruthDiscoveryError, match="no 'artifacts' records array"):
            RepositoryTruthEngine.discover(data_dir=data_dir, repository_root=tmp_path)

    def test_a_document_that_is_not_an_object_fails_closed(self, tmp_path):
        _repository_root, data_dir = build_substrate(tmp_path)
        (data_dir / "certification.json").write_text("[1, 2, 3]", encoding="utf-8")
        with pytest.raises(TruthDiscoveryError, match="not a JSON object"):
            RepositoryTruthEngine.discover(data_dir=data_dir, repository_root=tmp_path)

    def test_an_unreadable_catalogue_fails_closed(self, tmp_path):
        repository_root, data_dir = build_substrate(tmp_path)
        (repository_root / "intelligence" / "UCOS-RIE-CAPABILITY-CATALOG.json").write_text(
            "{oops", encoding="utf-8"
        )
        with pytest.raises(TruthDiscoveryError, match="could not be read"):
            RepositoryTruthEngine.discover(data_dir=data_dir, repository_root=repository_root)

    def test_a_catalogue_without_its_records_array_fails_closed(self, tmp_path):
        repository_root, data_dir = build_substrate(tmp_path)
        (repository_root / "intelligence" / "UCOS-RIE-CAPABILITY-CATALOG.json").write_text(
            '{"artifact_id": "x"}', encoding="utf-8"
        )
        with pytest.raises(TruthDiscoveryError, match="no 'capabilities' records array"):
            RepositoryTruthEngine.discover(data_dir=data_dir, repository_root=repository_root)

    def test_records_without_an_identifier_are_skipped_not_fatal(self):
        engine = build_truth_engine(
            artifacts=[{"universal_id": "", "name": "nameless"}, FIXTURE_ARTIFACTS[0]],
            capabilities=[{"canonical_name": ""}, FIXTURE_CAPABILITIES[0]],
            relationships=[{"type": "Depends-On", "from": "", "to": "X"}],
        )
        assert len(engine.artifacts()) == 1
        assert len(engine.capabilities()) == 1
        assert engine.dependencies() == ()

    def test_a_non_mapping_traceability_block_is_tolerated(self):
        record = dict(FIXTURE_ARTIFACTS[0])
        record["traceability"] = "not a mapping"
        assert build_truth_engine(artifacts=[record]).artifacts()[0].traceability == ()


class TestSuppliedRecords:
    def test_a_supplied_engine_projects_identically_to_a_discovered_one(self, engine):
        supplied = build_truth_engine(
            artifacts=FIXTURE_ARTIFACTS,
            relationships=FIXTURE_RELATIONSHIPS,
            capabilities=FIXTURE_CAPABILITIES,
            change_ledger=FIXTURE_CHANGE_LEDGER,
            policy=engine._policy,
        )
        assert [a.to_dict() for a in supplied.artifacts()] == [
            a.to_dict() for a in engine.artifacts()
        ]

    def test_a_supplied_engine_names_its_own_sources(self):
        supplied = build_truth_engine(artifacts=FIXTURE_ARTIFACTS)
        assert {s.kind for s in supplied.sources} == {"SUPPLIED"}

    def test_a_truth_source_projects_every_field(self):
        source = TruthSource("s", "REGISTRY", "f.json", "d", record_count=3)
        assert source.to_dict() == {
            "source_id": "s",
            "kind": "REGISTRY",
            "locator": "f.json",
            "digest": "d",
            "record_count": 3,
            "available": True,
        }


def test_the_package_ships_its_declared_catalogue():
    """The manifest is data the package carries, not something a deployment
    must supply — a control plane whose declaration is missing cannot start."""
    assert catalog_path().is_file()
    assert Path(catalog_path()).parent.name == "catalog"


class TestProgressCounts:
    def test_progress_can_be_measured_from_counts_a_caller_already_has(self):
        from platform.universal_control_plane.intelligence import ProgressEngine

        record = ProgressEngine().measure_counts("U", total=4, completed=1)
        assert record.total == 4
        assert record.percentage == 25.0

    @pytest.mark.parametrize(
        ("total", "completed", "match"),
        [(-1, 0, "non-negative"), (0, -1, "non-negative"), (2, 3, "cannot exceed total")],
    )
    def test_impossible_progress_counts_are_refused(self, total, completed, match):
        from platform.universal_control_plane.intelligence import ProgressEngine

        with pytest.raises(ValueError, match=match):
            ProgressEngine().measure_counts("U", total=total, completed=completed)


def test_a_traceability_stage_carried_as_a_bare_string_adds_no_references(engine) -> None:
    """A stage whose value is `"ABCD"` is not four references (the Sequence guard's skip).

    The projection must skip str and bytes: without the skip arm one hand-written string
    would inflate a real artifact's reference set to four invented ones.
    """

    record = dict(FIXTURE_ARTIFACTS[0])
    record["universal_id"] = "UCOS-REG-STRACE-1"
    record["name"] = "string trace"
    record["path"] = "00-BOOK/REGISTRIES/strace.md"
    record["traceability"] = {"spec": "ABCD", "design": ["UCOS-ARCH-000001"]}
    projected = RepositoryTruthEngine(
        manifest=engine.manifest,
        _artifact_records=(record, *FIXTURE_ARTIFACTS[1:]),
    )
    found = [a for a in projected.artifacts() if a.artifact_id == "UCOS-REG-STRACE-1"]
    assert found
    assert found[0].traceability == ("UCOS-ARCH-000001",)
