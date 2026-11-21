"""UCOS-EPIC-014 — Evidence Collection tests.

Evidence Collection is "the spine of the other nine". Its three load-bearing claims are
tested here rather than assumed:

* **Drift is visible in both directions.** A policy-required artifact no stage
  contributed is *missing*; an artifact a stage contributed that the policy never
  declared is *undeclared* and counted. Neither can be silent.
* **The write scope is enforced before a byte is written.** ``forbidden_write_prefixes``
  must stop a write into the read-only certified corpus whether it is spelled relatively
  or absolutely (DP-03 / C-01).
* **Byte stability.** Re-writing an identical bundle must produce identical bytes.

The manifest is self-verifying, so a payload mutated after collection must be detectable
by recomputation — that is exercised directly.
"""

from __future__ import annotations

import json
from platform.universal_assurance.contracts import AssuranceStage
from platform.universal_assurance.errors import AssuranceEvidenceError
from platform.universal_assurance.evidence import (
    EVIDENCE_BUNDLE_FORMAT,
    EVIDENCE_MANIFEST_FORMAT,
    MANIFEST_FILENAME,
    UNDECLARED_ARTIFACT_PREFIX,
    EvidenceArtifact,
    EvidenceBundle,
    EvidenceCollector,
    check_write_scope,
    write_bundle,
    write_json,
)

import pytest

from .universal_assurance_helpers import make_policy


def _collector():
    return EvidenceCollector(make_policy())


def _bundle_with_plan():
    collector = _collector()
    collector.record(AssuranceStage.VALIDATION_PLANNING, "validation-plan", {"a": 1})
    return collector.bundle(subject_id="S")


# -- artifacts ----------------------------------------------------------------


def test_an_artifact_content_addresses_its_payload():
    artifact = EvidenceArtifact.create(
        artifact_id="EV-PLAN",
        stage=AssuranceStage.VALIDATION_PLANNING,
        name="validation-plan",
        payload={"a": 1},
    )
    assert artifact.content_sha256
    assert artifact.intact is True
    assert artifact.recompute() == artifact.content_sha256
    assert artifact.filename == "validation-plan.json"


def test_an_artifact_payload_must_be_a_mapping():
    with pytest.raises(AssuranceEvidenceError):
        EvidenceArtifact.create(
            artifact_id="X",
            stage=AssuranceStage.VALIDATION_PLANNING,
            name="n",
            payload=["not", "a", "mapping"],
        )


def test_an_identical_payload_content_addresses_identically():
    def build():
        return EvidenceArtifact.create(
            artifact_id="X",
            stage=AssuranceStage.VALIDATION_PLANNING,
            name="n",
            payload={"b": 2, "a": 1},
        )

    assert build().content_sha256 == build().content_sha256


def test_artifact_core_stands_the_digest_in_for_the_payload():
    artifact = EvidenceArtifact.create(
        artifact_id="X",
        stage=AssuranceStage.VALIDATION_PLANNING,
        name="n",
        payload={"secret": "value"},
    )
    assert "payload" not in artifact.core()
    assert artifact.core()["content_sha256"] == artifact.content_sha256


def test_a_mutated_payload_is_detected_by_recomputation():
    """The manifest's self-verification claim, attacked directly."""
    artifact = EvidenceArtifact.create(
        artifact_id="X",
        stage=AssuranceStage.VALIDATION_PLANNING,
        name="n",
        payload={"a": 1},
    )
    tampered = EvidenceArtifact(
        artifact_id=artifact.artifact_id,
        stage=artifact.stage,
        name=artifact.name,
        declared=artifact.declared,
        content_sha256=artifact.content_sha256,
        payload={"a": 999},
    )
    assert tampered.intact is False


# -- collection and drift -----------------------------------------------------


def test_a_contribution_matching_a_declared_artifact_takes_the_declared_id():
    collector = _collector()
    artifact = collector.record(AssuranceStage.VALIDATION_PLANNING, "validation-plan", {"a": 1})
    assert artifact.artifact_id == "EV-PLAN"
    assert artifact.declared is True


def test_a_contribution_the_policy_never_declared_is_collected_and_flagged():
    """Drift must be visible, not silent — in this direction too."""
    collector = _collector()
    artifact = collector.record(AssuranceStage.VALIDATION_PLANNING, "surprise", {"a": 1})
    assert artifact.declared is False
    assert artifact.artifact_id.startswith(UNDECLARED_ARTIFACT_PREFIX)
    bundle = collector.bundle(subject_id="S")
    assert bundle.undeclared() == (artifact.artifact_id,)
    assert bundle.counts()["undeclared"] == 1


def test_a_required_artifact_no_stage_contributed_is_missing():
    bundle = _collector().bundle(subject_id="S")
    assert bundle.missing_required() == ("EV-PLAN",)
    assert bundle.complete is False


def test_a_bundle_with_every_required_artifact_is_complete():
    bundle = _bundle_with_plan()
    assert bundle.missing_required() == ()
    assert bundle.manifest_intact is True
    assert bundle.complete is True


def test_an_optional_artifact_is_not_required_for_completeness():
    bundle = _bundle_with_plan()
    assert "EV-OPTIONAL" not in bundle.required_ids
    assert bundle.complete is True


def test_the_same_stage_and_name_recorded_twice_replaces_rather_than_duplicates():
    collector = _collector()
    collector.record(AssuranceStage.VALIDATION_PLANNING, "validation-plan", {"v": 1})
    collector.record(AssuranceStage.VALIDATION_PLANNING, "validation-plan", {"v": 2})
    assert len(collector) == 1
    assert collector.artifacts()[0].payload == {"v": 2}


def test_an_artifact_requires_a_non_empty_name():
    with pytest.raises(AssuranceEvidenceError):
        _collector().record(AssuranceStage.VALIDATION_PLANNING, "", {"a": 1})


def test_a_collector_requires_a_policy():
    with pytest.raises(AssuranceEvidenceError):
        EvidenceCollector("not-a-policy")


def test_the_collector_exposes_the_policy_it_enforces():
    policy = make_policy()
    assert EvidenceCollector(policy).policy is policy


def test_required_scope_can_be_narrowed_to_the_stages_already_complete():
    """A bundle can never contain an artifact describing itself."""
    collector = _collector()
    scoped = collector.bundle(subject_id="S", required_stages=())
    assert scoped.required_ids == ()
    assert scoped.missing_required() == ()
    assert scoped.complete is True

    unscoped = collector.bundle(subject_id="S")
    assert unscoped.required_ids == ("EV-PLAN",)
    assert unscoped.complete is False


def test_bundle_lookup_returns_none_for_an_absent_artifact():
    bundle = _bundle_with_plan()
    assert bundle.get("EV-PLAN") is not None
    assert bundle.get("EV-GHOST") is None


def test_artifacts_can_be_selected_by_stage():
    bundle = _bundle_with_plan()
    assert len(bundle.artifacts_for(AssuranceStage.VALIDATION_PLANNING)) == 1
    assert bundle.artifacts_for(AssuranceStage.CERTIFICATION_REGISTRY) == ()


# -- measurability ------------------------------------------------------------


def test_bundle_observations_expose_what_the_evidence_metrics_decide():
    observations = _bundle_with_plan().observations()
    assert observations["evidence.artifacts"] == 1.0
    assert observations["evidence.required_artifacts"] == 1.0
    assert observations["evidence.missing_required_artifacts"] == 0.0
    assert observations["evidence.undeclared_artifacts"] == 0.0
    assert observations["evidence.manifest_intact"] == 1.0


def test_a_missing_required_artifact_shows_up_in_the_observations():
    assert (
        _collector().bundle(subject_id="S").observations()["evidence.missing_required_artifacts"]
        == 1.0
    )


# -- the manifest -------------------------------------------------------------


def test_the_manifest_declares_its_format_and_carries_the_full_census():
    manifest = _bundle_with_plan().manifest()
    assert manifest["manifest_format"] == EVIDENCE_MANIFEST_FORMAT
    assert manifest["complete"] is True
    assert manifest["required_ids"] == ["EV-PLAN"]
    assert manifest["missing_required"] == []
    assert manifest["artifacts"][0]["filename"] == "validation-plan.json"


def test_the_bundle_dict_adds_the_bundle_format_to_the_manifest():
    payload = _bundle_with_plan().to_dict()
    assert payload["bundle_format"] == EVIDENCE_BUNDLE_FORMAT
    assert payload["manifest_format"] == EVIDENCE_MANIFEST_FORMAT


def test_the_bundle_anchors_itself_to_the_policy_text():
    policy = make_policy()
    collector = EvidenceCollector(policy)
    bundle = collector.bundle(subject_id="S")
    assert bundle.policy_digest == policy.digest()
    assert bundle.policy_id == policy.identity.id
    assert bundle.evidence_id.startswith("UCOS-AEVD-")


# -- reproducibility ----------------------------------------------------------


def test_an_identical_contribution_set_reproduces_an_identical_bundle():
    assert _bundle_with_plan().bundle_sha256 == _bundle_with_plan().bundle_sha256


def test_the_bundle_hash_is_independent_of_contribution_order():
    def build(order):
        collector = _collector()
        for stage, name in order:
            collector.record(stage, name, {"n": name})
        return collector.bundle(subject_id="S")

    forward = [
        (AssuranceStage.VALIDATION_PLANNING, "validation-plan"),
        (AssuranceStage.EVIDENCE_COLLECTION, "optional-note"),
    ]
    assert build(forward).bundle_sha256 == build(list(reversed(forward))).bundle_sha256


def test_the_bundle_hash_changes_when_a_payload_changes():
    def build(value):
        collector = _collector()
        collector.record(AssuranceStage.VALIDATION_PLANNING, "validation-plan", {"v": value})
        return collector.bundle(subject_id="S")

    assert build(1).bundle_sha256 != build(2).bundle_sha256


def test_an_explicitly_assembled_bundle_sorts_its_artifacts_canonically():
    artifacts = [
        EvidenceArtifact.create(
            artifact_id="B",
            stage=AssuranceStage.CERTIFICATION_REGISTRY,
            name="z",
            payload={},
        ),
        EvidenceArtifact.create(
            artifact_id="A",
            stage=AssuranceStage.VALIDATION_PLANNING,
            name="a",
            payload={},
        ),
    ]
    bundle = EvidenceBundle.create(
        subject_id="S", policy=make_policy(), artifacts=list(reversed(artifacts))
    )
    assert [a.artifact_id for a in bundle.artifacts] == ["A", "B"]


# -- write-scope enforcement --------------------------------------------------


from pathlib import Path  # noqa: E402 — imported here to keep the guard tests together


@pytest.mark.parametrize(
    "directory",
    ["99-FREEZE", "99-FREEZE/nested", "./99-FREEZE", "00-BOOK/tools"],
)
def test_a_forbidden_prefix_blocks_the_write_before_any_byte_is_written(directory):
    with pytest.raises(AssuranceEvidenceError) as exc:
        check_write_scope(Path(directory), ["99-FREEZE", "00-BOOK"])
    assert "forbidden" in str(exc.value)


@pytest.mark.parametrize("directory", [".runtime/evidence", "platform/x", "99-FREEZER"])
def test_a_permitted_directory_passes_the_scope_check(directory):
    check_write_scope(Path(directory), ["99-FREEZE", "00-BOOK"])


def test_an_absolute_spelling_of_a_forbidden_location_is_also_blocked(tmp_path, monkeypatch):
    """Relative and absolute spellings must not differ — that would be a bypass."""
    monkeypatch.chdir(tmp_path)
    target = tmp_path / "99-FREEZE" / "evidence"
    with pytest.raises(AssuranceEvidenceError):
        check_write_scope(target, ["99-FREEZE"])


def test_no_forbidden_prefixes_permits_everything():
    check_write_scope(Path("99-FREEZE"), [])


def test_write_bundle_refuses_a_forbidden_target(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    with pytest.raises(AssuranceEvidenceError):
        write_bundle(_bundle_with_plan(), tmp_path / "99-FREEZE", forbidden_prefixes=["99-FREEZE"])
    assert not (tmp_path / "99-FREEZE").exists()


# -- deterministic writing ----------------------------------------------------


def test_writing_a_bundle_emits_every_artifact_plus_the_manifest(tmp_path):
    written = write_bundle(_bundle_with_plan(), tmp_path / "evidence")
    names = {path.name for path in written}
    assert names == {"validation-plan.json", MANIFEST_FILENAME}
    assert all(path.is_file() for path in written)


def test_rewriting_an_identical_bundle_produces_identical_bytes(tmp_path):
    first_dir, second_dir = tmp_path / "a", tmp_path / "b"
    write_bundle(_bundle_with_plan(), first_dir)
    write_bundle(_bundle_with_plan(), second_dir)
    for name in ("validation-plan.json", MANIFEST_FILENAME):
        assert (first_dir / name).read_bytes() == (second_dir / name).read_bytes()


def test_written_json_is_sorted_indented_and_newline_terminated(tmp_path):
    path = write_json(tmp_path / "x.json", {"b": 2, "a": 1})
    text = path.read_text(encoding="utf-8")
    assert text.endswith("\n")
    assert text.startswith("{\n  ")
    assert list(json.loads(text)) == ["a", "b"]


def test_writing_creates_intermediate_directories(tmp_path):
    write_bundle(_bundle_with_plan(), tmp_path / "deep" / "nested" / "dir")
    assert (tmp_path / "deep" / "nested" / "dir" / MANIFEST_FILENAME).is_file()


def test_an_unwritable_evidence_directory_fails_closed(tmp_path):
    blocker = tmp_path / "blocked"
    blocker.write_text("i am a file, not a directory", encoding="utf-8")
    with pytest.raises(AssuranceEvidenceError) as exc:
        write_bundle(_bundle_with_plan(), blocker)
    assert "could not be created" in str(exc.value)


def test_an_artifact_that_cannot_be_written_fails_closed_after_the_directory_exists(tmp_path):
    """The directory is creatable but an artifact path is not writable — a partially
    written bundle must raise rather than be reported as collected evidence."""
    target = tmp_path / "evidence"
    target.mkdir()
    # Occupy the artifact's filename with a directory, so writing the file raises OSError.
    (target / "validation-plan.json").mkdir()
    with pytest.raises(AssuranceEvidenceError) as exc:
        write_bundle(_bundle_with_plan(), target)
    assert "could not be written" in str(exc.value)


def test_the_written_manifest_round_trips_to_the_in_memory_manifest(tmp_path):
    bundle = _bundle_with_plan()
    write_bundle(bundle, tmp_path / "evidence")
    written = json.loads((tmp_path / "evidence" / MANIFEST_FILENAME).read_text(encoding="utf-8"))
    assert written == bundle.manifest()
