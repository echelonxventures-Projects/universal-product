"""EC3-B12-U02 — Realization orchestrator tests (AC-1…AC-7 + VC-1…VC-5 + determinism + CLI)."""

from __future__ import annotations

import json

from application.capability import Capability
from application.capability_meta import REALIZATION_UNIT
from application.capability_realize import (
    CANONICAL_OPERATION_REF,
    CANONICAL_TYPE_TAG,
    build_canonical_capability,
    determinism_check,
    emit_evidence,
    main,
    realize,
)
from application.capability_traceability import TraceabilityRecord


def test_canonical_capability_is_the_foundation_exemplar():
    cap = build_canonical_capability()
    assert isinstance(cap, Capability)
    assert cap.type_tag == CANONICAL_TYPE_TAG
    assert cap.operation_ref == CANONICAL_OPERATION_REF
    assert cap.meta_class == "AMC-02"


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


def test_ual_conformance_all_pass_and_includes_derived_laws():
    ual = realize().ual_conformance()
    assert ual["UAL-01"] is True  # structural
    assert ual["UAL-14"] is True  # derived (non-enforcing)
    assert ual["UAL-06"] is True  # capability consumes SF-2 operation
    assert ual["UAL-13"] is True  # capability presents DF-2 data
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


def test_capability_compliance_all_pass():
    comp = realize().capability_compliance()
    assert set(comp) == {f"C{n}" for n in range(1, 8)}
    assert all(comp.values())


def test_determination_complete_with_conditions_path():
    # byte_identical False breaks VC-4 (a validation criterion) but validation +
    # certification + trace still hold → "COMPLETE WITH CONDITIONS".
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
    assert bundle["meta_class"] == "AMC-02"
    assert bundle["authority"] == "ENGINEERING-EXECUTION-ONLY"
    assert bundle["determination"] == "COMPLETE"
    assert bundle["capability"]["meta_class"] == "AMC-02"
    assert bundle["traceability"]["closed"] is True
    assert "meta_validity_V1_V5" in bundle
    assert "ual_conformance" in bundle
    assert "application_compliance_C1_C7" in bundle


def test_emit_evidence_writes_all_files(tmp_path):
    summary = emit_evidence(tmp_path)
    assert summary["determination"] == "COMPLETE"
    assert summary["certified"] is True
    assert summary["byte_identical"] is True
    assert summary["capability_id"].startswith("UCOS-CAPABILITY-")
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
    assert "EC3-B12-U02 → COMPLETE" in out
    assert "PASS" in out


def test_traceability_fingerprint_is_deterministic_content_hash():
    result = realize()
    fp1 = result.trace.fingerprint()
    fp2 = result.trace.fingerprint()
    assert fp1 == fp2
    assert len(fp1) == 64


def test_determination_not_complete_for_rejected_result():
    from application.capability import make_capability
    from application.capability_certification import certify_capability
    from application.capability_realize import RealizationResult
    from application.capability_traceability import build_traceability
    from application.capability_validation import validate_capability

    # Technology-bearing capability fails validation + certification; empty-forward trace
    # is not closed → all three determination predicates false → "NOT COMPLETE".
    techy = make_capability("t", "ENG-005:SF-2:kafka.stream")
    trace = build_traceability(techy, unit=REALIZATION_UNIT, forward=())
    validation = validate_capability(techy, trace)
    certification = certify_capability(validation, version="1.0.0")
    result = RealizationResult(
        capability=techy, trace=trace, validation=validation, certification=certification
    )
    assert result.validation.accepted is False
    assert result.trace.closed is False
    assert result.determination(byte_identical=True) == "NOT COMPLETE"
