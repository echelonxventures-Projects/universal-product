"""EC3-B10-U10 — Relationship realization tests (spine, determinism, evidence, CLI)."""

from __future__ import annotations

import json
from dataclasses import replace

from data.entity_realize import build_canonical_entity
from data.relationship_realize import (
    REALIZATION_UNIT,
    build_canonical_relationship,
    build_canonical_target_entity,
    determinism_check,
    emit_evidence,
    main,
    realize,
)

EVIDENCE_FILES = (
    "realization-evidence.json",
    "validation-report.json",
    "validation-evidence.json",
    "acceptance-decision.json",
    "cce-certification.json",
    "certification-evidence.json",
    "certification-ledger.json",
    "data-compliance.json",
    "traceability.json",
    "determinism.json",
)


def test_realization_is_complete():
    result = realize()
    assert result.determination(byte_identical=True) == "COMPLETE"
    assert result.validation.accepted is True
    assert result.certification.certified is True
    assert result.trace.closed is True


def test_spine_is_closed():
    result = realize()
    spine = result.spine_closure()
    assert all(spine.values()), [k for k, v in spine.items() if not v]
    # source endpoint is the exact CERTIFIED U03 canonical entity (spine anchor)
    assert result.relationship.source_id() == build_canonical_entity().entity_id
    assert spine["relates_entities"] is True
    assert spine["source_is_certified_entity"] is True


def test_canonical_relationship_relates_two_distinct_certified_entities():
    r = build_canonical_relationship()
    source = build_canonical_entity()
    target = build_canonical_target_entity()
    assert r.relates_entities(source.entity_id, target.entity_id) is True
    assert source.entity_id != target.entity_id
    assert r.endpoints_distinct() is True


def test_target_entity_is_certified_surface_entity():
    target = build_canonical_target_entity()
    assert target.meta_class == "DMC-02"
    assert target.entity_id.startswith("UCOS-ENTITY-")


def test_meta_validity_v1_v5_all_true():
    result = realize()
    mv = result.meta_validity()
    assert set(mv) == {"V1", "V2", "V3", "V4", "V5"}
    assert all(mv.values())


def test_udl_conformance_includes_material_udl09():
    result = realize()
    udl = result.udl_conformance()
    assert udl["UDL-09"] is True  # material — ENG-005 reference + founding acyclic
    assert udl["UDL-01"] is True
    assert all(udl.values())


def test_acceptance_and_validation_criteria_all_true():
    result = realize()
    ac = result.acceptance_criteria()
    assert set(ac) == {f"AC-{n}" for n in range(1, 9)}
    assert all(ac.values())
    vc = result.validation_criteria(byte_identical=True)
    assert set(vc) == {f"VC-{n}" for n in range(1, 6)}
    assert all(vc.values())


def test_certification_gates_and_compliance_rollups():
    result = realize()
    gates = result.certification_gates()
    assert all(gates.values()) and len(gates) == 10
    compliance = result.data_compliance()
    assert all(compliance.values()) and len(compliance) == 7


def test_determination_complete_with_conditions_branch():
    # A byte_identical=False collapses VC-4 → not fully COMPLETE, but validation+cert+trace
    # hold, so the determination falls to the "COMPLETE WITH CONDITIONS" branch.
    result = realize()
    assert result.determination(byte_identical=False) == "COMPLETE WITH CONDITIONS"


def test_determination_not_complete_when_lineage_open():
    # An open (non-closed) traceability record collapses the determination to NOT COMPLETE,
    # proving the completion definition is fail-closed (UCIC-001 Output 6).
    result = realize()
    broken = replace(result, trace=replace(result.trace, forward=()))
    assert broken.trace.closed is False
    assert broken.determination(byte_identical=True) == "NOT COMPLETE"


def test_determinism_is_byte_identical():
    byte_identical, digest_a, digest_b = determinism_check()
    assert byte_identical is True
    assert digest_a == digest_b
    assert len(digest_a) == 64


def test_bundle_shape():
    bundle = realize().to_bundle(byte_identical=True)
    assert bundle["unit"] == REALIZATION_UNIT
    assert bundle["meta_class"] == "DMC-04"
    assert bundle["spine"].startswith("Relationship relates Entity")
    assert bundle["determination"] == "COMPLETE"
    assert "source_entity" in bundle and "target_entity" in bundle


def test_emit_evidence_writes_all_files(tmp_path):
    summary = emit_evidence(tmp_path)
    assert summary["determination"] == "COMPLETE"
    assert summary["certified"] is True
    assert summary["spine_closed"] is True
    for name in EVIDENCE_FILES:
        path = tmp_path / name
        assert path.exists(), name
        json.loads(path.read_text())  # deterministic, valid JSON


def test_emit_evidence_is_idempotent(tmp_path):
    first = emit_evidence(tmp_path)
    contents_a = {n: (tmp_path / n).read_text() for n in EVIDENCE_FILES}
    second = emit_evidence(tmp_path)
    contents_b = {n: (tmp_path / n).read_text() for n in EVIDENCE_FILES}
    assert first["bundle_sha256"] == second["bundle_sha256"]
    assert contents_a == contents_b  # byte-stable re-emission (no drift)


def test_cli_main_returns_zero(tmp_path, capsys):
    rc = main(["--evidence-dir", str(tmp_path)])
    assert rc == 0
    out = capsys.readouterr().out
    assert "[PASS] EC3-B10-U10 → COMPLETE" in out
