"""EC3-B10-U08 — Realization + determinism tests (VC-4, AC-1…8, VC-1…5, spine)."""

from __future__ import annotations

import json

from data.entity_realize import build_canonical_entity
from data.quality import make_measurements, make_quality, policy_ref_for
from data.quality_certification import certify_quality
from data.quality_meta import QualityKind
from data.quality_realize import (
    CANONICAL_QUALITY_NAME,
    UNIT_VERSION,
    RealizationResult,
    build_canonical_quality,
    determinism_check,
    emit_evidence,
    main,
    realize,
)
from data.quality_traceability import build_quality_traceability
from data.quality_validation import validate_quality

SCHEMA_REF = "UCOS-SCHEMA-REF:ucos.demo.schema"


def _result_for(quality):
    """Assemble a RealizationResult for an arbitrary quality object (test helper)."""
    trace = build_quality_traceability(quality, unit="EC3-B10-U08", forward=(quality.quality_id,))
    validation = validate_quality(quality, trace)
    certification = certify_quality(validation, version=UNIT_VERSION)
    return RealizationResult(
        quality=quality,
        measured_entity=build_canonical_entity(),
        trace=trace,
        validation=validation,
        certification=certification,
    )


def test_realization_determination_is_complete():
    result = realize()
    assert result.determination(byte_identical=True) == "COMPLETE"
    assert result.validation.accepted is True
    assert result.certification.certified is True
    assert result.trace.closed is True


def test_quality_measures_the_certified_entity_by_reference():
    result = realize()
    # the realized quality object measures the CERTIFIED-surface Entity's identity by reference
    assert result.quality.measures_construct(result.measured_entity.entity_id)  # DMR-08
    assert result.quality.absorbs_measured() is False  # DQA-C3 / DMX-02 non-owning


def test_full_spine_quality_measures_entity():
    result = realize()
    sc = result.spine_closure()
    assert sc["measures_entity"] is True  # DMR-08
    assert sc["evaluative"] is True  # DQA-01
    assert sc["non_remediating"] is True  # DQA-03 / UDL-14
    assert sc["binds_policy_by_reference"] is True  # DMR-11 / DQA-06
    assert sc["schema_relative"] is True  # DQA-05 / DQA-C2
    assert sc["technology_neutral"] is True  # UDL-14 / DQA-K5


def test_acceptance_criteria_ac1_ac8_all_hold():
    result = realize()
    ac = result.acceptance_criteria()
    assert set(ac) == {f"AC-{n}" for n in range(1, 9)}
    assert all(ac.values()), ac


def test_validation_criteria_vc1_vc5_all_hold():
    result = realize()
    vc = result.validation_criteria(byte_identical=True)
    assert set(vc) == {f"VC-{n}" for n in range(1, 6)}
    assert all(vc.values()), vc


def test_meta_validity_and_udl_conformance_complete():
    result = realize()
    assert all(result.meta_validity().values())  # V1…V5
    udl = result.udl_conformance()
    for law in ("UDL-01", "UDL-02", "UDL-03", "UDL-04", "UDL-12", "UDL-14", "UDL-15"):
        assert udl[law], law


def test_certification_gates_and_compliance_complete():
    result = realize()
    assert all(result.certification_gates().values())  # CC-1…CC-10
    assert all(result.data_compliance().values())  # C1…C7


def test_double_realization_is_byte_identical():
    byte_identical, digest_a, digest_b = determinism_check()
    assert byte_identical is True  # VC-4
    assert digest_a == digest_b
    assert len(digest_a) == 64


def test_canonical_builder_is_consistent():
    quality = build_canonical_quality()
    assert quality.name == CANONICAL_QUALITY_NAME
    assert quality.records_measurement() is True  # records its measurement verdicts
    assert quality.remediates() is False
    assert quality.names_technology() is False


def test_emit_evidence_writes_all_artifacts(tmp_path):
    summary = emit_evidence(tmp_path)
    assert summary["determination"] == "COMPLETE"
    assert summary["byte_identical"] is True
    assert summary["spine_closed"] is True
    expected = {
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
    }
    written = {p.name for p in tmp_path.iterdir()}
    assert expected <= written


def test_emitted_evidence_is_stable_across_runs(tmp_path):
    a = tmp_path / "a"
    b = tmp_path / "b"
    emit_evidence(a)
    emit_evidence(b)
    for name in ("realization-evidence.json", "cce-certification.json", "traceability.json"):
        assert (a / name).read_text() == (b / name).read_text()  # no drift


def test_version_is_pinned():
    assert UNIT_VERSION == "1.0.0"


def test_cli_main_returns_zero(tmp_path, capsys):
    rc = main(["--evidence-dir", str(tmp_path)])
    assert rc == 0
    out = capsys.readouterr().out
    assert "[PASS] EC3-B10-U08 → COMPLETE" in out
    bundle = json.loads((tmp_path / "realization-evidence.json").read_text())
    assert bundle["determination"] == "COMPLETE"
    assert bundle["meta_class"] == "DMC-09"


def test_determination_complete_with_conditions_when_not_byte_identical():
    # Validation accepted + certified + traced, but VC-4 (determinism) fails → conditional.
    result = realize()
    assert result.determination(byte_identical=False) == "COMPLETE WITH CONDITIONS"


def test_determination_not_complete_for_failing_quality():
    # A secret-bearing quality fails validation → not accepted/certified → NOT COMPLETE.
    entity = build_canonical_entity()
    bad = make_quality(
        "api_key",  # embeds a secret → non-constitutive gate fails
        "ucos.core.quality",
        entity,
        policy_ref_for("quality.udl"),
        kind=QualityKind.COMPLETENESS_MEASURE,
        measurements=make_measurements((("completeness", True, 100),)),
        schema_ref=SCHEMA_REF,
    )
    result = _result_for(bad)
    assert result.determination(byte_identical=True) == "NOT COMPLETE"
    assert result.validation.accepted is False
