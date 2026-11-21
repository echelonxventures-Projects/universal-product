"""EC3-B12-U04 — Realization orchestrator tests (AC-1…AC-7 + VC-1…VC-5 + determinism + CLI)."""

from __future__ import annotations

import json

from application.feature import Feature
from application.feature_meta import REALIZATION_UNIT, FeatureKind
from application.feature_realize import (
    CANONICAL_CAPABILITY_REF,
    CANONICAL_OPERATION_REFS,
    build_canonical_feature,
    determinism_check,
    emit_evidence,
    main,
    realize,
)
from application.feature_traceability import TraceabilityRecord


def test_canonical_feature_is_the_foundation_exemplar():
    feat = build_canonical_feature()
    assert isinstance(feat, Feature)
    assert feat.capability_ref == CANONICAL_CAPABILITY_REF
    assert set(feat.operation_refs) == set(CANONICAL_OPERATION_REFS)
    assert feat.kind is FeatureKind.COMPOSITE
    assert feat.composed_operation_count() == 2
    assert feat.meta_class == "AMC-04"


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


def test_ual_conformance_all_fifteen_pass():
    ual = realize().ual_conformance()
    # The Feature is the single construct that exercises every one of UAL-01…15.
    assert set(ual) == {f"UAL-{n:02d}" for n in range(1, 16)}
    assert ual["UAL-01"] is True  # structural
    assert ual["UAL-06"] is True  # delivers capability by consuming SF-2 ops (governing)
    assert ual["UAL-08"] is True  # declaration complete (governing)
    assert ual["UAL-11"] is True  # engaged through a typed interaction (governing)
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


def test_feature_compliance_all_pass():
    comp = realize().feature_compliance()
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
    assert bundle["meta_class"] == "AMC-04"
    assert bundle["authority"] == "ENGINEERING-EXECUTION-ONLY"
    assert bundle["determination"] == "COMPLETE"
    assert bundle["feature"]["meta_class"] == "AMC-04"
    assert bundle["traceability"]["closed"] is True
    assert "meta_validity_V1_V5" in bundle
    assert "ual_conformance" in bundle
    assert "application_compliance_C1_C7" in bundle


def test_emit_evidence_writes_all_files(tmp_path):
    summary = emit_evidence(tmp_path)
    assert summary["determination"] == "COMPLETE"
    assert summary["certified"] is True
    assert summary["byte_identical"] is True
    assert summary["feature_id"].startswith("UCOS-FEATURE-")
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
    assert "EC3-B12-U04 → COMPLETE" in out
    assert "PASS" in out


def test_traceability_fingerprint_is_deterministic_content_hash():
    result = realize()
    fp1 = result.trace.fingerprint()
    fp2 = result.trace.fingerprint()
    assert fp1 == fp2
    assert len(fp1) == 64


def test_determination_not_complete_for_rejected_result():
    from application.feature import make_feature
    from application.feature_certification import certify_feature
    from application.feature_realize import RealizationResult
    from application.feature_traceability import build_traceability
    from application.feature_validation import validate_feature

    # Technology-bearing feature fails validation + certification; empty-forward trace
    # is not closed → all three determination predicates false → "NOT COMPLETE".
    techy = make_feature("t", "ENG-005:AMC-02:cap", ("ENG-005:SF-2:kafka.consumer",))
    trace = build_traceability(techy, unit=REALIZATION_UNIT, forward=())
    validation = validate_feature(techy, trace)
    certification = certify_feature(validation, version="1.0.0")
    result = RealizationResult(
        feature=techy, trace=trace, validation=validation, certification=certification
    )
    assert result.validation.accepted is False
    assert result.trace.closed is False
    assert result.determination(byte_identical=True) == "NOT COMPLETE"
