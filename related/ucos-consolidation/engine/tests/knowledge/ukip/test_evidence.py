"""UKIP Part 13 — the evidence bundle, and every way it refuses to be trusted.

WHY THIS MODULE EXISTS. The bundle's three claims — sealed, self-verifying, deterministic
— are only worth what their negations cost. :func:`verify_evidence` enumerates seven
distinct defects and nothing had ever made one of them fire, so a bundle that disagreed
with itself would have been reported as verified. The same held for the two writes the
bundle refuses: into the frozen corpus (DP-03) and out of the directory it was handed.
"""

from __future__ import annotations

import json
from dataclasses import replace

import pytest

from engine.knowledge.model import content_hash
from engine.knowledge.ukip.errors import EvidenceError
from engine.knowledge.ukip.evidence import (
    EVIDENCE_FILENAME,
    EVIDENCE_SCHEMA,
    EVIDENCE_VERSION,
    SEAL_COMPONENTS,
    _repository_root,
    build_evidence,
    build_evidence_from_assimilation,
    read_evidence,
    verify_evidence,
    write_evidence,
)
from engine.knowledge.ukip.registry import KnowledgeRegistry


@pytest.fixture
def evidence(simple_registry: KnowledgeRegistry):
    return build_evidence(simple_registry)


# -- the bundle -----------------------------------------------------------------------


def test_a_bundle_seals_every_declared_component(evidence):
    assert set(evidence.component_seals) == set(SEAL_COMPONENTS)
    assert all(len(seal) == 64 for seal in evidence.component_seals.values())
    assert evidence.verify() is True
    assert evidence.seal == evidence.recompute_seal()


def test_the_bundle_is_deterministic_over_unchanged_knowledge(simple_registry):
    assert build_evidence(simple_registry).to_json() == build_evidence(simple_registry).to_json()


def test_altering_one_component_seal_breaks_the_bundle_seal(evidence):
    tampered = replace(evidence, component_seals={**evidence.component_seals, "registry": "0" * 64})
    assert tampered.verify() is False
    assert tampered.recompute_seal() != tampered.seal


def test_a_bundle_is_accepted_only_when_validation_and_certification_both_say_so(evidence):
    assert evidence.accepted is True
    sections = dict(evidence.sections)
    sections["certification"] = {**sections["certification"], "certified": False}
    assert replace(evidence, sections=sections).accepted is False


def test_a_section_is_returned_by_name_and_an_absent_one_is_refused(evidence):
    assert evidence.section("registry") == evidence.sections["registry"]
    with pytest.raises(EvidenceError):
        evidence.section("not-a-section")


def test_the_serialisation_is_canonical_and_newline_terminated(evidence):
    text = evidence.to_json()
    assert text.endswith("\n")
    document = json.loads(text)
    assert document["schema"] == EVIDENCE_SCHEMA
    assert document["version"] == EVIDENCE_VERSION
    assert document["seal"] == evidence.seal
    assert document["accepted"] is True


def test_an_assimilation_run_contributes_its_own_section(seed_report, seed_providers):
    bundle = build_evidence_from_assimilation(seed_report, providers=seed_providers)
    assert "assimilation" in bundle.sections
    assert bundle.sections["providers"]["count"] >= 1
    assert bundle.verify() is True


def test_without_providers_the_bundle_still_reports_the_provider_count(evidence):
    assert evidence.sections["providers"] == {"count": 1, "providers": []}
    assert evidence.sections["provenance"]["count"] == 3


# -- self-verification ----------------------------------------------------------------


def test_a_well_formed_document_verifies_against_itself(evidence):
    ok, defects = verify_evidence(evidence.to_dict())
    assert ok is True
    assert defects == ()


def test_a_non_mapping_document_is_refused_before_anything_else():
    ok, defects = verify_evidence(["not", "an", "object"])  # type: ignore[arg-type]
    assert ok is False
    assert defects == ("evidence document must be an object",)


def test_a_foreign_schema_is_a_defect(evidence):
    document = evidence.to_dict() | {"schema": "some-other-schema"}
    ok, defects = verify_evidence(document)
    assert ok is False
    assert "schema mismatch" in defects


def test_a_document_without_component_seals_cannot_be_verified_further(evidence):
    document = evidence.to_dict()
    del document["component_seals"]
    ok, defects = verify_evidence(document)
    assert ok is False
    assert defects[-1] == "component_seals missing"


def test_an_empty_component_seal_is_named_by_the_component_it_belongs_to(evidence):
    document = evidence.to_dict()
    document["component_seals"]["graph"] = ""
    ok, defects = verify_evidence(document)
    assert ok is False
    assert "missing component seal: graph" in defects


def test_a_bundle_seal_that_does_not_fold_its_components_is_a_defect(evidence):
    document = evidence.to_dict() | {"seal": "0" * 64}
    ok, defects = verify_evidence(document)
    assert ok is False
    assert "bundle seal does not match its component seals" in defects


def test_a_registry_section_that_disagrees_with_its_component_seal_is_a_defect(evidence):
    document = evidence.to_dict()
    document["sections"]["registry"] = {**document["sections"]["registry"], "seal": "1" * 64}
    ok, defects = verify_evidence(document)
    assert ok is False
    assert "registry section seal disagrees with component seal" in defects


def test_a_certification_section_that_disagrees_with_its_component_seal_is_a_defect(evidence):
    document = evidence.to_dict()
    document["sections"]["certification"] = {
        **document["sections"]["certification"],
        "seal": "2" * 64,
    }
    ok, defects = verify_evidence(document)
    assert ok is False
    assert "certification section seal disagrees with component seal" in defects


def test_sections_that_are_not_an_object_are_a_defect(evidence):
    document = evidence.to_dict() | {"sections": ["registry"]}
    ok, defects = verify_evidence(document)
    assert ok is False
    assert "sections missing" in defects


def test_sections_that_are_not_mappings_are_skipped_rather_than_crashing(evidence):
    """A section can be any JSON value; only a mapping carries a seal to compare."""
    document = evidence.to_dict()
    document["sections"]["registry"] = "not-a-mapping"
    document["sections"]["certification"] = 17
    ok, defects = verify_evidence(document)
    assert ok is True
    assert defects == ()


# -- writing --------------------------------------------------------------------------


def test_a_bundle_round_trips_through_the_filesystem(evidence, tmp_path):
    path = write_evidence(evidence, tmp_path)
    assert path.name == EVIDENCE_FILENAME
    document = read_evidence(path)
    assert verify_evidence(document) == (True, ())


def test_a_write_creates_the_directory_it_was_given(evidence, tmp_path):
    target = tmp_path / "deep" / "nested"
    path = write_evidence(evidence, target, filename="bundle.json")
    assert path == target / "bundle.json"
    assert path.is_file()


def test_a_write_into_the_frozen_corpus_is_refused(evidence):
    """DP-03 reused rather than restated: the Foundation frozen-path guard decides."""
    with pytest.raises(EvidenceError, match="frozen corpus"):
        write_evidence(evidence, _repository_root() / "00-BOOK" / "DATA")


def test_a_filename_that_escapes_the_target_directory_is_refused(evidence, tmp_path):
    with pytest.raises(EvidenceError, match="escapes the target directory"):
        write_evidence(evidence, tmp_path, filename="../escaped.json")


def test_an_unwritable_target_is_reported_rather_than_raised_as_an_oserror(
    evidence, tmp_path, monkeypatch
):
    def _refuse(*_args, **_kwargs):
        raise OSError("read-only file system")

    monkeypatch.setattr("pathlib.Path.mkdir", _refuse)
    with pytest.raises(EvidenceError, match="could not be written"):
        write_evidence(evidence, tmp_path / "unwritable")


# -- reading --------------------------------------------------------------------------


def test_a_missing_bundle_is_reported_by_path(tmp_path):
    with pytest.raises(EvidenceError, match="not found"):
        read_evidence(tmp_path / "absent.json")


def test_a_malformed_bundle_is_reported_as_invalid_json(tmp_path):
    path = tmp_path / "broken.json"
    path.write_text("{not json", encoding="utf-8")
    with pytest.raises(EvidenceError, match="not valid JSON"):
        read_evidence(path)


def test_a_bundle_whose_root_is_not_an_object_is_refused(tmp_path):
    path = tmp_path / "list.json"
    path.write_text("[1, 2, 3]", encoding="utf-8")
    with pytest.raises(EvidenceError, match="root must be an object"):
        read_evidence(path)


def test_the_recomputed_seal_ignores_components_the_bundle_never_recorded(evidence):
    stripped = replace(evidence, component_seals={})
    assert stripped.recompute_seal() == content_hash(dict.fromkeys(SEAL_COMPONENTS, ""))
