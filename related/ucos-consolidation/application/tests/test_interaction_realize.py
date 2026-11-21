"""EC3-B12-U06 — Realization orchestrator tests (AC-1…AC-7 + VC-1…VC-5 + determinism + CLI)."""

from __future__ import annotations

import json

from application.interaction import Interaction
from application.interaction_meta import REALIZATION_UNIT, InteractionKind
from application.interaction_realize import (
    CANONICAL_FEATURE_REF,
    build_canonical_interaction,
    determinism_check,
    emit_evidence,
    main,
    realize,
)
from application.interaction_traceability import TraceabilityRecord


def test_canonical_interaction_is_the_foundation_exemplar():
    it = build_canonical_interaction()
    assert isinstance(it, Interaction)
    assert it.feature_ref == CANONICAL_FEATURE_REF
    assert it.kind is InteractionKind.COMMAND
    assert it.direction() == "command"
    assert it.surface_is_abstract() is True
    assert it.presents_data() is True
    assert it.holds_state() is True
    assert it.meta_class == "AMC-06"


def test_realize_produces_complete_certified_result():
    result = realize()
    assert result.validation.accepted is True
    assert result.certification.certified is True
    assert result.trace.closed is True
    assert isinstance(result.trace, TraceabilityRecord)
    assert result.determination(byte_identical=True) == "COMPLETE"


def test_meta_validity_all_pass():
    mv = realize().meta_validity()
    assert set(mv) == {"V1", "V2", "V3", "V4", "V5"}
    assert all(mv.values())


def test_ual_conformance_applicable_laws_pass():
    ual = realize().ual_conformance()
    # Only the laws that apply to the Interaction are recorded (UAL-06/07/08/09 are scoped
    # to Feature/Module/Application/Composition units — recorded N/A elsewhere).
    assert set(ual) == {
        "UAL-01", "UAL-02", "UAL-03", "UAL-04", "UAL-05",
        "UAL-10", "UAL-11", "UAL-12", "UAL-13", "UAL-14", "UAL-15",
    }
    assert ual["UAL-01"] is True  # structural
    assert ual["UAL-11"] is True  # interaction typedness + abstract surface (governing)
    assert ual["UAL-13"] is True  # DF-2 data by reference
    assert ual["UAL-14"] is True  # derived (non-enforcing)
    assert all(ual.values())


def test_acceptance_criteria_all_pass():
    ac = realize().acceptance_criteria()
    assert set(ac) == {f"AC-{n}" for n in range(1, 8)}
    assert all(ac.values())


def test_validation_criteria_all_pass():
    vc = realize().validation_criteria(byte_identical=True)
    assert set(vc) == {f"VC-{n}" for n in range(1, 6)}
    assert all(vc.values())


def test_validation_criteria_vc4_reflects_determinism_flag():
    vc = realize().validation_criteria(byte_identical=False)
    assert vc["VC-4"] is False


def test_certification_gates_all_pass():
    gates = realize().certification_gates()
    assert set(gates) == {f"CC-{n}" for n in range(1, 11)}
    assert all(gates.values())


def test_interaction_compliance_all_pass():
    comp = realize().interaction_compliance()
    assert set(comp) == {f"C{n}" for n in range(1, 8)}
    assert all(comp.values())


def test_determination_complete_with_conditions_path():
    result = realize()
    assert result.determination(byte_identical=False) == "COMPLETE WITH CONDITIONS"


def test_determinism_check_is_byte_identical():
    ok, a, b = determinism_check()
    assert ok is True
    assert a == b
    assert len(a) == 64


def test_bundle_shape_and_provenance():
    bundle = realize().to_bundle(byte_identical=True)
    assert bundle["unit"] == REALIZATION_UNIT
    assert bundle["meta_class"] == "AMC-06"
    assert bundle["authority"] == "ENGINEERING-EXECUTION-ONLY"
    assert bundle["determination"] == "COMPLETE"
    assert bundle["interaction"]["meta_class"] == "AMC-06"
    assert bundle["traceability"]["closed"] is True
    assert "meta_validity_V1_V5" in bundle
    assert "ual_conformance" in bundle
    assert "application_compliance_C1_C7" in bundle


def test_emit_evidence_writes_all_files(tmp_path):
    summary = emit_evidence(tmp_path)
    assert summary["determination"] == "COMPLETE"
    assert summary["certified"] is True
    assert summary["byte_identical"] is True
    assert summary["interaction_id"].startswith("UCOS-INTERACTION-")
    expected = {
        "realization-evidence.json",
        "validation-report.json",
        "validation-evidence.json",
        "acceptance-decision.json",
        "cce-certification.json",
        "certification-evidence.json",
        "certification-ledger.json",
        "application-compliance.json",
        "traceability.json",
        "determinism.json",
    }
    written = {p.name for p in tmp_path.iterdir()}
    assert expected <= written


def test_emit_evidence_is_deterministic_on_disk(tmp_path):
    d1 = tmp_path / "run1"
    d2 = tmp_path / "run2"
    emit_evidence(d1)
    emit_evidence(d2)
    a = (d1 / "realization-evidence.json").read_text()
    b = (d2 / "realization-evidence.json").read_text()
    assert a == b  # byte-identical across independent runs


def test_written_evidence_is_valid_json(tmp_path):
    emit_evidence(tmp_path)
    payload = json.loads((tmp_path / "realization-evidence.json").read_text())
    assert payload["determination"] == "COMPLETE"


def test_cli_main_returns_zero_on_complete(tmp_path, capsys):
    rc = main(["--evidence-dir", str(tmp_path)])
    assert rc == 0
    out = capsys.readouterr().out
    assert "EC3-B12-U06 → COMPLETE" in out
    assert "PASS" in out


def test_traceability_fingerprint_is_deterministic_content_hash():
    result = realize()
    fp1 = result.trace.fingerprint()
    fp2 = result.trace.fingerprint()
    assert fp1 == fp2
    assert len(fp1) == 64


def test_determination_not_complete_for_rejected_result():
    from application.interaction import make_interaction
    from application.interaction_certification import certify_interaction
    from application.interaction_realize import RealizationResult
    from application.interaction_traceability import build_traceability
    from application.interaction_validation import validate_interaction

    # Technology-bearing interaction fails validation + certification; empty-forward trace
    # is not closed → all three determination predicates false → "NOT COMPLETE".
    techy = make_interaction("t", "ENG-005:AMC-04:angular.view")
    trace = build_traceability(techy, unit=REALIZATION_UNIT, forward=())
    validation = validate_interaction(techy, trace)
    certification = certify_interaction(validation, version="1.0.0")
    result = RealizationResult(
        interaction=techy, trace=trace, validation=validation, certification=certification
    )
    assert result.validation.accepted is False
    assert result.trace.closed is False
    assert result.determination(byte_identical=True) == "NOT COMPLETE"
